#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层记忆管理器

负责记忆的分层分配、查询和管理
"""

import logging
import time
from typing import List, Dict, Optional, Any
from .types import MemoryLayer, LayerConfig, LayerInfo

logger = logging.getLogger(__name__)


class LayeredMemoryManager:
    """分层记忆管理器"""
    
    def __init__(self, db_manager, config: LayerConfig = None):
        self.db_manager = db_manager
        self.config = config or LayerConfig.default()
        self._ensure_layer_table()
        
    def _ensure_layer_table(self):
        """确保分层表存在"""
        create_sql = """
        CREATE TABLE IF NOT EXISTS memory_layers (
            memory_id TEXT PRIMARY KEY,
            layer TEXT NOT NULL,
            weight REAL NOT NULL,
            created_at REAL NOT NULL,
            last_accessed REAL NOT NULL,
            access_count INTEGER DEFAULT 0,
            promotion_score REAL DEFAULT 0.0,
            metadata TEXT,
            FOREIGN KEY (memory_id) REFERENCES memories (id)
        )
        """
        
        index_sql = """
        CREATE INDEX IF NOT EXISTS idx_memory_layers_layer ON memory_layers(layer);
        CREATE INDEX IF NOT EXISTS idx_memory_layers_weight ON memory_layers(weight);
        CREATE INDEX IF NOT EXISTS idx_memory_layers_accessed ON memory_layers(last_accessed);
        """
        
        try:
            self.db_manager.execute(create_sql)
            self.db_manager.execute(index_sql)
            logger.info("✅ 分层表初始化完成")
        except Exception as e:
            logger.error(f"分层表初始化失败: {e}")
    
    def assign_layer(self, memory_id: str, weight: float, 
                    force_layer: MemoryLayer = None) -> MemoryLayer:
        """为记忆分配层级"""
        try:
            # 确定层级
            layer = force_layer or MemoryLayer.from_weight(weight)
            current_time = time.time()
            
            # 检查是否已存在
            existing = self.get_layer_info(memory_id)
            if existing:
                # 更新现有记录
                self._update_layer_info(memory_id, layer, weight, current_time)
            else:
                # 创建新记录
                self._create_layer_info(memory_id, layer, weight, current_time)
            
            logger.debug(f"记忆 {memory_id} 分配到 {layer.value} 层级")
            return layer
            
        except Exception as e:
            logger.error(f"分层分配失败: {e}")
            return MemoryLayer.SHORT_TERM  # 默认层级
    
    def get_layer_info(self, memory_id: str) -> Optional[LayerInfo]:
        """获取记忆的分层信息"""
        try:
            result = self.db_manager.query(
                "SELECT * FROM memory_layers WHERE memory_id = ?",
                (memory_id,)
            )
            
            if result:
                row = result[0]
                return LayerInfo(
                    memory_id=row[0],
                    layer=MemoryLayer(row[1]),
                    weight=row[2],
                    created_at=row[3],
                    last_accessed=row[4],
                    access_count=row[5],
                    promotion_score=row[6]
                )
            return None
            
        except Exception as e:
            logger.error(f"获取分层信息失败: {e}")
            return None
    
    def get_memories_by_layer(self, layer: MemoryLayer, 
                             limit: int = None) -> List[LayerInfo]:
        """获取指定层级的记忆"""
        try:
            sql = "SELECT * FROM memory_layers WHERE layer = ? ORDER BY weight DESC, last_accessed DESC"
            params = (layer.value,)
            
            if limit:
                sql += " LIMIT ?"
                params += (limit,)
            
            results = self.db_manager.query(sql, params)
            
            layer_infos = []
            for row in results:
                layer_infos.append(LayerInfo(
                    memory_id=row[0],
                    layer=MemoryLayer(row[1]),
                    weight=row[2],
                    created_at=row[3],
                    last_accessed=row[4],
                    access_count=row[5],
                    promotion_score=row[6]
                ))
            
            return layer_infos
            
        except Exception as e:
            logger.error(f"获取层级记忆失败: {e}")
            return []
    
    def update_access(self, memory_id: str):
        """更新记忆访问信息"""
        try:
            current_time = time.time()
            self.db_manager.execute(
                "UPDATE memory_layers SET last_accessed = ?, access_count = access_count + 1 WHERE memory_id = ?",
                (current_time, memory_id)
            )
        except Exception as e:
            logger.error(f"更新访问信息失败: {e}")
    
    def get_layer_statistics(self) -> Dict[str, Any]:
        """获取分层统计信息"""
        try:
            stats = {}
            
            for layer in MemoryLayer:
                result = self.db_manager.query(
                    "SELECT COUNT(*), AVG(weight), AVG(access_count) FROM memory_layers WHERE layer = ?",
                    (layer.value,)
                )
                
                if result and result[0][0] > 0:
                    stats[layer.value] = {
                        'count': result[0][0],
                        'avg_weight': round(result[0][1] or 0, 2),
                        'avg_access': round(result[0][2] or 0, 2)
                    }
                else:
                    stats[layer.value] = {
                        'count': 0,
                        'avg_weight': 0,
                        'avg_access': 0
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def _create_layer_info(self, memory_id: str, layer: MemoryLayer, 
                          weight: float, timestamp: float):
        """创建分层信息记录"""
        self.db_manager.execute(
            "INSERT INTO memory_layers (memory_id, layer, weight, created_at, last_accessed) VALUES (?, ?, ?, ?, ?)",
            (memory_id, layer.value, weight, timestamp, timestamp)
        )
    
    def _update_layer_info(self, memory_id: str, layer: MemoryLayer, 
                          weight: float, timestamp: float):
        """更新分层信息记录"""
        self.db_manager.execute(
            "UPDATE memory_layers SET layer = ?, weight = ?, last_accessed = ? WHERE memory_id = ?",
            (layer.value, weight, timestamp, memory_id)
        )