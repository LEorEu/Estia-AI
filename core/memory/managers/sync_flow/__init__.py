#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
同步流程管理器 (SyncFlowManager)
负责Step 1-9: 系统初始化、记忆检索和上下文构建、对话存储
职责：实时响应用户输入，性能敏感的同步操作
"""

import time
import logging
from typing import Dict, Any, Optional, List
from ...shared.internal import handle_memory_errors, ErrorHandlerMixin

logger = logging.getLogger(__name__)

class SyncFlowManager(ErrorHandlerMixin):
    """同步流程管理器 - 处理Step 1-9的实时流程"""
    
    def __init__(self, components: Dict[str, Any]):
        """
        初始化同步流程管理器
        
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
        self.memory_store = components.get('memory_store')
        self.unified_cache = components.get('unified_cache')
        
        # 性能监控
        self.step_times = {}
        self.logger = logger
    
    @handle_memory_errors("同步流程执行失败")
    def execute_sync_flow(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行完整的同步流程 (Step 1-9)
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            Dict: 包含增强上下文和存储结果
        """
        self.logger.debug("🚀 开始同步流程 (Step 4-9)")
        start_time = time.time()
        
        # Step 4: 统一缓存向量化
        query_vector = self._get_or_create_vector(user_input)
        self._record_step_time('step_4_vectorization', start_time)
        
        # Step 5: FAISS向量检索
        similar_memory_ids = self._faiss_search(query_vector)
        self._record_step_time('step_5_faiss_search', start_time)
        
        # Step 6: 关联网络拓展
        expanded_ids = self._expand_associations(similar_memory_ids)
        self._record_step_time('step_6_association_expansion', start_time)
        
        # Step 7: 历史对话聚合
        context_memories = self._retrieve_context_memories(expanded_ids, context)
        self._record_step_time('step_7_history_aggregation', start_time)
        
        # Step 8: 权重排序与去重
        ranked_memories = self._rank_and_dedup(context_memories, user_input)
        self._record_step_time('step_8_ranking_dedup', start_time)
        
        # Step 9: 组装最终上下文
        enhanced_context = self._build_enhanced_context(user_input, ranked_memories, context)
        self._record_step_time('step_9_context_assembly', start_time)
        
        total_time = time.time() - start_time
        self.logger.info(f"✅ 同步流程完成，总耗时: {total_time*1000:.2f}ms")
        
        return {
            'enhanced_context': enhanced_context,
            'ranked_memories': ranked_memories,
            'processing_time': total_time,
            'step_times': self.step_times.copy()
        }
    
    @handle_memory_errors(None)
    def store_interaction_sync(self, user_input: str, ai_response: str, 
                              context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        同步存储对话 (Step 9的一部分)
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
            context: 上下文信息
            
        Returns:
            Dict: 存储结果
        """
        self.logger.debug("💾 开始同步存储对话")
        
        try:
            if not self.memory_store:
                return {'error': '记忆存储器未初始化'}
            
            # 获取session_id和timestamp
            session_id = context.get('session_id', 'default') if context else 'default'
            timestamp = time.time()
            
            # 立即存储用户输入
            user_memory_id = self.memory_store.add_interaction_memory(
                user_input, "user_input", "user", session_id, timestamp
            )
            
            # 立即存储AI回复
            ai_memory_id = self.memory_store.add_interaction_memory(
                ai_response, "assistant_reply", "assistant", session_id, timestamp
            )
            
            # 🆕 通过统一缓存记录记忆访问（基于旧系统实现）
            if self.unified_cache and user_memory_id:
                try:
                    self.unified_cache.put(f"memory_access_{user_memory_id}", {
                        "memory_id": user_memory_id,
                        "access_time": timestamp,
                        "access_weight": 1.0
                    }, {"access_type": "store_interaction"})
                    self.logger.debug(f"✅ 记录记忆访问: {user_memory_id}")
                except Exception as e:
                    self.logger.debug(f"统一缓存记录访问失败: {e}")
            
            if self.unified_cache and ai_memory_id:
                try:
                    self.unified_cache.put(f"memory_access_{ai_memory_id}", {
                        "memory_id": ai_memory_id,
                        "access_time": timestamp,
                        "access_weight": 1.0
                    }, {"access_type": "store_interaction"})
                    self.logger.debug(f"✅ 记录记忆访问: {ai_memory_id}")
                except Exception as e:
                    self.logger.debug(f"统一缓存记录访问失败: {e}")
            
            self.logger.debug(f"✅ Step 9: 对话存储完成 (Session: {session_id}, 用户: {user_memory_id}, AI: {ai_memory_id})")
            
            return {
                'user_memory_id': user_memory_id,
                'ai_memory_id': ai_memory_id,
                'status': 'stored_sync'
            }
            
        except Exception as e:
            self.logger.error(f"同步存储失败: {e}")
            return {'error': str(e)}
    
    def _get_or_create_vector(self, text: str):
        """Step 4: 统一缓存向量化（基于旧系统实现）"""
        try:
            # 优先从统一缓存获取
            if self.unified_cache:
                cached_vector = self.unified_cache.get(text)
                if cached_vector is not None:
                    self.logger.debug("✅ 从统一缓存获取向量")
                    return cached_vector
            
            # 使用向量化器生成
            if self.vectorizer:
                vector = self.vectorizer.encode(text)
                
                # 存储到统一缓存（带metadata）
                if self.unified_cache and vector is not None:
                    self.unified_cache.put(text, vector, {"source": "vectorizer"})
                    self.logger.debug("✅ 向量化完成并存储到统一缓存")
                
                return vector
            else:
                self.logger.warning("向量化器未初始化")
                return None
                
        except Exception as e:
            self.logger.error(f"向量化失败: {e}")
            return None
    
    def _faiss_search(self, query_vector, k: int = 15, threshold: float = 0.3):
        """Step 5: FAISS向量检索（基于旧系统实现）"""
        try:
            if query_vector is None or not self.faiss_retriever:
                return []
            
            # 检查向量是否为有效的numpy数组
            import numpy as np
            if not isinstance(query_vector, np.ndarray) or query_vector.size == 0:
                return []
            
            # 执行FAISS搜索
            results = self.faiss_retriever.search(query_vector, k=k, threshold=threshold)
            
            # 提取记忆ID
            memory_ids = [result[0] for result in results if len(result) > 0]
            
            self.logger.debug(f"FAISS检索到 {len(memory_ids)} 个相似记忆")
            return memory_ids
            
        except Exception as e:
            self.logger.error(f"FAISS检索失败: {e}")
            return []
    
    def _expand_associations(self, memory_ids: List[str], depth: int = 2):
        """Step 6: 关联网络拓展（基于旧系统实现）"""
        try:
            if not memory_ids or not self.association_network:
                return memory_ids
            
            # 执行2层深度关联拓展
            expanded_ids = self.association_network.find_associated_memories(
                memory_ids[:5],  # 只对前5个最相似的进行拓展
                depth=depth,
                max_results=10,
                min_strength=0.3
            )
            
            # 合并原始ID和扩展ID
            all_ids = list(set(memory_ids + expanded_ids))
            
            self.logger.debug(f"关联拓展: {len(memory_ids)} → {len(all_ids)}")
            return all_ids
            
        except Exception as e:
            self.logger.error(f"关联拓展失败: {e}")
            return memory_ids
    
    def _retrieve_context_memories(self, memory_ids: List[str], context: Optional[Dict] = None):
        """Step 7: 历史对话聚合（基于旧系统实现）"""
        try:
            if not memory_ids:
                return []
            
            # 🆕 通过统一缓存记录记忆访问（基于旧系统实现）
            if self.unified_cache:
                timestamp = time.time()
                for memory_id in memory_ids:
                    try:
                        self.unified_cache.put(f"memory_access_{memory_id}", {
                            "memory_id": memory_id,
                            "access_time": timestamp,
                            "access_weight": 0.5  # 检索时权重较低
                        }, {"access_type": "retrieve_context"})
                        self.logger.debug(f"✅ 记录记忆检索访问: {memory_id}")
                    except Exception as e:
                        self.logger.debug(f"统一缓存记录检索访问失败: {e}")
            
            # 使用智能检索器的实现
            if self.smart_retriever:
                # 批量获取记忆内容
                memories = self.smart_retriever._get_memories_by_ids(memory_ids)
                
                # 添加会话信息
                session_id = context.get('session_id') if context else None
                if session_id and self.history_retriever:
                    # 获取会话历史
                    session_memories = self.history_retriever.get_session_memories(session_id)
                    memories.extend(session_memories)
                
                return memories
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"历史对话聚合失败: {e}")
            return []
    
    def _rank_and_dedup(self, memories: List[Dict], user_input: str, max_results: int = 20):
        """Step 8: 权重排序与去重（基于旧系统实现）"""
        try:
            if not memories:
                return []
            
            # 使用评分器排序
            if self.scorer:
                ranked_memories = self.scorer.rank_memories(memories, user_input)
            else:
                # 简单按权重排序
                ranked_memories = sorted(memories, key=lambda x: x.get('weight', 0), reverse=True)
            
            # 去重（基于内容相似度）
            unique_memories = self._remove_duplicates(ranked_memories)
            
            # 限制数量
            final_memories = unique_memories[:max_results]
            
            self.logger.debug(f"排序去重: {len(memories)} → {len(final_memories)}")
            return final_memories
            
        except Exception as e:
            self.logger.error(f"排序去重失败: {e}")
            return memories
    
    def _build_enhanced_context(self, user_input: str, memories: List[Dict], context: Optional[Dict] = None):
        """Step 9: 组装最终上下文（基于旧系统实现）"""
        try:
            # 构建增强上下文
            context_parts = []
            
            # 1. 系统角色设定
            context_parts.append("[系统角色设定]")
            context_parts.append("你是Estia，一个智能、友好、具有长期记忆的AI助手。")
            context_parts.append("")
            
            # 2. 核心记忆（高权重记忆）
            core_memories = [m for m in memories if m.get('weight', 0) >= 7.0]
            if core_memories:
                context_parts.append("[核心记忆]")
                for memory in core_memories[:5]:
                    weight = memory.get('weight', 0)
                    content = memory.get('content', '')[:200]  # 限制长度
                    context_parts.append(f"• [权重: {weight:.1f}] {content}")
                context_parts.append("")
            
            # 3. 相关记忆
            relevant_memories = [m for m in memories if m.get('weight', 0) < 7.0]
            if relevant_memories:
                context_parts.append("[相关记忆]")
                for memory in relevant_memories[:10]:
                    timestamp = memory.get('timestamp', 0)
                    content = memory.get('content', '')[:150]
                    time_str = time.strftime('%m-%d %H:%M', time.localtime(timestamp))
                    context_parts.append(f"• [{time_str}] {content}")
                context_parts.append("")
            
            # 4. 当前输入
            context_parts.append("[当前输入]")
            context_parts.append(user_input)
            
            enhanced_context = "\n".join(context_parts)
            
            # 长度控制
            if len(enhanced_context) > 8000:
                enhanced_context = enhanced_context[:8000] + "...\n[上下文已截断]"
            
            self.logger.debug(f"上下文构建完成: {len(enhanced_context)} 字符")
            return enhanced_context
            
        except Exception as e:
            self.logger.error(f"上下文构建失败: {e}")
            return f"[上下文构建失败，回退到原始输入]\n{user_input}"
    
    def _remove_duplicates(self, memories: List[Dict]) -> List[Dict]:
        """去重逻辑（基于内容相似度）"""
        if not memories:
            return []
        
        unique_memories = []
        seen_contents = set()
        
        for memory in memories:
            content = memory.get('content', '')
            content_hash = hash(content[:100])  # 使用前100字符的hash
            
            if content_hash not in seen_contents:
                unique_memories.append(memory)
                seen_contents.add(content_hash)
        
        return unique_memories
    
    def _record_step_time(self, step_name: str, start_time: float):
        """记录步骤耗时"""
        current_time = time.time()
        step_time = current_time - self.step_times.get('last_time', start_time)
        self.step_times[step_name] = round(step_time * 1000, 2)  # 转换为毫秒
        self.step_times['last_time'] = current_time
    
    def get_processing_time(self) -> Dict[str, float]:
        """获取处理时间统计"""
        return self.step_times.copy()