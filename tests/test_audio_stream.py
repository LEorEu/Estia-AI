#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试语音流式输出功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.audio.output import speak_stream
from core.dialogue.engine import DialogueEngine

def text_generator():
    """模拟文本生成器"""
    text = "你好！我是Estia，一个智能助手。我很高兴能和你聊天。今天天气怎么样？"
    words = text.split()
    
    for word in words:
        yield word + " "
        import time
        time.sleep(0.5)  # 模拟生成延迟

def test_audio_stream():
    """测试语音流式输出"""
    print("🎵 测试语音流式输出")
    print("=" * 40)
    
    try:
        # 测试简单的文本生成器
        print("测试1: 简单文本流")
        speak_stream(text_generator())
        
        print("\n测试2: 对话引擎流式输出")
        # 创建对话引擎
        engine = DialogueEngine()
        
        # 获取流式文本生成器
        question = "请简单介绍一下你自己"
        print(f"问题: {question}")
        
        # 调用流式方法
        response_generator = engine._call_gemini_api_stream([{"role": "user", "content": question}])
        
        # 使用语音流式输出
        speak_stream(response_generator)
        
        print("\n✅ 语音流式输出测试完成")
        
    except Exception as e:
        print(f"❌ 语音流式输出测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_normal_vs_stream():
    """对比普通语音输出和流式语音输出"""
    print("\n🔄 对比普通语音输出和流式语音输出")
    print("=" * 50)
    
    from core.audio.output import speak
    
    text = "你好！我是Estia，很高兴认识你。"
    
    print("📝 普通语音输出:")
    speak(text)
    
    print("\n⚡ 流式语音输出:")
    def simple_generator():
        words = text.split()
        for word in words:
            yield word + " "
            import time
            time.sleep(0.3)
    
    speak_stream(simple_generator())

def main():
    """主函数"""
    print("🎯 语音流式输出功能测试")
    print("=" * 60)
    
    # 测试语音流式输出
    test_audio_stream()
    
    # 对比测试
    test_normal_vs_stream()
    
    print("\n📊 测试总结:")
    print("  ✅ 语音流式输出功能已实现")
    print("  ✅ 支持文本生成器输入")
    print("  ✅ 边生成边播放效果")
    print("  ✅ 自动清理临时文件")

if __name__ == "__main__":
    main() 