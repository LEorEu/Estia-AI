"""
记忆管道 - 处理记忆的存储和检索流程
"""

import os
import logging
import time
from datetime import datetime

# 导入日志工具
try:
    from core.utils.logger import get_logger
    # 设置日志
    logger = get_logger("estia.memory")
except ImportError:
    # 如果还没有日志工具，使用标准日志
    logger = logging.getLogger("estia.memory")

# 导入记忆存储管理器
try:
    from core.memory.storage.memory_store import MemoryStore
    MEMORY_STORE_AVAILABLE = True
except ImportError:
    logger.warning("MemoryStore不可用，将使用简化存储")
    MEMORY_STORE_AVAILABLE = False

# 简单的内存存储器，用于在实际组件缺失时作为替代
class SimpleMockStore:
    """简单的内存存储类，用于临时替代正式存储"""
    
    def __init__(self):
        """初始化简单存储"""
        self.memories = []
        logger.info("使用简单内存存储作为替代")
        
    def add_memory(self, memory):
        """添加记忆"""
        memory_id = f"mem_{int(time.time() * 1000)}_{len(self.memories)}"
        memory["id"] = memory_id
        self.memories.append(memory)
        return memory_id
        
    def get_memories(self, limit=10):
        """获取最近的记忆"""
        return self.memories[-limit:]
    
    def search_similar(self, query, limit=5):
        """简单的关键词搜索"""
        results = []
        query_lower = query.lower()
        for memory in self.memories:
            content = memory.get("content", "").lower()
            if query_lower in content:
                results.append(memory)
        return results[-limit:]

class MemoryPipeline:
    """记忆管道类，管理记忆的存储、检索和增强功能"""
    
    def __init__(self):
        """初始化记忆管道"""
        self.logger = logger
        self.logger.info("记忆管道初始化中...")
        
        # 尝试使用真正的记忆存储管理器
        if MEMORY_STORE_AVAILABLE:
            try:
                self.store = MemoryStore()
                self.logger.info("使用MemoryStore作为存储后端")
                self.use_real_store = True
            except Exception as e:
                self.logger.warning(f"MemoryStore初始化失败: {e}，使用简单存储作为替代")
                self.store = SimpleMockStore()
                self.use_real_store = False
        else:
            self.store = SimpleMockStore()
            self.use_real_store = False
            
        self.logger.info("记忆管道初始化完成")
        
    def enhance_query(self, query, context=None):
        """
        增强用户查询，添加相关记忆和上下文
        
        参数:
            query: 用户查询文本
            context: 上下文信息
            
        返回:
            增强后的上下文字符串
        """
        self.logger.info(f"增强查询: {query}")
        
        try:
            if self.use_real_store:
                # 使用真正的相似度搜索
                similar_memories = self.store.search_similar(query, limit=5)
            else:
                # 使用简单的关键词搜索
                similar_memories = self.store.search_similar(query, limit=5)
            
            # 格式化记忆为上下文
            enhanced_context = self._format_memories_for_context(similar_memories)
            
            return enhanced_context
        except Exception as e:
            self.logger.error(f"查询增强失败: {e}")
            return "没有找到相关记忆。"
        
    def store_interaction(self, query, response, context=None):
        """
        存储一次交互
        
        参数:
            query: 用户查询
            response: AI响应
            context: 上下文信息
        """
        try:
            if self.use_real_store:
                # 使用真正的记忆存储
                query_id = self.store.add_memory(
                    content=query,
                    source="user",
                    importance=0.7,
                    metadata={"context": context} if context else {}
                )
                
                response_id = self.store.add_memory(
                    content=response,
                    source="assistant", 
                    importance=0.7,
                    metadata={"context": context} if context else {}
                )
                
                self.logger.info(f"存储交互成功: query_id={query_id}, response_id={response_id}")
            else:
                # 使用简单存储
                query_memory = {
                    "content": query,
                    "type": "interaction",
                    "role": "user",
                    "timestamp": time.time(),
                    "importance": 0.7
                }
                
                if context:
                    query_memory["context"] = context
                    
                self.store.add_memory(query_memory)
                
                response_memory = {
                    "content": response,
                    "type": "interaction",
                    "role": "assistant",
                    "timestamp": time.time(),
                    "importance": 0.7
                }
                
                if context:
                    response_memory["context"] = context
                    
                self.store.add_memory(response_memory)
                
                self.logger.info("存储交互成功（简单存储）")
                
        except Exception as e:
            self.logger.error(f"存储交互失败: {e}")
        
    def _format_memories_for_context(self, memories):
        """
        将记忆格式化为上下文文本
        
        参数:
            memories: 记忆列表
            
        返回:
            格式化后的字符串
        """
        if not memories:
            return "没有找到相关记忆。"
            
        formatted = []
        
        for memory in memories:
            if self.use_real_store:
                # MemoryStore返回的格式
                content = memory.get("content", "")
                source = memory.get("source", "system")
                timestamp = memory.get("timestamp", "")
                similarity = memory.get("similarity", 0.0)
                
                # 构建格式化字符串
                entry = f"[{timestamp}] {source}: {content} (相似度: {similarity:.3f})"
                formatted.append(entry)
            else:
                # SimpleMockStore返回的格式
                content = memory.get("content", "")
                role = memory.get("role", "system")
                timestamp = memory.get("timestamp", "")
                
                # 格式化时间
                if isinstance(timestamp, (int, float)):
                    timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                    
                # 添加上下文信息
                context_info = ""
                if "context" in memory:
                    context_info = f" (备注: {memory['context']})"
                    
                # 构建格式化字符串
                entry = f"[{timestamp}] {role}: {content}{context_info}"
                formatted.append(entry)
            
        return "相关记忆:\n" + "\n".join(formatted)
