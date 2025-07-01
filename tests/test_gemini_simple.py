#!/usr/bin/env python3
"""
简单的Gemini API测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dialogue.engine import DialogueEngine
from config import settings

def test_gemini_simple():
    """测试Gemini API的基本功能"""
    print("=== Gemini API 简单测试 ===")
    
    # 检查配置
    print(f"模型提供商: {settings.MODEL_PROVIDER}")
    print(f"Gemini模型: {settings.GEMINI_MODEL}")
    print(f"API Base: {settings.GEMINI_API_BASE}")
    print(f"API Key: {'已配置' if settings.GEMINI_API_KEY else '未配置'}")
    print()
    
    if not settings.GEMINI_API_KEY:
        print("❌ 错误：未配置GEMINI_API_KEY")
        return False
    
    # 创建对话引擎
    engine = DialogueEngine()
    
    # 测试简单对话
    test_messages = [
        "你好",
        "1+1等于几？",
        "请用一句话介绍Python"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"测试 {i}: {message}")
        try:
            response = engine._get_llm_response(message, [])
            print(f"回复: {response}")
            print("✅ 成功")
        except Exception as e:
            print(f"❌ 失败: {e}")
        print("-" * 50)
    
    print("测试完成")

if __name__ == "__main__":
    test_gemini_simple() 