#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia记忆系统主接口 v4.0.0 - 轻量级协调器版本
真正的模块化设计，所有具体实现委托给专门的组件
主文件代码量减少到300行以内
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# 导入专门的组件引擎
from .engines.query_enhancer import QueryEnhancer
from .engines.interaction_manager import InteractionManager
from .engines.context_builder import ContextBuilder
from .engines.system_manager import SystemManager

# 导入子模块管理器
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
    Estia记忆系统主接口 v4.0.0 - 轻量级协调器
    所有具体实现委托给专门的组件引擎
    """
    
    def __init__(self, enable_advanced: bool = True, context_preset: str = None):
        """
        初始化Estia记忆系统 - 轻量级协调器版本
        
        Args:
            enable_advanced: 是否启用高级功能
            context_preset: 上下文长度预设
        """
        self.logger = logger
        
        # 系统状态
        self.enable_advanced = enable_advanced
        self.initialized = False
        self.async_initialized = False
        
        # 会话管理
        self.current_session_id = None
        self.session_start_time = None
        self.session_timeout = 3600  # 1小时会话超时
        
        # 🔥 使用ComponentManager统一管理所有组件
        from .internal.component_manager import ComponentManager
        self.component_manager = ComponentManager()
        
        # 核心组件（由ComponentManager管理）
        self.db_manager = None
        self.memory_store = None
        self.vectorizer = None
        self.faiss_retriever = None
        self.association_network = None
        self.history_retriever = None
        self.smart_retriever = None
        self.scorer = None
        self.async_evaluator = None
        
        # 功能模块
        self.memory_search_manager = None
        self.weight_manager = None
        self.lifecycle_manager = None
        self.system_stats_manager = None
        self.user_profiler = None
        self.summary_generator = None
        self.emotion_analyzer = None
        
        # 🆕 专门的组件引擎
        self.query_enhancer = None
        self.interaction_manager = None
        self.context_builder = None
        self.system_manager = None
        
        # 上下文管理器
        from .context.context_manager import ContextLengthManager
        self.context_manager = ContextLengthManager(preset=context_preset)
        
        # 初始化所有组件
        self._initialize_system()
        
        logger.info(f"Estia记忆系统v4.0轻量级协调器初始化完成 (高级功能: {'启用' if enable_advanced else '禁用'})")
    
    def _initialize_system(self):
        """初始化整个系统"""
        try:
            # 1. 注册所有组件
            self._register_all_components()
            
            # 2. 初始化所有组件
            self._initialize_all_components()
            
            # 3. 创建专门的组件引擎
            self._create_component_engines()
            
            self.initialized = True
            logger.info("✅ 轻量级协调器初始化成功")
            
        except Exception as e:
            logger.error(f"系统初始化失败: {e}")
            self.initialized = False
            raise
    
    def _register_all_components(self):
        """注册所有组件到ComponentManager"""
        # 核心组件
        self.component_manager.register_component('db_manager', self._create_db_manager)
        self.component_manager.register_component('memory_store', self._create_memory_store, ['db_manager'])
        
        if self.enable_advanced:
            # 高级组件
            self.component_manager.register_component('vectorizer', self._create_vectorizer)
            self.component_manager.register_component('faiss_retriever', self._create_faiss_retriever)
            self.component_manager.register_component('association_network', self._create_association_network, ['db_manager'])
            self.component_manager.register_component('history_retriever', self._create_history_retriever, ['db_manager'])
            self.component_manager.register_component('smart_retriever', self._create_smart_retriever, ['db_manager'])
            self.component_manager.register_component('scorer', self._create_scorer)
            self.component_manager.register_component('async_evaluator', self._create_async_evaluator, ['db_manager'])
        
        # 功能模块
        self.component_manager.register_component('memory_search_manager', self._create_memory_search_manager, ['db_manager'])
        self.component_manager.register_component('weight_manager', self._create_weight_manager, ['db_manager'])
        self.component_manager.register_component('lifecycle_manager', self._create_lifecycle_manager, ['db_manager', 'weight_manager'])
        self.component_manager.register_component('system_stats_manager', self._create_system_stats_manager, ['db_manager'])
        self.component_manager.register_component('user_profiler', self._create_user_profiler, ['db_manager'])
        self.component_manager.register_component('summary_generator', self._create_summary_generator, ['db_manager'])
        self.component_manager.register_component('emotion_analyzer', self._create_emotion_analyzer)
    
    def _initialize_all_components(self):
        """初始化所有组件"""
        self.component_manager.initialize_all()
        
        # 获取组件引用
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
    
    def _create_component_engines(self):
        """创建专门的组件引擎"""
        components = {
            'db_manager': self.db_manager,
            'vectorizer': self.vectorizer,
            'faiss_retriever': self.faiss_retriever,
            'association_network': self.association_network,
            'history_retriever': self.history_retriever,
            'smart_retriever': self.smart_retriever,
            'scorer': self.scorer,
            'context_manager': self.context_manager,
            'memory_store': self.memory_store,
            'async_evaluator': self.async_evaluator,
            'memory_search_manager': self.memory_search_manager,
            'weight_manager': self.weight_manager,
            'lifecycle_manager': self.lifecycle_manager,
            'system_stats_manager': self.system_stats_manager,
            'user_profiler': self.user_profiler,
            'emotion_analyzer': self.emotion_analyzer
        }
        
        # 创建专门的引擎
        self.query_enhancer = QueryEnhancer(components)
        self.interaction_manager = InteractionManager(components)
        self.context_builder = ContextBuilder(components)
        self.system_manager = SystemManager(components)
    
    # === 核心API接口 - 委托给专门的组件引擎 ===
    
    def enhance_query(self, user_input: str, context: Optional[Dict] = None) -> str:
        """委托给QueryEnhancer处理查询增强"""
        # 会话管理
        context = self._prepare_context(context)
        
        # 委托给QueryEnhancer
        return self.query_enhancer.enhance_query(user_input, context)
    
    def store_interaction(self, user_input: str, ai_response: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """委托给InteractionManager处理交互存储"""
        # 会话管理
        context = self._prepare_context(context)
        
        # 委托给InteractionManager
        return self.interaction_manager.store_interaction(user_input, ai_response, context)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """委托给SystemManager获取系统统计"""
        return self.system_manager.get_system_stats()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """委托给SystemManager获取性能统计"""
        return self.system_manager.get_performance_stats()
    
    # === 其他功能API - 委托给SystemManager ===
    
    def get_memory_search_tools(self) -> list:
        """获取记忆搜索工具"""
        return self.system_manager.get_memory_search_tools()
    
    def execute_memory_search_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """执行记忆搜索工具"""
        return self.system_manager.execute_memory_search_tool(tool_name, **kwargs)
    
    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """分析情感"""
        return self.system_manager.analyze_emotion(text)
    
    def get_user_profile(self, user_id: str = None) -> Dict[str, Any]:
        """获取用户画像"""
        return self.system_manager.get_user_profile(user_id)
    
    def update_memory_weight_dynamically(self, memory_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """动态更新记忆权重"""
        return self.system_manager.update_memory_weight_dynamically(memory_id, context)
    
    def archive_old_memories(self, days_threshold: int = 30) -> Dict[str, Any]:
        """归档旧记忆"""
        return self.system_manager.archive_old_memories(days_threshold)
    
    # === 会话管理 ===
    
    def _prepare_context(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """准备上下文信息"""
        if context is None:
            context = {}
        
        # 确保有session_id
        if 'session_id' not in context:
            context['session_id'] = self.get_current_session_id()
        
        return context
    
    def get_current_session_id(self) -> str:
        """获取当前会话ID"""
        current_time = time.time()
        
        if (not self.current_session_id or 
            not self.session_start_time or 
            (current_time - self.session_start_time) > self.session_timeout):
            return self.start_new_session()
        
        return self.current_session_id
    
    def start_new_session(self, session_id: str = None) -> str:
        """开始新会话"""
        current_time = time.time()
        
        if session_id:
            self.current_session_id = session_id
        else:
            timestamp_str = datetime.fromtimestamp(current_time).strftime('%Y%m%d_%H%M%S')
            self.current_session_id = f"sess_{timestamp_str}"
        
        self.session_start_time = current_time
        logger.info(f"🆕 开始新会话: {self.current_session_id}")
        return self.current_session_id
    
    def end_current_session(self):
        """结束当前会话"""
        if self.current_session_id:
            logger.info(f"🔚 结束会话: {self.current_session_id}")
            self.current_session_id = None
            self.session_start_time = None
    
    def ensure_async_initialized(self) -> bool:
        """确保异步组件初始化"""
        return self.system_manager.ensure_async_initialized()
    
    # === 组件创建方法（简化版本）===
    
    def _create_db_manager(self):
        from .init.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        if db_manager.connect():
            db_manager.initialize_database()
        return db_manager
    
    def _create_memory_store(self):
        from .storage.memory_store import MemoryStore
        return MemoryStore(db_manager=self.component_manager.get_component('db_manager'))
    
    def _create_vectorizer(self):
        from .embedding.vectorizer import TextVectorizer
        return TextVectorizer()
    
    def _create_faiss_retriever(self):
        from .retrieval.faiss_search import FAISSSearchEngine
        return FAISSSearchEngine(index_path="data/vectors/memory_index.bin", dimension=1024)
    
    def _create_association_network(self):
        from .association.network import AssociationNetwork
        return AssociationNetwork(self.component_manager.get_component('db_manager'))
    
    def _create_history_retriever(self):
        from .context.history import HistoryRetriever
        return HistoryRetriever(self.component_manager.get_component('db_manager'))
    
    def _create_smart_retriever(self):
        from .retrieval.smart_retriever import SmartRetriever
        return SmartRetriever(self.component_manager.get_component('db_manager'))
    
    def _create_scorer(self):
        from .scoring.scorer import MemoryScorer
        return MemoryScorer()
    
    def _create_async_evaluator(self):
        from .evaluation.async_evaluator import AsyncMemoryEvaluator
        return AsyncMemoryEvaluator(self.component_manager.get_component('db_manager'))
    
    def _create_memory_search_manager(self):
        return MemorySearchManager(self.component_manager.get_component('db_manager'))
    
    def _create_weight_manager(self):
        return WeightManager(self.component_manager.get_component('db_manager'))
    
    def _create_lifecycle_manager(self):
        return LifecycleManager(
            self.component_manager.get_component('db_manager'),
            self.component_manager.get_component('weight_manager')
        )
    
    def _create_system_stats_manager(self):
        return SystemStatsManager(self.component_manager.get_component('db_manager'))
    
    def _create_user_profiler(self):
        return UserProfiler(self.component_manager.get_component('db_manager'))
    
    def _create_summary_generator(self):
        return SummaryGenerator(self.component_manager.get_component('db_manager'))
    
    def _create_emotion_analyzer(self):
        return EmotionAnalyzer()

def create_estia_memory(enable_advanced: bool = True, context_preset: str = None) -> EstiaMemorySystem:
    """创建Estia记忆系统实例"""
    return EstiaMemorySystem(enable_advanced=enable_advanced, context_preset=context_preset)