#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆存储模块
Step 3: 记忆数据存储管理

功能：
- 记忆数据持久化存储
- 存储策略优化
- 数据完整性保证
- 存储性能监控
"""

from .memory_store import MemoryStore

__all__ = ['MemoryStore']

# 模块版本
__version__ = '1.0.0'

# 模块配置
DEFAULT_BATCH_SIZE = 100
DEFAULT_SYNC_INTERVAL = 300  # 5分钟
MAX_MEMORY_CACHE = 1000     # 最大内存缓存数量
