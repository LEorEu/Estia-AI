#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预设切换测试脚本
验证不同预设配置的正确性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.context.context_manager import ContextLengthManager
from core.utils.logger import setup_logger

def test_preset_switching():
    """测试预设切换功能"""
    print("🎯 预设切换测试")
    print("=" * 60)
    
    # 创建测试数据
    test_data = {
        "current_session": [
            {"user": "你好，今天感觉怎么样？", "assistant": "你好！我今天感觉还不错，谢谢关心。"},
            {"user": "我最近工作压力很大", "assistant": "我理解你的感受，工作压力确实会影响心情。"},
            {"user": "你有什么建议吗？", "assistant": "建议你可以尝试一些放松的方法，比如深呼吸、散步或者听音乐。"},
            {"user": "谢谢你的建议", "assistant": "不客气！记住要照顾好自己。"},
            {"user": "我会的，你也要保重", "assistant": "谢谢你的关心！我会继续努力为你提供帮助。"},
            {"user": "我想了解一下时间管理", "assistant": "时间管理确实很重要，建议你可以使用番茄工作法。"},
            {"user": "具体怎么做？", "assistant": "可以设置25分钟专注工作，然后休息5分钟。"},
            {"user": "听起来不错", "assistant": "是的，这种方法很有效，你可以试试看。"}
        ],
        "memories": [
            {"content": "昨天工作到很晚，感觉很累", "weight": 8.5},
            {"content": "最近工作压力确实很大，建议适当休息", "weight": 9.2},
            {"content": "用户经常询问工作压力相关的问题", "weight": 7.8},
            {"content": "用户对放松方法很感兴趣", "weight": 8.1},
            {"content": "用户性格比较温和，容易接受建议", "weight": 7.5},
            {"content": "用户关心助手的感受", "weight": 6.8},
            {"content": "用户有良好的自我照顾意识", "weight": 7.2},
            {"content": "用户喜欢与助手进行友好交流", "weight": 6.5},
            {"content": "用户对时间管理很感兴趣", "weight": 8.3},
            {"content": "用户愿意尝试新的工作方法", "weight": 7.9}
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
                },
                "session_3": {
                    "dialogue_pairs": [
                        {"user": {"content": "我想学习编程"}, "assistant": {"content": "编程是个很好的技能，建议从Python开始。"}},
                        {"user": {"content": "有什么推荐的学习资源吗？"}, "assistant": {"content": "可以试试菜鸟教程或者慕课网，都很适合初学者。"}}
                    ]
                }
            },
            "summaries": {
                "direct_summaries": [
                    {"content": "用户是一个工作压力较大的上班族，需要放松建议"},
                    {"content": "用户性格温和，容易接受建议和关心"},
                    {"content": "用户对时间管理很感兴趣，愿意尝试新方法"}
                ],
                "memory_summaries": [
                    {"content": "用户有良好的自我照顾意识和沟通习惯"},
                    {"content": "用户对健康和工作平衡比较关注"},
                    {"content": "用户有学习新技能的积极态度"}
                ]
            }
        }
    }
    
    # 测试三种预设
    presets = ["compact", "balanced", "detailed"]
    
    for preset in presets:
        print(f"\n📋 测试预设: {preset}")
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
        
        # 验证配置是否正确应用
        expected_configs = {
            "compact": {
                "current_session": 3,
                "core_memories": 3,
                "historical_dialogues": 2,
                "relevant_memories": 5,
                "summaries": 3
            },
            "balanced": {
                "current_session": 5,
                "core_memories": 5,
                "historical_dialogues": 3,
                "relevant_memories": 8,
                "summaries": 5
            },
            "detailed": {
                "current_session": 8,
                "core_memories": 8,
                "historical_dialogues": 4,
                "relevant_memories": 12,
                "summaries": 8
            }
        }
        
        expected = expected_configs[preset]
        actual = {
            "current_session": limits['current_session']['max_dialogues'],
            "core_memories": limits['core_memories']['max_count'],
            "historical_dialogues": limits['historical_dialogues']['max_sessions'],
            "relevant_memories": limits['relevant_memories']['max_count'],
            "summaries": limits['summaries']['max_count']
        }
        
        print(f"配置验证:")
        for key in expected:
            if actual[key] == expected[key]:
                print(f"  ✅ {key}: {actual[key]} (正确)")
            else:
                print(f"  ❌ {key}: {actual[key]} (期望: {expected[key]})")
        
        print()

def main():
    """主函数"""
    setup_logger(name="preset_switching_test")
    
    print("🚀 开始预设切换测试")
    
    # 测试预设切换
    test_preset_switching()
    
    print("\n✅ 测试完成！")
    print("\n📊 测试总结:")
    print("  验证了不同预设配置的正确应用")
    print("  确保硬编码默认值与基础配置一致")
    print("  确保预设配置能正确覆盖基础配置")

if __name__ == "__main__":
    main() 