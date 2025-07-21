#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对话生成指导原则管理
提供统一的回复指导原则，供各模块使用
"""

from typing import List

class DialogueGenerationPrompts:
    """对话生成指导原则管理类"""
    
    @staticmethod
    def get_response_guidance_text(has_memories: bool = True) -> str:
        """
        获取回复指导原则文本
        
        参数:
            has_memories: 是否有记忆上下文
            
        返回:
            格式化的指导原则文本
        """
        if has_memories:
            # 有记忆情况下的指导
            return """请注意：
1. 优先使用记忆中的相关信息来回答
2. 如果记忆中没有相关信息，可以基于常识回答
3. 保持友好、自然的对话风格
4. 回答要简洁明了，避免过于冗长
5. 如果涉及个人隐私或敏感信息，要谨慎处理"""
        else:
            # 无记忆情况下的指导（简化版）
            return """请注意：
1. 保持友好、自然的对话风格
2. 回答要简洁明了
3. 如果不确定答案，可以诚实地说不知道
4. 避免提供可能有害或不准确的信息"""
    
    @staticmethod
    def get_response_guidance_list(has_memories: bool = True) -> List[str]:
        """
        获取回复指导原则列表（供ContextLengthManager使用）
        
        参数:
            has_memories: 是否有记忆上下文
            
        返回:
            指导原则列表
        """
        if has_memories:
            return [
                "请基于以上记忆和历史对话回复，注意：",
                "1. 优先使用记忆中的相关信息来回答",
                "2. 如果记忆中没有相关信息，可以基于常识回答",
                "3. 保持友好、自然的对话风格",
                "4. 回答要简洁明了，避免过于冗长",
                "5. 如果涉及个人隐私或敏感信息，要谨慎处理",
                "",
                "请直接给出回复："
            ]
        else:
            return [
                "请回答用户的问题，注意：",
                "1. 保持友好、自然的对话风格",
                "2. 回答要简洁明了",
                "3. 如果不确定答案，可以诚实地说不知道",
                "4. 避免提供可能有害或不准确的信息",
                "",
                "请直接给出回复："
            ]
    
    @staticmethod
    def get_guidance_principles() -> dict:
        """
        获取完整的指导原则配置（用于扩展和配置管理）
        
        返回:
            指导原则配置字典
        """
        return {
            "with_memories": {
                "priority_rules": [
                    "优先使用记忆中的相关信息来回答",
                    "如果记忆中没有相关信息，可以基于常识回答"
                ],
                "style_rules": [
                    "保持友好、自然的对话风格",
                    "回答要简洁明了，避免过于冗长"
                ],
                "safety_rules": [
                    "如果涉及个人隐私或敏感信息，要谨慎处理"
                ]
            },
            "without_memories": {
                "style_rules": [
                    "保持友好、自然的对话风格",
                    "回答要简洁明了"
                ],
                "safety_rules": [
                    "如果不确定答案，可以诚实地说不知道",
                    "避免提供可能有害或不准确的信息"
                ]
            }
        }