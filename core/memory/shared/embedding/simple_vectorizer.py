#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的向量化器实现
用于测试缓存功能，不依赖外部模型
"""

import numpy as np
import hashlib
import time
import logging
from typing import Optional, Union, List

logger = logging.getLogger(__name__)

class SimpleVectorizer:
    """
    简化的向量化器，用于测试缓存功能
    不依赖外部模型，使用哈希+随机向量生成
    """
    
    def __init__(self, dimension: int = 384, use_cache: bool = True):
        """
        初始化简化向量化器
        
        Args:
            dimension: 向量维度
            use_cache: 是否使用缓存
        """
        self.dimension = dimension
        self.use_cache = use_cache
        self.vector_cache = {}
        self.model = self  # 设置model属性以兼容现有代码
        self.vector_dim = dimension
        self._initialized = True
        
        logger.info(f"SimpleVectorizer初始化完成，维度: {dimension}")
    
    def encode(self, text: str) -> np.ndarray:
        """
        编码文本为向量
        
        Args:
            text: 输入文本
            
        Returns:
            np.ndarray: 向量表示
        """
        if not isinstance(text, str):
            text = str(text)
            
        # 检查缓存
        if self.use_cache and text in self.vector_cache:
            logger.debug(f"缓存命中: {text[:20]}...")
            return self.vector_cache[text]
        
        # 模拟向量化过程（添加一些计算延迟）
        time.sleep(0.001)  # 模拟计算时间
        
        # 使用哈希生成确定性的随机向量
        hash_obj = hashlib.md5(text.encode('utf-8'))
        seed = int(hash_obj.hexdigest(), 16) % (2**32)
        
        np.random.seed(seed)
        vector = np.random.randn(self.dimension).astype(np.float32)
        
        # 归一化
        vector = vector / np.linalg.norm(vector)
        
        # 存储到缓存
        if self.use_cache:
            self.vector_cache[text] = vector
            logger.debug(f"缓存存储: {text[:20]}...")
        
        return vector
    
    def get_sentence_embedding_dimension(self) -> int:
        """获取向量维度"""
        return self.dimension
    
    def clear_cache(self):
        """清理缓存"""
        self.vector_cache.clear()
        logger.info("SimpleVectorizer缓存已清理")
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        return {
            "cache_size": len(self.vector_cache),
            "dimension": self.dimension,
            "use_cache": self.use_cache
        }