#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一的记忆分层逻辑
解决多个模块中重复的分层代码
"""

from typing import Dict, Any, List

class MemoryLayer:
    """记忆层级管理 - 统一实现"""
    
    # 层级阈值定义
    LAYER_THRESHOLDS = {
        'core': (9.0, 10.0),      # 核心记忆
        'archive': (7.0, 9.0),    # 归档记忆  
        'long_term': (4.0, 7.0),  # 长期记忆
        'short_term': (0.0, 4.0)  # 短期记忆
    }
    
    # 层级中文名称
    LAYER_NAMES = {
        'core': '核心记忆',
        'archive': '归档记忆',
        'long_term': '长期记忆',
        'short_term': '短期记忆'
    }
    
    # 层级英文名称
    LAYER_KEYS = {
        'core': 'core',
        'archive': 'archive', 
        'long_term': 'long_term',
        'short_term': 'short_term'
    }
    
    @classmethod
    def get_layer_key(cls, weight: float) -> str:
        """
        获取层级键名
        
        Args:
            weight: 权重值
            
        Returns:
            str: 层级键名
        """
        if 9.0 <= weight <= 10.0:
            return 'core'
        elif 7.0 <= weight < 9.0:
            return 'archive'
        elif 4.0 <= weight < 7.0:
            return 'long_term'
        else:
            return 'short_term'
    
    @classmethod
    def get_layer_name(cls, weight: float) -> str:
        """
        获取层级中文名称
        
        Args:
            weight: 权重值
            
        Returns:
            str: 层级中文名称
        """
        layer_key = cls.get_layer_key(weight)
        return cls.LAYER_NAMES[layer_key]
    
    @classmethod
    def get_layer_sql_case(cls, weight_column: str = 'weight') -> str:
        """
        获取SQL CASE语句
        
        Args:
            weight_column: 权重列名
            
        Returns:
            str: SQL CASE语句
        """
        return f"""
            CASE 
                WHEN {weight_column} >= 9.0 THEN '核心记忆'
                WHEN {weight_column} >= 7.0 THEN '归档记忆'
                WHEN {weight_column} >= 4.0 THEN '长期记忆'
                ELSE '短期记忆'
            END
        """
    
    @classmethod
    def get_layered_stats(cls, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取分层统计信息
        
        Args:
            memories: 记忆列表
            
        Returns:
            Dict: 分层统计信息
        """
        if not memories:
            return {
                'layer_distribution': {},
                'layered_memories': {},
                'total_memories': 0
            }
        
        layer_stats = {
            "核心记忆": [],
            "归档记忆": [],
            "长期记忆": [],
            "短期记忆": []
        }
        
        for memory in memories:
            weight = memory.get('weight', 1.0)
            layer_name = cls.get_layer_name(weight)
            layer_stats[layer_name].append(memory)
        
        return {
            'layer_distribution': {
                layer: len(memories_in_layer) 
                for layer, memories_in_layer in layer_stats.items()
            },
            'layered_memories': layer_stats,
            'total_memories': len(memories)
        }
    
    @classmethod
    def get_weight_range(cls, layer_key: str) -> tuple:
        """
        获取层级权重范围
        
        Args:
            layer_key: 层级键名
            
        Returns:
            tuple: (最小权重, 最大权重)
        """
        return cls.LAYER_THRESHOLDS.get(layer_key, (0.0, 10.0))
    
    @classmethod
    def is_core_memory(cls, weight: float) -> bool:
        """检查是否为核心记忆"""
        return weight >= 9.0
    
    @classmethod
    def is_archive_memory(cls, weight: float) -> bool:
        """检查是否为归档记忆"""
        return 7.0 <= weight < 9.0
    
    @classmethod
    def is_long_term_memory(cls, weight: float) -> bool:
        """检查是否为长期记忆"""
        return 4.0 <= weight < 7.0
    
    @classmethod
    def is_short_term_memory(cls, weight: float) -> bool:
        """检查是否为短期记忆"""
        return weight < 4.0
    
    @classmethod
    def get_layer_description(cls, layer_key: str) -> str:
        """
        获取层级描述
        
        Args:
            layer_key: 层级键名
            
        Returns:
            str: 层级描述
        """
        descriptions = {
            'core': '永久保留的核心记忆',
            'archive': '长期保留的归档记忆',
            'long_term': '定期清理的长期记忆',
            'short_term': '快速过期的短期记忆'
        }
        return descriptions.get(layer_key, '未知层级')