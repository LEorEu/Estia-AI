#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层记忆系统

实现智能记忆分层与优先级管理的核心模块

主要功能:
- 记忆分层管理 (核心、归档、长期、短期)
- 权重与分层双向同步
- 自动生命周期管理
- 分层检索增强
- 系统监控与统计
- 无缝集成现有记忆系统
"""

# 核心类型
from .types import MemoryLayer, LayerConfig, LayerInfo

# 分层管理器
from .manager import LayeredMemoryManager

# 生命周期管理
from .lifecycle import MemoryLifecycleManager

# 权重同步器
from .sync import WeightLayerSynchronizer

# 检索增强器
from .retrieval import LayeredRetrievalEnhancer

# 配置管理
from .config import LayerConfigManager, LayerSystemConfig, get_config_manager, set_config_manager

# 监控系统
from .monitoring import LayerMonitor, LayerMetrics, SystemMetrics

# 集成模块
from .integration import (
    LayeredMemoryIntegration, 
    get_layered_integration, 
    set_layered_integration,
    initialize_layered_memory_system
)

__all__ = [
    # 核心类型
    'MemoryLayer',
    'LayerConfig', 
    'LayerInfo',
    
    # 管理器
    'LayeredMemoryManager',
    'MemoryLifecycleManager',
    'WeightLayerSynchronizer',
    'LayeredRetrievalEnhancer',
    
    # 配置管理
    'LayerConfigManager',
    'LayerSystemConfig',
    'get_config_manager',
    'set_config_manager',
    
    # 监控系统
    'LayerMonitor',
    'LayerMetrics',
    'SystemMetrics',
    
    # 集成模块
    'LayeredMemoryIntegration',
    'get_layered_integration',
    'set_layered_integration',
    'initialize_layered_memory_system'
]

# 版本信息
__version__ = '1.0.0'
__author__ = 'Estia Memory Team'
__description__ = 'Intelligent Memory Layering and Priority Management System'