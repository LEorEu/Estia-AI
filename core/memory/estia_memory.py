#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia记忆系统主接口 - 严格按照设计文档实现
实现完整的13步记忆处理工作流程
"""

import time
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EstiaMemorySystem:
    """
    Estia记忆系统主接口 v2.0.0
    按照设计文档实现完整的13步工作流程
    """
    
    def __init__(self, enable_advanced: bool = True):
        """
        初始化Estia记忆系统
        
        Args:
            enable_advanced: 是否启用高级功能（关联网络、异步评估等）
        """
        # 使用模块级logger，避免重复设置
        self.logger = logger
        
        # 核心组件
        self.db_manager = None
        self.vectorizer = None
        self.faiss_retriever = None
        
        # 高级组件
        self.association_network = None
        self.history_retriever = None
        self.memory_store = None
        self.scorer = None
        self.async_evaluator = None
        
        # 🆕 会话状态管理
        self.current_session_id = None
        self.session_start_time = None
        self.session_timeout = 3600  # 1小时会话超时
        
        # 系统状态
        self.enable_advanced = enable_advanced
        self.initialized = False
        self.async_initialized = False
        
        # 初始化组件
        self._initialize_components()
        if enable_advanced:
            self._initialize_advanced_components()
            self._initialize_async_evaluator()
        
        logger.info(f"Estia记忆系统初始化完成 (高级功能: {'启用' if enable_advanced else '禁用'})")
    
    def _initialize_components(self):
        """初始化7个核心组件"""
        try:
            # Step 1: 初始化数据库管理器
            from .init.db_manager import DatabaseManager
            self.db_manager = DatabaseManager()
            if self.db_manager.connect():
                self.db_manager.initialize_database()
                logger.info("✅ 数据库管理器初始化成功")
            
            # Step 2: 初始化记忆存储 - 🔥 复用db_manager避免重复初始化
            from .storage.memory_store import MemoryStore
            self.memory_store = MemoryStore(db_manager=self.db_manager)
            logger.info("✅ 记忆存储初始化成功 (复用数据库连接)")
            
            # Step 3: 初始化其他高级组件
            if self.enable_advanced:
                self._initialize_advanced_components()
            
            # 🔥 初始化异步评估器
            self._initialize_async_evaluator()
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            self.initialized = False
    
    def _initialize_advanced_components(self):
        """初始化高级组件"""
        try:
            # 向量化器
            from .embedding.vectorizer import TextVectorizer
            self.vectorizer = TextVectorizer()
            logger.info("✅ 向量化器初始化成功")
            
            # FAISS检索
            from .retrieval.faiss_search import FAISSSearchEngine
            self.faiss_retriever = FAISSSearchEngine(
                index_path="data/vectors/memory_index.bin",
                dimension=1024  # Qwen3-Embedding-0.6B
            )
            logger.info("✅ FAISS检索初始化成功")
            
            # 🆕 智能检索器 - 这里会自动注册数据库缓存和检索缓存
            from .retrieval.smart_retriever import SmartRetriever
            self.smart_retriever = SmartRetriever(self.db_manager)
            logger.info("✅ 智能检索器初始化成功")
            
            # 关联网络
            from .association.network import AssociationNetwork
            self.association_network = AssociationNetwork(self.db_manager)
            logger.info("✅ 关联网络初始化成功")
            
            # 历史检索器
            from .context.history import HistoryRetriever
            self.history_retriever = HistoryRetriever(self.db_manager)
            logger.info("✅ 历史检索器初始化成功")
            
            # 记忆评分器
            from .ranking.scorer import MemoryScorer
            self.scorer = MemoryScorer()
            logger.info("✅ 记忆评分器初始化成功")
            
        except Exception as e:
            logger.warning(f"高级组件初始化失败: {e}")
            self.enable_advanced = False
    
    def _initialize_async_evaluator(self):
        """🔥 初始化异步评估器 - Step 11-13的核心 - 使用稳定的启动管理器"""
        try:
            from .evaluator.async_evaluator import AsyncMemoryEvaluator
            from .evaluator.async_startup_manager import initialize_async_evaluator_safely
            
            # 创建异步评估器实例
            self.async_evaluator = AsyncMemoryEvaluator(self.db_manager)
            logger.info("✅ 异步评估器实例创建成功")
            
            # 使用稳定的启动管理器初始化
            self.async_initialized = initialize_async_evaluator_safely(self.async_evaluator)
            
            if self.async_initialized:
                logger.info("🚀 异步评估器启动成功 - 使用稳定启动管理器")
            else:
                logger.warning("⚠️ 异步评估器启动失败，将在后续尝试重新启动")
                
        except Exception as e:
            logger.warning(f"异步评估器初始化失败: {e}")
            self.async_evaluator = None
            self.async_initialized = False
    
    def ensure_async_initialized(self):
        """确保异步组件已初始化 - 简化版本"""
        if not self.async_initialized and self.async_evaluator:
            from .evaluator.async_startup_manager import initialize_async_evaluator_safely
            self.async_initialized = initialize_async_evaluator_safely(self.async_evaluator)
            
        return self.async_initialized
    
    def start_new_session(self, session_id: str = None) -> str:
        """开始新的对话会话"""
        import time
        current_time = time.time()
        
        if session_id:
            self.current_session_id = session_id
        else:
            # 生成基于时间的session_id
            from datetime import datetime
            timestamp_str = datetime.fromtimestamp(current_time).strftime('%Y%m%d_%H%M%S')
            self.current_session_id = f"sess_{timestamp_str}"
        
        self.session_start_time = current_time
        self.logger.info(f"🆕 开始新会话: {self.current_session_id}")
        return self.current_session_id
    
    def get_current_session_id(self) -> str:
        """获取当前会话ID，如果没有则创建新会话"""
        import time
        current_time = time.time()
        
        # 检查是否需要创建新会话
        if (not self.current_session_id or 
            not self.session_start_time or 
            (current_time - self.session_start_time) > self.session_timeout):
            return self.start_new_session()
        
        return self.current_session_id
    
    def end_current_session(self):
        """结束当前会话"""
        if self.current_session_id:
            self.logger.info(f"🔚 结束会话: {self.current_session_id}")
            self.current_session_id = None
            self.session_start_time = None

    def enhance_query(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        增强用户查询，实现完整的13步工作流程 (Step 3-8)
        
        Args:
            user_input: 用户输入
            context: 上下文信息，可包含session_id等
            
        Returns:
            增强后的上下文prompt
        """
        try:
            self.logger.debug("🚀 开始记忆增强查询流程")
            
            # 🆕 Step 0: 会话管理
            if context and 'session_id' in context:
                # 使用指定的session_id
                if context['session_id'] != self.current_session_id:
                    self.start_new_session(context['session_id'])
            else:
                # 确保有当前会话
                current_session = self.get_current_session_id()
                if not context:
                    context = {}
                context['session_id'] = current_session
            
            # 🆕 Step 3: 使用统一缓存管理器进行向量化
            self.logger.debug("📝 Step 3: 向量化用户输入 (使用统一缓存)")
            if not self.vectorizer:
                return self._build_fallback_context(user_input)
            
            # 统一缓存管理器进行向量化 - 不再降级
            from .caching.cache_manager import UnifiedCacheManager
            unified_cache = UnifiedCacheManager.get_instance()
            
            # 尝试从缓存获取向量
            cached_vector = unified_cache.get(user_input)
            if cached_vector is not None:
                query_vector = cached_vector
                self.logger.debug("✅ 从统一缓存获取向量")
            else:
                # 缓存未命中，进行向量化
                query_vector = self.vectorizer.encode(user_input)
                if query_vector is not None:
                    # 将向量存储到统一缓存
                    unified_cache.put(user_input, query_vector, {"source": "vectorizer"})
                    self.logger.debug("✅ 向量化完成并存储到统一缓存")
            
            if query_vector is None:
                self.logger.warning("向量化失败，使用降级模式")
                return self._build_fallback_context(user_input)
            
            # Step 4: FAISS检索相似记忆
            self.logger.debug("🎯 Step 4: FAISS向量检索")
            similar_memory_ids = []
            if self.faiss_retriever:
                search_results = self.faiss_retriever.search(query_vector, k=15)
                similar_memory_ids = [memory_id for memory_id, similarity in search_results 
                                    if memory_id and similarity > 0.5]
            
            # Step 5: 关联网络拓展 (可选)
            expanded_memory_ids = similar_memory_ids.copy()
            if self.enable_advanced and self.association_network:
                self.logger.debug("🕸️ Step 5: 关联网络拓展")
                try:
                    # get_related_memories返回字典列表，需要提取memory_id
                    if similar_memory_ids:
                        associated_memories = self.association_network.get_related_memories(
                            similar_memory_ids[0], depth=2, min_strength=0.3
                        )
                        associated_ids = [mem.get('memory_id') for mem in associated_memories 
                                        if mem.get('memory_id')]
                        expanded_memory_ids.extend(associated_ids)
                        # 去重
                        expanded_memory_ids = list(dict.fromkeys(expanded_memory_ids))
                except Exception as e:
                    self.logger.warning(f"关联网络拓展失败: {e}")
            
            # Step 6: 历史对话聚合 + 获取记忆内容
            self.logger.debug("📚 Step 6: 历史对话聚合")
            context_memories = []
            historical_context = {}
            
            if self.history_retriever and expanded_memory_ids:
                # 🔥 关键修正：正确使用history_retriever进行session聚合
                retrieval_result = self.history_retriever.retrieve_memory_contents(
                    memory_ids=expanded_memory_ids,
                    include_summaries=True,
                    include_sessions=True,  # 启用session聚合
                    max_recent_dialogues=10
                )
                
                # 提取记忆和历史对话
                context_memories = retrieval_result.get('primary_memories', [])  # 🔧 修正字段名
                historical_context = {
                    'grouped_memories': retrieval_result.get('grouped_memories', {}),
                    'session_dialogues': retrieval_result.get('session_dialogues', {}),  # 🆕 会话对话
                    'summaries': retrieval_result.get('summaries', {}),
                    'total_memories': len(context_memories)
                }
                
                self.logger.debug(f"✅ 检索到 {len(context_memories)} 条记忆，"
                                f"{len(historical_context['session_dialogues'])} 个会话")
            else:
                # 降级：使用MemoryStore直接获取记忆
                context_memories = self.memory_store.get_memories_by_ids(expanded_memory_ids) if self.memory_store else []
            
            # 保存上下文记忆到context（供后续异步评估使用）
            if context:
                context['context_memories'] = context_memories
            
            # Step 7: 权重排序 + 去重
            self.logger.debug("⚖️ Step 7: 记忆排序与去重")
            if self.scorer:
                try:
                    ranked_memories = self.scorer.rank_memories(context_memories, user_input)
                    context_memories = ranked_memories[:20]  # 取前20条
                except Exception as e:
                    self.logger.warning(f"记忆排序失败: {e}")
            
            # Step 8: 组装最终上下文
            self.logger.debug("🎨 Step 8: 组装上下文")
            enhanced_context = self._build_enhanced_context(user_input, context_memories, historical_context)
            
            self.logger.debug("✅ 记忆增强查询完成")
            return enhanced_context
            
        except Exception as e:
            self.logger.error(f"记忆增强查询失败: {e}")
            return self._build_fallback_context(user_input)
    
    def store_interaction(self, user_input: str, ai_response: str, 
                         context: Optional[Dict] = None):
        """
        存储用户交互 (Step 12) + 触发异步评估 (Step 11-13)
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
            context: 上下文信息
        """
        try:
            if not self.memory_store:
                logger.warning("MemoryStore未初始化，跳过存储")
                return
            
            # 🆕 Step 12: 使用当前会话ID
            timestamp = time.time()
            session_id = context.get('session_id') if context else self.get_current_session_id()
            
            # 确保使用一致的session_id
            if context:
                context['session_id'] = session_id
            
            # 🆕 使用统一缓存管理器记录访问
            unified_cache = None
            try:
                from .caching.cache_manager import UnifiedCacheManager
                unified_cache = UnifiedCacheManager.get_instance()
            except Exception as e:
                self.logger.debug(f"统一缓存管理器不可用: {e}")
            
            # 🔥 Step 12: 使用MemoryStore保存对话（包含向量化）
            user_memory_id = self.memory_store.add_interaction_memory(
                content=user_input,
                memory_type="user_input", 
                role="user",
                session_id=session_id,
                timestamp=timestamp,
                weight=5.0
            )
            
            ai_memory_id = self.memory_store.add_interaction_memory(
                content=ai_response,
                memory_type="assistant_reply",
                role="assistant", 
                session_id=session_id,
                timestamp=timestamp,
                weight=5.0
            )
            
            # 🆕 通过统一缓存记录记忆访问
            if unified_cache and user_memory_id:
                try:
                    unified_cache.put(f"memory_access_{user_memory_id}", {
                        "memory_id": user_memory_id,
                        "access_time": timestamp,
                        "access_weight": 1.0
                    }, {"access_type": "store_interaction"})
                except Exception as e:
                    self.logger.debug(f"统一缓存记录访问失败: {e}")
            
            logger.debug(f"✅ Step 12: 对话存储完成 (Session: {session_id}, 用户: {user_memory_id}, AI: {ai_memory_id})")
            
            # 🔥 触发异步评估 (Step 11 + Step 13)
            if self.async_evaluator:
                # 获取上下文记忆
                context_memories = context.get('context_memories', []) if context else []
                
                # 安全地触发异步评估
                self._safe_trigger_async_evaluation(
                    user_input, ai_response, session_id, context_memories
                )
                logger.debug("🚀 异步评估已触发")
            else:
                logger.warning("异步评估器不可用，跳过Step 11-13")
            
        except Exception as e:
            logger.error(f"存储交互失败: {e}")
    
    def _safe_trigger_async_evaluation(self, user_input: str, ai_response: str, 
                                     session_id: str, context_memories: List):
        """安全地触发异步评估 - 使用稳定的启动管理器"""
        try:
            # 确保异步评估器已初始化
            if not self.ensure_async_initialized():
                logger.warning("异步评估器未就绪，跳过异步评估")
                return
            
            # 使用启动管理器安全地加入评估任务
            from .evaluator.async_startup_manager import queue_evaluation_task_safely
            
            # 创建评估协程
            evaluation_coro = self._queue_for_async_evaluation(
                    user_input, ai_response, session_id, context_memories
            )
            
            # 安全地加入队列
            success = queue_evaluation_task_safely(evaluation_coro)
            
            if success:
                logger.debug("✅ 异步评估任务已安全加入队列")
            else:
                logger.warning("❌ 异步评估任务加入失败")
                
        except Exception as e:
            logger.error(f"异步评估触发失败: {e}")
    
    async def _queue_for_async_evaluation(self, user_input: str, ai_response: str, 
                                        session_id: str, context_memories: List):
        """将对话加入异步评估队列 - 简化版本"""
        try:
            if self.async_evaluator and self.async_initialized:
                await self.async_evaluator.queue_dialogue_for_evaluation(
                    user_input=user_input,
                    ai_response=ai_response,
                    session_id=session_id,
                    context_memories=context_memories
                )
                logger.debug("📝 对话已加入异步评估队列")
            else:
                logger.warning("异步评估器未就绪")
                
        except Exception as e:
            logger.error(f"异步评估队列失败: {e}")
    



    def _build_enhanced_context(self, user_input: str, memories: List[Dict], 
                              historical_context: Dict) -> str:
        """Step 8: 组装最终上下文 - 🆕 包含会话对话"""
        context_parts = []
        
        # 角色设定
        context_parts.append("[系统角色设定]")
        context_parts.append("你是Estia，一个智能、友好、具有长期记忆的AI助手。")
        context_parts.append("")
        
        # 核心记忆（高权重）
        core_memories = [m for m in memories if m.get('weight', 0) >= 8.0]
        if core_memories:
            context_parts.append("[核心记忆]")
            for memory in core_memories[:3]:
                content = memory.get('content', '')[:100]
                weight = memory.get('weight', 0)
                context_parts.append(f"• [权重: {weight:.1f}] {content}")
            context_parts.append("")
        
        # 🆕 会话历史对话（按设计文档Step 6实现）
        session_dialogues = historical_context.get('session_dialogues', {})
        if session_dialogues:
            context_parts.append("[历史对话]")
            for session_id, session_data in session_dialogues.items():
                dialogue_pairs = session_data.get('dialogue_pairs', [])
                if dialogue_pairs:
                    context_parts.append(f"会话 {session_id}:")
                    for i, pair in enumerate(dialogue_pairs[-3:]):  # 最近3轮对话
                        user_content = pair['user']['content'][:80]
                        ai_content = pair['assistant']['content'][:80]
                        context_parts.append(f"  {i+1}. 你: {user_content}")
                        context_parts.append(f"     我: {ai_content}")
            context_parts.append("")
        
        # 相关记忆
        relevant_memories = [m for m in memories if m.get('weight', 0) >= 5.0][:8]
        if relevant_memories:
            context_parts.append("[相关记忆]")
            for memory in relevant_memories:
                content = memory.get('content', '')[:120]
                timestamp = memory.get('timestamp', 0)
                try:
                    time_str = datetime.fromtimestamp(timestamp).strftime('%m-%d %H:%M')
                except:
                    time_str = "未知时间"
                context_parts.append(f"• [{time_str}] {content}")
            context_parts.append("")
        
        # 总结内容
        summaries_data = historical_context.get('summaries', {})
        all_summaries = []
        all_summaries.extend(summaries_data.get('direct_summaries', []))
        all_summaries.extend(summaries_data.get('memory_summaries', []))
        
        if all_summaries:
            context_parts.append("[重要总结]")
            for summary in all_summaries[:5]:
                content = summary.get('content', '')[:100]
                context_parts.append(f"• {content}")
            context_parts.append("")
        
        # 当前用户输入
        context_parts.append(f"[当前输入] {user_input}")
        context_parts.append("")
        context_parts.append("请基于以上记忆和历史对话，给出自然、连贯的回复：")
        
        return "\n".join(context_parts)
    
    def _build_fallback_context(self, user_input: str) -> str:
        """构建降级上下文"""
        return f"""[系统角色设定]
你是Estia，一个智能、友好的AI助手。

[用户当前输入]
{user_input}"""
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        stats = {
            'initialized': self.initialized,
            'advanced_features': self.enable_advanced,
            'async_evaluator_running': self.async_initialized,  # 🔥 关键状态
            'components': {
                'db_manager': self.db_manager is not None,
                'vectorizer': self.vectorizer is not None,
                'faiss_retriever': self.faiss_retriever is not None,
                'association_network': self.association_network is not None,
                'history_retriever': self.history_retriever is not None,
                'memory_store': self.memory_store is not None,
                'scorer': self.scorer is not None,
                'async_evaluator': self.async_evaluator is not None  # 🔥 异步评估器状态
            }
        }
        
        # 🆕 添加统一缓存统计
        try:
            from .caching.cache_manager import UnifiedCacheManager
            unified_cache = UnifiedCacheManager.get_instance()
            stats['unified_cache'] = unified_cache.get_stats()
        except Exception as e:
            stats['unified_cache'] = {"error": str(e)}
        
        # 获取记忆统计
        if self.memory_store and self.memory_store.db_manager:
            try:
                result = self.memory_store.db_manager.query("SELECT COUNT(*) FROM memories")
                stats['total_memories'] = result[0][0] if result else 0
            except:
                stats['total_memories'] = 0
        
        # 获取异步队列状态
        if self.async_evaluator:
            try:
                queue_stats = self.async_evaluator.get_queue_status()
                stats['async_queue'] = queue_stats
            except:
                stats['async_queue'] = {'status': 'unknown'}
        
        return stats
    
    async def shutdown(self):
        """🔥 优雅关闭系统 - 使用启动管理器"""
        try:
            # 使用启动管理器关闭异步评估器
            if self.async_evaluator and self.async_initialized:
                try:
                    from .evaluator.async_startup_manager import get_startup_manager
                    startup_manager = get_startup_manager()
                    startup_manager.shutdown()
                    logger.info("✅ 异步评估器已通过启动管理器关闭")
                except Exception as e:
                    logger.warning(f"启动管理器关闭失败，尝试直接关闭: {e}")
                    await self.async_evaluator.stop()
                    logger.info("✅ 异步评估器已直接关闭")
            
            if self.memory_store:
                self.memory_store.close()
                logger.info("✅ MemoryStore已关闭")
            
            if self.db_manager:
                self.db_manager.close()
                logger.info("✅ 数据库连接已关闭")
                
            logger.info("🛑 Estia记忆系统已关闭")
            
        except Exception as e:
            logger.error(f"系统关闭失败: {e}")


def create_estia_memory(enable_advanced: bool = True) -> EstiaMemorySystem:
    """创建Estia记忆系统实例"""
    return EstiaMemorySystem(enable_advanced=enable_advanced) 