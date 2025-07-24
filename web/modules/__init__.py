#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web监控模块
============

将web_dashboard.py中的功能模块化，提高代码可维护性。
本模块采用非侵入式设计，不影响现有核心记忆系统。
"""

__version__ = "1.0.0"
__author__ = "Estia AI Team"

# 模块导入
from .api_handlers import *
from .data_adapters import *
from .performance_utils import *
from .websocket_handlers import *

__all__ = [
    # API处理器
    'APIHandlers',
    'create_api_blueprint',
    
    # 数据适配器
    'V6DataAdapter',
    'DataCache',
    'KeywordAnalyzer',
    'MemoryContentAnalyzer',
    
    # 性能工具
    'PerformanceOptimizer',
    'BackgroundMonitor',
    
    # WebSocket处理器
    'WebSocketHandlers',
    'setup_websocket_events'
]