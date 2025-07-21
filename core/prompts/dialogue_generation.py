#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对话生成相关提示词
包含基于记忆的对话生成提示词模板
"""

from typing import Dict, Any, List, Optional

class DialogueGenerationPrompts:
    """对话生成提示词管理类"""
    
    @staticmethod
    def get_context_response_prompt(user_query: str, memory_context: str, 
                                  personality: str = "") -> str:
        """
        获取基于上下文的响应生成提示词
        
        参数:
            user_query: 用户查询
            memory_context: 记忆上下文
            personality: 个性化设定
            
        返回:
            完整的对话生成提示词
        """
        
        # 基础提示词
        base_prompt = f"""你是Estia，一个智能AI助手。请基于以下记忆上下文回复用户。

{DialogueGenerationPrompts._format_context_memories(memory_context)}

用户当前问题：{user_query}

请注意：
1. 优先使用记忆中的相关信息来回答
2. 如果记忆中没有相关信息，可以基于常识回答
3. 保持友好、自然的对话风格
4. 回答要简洁明了，避免过于冗长
5. 如果涉及个人隐私或敏感信息，要谨慎处理

请直接给出回复，不需要解释推理过程："""

        # 如果有个性化设定，添加到提示词开头
        if personality:
            personality_section = DialogueGenerationPrompts._format_personality_info(personality)
            base_prompt = f"{personality_section}\n\n{base_prompt}"
        
        return base_prompt
    
    @staticmethod
    def _format_context_memories(memory_context: str) -> str:
        """格式化记忆上下文"""
        if not memory_context or memory_context.strip() == "":
            return "[记忆上下文]\n暂无相关历史记忆"
        
        return f"[记忆上下文]\n{memory_context}"
    
    @staticmethod
    def _format_personality_info(personality: str) -> str:
        """格式化个性化信息"""
        if not personality:
            return ""
        
        return f"[个性化设定]\n{personality}"
    
    @staticmethod
    def get_simple_response_prompt(user_query: str) -> str:
        """
        获取简单响应提示词（无记忆上下文）
        
        参数:
            user_query: 用户查询
            
        返回:
            简单的对话提示词
        """
        return f"""你是Estia，一个友好的AI助手。请回答用户的问题：

用户问题：{user_query}

请注意：
1. 保持友好、自然的对话风格
2. 回答要简洁明了
3. 如果不确定答案，可以诚实地说不知道
4. 避免提供可能有害或不准确的信息

请直接给出回复："""
    
    @staticmethod
    def get_memory_enhanced_prompt(user_query: str, core_memories: List[Dict], 
                                 related_memories: List[Dict], 
                                 topic_summary: str = "") -> str:
        """
        获取记忆增强的对话提示词
        
        参数:
            user_query: 用户查询
            core_memories: 核心记忆列表
            related_memories: 相关记忆列表
            topic_summary: 话题摘要
            
        返回:
            记忆增强的对话提示词
        """
        
        context_parts = []
        
        # 添加核心记忆
        if core_memories:
            context_parts.append("[重要记忆]")
            for memory in core_memories[:3]:  # 最多3条核心记忆
                summary = memory.get('summary', memory.get('content', ''))[:100]
                weight = memory.get('weight', 0)
                context_parts.append(f"• [{weight}分] {summary}")
            context_parts.append("")
        
        # 添加相关记忆
        if related_memories:
            context_parts.append("[相关记忆]")
            for memory in related_memories[:5]:  # 最多5条相关记忆
                summary = memory.get('summary', memory.get('content', ''))[:80]
                timestamp = memory.get('timestamp', '')
                context_parts.append(f"• {summary}")
            context_parts.append("")
        
        # 添加话题摘要
        if topic_summary:
            context_parts.append(f"[话题摘要]\n{topic_summary}\n")
        
        context_text = "\n".join(context_parts) if context_parts else "[记忆上下文]\n暂无相关历史记忆"
        
        return f"""你是Estia，一个智能AI助手。请基于以下记忆信息回复用户。

{context_text}

用户当前问题：{user_query}

请注意：
1. 优先使用记忆中的信息来回答
2. 结合记忆内容提供个性化的回复
3. 保持友好、自然的对话风格
4. 如果记忆中的信息不足，可以补充常识性回答
5. 避免重复记忆中已有的基础信息

请直接给出回复：""" 