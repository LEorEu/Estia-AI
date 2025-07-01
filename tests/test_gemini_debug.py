#!/usr/bin/env python3
"""
详细的Gemini API调试测试脚本
"""

import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dialogue.engine import DialogueEngine
from config import settings

def setup_debug_logging():
    """设置调试日志"""
    # 设置dialogue_engine的日志级别为DEBUG
    logger = logging.getLogger('dialogue_engine')
    logger.setLevel(logging.DEBUG)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def test_gemini_debug():
    """详细测试Gemini API"""
    print("=== Gemini API 详细调试测试 ===")
    
    # 设置调试日志
    setup_debug_logging()
    
    # 检查配置
    print(f"模型提供商: {settings.MODEL_PROVIDER}")
    print(f"Gemini模型: {settings.GEMINI_MODEL}")
    print(f"API Base: {settings.GEMINI_API_BASE}")
    print(f"API Key前缀: {settings.GEMINI_API_KEY[:10]}..." if settings.GEMINI_API_KEY else "未配置")
    print()
    
    if not settings.GEMINI_API_KEY:
        print("❌ 错误：未配置GEMINI_API_KEY")
        return False
    
    # 创建对话引擎
    engine = DialogueEngine()
    
    # 测试会出问题的消息
    problem_message = "请用一句话介绍Python"
    
    print(f"🔍 调试测试: {problem_message}")
    print("=" * 60)
    
    try:
        response = engine._get_llm_response(problem_message, [])
        print(f"✅ 最终回复: {response}")
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
    print("调试测试完成，请查看上方的详细日志")

if __name__ == "__main__":
    test_gemini_debug() 