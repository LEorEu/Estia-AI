#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estia AI 统一监控系统
====================

将分散的监控代码整合到统一的目录结构中，便于管理和维护。

**安全保障：**
- 绝不修改 core/memory/ 下的任何文件
- 采用复制+整合的方式
- 保持所有原有功能
- 支持向后兼容

目录结构：
monitoring/
├── core/           # 核心监控逻辑（从core/monitoring复制）
├── web/            # Web界面（从web/modules整合）
├── memory/         # 记忆系统监控接口（安全封装）
└── config/         # 配置管理
"""

__version__ = "1.0.0"
__description__ = "Estia AI 统一监控系统"

# 导入核心监控组件
from .core.performance_monitor import PerformanceMonitor
from .core.metrics_collector import MetricsCollector  
from .core.alert_manager import AlertManager

# 导入Web组件
from .web.dashboard import create_unified_dashboard
from .web.api_handlers import APIHandlers

# 导入记忆系统监控接口
from .memory.memory_monitor_interface import MemoryMonitorInterface

# 导入配置
from .config.monitoring_config import MonitoringConfig

__all__ = [
    # 核心组件
    'PerformanceMonitor',
    'MetricsCollector', 
    'AlertManager',
    
    # Web组件
    'create_unified_dashboard',
    'APIHandlers',
    
    # 记忆系统接口
    'MemoryMonitorInterface',
    
    # 配置
    'MonitoringConfig'
]


def create_monitoring_system(config=None):
    """
    创建统一的监控系统实例
    
    Args:
        config: 配置对象，如果为None则使用默认配置
        
    Returns:
        MonitoringSystem: 监控系统实例
    """
    from .system import MonitoringSystem
    
    if config is None:
        config = MonitoringConfig()
    
    return MonitoringSystem(config)