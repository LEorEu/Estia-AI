#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆生命周期管理器

负责记忆的自动清理、提升和降级
"""

import logging
import time
from typing import List, Dict, Any
from .types import MemoryLayer, LayerConfig, LayerInfo
from .manager import LayeredMemoryManager

logger = logging.getLogger(__name__)


class MemoryLifecycleManager:
    """记忆生命周期管理器"""
    
    def __init__(self, layer_manager: LayeredMemoryManager):
        self.layer_manager = layer_manager
        self.config = layer_manager.config
        self.db_manager = layer_manager.db_manager
        
    def cleanup_expired_memories(self) -> Dict[str, int]:
        """清理过期记忆"""
        cleanup_stats = {layer.value: 0 for layer in MemoryLayer}
        
        try:
            for layer in MemoryLayer:
                if layer.retention_days is None:
                    continue  # 跳过永久保留的层级
                
                expired_memories = self._find_expired_memories(layer)
                
                for memory_info in expired_memories:
                    if self._should_demote_instead_of_delete(memory_info):
                        # 降级而不是删除
                        self._demote_memory(memory_info)
                    else:
                        # 删除记忆
                        self._delete_memory(memory_info.memory_id)
                        cleanup_stats[layer.value] += 1
            
            logger.info(f"清理完成: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"清理过期记忆失败: {e}")
            return cleanup_stats
    
    def promote_memories(self) -> Dict[str, int]:
        """提升高价值记忆"""
        promotion_stats = {layer.value: 0 for layer in MemoryLayer}
        
        if not self.config.auto_promotion_enabled:
            return promotion_stats
        
        try:
            # 从低层级向高层级提升
            layers_to_check = [MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM, MemoryLayer.ARCHIVE]
            
            for layer in layers_to_check:
                candidates = self._find_promotion_candidates(layer)
                
                for memory_info in candidates:
                    new_layer = self._calculate_target_layer(memory_info)
                    if new_layer != memory_info.layer:
                        self._promote_memory(memory_info, new_layer)
                        promotion_stats[layer.value] += 1
            
            logger.info(f"提升完成: {promotion_stats}")
            return promotion_stats
            
        except Exception as e:
            logger.error(f"记忆提升失败: {e}")
            return promotion_stats
    
    def balance_layer_capacity(self) -> Dict[str, int]:
        """平衡各层级容量"""
        balance_stats = {layer.value: 0 for layer in MemoryLayer}
        
        try:
            for layer in MemoryLayer:
                max_capacity = self.config.max_memories_per_layer[layer]
                current_memories = self.layer_manager.get_memories_by_layer(layer)
                
                if len(current_memories) > max_capacity:
                    # 需要清理或降级
                    excess_count = len(current_memories) - max_capacity
                    
                    # 按权重和访问时间排序，移除最不重要的
                    sorted_memories = sorted(
                        current_memories,
                        key=lambda m: (m.weight, m.last_accessed)
                    )
                    
                    for memory_info in sorted_memories[:excess_count]:
                        if layer == MemoryLayer.SHORT_TERM:
                            # 短期记忆直接删除
                            self._delete_memory(memory_info.memory_id)
                        else:
                            # 其他层级降级
                            self._demote_memory(memory_info)
                        
                        balance_stats[layer.value] += 1
            
            logger.info(f"容量平衡完成: {balance_stats}")
            return balance_stats
            
        except Exception as e:
            logger.error(f"容量平衡失败: {e}")
            return balance_stats
    
    def run_maintenance(self) -> Dict[str, Any]:
        """运行完整的维护流程"""
        logger.info("🔧 开始记忆维护流程")
        
        maintenance_results = {
            'cleanup': self.cleanup_expired_memories(),
            'promotion': self.promote_memories(),
            'balance': self.balance_layer_capacity(),
            'timestamp': time.time()
        }
        
        logger.info("✅ 记忆维护流程完成")
        return maintenance_results
    
    def _find_expired_memories(self, layer: MemoryLayer) -> List[LayerInfo]:
        """查找过期记忆"""
        memories = self.layer_manager.get_memories_by_layer(layer)
        return [m for m in memories if m.should_expire]
    
    def _find_promotion_candidates(self, layer: MemoryLayer) -> List[LayerInfo]:
        """查找提升候选记忆"""
        memories = self.layer_manager.get_memories_by_layer(layer, limit=100)
        
        candidates = []
        for memory_info in memories:
            score = memory_info.calculate_promotion_score()
            if score > 0.7:  # 提升阈值
                candidates.append(memory_info)
        
        # 按分数排序
        candidates.sort(key=lambda m: m.promotion_score, reverse=True)
        return candidates[:10]  # 最多提升10个
    
    def _calculate_target_layer(self, memory_info: LayerInfo) -> MemoryLayer:
        """计算目标层级"""
        current_layer = memory_info.layer
        score = memory_info.promotion_score
        
        if score > 0.9 and current_layer != MemoryLayer.CORE:
            return MemoryLayer.CORE
        elif score > 0.8 and current_layer not in [MemoryLayer.CORE, MemoryLayer.ARCHIVE]:
            return MemoryLayer.ARCHIVE
        elif score > 0.7 and current_layer == MemoryLayer.SHORT_TERM:
            return MemoryLayer.LONG_TERM
        
        return current_layer
    
    def _should_demote_instead_of_delete(self, memory_info: LayerInfo) -> bool:
        """判断是否应该降级而不是删除"""
        # 如果记忆有一定价值（权重>3或访问次数>5），则降级
        return memory_info.weight > 3.0 or memory_info.access_count > 5
    
    def _promote_memory(self, memory_info: LayerInfo, target_layer: MemoryLayer):
        """提升记忆到目标层级"""
        try:
            # 更新权重到目标层级范围
            min_weight, max_weight = target_layer.weight_range
            new_weight = min(max_weight, memory_info.weight + 1.0)
            
            self.layer_manager.assign_layer(
                memory_info.memory_id, 
                new_weight, 
                target_layer
            )
            
            # 同步更新memories表的权重
            self.db_manager.execute(
                "UPDATE memories SET weight = ? WHERE id = ?",
                (new_weight, memory_info.memory_id)
            )
            
            logger.debug(f"记忆 {memory_info.memory_id} 从 {memory_info.layer.value} 提升到 {target_layer.value}")
            
        except Exception as e:
            logger.error(f"记忆提升失败: {e}")
    
    def _demote_memory(self, memory_info: LayerInfo):
        """降级记忆"""
        try:
            # 确定降级目标
            current_layer = memory_info.layer
            if current_layer == MemoryLayer.CORE:
                target_layer = MemoryLayer.ARCHIVE
            elif current_layer == MemoryLayer.ARCHIVE:
                target_layer = MemoryLayer.LONG_TERM
            elif current_layer == MemoryLayer.LONG_TERM:
                target_layer = MemoryLayer.SHORT_TERM
            else:
                # 短期记忆直接删除
                self._delete_memory(memory_info.memory_id)
                return
            
            # 更新权重到目标层级范围
            min_weight, max_weight = target_layer.weight_range
            new_weight = max(min_weight, memory_info.weight - 1.0)
            
            self.layer_manager.assign_layer(
                memory_info.memory_id,
                new_weight,
                target_layer
            )
            
            # 同步更新memories表的权重
            self.db_manager.execute(
                "UPDATE memories SET weight = ? WHERE id = ?",
                (new_weight, memory_info.memory_id)
            )
            
            logger.debug(f"记忆 {memory_info.memory_id} 从 {current_layer.value} 降级到 {target_layer.value}")
            
        except Exception as e:
            logger.error(f"记忆降级失败: {e}")
    
    def _delete_memory(self, memory_id: str):
        """删除记忆"""
        try:
            # 删除相关记录
            self.db_manager.execute("DELETE FROM memory_layers WHERE memory_id = ?", (memory_id,))
            self.db_manager.execute("DELETE FROM memory_vectors WHERE memory_id = ?", (memory_id,))
            self.db_manager.execute("DELETE FROM memory_association WHERE source_key = ? OR target_key = ?", (memory_id, memory_id))
            self.db_manager.execute("DELETE FROM memory_cache WHERE memory_id = ?", (memory_id,))
            self.db_manager.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            
            logger.debug(f"记忆 {memory_id} 已删除")
            
        except Exception as e:
            logger.error(f"删除记忆失败: {e}")