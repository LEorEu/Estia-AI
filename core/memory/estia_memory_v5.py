#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia记忆系统主接口 v5.0.0 - 六大模块架构版本
简化版本，基于已迁移的成熟组件
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# 导入六大核心管理器
from .managers.sync_flow import SyncFlowManager
from .managers.async_flow import AsyncFlowManager

logger = logging.getLogger(__name__)

class EstiaMemorySystem:
    """
    Estia记忆系统主接口 v5.0.0 - 简化架构版本
    基于已迁移的成熟组件
    """
    
    def __init__(self, enable_advanced: bool = True, context_preset: str = None):
        """
        初始化Estia记忆系统 v5.0.0
        
        Args:
            enable_advanced: 是否启用高级功能
            context_preset: 上下文长度预设
        """
        self.logger = logger
        
        # 系统状态
        self.enable_advanced = enable_advanced
        self.initialized = False
        self.context_preset = context_preset or "balanced"
        
        # 会话管理
        self.current_session_id: Optional[str] = None
        self.session_start_time: Optional[float] = None
        self.session_timeout = 3600  # 1小时
        
        # 核心管理器
        self.sync_flow_manager = None
        self.async_flow_manager = None
        
        # 初始化系统
        self._initialize_system()
    
    def _initialize_system(self):
        """初始化系统组件"""
        try:
            self.logger.info("🚀 开始初始化Estia记忆系统 v5.0.0")
            
            # 初始化核心组件
            components = self._initialize_components()
            
            # 初始化管理器
            if components.get('db_manager'):
                self.sync_flow_manager = SyncFlowManager(components)
                self.async_flow_manager = AsyncFlowManager(components)
                self.initialized = True
                self.logger.info("✅ Estia记忆系统 v5.0.0 初始化完成")
            else:
                self.logger.error("❌ 数据库初始化失败，系统无法启动")
                
        except Exception as e:
            self.logger.error(f"系统初始化失败: {e}")
            self.initialized = False
    
    def _initialize_components(self) -> Dict[str, Any]:
        """初始化核心组件"""
        components = {}
        
        try:
            # 🔥 初始化数据库管理器
            from .managers.sync_flow.init.db_manager import DatabaseManager
            db_manager = DatabaseManager()
            if db_manager.connect():
                db_manager.initialize_database()
                components['db_manager'] = db_manager
                self.logger.info("✅ 数据库管理器初始化成功")
            
            # 🔥 初始化统一缓存管理器
            from .shared.caching.cache_manager import UnifiedCacheManager
            unified_cache = UnifiedCacheManager.get_instance()
            self.unified_cache = unified_cache  # 保存到实例变量
            components['unified_cache'] = unified_cache
            self.logger.info("✅ 统一缓存管理器初始化成功")
            
            # 🔥 基础向量化器（始终初始化）
            from .shared.embedding.vectorizer import TextVectorizer
            from .shared.embedding.simple_vectorizer import SimpleVectorizer
            
            # 设置离线模式环境变量，使用本地缓存
            import os
            project_cache = os.path.join(os.path.dirname(__file__), "..", "..", "cache")
            os.environ['HF_HUB_OFFLINE'] = '1'
            os.environ['TRANSFORMERS_OFFLINE'] = '1'
            os.environ['HUGGINGFACE_HUB_CACHE'] = project_cache
            os.environ['SENTENCE_TRANSFORMERS_HOME'] = project_cache
            os.environ['HF_HOME'] = project_cache
            
            # 尝试使用本地缓存的模型，失败时回退到简化版本
            vectorizer = None
            vector_dim = 384
            
            try:
                # 尝试使用本地缓存的模型
                vectorizer = TextVectorizer(
                    model_type="sentence-transformers",
                    model_name="Qwen/Qwen3-Embedding-0.6B",
                    use_cache=True,
                    device="cpu",
                    cache_dir=project_cache
                )
                vector_dim = vectorizer.vector_dim
                self.logger.info("✅ 使用TextVectorizer（all-MiniLM-L6-v2）")
                
            except Exception as e:
                self.logger.warning(f"TextVectorizer初始化失败: {e}")
                self.logger.info("🔄 回退到SimpleVectorizer")
                
                # 回退到简化版本
                vectorizer = SimpleVectorizer(
                    dimension=1024,  # 🔥 修复：使用1024维度与Qwen模型保持一致
                    use_cache=True
                )
                vector_dim = vectorizer.vector_dim
                self.logger.info("✅ 使用SimpleVectorizer（测试版本）")
            
            components['vectorizer'] = vectorizer
            
            # 🔥 基础记忆存储器（如果有数据库管理器）
            if components.get('db_manager'):
                try:
                    from .managers.sync_flow.storage.memory_store import MemoryStore
                    memory_store = MemoryStore(db_manager)
                    components['memory_store'] = memory_store
                    self.logger.info("✅ 基础记忆存储器初始化成功")
                except Exception as e:
                    self.logger.warning(f"基础记忆存储器初始化失败: {e}")
            
            # 🔥 可选高级组件
            if self.enable_advanced and components.get('db_manager'):
                try:
                    # 确保UnifiedCacheManager可用
                    unified_cache = components.get('unified_cache')
                    if not unified_cache:
                        unified_cache = UnifiedCacheManager.get_instance()
                    # 智能检索器
                    from .managers.sync_flow.retrieval.smart_retriever import SmartRetriever
                    smart_retriever = SmartRetriever(db_manager)
                    components['smart_retriever'] = smart_retriever
                    self.logger.info("✅ 智能检索器初始化成功")
                    
                    # FAISS搜索（使用已初始化的向量化器）
                    from .managers.sync_flow.retrieval.faiss_search import FAISSSearchEngine
                    
                    faiss_retriever = FAISSSearchEngine(
                        index_path="data/vectors/memory_index.bin",
                        dimension=vector_dim  # 使用已初始化的向量维度
                    )
                    components['faiss_retriever'] = faiss_retriever
                    self.logger.info("✅ 高级检索组件初始化成功")
                    
                    # === 文档标准的核心组件初始化 ===
                    
                    # 关联网络 (Step 6 核心组件)
                    from .managers.async_flow.association.network import AssociationNetwork
                    association_network = AssociationNetwork(db_manager)
                    components['association_network'] = association_network
                    self.logger.info("✅ 关联网络初始化成功 (文档Step 6)")
                    
                    # 历史检索器 (Step 7 核心组件)
                    from .managers.sync_flow.context.history import HistoryRetriever
                    history_retriever = HistoryRetriever(db_manager)
                    components['history_retriever'] = history_retriever
                    self.logger.info("✅ 历史检索器初始化成功 (文档Step 7)")
                    
                    # 记忆评分器 (Step 8 核心组件)
                    from .managers.sync_flow.ranking.scorer import MemoryScorer
                    scorer = MemoryScorer()
                    components['scorer'] = scorer
                    self.logger.info("✅ 记忆评分器初始化成功 (文档Step 8)")
                    
                except Exception as e:
                    self.logger.warning(f"高级组件初始化失败: {e}")
                    # 确保UnifiedCacheManager在异常处理中可用
                    try:
                        from .shared.caching.cache_manager import UnifiedCacheManager
                    except:
                        pass
            
        except Exception as e:
            self.logger.error(f"组件初始化失败: {e}")
        
        return components
    
    # === 核心API方法 ===
    
    def enhance_query(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        执行查询增强 - 委托给同步流程管理器
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            str: 增强后的上下文
        """
        if not self.initialized or not self.sync_flow_manager:
            self.logger.warning("系统未正确初始化，返回原始输入")
            return user_input
        
        try:
            context = self._prepare_context(context)
            
            # 委托给同步流程管理器
            result = self.sync_flow_manager.execute_sync_flow(user_input, context)
            
            enhanced_context = result.get('enhanced_context', user_input)
            self.logger.debug(f"查询增强完成: {len(enhanced_context)} 字符")
            
            return enhanced_context
            
        except Exception as e:
            self.logger.error(f"查询增强失败: {e}")
            return user_input
    
    def store_interaction(self, user_input: str, ai_response: str, 
                         context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        存储交互对话
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
            context: 上下文信息
            
        Returns:
            Dict: 存储结果
        """
        if not self.initialized or not self.sync_flow_manager:
            return {'error': '系统未正确初始化'}
        
        try:
            context = self._prepare_context(context)
            
            # 同步存储
            sync_result = self.sync_flow_manager.store_interaction_sync(user_input, ai_response, context)
            
            # 🔥 触发异步评估（如果可用）
            if self.async_flow_manager:
                try:
                    # 检查是否有运行的事件循环
                    try:
                        import asyncio
                        loop = asyncio.get_running_loop()
                        # 如果有事件循环，创建任务
                        asyncio.create_task(
                            self.async_flow_manager.trigger_async_evaluation(
                                user_input, ai_response, sync_result, context
                            )
                        )
                    except RuntimeError:
                        # 没有运行的事件循环，使用线程池执行
                        import threading
                        
                        def run_async_evaluation():
                            try:
                                asyncio.run(
                                    self.async_flow_manager.trigger_async_evaluation(
                                        user_input, ai_response, sync_result, context
                                    )
                                )
                            except Exception as e:
                                self.logger.warning(f"异步评估执行失败: {e}")
                        
                        # 在后台线程中运行
                        thread = threading.Thread(target=run_async_evaluation, daemon=True)
                        thread.start()
                        
                except Exception as async_error:
                    self.logger.warning(f"异步评估触发失败: {async_error}")
                    # 异步评估失败不影响主流程
            
            return sync_result
            
        except Exception as e:
            self.logger.error(f"交互存储失败: {e}")
            return {'error': str(e)}
    
    # === 缓存统计和监控API ===
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 缓存统计数据
        """
        try:
            # 获取统一缓存管理器
            from .shared.caching.cache_manager import UnifiedCacheManager
            unified_cache = UnifiedCacheManager.get_instance()
            self.unified_cache = unified_cache  # 保存到实例变量
            
            # 获取缓存统计
            stats = unified_cache.get_stats()
            
            # 添加记忆访问统计
            memory_access_stats = self._get_memory_access_stats(unified_cache)
            stats.update(memory_access_stats)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取缓存统计失败: {e}")
            return {'error': str(e)}
    
    def _get_memory_access_stats(self, unified_cache) -> Dict[str, Any]:
        """获取记忆访问统计"""
        try:
            # 获取缓存的记忆访问记录
            cached_memories = unified_cache.get_cached_memories()
            
            access_stats = {
                'total_memory_accesses': len(cached_memories),
                'recent_accessed_memories': cached_memories[:10],  # 最近访问的10条记忆
                'cache_performance': {
                    'hit_ratio': unified_cache.stats.get_hit_ratio(),
                    'total_hits': unified_cache.stats.total_hits,
                    'total_misses': unified_cache.stats.total_misses,
                    'average_access_time_ms': unified_cache.stats.get_average_access_time()
                }
            }
            
            return access_stats
            
        except Exception as e:
            self.logger.error(f"获取记忆访问统计失败: {e}")
            return {}
    
    def clear_cache(self) -> Dict[str, Any]:
        """
        清理缓存
        
        Returns:
            Dict: 清理结果
        """
        try:
            # 获取统一缓存管理器
            from .shared.caching.cache_manager import UnifiedCacheManager
            unified_cache = UnifiedCacheManager.get_instance()
            self.unified_cache = unified_cache  # 保存到实例变量
            
            # 清理缓存
            unified_cache.clear_all()
            
            self.logger.info("✅ 缓存清理完成")
            
            return {
                'success': True,
                'message': '缓存清理完成'
            }
            
        except Exception as e:
            self.logger.error(f"缓存清理失败: {e}")
            return {'error': str(e)}
    
    # === 原有的LLM搜索工具API ===
    
    def get_memory_search_tools(self):
        """获取LLM可用的记忆搜索工具"""
        if not self.async_flow_manager:
            return []
        
        return self.async_flow_manager.get_memory_search_tools()
    
    def execute_memory_search_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行记忆搜索工具（供LLM调用）"""
        if not self.async_flow_manager:
            return {
                'success': False,
                'message': '异步流程管理器未初始化',
                'memories': []
            }
        
        return self.async_flow_manager.execute_memory_search_tool(tool_name, parameters)
    
    # === 系统状态API ===
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计"""
        return {
            'initialized': self.initialized,
            'enable_advanced': self.enable_advanced,
            'context_preset': self.context_preset,
            'sync_manager_available': self.sync_flow_manager is not None,
            'async_manager_available': self.async_flow_manager is not None,
            'current_session': self.current_session_id or 'none'
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if not self.sync_flow_manager:
            return {}
        
        return self.sync_flow_manager.get_processing_time()
    
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
        
        return self.current_session_id or "default_session"
    
    def start_new_session(self, session_id: str = None) -> str:
        """开始新会话"""
        current_time = time.time()
        
        if session_id:
            self.current_session_id = session_id
        else:
            timestamp_str = datetime.fromtimestamp(current_time).strftime('%Y%m%d_%H%M%S')
            self.current_session_id = f"sess_{timestamp_str}"
        
        self.session_start_time = current_time
        self.logger.info(f"🆕 开始新会话: {self.current_session_id}")
        return self.current_session_id

def create_estia_memory(enable_advanced: bool = True, context_preset: str = None) -> EstiaMemorySystem:
    """创建Estia记忆系统实例"""
    return EstiaMemorySystem(enable_advanced=enable_advanced, context_preset=context_preset)