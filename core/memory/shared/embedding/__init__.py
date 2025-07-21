# This file makes this directory a Python package.

"""
记忆系统的Embedding模块
包含文本向量化和向量缓存功能
"""

# 导出主要类，方便直接导入
from .cache import EmbeddingCache
from .vectorizer import TextVectorizer
