#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生命周期管理器 (LifecycleManager)
基于现有lifecycle_management.py，增强为完整的生命周期管理
职责：定期任务、系统维护、归档清理
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ...internal import handle_memory_errors, ErrorHandlerMixin

logger = logging.getLogger(__name__)

class LifecycleManager(ErrorHandlerMixin):
    """生命周期管理器 - 系统维护和定期任务"""
    
    def __init__(self, components: Dict[str, Any], config_manager=None):
        """
        初始化生命周期管理器
        
        Args:
            components: 所需的组件字典
            config_manager: 配置管理器
        """
        super().__init__()
        self.db_manager = components.get('db_manager')
        self.weight_manager = components.get('weight_manager')
        self.memory_store = components.get('memory_store')
        self.config_manager = config_manager
        
        # 导入原有的生命周期管理功能
        try:
            from ...lifecycle_management import LifecycleManager as OriginalLifecycleManager
            self.original_lifecycle = OriginalLifecycleManager(self.db_manager)
        except ImportError:
            self.original_lifecycle = None
        
        # 任务调度器
        self.scheduled_tasks = {}
        self.is_running = False
        self.scheduler_task = None
        
        # 获取配置
        self.lifecycle_config = self._get_lifecycle_config()
        
        self.logger = logger
    
    def _get_lifecycle_config(self) -> Dict[str, Any]:
        """获取生命周期配置"""
        if self.config_manager:
            return self.config_manager.get_config('lifecycle', {})
        
        # 默认配置
        return {
            'cleanup_interval': 86400,  # 24小时
            'archive_threshold_days': 30,
            'delete_threshold_days': 90,
            'compression_enabled': True,
            'backup_interval': 3600,  # 1小时
            'vacuum_interval': 604800,  # 7天
            'weight_decay_interval': 3600  # 1小时
        }
    
    async def start_lifecycle_management(self):
        """启动生命周期管理"""
        self.is_running = True
        
        # 注册定期任务
        await self._register_scheduled_tasks()
        
        # 启动调度器
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        self.logger.info("🔄 生命周期管理器已启动")
    
    async def stop_lifecycle_management(self):
        """停止生命周期管理"""
        self.is_running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("⏹️ 生命周期管理器已停止")
    
    async def _register_scheduled_tasks(self):
        """注册定期任务"""
        config = self.lifecycle_config
        
        # 注册清理任务
        self.scheduled_tasks['cleanup'] = {
            'function': self.cleanup_old_memories,
            'interval': config.get('cleanup_interval', 86400),
            'last_run': 0,
            'description': '清理过期记忆'
        }
        
        # 注册归档任务
        self.scheduled_tasks['archive'] = {
            'function': self.archive_old_memories,
            'interval': config.get('archive_threshold_days', 30) * 86400,
            'last_run': 0,
            'description': '归档旧记忆'
        }
        
        # 注册权重衰减任务
        self.scheduled_tasks['weight_decay'] = {
            'function': self.apply_weight_decay,
            'interval': config.get('weight_decay_interval', 3600),
            'last_run': 0,
            'description': '应用权重衰减'
        }
        
        # 注册数据库维护任务
        self.scheduled_tasks['database_maintenance'] = {
            'function': self.perform_database_maintenance,
            'interval': config.get('vacuum_interval', 604800),
            'last_run': 0,
            'description': '数据库维护'
        }
        
        # 注册备份任务
        self.scheduled_tasks['backup'] = {
            'function': self.backup_database,
            'interval': config.get('backup_interval', 3600),
            'last_run': 0,
            'description': '数据库备份'
        }
        
        self.logger.info(f"✅ 已注册 {len(self.scheduled_tasks)} 个定期任务")
    
    async def _scheduler_loop(self):
        """调度器循环"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # 检查每个任务是否需要执行
                for task_name, task_info in self.scheduled_tasks.items():
                    if (current_time - task_info['last_run']) >= task_info['interval']:
                        try:
                            self.logger.info(f"🔄 执行定期任务: {task_info['description']}")
                            
                            # 执行任务
                            await task_info['function']()
                            
                            # 更新最后执行时间
                            task_info['last_run'] = current_time
                            
                            self.logger.info(f"✅ 任务完成: {task_info['description']}")
                            
                        except Exception as e:
                            self.logger.error(f"❌ 任务执行失败 {task_name}: {e}")
                
                # 等待一分钟再检查
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"调度器循环错误: {e}")
                await asyncio.sleep(60)
    
    @handle_memory_errors({'cleaned_count': 0, 'error': '清理失败'})
    async def cleanup_old_memories(self, days_threshold: int = None, 
                                  weight_threshold: float = None) -> Dict[str, Any]:
        """
        清理过期记忆
        
        Args:
            days_threshold: 天数阈值
            weight_threshold: 权重阈值
            
        Returns:
            Dict: 清理结果
        """
        try:
            # 使用配置或参数
            days_threshold = days_threshold or self.lifecycle_config.get('delete_threshold_days', 90)
            weight_threshold = weight_threshold or 2.0
            
            # 如果有原始生命周期管理器，使用它
            if self.original_lifecycle:
                result = self.original_lifecycle.cleanup_old_memories(days_threshold, weight_threshold)
                if isinstance(result, dict):
                    return result
            
            # 否则实现基本清理逻辑
            cutoff_time = time.time() - (days_threshold * 86400)
            
            cleanup_query = """
                DELETE FROM memories 
                WHERE timestamp < ? 
                AND weight < ?
                AND (archived = 1 OR deleted = 1)
            """
            
            if self.db_manager:
                result = self.db_manager.execute_query(cleanup_query, (cutoff_time, weight_threshold))
                cleaned_count = self.db_manager.get_affected_rows()
                
                self.logger.info(f"🗑️ 清理完成: 删除了 {cleaned_count} 条过期记忆")
                
                return {
                    'cleaned_count': cleaned_count,
                    'days_threshold': days_threshold,
                    'weight_threshold': weight_threshold,
                    'timestamp': time.time()
                }
            
            return {'cleaned_count': 0, 'error': '数据库管理器未初始化'}
            
        except Exception as e:
            self.logger.error(f"清理过期记忆失败: {e}")
            return {'cleaned_count': 0, 'error': str(e)}
    
    @handle_memory_errors({'archived_count': 0, 'error': '归档失败'})
    async def archive_old_memories(self, days_threshold: int = None) -> Dict[str, Any]:
        """
        归档旧记忆
        
        Args:
            days_threshold: 天数阈值
            
        Returns:
            Dict: 归档结果
        """
        try:
            days_threshold = days_threshold or self.lifecycle_config.get('archive_threshold_days', 30)
            cutoff_time = time.time() - (days_threshold * 86400)
            
            archive_query = """
                UPDATE memories 
                SET archived = 1, 
                    metadata = json_set(COALESCE(metadata, '{}'), '$.archived_at', ?)
                WHERE timestamp < ? 
                AND archived = 0
                AND weight < 7.0
            """
            
            if self.db_manager:
                self.db_manager.execute_query(archive_query, (time.time(), cutoff_time))
                archived_count = self.db_manager.get_affected_rows()
                
                self.logger.info(f"📦 归档完成: 归档了 {archived_count} 条旧记忆")
                
                return {
                    'archived_count': archived_count,
                    'days_threshold': days_threshold,
                    'timestamp': time.time()
                }
            
            return {'archived_count': 0, 'error': '数据库管理器未初始化'}
            
        except Exception as e:
            self.logger.error(f"归档旧记忆失败: {e}")
            return {'archived_count': 0, 'error': str(e)}
    
    @handle_memory_errors({'updated_count': 0, 'error': '权重衰减失败'})
    async def apply_weight_decay(self) -> Dict[str, Any]:
        """
        应用权重衰减
        
        Returns:
            Dict: 权重衰减结果
        """
        try:
            if self.weight_manager:
                # 使用权重管理器的衰减功能
                result = await self.weight_manager.apply_time_decay()
                self.logger.info(f"⚖️ 权重衰减完成: 更新了 {result.get('updated_count', 0)} 条记忆")
                return result
            
            # 基本权重衰减实现
            decay_rate = self.lifecycle_config.get('weight_decay_rate', 0.995)
            current_time = time.time()
            one_day_ago = current_time - 86400
            
            decay_query = """
                UPDATE memories 
                SET weight = weight * ?,
                    last_accessed = ?
                WHERE timestamp < ?
                AND archived = 0
                AND weight > 1.0
            """
            
            if self.db_manager:
                self.db_manager.execute_query(decay_query, (decay_rate, current_time, one_day_ago))
                updated_count = self.db_manager.get_affected_rows()
                
                return {
                    'updated_count': updated_count,
                    'decay_rate': decay_rate,
                    'timestamp': current_time
                }
            
            return {'updated_count': 0, 'error': '数据库管理器未初始化'}
            
        except Exception as e:
            self.logger.error(f"权重衰减失败: {e}")
            return {'updated_count': 0, 'error': str(e)}
    
    @handle_memory_errors({'success': False, 'error': '数据库维护失败'})
    async def perform_database_maintenance(self) -> Dict[str, Any]:
        """
        执行数据库维护
        
        Returns:
            Dict: 维护结果
        """
        try:
            if not self.db_manager:
                return {'success': False, 'error': '数据库管理器未初始化'}
            
            maintenance_tasks = []
            
            # 1. VACUUM数据库
            try:
                self.db_manager.execute_query("VACUUM")
                maintenance_tasks.append("VACUUM完成")
            except Exception as e:
                maintenance_tasks.append(f"VACUUM失败: {e}")
            
            # 2. 重建索引
            try:
                self.db_manager.execute_query("REINDEX")
                maintenance_tasks.append("索引重建完成")
            except Exception as e:
                maintenance_tasks.append(f"索引重建失败: {e}")
            
            # 3. 更新统计信息
            try:
                self.db_manager.execute_query("ANALYZE")
                maintenance_tasks.append("统计信息更新完成")
            except Exception as e:
                maintenance_tasks.append(f"统计信息更新失败: {e}")
            
            # 4. 检查数据完整性
            try:
                result = self.db_manager.execute_query("PRAGMA integrity_check")
                if result and result[0][0] == "ok":
                    maintenance_tasks.append("数据完整性检查通过")
                else:
                    maintenance_tasks.append("数据完整性检查发现问题")
            except Exception as e:
                maintenance_tasks.append(f"数据完整性检查失败: {e}")
            
            self.logger.info(f"🔧 数据库维护完成: {len(maintenance_tasks)} 个任务")
            
            return {
                'success': True,
                'tasks': maintenance_tasks,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"数据库维护失败: {e}")
            return {'success': False, 'error': str(e)}
    
    @handle_memory_errors({'success': False, 'error': '备份失败'})
    async def backup_database(self) -> Dict[str, Any]:
        """
        备份数据库
        
        Returns:
            Dict: 备份结果
        """
        try:
            if not self.db_manager:
                return {'success': False, 'error': '数据库管理器未初始化'}
            
            # 生成备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"backups/memory_backup_{timestamp}.db"
            
            # 创建备份目录
            import os
            os.makedirs('backups', exist_ok=True)
            
            # 执行备份
            backup_query = f"VACUUM INTO '{backup_path}'"
            self.db_manager.execute_query(backup_query)
            
            self.logger.info(f"💾 数据库备份完成: {backup_path}")
            
            return {
                'success': True,
                'backup_path': backup_path,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"数据库备份失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_lifecycle_stats(self) -> Dict[str, Any]:
        """
        获取生命周期统计信息
        
        Returns:
            Dict: 生命周期统计
        """
        try:
            stats = {
                'timestamp': time.time(),
                'is_running': self.is_running,
                'config': self.lifecycle_config,
                'scheduled_tasks': {}
            }
            
            # 添加任务状态
            current_time = time.time()
            for task_name, task_info in self.scheduled_tasks.items():
                next_run = task_info['last_run'] + task_info['interval']
                stats['scheduled_tasks'][task_name] = {
                    'description': task_info['description'],
                    'interval': task_info['interval'],
                    'last_run': task_info['last_run'],
                    'next_run': next_run,
                    'overdue': current_time > next_run
                }
            
            # 如果有原始生命周期管理器，获取其统计信息
            if self.original_lifecycle:
                try:
                    original_stats = self.original_lifecycle.get_lifecycle_stats()
                    if isinstance(original_stats, dict):
                        stats['original_lifecycle'] = original_stats
                except Exception as e:
                    stats['original_lifecycle'] = {'error': str(e)}
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取生命周期统计失败: {e}")
            return {'error': str(e), 'timestamp': time.time()}
    
    async def force_cleanup(self) -> Dict[str, Any]:
        """强制执行清理"""
        return await self.cleanup_old_memories()
    
    async def force_archive(self) -> Dict[str, Any]:
        """强制执行归档"""
        return await self.archive_old_memories()
    
    async def force_maintenance(self) -> Dict[str, Any]:
        """强制执行维护"""
        return await self.perform_database_maintenance()