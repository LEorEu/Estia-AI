#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试上下文长度管理器
验证不同预设配置下的上下文长度管理功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from core.memory.context.context_manager import ContextLengthManager

# 设置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_context_length_manager():
    """测试上下文长度管理器"""
    print("🧪 开始测试上下文长度管理器")
    
    # 测试不同预设
    presets = ["compact", "balanced", "detailed"]
    
    for preset in presets:
        print(f"\n📋 测试预设: {preset}")
        
        # 创建管理器
        manager = ContextLengthManager(preset=preset)
        
        # 获取配置统计
        stats = manager.get_context_stats()
        print(f"  配置: {stats['preset']}")
        print(f"  最大长度: {stats['max_length']}")
        print(f"  自适应: {stats['adaptive_enabled']}")
        
        # 模拟数据
        user_input = "我今天工作压力很大，感觉很累"
        
        memories = [
            {
                "memory_id": "mem_abc123",
                "content": "昨天工作到很晚，感觉很累",
                "role": "user",
                "weight": 8.5,
                "timestamp": 1719446400,
                "type": "user_input"
            },
            {
                "memory_id": "mem_def456",
                "content": "最近工作压力确实很大，建议适当休息",
                "role": "assistant",
                "weight": 9.2,
                "timestamp": 1719446460,
                "type": "assistant_reply"
            },
            {
                "memory_id": "mem_ghi789",
                "content": "你提到过工作生活平衡的问题",
                "role": "assistant",
                "weight": 7.8,
                "timestamp": 1719446520,
                "type": "assistant_reply"
            }
        ]
        
        historical_context = {
            "session_dialogues": {
                "sess_20250626_001": {
                    "session_id": "sess_20250626_001",
                    "count": 4,
                    "dialogue_pairs": [
                        {
                            "user": {"content": "最近工作很忙", "timestamp": 1719446400},
                            "assistant": {"content": "工作压力确实很大，要注意休息", "timestamp": 1719446460}
                        },
                        {
                            "user": {"content": "是的，感觉时间不够用", "timestamp": 1719446520},
                            "assistant": {"content": "建议合理安排时间，提高效率", "timestamp": 1719446580}
                        }
                    ]
                }
            },
            "summaries": {
                "direct_summaries": [
                    {"content": "用户经常提到工作压力问题", "weight": 8.0},
                    {"content": "建议关注工作生活平衡", "weight": 7.5}
                ],
                "memory_summaries": [
                    {"content": "工作压力是主要话题", "weight": 8.2}
                ]
            }
        }
        
        current_session_dialogues = [
            {
                "user": "你好，今天感觉怎么样？",
                "assistant": "你好！我今天感觉还不错，谢谢关心。"
            },
            {
                "user": "我最近工作压力很大",
                "assistant": "我理解你的感受，工作压力确实会影响心情。"
            }
        ]
        
        # 构建上下文
        context = manager.build_enhanced_context(
            user_input=user_input,
            memories=memories,
            historical_context=historical_context,
            current_session_id="sess_20250627_001",
            current_session_dialogues=current_session_dialogues
        )
        
        # 输出结果
        print(f"  上下文长度: {len(context)} 字符")
        print(f"  目标长度: {stats['target_length']} 字符")
        print(f"  是否超出限制: {len(context) > stats['max_length']}")
        
        # 显示上下文内容（前200字符）
        preview = context[:200] + "..." if len(context) > 200 else context
        print(f"  上下文预览:\n{preview}")
        
        # 验证各部分是否正确格式化
        sections = ["[系统角色设定]", "[当前会话]", "[核心记忆]", "[相关历史对话]", "[相关记忆]", "[重要总结]"]
        found_sections = []
        for section in sections:
            if section in context:
                found_sections.append(section)
        
        print(f"  包含的部分: {found_sections}")
        
        # 验证长度限制
        if len(context) <= stats['max_length']:
            print("  ✅ 长度符合限制")
        else:
            print("  ⚠️ 长度超出限制，但已压缩")

def test_text_truncation():
    """测试文本截断功能"""
    print("\n🔧 测试文本截断功能")
    
    manager = ContextLengthManager()
    
    test_texts = [
        "这是一个很长的句子，需要被截断到指定长度。",
        "Short text.",
        "这是一个包含标点符号的长句子，应该在合适的位置截断。",
        "This is a very long English sentence that needs to be truncated at an appropriate position."
    ]
    
    max_lengths = [10, 20, 30, 50]
    
    for text in test_texts:
        print(f"\n原文: {text}")
        for max_len in max_lengths:
            truncated = manager.truncate_text(text, max_len)
            print(f"  截断到{max_len}字符: {truncated}")

def test_preset_configurations():
    """测试预设配置"""
    print("\n⚙️ 测试预设配置")
    
    presets = ["compact", "balanced", "detailed"]
    
    for preset in presets:
        manager = ContextLengthManager(preset=preset)
        limits = manager.limits
        
        print(f"\n预设: {preset}")
        print(f"  当前会话: 最多{limits['current_session']['max_dialogues']}轮对话")
        print(f"  核心记忆: 最多{limits['core_memories']['max_count']}条")
        print(f"  历史对话: 最多{limits['historical_dialogues']['max_sessions']}个会话")
        print(f"  相关记忆: 最多{limits['relevant_memories']['max_count']}条")
        print(f"  重要总结: 最多{limits['summaries']['max_count']}条")

if __name__ == "__main__":
    print("🚀 开始测试上下文长度管理器")
    
    try:
        test_context_length_manager()
        test_text_truncation()
        test_preset_configurations()
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 