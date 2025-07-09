#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交互管理器 - 处理用户对话的存储和相关逻辑
从 EstiaMemorySystem 中拆分出来的专门组件
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
from ..internal import handle_memory_errors, ErrorHandlerMixin

logger = logging.getLogger(__name__)

class InteractionManager(ErrorHandlerMixin):
    """交互管理器 - 专门处理对话存储逻辑"""
    
    def __init__(self, components: Dict[str, Any]):
        """
        初始化交互管理器
        
        Args:
            components: 所需的组件字典
        """
        super().__init__()
        self.memory_store = components.get('memory_store')
        self.async_evaluator = components.get('async_evaluator')
        self.db_manager = components.get('db_manager')
        
        self.logger = logger
    
    @handle_memory_errors({"user_memory_id": None, "ai_memory_id": None})
    def store_interaction(self, user_input: str, ai_response: str, 
                         context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        存储用户交互对话 (Step 10-12)
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
            context: 上下文信息
            
        Returns:
            Dict: 包含存储结果的字典
        """
        try:
            self.logger.debug("💾 开始存储交互对话")
            
            # 准备会话信息
            session_id = context.get('session_id') if context else None
            timestamp = time.time()
            
            # Step 10: 存储用户输入
            user_memory_id = self._store_user_input(user_input, session_id, timestamp)
            
            # Step 11: 存储AI回复
            ai_memory_id = self._store_ai_response(ai_response, session_id, timestamp)
            
            # Step 12: 记录访问信息
            self._record_access_info(user_memory_id, timestamp, context)
            
            # 触发异步评估
            self._trigger_async_evaluation(user_input, ai_response, context)
            
            result = {
                "user_memory_id": user_memory_id,
                "ai_memory_id": ai_memory_id,
                "session_id": session_id,
                "timestamp": timestamp,
                "status": "success"
            }
            
            self.logger.debug(f"✅ 交互存储完成 (用户: {user_memory_id}, AI: {ai_memory_id})")
            return result
            
        except Exception as e:
            self.logger.error(f"交互存储失败: {e}")
            return {
                "user_memory_id": None,
                "ai_memory_id": None,
                "status": "failed",
                "error": str(e)
            }
    
    def _store_user_input(self, user_input: str, session_id: str, timestamp: float) -> Optional[str]:
        """存储用户输入"""
        if not self.memory_store:
            return None
            
        try:
            user_memory_id = self.memory_store.add_interaction_memory(
                content=user_input,
                memory_type="user_input",
                role="user",
                session_id=session_id,
                timestamp=timestamp,
                metadata={
                    "input_length": len(user_input),
                    "has_question": "?" in user_input,
                    "storage_time": timestamp
                }
            )
            
            self.logger.debug(f"✅ 用户输入存储完成: {user_memory_id}")
            return user_memory_id
            
        except Exception as e:
            self.logger.error(f"用户输入存储失败: {e}")
            return None
    
    def _store_ai_response(self, ai_response: str, session_id: str, timestamp: float) -> Optional[str]:
        """存储AI回复"""
        if not self.memory_store:
            return None
            
        try:
            ai_memory_id = self.memory_store.add_interaction_memory(
                content=ai_response,
                memory_type="assistant_reply",
                role="assistant", 
                session_id=session_id,
                timestamp=timestamp,
                metadata={
                    "response_length": len(ai_response),
                    "has_code": "```" in ai_response,
                    "storage_time": timestamp
                }
            )
            
            self.logger.debug(f"✅ AI回复存储完成: {ai_memory_id}")
            return ai_memory_id
            
        except Exception as e:
            self.logger.error(f"AI回复存储失败: {e}")
            return None
    
    def _record_access_info(self, user_memory_id: str, timestamp: float, context: Dict = None):
        """记录访问信息到统一缓存"""
        try:
            from ...caching.cache_manager import UnifiedCacheManager
            unified_cache = UnifiedCacheManager.get_instance()
            
            if unified_cache and user_memory_id:
                unified_cache.put(f"memory_access_{user_memory_id}", {
                    "memory_id": user_memory_id,
                    "access_time": timestamp,
                    "access_weight": 1.0
                }, {"access_type": "store_interaction"})
                
                self.logger.debug("✅ 访问信息记录完成")
                
        except Exception as e:
            self.logger.debug(f"访问信息记录失败: {e}")
    
    def _trigger_async_evaluation(self, user_input: str, ai_response: str, context: Dict = None):
        """触发异步评估"""
        if not self.async_evaluator:
            return
            
        try:
            # 获取上下文记忆
            context_memories = context.get('context_memories', []) if context else []
            
            # 构建评估上下文
            evaluation_context = self._build_evaluation_context(
                user_input, ai_response, context_memories, context
            )
            
            # 异步评估对话
            self.async_evaluator.queue_dialogue_for_evaluation(
                user_input, ai_response, evaluation_context
            )
            
            self.logger.debug("✅ 异步评估已触发")
            
        except Exception as e:
            self.logger.debug(f"异步评估触发失败: {e}")
    
    def _build_evaluation_context(self, user_input: str, ai_response: str, 
                                 context_memories: list, context: Dict = None) -> Dict[str, Any]:
        """构建评估上下文"""
        evaluation_context = {
            "user_input": user_input,
            "ai_response": ai_response,
            "context_memories_count": len(context_memories),
            "session_id": context.get('session_id') if context else None,
            "timestamp": time.time()
        }
        
        # 添加记忆内容摘要
        if context_memories:
            memory_contents = [m.get('content', '')[:100] for m in context_memories[:3]]
            evaluation_context["memory_summary"] = memory_contents
        
        # 添加对话特征
        evaluation_context.update({
            "input_length": len(user_input),
            "response_length": len(ai_response),
            "has_question": "?" in user_input,
            "has_code": "```" in ai_response,
            "dialogue_complexity": self._assess_complexity(user_input, ai_response)
        })
        
        return evaluation_context
    
    def _assess_complexity(self, user_input: str, ai_response: str) -> str:
        """评估对话复杂度"""
        # 简单的复杂度评估
        if len(user_input) > 200 or len(ai_response) > 500:
            return "high"
        elif len(user_input) > 50 or len(ai_response) > 150:
            return "medium"
        else:
            return "low"