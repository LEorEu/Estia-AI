#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
同步流程管理器 (SyncFlowManager) - v6.0 融合版本
负责Step 3-9: 实时记忆增强和对话存储
基于旧系统的完整14步工作流程，保持所有已测试的功能
"""

import time
import logging
import hashlib
from typing import Dict, Any, Optional, List
from ...shared.internal import handle_memory_errors, ErrorHandlerMixin

logger = logging.getLogger(__name__)

class SyncFlowManager(ErrorHandlerMixin):
    """同步流程管理器 - 完整实现旧系统的Step 3-9流程"""
    
    def __init__(self, components: Dict[str, Any]):
        """
        初始化同步流程管理器
        
        Args:
            components: 所需的组件字典
        """
        super().__init__()
        
        # 核心组件
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
        
        # 检查关键组件
        self._validate_components()
    
    def _validate_components(self):
        """验证关键组件是否初始化"""
        required_components = ['db_manager', 'vectorizer', 'memory_store', 'unified_cache']
        for component in required_components:
            if not getattr(self, component):
                self.logger.warning(f"关键组件 {component} 未初始化")
    
    @handle_memory_errors("同步流程执行失败")
    def execute_sync_flow(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行完整的同步流程 (Step 3-9) - 基于旧系统的完整实现
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            Dict: 包含增强上下文和处理结果
        """
        self.logger.debug("🚀 开始同步流程 (Step 3-9)")
        start_time = time.time()
        
        try:
            # Step 3: 统一缓存向量化（基于旧系统实现）
            query_vector = self._step_3_unified_cache_vectorization(user_input)
            self._record_step_time('step_3_vectorization', start_time)
            
            if query_vector is None:
                self.logger.warning("向量化失败，使用降级模式")
                return self._build_fallback_result(user_input, context)
            
            # Step 4: FAISS向量检索（基于旧系统实现）
            similar_memory_ids = self._step_4_faiss_search(query_vector)
            self._record_step_time('step_4_faiss_search', start_time)
            
            # Step 5: 关联网络拓展（基于旧系统实现）
            expanded_ids = self._step_5_association_expansion(similar_memory_ids)
            self._record_step_time('step_5_association_expansion', start_time)
            
            # Step 6: 历史对话聚合（基于旧系统实现）
            context_memories, historical_context = self._step_6_history_aggregation(expanded_ids, context)
            self._record_step_time('step_6_history_aggregation', start_time)
            
            # 保存上下文记忆到context（供后续异步评估使用）
            if context:
                context['context_memories'] = context_memories
            
            # Step 7: 权重排序与去重（基于旧系统实现）
            ranked_memories = self._step_7_ranking_and_deduplication(context_memories, user_input)
            self._record_step_time('step_7_ranking_dedup', start_time)
            
            # Step 8: 组装最终上下文（基于旧系统实现）
            enhanced_context = self._step_8_build_enhanced_context(user_input, ranked_memories, historical_context, context)
            self._record_step_time('step_8_context_assembly', start_time)
            
            total_time = time.time() - start_time
            self.logger.info(f"✅ 同步流程完成，总耗时: {total_time*1000:.2f}ms")
            
            return {
                'enhanced_context': enhanced_context,
                'ranked_memories': ranked_memories,
                'historical_context': historical_context,
                'processing_time': total_time,
                'step_times': self.step_times.copy(),
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"同步流程执行失败: {e}")
            return self._build_fallback_result(user_input, context)
    
    def _step_3_unified_cache_vectorization(self, user_input: str):
        """Step 3: 统一缓存向量化 - 基于旧系统实现"""
        try:
            if not self.unified_cache:
                self.logger.warning("统一缓存未初始化，直接使用向量化器")
                return self.vectorizer.encode(user_input) if self.vectorizer else None
            
            # 尝试从缓存获取向量
            cached_vector = self.unified_cache.get(user_input)
            if cached_vector is not None:
                self.logger.debug("✅ 从统一缓存获取向量")
                return cached_vector
            
            # 缓存未命中，进行向量化
            if self.vectorizer:
                query_vector = self.vectorizer.encode(user_input)
                if query_vector is not None:
                    # 将向量存储到统一缓存
                    self.unified_cache.put(user_input, query_vector, {"source": "vectorizer"})
                    self.logger.debug("✅ 向量化完成并存储到统一缓存")
                    return query_vector
            
            self.logger.warning("向量化器未初始化或向量化失败")
            return None
            
        except Exception as e:
            self.logger.error(f"Step 3 向量化失败: {e}")
            return None
    
    def _step_4_faiss_search(self, query_vector, k: int = 15, threshold: float = 0.3) -> List[str]:
        """Step 4: FAISS向量检索 - 基于旧系统实现"""
        try:
            if query_vector is None or not self.faiss_retriever:
                self.logger.debug("FAISS检索器不可用，尝试使用MemoryStore搜索")
                return self._fallback_memory_search(k)
            
            # 检查向量是否为有效的numpy数组
            import numpy as np
            if not isinstance(query_vector, np.ndarray) or query_vector.size == 0:
                self.logger.warning("查询向量无效")
                return self._fallback_memory_search(k)
            
            # 执行FAISS搜索
            search_results = self.faiss_retriever.search(query_vector, k=k)
            
            # 🔥 降低相似度阈值，提高检索召回率（基于旧系统）
            similar_memory_ids = [memory_id for memory_id, similarity in search_results 
                                if memory_id and similarity > threshold]
            
            # 如果检索结果太少，进一步降低阈值
            if len(similar_memory_ids) < 3:
                similar_memory_ids = [memory_id for memory_id, similarity in search_results 
                                    if memory_id and similarity > 0.1]
            
            self.logger.debug(f"FAISS检索到 {len(similar_memory_ids)} 条相似记忆")
            return similar_memory_ids
            
        except Exception as e:
            self.logger.error(f"Step 4 FAISS搜索失败: {e}")
            return self._fallback_memory_search(k)
    
    def _fallback_memory_search(self, limit: int = 10) -> List[str]:
        """回退的记忆搜索"""
        try:
            if self.memory_store:
                similar_memories = self.memory_store.search_similar("", limit=limit)
                memory_ids = [mem.get('memory_id') for mem in similar_memories 
                            if mem.get('memory_id')]
                self.logger.debug(f"回退搜索到 {len(memory_ids)} 条记忆")
                return memory_ids
        except Exception as e:
            self.logger.warning(f"回退搜索失败: {e}")
        return []
    
    def _step_5_association_expansion(self, similar_memory_ids: List[str], depth: int = 1) -> List[str]:
        """Step 5: 关联网络拓展 - 基于旧系统实现"""
        expanded_memory_ids = similar_memory_ids.copy()
        
        try:
            if not self.association_network or not similar_memory_ids:
                self.logger.debug("关联网络不可用或无输入记忆")
                return expanded_memory_ids
            
            # 对每个相似记忆进行关联拓展（基于旧系统）
            for memory_id in similar_memory_ids[:3]:  # 只对前3个记忆进行拓展
                try:
                    associated_memories = self.association_network.get_related_memories(
                        memory_id, depth=depth, min_strength=0.3
                    )
                    associated_ids = [mem.get('memory_id') for mem in associated_memories 
                                    if mem.get('memory_id')]
                    expanded_memory_ids.extend(associated_ids)
                except Exception as e:
                    self.logger.debug(f"关联拓展失败 {memory_id}: {e}")
                    continue
            
            # 去重
            expanded_memory_ids = list(dict.fromkeys(expanded_memory_ids))
            self.logger.debug(f"关联网络拓展后共有 {len(expanded_memory_ids)} 条记忆")
            
        except Exception as e:
            self.logger.error(f"Step 5 关联网络拓展失败: {e}")
        
        return expanded_memory_ids
    
    def _step_6_history_aggregation(self, expanded_ids: List[str], context: Optional[Dict] = None) -> tuple:
        """Step 6: 历史对话聚合 - 基于旧系统实现"""
        context_memories = []
        historical_context = {}
        
        try:
            if not expanded_ids:
                self.logger.debug("无记忆ID，获取最近的记忆")
                if self.memory_store:
                    context_memories = self.memory_store.get_recent_memories(limit=5)
                return context_memories, historical_context
            
            if self.history_retriever:
                # 🔥 关键修正：正确使用history_retriever进行session聚合（基于旧系统）
                retrieval_result = self.history_retriever.retrieve_memory_contents(
                    memory_ids=expanded_ids,
                    include_summaries=True,
                    include_sessions=True,  # 启用session聚合
                    max_recent_dialogues=10
                )
                
                # 提取记忆和历史对话
                context_memories = retrieval_result.get('primary_memories', [])
                historical_context = {
                    'grouped_memories': retrieval_result.get('grouped_memories', {}),
                    'session_dialogues': retrieval_result.get('session_dialogues', {}),
                    'summaries': retrieval_result.get('summaries', {}),
                    'total_memories': len(context_memories)
                }
                
                self.logger.debug(f"✅ 检索到 {len(context_memories)} 条记忆，"
                                f"{len(historical_context['session_dialogues'])} 个会话")
            else:
                # 降级：使用MemoryStore直接获取记忆
                if self.memory_store:
                    context_memories = self.memory_store.get_memories_by_ids(expanded_ids)
                    self.logger.debug(f"降级模式：直接获取 {len(context_memories)} 条记忆")
                    
        except Exception as e:
            self.logger.error(f"Step 6 历史对话聚合失败: {e}")
            # 最终降级
            if self.memory_store:
                context_memories = self.memory_store.get_recent_memories(limit=5)
        
        return context_memories, historical_context
    
    def _step_7_ranking_and_deduplication(self, context_memories: List[Dict], user_input: str, max_results: int = 20) -> List[Dict]:
        """Step 7: 权重排序与去重 - 基于旧系统实现"""
        try:
            if not context_memories:
                return []
            
            # 使用记忆评分器排序
            if self.scorer:
                try:
                    ranked_memories = self.scorer.rank_memories(context_memories, user_input)
                    context_memories = ranked_memories[:max_results]  # 取前20条
                    self.logger.debug(f"✅ 记忆排序完成，保留 {len(context_memories)} 条")
                except Exception as e:
                    self.logger.warning(f"记忆排序失败: {e}")
            
            # 去重处理
            unique_memories = self._remove_duplicates(context_memories)
            self.logger.debug(f"去重后剩余 {len(unique_memories)} 条记忆")
            
            return unique_memories
            
        except Exception as e:
            self.logger.error(f"Step 7 排序去重失败: {e}")
            return context_memories[:max_results]
    
    def _step_8_build_enhanced_context(self, user_input: str, ranked_memories: List[Dict], 
                                     historical_context: Dict, context: Optional[Dict] = None) -> str:
        """Step 8: 组装最终上下文 - 基于旧系统实现"""
        try:
            # 获取当前会话的对话历史
            current_session_dialogues = []
            current_session_id = context.get('session_id') if context else None
            
            if current_session_id and self.memory_store:
                try:
                    # 从当前会话获取最近的对话
                    session_memories = self.memory_store.get_session_memories(
                        current_session_id, max_count=10
                    )
                    
                    # 构建对话对
                    user_memories = [m for m in session_memories if m.get('role') == 'user']
                    assistant_memories = [m for m in session_memories if m.get('role') == 'assistant']
                    
                    # 配对对话
                    for i in range(min(len(user_memories), len(assistant_memories))):
                        current_session_dialogues.append({
                            "user": user_memories[i].get('content', ''),
                            "assistant": assistant_memories[i].get('content', '')
                        })
                except Exception as e:
                    self.logger.debug(f"获取当前会话对话失败: {e}")
            
            # 🆕 获取分层信息（基于旧系统）
            layered_info = self._get_layered_context_info(ranked_memories)
            
            # 使用上下文长度管理器构建基础上下文
            if self.context_manager:
                # 获取persona名称：用户设置 > 全局配置 > 默认estia
                persona_name = None
                if context:
                    persona_name = context.get('persona_name')
                
                # 如果用户没有指定，使用全局配置
                if not persona_name:
                    try:
                        from config.settings import ACTIVE_PERSONA
                        persona_name = ACTIVE_PERSONA
                    except ImportError:
                        persona_name = "estia"  # 默认fallback
                
                base_context = self.context_manager.build_enhanced_context(
                    user_input=user_input,
                    memories=ranked_memories,
                    historical_context=historical_context,
                    current_session_id=current_session_id,
                    current_session_dialogues=current_session_dialogues,
                    persona_name=persona_name
                )
                
                # 🆕 添加分层统计信息到上下文
                if layered_info and layered_info.get('layer_distribution'):
                    layer_stats = layered_info['layer_distribution']
                    layered_memories = layered_info['layered_memories']
                    
                    # 添加分层统计
                    base_context += f"\n\n[记忆分层统计]"
                    for layer, count in layer_stats.items():
                        if count > 0:
                            base_context += f"\n• {layer}: {count}条记忆"
                    
                    # 添加核心记忆优先显示
                    if layered_memories.get('核心记忆'):
                        base_context += f"\n\n[核心记忆详情]"
                        for memory in layered_memories['核心记忆'][:3]:  # 最多显示3条核心记忆
                            weight = memory.get('weight', 0)
                            content = memory.get('content', '')
                            if len(content) > 100:
                                content = content[:100] + "..."
                            base_context += f"\n• [权重: {weight:.1f}] {content}"
                
                return base_context
            else:
                # 降级模式：简单构建上下文
                return self._build_simple_context(user_input, ranked_memories)
                
        except Exception as e:
            self.logger.error(f"Step 8 上下文构建失败: {e}")
            return self._build_simple_context(user_input, ranked_memories)
    
    def _get_layered_context_info(self, memories: List[Dict]) -> Dict[str, Any]:
        """获取分层上下文信息 - 基于旧系统"""
        if not memories:
            return {}
        
        layer_stats = {
            "核心记忆": [],
            "归档记忆": [],
            "长期记忆": [],
            "短期记忆": []
        }
        
        for memory in memories:
            weight = memory.get('weight', 1.0)
            layer = self._get_memory_layer(weight)
            layer_stats[layer].append(memory)
        
        return {
            'layer_distribution': {
                layer: len(memories_in_layer) 
                for layer, memories_in_layer in layer_stats.items()
            },
            'layered_memories': layer_stats
        }
    
    def _get_memory_layer(self, weight: float) -> str:
        """根据权重确定记忆层级 - 基于旧系统"""
        if 9.0 <= weight <= 10.0:
            return "核心记忆"  # 永久保留
        elif 7.0 <= weight < 9.0:
            return "归档记忆"  # 长期保留
        elif 4.0 <= weight < 7.0:
            return "长期记忆"  # 定期清理
        else:
            return "短期记忆"  # 快速过期
    
    def _build_simple_context(self, user_input: str, memories: List[Dict]) -> str:
        """简单上下文构建"""
        context = f"""[系统角色设定]
你是Estia，一个智能、友好、具有长期记忆的AI助手。

[相关记忆]
"""
        
        for i, memory in enumerate(memories[:5]):
            weight = memory.get('weight', 1.0)
            content = memory.get('content', '')
            if len(content) > 100:
                content = content[:100] + "..."
            context += f"• [权重: {weight:.1f}] {content}\n"
        
        context += f"""
[用户当前输入]
{user_input}"""
        
        return context
    
    @handle_memory_errors(None)
    def store_interaction_sync(self, user_input: str, ai_response: str, 
                              context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        同步存储对话 (Step 9) - 基于旧系统实现
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
            context: 上下文信息
            
        Returns:
            Dict: 存储结果
        """
        self.logger.debug("💾 开始同步存储对话 (Step 9)")
        
        try:
            if not self.memory_store:
                return {'error': '记忆存储器未初始化'}
            
            # 获取session_id和timestamp
            session_id = context.get('session_id', 'default') if context else 'default'
            timestamp = time.time()
            
            # 🆕 使用统一缓存管理器记录访问（基于旧系统）
            unified_cache = self.unified_cache
            
            # 🔥 Step 9: 使用MemoryStore保存对话（包含向量化）
            user_memory_id = self.memory_store.add_interaction_memory(
                content=user_input,
                memory_type="user_input", 
                role="user",
                session_id=session_id,
                timestamp=timestamp,
                weight=5.0  # 默认权重，等待LLM精确评估
            )
            
            ai_memory_id = self.memory_store.add_interaction_memory(
                content=ai_response,
                memory_type="assistant_reply",
                role="assistant", 
                session_id=session_id,
                timestamp=timestamp,
                weight=5.0
            )
            
            # 🆕 通过统一缓存记录记忆访问（基于旧系统实现）
            if unified_cache and user_memory_id:
                try:
                    unified_cache.put(f"memory_access_{user_memory_id}", {
                        "memory_id": user_memory_id,
                        "access_time": timestamp,
                        "access_weight": 1.0
                    }, {"access_type": "store_interaction"})
                    self.logger.debug(f"✅ 记录记忆访问: {user_memory_id}")
                except Exception as e:
                    self.logger.debug(f"统一缓存记录访问失败: {e}")
            
            if unified_cache and ai_memory_id:
                try:
                    unified_cache.put(f"memory_access_{ai_memory_id}", {
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
                'session_id': session_id,
                'timestamp': timestamp,
                'status': 'stored_sync'
            }
            
        except Exception as e:
            self.logger.error(f"同步存储失败: {e}")
            return {'error': str(e)}
    
    def _remove_duplicates(self, memories: List[Dict]) -> List[Dict]:
        """去除重复记忆"""
        if not memories:
            return []
        
        unique_memories = []
        seen_contents = set()
        
        for memory in memories:
            content = memory.get('content', '')
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            if content_hash not in seen_contents:
                unique_memories.append(memory)
                seen_contents.add(content_hash)
        
        return unique_memories
    
    def _build_fallback_result(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """构建降级结果"""
        fallback_context = f"""[系统角色设定]
你是Estia，一个智能、友好的AI助手。

[用户当前输入]
{user_input}"""
        
        return {
            'enhanced_context': fallback_context,
            'ranked_memories': [],
            'historical_context': {},
            'processing_time': 0.0,
            'step_times': {},
            'success': False,
            'fallback': True
        }
    
    def _record_step_time(self, step_name: str, start_time: float):
        """记录步骤执行时间"""
        self.step_times[step_name] = time.time() - start_time
    
    def get_processing_time(self) -> Dict[str, float]:
        """获取处理时间统计"""
        return self.step_times.copy()