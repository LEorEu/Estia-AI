#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查询增强器 - 处理完整的13步记忆增强工作流程
从 EstiaMemorySystem 中拆分出来的专门组件
"""

import logging
from typing import Dict, Any, Optional
from ..internal import handle_memory_errors, ErrorHandlerMixin

logger = logging.getLogger(__name__)

class QueryEnhancer(ErrorHandlerMixin):
    """查询增强器 - 专门处理13步记忆增强工作流程"""
    
    def __init__(self, components: Dict[str, Any]):
        """
        初始化查询增强器
        
        Args:
            components: 所需的组件字典
        """
        super().__init__()
        self.db_manager = components.get('db_manager')
        self.vectorizer = components.get('vectorizer')
        self.faiss_retriever = components.get('faiss_retriever')
        self.association_network = components.get('association_network')
        self.history_retriever = components.get('history_retriever')
        self.smart_retriever = components.get('smart_retriever')
        self.scorer = components.get('scorer')
        self.context_manager = components.get('context_manager')
        
        self.logger = logger
    
    @handle_memory_errors("查询增强失败，返回基础上下文")
    def enhance_query(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        执行完整的13步记忆增强工作流程
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            增强后的上下文prompt
        """
        try:
            self.logger.debug("🚀 开始13步记忆增强查询流程")
            
            # Step 3: 向量化用户输入
            query_vector = self._vectorize_input(user_input)
            if query_vector is None:
                return self._build_fallback_context(user_input)
            
            # Step 4: FAISS向量检索
            similar_memory_ids = self._faiss_search(query_vector)
            
            # Step 5: 关联网络拓展
            expanded_ids = self._expand_associations(similar_memory_ids)
            
            # Step 6: 历史对话聚合
            context_memories = self._aggregate_history(expanded_ids, context)
            
            # Step 7: 权重排序与去重
            ranked_memories = self._rank_and_deduplicate(context_memories, user_input)
            
            # Step 8: 组装最终上下文
            enhanced_context = self._build_enhanced_context(user_input, ranked_memories, context)
            
            return enhanced_context
            
        except Exception as e:
            self.logger.error(f"查询增强失败: {e}")
            return self._build_fallback_context(user_input)
    
    def _vectorize_input(self, user_input: str):
        """Step 3: 向量化用户输入"""
        if not self.vectorizer:
            return None
            
        try:
            # 使用统一缓存管理器
            from ...caching.cache_manager import UnifiedCacheManager
            unified_cache = UnifiedCacheManager.get_instance()
            
            # 尝试从缓存获取
            cached_vector = unified_cache.get(user_input)
            if cached_vector is not None:
                self.logger.debug("✅ 从统一缓存获取向量")
                return cached_vector
            
            # 缓存未命中，进行向量化
            query_vector = self.vectorizer.encode(user_input)
            if query_vector is not None:
                unified_cache.put(user_input, query_vector, {"source": "vectorizer"})
                self.logger.debug("✅ 向量化完成并存储到统一缓存")
            
            return query_vector
            
        except Exception as e:
            self.logger.error(f"向量化失败: {e}")
            return None
    
    def _faiss_search(self, query_vector, top_k: int = 15):
        """Step 4: FAISS向量检索"""
        if not self.faiss_retriever:
            return []
            
        try:
            similar_memories = self.faiss_retriever.search(query_vector, k=top_k, threshold=0.3)
            memory_ids = [result['memory_id'] for result in similar_memories if result.get('memory_id')]
            
            self.logger.debug(f"✅ FAISS检索完成，找到 {len(memory_ids)} 条相似记忆")
            return memory_ids
            
        except Exception as e:
            self.logger.error(f"FAISS检索失败: {e}")
            return []
    
    def _expand_associations(self, memory_ids, depth: int = 2):
        """Step 5: 关联网络拓展"""
        if not self.association_network or not memory_ids:
            return memory_ids
            
        try:
            expanded_ids = self.association_network.find_associated(memory_ids, depth=depth)
            self.logger.debug(f"✅ 关联网络拓展完成，扩展到 {len(expanded_ids)} 条记忆")
            return expanded_ids
            
        except Exception as e:
            self.logger.error(f"关联网络拓展失败: {e}")
            return memory_ids
    
    def _aggregate_history(self, memory_ids, context):
        """Step 6: 历史对话聚合"""
        if not self.history_retriever or not memory_ids:
            return []
            
        try:
            context_memories = self.history_retriever.retrieve_memory_contents(memory_ids)
            self.logger.debug(f"✅ 历史对话聚合完成，获取 {len(context_memories)} 条记忆内容")
            return context_memories
            
        except Exception as e:
            self.logger.error(f"历史对话聚合失败: {e}")
            return []
    
    def _rank_and_deduplicate(self, memories, user_input):
        """Step 7: 权重排序与去重"""
        if not self.scorer or not memories:
            return memories
            
        try:
            ranked_memories = self.scorer.rank_memories(memories, user_input)
            self.logger.debug(f"✅ 权重排序与去重完成，最终 {len(ranked_memories)} 条记忆")
            return ranked_memories
            
        except Exception as e:
            self.logger.error(f"权重排序失败: {e}")
            return memories
    
    def _build_enhanced_context(self, user_input, memories, context):
        """Step 8: 组装最终上下文"""
        try:
            if not memories:
                return self._build_fallback_context(user_input)
            
            # 使用上下文管理器构建
            if self.context_manager:
                enhanced_context = self.context_manager.build_enhanced_context(
                    user_input, memories, context
                )
            else:
                # 简单的上下文构建
                memory_texts = [m.get('content', '') for m in memories[:5]]
                enhanced_context = f"相关记忆：\n{chr(10).join(memory_texts)}\n\n用户问题：{user_input}"
            
            self.logger.debug("✅ 最终上下文组装完成")
            return enhanced_context
            
        except Exception as e:
            self.logger.error(f"上下文组装失败: {e}")
            return self._build_fallback_context(user_input)
    
    def _build_fallback_context(self, user_input):
        """构建降级上下文"""
        return f"用户问题：{user_input}\n\n注意：记忆系统当前不可用，请基于当前问题回答。"