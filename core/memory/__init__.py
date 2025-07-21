#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia记忆系统模块
提供完整的记忆管理、存储、检索和关联功能
"""

import os
import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .init.db_manager import DatabaseManager

# 统一日志配置
logger = logging.getLogger(__name__)

def get_memory_logger(name: str) -> logging.Logger:
    """
    获取记忆系统专用logger
    
    Args:
        name: logger名称，通常使用__name__
        
    Returns:
        logging.Logger: 配置好的logger实例
    """
    return logging.getLogger(f"estia.memory.{name.split('.')[-1]}")

def get_default_db_path() -> str:
    """
    获取默认数据库路径
    
    Returns:
        str: 默认数据库文件路径
    """
    return os.path.join("assets", "memory.db")

def safe_db_execute(db_manager: "DatabaseManager", query: str, params=None, 
                   auto_commit: bool = True, operation_name: str = "数据库操作") -> bool:
    """
    安全执行数据库操作的公共方法
    
    Args:
        db_manager: 数据库管理器实例
        query: SQL查询语句
        params: 查询参数
        auto_commit: 是否自动提交事务
        operation_name: 操作名称，用于日志
        
    Returns:
        bool: 操作是否成功
    """
    if db_manager is None:
        logger.error(f"{operation_name}失败: 数据库管理器未初始化")
        return False
    
    try:
        db_manager.execute_query(query, params)
        
        if auto_commit and db_manager.conn:
            db_manager.conn.commit()
        
        logger.debug(f"{operation_name}成功")
        return True
        
    except Exception as e:
        logger.error(f"{operation_name}失败: {e}")
        return False

# 主要组件导入
try:
    from .estia_memory_v6 import EstiaMemorySystem, create_estia_memory
    from .managers.sync_flow.storage.memory_store import MemoryStore
    from .managers.sync_flow.init.db_manager import DatabaseManager
    
    # 子模块快捷导入
    from .managers.async_flow.association.network import AssociationNetwork
    from .managers.sync_flow.context.history import HistoryRetriever
    from .shared.embedding.vectorizer import TextVectorizer
    from .shared.embedding.cache import EmbeddingCache
    from .managers.async_flow.evaluator.async_evaluator import AsyncMemoryEvaluator
    from .managers.sync_flow.ranking.scorer import MemoryScorer
    from .managers.sync_flow.retrieval.faiss_search import FAISSSearchEngine
    from .managers.sync_flow.retrieval.smart_retriever import SmartRetriever
    
    # 向后兼容别名
    SimpleMemoryPipeline = EstiaMemorySystem
    create_memory_system = create_estia_memory
    
    def create_simple_pipeline(advanced: bool = True):
        """向后兼容函数：映射到create_estia_memory"""
        logger.warning("⚠️ create_simple_pipeline已废弃，建议使用create_estia_memory")
        return create_estia_memory(enable_advanced=advanced)
    
    __all__ = [
        # 主要组件
        'EstiaMemorySystem', 'create_estia_memory', 'MemoryStore', 'DatabaseManager',
        # 子模块组件
        'AssociationNetwork', 'HistoryRetriever',
        'TextVectorizer', 'EmbeddingCache', 'AsyncMemoryEvaluator', 
        'MemoryScorer', 'FAISSSearchEngine', 'SmartRetriever',
        # 向后兼容
        'SimpleMemoryPipeline', 'create_simple_pipeline', 'create_memory_system',
        # 工具函数
        'get_memory_logger', 'get_default_db_path', 'safe_db_execute'
    ]
    
    logger.info("✅ Estia记忆系统模块加载成功")
    
except Exception as e:
    logger.warning(f"部分记忆组件导入失败: {e}")
    # 基础导入
    EstiaMemorySystem = None
    create_estia_memory = None
    SimpleMemoryPipeline = None
    
    def create_simple_pipeline(advanced: bool = True):
        raise ImportError("记忆系统组件未正确加载，无法创建系统")
    
    def create_memory_system(enable_advanced: bool = True):
        raise ImportError("记忆系统组件未正确加载，无法创建系统")
    
    __all__ = ['get_memory_logger', 'get_default_db_path', 'safe_db_execute']

# 版本信息
__version__ = "2.0.0"