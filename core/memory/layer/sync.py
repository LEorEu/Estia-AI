#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权重与分层同步器

确保现有权重系统与分层系统的双向同步
"""

import logging
from typing import List, Dict, Optional
from .types import MemoryLayer, LayerInfo
from .manager import LayeredMemoryManager

logger = logging.getLogger(__name__)


class WeightLayerSynchronizer:
    """权重与分层同步器"""
    
    def __init__(self, layer_manager: LayeredMemoryManager):
        self.layer_manager = layer_manager
        self.db_manager = layer_manager.db_manager
        
    def sync_weight_to_layer(self, memory_id: str, new_weight: float) -> MemoryLayer:
        """权重变化时同步到分层系统"""
        try:
            # 根据新权重确定层级
            new_layer = MemoryLayer.from_weight(new_weight)
            
            # 更新分层信息
            self.layer_manager.assign_layer(memory_id, new_weight, new_layer)
            
            logger.debug(f"权重同步: 记忆 {memory_id} 权重 {new_weight} -> 层级 {new_layer.value}")
            return new_layer
            
        except Exception as e:
            logger.error(f"权重同步失败: {e}")
            return MemoryLayer.SHORT_TERM
    
    def sync_layer_to_weight(self, memory_id: str, new_layer: MemoryLayer) -> float:
        """分层变化时同步到权重系统"""
        try:
            # 获取当前权重
            current_info = self.layer_manager.get_layer_info(memory_id)
            current_weight = current_info.weight if current_info else 5.0
            
            # 计算新权重（在目标层级范围内）
            min_weight, max_weight = new_layer.weight_range
            
            # 保持在合理范围内，优先保持原权重的相对位置
            if min_weight <= current_weight <= max_weight:
                new_weight = current_weight
            else:
                # 映射到新范围的中位数
                new_weight = (min_weight + max_weight) / 2
            
            # 更新memories表的权重
            self.db_manager.execute(
                "UPDATE memories SET weight = ? WHERE id = ?",
                (new_weight, memory_id)
            )
            
            # 更新分层信息
            self.layer_manager.assign_layer(memory_id, new_weight, new_layer)
            
            logger.debug(f"分层同步: 记忆 {memory_id} 层级 {new_layer.value} -> 权重 {new_weight}")
            return new_weight
            
        except Exception as e:
            logger.error(f"分层同步失败: {e}")
            return 5.0
    
    def batch_sync_existing_memories(self) -> Dict[str, int]:
        """批量同步现有记忆到分层系统"""
        sync_stats = {layer.value: 0 for layer in MemoryLayer}
        
        try:
            # 获取所有未分层的记忆
            unsynced_memories = self._get_unsynced_memories()
            
            for memory_id, weight in unsynced_memories:
                layer = self.sync_weight_to_layer(memory_id, weight)
                sync_stats[layer.value] += 1
            
            logger.info(f"批量同步完成: {sync_stats}")
            return sync_stats
            
        except Exception as e:
            logger.error(f"批量同步失败: {e}")
            return sync_stats
    
    def validate_sync_consistency(self) -> Dict[str, any]:
        """验证同步一致性"""
        try:
            inconsistencies = []
            total_checked = 0
            
            # 检查所有已分层的记忆
            layered_memories = self.db_manager.query(
                "SELECT ml.memory_id, ml.layer, ml.weight, m.weight FROM memory_layers ml JOIN memories m ON ml.memory_id = m.id"
            )
            
            for memory_id, layer_str, layer_weight, memory_weight in layered_memories:
                total_checked += 1
                layer = MemoryLayer(layer_str)
                expected_layer = MemoryLayer.from_weight(memory_weight)
                
                # 检查权重一致性
                if abs(layer_weight - memory_weight) > 0.1:
                    inconsistencies.append({
                        'memory_id': memory_id,
                        'type': 'weight_mismatch',
                        'layer_weight': layer_weight,
                        'memory_weight': memory_weight
                    })
                
                # 检查分层一致性
                if layer != expected_layer:
                    inconsistencies.append({
                        'memory_id': memory_id,
                        'type': 'layer_mismatch',
                        'current_layer': layer.value,
                        'expected_layer': expected_layer.value
                    })
            
            return {
                'total_checked': total_checked,
                'inconsistencies': inconsistencies,
                'consistency_rate': (total_checked - len(inconsistencies)) / max(total_checked, 1)
            }
            
        except Exception as e:
            logger.error(f"一致性验证失败: {e}")
            return {'error': str(e)}
    
    def fix_inconsistencies(self) -> Dict[str, int]:
        """修复同步不一致问题"""
        fix_stats = {'weight_fixed': 0, 'layer_fixed': 0}
        
        try:
            validation_result = self.validate_sync_consistency()
            inconsistencies = validation_result.get('inconsistencies', [])
            
            for issue in inconsistencies:
                memory_id = issue['memory_id']
                
                if issue['type'] == 'weight_mismatch':
                    # 以memories表的权重为准
                    memory_weight = issue['memory_weight']
                    self.sync_weight_to_layer(memory_id, memory_weight)
                    fix_stats['weight_fixed'] += 1
                    
                elif issue['type'] == 'layer_mismatch':
                    # 以权重推导的层级为准
                    expected_layer = MemoryLayer(issue['expected_layer'])
                    self.sync_layer_to_weight(memory_id, expected_layer)
                    fix_stats['layer_fixed'] += 1
            
            logger.info(f"不一致修复完成: {fix_stats}")
            return fix_stats
            
        except Exception as e:
            logger.error(f"修复不一致失败: {e}")
            return fix_stats
    
    def _get_unsynced_memories(self) -> List[tuple]:
        """获取未同步的记忆"""
        try:
            # 查找在memories表中但不在memory_layers表中的记忆
            result = self.db_manager.query("""
                SELECT m.id, m.weight 
                FROM memories m 
                LEFT JOIN memory_layers ml ON m.id = ml.memory_id 
                WHERE ml.memory_id IS NULL
            """)
            
            return [(row[0], row[1]) for row in result]
            
        except Exception as e:
            logger.error(f"获取未同步记忆失败: {e}")
            return []
    
    def get_sync_statistics(self) -> Dict[str, any]:
        """获取同步统计信息"""
        try:
            # 总记忆数
            total_memories = self.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
            
            # 已分层记忆数
            layered_memories = self.db_manager.query("SELECT COUNT(*) FROM memory_layers")[0][0]
            
            # 各层级分布
            layer_distribution = {}
            for layer in MemoryLayer:
                count = self.db_manager.query(
                    "SELECT COUNT(*) FROM memory_layers WHERE layer = ?",
                    (layer.value,)
                )[0][0]
                layer_distribution[layer.value] = count
            
            # 一致性检查
            consistency = self.validate_sync_consistency()
            
            return {
                'total_memories': total_memories,
                'layered_memories': layered_memories,
                'sync_rate': layered_memories / max(total_memories, 1),
                'layer_distribution': layer_distribution,
                'consistency_rate': consistency.get('consistency_rate', 0),
                'inconsistencies_count': len(consistency.get('inconsistencies', []))
            }
            
        except Exception as e:
            logger.error(f"获取同步统计失败: {e}")
            return {'error': str(e)}