#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层记忆系统 - 类型定义

定义记忆层级、配置和数据结构
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
import time


class MemoryLayer(Enum):
    """记忆层级枚举"""
    CORE = "core"           # 核心记忆：永久保留
    ARCHIVE = "archive"     # 归档记忆：长期保留
    LONG_TERM = "long_term" # 长期记忆：定期清理
    SHORT_TERM = "short_term" # 短期记忆：快速过期

    @property
    def weight_range(self) -> tuple[float, float]:
        """获取层级对应的权重范围"""
        ranges = {
            MemoryLayer.CORE: (9.0, 10.0),
            MemoryLayer.ARCHIVE: (7.0, 8.9),
            MemoryLayer.LONG_TERM: (4.0, 6.9),
            MemoryLayer.SHORT_TERM: (1.0, 3.9)
        }
        return ranges[self]
    
    @property
    def retention_days(self) -> Optional[int]:
        """获取层级的保留天数，None表示永久保留"""
        retention = {
            MemoryLayer.CORE: None,      # 永久保留
            MemoryLayer.ARCHIVE: 365,    # 1年
            MemoryLayer.LONG_TERM: 90,   # 3个月
            MemoryLayer.SHORT_TERM: 7    # 1周
        }
        return retention[self]
    
    @classmethod
    def from_weight(cls, weight: float) -> 'MemoryLayer':
        """根据权重确定记忆层级"""
        if 9.0 <= weight <= 10.0:
            return cls.CORE
        elif 7.0 <= weight < 9.0:
            return cls.ARCHIVE
        elif 4.0 <= weight < 7.0:
            return cls.LONG_TERM
        else:
            return cls.SHORT_TERM


@dataclass
class LayerConfig:
    """分层配置"""
    max_memories_per_layer: Dict[MemoryLayer, int]
    cleanup_interval_hours: int = 24
    auto_promotion_enabled: bool = True
    auto_demotion_enabled: bool = True
    
    @classmethod
    def default(cls) -> 'LayerConfig':
        """默认配置"""
        return cls(
            max_memories_per_layer={
                MemoryLayer.CORE: 100,
                MemoryLayer.ARCHIVE: 500,
                MemoryLayer.LONG_TERM: 2000,
                MemoryLayer.SHORT_TERM: 200
            }
        )


@dataclass
class LayerInfo:
    """记忆分层信息"""
    memory_id: str
    layer: MemoryLayer
    weight: float
    created_at: float
    last_accessed: float
    access_count: int = 0
    promotion_score: float = 0.0
    
    @property
    def age_days(self) -> float:
        """记忆年龄（天数）"""
        return (time.time() - self.created_at) / 86400
    
    @property
    def should_expire(self) -> bool:
        """是否应该过期"""
        retention_days = self.layer.retention_days
        if retention_days is None:
            return False
        return self.age_days > retention_days
    
    def calculate_promotion_score(self) -> float:
        """计算提升分数"""
        # 基于访问频率、权重和时间衰减计算
        access_factor = min(self.access_count / 10.0, 1.0)  # 访问次数因子
        weight_factor = self.weight / 10.0  # 权重因子
        time_factor = max(0.1, 1.0 - (self.age_days / 30.0))  # 时间因子
        
        self.promotion_score = (access_factor * 0.4 + 
                               weight_factor * 0.4 + 
                               time_factor * 0.2)
        return self.promotion_score