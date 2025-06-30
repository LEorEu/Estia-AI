#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆检索模块

提供多种记忆检索策略：
- FAISS向量检索
- 智能查询检索
- 关键词检索
- 最近记忆检索
"""

from .faiss_search import FAISSRetriever
from .smart_retriever import SmartRetriever

__all__ = [
    'FAISSRetriever',
    'SmartRetriever'
]

# 模块版本
__version__ = '1.0.0'

# 模块配置
DEFAULT_SIMILARITY_THRESHOLD = 0.6
DEFAULT_MAX_RESULTS = 20
DEFAULT_SEARCH_LAYERS = ['recent', 'important', 'relevant']
