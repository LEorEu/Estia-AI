#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文长度配置演示脚本
展示新的4000、8000、16000字符配置效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.context.context_manager import ContextLengthManager
from core.utils.logger import setup_logger

def demo_context_length_configs():
    """演示不同配置的上下文长度效果"""
    print("🎯 上下文长度配置演示")
    print("=" * 60)
    
    # 创建测试数据
    test_data = {
        "current_session": [
            {"user": "你好，今天感觉怎么样？", "assistant": "你好！我今天感觉还不错，谢谢关心。"},
            {"user": "我最近工作压力很大", "assistant": "我理解你的感受，工作压力确实会影响心情。"},
            {"user": "你有什么建议吗？", "assistant": "建议你可以尝试一些放松的方法，比如深呼吸、散步或者听音乐。"},
            {"user": "谢谢你的建议", "assistant": "不客气！记住要照顾好自己。"},
            {"user": "我会的，你也要保重", "assistant": "谢谢你的关心！我会继续努力为你提供帮助。"}
        ],
        "memories": [
            {"content": "昨天工作到很晚，感觉很累", "weight": 8.5},
            {"content": "最近工作压力确实很大，建议适当休息", "weight": 9.2},
            {"content": "用户经常询问工作压力相关的问题", "weight": 7.8},
            {"content": "用户对放松方法很感兴趣", "weight": 8.1},
            {"content": "用户性格比较温和，容易接受建议", "weight": 7.5},
            {"content": "用户关心助手的感受", "weight": 6.8},
            {"content": "用户有良好的自我照顾意识", "weight": 7.2},
            {"content": "用户喜欢与助手进行友好交流", "weight": 6.5}
        ],
        "historical_context": {
            "session_dialogues": {
                "session_1": {
                    "dialogue_pairs": [
                        {"user": {"content": "今天天气怎么样？"}, "assistant": {"content": "今天天气晴朗，温度适宜。"}},
                        {"user": {"content": "谢谢你的信息"}, "assistant": {"content": "不客气！有其他需要帮助的吗？"}}
                    ]
                },
                "session_2": {
                    "dialogue_pairs": [
                        {"user": {"content": "我想了解一下健康建议"}, "assistant": {"content": "建议你每天保持适量运动，注意饮食均衡。"}},
                        {"user": {"content": "具体应该怎么做？"}, "assistant": {"content": "可以从每天散步30分钟开始，逐渐增加运动量。"}}
                    ]
                }
            },
            "summaries": {
                "direct_summaries": [
                    {"content": "用户是一个工作压力较大的上班族，需要放松建议"},
                    {"content": "用户性格温和，容易接受建议和关心"}
                ],
                "memory_summaries": [
                    {"content": "用户有良好的自我照顾意识和沟通习惯"},
                    {"content": "用户对健康和工作平衡比较关注"}
                ]
            }
        }
    }
    
    # 测试三种预设
    presets = ["compact", "balanced", "detailed"]
    
    for preset in presets:
        print(f"\n📋 预设配置: {preset}")
        print("-" * 40)
        
        # 创建管理器
        manager = ContextLengthManager(preset=preset)
        
        # 构建上下文
        context = manager.build_enhanced_context(
            user_input="我想了解一下如何更好地管理时间",
            memories=test_data["memories"],
            historical_context=test_data["historical_context"],
            current_session_dialogues=test_data["current_session"]
        )
        
        # 显示结果
        print(f"配置: {preset}")
        stats = manager.get_context_stats()
        print(f"最大长度: {stats['max_length']:,} 字符")
        print(f"实际长度: {len(context):,} 字符")
        print(f"使用率: {len(context)/stats['max_length']*100:.1f}%")
        
        # 显示配置详情
        limits = manager.limits
        print(f"配置详情:")
        print(f"  当前会话: 最多{limits['current_session']['max_dialogues']}轮对话")
        print(f"  核心记忆: 最多{limits['core_memories']['max_count']}条")
        print(f"  历史对话: 最多{limits['historical_dialogues']['max_sessions']}个会话")
        print(f"  相关记忆: 最多{limits['relevant_memories']['max_count']}条")
        print(f"  重要总结: 最多{limits['summaries']['max_count']}条")
        
        # 显示上下文预览
        print(f"上下文预览 (前500字符):")
        preview = context[:500] + "..." if len(context) > 500 else context
        print(f"  {preview}")
        
        print()

def demo_adaptive_compression():
    """演示自适应压缩功能"""
    print("\n🔧 自适应压缩演示")
    print("=" * 60)
    
    # 创建超长测试数据
    long_text = "这是一个很长的句子，" * 1000  # 约20000字符
    
    manager = ContextLengthManager(preset="balanced")
    stats = manager.get_context_stats()
    
    print(f"原始长度: {len(long_text):,} 字符")
    print(f"目标长度: {stats['target_length']:,} 字符")
    
    # 压缩文本
    compressed = manager.truncate_text(long_text, stats['target_length'])
    print(f"压缩后长度: {len(compressed):,} 字符")
    print(f"压缩比例: {len(compressed)/len(long_text)*100:.1f}%")
    
    print(f"压缩后预览 (前200字符):")
    print(f"  {compressed[:200]}...")

def main():
    """主函数"""
    setup_logger(name="context_length_demo")
    
    print("🚀 开始上下文长度配置演示")
    
    # 演示不同配置
    demo_context_length_configs()
    
    # 演示自适应压缩
    demo_adaptive_compression()
    
    print("\n✅ 演示完成！")
    print("\n📊 配置总结:")
    print("  compact: 4000字符 - 快速响应，适合简单对话")
    print("  balanced: 8000字符 - 平衡模式，适合日常使用")
    print("  detailed: 16000字符 - 详细模式，适合深度对话")

if __name__ == "__main__":
    main() 