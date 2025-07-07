#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
上下文长度管理演示
展示如何使用不同的预设配置来管理记忆系统的上下文长度
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from core.memory.estia_memory import create_estia_memory

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_different_presets():
    """演示不同预设的效果"""
    print("🎯 上下文长度管理演示")
    print("=" * 50)
    
    # 测试不同的预设
    presets = ["compact", "balanced", "detailed"]
    
    for preset in presets:
        print(f"\n📋 使用预设: {preset}")
        print("-" * 30)
        
        # 创建记忆系统实例
        memory_system = create_estia_memory(
            enable_advanced=True,
            context_preset=preset
        )
        
        # 获取配置信息
        context_stats = memory_system.context_manager.get_context_stats()
        print(f"配置信息:")
        print(f"  预设: {context_stats['preset']}")
        print(f"  最大长度: {context_stats['max_length']} 字符")
        print(f"  目标长度: {context_stats['target_length']} 字符")
        print(f"  自适应: {'启用' if context_stats['adaptive_enabled'] else '禁用'}")
        
        # 模拟对话
        user_input = "我今天工作压力很大，感觉很累，你有什么建议吗？"
        
        # 增强查询
        enhanced_context = memory_system.enhance_query(user_input)
        
        # 显示结果
        print(f"\n增强后的上下文长度: {len(enhanced_context)} 字符")
        
        # 显示上下文预览（前300字符）
        preview = enhanced_context[:300] + "..." if len(enhanced_context) > 300 else enhanced_context
        print(f"上下文预览:\n{preview}")
        
        # 分析各部分
        sections = {
            "[系统角色设定]": "角色设定",
            "[当前会话]": "当前会话",
            "[核心记忆]": "核心记忆", 
            "[相关历史对话]": "历史对话",
            "[相关记忆]": "相关记忆",
            "[重要总结]": "重要总结"
        }
        
        found_sections = []
        for marker, name in sections.items():
            if marker in enhanced_context:
                found_sections.append(name)
        
        print(f"包含的部分: {', '.join(found_sections)}")
        
        # 存储对话（模拟）
        ai_response = "我理解你的感受。工作压力确实会影响心情和健康。建议你可以：1. 合理安排工作时间，避免过度劳累；2. 适当运动放松；3. 与朋友家人交流；4. 培养兴趣爱好。记住，健康是最重要的。"
        
        memory_system.store_interaction(user_input, ai_response)
        
        print(f"✅ 预设 {preset} 演示完成")
        
        # 清理
        try:
            import asyncio
            asyncio.run(memory_system.shutdown())
        except:
            pass

def demo_context_adaptation():
    """演示上下文自适应功能"""
    print("\n🔄 上下文自适应演示")
    print("=" * 50)
    
    # 创建记忆系统
    memory_system = create_estia_memory(
        enable_advanced=True,
        context_preset="balanced"
    )
    
    # 模拟多轮对话
    conversations = [
        ("你好，今天天气怎么样？", "今天天气很好，阳光明媚，适合外出活动。"),
        ("我最近在学习Python编程", "Python是一个很好的编程语言，适合初学者。建议从基础语法开始学习。"),
        ("工作压力很大，感觉很累", "我理解你的感受。工作压力确实会影响心情。建议适当休息，合理安排时间。"),
        ("我想学习机器学习", "机器学习是一个很有趣的领域。建议先掌握Python基础，然后学习数学和统计学。"),
        ("最近睡眠质量不好", "睡眠质量对健康很重要。建议保持规律作息，避免睡前使用电子设备。")
    ]
    
    for i, (user_input, ai_response) in enumerate(conversations, 1):
        print(f"\n--- 第{i}轮对话 ---")
        print(f"用户: {user_input}")
        print(f"AI: {ai_response}")
        
        # 增强查询
        enhanced_context = memory_system.enhance_query(user_input)
        
        # 显示上下文长度
        print(f"上下文长度: {len(enhanced_context)} 字符")
        
        # 存储对话
        memory_system.store_interaction(user_input, ai_response)
        
        # 等待一下，模拟真实对话
        import time
        time.sleep(0.5)
    
    print("\n✅ 多轮对话演示完成")

def demo_preset_comparison():
    """演示预设对比"""
    print("\n📊 预设对比演示")
    print("=" * 50)
    
    # 相同的用户输入
    user_input = "我今天工作压力很大，感觉很累，你有什么建议吗？"
    
    results = {}
    
    for preset in ["compact", "balanced", "detailed"]:
        print(f"\n测试预设: {preset}")
        
        # 创建记忆系统
        memory_system = create_estia_memory(
            enable_advanced=True,
            context_preset=preset
        )
        
        # 增强查询
        enhanced_context = memory_system.enhance_query(user_input)
        
        # 记录结果
        results[preset] = {
            "length": len(enhanced_context),
            "context": enhanced_context
        }
        
        print(f"  上下文长度: {len(enhanced_context)} 字符")
        
        # 清理
        try:
            import asyncio
            asyncio.run(memory_system.shutdown())
        except:
            pass
    
    # 对比结果
    print(f"\n📈 对比结果:")
    print(f"{'预设':<12} {'长度':<8} {'差异':<10}")
    print("-" * 30)
    
    balanced_length = results["balanced"]["length"]
    for preset in ["compact", "balanced", "detailed"]:
        length = results[preset]["length"]
        diff = length - balanced_length
        diff_str = f"{diff:+d}" if diff != 0 else "0"
        print(f"{preset:<12} {length:<8} {diff_str:<10}")

if __name__ == "__main__":
    print("🚀 开始上下文长度管理演示")
    
    try:
        # 演示不同预设
        demo_different_presets()
        
        # 演示上下文自适应
        demo_context_adaptation()
        
        # 演示预设对比
        demo_preset_comparison()
        
        print("\n✅ 所有演示完成！")
        
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc() 