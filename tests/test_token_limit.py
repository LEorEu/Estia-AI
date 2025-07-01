#!/usr/bin/env python3
"""
Token限制测试和配置验证
"""

import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dialogue.engine import DialogueEngine
from config import settings

def setup_debug_logging():
    """设置调试日志"""
    logger = logging.getLogger('dialogue_engine')
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def test_token_configuration():
    """测试token配置"""
    print("=== Token配置验证 ===")
    print(f"settings.LLM_MAX_NEW_TOKENS: {settings.LLM_MAX_NEW_TOKENS}")
    print(f"getattr(settings, 'LLM_MAX_NEW_TOKENS', 2048): {getattr(settings, 'LLM_MAX_NEW_TOKENS', 2048)}")
    print()
    
    # 设置调试日志
    setup_debug_logging()
    
    engine = DialogueEngine()
    
    # 测试一个可能触发token限制的问题
    long_question = "请详细介绍Python编程语言的历史、特点、应用领域、语法特性、生态系统、学习路径、职业前景，以及与其他编程语言的对比分析。"
    
    print(f"🔍 测试长问题: {long_question}")
    print("=" * 80)
    
    try:
        response = engine._get_llm_response(long_question, [])
        print(f"✅ 回复: {response}")
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 80)
    print("测试完成")

if __name__ == "__main__":
    test_token_configuration() 