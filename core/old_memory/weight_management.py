#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
权重管理模块
负责记忆权重的动态调整和生命周期管理
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class WeightManager:
    """权重管理器 - 优化版本"""
    
    def __init__(self, db_manager):
        """
        初始化权重管理器
        
        Args:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager
        self.logger = logger
        
        # 🔥 优化：权重调整参数（降低增益幅度）
        self.weight_config = {
            'max_change_per_update': 0.5,  # 单次最大变化量
            'decay_rates': {
                'core': 0.999,      # 核心记忆：每天衰减0.1%
                'archive': 0.995,   # 归档记忆：每天衰减0.5%
                'long_term': 0.99,  # 长期记忆：每天衰减1%
                'short_term': 0.97  # 短期记忆：每天衰减3%
            },
            'access_bonus': {
                'recent': 1.02,     # 最近访问：增加2%
                'frequent': 1.05,   # 频繁访问：增加5%
                'rare': 0.99        # 很少访问：减少1%
            }
        }
    
    def update_memory_weight_dynamically(self, memory_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        动态更新记忆权重（优化版本）
        
        Args:
            memory_id: 记忆ID
            context: 上下文信息
            
        Returns:
            Dict: 更新结果
        """
        if not self.db_manager:
            return {'success': False, 'message': '数据库未初始化'}
        
        try:
            # 获取当前记忆信息
            memory_query = "SELECT * FROM memories WHERE id = ?"
            result = self.db_manager.execute_query(memory_query, (memory_id,))
            
            if not result:
                return {'success': False, 'message': '记忆不存在'}
            
            memory = result[0]
            current_weight = memory[6]  # weight字段
            current_time = time.time()
            
            # 🔥 优化：简化权重计算
            new_weight = self._calculate_optimized_weight(memory, current_time, context)
            
            # 🔥 限制权重变化幅度
            weight_change = new_weight - current_weight
            if abs(weight_change) > self.weight_config['max_change_per_update']:
                if weight_change > 0:
                    new_weight = current_weight + self.weight_config['max_change_per_update']
                else:
                    new_weight = current_weight - self.weight_config['max_change_per_update']
            
            # 确保权重在合理范围
            new_weight = max(0.1, min(10.0, new_weight))
            
            # 更新记忆权重
            self._update_memory_weight(memory_id, new_weight, current_time, {
                'previous_weight': current_weight,
                'change_reason': context.get('change_reason', 'dynamic_update') if context else 'dynamic_update'
            })
            
            self.logger.debug(f"记忆 {memory_id} 权重更新: {current_weight:.2f} → {new_weight:.2f}")
            
            return {
                'success': True,
                'memory_id': memory_id,
                'old_weight': current_weight,
                'new_weight': new_weight,
                'weight_change': new_weight - current_weight,
                'message': f'权重更新成功: {current_weight:.2f} → {new_weight:.2f}'
            }
            
        except Exception as e:
            self.logger.error(f"动态权重更新失败: {e}")
            return {'success': False, 'message': f'更新失败: {str(e)}'}
    
    def _calculate_optimized_weight(self, memory: Any, current_time: float, context: Dict[str, Any] = None) -> float:
        """
        计算优化后的权重（简化版本）
        
        Args:
            memory: 记忆数据
            current_time: 当前时间
            context: 上下文信息
            
        Returns:
            float: 新权重
        """
        current_weight = memory[6]
        creation_time = memory[5]
        last_accessed = memory[9] if memory[9] else creation_time
        
        # 1. 基于时间的自然衰减
        age_days = (current_time - creation_time) / 86400
        if age_days > 0:
            layer = self._get_memory_layer(current_weight)
            decay_rate = self.weight_config['decay_rates'].get(layer, 0.98)
            time_factor = decay_rate ** age_days
        else:
            time_factor = 1.0
        
        # 2. 基于访问频率的调整
        hours_since_access = (current_time - last_accessed) / 3600
        if hours_since_access < 6:  # 6小时内访问过
            access_factor = self.weight_config['access_bonus']['recent']
        elif hours_since_access < 72:  # 3天内访问过
            access_factor = self.weight_config['access_bonus']['frequent']
        else:
            access_factor = self.weight_config['access_bonus']['rare']
        
        # 3. 上下文相关性（简化版本）
        context_factor = 1.0
        if context:
            search_type = context.get('search_type', '')
            if search_type == 'keyword':
                context_factor = 1.02  # 关键词匹配，轻微增强
            elif search_type == 'core_memories':
                context_factor = 1.01  # 核心记忆搜索，保持稳定
        
        # 综合计算新权重
        new_weight = current_weight * time_factor * access_factor * context_factor
        
        return new_weight
    
    def _update_memory_weight(self, memory_id: str, new_weight: float, timestamp: float, metadata: Dict[str, Any]):
        """更新记忆权重到数据库"""
        try:
            update_query = """
                UPDATE memories 
                SET weight = ?, 
                    last_accessed = ?,
                    metadata = CASE 
                        WHEN metadata IS NULL THEN ?
                        ELSE json_patch(metadata, ?)
                    END
                WHERE id = ?
            """
            
            metadata_json = json.dumps({
                "last_weight_update": timestamp,
                "weight_history": metadata
            })
            
            self.db_manager.execute_query(
                update_query, 
                (new_weight, timestamp, metadata_json, metadata_json, memory_id)
            )
            
        except Exception as e:
            self.logger.error(f"更新记忆权重失败: {e}")
    
    def get_memory_layer(self, weight: float) -> str:
        """根据权重确定记忆层级"""
        return self._get_memory_layer(weight)
    
    def _get_memory_layer(self, weight: float) -> str:
        """内部方法：根据权重确定记忆层级"""
        if 9.0 <= weight <= 10.0:
            return "core"  # 核心记忆
        elif 7.0 <= weight < 9.0:
            return "archive"  # 归档记忆
        elif 4.0 <= weight < 7.0:
            return "long_term"  # 长期记忆
        else:
            return "short_term"  # 短期记忆
    
    def get_layered_context_info(self, memories: List[Dict]) -> Dict[str, Any]:
        """
        获取分层上下文信息
        
        Args:
            memories: 记忆列表
            
        Returns:
            Dict: 分层统计信息
        """
        if not memories:
            return {}
        
        layer_stats = {
            "核心记忆": [],
            "归档记忆": [],
            "长期记忆": [],
            "短期记忆": []
        }
        
        for memory in memories:
            weight = memory.get('weight', 1.0)
            layer = self._get_memory_layer_name(weight)
            layer_stats[layer].append(memory)
        
        return {
            'layer_distribution': {
                layer: len(memories_in_layer) 
                for layer, memories_in_layer in layer_stats.items()
            },
            'layered_memories': layer_stats
        }
    
    def _get_memory_layer_name(self, weight: float) -> str:
        """根据权重确定记忆层级名称（中文）"""
        if 9.0 <= weight <= 10.0:
            return "核心记忆"
        elif 7.0 <= weight < 9.0:
            return "归档记忆"
        elif 4.0 <= weight < 7.0:
            return "长期记忆"
        else:
            return "短期记忆"
    
    def batch_update_weights(self, memory_ids: List[str], reason: str = "batch_update") -> Dict[str, Any]:
        """
        批量更新记忆权重
        
        Args:
            memory_ids: 记忆ID列表
            reason: 更新原因
            
        Returns:
            Dict: 更新结果
        """
        if not memory_ids:
            return {'success': False, 'message': '没有提供记忆ID'}
        
        try:
            updated_count = 0
            failed_count = 0
            
            for memory_id in memory_ids:
                result = self.update_memory_weight_dynamically(
                    memory_id, 
                    context={'change_reason': reason}
                )
                
                if result['success']:
                    updated_count += 1
                else:
                    failed_count += 1
            
            return {
                'success': True,
                'updated_count': updated_count,
                'failed_count': failed_count,
                'total_count': len(memory_ids),
                'message': f'批量更新完成: 成功 {updated_count}，失败 {failed_count}'
            }
            
        except Exception as e:
            self.logger.error(f"批量更新权重失败: {e}")
            return {'success': False, 'message': f'批量更新失败: {str(e)}'}
    
    def get_weight_statistics(self) -> Dict[str, Any]:
        """
        获取权重统计信息
        
        Returns:
            Dict: 权重统计
        """
        try:
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
                    MIN(weight) as min_weight,
                    MAX(weight) as max_weight
                FROM memories 
                WHERE (archived IS NULL OR archived = 0)
                GROUP BY 
                    CASE 
                        WHEN weight >= 9.0 THEN '核心记忆'
                        WHEN weight >= 7.0 THEN '归档记忆'
                        WHEN weight >= 4.0 THEN '长期记忆'
                        ELSE '短期记忆'
                    END
            """
            
            results = self.db_manager.execute_query(stats_query)
            
            stats = {}
            total_memories = 0
            
            if results:
                for row in results:
                    layer = row[0]
                    count = row[1]
                    total_memories += count
                    
                    stats[layer] = {
                        'count': count,
                        'avg_weight': round(row[2], 2),
                        'min_weight': round(row[3], 2),
                        'max_weight': round(row[4], 2)
                    }
            
            return {
                'layer_statistics': stats,
                'total_memories': total_memories,
                'weight_config': self.weight_config,
                'last_updated': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"获取权重统计失败: {e}")
            return {'error': str(e)}
    
    def validate_weight_health(self) -> Dict[str, Any]:
        """
        验证权重系统健康状况
        
        Returns:
            Dict: 健康检查结果
        """
        try:
            # 检查权重分布
            stats = self.get_weight_statistics()
            
            health_issues = []
            recommendations = []
            
            # 检查是否有过多的高权重记忆
            layer_stats = stats.get('layer_statistics', {})
            core_count = layer_stats.get('核心记忆', {}).get('count', 0)
            total_count = stats.get('total_memories', 0)
            
            if total_count > 0:
                core_ratio = core_count / total_count
                if core_ratio > 0.1:  # 核心记忆超过10%
                    health_issues.append(f"核心记忆比例过高: {core_ratio:.1%}")
                    recommendations.append("考虑降低部分核心记忆的权重")
            
            # 检查权重异常值
            abnormal_weights_query = """
                SELECT id, weight FROM memories 
                WHERE weight < 0.1 OR weight > 10.0
                AND (archived IS NULL OR archived = 0)
            """
            
            abnormal_results = self.db_manager.execute_query(abnormal_weights_query)
            
            if abnormal_results:
                health_issues.append(f"发现 {len(abnormal_results)} 个异常权重记忆")
                recommendations.append("修正异常权重值")
            
            # 生成健康报告
            health_status = "healthy" if not health_issues else "needs_attention"
            
            return {
                'status': health_status,
                'issues': health_issues,
                'recommendations': recommendations,
                'statistics': stats,
                'check_time': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"权重健康检查失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'check_time': time.time()
            } 