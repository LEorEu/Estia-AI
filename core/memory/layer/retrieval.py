#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层检索增强器

为现有检索系统添加分层过滤和优化功能
"""

import logging
from typing import List, Dict, Optional, Any
from .types import MemoryLayer, LayerInfo
from .manager import LayeredMemoryManager

logger = logging.getLogger(__name__)


class LayeredRetrievalEnhancer:
    """分层检索增强器"""
    
    def __init__(self, layer_manager: LayeredMemoryManager):
        self.layer_manager = layer_manager
        self.db_manager = layer_manager.db_manager
        
    def enhance_retrieval_with_layers(self, memory_ids: List[str], 
                                     layer_priority: List[MemoryLayer] = None,
                                     max_per_layer: int = None) -> List[Dict[str, Any]]:
        """使用分层信息增强检索结果"""
        try:
            if not memory_ids:
                return []
            
            # 默认层级优先级：核心 > 归档 > 长期 > 短期
            if layer_priority is None:
                layer_priority = [MemoryLayer.CORE, MemoryLayer.ARCHIVE, 
                                MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM]
            
            # 获取记忆的分层信息
            layered_memories = self._get_memories_with_layer_info(memory_ids)
            
            # 按层级分组
            grouped_by_layer = self._group_memories_by_layer(layered_memories)
            
            # 按优先级排序并限制数量
            enhanced_results = []
            for layer in layer_priority:
                if layer.value in grouped_by_layer:
                    layer_memories = grouped_by_layer[layer.value]
                    
                    # 在同一层级内按权重和访问时间排序
                    layer_memories.sort(
                        key=lambda m: (m.get('weight', 0), m.get('last_accessed', 0)), 
                        reverse=True
                    )
                    
                    # 限制每层级的数量
                    if max_per_layer:
                        layer_memories = layer_memories[:max_per_layer]
                    
                    enhanced_results.extend(layer_memories)
            
            # 更新访问信息
            for memory in enhanced_results:
                self.layer_manager.update_access(memory['memory_id'])
            
            logger.debug(f"分层检索增强: {len(memory_ids)} -> {len(enhanced_results)} 条记忆")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"分层检索增强失败: {e}")
            return self._fallback_retrieval(memory_ids)
    
    def filter_by_layer(self, memory_ids: List[str], 
                       allowed_layers: List[MemoryLayer]) -> List[str]:
        """按层级过滤记忆ID"""
        try:
            if not memory_ids or not allowed_layers:
                return memory_ids
            
            layer_values = [layer.value for layer in allowed_layers]
            
            # 查询符合层级要求的记忆
            placeholders = ','.join(['?' for _ in memory_ids])
            layer_placeholders = ','.join(['?' for _ in layer_values])
            
            sql = f"""
                SELECT memory_id FROM memory_layers 
                WHERE memory_id IN ({placeholders}) 
                AND layer IN ({layer_placeholders})
            """
            
            params = memory_ids + layer_values
            results = self.db_manager.query(sql, params)
            
            filtered_ids = [row[0] for row in results]
            
            logger.debug(f"层级过滤: {len(memory_ids)} -> {len(filtered_ids)} 条记忆")
            return filtered_ids
            
        except Exception as e:
            logger.error(f"层级过滤失败: {e}")
            return memory_ids
    
    def get_layer_aware_context(self, user_input: str, 
                               context_memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建层级感知的上下文"""
        try:
            # 按层级分组记忆
            layer_groups = {layer.value: [] for layer in MemoryLayer}
            
            for memory in context_memories:
                layer_info = self.layer_manager.get_layer_info(memory.get('memory_id', ''))
                if layer_info:
                    layer_groups[layer_info.layer.value].append(memory)
                else:
                    # 未分层的记忆放入短期记忆
                    layer_groups[MemoryLayer.SHORT_TERM.value].append(memory)
            
            # 构建分层上下文
            layered_context = {
                'user_input': user_input,
                'core_memories': layer_groups[MemoryLayer.CORE.value],
                'archive_memories': layer_groups[MemoryLayer.ARCHIVE.value],
                'long_term_memories': layer_groups[MemoryLayer.LONG_TERM.value],
                'short_term_memories': layer_groups[MemoryLayer.SHORT_TERM.value],
                'layer_statistics': self._calculate_context_stats(layer_groups)
            }
            
            return layered_context
            
        except Exception as e:
            logger.error(f"构建层级上下文失败: {e}")
            return {'user_input': user_input, 'memories': context_memories}
    
    def smart_layer_selection(self, query_type: str = "general") -> List[MemoryLayer]:
        """智能选择检索层级"""
        try:
            # 根据查询类型选择合适的层级
            layer_strategies = {
                'personal_info': [MemoryLayer.CORE, MemoryLayer.ARCHIVE],
                'recent_chat': [MemoryLayer.SHORT_TERM, MemoryLayer.LONG_TERM],
                'knowledge': [MemoryLayer.ARCHIVE, MemoryLayer.LONG_TERM],
                'general': [MemoryLayer.CORE, MemoryLayer.ARCHIVE, 
                           MemoryLayer.LONG_TERM, MemoryLayer.SHORT_TERM]
            }
            
            return layer_strategies.get(query_type, layer_strategies['general'])
            
        except Exception as e:
            logger.error(f"智能层级选择失败: {e}")
            return list(MemoryLayer)
    
    def _get_memories_with_layer_info(self, memory_ids: List[str]) -> List[Dict[str, Any]]:
        """获取带有分层信息的记忆"""
        try:
            if not memory_ids:
                return []
            
            placeholders = ','.join(['?' for _ in memory_ids])
            sql = f"""
                SELECT m.id, m.content, m.type, m.role, m.session_id, 
                       m.timestamp, m.weight, m.group_id, m.summary, m.last_accessed,
                       ml.layer, ml.access_count, ml.promotion_score
                FROM memories m
                LEFT JOIN memory_layers ml ON m.id = ml.memory_id
                WHERE m.id IN ({placeholders})
            """
            
            results = self.db_manager.query(sql, memory_ids)
            
            memories = []
            for row in results:
                memory = {
                    'memory_id': row[0],
                    'content': row[1],
                    'type': row[2],
                    'role': row[3],
                    'session_id': row[4],
                    'timestamp': row[5],
                    'weight': row[6],
                    'group_id': row[7],
                    'summary': row[8],
                    'last_accessed': row[9],
                    'layer': row[10] if row[10] else MemoryLayer.SHORT_TERM.value,
                    'access_count': row[11] or 0,
                    'promotion_score': row[12] or 0.0
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"获取分层记忆信息失败: {e}")
            return []
    
    def _group_memories_by_layer(self, memories: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按层级分组记忆"""
        groups = {layer.value: [] for layer in MemoryLayer}
        
        for memory in memories:
            layer = memory.get('layer', MemoryLayer.SHORT_TERM.value)
            if layer in groups:
                groups[layer].append(memory)
            else:
                groups[MemoryLayer.SHORT_TERM.value].append(memory)
        
        return groups
    
    def _calculate_context_stats(self, layer_groups: Dict[str, List]) -> Dict[str, int]:
        """计算上下文统计信息"""
        return {
            layer: len(memories) 
            for layer, memories in layer_groups.items()
        }
    
    def _fallback_retrieval(self, memory_ids: List[str]) -> List[Dict[str, Any]]:
        """降级检索（不使用分层信息）"""
        try:
            if not memory_ids:
                return []
            
            placeholders = ','.join(['?' for _ in memory_ids])
            sql = f"""
                SELECT id, content, type, role, session_id, timestamp, weight, group_id, summary, last_accessed
                FROM memories 
                WHERE id IN ({placeholders})
                ORDER BY weight DESC, last_accessed DESC
            """
            
            results = self.db_manager.query(sql, memory_ids)
            
            memories = []
            for row in results:
                memory = {
                    'memory_id': row[0],
                    'content': row[1],
                    'type': row[2],
                    'role': row[3],
                    'session_id': row[4],
                    'timestamp': row[5],
                    'weight': row[6],
                    'group_id': row[7],
                    'summary': row[8],
                    'last_accessed': row[9]
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"降级检索失败: {e}")
            return []