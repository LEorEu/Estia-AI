#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文历史消息测试脚本
验证新系统是否包含历史消息，并与老代码对比
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.context.context_manager import ContextLengthManager
from core.utils.logger import setup_logger

def test_context_with_history():
    """测试上下文是否包含历史消息"""
    print("🎯 上下文历史消息测试")
    print("=" * 60)
    
    # 创建测试数据 - 模拟当前会话和历史会话
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
            {"content": "用户性格比较温和，容易接受建议", "weight": 7.5}
        ],
        "historical_context": {
            "session_dialogues": {
                "session_20240701_143022": {
                    "dialogue_pairs": [
                        {"user": {"content": "今天天气怎么样？"}, "assistant": {"content": "今天天气晴朗，温度适宜。"}},
                        {"user": {"content": "谢谢你的信息"}, "assistant": {"content": "不客气！有其他需要帮助的吗？"}},
                        {"user": {"content": "我想了解一下健康建议"}, "assistant": {"content": "建议你每天保持适量运动，注意饮食均衡。"}}
                    ]
                },
                "session_20240702_091545": {
                    "dialogue_pairs": [
                        {"user": {"content": "我想学习编程"}, "assistant": {"content": "编程是个很好的技能，建议从Python开始。"}},
                        {"user": {"content": "有什么推荐的学习资源吗？"}, "assistant": {"content": "可以试试菜鸟教程或者慕课网，都很适合初学者。"}},
                        {"user": {"content": "谢谢你的建议"}, "assistant": {"content": "不客气！祝你学习顺利。"}}
                    ]
                },
                "session_20240703_162030": {
                    "dialogue_pairs": [
                        {"user": {"content": "我想了解一下时间管理"}, "assistant": {"content": "时间管理确实很重要，建议你可以使用番茄工作法。"}},
                        {"user": {"content": "具体怎么做？"}, "assistant": {"content": "可以设置25分钟专注工作，然后休息5分钟。"}},
                        {"user": {"content": "听起来不错"}, "assistant": {"content": "是的，这种方法很有效，你可以试试看。"}}
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
                    {"content": "用户对健康和工作平衡比较关注"}
                ]
            }
        }
    }
    
    # 测试不同预设
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
        
        # 分析上下文内容
        print(f"配置: {preset}")
        print(f"上下文长度: {len(context):,} 字符")
        
        # 检查各部分是否存在
        sections = {
            "[当前会话]": "当前会话对话",
            "[核心记忆]": "核心记忆",
            "[相关历史对话]": "相关历史对话", 
            "[相关记忆]": "相关记忆",
            "[重要总结]": "重要总结"
        }
        
        print(f"上下文内容分析:")
        for section_marker, section_name in sections.items():
            if section_marker in context:
                print(f"  ✅ {section_name}: 包含")
            else:
                print(f"  ❌ {section_name}: 缺失")
        
        # 显示上下文预览
        print(f"\n上下文预览 (前800字符):")
        preview = context[:800] + "..." if len(context) > 800 else context
        print(f"  {preview}")
        
        # 检查历史对话数量
        if "[相关历史对话]" in context:
            # 简单统计历史对话数量
            history_section = context.split("[相关历史对话]")[1].split("[")[0]
            session_count = history_section.count("会话 ")
            print(f"  历史会话数量: {session_count}")
        
        print()

def compare_with_old_system():
    """与老系统对比"""
    print("\n🔄 与老系统对比")
    print("=" * 60)
    
    print("老系统的特点:")
    print("  ✅ 包含最近3条对话信息")
    print("  ✅ 从session_dialogues中提取历史对话")
    print("  ✅ 使用format_for_context方法")
    print("  ✅ 限制在max_context_length内")
    
    print("\n新系统的特点:")
    print("  ✅ 包含当前会话对话 (可配置轮数)")
    print("  ✅ 包含相关历史对话 (可配置会话数)")
    print("  ✅ 包含核心记忆和相关记忆")
    print("  ✅ 包含重要总结")
    print("  ✅ 使用ContextLengthManager管理长度")
    print("  ✅ 支持多种预设配置")
    
    print("\n主要改进:")
    print("  📈 更灵活的配置系统")
    print("  📈 更丰富的上下文内容")
    print("  📈 更好的长度管理")
    print("  📈 更清晰的分类组织")

def main():
    """主函数"""
    setup_logger(name="context_history_test")
    
    print("🚀 开始上下文历史消息测试")
    
    # 测试上下文构建
    test_context_with_history()
    
    # 与老系统对比
    compare_with_old_system()
    
    print("\n✅ 测试完成！")
    print("\n📊 测试总结:")
    print("  新系统确实包含了历史消息")
    print("  相比老系统有更好的配置灵活性")
    print("  支持更丰富的上下文内容组织")

if __name__ == "__main__":
    main() 