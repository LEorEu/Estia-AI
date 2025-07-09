#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia记忆系统主接口 v3.0.0 - 重构版
实现模块化设计，将功能委托给专门的子模块
保持API兼容性，提高可维护性
"""

import time
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# 导入子模块
from .memory_search import MemorySearchManager
from .weight_management import WeightManager
from .lifecycle_management import LifecycleManager
from .system_stats import SystemStatsManager
from .profiling.user_profiler import UserProfiler
from .profiling.summary_generator import SummaryGenerator
from .emotion.emotion_analyzer import EmotionAnalyzer

logger = logging.getLogger(__name__)

class EstiaMemorySystem:
    """
    Estia记忆系统主接口 v3.0.0 - 重构版
    模块化设计，委托功能给专门的子模块
    """
    
    def __init__(self, enable_advanced: bool = True, context_preset: str = None):
        """
        初始化Estia记忆系统 - 重构版本使用ComponentManager
        
        Args:
            enable_advanced: 是否启用高级功能（关联网络、异步评估等）
            context_preset: 上下文长度预设，可选: "compact", "balanced", "detailed"
        """
        # 使用模块级logger，避免重复设置
        self.logger = logger
        
        # 🔥 使用ComponentManager统一管理组件
        from .internal.component_manager import ComponentManager
        self.component_manager = ComponentManager()
        
        # 核心组件（通过ComponentManager管理）
        self.db_manager = None
        self.vectorizer = None
        self.faiss_retriever = None
        
        # 高级组件
        self.association_network = None
        self.history_retriever = None
        self.memory_store = None
        self.scorer = None
        self.async_evaluator = None
        
        # 🆕 功能模块管理器
        self.memory_search_manager = None
        self.weight_manager = None
        self.lifecycle_manager = None
        self.system_stats_manager = None
        self.user_profiler = None
        self.summary_generator = None
        self.emotion_analyzer = None
        
        # 🆕 会话状态管理
        self.current_session_id = None
        self.session_start_time = None
        self.session_timeout = 3600  # 1小时会话超时
        
        # 🆕 上下文长度管理器
        from .context.context_manager import ContextLengthManager
        self.context_manager = ContextLengthManager(preset=context_preset)
        
        # 系统状态
        self.enable_advanced = enable_advanced
        self.initialized = False
        self.async_initialized = False
        
        # 🔥 使用ComponentManager初始化所有组件
        self._register_all_components()
        self._initialize_all_components()
        
        logger.info(f"Estia记忆系统v3.0初始化完成 (高级功能: {'启用' if enable_advanced else '禁用'}, 上下文预设: {self.context_manager.preset})")
    
    def _register_all_components(self):
        """注册所有组件到ComponentManager"""
        # 核心组件注册
        self.component_manager.register_component(
            'db_manager',
            self._create_db_manager,
            dependencies=[],
            config={}
        )
        
        self.component_manager.register_component(
            'memory_store',
            self._create_memory_store,
            dependencies=['db_manager'],
            config={}
        )
        
        if self.enable_advanced:
            # 高级组件注册
            self.component_manager.register_component(
                'vectorizer',
                self._create_vectorizer,
                dependencies=[],
                config={}
            )
            
            self.component_manager.register_component(
                'faiss_retriever',
                self._create_faiss_retriever,
                dependencies=[],
                config={'dimension': 1024}
            )
            
            self.component_manager.register_component(
                'association_network',
                self._create_association_network,
                dependencies=['db_manager'],
                config={}
            )
            
            self.component_manager.register_component(
                'history_retriever',
                self._create_history_retriever,
                dependencies=['db_manager'],
                config={}
            )
            
            self.component_manager.register_component(
                'smart_retriever',
                self._create_smart_retriever,
                dependencies=['db_manager'],
                config={}
            )
            
            self.component_manager.register_component(
                'scorer',
                self._create_scorer,
                dependencies=[],
                config={}
            )
            
            self.component_manager.register_component(
                'async_evaluator',
                self._create_async_evaluator,
                dependencies=['db_manager'],
                config={}
            )
        
        # 功能模块注册
        self.component_manager.register_component(
            'memory_search_manager',
            self._create_memory_search_manager,
            dependencies=['db_manager'],
            config={}
        )
        
        self.component_manager.register_component(
            'weight_manager',
            self._create_weight_manager,
            dependencies=['db_manager'],
            config={}
        )
        
        self.component_manager.register_component(
            'lifecycle_manager',
            self._create_lifecycle_manager,
            dependencies=['db_manager', 'weight_manager'],
            config={}
        )
        
        self.component_manager.register_component(
            'system_stats_manager',
            self._create_system_stats_manager,
            dependencies=['db_manager'],
            config={}
        )
        
        self.component_manager.register_component(
            'user_profiler',
            self._create_user_profiler,
            dependencies=['db_manager'],
            config={}
        )
        
        self.component_manager.register_component(
            'summary_generator',
            self._create_summary_generator,
            dependencies=['db_manager'],
            config={}
        )
        
        self.component_manager.register_component(
            'emotion_analyzer',
            self._create_emotion_analyzer,
            dependencies=[],
            config={}
        )
    
    def _initialize_all_components(self):
        """使用ComponentManager初始化所有组件"""
        try:
            # 初始化所有注册的组件
            self.component_manager.initialize_all()
            
            # 获取初始化的组件并设置到实例属性
            self.db_manager = self.component_manager.get_component('db_manager')
            self.memory_store = self.component_manager.get_component('memory_store')
            
            if self.enable_advanced:
                self.vectorizer = self.component_manager.get_component('vectorizer')
                self.faiss_retriever = self.component_manager.get_component('faiss_retriever')
                self.association_network = self.component_manager.get_component('association_network')
                self.history_retriever = self.component_manager.get_component('history_retriever')
                self.smart_retriever = self.component_manager.get_component('smart_retriever')
                self.scorer = self.component_manager.get_component('scorer')
                self.async_evaluator = self.component_manager.get_component('async_evaluator')
                self.async_initialized = True
            
            # 功能模块
            self.memory_search_manager = self.component_manager.get_component('memory_search_manager')
            self.weight_manager = self.component_manager.get_component('weight_manager')
            self.lifecycle_manager = self.component_manager.get_component('lifecycle_manager')
            self.system_stats_manager = self.component_manager.get_component('system_stats_manager')
            self.user_profiler = self.component_manager.get_component('user_profiler')
            self.summary_generator = self.component_manager.get_component('summary_generator')
            self.emotion_analyzer = self.component_manager.get_component('emotion_analyzer')
            
            self.initialized = True
            logger.info("✅ 所有组件通过ComponentManager初始化成功")
            
        except Exception as e:
            logger.error(f"ComponentManager初始化失败: {e}")
            self.initialized = False
            raise
    
    # 组件创建方法
    def _create_db_manager(self):
        """创建数据库管理器"""
        from .init.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        if db_manager.connect():
            db_manager.initialize_database()
            logger.info("✅ 数据库管理器初始化成功")
        return db_manager
    
    def _create_memory_store(self):
        """创建记忆存储"""
        from .storage.memory_store import MemoryStore
        memory_store = MemoryStore(db_manager=self.component_manager.get_component('db_manager'))
        logger.info("✅ 记忆存储初始化成功 (复用数据库连接)")
        return memory_store
    
    def _create_vectorizer(self):
        """创建向量化器"""
        from .embedding.vectorizer import TextVectorizer
        vectorizer = TextVectorizer()
        logger.info("✅ 向量化器初始化成功")
        return vectorizer
    
    def _create_faiss_retriever(self):
        """创建FAISS检索器"""
        from .retrieval.faiss_search import FAISSSearchEngine
        faiss_retriever = FAISSSearchEngine(
            index_path="data/vectors/memory_index.bin",
            dimension=1024  # Qwen3-Embedding-0.6B
        )
        logger.info("✅ FAISS检索初始化成功")
        return faiss_retriever
    
    def _create_association_network(self):
        """创建关联网络"""
        from .association.network import AssociationNetwork
        association_network = AssociationNetwork(self.component_manager.get_component('db_manager'))
        logger.info("✅ 关联网络初始化成功")
        return association_network
    
    def _create_history_retriever(self):
        """创建历史检索器"""
        from .context.history import HistoryRetriever
        history_retriever = HistoryRetriever(self.component_manager.get_component('db_manager'))
        logger.info("✅ 历史检索器初始化成功")
        return history_retriever
    
    def _create_smart_retriever(self):
        """创建智能检索器"""
        from .retrieval.smart_retriever import SmartRetriever
        smart_retriever = SmartRetriever(self.component_manager.get_component('db_manager'))
        logger.info("✅ 智能检索器初始化成功")
        return smart_retriever
    
    def _create_scorer(self):
        """创建记忆评分器"""
        from .scoring.scorer import MemoryScorer
        scorer = MemoryScorer()
        logger.info("✅ 记忆评分器初始化成功")
        return scorer
    
    def _create_async_evaluator(self):
        """创建异步评估器"""
        from .evaluation.async_evaluator import AsyncMemoryEvaluator
        async_evaluator = AsyncMemoryEvaluator(self.component_manager.get_component('db_manager'))
        logger.info("✅ 异步评估器初始化成功")
        return async_evaluator
    
    def _create_memory_search_manager(self):
        """创建记忆搜索管理器"""
        return MemorySearchManager(self.component_manager.get_component('db_manager'))
    
    def _create_weight_manager(self):
        """创建权重管理器"""
        return WeightManager(self.component_manager.get_component('db_manager'))
    
    def _create_lifecycle_manager(self):
        """创建生命周期管理器"""
        return LifecycleManager(
            self.component_manager.get_component('db_manager'),
            self.component_manager.get_component('weight_manager')
        )
    
    def _create_system_stats_manager(self):
        """创建系统统计管理器"""
        return SystemStatsManager(self.component_manager.get_component('db_manager'))
    
    def _create_user_profiler(self):
        """创建用户画像器"""
        return UserProfiler(self.component_manager.get_component('db_manager'))
    
    def _create_summary_generator(self):
        """创建摘要生成器"""
        return SummaryGenerator(self.component_manager.get_component('db_manager'))
    
    def _create_emotion_analyzer(self):
        """创建情感分析器"""
        return EmotionAnalyzer()
    
    # === 会话管理 ===
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

    # === 13步记忆增强工作流程 ===

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
                # 🔥 降低相似度阈值，提高检索召回率
                similar_memory_ids = [memory_id for memory_id, similarity in search_results 
                                    if memory_id and similarity > 0.3]  # 从0.5降低到0.3
                
                # 如果检索结果太少，进一步降低阈值
                if len(similar_memory_ids) < 3:
                    similar_memory_ids = [memory_id for memory_id, similarity in search_results 
                                        if memory_id and similarity > 0.1]  # 进一步降低到0.1
                
                self.logger.debug(f"FAISS检索到 {len(similar_memory_ids)} 条相似记忆")
            
            # 如果FAISS检索失败，尝试使用MemoryStore的搜索功能
            if not similar_memory_ids and self.memory_store:
                self.logger.debug("FAISS检索失败，使用MemoryStore搜索")
                try:
                    similar_memories = self.memory_store.search_similar(user_input, limit=10)
                    similar_memory_ids = [mem.get('memory_id') for mem in similar_memories 
                                        if mem.get('memory_id')]
                    self.logger.debug(f"MemoryStore搜索到 {len(similar_memory_ids)} 条记忆")
                except Exception as e:
                    self.logger.warning(f"MemoryStore搜索失败: {e}")
            
            # Step 5: 关联网络拓展 (可选)
            expanded_memory_ids = similar_memory_ids.copy()
            if self.enable_advanced and self.association_network and similar_memory_ids:
                self.logger.debug("🕸️ Step 5: 关联网络拓展")
                try:
                    # 对每个相似记忆进行关联拓展
                    for memory_id in similar_memory_ids[:3]:  # 只对前3个记忆进行拓展
                        associated_memories = self.association_network.get_related_memories(
                            memory_id, depth=1, min_strength=0.3
                        )
                        associated_ids = [mem.get('memory_id') for mem in associated_memories 
                                        if mem.get('memory_id')]
                        expanded_memory_ids.extend(associated_ids)
                    
                    # 去重
                    expanded_memory_ids = list(dict.fromkeys(expanded_memory_ids))
                    self.logger.debug(f"关联网络拓展后共有 {len(expanded_memory_ids)} 条记忆")
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
                if self.memory_store and expanded_memory_ids:
                    context_memories = self.memory_store.get_memories_by_ids(expanded_memory_ids)
                    self.logger.debug(f"降级模式：直接获取 {len(context_memories)} 条记忆")
                else:
                    # 如果没有任何记忆，获取最近的记忆
                    if self.memory_store:
                        context_memories = self.memory_store.get_recent_memories(limit=5)
                        self.logger.debug(f"无相似记忆，获取最近 {len(context_memories)} 条记忆")
            
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
        """安全地触发异步评估 - 增强版本（包含丰富上下文）"""
        try:
            # 确保异步评估器已初始化
            if not self.ensure_async_initialized():
                logger.warning("异步评估器未就绪，跳过异步评估")
                return
            
            # 🆕 构建增强的评估上下文
            enhanced_context = self._build_evaluation_context(
                user_input=user_input,
                ai_response=ai_response,
                memories=context_memories,
                session_id=session_id
            )
            
            # 使用启动管理器安全地加入评估任务
            from .evaluator.async_startup_manager import queue_evaluation_task_safely
            
            # 创建评估协程（包含增强上下文）
            evaluation_coro = self._queue_for_async_evaluation(
                    user_input, ai_response, session_id, context_memories, enhanced_context
            )
            
            # 安全地加入队列
            success = queue_evaluation_task_safely(evaluation_coro)
            
            if success:
                logger.debug("✅ 异步评估任务已安全加入队列（增强版上下文）")
            else:
                logger.warning("❌ 异步评估任务加入失败，但不会影响主流程")
                
        except Exception as e:
            logger.error(f"异步评估触发失败: {e}")
            # 不抛出异常，避免影响主流程
    
    async def _queue_for_async_evaluation(self, user_input: str, ai_response: str, 
                                        session_id: str, context_memories: List, 
                                        enhanced_context: Dict[str, Any] = None):
        """将对话加入异步评估队列 - 增强版本"""
        try:
            if self.async_evaluator and self.async_initialized:
                await self.async_evaluator.queue_dialogue_for_evaluation(
                    user_input=user_input,
                    ai_response=ai_response,
                    session_id=session_id,
                    context_memories=context_memories,
                    enhanced_context=enhanced_context  # 🆕 传递增强上下文
                )
                logger.debug("📝 对话已加入异步评估队列（增强版上下文）")
            else:
                logger.warning("异步评估器未就绪")
                
        except Exception as e:
            logger.error(f"异步评估队列失败: {e}")
    
    def _build_evaluation_context(self, user_input: str, ai_response: str, 
                                memories: List[Dict], session_id: str = None) -> Dict[str, Any]:
        """
        构建评估上下文信息
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
            memories: 相关记忆
            session_id: 会话ID
            
        Returns:
            Dict: 增强的评估上下文
        """
        context = {
            'context_memories': memories[:5] if memories else [],
            'user_profile': {},
            'conversation_history': [],
            'topic_context': {},
            'emotional_context': {}
        }
        
        try:
            # 1. 构建用户画像
            core_memories = self._search_core_memories()
            if core_memories['success']:
                user_profile = {
                    'basic_info': [],
                    'preferences': [],
                    'goals': [],
                    'personality_traits': []
                }
                
                for memory in core_memories['memories']:
                    content = memory['content'].lower()
                    if any(keyword in content for keyword in ['我叫', '我是', '姓名', '名字']):
                        user_profile['basic_info'].append(memory['content'])
                    elif any(keyword in content for keyword in ['喜欢', '爱好', '兴趣', '偏好']):
                        user_profile['preferences'].append(memory['content'])
                    elif any(keyword in content for keyword in ['目标', '计划', '想要', '希望']):
                        user_profile['goals'].append(memory['content'])
                    elif any(keyword in content for keyword in ['性格', '特点', '习惯', '风格']):
                        user_profile['personality_traits'].append(memory['content'])
                
                context['user_profile'] = user_profile
            
            # 2. 获取近期对话历史
            if session_id:
                recent_memories = self._search_memories_by_timeframe(days_ago=1, max_results=10)
                if recent_memories['success']:
                    conversation_pairs = []
                    user_msgs = []
                    assistant_msgs = []
                    
                    for memory in recent_memories['memories']:
                        if memory['type'] == 'user_input':
                            user_msgs.append(memory)
                        elif memory['type'] == 'assistant_reply':
                            assistant_msgs.append(memory)
                    
                    # 配对对话
                    for i in range(min(len(user_msgs), len(assistant_msgs))):
                        conversation_pairs.append({
                            'user': user_msgs[i]['content'],
                            'assistant': assistant_msgs[i]['content'],
                            'timestamp': user_msgs[i]['timestamp']
                        })
                    
                    context['conversation_history'] = conversation_pairs[-3:]  # 最近3轮对话
            
            # 3. 构建话题上下文
            if memories:
                topic_keywords = []
                topic_groups = set()
                
                for memory in memories:
                    if memory.get('group_id'):
                        topic_groups.add(memory['group_id'])
                    
                    # 提取关键词
                    content = memory['content']
                    if len(content) > 10:
                        topic_keywords.append(content[:50])  # 取前50个字符作为关键词
                
                # 获取相关话题的发展轨迹
                topic_evolution = []
                for group_id in topic_groups:
                    group_memories = self._get_memories_by_group(group_id)
                    if group_memories:
                        topic_evolution.append({
                            'group_id': group_id,
                            'memory_count': len(group_memories),
                            'latest_content': group_memories[0]['content'] if group_memories else '',
                            'timeline': [mem['timestamp'] for mem in group_memories[:3]]
                        })
                
                context['topic_context'] = {
                    'current_keywords': topic_keywords[:5],
                    'active_topics': list(topic_groups),
                    'topic_evolution': topic_evolution
                }
            
            # 4. 构建情感上下文
            emotional_indicators = []
            if memories:
                for memory in memories:
                    content = memory['content'].lower()
                    # 简单的情感关键词检测
                    if any(word in content for word in ['开心', '高兴', '兴奋', '愉快']):
                        emotional_indicators.append('positive')
                    elif any(word in content for word in ['难过', '沮丧', '烦恼', '郁闷']):
                        emotional_indicators.append('negative')
                    elif any(word in content for word in ['焦虑', '担心', '紧张', '害怕']):
                        emotional_indicators.append('anxious')
                    elif any(word in content for word in ['愤怒', '生气', '恼火', '愤恨']):
                        emotional_indicators.append('angry')
            
            # 分析当前输入的情感倾向
            user_input_lower = user_input.lower()
            current_emotion = 'neutral'
            if any(word in user_input_lower for word in ['开心', '高兴', '兴奋', '愉快']):
                current_emotion = 'positive'
            elif any(word in user_input_lower for word in ['难过', '沮丧', '烦恼', '郁闷']):
                current_emotion = 'negative'
            elif any(word in user_input_lower for word in ['焦虑', '担心', '紧张', '害怕']):
                current_emotion = 'anxious'
            elif any(word in user_input_lower for word in ['愤怒', '生气', '恼火', '愤恨']):
                current_emotion = 'angry'
            
            context['emotional_context'] = {
                'current_emotion': current_emotion,
                'historical_emotions': emotional_indicators,
                'emotion_pattern': self._analyze_emotion_pattern(emotional_indicators)
            }
            
        except Exception as e:
            logger.error(f"构建评估上下文失败: {e}")
        
        return context
    
    def _get_memories_by_group(self, group_id: str) -> List[Dict]:
        """根据group_id获取记忆"""
        try:
            query = """
                SELECT id, content, type, weight, timestamp, group_id
                FROM memories 
                WHERE group_id = ?
                AND (archived IS NULL OR archived = 0)
                ORDER BY timestamp DESC
            """
            results = self.db_manager.execute_query(query, (group_id,))
            
            memories = []
            if results:
                for row in results:
                    memories.append({
                        'id': row[0],
                        'content': row[1],
                        'type': row[2],
                        'weight': row[3],
                        'timestamp': row[4],
                        'group_id': row[5]
                    })
            
            return memories
            
        except Exception as e:
            logger.error(f"获取分组记忆失败: {e}")
            return []
    
    def _analyze_emotion_pattern(self, emotional_indicators: List[str]) -> str:
        """分析情感模式"""
        if not emotional_indicators:
            return 'stable'
        
        # 统计情感类型
        emotion_counts = {}
        for emotion in emotional_indicators:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # 分析模式
        if len(emotion_counts) == 1:
            return 'consistent'  # 情感一致
        elif 'positive' in emotion_counts and 'negative' in emotion_counts:
            return 'mixed'  # 情感混合
        elif any(count > 2 for count in emotion_counts.values()):
            return 'intense'  # 情感强烈
        else:
            return 'fluctuating'  # 情感波动



    def _build_enhanced_context(self, user_input: str, memories: List[Dict], 
                              historical_context: Dict) -> str:
        """Step 9: 使用上下文长度管理器构建增强上下文，包含分层信息"""
        # 获取当前会话的对话历史
        current_session_dialogues = []
        if self.current_session_id:
            try:
                # 从当前会话获取最近的对话
                session_memories = self.memory_store.get_session_memories(
                    self.current_session_id, max_count=10
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
        
        # 🆕 获取分层信息
        layered_info = self.get_layered_context_info(memories)
        
        # 使用上下文长度管理器构建基础上下文
        base_context = self.context_manager.build_enhanced_context(
            user_input=user_input,
            memories=memories,
            historical_context=historical_context,
            current_session_id=self.current_session_id,
            current_session_dialogues=current_session_dialogues
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
                    content = memory.get('content', '')[:100] + "..." if len(memory.get('content', '')) > 100 else memory.get('content', '')
                    base_context += f"\n• [权重: {weight:.1f}] {content}"
        
        return base_context
    
    def _build_fallback_context(self, user_input: str) -> str:
        """构建降级上下文"""
        return f"""[系统角色设定]
