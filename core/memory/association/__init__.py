#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆关联模块
Step 5: 记忆关联网络管理

功能：
- 记忆间关联关系建立
- 关联强度计算
- 关联网络扩展检索
- 时间衰减和关联更新
"""

from .network import AssociationNetwork

__all__ = ['AssociationNetwork']

# 模块版本
__version__ = '1.0.0'

# 模块配置
DEFAULT_ASSOCIATION_THRESHOLD = 0.7
DEFAULT_DECAY_FACTOR = 0.95
MAX_ASSOCIATION_DEPTH = 3
