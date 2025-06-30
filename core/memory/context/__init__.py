#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆上下文模块
Step 6: 历史记忆检索和上下文管理
Step 8: 上下文构建和组织

功能：
- 历史对话记录检索
- 上下文相关性分析
- 会话状态管理
- 时间窗口控制
- 结构化上下文构建
- 智能上下文截断
"""

from .history import HistoryRetriever
from .builder import ContextBuilder

__all__ = ['HistoryRetriever', 'ContextBuilder']

# 模块版本
__version__ = '1.1.0'

# 模块配置
DEFAULT_CONTEXT_WINDOW = 10  # 默认上下文窗口大小
DEFAULT_TIME_WINDOW = 3600   # 默认时间窗口（秒）
MAX_CONTEXT_LENGTH = 2000    # 最大上下文长度
MAX_MEMORIES = 15            # 最大记忆数量
