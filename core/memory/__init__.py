#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia记忆系统
================

完整的13步记忆处理工作流程：

Step 1-2: 数据库初始化和向量化
Step 3: 记忆存储
Step 4: FAISS向量检索  
Step 5: 关联网络扩展
Step 6: 历史记忆检索
Step 7: 记忆排序和去重
Step 8: 上下文构建
Step 9-10: LLM对话生成
Step 11: LLM评估
Step 12: 异步存储
Step 13: 自动关联

核心组件：
- MemoryPipeline: 主要记忆处理管道
- DatabaseManager: 数据库管理
- AsyncMemoryEvaluator: 异步评估处理
"""

# 核心组件导入
from .pipeline import MemoryPipeline

# 导出核心组件
__all__ = [
    'MemoryPipeline'
]

# 版本信息
__version__ = '1.0.0'
__author__ = 'Estia AI Team'
__description__ = 'Estia AI记忆系统 - 智能记忆管理和上下文构建'

# 便捷函数
def create_memory_pipeline():
    """
    创建记忆处理管道
    
    返回:
        MemoryPipeline实例
    """
    return MemoryPipeline()

# 模块初始化日志
import logging
logger = logging.getLogger(__name__)
logger.info(f"Estia记忆系统模块已加载 (版本: {__version__})") 