你是Estia，一个智能、友好的AI助手。

[用户当前输入]
{user_input}"""
    
    def get_memory_layer(self, weight: float) -> str:
        """
        根据权重确定记忆层级
        
        Args:
            weight: 记忆权重 (1.0-10.0)
            
        Returns:
            str: 层级名称
        """
        if 9.0 <= weight <= 10.0:
            return "核心记忆"  # 永久保留
        elif 7.0 <= weight < 9.0:
            return "归档记忆"  # 长期保留
        elif 4.0 <= weight < 7.0:
            return "长期记忆"  # 定期清理
        else:
            return "短期记忆"  # 快速过期
    
    def get_layered_context_info(self, memories: List[Dict]) -> Dict[str, Any]:
        """
        获取分层上下文信息
        
        Args:
            memories: 记忆列表
            
        Returns:
            Dict: 分层统计信息
        """
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
            layer = self.get_memory_layer(weight)
            layer_stats[layer].append(memory)
        
        return {
            'layer_distribution': {
                layer: len(memories_in_layer) 
                for layer, memories_in_layer in layer_stats.items()
            },
            'layered_memories': layer_stats
        }
    
    def archive_old_memories(self, days_threshold: int = 30, archive_weight_penalty: float = 0.5) -> Dict[str, Any]:
        """
        归档过期记忆 - 委托给生命周期管理器
        
        Args:
            days_threshold: 归档天数阈值
            archive_weight_penalty: 归档权重惩罚系数
            
        Returns:
            Dict: 归档结果
        """
        try:
            if self.lifecycle_manager:
                # 委托给生命周期管理器
                return self.lifecycle_manager.archive_old_memories(days_threshold, archive_weight_penalty)
            else:
                # 降级方案
                return self._archive_memories_fallback(days_threshold, archive_weight_penalty)
                
        except Exception as e:
            logger.error(f"归档记忆失败: {e}")
            return {'success': False, 'message': f'归档失败: {str(e)}'}
    
    def _archive_memories_fallback(self, days_threshold: int, archive_weight_penalty: float) -> Dict[str, Any]:
        """归档记忆降级方案"""
        if not self.initialized or not self.memory_store:
            return {'success': False, 'message': '系统未初始化'}
        
        try:
            # 简单的归档逻辑
            current_time = time.time()
            cutoff_time = current_time - (days_threshold * 24 * 3600)
            
            # 简单标记为已访问，不做复杂的归档操作
            update_query = """
                UPDATE memories 
                SET last_accessed = ? 
                WHERE timestamp < ?
                AND weight < 4.0
            """
            
            self.db_manager.execute_query(update_query, (current_time, cutoff_time))
            
            return {
                'success': True,
                'archived_count': 0,
                'message': '记忆归档完成（降级模式）',
                'method': 'fallback'
            }
            
        except Exception as e:
            logger.error(f"降级归档失败: {e}")
            return {'success': False, 'message': f'降级归档失败: {str(e)}'}
    
    def restore_archived_memories(self, memory_ids: List[str] = None, restore_weight_bonus: float = 1.5) -> Dict[str, Any]:
        """
        恢复归档记忆（当再次被访问时）
        
        Args:
            memory_ids: 要恢复的记忆ID列表，None表示恢复所有
            restore_weight_bonus: 恢复时的权重奖励系数
            
        Returns:
            Dict: 恢复结果
        """
        if not self.initialized or not self.memory_store:
            return {'success': False, 'message': '系统未初始化'}
        
        try:
            current_time = time.time()
            
            if memory_ids:
                # 恢复指定记忆
                placeholders = ','.join(['?' for _ in memory_ids])
                restore_query = f"""
                    UPDATE memories 
                    SET archived = 0,
                        weight = CASE 
                            WHEN weight * ? <= 10.0 THEN weight * ?
                            ELSE 10.0
                        END,
                        last_accessed = ?,
                        metadata = CASE 
                            WHEN metadata IS NULL THEN '{{"restored_at": ' || ? || '}}'
                            ELSE json_patch(metadata, '{{"restored_at": ' || ? || '}}')
                        END
                    WHERE id IN ({placeholders}) AND archived = 1
                """
                params = [restore_weight_bonus, restore_weight_bonus, current_time, current_time, current_time] + memory_ids
            else:
                # 恢复所有归档记忆（慎用）
                restore_query = """
                    UPDATE memories 
                    SET archived = 0,
                        weight = CASE 
                            WHEN weight * ? <= 10.0 THEN weight * ?
                            ELSE 10.0
                        END,
                        last_accessed = ?,
                        metadata = CASE 
                            WHEN metadata IS NULL THEN '{"restored_at": ' || ? || '}'
                            ELSE json_patch(metadata, '{"restored_at": ' || ? || '}')
                        END
                    WHERE archived = 1
                """
                params = [restore_weight_bonus, restore_weight_bonus, current_time, current_time, current_time]
            
            result = self.db_manager.execute_query(restore_query, params)
            
            if result:
                restored_count = result.rowcount if hasattr(result, 'rowcount') else 0
                logger.info(f"恢复了 {restored_count} 条归档记忆")
                
                return {
                    'success': True,
                    'restored_count': restored_count,
                    'weight_bonus': restore_weight_bonus,
                    'message': f'成功恢复 {restored_count} 条归档记忆'
                }
            else:
                return {
                    'success': True,
                    'restored_count': 0,
                    'message': '没有找到需要恢复的归档记忆'
                }
                
        except Exception as e:
            logger.error(f"恢复归档记忆失败: {e}")
            return {
                'success': False,
                'message': f'恢复失败: {str(e)}'
            }
    
    def get_memory_lifecycle_stats(self) -> Dict[str, Any]:
        """
        获取记忆生命周期统计
        
        Returns:
            Dict: 生命周期统计信息
        """
        if not self.initialized or not self.db_manager:
            return {}
        
        try:
            # 按权重范围统计记忆数量
            stats_query = """
                SELECT 
                    CASE 
                        WHEN weight >= 9.0 THEN '核心记忆'
                        WHEN weight >= 7.0 THEN '归档记忆'
                        WHEN weight >= 4.0 THEN '长期记忆'
                        ELSE '短期记忆'
                    END as layer,
                    COUNT(*) as count,
                    AVG(weight) as avg_weight,
                    MIN(timestamp) as oldest_timestamp,
                    MAX(timestamp) as newest_timestamp
                FROM memories 
                GROUP BY 
                    CASE 
                        WHEN weight >= 9.0 THEN '核心记忆'
                        WHEN weight >= 7.0 THEN '归档记忆'
                        WHEN weight >= 4.0 THEN '长期记忆'
                        ELSE '短期记忆'
                    END
            """
            
            results = self.db_manager.execute_query(stats_query)
            
            stats = {}
            if results:
                for row in results:
                    layer = row[0]
                    stats[layer] = {
                        'count': row[1],
                        'avg_weight': round(row[2], 2),
                        'oldest_days': int((time.time() - row[3]) / 86400) if row[3] else 0,
                        'newest_days': int((time.time() - row[4]) / 86400) if row[4] else 0
                    }
            
            return {
                'layer_statistics': stats,
                'total_memories': sum(s['count'] for s in stats.values()),
                'last_updated': time.time()
            }
            
        except Exception as e:
            logger.error(f"获取生命周期统计失败: {e}")
            return {}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息 - 委托给系统统计管理器"""
        try:
            if self.system_stats_manager:
                # 构建组件状态信息
                components = {
                    'initialized': self.initialized,
                    'advanced_features': self.enable_advanced,
                    'async_initialized': self.async_initialized,
                    'db_manager': self.db_manager,
                    'vectorizer': self.vectorizer,
                    'faiss_retriever': self.faiss_retriever,
                    'association_network': self.association_network,
                    'history_retriever': self.history_retriever,
                    'memory_store': self.memory_store,
                    'scorer': self.scorer,
                    'async_evaluator': self.async_evaluator
                }
                
                # 委托给系统统计管理器
                return self.system_stats_manager.get_system_stats(components)
            else:
                # 降级方案
                return self._get_basic_system_stats()
                
        except Exception as e:
            logger.error(f"获取系统统计失败: {e}")
            return self._get_basic_system_stats()
    
    def _get_basic_system_stats(self) -> Dict[str, Any]:
        """基础系统统计（降级方案）"""
        return {
            'initialized': self.initialized,
            'advanced_features': self.enable_advanced,
            'async_evaluator_running': self.async_initialized,
            'components': {
                'db_manager': self.db_manager is not None,
                'vectorizer': self.vectorizer is not None,
                'memory_store': self.memory_store is not None,
                'functional_modules': {
                    'memory_search_manager': self.memory_search_manager is not None,
                    'weight_manager': self.weight_manager is not None,
                    'lifecycle_manager': self.lifecycle_manager is not None,
                    'system_stats_manager': self.system_stats_manager is not None,
                    'user_profiler': self.user_profiler is not None,
                    'summary_generator': self.summary_generator is not None,
                    'emotion_analyzer': self.emotion_analyzer is not None,
                }
            },
            'version': '3.0.0',
            'timestamp': time.time()
        }
    
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

    def update_memory_weight_dynamically(self, memory_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        动态更新记忆权重 - 委托给权重管理器
        
        Args:
            memory_id: 记忆ID
            context: 上下文信息（用于计算权重变化）
            
        Returns:
            Dict: 更新结果
        """
        try:
            if self.weight_manager:
                # 委托给权重管理器
                return self.weight_manager.update_memory_weight_dynamically(memory_id, context)
            else:
                # 降级方案
                return self._update_weight_fallback(memory_id, context)
                
        except Exception as e:
            logger.error(f"权重更新失败: {e}")
            return {'success': False, 'message': f'更新失败: {str(e)}'}
    
    def _update_weight_fallback(self, memory_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """权重更新降级方案"""
        if not self.initialized or not self.memory_store:
            return {'success': False, 'message': '系统未初始化'}
        
        try:
            # 简单的权重更新逻辑
            current_time = time.time()
            update_query = "UPDATE memories SET last_accessed = ? WHERE id = ?"
            self.db_manager.execute_query(update_query, (current_time, memory_id))
            
            return {
                'success': True,
                'memory_id': memory_id,
                'message': '权重更新完成（降级模式）',
                'method': 'fallback'
            }
            
        except Exception as e:
            logger.error(f"降级权重更新失败: {e}")
            return {'success': False, 'message': f'降级更新失败: {str(e)}'}
    
    def _calculate_dynamic_weight_factors(self, memory: Any, current_time: float, context: Dict[str, Any] = None) -> Dict[str, float]:
        """
        计算动态权重调整因子
        
        Args:
            memory: 记忆数据
            current_time: 当前时间
            context: 上下文信息
            
        Returns:
            Dict: 权重调整因子
        """
        factors = {
            'time_decay': 1.0,        # 时间衰减因子
            'access_frequency': 1.0,   # 访问频率因子
            'contextual_relevance': 1.0, # 上下文相关性因子
            'emotional_intensity': 1.0,  # 情感强度因子
            'recency_boost': 1.0       # 近期活跃度因子
        }
        
        try:
            creation_time = memory[5]
            last_accessed = memory[9]
            age_days = (current_time - creation_time) / 86400
            
            # 1. 时间衰减因子（记忆随时间自然衰减）
            if age_days > 0:
                # 核心记忆衰减更慢，短期记忆衰减更快
                current_weight = memory[6]
                if current_weight >= 9.0:  # 核心记忆
                    decay_rate = 0.995  # 每天衰减0.5%
                elif current_weight >= 7.0:  # 归档记忆
                    decay_rate = 0.99   # 每天衰减1%
                elif current_weight >= 4.0:  # 长期记忆
                    decay_rate = 0.98   # 每天衰减2%
                else:  # 短期记忆
                    decay_rate = 0.95   # 每天衰减5%
                
                factors['time_decay'] = decay_rate ** age_days
            
            # 2. 访问频率因子（经常访问的记忆权重增加）
            hours_since_last_access = (current_time - last_accessed) / 3600
            if hours_since_last_access < 24:  # 24小时内访问过
                factors['access_frequency'] = 1.1  # 增强10%
            elif hours_since_last_access < 168:  # 一周内访问过
                factors['access_frequency'] = 1.05  # 增强5%
            else:
                factors['access_frequency'] = 0.98  # 轻微衰减
            
            # 3. 上下文相关性因子
            if context:
                current_topic = context.get('current_topic', '')
                user_emotion = context.get('user_emotion', 'neutral')
                session_type = context.get('session_type', 'normal')
                
                # 根据当前话题调整权重
                memory_content = memory[1].lower()  # content字段
                if current_topic and current_topic.lower() in memory_content:
                    factors['contextual_relevance'] = 1.2  # 话题相关性强，增强20%
                
                # 根据情感状态调整权重
                if user_emotion in ['happy', 'excited'] and '开心' in memory_content:
                    factors['emotional_intensity'] = 1.15
                elif user_emotion in ['sad', 'depressed'] and '难过' in memory_content:
                    factors['emotional_intensity'] = 1.15
            
            # 4. 近期活跃度因子（刚被访问的记忆临时权重提升）
            minutes_since_access = (current_time - last_accessed) / 60
            if minutes_since_access < 30:  # 30分钟内刚被访问
                factors['recency_boost'] = 1.3  # 临时增强30%
            elif minutes_since_access < 120:  # 2小时内
                factors['recency_boost'] = 1.1  # 轻微增强
            
        except Exception as e:
            logger.error(f"计算权重因子失败: {e}")
        
        return factors
    
    def _apply_weight_factors(self, current_weight: float, factors: Dict[str, float]) -> float:
        """
        应用权重调整因子
        
        Args:
            current_weight: 当前权重
            factors: 权重调整因子
            
        Returns:
            float: 新的权重值
        """
        try:
            # 综合所有因子
            combined_factor = 1.0
            for factor_name, factor_value in factors.items():
                combined_factor *= factor_value
            
            new_weight = current_weight * combined_factor
            
            # 确保权重在合理范围内
            new_weight = max(0.1, min(10.0, new_weight))
            
            return round(new_weight, 2)
            
        except Exception as e:
            logger.error(f"应用权重因子失败: {e}")
            return current_weight
    
    def get_memory_search_tools(self) -> List[Dict[str, Any]]:
        """
        获取LLM可用的记忆搜索工具定义 - 委托给记忆搜索管理器
        
        Returns:
            List: 工具定义列表
        """
        try:
            if self.memory_search_manager:
                # 委托给记忆搜索管理器
                return self.memory_search_manager.get_memory_search_tools()
            else:
                # 降级方案 - 返回基础工具定义
                return self._get_basic_search_tools()
                
        except Exception as e:
            logger.error(f"获取搜索工具失败: {e}")
            return self._get_basic_search_tools()
    
    def _get_basic_search_tools(self) -> List[Dict[str, Any]]:
        """基础搜索工具定义（降级方案）"""
        return [
            {
                "name": "search_memories_by_keyword",
                "description": "根据关键词搜索相关记忆",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "string", "description": "搜索关键词"},
                        "max_results": {"type": "integer", "default": 5}
                    },
                    "required": ["keywords"]
                }
            }
        ]
    
    def execute_memory_search_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行记忆搜索工具 - 委托给记忆搜索管理器
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            Dict: 搜索结果
        """
        try:
            if self.memory_search_manager:
                # 委托给记忆搜索管理器
                return self.memory_search_manager.execute_memory_search_tool(tool_name, parameters)
            else:
                # 降级方案 - 仅支持基本关键词搜索
                return self._execute_search_tool_fallback(tool_name, parameters)
                
        except Exception as e:
            logger.error(f"执行记忆搜索工具失败: {e}")
            return {
                'success': False,
                'message': f'工具执行失败: {str(e)}',
                'memories': []
            }
    
    def _execute_search_tool_fallback(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """搜索工具执行降级方案"""
        if tool_name == "search_memories_by_keyword":
            try:
                keywords = parameters.get('keywords', '')
                max_results = parameters.get('max_results', 5)
                
                # 简单的关键词搜索
                search_query = """
                    SELECT id, content, type, weight, timestamp
                    FROM memories 
                    WHERE content LIKE ? 
                    ORDER BY weight DESC, timestamp DESC
                    LIMIT ?
                """
                
                results = self.db_manager.execute_query(
                    search_query, 
                    (f'%{keywords}%', max_results)
                )
                
                memories = []
                if results:
                    for row in results:
                        memories.append({
                            'id': row[0],
                            'content': row[1],
                            'type': row[2],
                            'weight': row[3],
                            'timestamp': row[4]
                        })
                
                return {
                    'success': True,
                    'message': f'找到 {len(memories)} 条记忆（降级搜索）',
                    'memories': memories,
                    'method': 'fallback'
                }
                
            except Exception as e:
                logger.error(f"降级搜索失败: {e}")
                return {'success': False, 'message': f'降级搜索失败: {str(e)}', 'memories': []}
        
        else:
            return {
                'success': False,
                'message': f'降级模式不支持工具: {tool_name}',
                'memories': []
            }
    
    # 🔥 以下搜索方法已委托给memory_search_manager，保留空实现以确保向后兼容
    def _search_memories_by_keyword(self, keywords: str, max_results: int = 5, weight_threshold: float = 3.0) -> Dict[str, Any]:
        """关键词搜索记忆 - 委托给memory_search_manager"""
        if self.memory_search_manager:
            return self.memory_search_manager.search_memories_by_keyword(keywords, max_results, weight_threshold)
        else:
            return self._execute_search_tool_fallback("search_memories_by_keyword", {
                'keywords': keywords, 'max_results': max_results, 'weight_threshold': weight_threshold
            })
    
    def _search_memories_by_timeframe(self, days_ago: int, max_results: int = 10) -> Dict[str, Any]:
        """时间范围搜索记忆 - 委托给memory_search_manager"""
        if self.memory_search_manager:
            return self.memory_search_manager.search_memories_by_timeframe(days_ago, max_results)
        else:
            return {
                'success': False,
                'message': '时间范围搜索需要memory_search_manager',
                'memories': []
            }
    
    def _search_core_memories(self, category: str = '') -> Dict[str, Any]:
        """搜索核心记忆 - 委托给memory_search_manager"""
        if self.memory_search_manager:
            return self.memory_search_manager.search_core_memories(category)
        else:
            return {
                'success': False,
                'message': '核心记忆搜索需要memory_search_manager',
                'memories': []
            }
    
    def _get_related_memories_tool(self, reference_memory_id: str, association_types: List[str]) -> Dict[str, Any]:
        """获取相关记忆（工具版本）"""
        try:
            if not self.association_network:
                return {'success': False, 'message': '关联网络未初始化', 'memories': []}
            
            # 使用关联网络获取相关记忆
            related_memory_ids = []
            for assoc_type in association_types:
                associated = self.association_network.get_related_memories(
                    reference_memory_id, depth=1, min_strength=0.3
                )
                related_memory_ids.extend([mem['target_id'] for mem in associated])
            
            # 去重
            related_memory_ids = list(set(related_memory_ids))
            
            if not related_memory_ids:
                return {
                    'success': True,
                    'message': '没有找到相关记忆',
                    'memories': [],
                    'search_type': 'related_memories'
                }
            
            # 获取相关记忆详情
            placeholders = ','.join(['?' for _ in related_memory_ids])
            search_query = f"""
                SELECT id, content, type, weight, timestamp, group_id
                FROM memories 
                WHERE id IN ({placeholders})
                AND (archived IS NULL OR archived = 0)
                ORDER BY weight DESC
            """
            
            results = self.db_manager.execute_query(search_query, related_memory_ids)
            
            memories = []
            if results:
                for row in results:
                    memories.append({
                        'id': row[0],
                        'content': row[1],
                        'type': row[2],
                        'weight': row[3],
                        'timestamp': row[4],
                        'group_id': row[5],
                        'layer': self.get_memory_layer(row[3])
                    })
            
            return {
                'success': True,
                'message': f'找到 {len(memories)} 条相关记忆',
                'memories': memories,
                'search_type': 'related_memories',
                'parameters': {
                    'reference_memory_id': reference_memory_id,
                    'association_types': association_types
                }
            }
            
        except Exception as e:
            logger.error(f"相关记忆搜索失败: {e}")
            return {'success': False, 'message': str(e), 'memories': []}


    # 🆕 新的API方法，利用新的功能模块
    def get_user_profile(self, user_id: str = None, include_history: bool = True) -> Dict[str, Any]:
        """获取用户画像 - 委托给用户画像器"""
        try:
            if self.user_profiler:
                return self.user_profiler.get_user_profile(user_id, include_history)
            else:
                return {
                    'success': False,
                    'message': '用户画像器未初始化',
                    'profile': {}
                }
        except Exception as e:
            logger.error(f"获取用户画像失败: {e}")
            return {'success': False, 'message': str(e), 'profile': {}}
    
    def generate_user_summary(self, summary_type: str = 'daily', user_id: str = None) -> Dict[str, Any]:
        """生成用户摘要 - 委托给摘要生成器"""
        try:
            if self.summary_generator:
                return self.summary_generator.generate_user_summary(summary_type, user_id)
            else:
                return {
                    'success': False,
                    'message': '摘要生成器未初始化',
                    'summary': {}
                }
        except Exception as e:
            logger.error(f"生成用户摘要失败: {e}")
            return {'success': False, 'message': str(e), 'summary': {}}
    
    def analyze_emotion(self, text: str, return_details: bool = False) -> Dict[str, Any]:
        """分析情感 - 委托给情感分析器"""
        try:
            if self.emotion_analyzer:
                return self.emotion_analyzer.analyze_emotion(text, return_details)
            else:
                return {
                    'success': False,
                    'message': '情感分析器未初始化',
                    'emotion': 'neutral'
                }
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {'success': False, 'message': str(e), 'emotion': 'neutral'}
    
    def get_lifecycle_stats(self) -> Dict[str, Any]:
        """获取生命周期统计 - 委托给生命周期管理器"""
        try:
            if self.lifecycle_manager:
                return self.lifecycle_manager.get_lifecycle_stats()
            else:
                return self.get_memory_lifecycle_stats()  # 降级方案
        except Exception as e:
            logger.error(f"获取生命周期统计失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def cleanup_old_memories(self, days_threshold: int = 60, weight_threshold: float = 2.0) -> Dict[str, Any]:
        """清理过期记忆 - 委托给生命周期管理器"""
        try:
            if self.lifecycle_manager:
                return self.lifecycle_manager.cleanup_old_memories(days_threshold, weight_threshold)
            else:
                return {
                    'success': False,
                    'message': '生命周期管理器未初始化',
                    'cleaned_count': 0
                }
        except Exception as e:
            logger.error(f"清理记忆失败: {e}")
            return {'success': False, 'message': str(e), 'cleaned_count': 0}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计 - 委托给系统统计管理器"""
        try:
            if self.system_stats_manager:
                return self.system_stats_manager.get_performance_stats()
            else:
                return {
                    'success': False,
                    'message': '系统统计管理器未初始化',
                    'performance': {}
                }
        except Exception as e:
            logger.error(f"获取性能统计失败: {e}")
            return {'success': False, 'message': str(e), 'performance': {}}


def create_estia_memory(enable_advanced: bool = True, context_preset: str = None) -> EstiaMemorySystem:
    """创建Estia记忆系统实例"""
    return EstiaMemorySystem(enable_advanced=enable_advanced, context_preset=context_preset) 