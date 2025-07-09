#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
上下文构建器 - 处理各种上下文构建逻辑
从 EstiaMemorySystem 中拆分出来的专门组件
"""

import logging
from typing import Dict, Any, List, Optional
from ..internal import handle_memory_errors, ErrorHandlerMixin

logger = logging.getLogger(__name__)

class ContextBuilder(ErrorHandlerMixin):
    """上下文构建器 - 专门处理各种上下文构建逻辑"""
    
    def __init__(self, components: Dict[str, Any]):
        """
        初始化上下文构建器
        
        Args:
            components: 所需的组件字典
        """
        super().__init__()
        self.context_manager = components.get('context_manager')
        self.db_manager = components.get('db_manager')
        
        self.logger = logger
    
    @handle_memory_errors("上下文构建失败")
    def build_enhanced_context(self, user_input: str, memories: List[Dict], 
                              context: Optional[Dict] = None) -> str:
        """
        构建增强上下文
        
        Args:
            user_input: 用户输入
            memories: 相关记忆列表
            context: 额外上下文信息
            
        Returns:
            构建好的上下文字符串
        """
        try:
            if self.context_manager:
                return self.context_manager.build_enhanced_context(user_input, memories, context)
            else:
                return self._build_simple_context(user_input, memories)
                
        except Exception as e:
            self.logger.error(f"增强上下文构建失败: {e}")
            return self._build_fallback_context(user_input)
    
    @handle_memory_errors({})
    def build_evaluation_context(self, user_input: str, ai_response: str,
                               context_memories: List[Dict], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        构建评估上下文
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
            context_memories: 上下文记忆
            context: 额外上下文
            
        Returns:
            评估上下文字典
        """
        import time
        
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
    
    @handle_memory_errors("")
    def build_fallback_context(self, user_input: str) -> str:
        """
        构建降级上下文
        
        Args:
            user_input: 用户输入
            
        Returns:
            降级上下文字符串
        """
        return f"用户问题：{user_input}\n\n注意：记忆系统当前不可用，请基于当前问题回答。"
    
    def _build_simple_context(self, user_input: str, memories: List[Dict]) -> str:
        """构建简单上下文"""
        if not memories:
            return self._build_fallback_context(user_input)
        
        # 提取记忆内容
        memory_texts = []
        for memory in memories[:5]:  # 只取前5条记忆
            content = memory.get('content', '')
            if content:
                memory_texts.append(f"- {content[:200]}")  # 限制长度
        
        context_text = "\n".join(memory_texts)
        return f"相关记忆：\n{context_text}\n\n用户问题：{user_input}"
    
    def _build_fallback_context(self, user_input: str) -> str:
        """构建降级上下文"""
        return f"用户问题：{user_input}\n\n注意：记忆系统当前不可用，请基于当前问题回答。"
    
    def _assess_complexity(self, user_input: str, ai_response: str) -> str:
        """评估对话复杂度"""
        # 简单的复杂度评估
        if len(user_input) > 200 or len(ai_response) > 500:
            return "high"
        elif len(user_input) > 50 or len(ai_response) > 150:
            return "medium"
        else:
            return "low"