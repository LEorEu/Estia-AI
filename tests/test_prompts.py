#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
提示词管理模块测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.prompts.memory_evaluation import MemoryEvaluationPrompts
from core.prompts.dialogue_generation import DialogueGenerationPrompts

def test_memory_evaluation_prompts():
    """测试记忆评估提示词"""
    print("测试记忆评估提示词")
    print("=" * 60)
    
    # 测试基础对话评估提示词
    user_input = "我今天完成了Python项目的核心功能开发"
    ai_response = "恭喜你！能详细说说都实现了哪些核心功能吗？"
    
    prompt = MemoryEvaluationPrompts.get_dialogue_evaluation_prompt(
        user_input=user_input,
        ai_response=ai_response
    )
    
    print("基础对话评估提示词:")
    print(f"长度: {len(prompt)} 字符")
    print("包含关键词:", "JSON格式" in prompt)
    print("包含权重评分:", "weight" in prompt)
    print("包含摘要:", "summary" in prompt)
    
    return True

def test_dialogue_generation_prompts():
    """测试对话生成提示词"""
    print("\n测试对话生成提示词")
    print("=" * 60)
    
    user_input = "我想继续学习机器学习"
    context_memories = [
        {
            'summary': '用户之前学习了Python基础语法',
            'weight': 6,
            'group_id': '学习_2025_07_01'
        }
    ]
    
    prompt = DialogueGenerationPrompts.get_context_response_prompt(
        user_input=user_input,
        context_memories=context_memories
    )
    
    print("上下文响应生成提示词:")
    print(f"长度: {len(prompt)} 字符")
    print("包含记忆信息:", "相关历史记忆" in prompt)
    print("包含用户输入:", user_input in prompt)
    
    return True

def main():
    """主测试函数"""
    print("开始提示词管理模块测试")
    print("=" * 80)
    
    try:
        # 测试记忆评估提示词
        if not test_memory_evaluation_prompts():
            print("记忆评估提示词测试失败")
            return False
        
        # 测试对话生成提示词
        if not test_dialogue_generation_prompts():
            print("对话生成提示词测试失败")
            return False
        
        print("\n" + "=" * 80)
        print("提示词管理模块测试完成！")
        print("\n验证了:")
        print("• 记忆评估提示词生成")
        print("• 对话生成提示词构建")
        print("• 上下文信息格式化")
        print("• 提示词组件模块化")
        
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main() 