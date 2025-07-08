#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆生命周期管理模块
负责记忆的归档、恢复、清理等生命周期操作
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class LifecycleManager:
    """记忆生命周期管理器"""
    
    def __init__(self, db_manager, weight_manager=None):
        """
        初始化生命周期管理器
        
        Args:
            db_manager: 数据库管理器
            weight_manager: 权重管理器（可选）
        """
        self.db_manager = db_manager
        self.weight_manager = weight_manager
        self.logger = logger
        
        # 生命周期配置
        self.lifecycle_config = {
            'archive_threshold_days': 30,  # 归档阈值天数
            'cleanup_threshold_days': 90,  # 清理阈值天数
            'archive_weight_penalty': 0.5,  # 归档权重惩罚
            'restore_weight_bonus': 1.2,   # 恢复权重奖励
            'min_weight_for_permanent': 7.0,  # 永久保存的最低权重
            'batch_size': 100  # 批处理大小
        }
    
    def archive_old_memories(self, days_threshold: int = None, archive_weight_penalty: float = None) -> Dict[str, Any]:
        """
        归档过期记忆（软删除，不物理删除）
        
        Args:
            days_threshold: 归档天数阈值
            archive_weight_penalty: 归档权重惩罚系数
            
        Returns:
            Dict: 归档结果
        """
        try:
            # 使用默认配置
            days_threshold = days_threshold or self.lifecycle_config['archive_threshold_days']
            archive_weight_penalty = archive_weight_penalty or self.lifecycle_config['archive_weight_penalty']
            
            current_time = time.time()
            cutoff_time = current_time - (days_threshold * 24 * 3600)
            
            # 确保archived字段存在
            try:
                self.db_manager.execute_query("ALTER TABLE memories ADD COLUMN archived INTEGER DEFAULT 0")
            except:
                pass  # 字段可能已存在
            
            # 归档短期记忆（权重4.0以下）且超过阈值的记忆
            archive_query = """
                UPDATE memories 
                SET archived = 1,
                    weight = weight * ?,
                    metadata = CASE 
                        WHEN metadata IS NULL THEN ?
                        ELSE json_patch(metadata, ?)
                    END
                WHERE weight < 4.0 
                AND timestamp < ? 
                AND archived = 0
                AND type NOT IN ('system', 'summary')
            """
            
            metadata_json = json.dumps({
                "archived_at": current_time,
                "archive_reason": "automatic_cleanup",
                "original_weight": "preserved_in_calculation"
            })
            
            result = self.db_manager.execute_query(
                archive_query, 
                (archive_weight_penalty, metadata_json, metadata_json, cutoff_time)
            )
            
            archived_count = result.rowcount if result and hasattr(result, 'rowcount') else 0
            
            self.logger.info(f"归档了 {archived_count} 条过期短期记忆")
            
            return {
                'success': True,
                'archived_count': archived_count,
                'threshold_days': days_threshold,
                'weight_penalty': archive_weight_penalty,
                'message': f'成功归档 {archived_count} 条过期记忆'
            }
            
        except Exception as e:
            self.logger.error(f"归档过期记忆失败: {e}")
            return {'success': False, 'message': f'归档失败: {str(e)}'}
    
    def restore_archived_memories(self, memory_ids: List[str] = None, restore_weight_bonus: float = None) -> Dict[str, Any]:
        """
        恢复归档记忆
        
        Args:
            memory_ids: 要恢复的记忆ID列表，None表示恢复所有
            restore_weight_bonus: 恢复时的权重奖励系数
            
        Returns:
            Dict: 恢复结果
        """
        try:
            restore_weight_bonus = restore_weight_bonus or self.lifecycle_config['restore_weight_bonus']
            current_time = time.time()
            
            if memory_ids:
                # 恢复指定记忆
                placeholders = ','.join(['?' for _ in memory_ids])
                restore_query = f"""
                    UPDATE memories 
                    SET archived = 0,
                        weight = CASE 
                            WHEN weight * ? <= 10.0 THEN weight * ?
                            ELSE 10.0
                        END,
                        last_accessed = ?,
                        metadata = CASE 
                            WHEN metadata IS NULL THEN ?
                            ELSE json_patch(metadata, ?)
                        END
                    WHERE id IN ({placeholders}) AND archived = 1
                """
                
                metadata_json = json.dumps({
                    "restored_at": current_time,
                    "restore_reason": "manual_restore",
                    "weight_bonus_applied": restore_weight_bonus
                })
                
                params = [restore_weight_bonus, restore_weight_bonus, current_time, metadata_json, metadata_json] + memory_ids
            else:
                # 恢复所有归档记忆（慎用）
                restore_query = """
                    UPDATE memories 
                    SET archived = 0,
                        weight = CASE 
                            WHEN weight * ? <= 10.0 THEN weight * ?
                            ELSE 10.0
                        END,
                        last_accessed = ?,
                        metadata = CASE 
                            WHEN metadata IS NULL THEN ?
                            ELSE json_patch(metadata, ?)
                        END
                    WHERE archived = 1
                """
                
                metadata_json = json.dumps({
                    "restored_at": current_time,
                    "restore_reason": "batch_restore",
                    "weight_bonus_applied": restore_weight_bonus
                })
                
                params = [restore_weight_bonus, restore_weight_bonus, current_time, metadata_json, metadata_json]
            
            result = self.db_manager.execute_query(restore_query, params)
            restored_count = result.rowcount if result and hasattr(result, 'rowcount') else 0
            
            self.logger.info(f"恢复了 {restored_count} 条归档记忆")
            
            return {
                'success': True,
                'restored_count': restored_count,
                'weight_bonus': restore_weight_bonus,
                'message': f'成功恢复 {restored_count} 条归档记忆'
            }
            
        except Exception as e:
            self.logger.error(f"恢复归档记忆失败: {e}")
            return {'success': False, 'message': f'恢复失败: {str(e)}'}
    
    def cleanup_old_memories(self, days_threshold: int = None, permanent_delete: bool = False) -> Dict[str, Any]:
        """
        清理过期记忆（可选择永久删除）
        
        Args:
            days_threshold: 清理天数阈值
            permanent_delete: 是否永久删除（否则仅标记为已删除）
            
        Returns:
            Dict: 清理结果
        """
        try:
            days_threshold = days_threshold or self.lifecycle_config['cleanup_threshold_days']
            min_weight = self.lifecycle_config['min_weight_for_permanent']
            
            current_time = time.time()
            cutoff_time = current_time - (days_threshold * 24 * 3600)
            
            if permanent_delete:
                # 永久删除（只删除权重很低的记忆）
                cleanup_query = """
                    DELETE FROM memories 
                    WHERE weight < 2.0 
                    AND timestamp < ? 
                    AND archived = 1
                    AND type NOT IN ('system', 'summary')
                """
                
                result = self.db_manager.execute_query(cleanup_query, (cutoff_time,))
                cleaned_count = result.rowcount if result and hasattr(result, 'rowcount') else 0
                
                operation_type = "永久删除"
            else:
                # 软删除（标记为已删除）
                try:
                    self.db_manager.execute_query("ALTER TABLE memories ADD COLUMN deleted INTEGER DEFAULT 0")
                except:
                    pass  # 字段可能已存在
                
                cleanup_query = """
                    UPDATE memories 
                    SET deleted = 1,
                        metadata = CASE 
                            WHEN metadata IS NULL THEN ?
                            ELSE json_patch(metadata, ?)
                        END
                    WHERE weight < 2.0 
                    AND timestamp < ? 
                    AND archived = 1
                    AND deleted = 0
                    AND type NOT IN ('system', 'summary')
                """
                
                metadata_json = json.dumps({
                    "deleted_at": current_time,
                    "delete_reason": "automatic_cleanup",
                    "cleanup_threshold": days_threshold
                })
                
                result = self.db_manager.execute_query(
                    cleanup_query, 
                    (metadata_json, metadata_json, cutoff_time)
                )
                cleaned_count = result.rowcount if result and hasattr(result, 'rowcount') else 0
                
                operation_type = "软删除"
            
            self.logger.info(f"{operation_type}了 {cleaned_count} 条过期记忆")
            
            return {
                'success': True,
                'cleaned_count': cleaned_count,
                'operation_type': operation_type,
                'threshold_days': days_threshold,
                'permanent_delete': permanent_delete,
                'message': f'成功{operation_type} {cleaned_count} 条过期记忆'
            }
            
        except Exception as e:
            self.logger.error(f"清理过期记忆失败: {e}")
            return {'success': False, 'message': f'清理失败: {str(e)}'}
    
    def get_memory_lifecycle_stats(self) -> Dict[str, Any]:
        """
        获取记忆生命周期统计
        
        Returns:
            Dict: 生命周期统计信息
        """
        try:
            # 按权重范围统计记忆数量
            stats_query = """
                SELECT 
                    CASE 
                        WHEN weight >= 9.0 THEN '核心记忆'
                        WHEN weight >= 7.0 THEN '归档记忆'
                        WHEN weight >= 4.0 THEN '长期记忆'
                        ELSE '短期记忆'
                    END as layer,
                    COUNT(*) as count,
                    AVG(weight) as avg_weight,
                    MIN(timestamp) as oldest_timestamp,
                    MAX(timestamp) as newest_timestamp
                FROM memories 
                WHERE (archived IS NULL OR archived = 0)
                AND (deleted IS NULL OR deleted = 0)
                GROUP BY 
                    CASE 
                        WHEN weight >= 9.0 THEN '核心记忆'
                        WHEN weight >= 7.0 THEN '归档记忆'
                        WHEN weight >= 4.0 THEN '长期记忆'
                        ELSE '短期记忆'
                    END
            """
            
            results = self.db_manager.execute_query(stats_query)
            
            layer_stats = {}
            total_active = 0
            
            if results:
                for row in results:
                    layer = row[0]
                    count = row[1]
                    total_active += count
                    
                    layer_stats[layer] = {
                        'count': count,
                        'avg_weight': round(row[2], 2),
                        'oldest_days': int((time.time() - row[3]) / 86400) if row[3] else 0,
                        'newest_days': int((time.time() - row[4]) / 86400) if row[4] else 0
                    }
            
            # 获取归档和删除统计
            archive_query = """
                SELECT 
                    COUNT(*) as archived_count,
                    AVG(weight) as avg_archived_weight
                FROM memories 
                WHERE archived = 1
                AND (deleted IS NULL OR deleted = 0)
            """
            
            archive_result = self.db_manager.execute_query(archive_query)
            archived_count = archive_result[0][0] if archive_result else 0
            avg_archived_weight = archive_result[0][1] if archive_result and archive_result[0][1] else 0
            
            delete_query = """
                SELECT COUNT(*) as deleted_count
                FROM memories 
                WHERE deleted = 1
            """
            
            delete_result = self.db_manager.execute_query(delete_query)
            deleted_count = delete_result[0][0] if delete_result else 0
            
            return {
                'layer_statistics': layer_stats,
                'total_active_memories': total_active,
                'archived_memories': {
                    'count': archived_count,
                    'avg_weight': round(avg_archived_weight, 2)
                },
                'deleted_memories': {
                    'count': deleted_count
                },
                'lifecycle_config': self.lifecycle_config,
                'last_updated': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"获取生命周期统计失败: {e}")
            return {'error': str(e)}
    
    def schedule_lifecycle_maintenance(self) -> Dict[str, Any]:
        """
        执行定期生命周期维护
        
        Returns:
            Dict: 维护结果
        """
        try:
            maintenance_results = {
                'archive_result': None,
                'cleanup_result': None,
                'start_time': time.time(),
                'end_time': None,
                'total_processed': 0
            }
            
            # 1. 归档过期记忆
            self.logger.info("开始归档过期记忆")
            archive_result = self.archive_old_memories()
            maintenance_results['archive_result'] = archive_result
            
            if archive_result['success']:
                maintenance_results['total_processed'] += archive_result['archived_count']
            
            # 2. 清理非常旧的记忆（软删除）
            self.logger.info("开始清理过期记忆")
            cleanup_result = self.cleanup_old_memories(permanent_delete=False)
            maintenance_results['cleanup_result'] = cleanup_result
            
            if cleanup_result['success']:
                maintenance_results['total_processed'] += cleanup_result['cleaned_count']
            
            # 3. 更新权重（如果有权重管理器）
            if self.weight_manager:
                self.logger.info("开始更新记忆权重")
                # 这里可以实现批量权重更新逻辑
                pass
            
            maintenance_results['end_time'] = time.time()
            maintenance_results['duration'] = maintenance_results['end_time'] - maintenance_results['start_time']
            
            success = (archive_result.get('success', False) and 
                      cleanup_result.get('success', False))
            
            return {
                'success': success,
                'maintenance_results': maintenance_results,
                'message': f'维护完成，共处理 {maintenance_results["total_processed"]} 条记忆'
            }
            
        except Exception as e:
            self.logger.error(f"生命周期维护失败: {e}")
            return {'success': False, 'message': f'维护失败: {str(e)}'}
    
    def get_lifecycle_recommendations(self) -> Dict[str, Any]:
        """
        获取生命周期维护建议
        
        Returns:
            Dict: 维护建议
        """
        try:
            recommendations = []
            stats = self.get_memory_lifecycle_stats()
            
            if 'error' in stats:
                return {'error': stats['error']}
            
            # 检查短期记忆数量
            short_term_count = stats['layer_statistics'].get('短期记忆', {}).get('count', 0)
            total_active = stats['total_active_memories']
            
            if total_active > 0:
                short_term_ratio = short_term_count / total_active
                if short_term_ratio > 0.6:  # 短期记忆超过60%
                    recommendations.append({
                        'type': 'archive',
                        'priority': 'medium',
                        'message': f'短期记忆比例过高 ({short_term_ratio:.1%})，建议执行归档操作',
                        'action': 'archive_old_memories'
                    })
            
            # 检查归档记忆数量
            archived_count = stats['archived_memories']['count']
            if archived_count > 1000:  # 归档记忆超过1000条
                recommendations.append({
                    'type': 'cleanup',
                    'priority': 'low',
                    'message': f'归档记忆数量较多 ({archived_count})，建议定期清理',
                    'action': 'cleanup_old_memories'
                })
            
            # 检查核心记忆比例
            core_count = stats['layer_statistics'].get('核心记忆', {}).get('count', 0)
            if total_active > 0:
                core_ratio = core_count / total_active
                if core_ratio > 0.15:  # 核心记忆超过15%
                    recommendations.append({
                        'type': 'weight_adjustment',
                        'priority': 'medium',
                        'message': f'核心记忆比例过高 ({core_ratio:.1%})，建议调整权重策略',
                        'action': 'review_weight_thresholds'
                    })
            
            return {
                'recommendations': recommendations,
                'stats_summary': stats,
                'check_time': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"获取生命周期建议失败: {e}")
            return {'error': str(e)}
    
    def validate_lifecycle_health(self) -> Dict[str, Any]:
        """
        验证生命周期系统健康状况
        
        Returns:
            Dict: 健康检查结果
        """
        try:
            health_issues = []
            warnings = []
            
            stats = self.get_memory_lifecycle_stats()
            
            if 'error' in stats:
                return {'status': 'error', 'message': stats['error']}
            
            # 检查数据完整性
            total_active = stats['total_active_memories']
            archived_count = stats['archived_memories']['count']
            deleted_count = stats['deleted_memories']['count']
            
            if total_active == 0:
                health_issues.append("没有活跃记忆")
            
            # 检查归档状态
            if archived_count > total_active * 2:
                warnings.append(f"归档记忆数量 ({archived_count}) 远超活跃记忆 ({total_active})")
            
            # 检查删除状态
            if deleted_count > 0:
                warnings.append(f"存在 {deleted_count} 条已删除记忆")
            
            # 检查权重分布
            layer_stats = stats['layer_statistics']
            if '短期记忆' in layer_stats:
                short_term_count = layer_stats['短期记忆']['count']
                if short_term_count > total_active * 0.8:
                    health_issues.append(f"短期记忆占比过高: {short_term_count}/{total_active}")
            
            # 确定健康状态
            if health_issues:
                health_status = 'unhealthy'
            elif warnings:
                health_status = 'warning'
            else:
                health_status = 'healthy'
            
            return {
                'status': health_status,
                'issues': health_issues,
                'warnings': warnings,
                'statistics': stats,
                'check_time': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"生命周期健康检查失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'check_time': time.time()
            } 