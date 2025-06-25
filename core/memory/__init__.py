"""
Estia AI 记忆系统
包含多层记忆结构、记忆关联网络、冲突检测和记忆总结等功能
"""

# 导出主要类，方便直接从memory包导入
from .layers import (
    MemoryManager, 
    CoreMemory, 
    ArchivalMemory, 
    LongTermMemory, 
    ShortTermMemory
)
from .association import MemoryAssociationNetwork
from .conflict import MemoryConflictDetector
from .summarizer import MemorySummarizer
from .processor import process_and_store_memory

# 版本信息
__version__ = "1.0.0" 