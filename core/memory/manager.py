#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia记忆管理器 - 简化统一版本
"""

import time
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryLayer:
    """记忆层"""
    
    def __init__(self, name: str, capacity: int = 1000):
        self.name = name
        self.capacity = capacity
        self.memories = {}
        self.access_order = deque()
        
    def add(self, memory_id: str, content: Dict[str, Any]) -> bool:
        """添加记忆"""
        if memory_id in self.memories:
            self.memories[memory_id] = content
            self._move_to_front(memory_id)
            return True
        
        if len(self.memories) >= self.capacity:
            oldest_id = self.access_order.popleft()
            del self.memories[oldest_id]
        
        self.memories[memory_id] = content
        self.access_order.append(memory_id)
        return True
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """获取记忆"""
        if memory_id in self.memories:
            self._move_to_front(memory_id)
            return self.memories[memory_id]
        return None
    
    def _move_to_front(self, memory_id: str):
        """移到最前"""
        if memory_id in self.access_order:
            self.access_order.remove(memory_id)
        self.access_order.append(memory_id)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有记忆"""
        return list(self.memories.values())

class EstiaMemoryManager:
    """Estia记忆管理器"""
    
    def __init__(self, enable_advanced: bool = True):
        logger.info("正在初始化Estia记忆管理器...")
        
        self.enable_advanced = enable_advanced
        
        # 分层记忆架构
        self.core_memory = MemoryLayer("core", capacity=100)
        self.active_memory = MemoryLayer("active", capacity=500)
        self.archive_memory = MemoryLayer("archive", capacity=2000)
        self.temp_memory = MemoryLayer("temp", capacity=200)
        
        # 层级阈值
        self.layer_thresholds = {
            'core': 9.0,
            'active': 6.0,
            'archive': 4.0,
            'temp': 0.0
        }
        
        # 高级功能组件（可选）
        self.db_manager = None
        self.vectorizer = None
        self.retriever = None
        
        if enable_advanced:
            self._try_load_advanced_features()
        
        logger.info(f"记忆管理器初始化完成 (高级功能: {'启用' if enable_advanced else '禁用'})")
    
    def _try_load_advanced_features(self):
        """尝试加载高级功能"""
        try:
            from .init.db_manager import DatabaseManager
            from .retrieval.smart_retriever import SmartRetriever
            
            self.db_manager = DatabaseManager()
            self.retriever = SmartRetriever(self.db_manager)
            logger.info("高级功能加载成功")
            
        except ImportError as e:
            logger.warning(f"高级功能不可用: {e}")
            self.enable_advanced = False
    
    def store_memory(self, content: str, role: str = "user", 
                    importance: float = 5.0, memory_type: str = "dialogue",
                    metadata: Optional[Dict] = None) -> str:
        """存储记忆"""
        try:
            memory_id = hashlib.md5(f"{content}_{time.time()}".encode()).hexdigest()[:16]
            
            memory_data = {
                'id': memory_id,
                'content': content,
                'role': role,
                'importance': importance,
                'memory_type': memory_type,
                'timestamp': time.time(),
                'metadata': metadata or {}
            }
            
            # 根据重要性选择层级
            target_layer = self._select_layer(importance)
            target_layer.add(memory_id, memory_data)
            
            # 如果有数据库，也存储
            if self.db_manager:
                self._store_to_db(memory_data)
            
            logger.debug(f"记忆已存储: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"存储失败: {e}")
            return ""
    
    def retrieve_memories(self, query: str, limit: int = 10, 
                         min_importance: float = 0.0) -> List[Dict[str, Any]]:
        """检索记忆"""
        try:
            memories = []
            
            # 从各层收集记忆
            for layer in [self.core_memory, self.active_memory, self.archive_memory]:
                for memory in layer.get_all():
                    if memory.get('importance', 0) >= min_importance:
                        memory['layer'] = layer.name
                        memories.append(memory)
            
            # 如果有高级检索器，使用它
            if self.retriever:
                try:
                    advanced_memories = self.retriever.smart_search(query)
                    # 过滤重要性
                    filtered_memories = [m for m in advanced_memories if m.get('weight', 0) >= min_importance]
                    memories.extend(filtered_memories[:limit])
                except Exception as e:
                    logger.warning(f"高级检索失败: {e}")
            
            # 简单排序
            memories = self._rank_memories(memories, query)
            return memories[:limit]
            
        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []
    
    def _select_layer(self, importance: float) -> MemoryLayer:
        """选择存储层"""
        if importance >= self.layer_thresholds['core']:
            return self.core_memory
        elif importance >= self.layer_thresholds['active']:
            return self.active_memory
        elif importance >= self.layer_thresholds['archive']:
            return self.archive_memory
        else:
            return self.temp_memory
    
    def _store_to_db(self, memory_data: Dict[str, Any]):
        """存储到数据库"""
        try:
            if self.db_manager:
                self.db_manager.execute_query(
                    """INSERT OR REPLACE INTO memories 
                       (id, content, role, weight, memory_type, timestamp, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        memory_data['id'],
                        memory_data['content'],
                        memory_data['role'],
                        memory_data['importance'],
                        memory_data['memory_type'],
                        memory_data['timestamp'],
                        json.dumps(memory_data['metadata'])
                    )
                )
        except Exception as e:
            logger.error(f"数据库存储失败: {e}")
    
    def _rank_memories(self, memories: List[Dict], query: str) -> List[Dict]:
        """简单排序"""
        query_words = set(query.lower().split())
        
        def score(memory):
            content = memory.get('content', '').lower()
            words = set(content.split())
            overlap = len(query_words.intersection(words))
            total = len(query_words.union(words))
            relevance = overlap / total if total > 0 else 0
            importance = memory.get('importance', 0) / 10.0
            return relevance * 0.7 + importance * 0.3
        
        return sorted(memories, key=score, reverse=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'layers': {
                'core': len(self.core_memory.memories),
                'active': len(self.active_memory.memories),
                'archive': len(self.archive_memory.memories),
                'temp': len(self.temp_memory.memories)
            },
            'advanced_features': self.enable_advanced,
            'total_memories': sum([
                len(self.core_memory.memories),
                len(self.active_memory.memories),
                len(self.archive_memory.memories),
                len(self.temp_memory.memories)
            ])
        }

def create_memory_manager(advanced: bool = True) -> EstiaMemoryManager:
    """创建记忆管理器"""
    return EstiaMemoryManager(enable_advanced=advanced)