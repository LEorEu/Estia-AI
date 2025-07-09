#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的语音流式输出测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.audio.output import speak_stream
import time

def simple_text_generator():
    """简单的文本生成器"""
    text = "你好！我是Estia。"
    words = text.split()
    
    for word in words:
        yield word + " "
        time.sleep(0.5)  # 模拟延迟

def test_simple_stream():
    """测试简单的语音流式输出"""
    print("🎵 简单语音流式输出测试")
    print("=" * 40)
    
    try:
        print("开始测试...")
        speak_stream(simple_text_generator())
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_stream() 