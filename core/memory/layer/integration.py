#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层记忆系统集成

将分层系统与现有记忆系统无缝集成的核心模块
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .types import MemoryLayer, LayerConfig
from .manager import LayeredMemoryManager
from .lifecycle import MemoryLifecycleManager
from .sync import WeightLayerSynchronizer
from .retrieval import LayeredRetrievalEnhancer
from .config import LayerConfigManager, get_config_manager
from .monitoring import LayerMonitor

logger = logging.getLogger(__name__)


class LayeredMemoryIntegration:
    """分层记忆系统集成器"""
    
    def __init__(self, db_manager, vectorizer=None, config_manager: LayerConfigManager = None):
        """初始化分层集成系统"""
        self.db_manager = db_manager
        self.vectorizer = vectorizer
        
        # 配置管理
        self.config_manager = config_manager or get_config_manager()
        
        # 核心组件
        self.layer_manager = LayeredMemoryManager(db_manager, self.config_manager)
        self.lifecycle_manager = MemoryLifecycleManager(self.layer_manager, self.config_manager)
        self.synchronizer = WeightLayerSynchronizer(self.layer_manager)
        self.retrieval_enhancer = LayeredRetrievalEnhancer(self.layer_manager)
        self.monitor = LayerMonitor(self.layer_manager, self.config_manager)
        
        # 状态标志
        self._initialized = False
        self._maintenance_task = None
        
        logger.info("分层记忆系统集成器已创建")
    
    async def initialize(self) -> bool:
        """初始化分层系统"""
        try:
            if self._initialized:
                logger.warning("分层系统已经初始化")
                return True
            
            logger.info("开始初始化分层记忆系统...")
            
            # 1. 确保数据库表存在
            if not await self._ensure_database_schema():
                logger.error("数据库模式初始化失败")
                return False
            
            # 2. 执行初始同步
            if not await self._perform_initial_sync():
                logger.error("初始同步失败")
                return False
            
            # 3. 启动维护任务
            if self.config_manager.get_system_config().auto_maintenance_enabled:
                await self._start_maintenance_task()
            
            self._initialized = True
            logger.info("分层记忆系统初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"分层系统初始化失败: {e}")
            return False
    
    async def shutdown(self):
        """关闭分层系统"""
        try:
            logger.info("开始关闭分层记忆系统...")
            
            # 停止维护任务
            if self._maintenance_task and not self._maintenance_task.done():
                self._maintenance_task.cancel()
                try:
                    await self._maintenance_task
                except asyncio.CancelledError:
                    pass
            
            self._initialized = False
            logger.info("分层记忆系统已关闭")
            
        except Exception as e:
            logger.error(f"关闭分层系统失败: {e}")
    
    def enhance_memory_storage(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """增强记忆存储（集成到现有存储流程）"""
        try:
            if not self._initialized:
                logger.warning("分层系统未初始化，跳过分层处理")
                return memory_data
            
            memory_id = memory_data.get('id')
            weight = memory_data.get('weight', 1.0)
            
            if memory_id and weight is not None:
                # 分配层级
                layer_info = self.layer_manager.assign_layer(memory_id, weight)
                
                # 添加分层信息到记忆数据
                memory_data['layer_info'] = {
                    'layer': layer_info.layer.value,
                    'weight': layer_info.weight,
                    'created_at': layer_info.created_at.isoformat(),
                    'promotion_score': layer_info.promotion_score
                }
                
                logger.debug(f"记忆 {memory_id} 已分配到 {layer_info.layer.value} 层级")
            
            return memory_data
            
        except Exception as e:
            logger.error(f"增强记忆存储失败: {e}")
            return memory_data
    
    def enhance_memory_retrieval(self, memory_ids: List[str], 
                                query_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """增强记忆检索（集成到现有检索流程）"""
        try:
            if not self._initialized or not memory_ids:
                return []
            
            # 确定查询类型和层级优先级
            query_type = self._determine_query_type(query_context)
            layer_priority = self.retrieval_enhancer.smart_layer_selection(query_type)
            
            # 使用分层信息增强检索
            enhanced_memories = self.retrieval_enhancer.enhance_retrieval_with_layers(
                memory_ids=memory_ids,
                layer_priority=layer_priority,
                max_per_layer=self.config_manager.get_system_config().default_max_per_layer
            )
            
            logger.debug(f"分层检索增强: {len(memory_ids)} -> {len(enhanced_memories)} 条记忆")
            return enhanced_memories
            
        except Exception as e:
            logger.error(f"增强记忆检索失败: {e}")
            return []
    
    def enhance_context_building(self, user_input: str, 
                                context_memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """增强上下文构建（集成到现有上下文构建流程）"""
        try:
            if not self._initialized:
                return {'user_input': user_input, 'memories': context_memories}
            
            # 构建层级感知的上下文
            layered_context = self.retrieval_enhancer.get_layer_aware_context(
                user_input, context_memories
            )
            
            # 添加系统统计信息
            system_metrics = self.monitor.get_system_metrics(use_cache=True)
            layered_context['system_info'] = {
                'total_memories': system_metrics.total_memories,
                'sync_status': system_metrics.sync_status,
                'layer_distribution': {
                    layer.value: metrics.total_memories 
                    for layer, metrics in system_metrics.layer_metrics.items()
                }
            }
            
            return layered_context
            
        except Exception as e:
            logger.error(f"增强上下文构建失败: {e}")
            return {'user_input': user_input, 'memories': context_memories}
    
    def update_memory_access(self, memory_id: str, access_context: Dict[str, Any] = None):
        """更新记忆访问信息（集成到现有访问跟踪）"""
        try:
            if not self._initialized or not memory_id:
                return
            
            # 更新分层访问信息
            self.layer_manager.update_access(memory_id)
            
            logger.debug(f"已更新记忆 {memory_id} 的访问信息")
            
        except Exception as e:
            logger.error(f"更新记忆访问失败: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态（用于监控和调试）"""
        try:
            if not self._initialized:
                return {'status': 'not_initialized'}
            
            # 获取系统指标
            system_metrics = self.monitor.get_system_metrics(use_cache=True)
            health_status = self.monitor.get_layer_health_status()
            capacity_alerts = self.monitor.get_capacity_alerts()
            
            return {
                'status': 'initialized',
                'system_metrics': system_metrics,
                'health_status': {layer.value: status for layer, status in health_status.items()},
                'capacity_alerts': capacity_alerts,
                'config': self.config_manager.export_config()
            }
            
        except Exception as e:
            logger.error(f"获取系统状态失败: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def run_maintenance(self, force: bool = False) -> Dict[str, Any]:
        """运行维护操作"""
        try:
            if not self._initialized:
                return {'success': False, 'error': '系统未初始化'}
            
            logger.info("开始运行分层系统维护...")
            
            # 执行维护操作
            maintenance_result = await self.lifecycle_manager.run_maintenance()
            
            # 执行同步检查
            sync_result = await self.synchronizer.sync_all_memories()
            
            # 合并结果
            result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'maintenance': maintenance_result,
                'sync': sync_result
            }
            
            logger.info("分层系统维护完成")
            return result
            
        except Exception as e:
            logger.error(f"运行维护失败: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _ensure_database_schema(self) -> bool:
        """确保数据库模式存在"""
        try:
            # 这里调用 layer_manager 的初始化方法
            # layer_manager 会确保 memory_layers 表存在
            return True
        except Exception as e:
            logger.error(f"确保数据库模式失败: {e}")
            return False
    
    async def _perform_initial_sync(self) -> bool:
        """执行初始同步"""
        try:
            logger.info("开始执行初始同步...")
            
            # 检查是否需要同步
            sync_stats = await self.synchronizer.get_sync_statistics()
            
            if sync_stats['unsynced_memories'] > 0:
                logger.info(f"发现 {sync_stats['unsynced_memories']} 条未同步记忆，开始同步...")
                
                # 执行批量同步
                sync_result = await self.synchronizer.sync_all_memories()
                
                if sync_result['success']:
                    logger.info(f"初始同步完成，同步了 {sync_result['synced_count']} 条记忆")
                    return True
                else:
                    logger.error(f"初始同步失败: {sync_result.get('error', '未知错误')}")
                    return False
            else:
                logger.info("所有记忆已同步，跳过初始同步")
                return True
                
        except Exception as e:
            logger.error(f"执行初始同步失败: {e}")
            return False
    
    async def _start_maintenance_task(self):
        """启动维护任务"""
        try:
            maintenance_interval = self.config_manager.get_system_config().maintenance_interval_hours
            
            async def maintenance_loop():
                while True:
                    try:
                        await asyncio.sleep(maintenance_interval * 3600)  # 转换为秒
                        await self.run_maintenance()
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        logger.error(f"维护任务执行失败: {e}")
            
            self._maintenance_task = asyncio.create_task(maintenance_loop())
            logger.info(f"维护任务已启动，间隔 {maintenance_interval} 小时")
            
        except Exception as e:
            logger.error(f"启动维护任务失败: {e}")
    
    def _determine_query_type(self, query_context: Dict[str, Any] = None) -> str:
        """确定查询类型"""
        if not query_context:
            return "general"
        
        # 根据上下文确定查询类型
        # 这里可以根据实际需求扩展更复杂的逻辑
        query_text = query_context.get('user_input', '').lower()
        
        if any(keyword in query_text for keyword in ['我的', '个人', '信息', '资料']):
            return "personal_info"
        elif any(keyword in query_text for keyword in ['刚才', '最近', '今天', '昨天']):
            return "recent_chat"
        elif any(keyword in query_text for keyword in ['知识', '学习', '了解', '什么是']):
            return "knowledge"
        else:
            return "general"


# 全局集成实例
_global_integration: Optional[LayeredMemoryIntegration] = None


def get_layered_integration() -> Optional[LayeredMemoryIntegration]:
    """获取全局分层集成实例"""
    return _global_integration


def set_layered_integration(integration: LayeredMemoryIntegration):
    """设置全局分层集成实例"""
    global _global_integration
    _global_integration = integration


async def initialize_layered_memory_system(db_manager, vectorizer=None, 
                                         config_manager: LayerConfigManager = None) -> LayeredMemoryIntegration:
    """初始化分层记忆系统"""
    try:
        integration = LayeredMemoryIntegration(db_manager, vectorizer, config_manager)
        
        if await integration.initialize():
            set_layered_integration(integration)
            logger.info("分层记忆系统初始化成功")
            return integration
        else:
            logger.error("分层记忆系统初始化失败")
            return None
            
    except Exception as e:
        logger.error(f"初始化分层记忆系统失败: {e}")
        return None