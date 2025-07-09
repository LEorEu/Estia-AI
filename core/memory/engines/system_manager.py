#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统管理器 - 处理系统状态、统计和管理功能
从 EstiaMemorySystem 中拆分出来的专门组件
"""

import time
import logging
from typing import Dict, Any, Optional
from ..internal import handle_memory_errors, ErrorHandlerMixin

logger = logging.getLogger(__name__)

class SystemManager(ErrorHandlerMixin):
    """系统管理器 - 专门处理系统状态和管理功能"""
    
    def __init__(self, components: Dict[str, Any]):
        """
        初始化系统管理器
        
        Args:
            components: 所需的组件字典
        """
        super().__init__()
        self.system_stats_manager = components.get('system_stats_manager')
        self.memory_search_manager = components.get('memory_search_manager')
        self.weight_manager = components.get('weight_manager')
        self.lifecycle_manager = components.get('lifecycle_manager')
        self.user_profiler = components.get('user_profiler')
        self.emotion_analyzer = components.get('emotion_analyzer')
        self.async_evaluator = components.get('async_evaluator')
        
        # 记录所有组件状态
        self.all_components = components
        
        self.logger = logger
    
    @handle_memory_errors({})
    def get_system_stats(self) -> Dict[str, Any]:
        """
        获取系统统计信息
        
        Returns:
            系统统计信息字典
        """
        if self.system_stats_manager:
            return self.system_stats_manager.get_system_stats(self.all_components)
        else:
            return self._get_basic_stats()
    
    @handle_memory_errors({})
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        获取性能统计信息
        
        Returns:
            性能统计信息字典
        """
        if self.system_stats_manager:
            return self.system_stats_manager.get_performance_statistics()
        else:
            return {"error": "系统统计管理器未初始化"}
    
    @handle_memory_errors([])
    def get_memory_search_tools(self) -> list:
        """
        获取记忆搜索工具列表
        
        Returns:
            搜索工具列表
        """
        if self.memory_search_manager:
            return self.memory_search_manager.get_search_tools()
        else:
            return []
    
    @handle_memory_errors({})
    def execute_memory_search_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        执行记忆搜索工具
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            搜索结果
        """
        if self.memory_search_manager:
            return self.memory_search_manager.execute_search_tool(tool_name, **kwargs)
        else:
            return {"error": "记忆搜索管理器未初始化"}
    
    @handle_memory_errors({})
    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """
        分析文本情感
        
        Args:
            text: 要分析的文本
            
        Returns:
            情感分析结果
        """
        if self.emotion_analyzer:
            return self.emotion_analyzer.analyze_emotion(text)
        else:
            return {"error": "情感分析器未初始化"}
    
    @handle_memory_errors({})
    def get_user_profile(self, user_id: str = None) -> Dict[str, Any]:
        """
        获取用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户画像信息
        """
        if self.user_profiler:
            return self.user_profiler.get_user_profile(user_id)
        else:
            return {"error": "用户画像器未初始化"}
    
    @handle_memory_errors({})
    def update_memory_weight_dynamically(self, memory_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        动态更新记忆权重
        
        Args:
            memory_id: 记忆ID
            context: 上下文信息
            
        Returns:
            更新结果
        """
        if self.weight_manager:
            return self.weight_manager.update_memory_weight_dynamically(memory_id, context)
        else:
            return {"error": "权重管理器未初始化"}
    
    @handle_memory_errors({})
    def archive_old_memories(self, days_threshold: int = 30) -> Dict[str, Any]:
        """
        归档旧记忆
        
        Args:
            days_threshold: 天数阈值
            
        Returns:
            归档结果
        """
        if self.lifecycle_manager:
            return self.lifecycle_manager.archive_old_memories(days_threshold)
        else:
            return {"error": "生命周期管理器未初始化"}
    
    def ensure_async_initialized(self) -> bool:
        """
        确保异步组件已初始化
        
        Returns:
            是否初始化成功
        """
        if not self.async_evaluator:
            return False
            
        try:
            from ...evaluator.async_startup_manager import initialize_async_evaluator_safely
            return initialize_async_evaluator_safely(self.async_evaluator)
        except Exception as e:
            self.logger.error(f"异步组件初始化失败: {e}")
            return False
    
    def _get_basic_stats(self) -> Dict[str, Any]:
        """获取基础统计信息"""
        return {
            'system_status': {
                'initialized': True,
                'timestamp': time.time()
            },
            'components': {
                'memory_search_manager': self.memory_search_manager is not None,
                'weight_manager': self.weight_manager is not None,
                'lifecycle_manager': self.lifecycle_manager is not None,
                'user_profiler': self.user_profiler is not None,
                'emotion_analyzer': self.emotion_analyzer is not None,
                'async_evaluator': self.async_evaluator is not None
            }
        }