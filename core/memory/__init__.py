#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia记忆系统模块
提供完整的记忆管理、存储、检索和关联功能
"""

import logging

logger = logging.getLogger(__name__)

# 主接口：严格按照设计文档实现
try:
    from .estia_memory import EstiaMemorySystem, create_estia_memory
    logger.info("✅ 主记忆系统接口加载成功")
except ImportError as e:
    logger.error(f"❌ 主记忆系统接口加载失败: {e}")
    EstiaMemorySystem = None
    create_estia_memory = None

# 向后兼容：使用别名映射到新系统
if EstiaMemorySystem is not None:
    # 🔄 向后兼容别名
    SimpleMemoryPipeline = EstiaMemorySystem  # 别名映射
    
    def create_simple_pipeline(advanced: bool = True):
        """向后兼容函数：映射到create_estia_memory"""
        logger.warning("⚠️ create_simple_pipeline已废弃，建议使用create_estia_memory")
        return create_estia_memory(enable_advanced=advanced)
    
    logger.info("📝 向后兼容别名已设置 (SimpleMemoryPipeline → EstiaMemorySystem)")
else:
    SimpleMemoryPipeline = None
    create_simple_pipeline = None

# manager.py 兼容性 - 暂时禁用避免语法错误
EstiaMemoryManager = None
create_memory_manager = None

# 导出接口
__all__ = [
    # === 主接口（推荐使用）===
    'EstiaMemorySystem',       # 主记忆系统类
    'create_estia_memory',     # 主记忆系统工厂函数
    
    # === 向后兼容接口 ===
    'SimpleMemoryPipeline',    # 简化管道类（向后兼容）
    'create_simple_pipeline',  # 简化管道工厂函数（向后兼容）
    'EstiaMemoryManager',      # 记忆管理器类（向后兼容）
    'create_memory_manager',   # 记忆管理器工厂函数（向后兼容）
]

# 默认创建函数：优先使用新接口
def create_memory_system(enable_advanced: bool = True):
    """
    创建记忆系统的默认函数
    
    现在直接使用EstiaMemorySystem（按设计文档实现）
    
    参数:
        enable_advanced: 是否启用高级功能
        
    返回:
        EstiaMemorySystem实例
    """
    if EstiaMemorySystem is not None:
        logger.debug("🎯 使用Estia记忆系统")
        return create_estia_memory(enable_advanced=enable_advanced)
    else:
        logger.error("❌ EstiaMemorySystem不可用")
        raise ImportError("无法创建记忆系统：EstiaMemorySystem不可用")

# 添加默认函数到导出列表
__all__.append('create_memory_system')

# 版本信息
__version__ = "2.0.0"  # 新版本，基于设计文档重构

# 模块初始化日志
logger.info(f"Estia记忆系统模块已加载 (版本: {__version__})") 