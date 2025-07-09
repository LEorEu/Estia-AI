#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia记忆系统主接口 v5.0.0 - 六大模块架构版本
真正的模块化设计：六大核心管理器统一协调
主文件代码量控制在200行以内
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# 导入六大核心管理器
from .managers import (
    SyncFlowManager,
    AsyncFlowManager,
    MemoryFlowMonitor,
    LifecycleManager,
    ConfigManager,
    ErrorRecoveryManager
)

# 导入内部工具
from .internal.component_manager import ComponentManager
from .internal import handle_memory_errors, ErrorHandlerMixin

logger = logging.getLogger(__name__)

class EstiaMemorySystem(ErrorHandlerMixin):
    """
    Estia记忆系统主接口 v5.0.0 - 六大模块架构
    真正的轻量级协调器，所有功能委托给六大管理器
    """
    
    def __init__(self, enable_advanced: bool = True, context_preset: str = None):
        """
        初始化Estia记忆系统 v5.0.0
        
        Args:
            enable_advanced: 是否启用高级功能
            context_preset: 上下文长度预设
        """
        super().__init__()
        self.logger = logger
        
        # 系统状态
        self.enable_advanced = enable_advanced
        self.initialized = False
        self.context_preset = context_preset
        
        # 会话管理
        self.current_session_id = None
        self.session_start_time = None
        self.session_timeout = 3600  # 1小时
        
        # 组件管理器
        self.component_manager = ComponentManager()
        
        # 六大核心管理器
        self.config_manager = None
        self.sync_flow_manager = None
        self.async_flow_manager = None
        self.monitor_flow_manager = None
        self.lifecycle_manager = None
        self.recovery_manager = None
        
        # 初始化系统
        self._initialize_system()
    
    def _initialize_system(self):
        """初始化系统组件"""
        try:
            self.logger.info("🚀 开始初始化Estia记忆系统 v5.0.0")
            
            # 1. 初始化配置管理器
            self.config_manager = ConfigManager()
            
            # 2. 初始化基础组件
            self._initialize_core_components()
            
            # 3. 初始化六大管理器
            self._initialize_managers()
            
            # 4. 启动异步组件
            self._start_async_components()
            
            self.initialized = True
            self.logger.info("✅ Estia记忆系统 v5.0.0 初始化完成")
            
        except Exception as e:
            self.logger.error(f"系统初始化失败: {e}")
            raise
    
    def _initialize_core_components(self):
        """初始化核心组件"""
        # 使用ComponentManager管理所有组件
        components = {
            'db_manager': self.component_manager.get_component('db_manager'),
            'vectorizer': self.component_manager.get_component('vectorizer'),
            'faiss_retriever': self.component_manager.get_component('faiss_retriever'),
            'association_network': self.component_manager.get_component('association_network'),
            'history_retriever': self.component_manager.get_component('history_retriever'),
            'memory_store': self.component_manager.get_component('memory_store'),
            'scorer': self.component_manager.get_component('scorer'),
            'async_evaluator': self.component_manager.get_component('async_evaluator'),
            'weight_manager': self.component_manager.get_component('weight_manager'),
            'unified_cache': self.component_manager.get_component('unified_cache'),
        }
        
        self.components = components
    
    def _initialize_managers(self):
        """初始化六大管理器"""
        # 同步流程管理器
        self.sync_flow_manager = SyncFlowManager(self.components)
        
        # 异步流程管理器
        self.async_flow_manager = AsyncFlowManager(self.components)
        
        # 监控流程管理器
        monitor_components = self.components.copy()
        monitor_components.update({
            'sync_flow_manager': self.sync_flow_manager,
            'async_flow_manager': self.async_flow_manager
        })
        self.monitor_flow_manager = MemoryFlowMonitor(monitor_components)
        
        # 生命周期管理器
        self.lifecycle_manager = LifecycleManager(self.components, self.config_manager)
        
        # 错误恢复管理器
        recovery_components = self.components.copy()
        recovery_components.update({
            'sync_flow_manager': self.sync_flow_manager,
            'async_flow_manager': self.async_flow_manager,
            'monitor_flow_manager': self.monitor_flow_manager,
            'lifecycle_manager': self.lifecycle_manager
        })
        self.recovery_manager = ErrorRecoveryManager(recovery_components)
    
    def _start_async_components(self):
        """启动异步组件"""
        try:
            import asyncio
            
            # 检查是否有运行的事件循环
            try:
                loop = asyncio.get_running_loop()
                if loop:
                    asyncio.create_task(self._async_startup())
            except RuntimeError:
                # 没有事件循环，稍后启动
                pass
                
        except Exception as e:
            self.logger.warning(f"异步组件启动失败: {e}")
    
    async def _async_startup(self):
        """异步启动流程"""
        try:
            # 启动异步流程管理器
            await self.async_flow_manager.start_async_processing()
            
            # 启动生命周期管理器
            await self.lifecycle_manager.start_lifecycle_management()
            
            # 启动错误恢复监控
            await self.recovery_manager.start_monitoring()
            
            self.logger.info("✅ 异步组件启动完成")
            
        except Exception as e:
            self.logger.error(f"异步启动失败: {e}")
    
    # === 核心API方法 ===
    
    @handle_memory_errors("查询增强失败")
    def enhance_query(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        执行查询增强 - 委托给同步流程管理器
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            str: 增强后的上下文
        """
        context = self._prepare_context(context)
        
        # 委托给同步流程管理器
        result = self.sync_flow_manager.execute_sync_flow(user_input, context)
        
        return result.get('enhanced_context', user_input)
    
    @handle_memory_errors({'user_memory_id': None, 'ai_memory_id': None})
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
        context = self._prepare_context(context)
        
        # 同步存储
        sync_result = self.sync_flow_manager.store_interaction_sync(user_input, ai_response, context)
        
        # 触发异步评估
        if self.async_flow_manager:
            import asyncio
            try:
                asyncio.create_task(
                    self.async_flow_manager.trigger_async_evaluation(
                        user_input, ai_response, sync_result, context
                    )
                )
            except RuntimeError:
                # 没有事件循环，跳过异步评估
                pass
        
        return sync_result
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计 - 委托给监控流程管理器"""
        return self.monitor_flow_manager.get_comprehensive_stats()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计 - 委托给监控流程管理器"""
        return self.monitor_flow_manager.get_real_time_metrics()
    
    def get_13_step_monitoring(self) -> Dict[str, Any]:
        """获取13步流程监控"""
        return self.monitor_flow_manager.get_13_step_monitoring()
    
    def get_lifecycle_stats(self) -> Dict[str, Any]:
        """获取生命周期统计"""
        return self.lifecycle_manager.get_lifecycle_stats()
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """获取恢复统计"""
        return self.recovery_manager.get_recovery_stats()
    
    # === 配置管理 ===
    
    def get_config(self, key_path: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config_manager.get_config(key_path, default)
    
    def set_config(self, key_path: str, value: Any) -> bool:
        """设置配置值"""
        return self.config_manager.set_config(key_path, value)
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        return self.config_manager.validate_config()
    
    # === 生命周期管理 ===
    
    async def cleanup_old_memories(self, days_threshold: int = 90) -> Dict[str, Any]:
        """清理过期记忆"""
        return await self.lifecycle_manager.cleanup_old_memories(days_threshold)
    
    async def archive_old_memories(self, days_threshold: int = 30) -> Dict[str, Any]:
        """归档旧记忆"""
        return await self.lifecycle_manager.archive_old_memories(days_threshold)
    
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
        self.logger.info(f"🆕 开始新会话: {self.current_session_id}")
        return self.current_session_id

def create_estia_memory(enable_advanced: bool = True, context_preset: str = None) -> EstiaMemorySystem:
    """创建Estia记忆系统实例"""
    return EstiaMemorySystem(enable_advanced=enable_advanced, context_preset=context_preset)