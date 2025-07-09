#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆搜索模块
提供各种记忆搜索工具和方法
"""

import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MemorySearchManager:
    """记忆搜索管理器"""
    
    def __init__(self, db_manager, association_network=None):
        """
        初始化记忆搜索管理器
        
        Args:
            db_manager: 数据库管理器
            association_network: 关联网络（可选）
        """
        self.db_manager = db_manager
        self.association_network = association_network
        self.logger = logger
    
    def get_memory_search_tools(self) -> List[Dict[str, Any]]:
        """
        获取LLM可用的记忆搜索工具定义
        供LLM主动查询记忆使用
        
        Returns:
            List: 工具定义列表
        """
        return [
            {
                "name": "search_memories_by_keyword",
                "description": "根据关键词搜索相关记忆，用于获取特定主题的信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "string",
                            "description": "搜索关键词，可以是人名、地点、事件、概念等"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "最大返回结果数量",
                            "default": 5
                        },
                        "weight_threshold": {
                            "type": "number",
                            "description": "最低权重阈值，只返回权重高于此值的记忆",
                            "default": 3.0
                        }
                    },
                    "required": ["keywords"]
                }
            },
            {
                "name": "search_memories_by_timeframe",
                "description": "根据时间范围搜索记忆，用于回顾特定时期的信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days_ago": {
                            "type": "integer",
                            "description": "搜索多少天前的记忆"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "最大返回结果数量",
                            "default": 10
                        }
                    },
                    "required": ["days_ago"]
                }
            },
            {
                "name": "search_core_memories",
                "description": "搜索核心记忆（权重9.0+），用于获取最重要的用户信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "记忆类别，如 'user_info', 'preference', 'important_events'",
                            "default": ""
                        }
                    }
                }
            },
            {
                "name": "get_related_memories",
                "description": "获取与当前话题相关的记忆，用于深入理解上下文",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reference_memory_id": {
                            "type": "string",
                            "description": "参考记忆ID，用于查找相关记忆"
                        },
                        "association_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "关联类型列表",
                            "default": ["is_related_to", "same_topic"]
                        }
                    },
                    "required": ["reference_memory_id"]
                }
            }
        ]
    
    def execute_memory_search_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行记忆搜索工具（供LLM调用）
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            Dict: 搜索结果
        """
        try:
            if tool_name == "search_memories_by_keyword":
                return self.search_memories_by_keyword(
                    keywords=parameters.get('keywords', ''),
                    max_results=parameters.get('max_results', 5),
                    weight_threshold=parameters.get('weight_threshold', 3.0)
                )
            
            elif tool_name == "search_memories_by_timeframe":
                return self.search_memories_by_timeframe(
                    days_ago=parameters.get('days_ago', 7),
                    max_results=parameters.get('max_results', 10)
                )
            
            elif tool_name == "search_core_memories":
                return self.search_core_memories(
                    category=parameters.get('category', '')
                )
            
            elif tool_name == "get_related_memories":
                return self.get_related_memories(
                    reference_memory_id=parameters.get('reference_memory_id', ''),
                    association_types=parameters.get('association_types', ["is_related_to", "same_topic"])
                )
            
            else:
                return {
                    'success': False,
                    'message': f'未知的工具: {tool_name}',
                    'memories': []
                }
                
        except Exception as e:
            self.logger.error(f"执行记忆搜索工具失败: {e}")
            return {
                'success': False,
                'message': f'工具执行失败: {str(e)}',
                'memories': []
            }
    
    def search_memories_by_keyword(self, keywords: str, max_results: int = 5, weight_threshold: float = 3.0) -> Dict[str, Any]:
        """关键词搜索记忆"""
        try:
            search_query = """
                SELECT id, content, type, weight, timestamp, group_id
                FROM memories 
                WHERE content LIKE ? 
                AND weight >= ?
                AND (archived IS NULL OR archived = 0)
                ORDER BY weight DESC, timestamp DESC
                LIMIT ?
            """
            
            results = self.db_manager.execute_query(
                search_query, 
                (f'%{keywords}%', weight_threshold, max_results)
            )
            
            memories = []
            if results:
                for row in results:
                    memories.append({
                        'id': row[0],
                        'content': row[1],
                        'type': row[2],
                        'weight': row[3],
                        'timestamp': row[4],
                        'group_id': row[5],
                        'layer': self._get_memory_layer(row[3])
                    })
            
            return {
                'success': True,
                'message': f'找到 {len(memories)} 条包含关键词 "{keywords}" 的记忆',
                'memories': memories,
                'search_type': 'keyword',
                'parameters': {'keywords': keywords, 'weight_threshold': weight_threshold}
            }
            
        except Exception as e:
            self.logger.error(f"关键词搜索失败: {e}")
            return {'success': False, 'message': str(e), 'memories': []}
    
    def search_memories_by_timeframe(self, days_ago: int, max_results: int = 10) -> Dict[str, Any]:
        """时间范围搜索记忆"""
        try:
            current_time = time.time()
            start_time = current_time - (days_ago * 24 * 3600)
            
            search_query = """
                SELECT id, content, type, weight, timestamp, group_id
                FROM memories 
                WHERE timestamp >= ?
                AND (archived IS NULL OR archived = 0)
                ORDER BY weight DESC, timestamp DESC
                LIMIT ?
            """
            
            results = self.db_manager.execute_query(
                search_query, 
                (start_time, max_results)
            )
            
            memories = []
            if results:
                for row in results:
                    memories.append({
                        'id': row[0],
                        'content': row[1],
                        'type': row[2],
                        'weight': row[3],
                        'timestamp': row[4],
                        'group_id': row[5],
                        'layer': self._get_memory_layer(row[3]),
                        'age_days': (current_time - row[4]) / 86400
                    })
            
            return {
                'success': True,
                'message': f'找到 {len(memories)} 条 {days_ago} 天内的记忆',
                'memories': memories,
                'search_type': 'timeframe',
                'parameters': {'days_ago': days_ago}
            }
            
        except Exception as e:
            self.logger.error(f"时间范围搜索失败: {e}")
            return {'success': False, 'message': str(e), 'memories': []}
    
    def search_core_memories(self, category: str = '') -> Dict[str, Any]:
        """搜索核心记忆"""
        try:
            if category:
                search_query = """
                    SELECT id, content, type, weight, timestamp, group_id
                    FROM memories 
                    WHERE weight >= 9.0 
                    AND type LIKE ?
                    AND (archived IS NULL OR archived = 0)
                    ORDER BY weight DESC, timestamp DESC
                """
                params = (f'%{category}%',)
            else:
                search_query = """
                    SELECT id, content, type, weight, timestamp, group_id
                    FROM memories 
                    WHERE weight >= 9.0
                    AND (archived IS NULL OR archived = 0)
                    ORDER BY weight DESC, timestamp DESC
                """
                params = ()
            
            results = self.db_manager.execute_query(search_query, params)
            
            memories = []
            if results:
                for row in results:
                    memories.append({
                        'id': row[0],
                        'content': row[1],
                        'type': row[2],
                        'weight': row[3],
                        'timestamp': row[4],
                        'group_id': row[5],
                        'layer': '核心记忆'
                    })
            
            return {
                'success': True,
                'message': f'找到 {len(memories)} 条核心记忆',
                'memories': memories,
                'search_type': 'core_memories',
                'parameters': {'category': category}
            }
            
        except Exception as e:
            self.logger.error(f"核心记忆搜索失败: {e}")
            return {'success': False, 'message': str(e), 'memories': []}
    
    def get_related_memories(self, reference_memory_id: str, association_types: List[str]) -> Dict[str, Any]:
        """获取相关记忆"""
        try:
            if not self.association_network:
                return {'success': False, 'message': '关联网络未初始化', 'memories': []}
            
            # 使用关联网络获取相关记忆
            related_memory_ids = []
            for assoc_type in association_types:
                associated = self.association_network.get_related_memories(
                    reference_memory_id, depth=1, min_strength=0.3
                )
                related_memory_ids.extend([mem['target_id'] for mem in associated])
            
            # 去重
            related_memory_ids = list(set(related_memory_ids))
            
            if not related_memory_ids:
                return {
                    'success': True,
                    'message': '没有找到相关记忆',
                    'memories': [],
                    'search_type': 'related_memories'
                }
            
            # 获取相关记忆详情
            placeholders = ','.join(['?' for _ in related_memory_ids])
            search_query = f"""
                SELECT id, content, type, weight, timestamp, group_id
                FROM memories 
                WHERE id IN ({placeholders})
                AND (archived IS NULL OR archived = 0)
                ORDER BY weight DESC
            """
            
            results = self.db_manager.execute_query(search_query, related_memory_ids)
            
            memories = []
            if results:
                for row in results:
                    memories.append({
                        'id': row[0],
                        'content': row[1],
                        'type': row[2],
                        'weight': row[3],
                        'timestamp': row[4],
                        'group_id': row[5],
                        'layer': self._get_memory_layer(row[3])
                    })
            
            return {
                'success': True,
                'message': f'找到 {len(memories)} 条相关记忆',
                'memories': memories,
                'search_type': 'related_memories',
                'parameters': {
                    'reference_memory_id': reference_memory_id,
                    'association_types': association_types
                }
            }
            
        except Exception as e:
            self.logger.error(f"相关记忆搜索失败: {e}")
            return {'success': False, 'message': str(e), 'memories': []}
    
    def get_memories_by_group(self, group_id: str) -> List[Dict]:
        """根据group_id获取记忆"""
        try:
            query = """
                SELECT id, content, type, weight, timestamp, group_id
                FROM memories 
                WHERE group_id = ?
                AND (archived IS NULL OR archived = 0)
                ORDER BY timestamp DESC
            """
            results = self.db_manager.execute_query(query, (group_id,))
            
            memories = []
            if results:
                for row in results:
                    memories.append({
                        'id': row[0],
                        'content': row[1],
                        'type': row[2],
                        'weight': row[3],
                        'timestamp': row[4],
                        'group_id': row[5]
                    })
            
            return memories
            
        except Exception as e:
            self.logger.error(f"获取分组记忆失败: {e}")
            return []
    
    def _get_memory_layer(self, weight: float) -> str:
        """根据权重确定记忆层级"""
        if 9.0 <= weight <= 10.0:
            return "核心记忆"  # 永久保留
        elif 7.0 <= weight < 9.0:
            return "归档记忆"  # 长期保留
        elif 4.0 <= weight < 7.0:
            return "长期记忆"  # 定期清理
        else:
            return "短期记忆"  # 快速过期 