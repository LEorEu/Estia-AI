#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级记忆功能演示

展示Estia记忆系统的新功能：
1. 动态权重机制
2. LLM主动记忆访问
3. 增强评估上下文
4. 智能归档管理
"""

import sys
import os
import time
import asyncio
from datetime import datetime
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.estia_memory import create_estia_memory

async def demo_dynamic_weight_system():
    """演示动态权重机制"""
    print("🧠 动态权重机制演示")
    print("=" * 50)
    
    # 初始化记忆系统
    memory_system = create_estia_memory(enable_advanced=True)
    
    if not memory_system.initialized:
        print("❌ 记忆系统初始化失败")
        return
    
    print("✅ 记忆系统初始化成功")
    
    # 1. 添加测试记忆
    print("\n1. 添加测试记忆...")
    test_memories = [
        {"content": "用户的姓名是张三，是一名Python程序员", "weight": 8.0},
        {"content": "用户喜欢喝咖啡，特别是拿铁", "weight": 5.0},
        {"content": "今天天气很好，阳光明媚", "weight": 2.0},
        {"content": "用户最近工作压力很大，经常加班", "weight": 6.0},
        {"content": "用户在考虑换工作，想找更好的发展机会", "weight": 7.0}
    ]
    
    memory_ids = []
    for i, memory in enumerate(test_memories):
        # 模拟存储记忆（这里简化处理）
        memory_id = f"mem_{i:03d}"
        memory_ids.append(memory_id)
        print(f"  添加记忆 {memory_id}: {memory['content'][:30]}... (权重: {memory['weight']})")
    
    time.sleep(1)
    
    # 2. 演示动态权重更新
    print("\n2. 演示动态权重更新...")
    
    # 模拟访问"工作压力"相关记忆
    test_memory_id = "mem_003"
    print(f"\n访问记忆 {test_memory_id}（工作压力相关）...")
    
    # 构建上下文信息
    context = {
        'current_topic': '工作压力',
        'user_emotion': 'anxious',
        'session_type': 'emotional_support',
        'search_type': 'keyword'
    }
    
    # 更新动态权重
    result = memory_system.update_memory_weight_dynamically(test_memory_id, context)
    
    if result['success']:
        print(f"✅ 权重更新成功:")
        print(f"   原权重: {result['old_weight']:.2f}")
        print(f"   新权重: {result['new_weight']:.2f}")
        print(f"   变化量: {result['weight_change']:+.2f}")
        print(f"   调整因子: {result['factors']}")
    else:
        print(f"❌ 权重更新失败: {result['message']}")
    
    # 3. 演示不同场景的权重调整
    print("\n3. 演示不同场景的权重调整...")
    
    scenarios = [
        {
            'name': '情感支持场景',
            'context': {
                'current_topic': '情感',
                'user_emotion': 'sad',
                'session_type': 'emotional_support'
            }
        },
        {
            'name': '技术讨论场景',
            'context': {
                'current_topic': 'Python编程',
                'user_emotion': 'neutral',
                'session_type': 'technical'
            }
        },
        {
            'name': '职业规划场景',
            'context': {
                'current_topic': '职业发展',
                'user_emotion': 'hopeful',
                'session_type': 'career_planning'
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        for memory_id in memory_ids[:3]:  # 只演示前3个记忆
            result = memory_system.update_memory_weight_dynamically(memory_id, scenario['context'])
            if result['success']:
                print(f"  {memory_id}: {result['old_weight']:.2f} → {result['new_weight']:.2f} ({result['weight_change']:+.2f})")

async def demo_llm_memory_access():
    """演示LLM主动记忆访问"""
    print("\n🔍 LLM主动记忆访问演示")
    print("=" * 50)
    
    memory_system = create_estia_memory(enable_advanced=True)
    
    if not memory_system.initialized:
        print("❌ 记忆系统初始化失败")
        return
    
    # 1. 获取可用的记忆搜索工具
    print("\n1. 获取可用的记忆搜索工具...")
    tools = memory_system.get_memory_search_tools()
    
    print(f"✅ 找到 {len(tools)} 个记忆搜索工具:")
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool['name']}: {tool['description']}")
    
    # 2. 演示关键词搜索
    print("\n2. 演示关键词搜索...")
    
    search_params = {
        'keywords': '工作',
        'weight_threshold': 3.0,
        'max_results': 5
    }
    
    print(f"搜索参数: {search_params}")
    result = memory_system.execute_memory_search_tool('search_memories_by_keyword', search_params)
    
    if result['success']:
        print(f"✅ {result['message']}")
        for memory in result['memories']:
            print(f"  - [{memory['layer']}] {memory['content'][:50]}... (权重: {memory['weight']:.1f})")
    else:
        print(f"❌ 搜索失败: {result['message']}")
    
    # 3. 演示时间范围搜索
    print("\n3. 演示时间范围搜索...")
    
    search_params = {
        'days_ago': 7,
        'max_results': 10
    }
    
    print(f"搜索参数: {search_params}")
    result = memory_system.execute_memory_search_tool('search_memories_by_timeframe', search_params)
    
    if result['success']:
        print(f"✅ {result['message']}")
        for memory in result['memories']:
            age = memory['age_days']
            print(f"  - [{memory['layer']}] {memory['content'][:40]}... (权重: {memory['weight']:.1f}, {age:.1f}天前)")
    else:
        print(f"❌ 搜索失败: {result['message']}")
    
    # 4. 演示核心记忆搜索
    print("\n4. 演示核心记忆搜索...")
    
    search_params = {
        'category': 'user_info'
    }
    
    print(f"搜索参数: {search_params}")
    result = memory_system.execute_memory_search_tool('search_core_memories', search_params)
    
    if result['success']:
        print(f"✅ {result['message']}")
        for memory in result['memories']:
            print(f"  - [核心记忆] {memory['content'][:60]}... (权重: {memory['weight']:.1f})")
    else:
        print(f"❌ 搜索失败: {result['message']}")
    
    # 5. 演示LLM思考过程模拟
    print("\n5. 演示LLM思考过程模拟...")
    
    user_query = "我最近工作压力好大，你觉得我该怎么办？"
    print(f"用户问题: {user_query}")
    print("\nLLM思考过程:")
    
    # 步骤1: 搜索相关记忆
    print("  步骤1: 搜索工作压力相关记忆...")
    result1 = memory_system.execute_memory_search_tool('search_memories_by_keyword', {'keywords': '工作压力'})
    if result1['success']:
        print(f"    找到 {len(result1['memories'])} 条相关记忆")
    
    # 步骤2: 获取用户基本信息
    print("  步骤2: 获取用户基本信息...")
    result2 = memory_system.execute_memory_search_tool('search_core_memories', {'category': 'user_info'})
    if result2['success']:
        print(f"    找到 {len(result2['memories'])} 条用户信息")
    
    # 步骤3: 查看近期对话
    print("  步骤3: 查看近期对话...")
    result3 = memory_system.execute_memory_search_tool('search_memories_by_timeframe', {'days_ago': 3})
    if result3['success']:
        print(f"    找到 {len(result3['memories'])} 条近期记忆")
    
    # 步骤4: 综合分析
    print("  步骤4: 综合分析...")
    print("    基于检索到的记忆，LLM可以:")
    print("    - 了解用户的工作背景和专业技能")
    print("    - 分析压力产生的具体原因")
    print("    - 结合用户性格特点给出个性化建议")
    print("    - 提供情感支持和实用解决方案")

async def demo_enhanced_evaluation_context():
    """演示增强评估上下文"""
    print("\n📊 增强评估上下文演示")
    print("=" * 50)
    
    memory_system = create_estia_memory(enable_advanced=True)
    
    if not memory_system.initialized:
        print("❌ 记忆系统初始化失败")
        return
    
    # 1. 构建测试上下文
    print("\n1. 构建增强评估上下文...")
    
    user_input = "我今天工作状态很好，完成了很多任务"
    ai_response = "听起来你今天很有效率！这和之前提到的工作压力形成了很好的对比。"
    session_id = "test_session_001"
    
    # 模拟相关记忆
    test_memories = [
        {
            'id': 'mem_001',
            'content': '用户最近工作压力很大，经常加班',
            'type': 'user_input',
            'weight': 6.0,
            'timestamp': time.time() - 86400,  # 1天前
            'group_id': 'work_stress_topic'
        },
        {
            'id': 'mem_002',
            'content': '用户是Python程序员，喜欢技术挑战',
            'type': 'user_input',
            'weight': 8.0,
            'timestamp': time.time() - 604800,  # 7天前
            'group_id': 'user_profile'
        }
    ]
    
    # 构建评估上下文
    context = memory_system._build_evaluation_context(
        user_input=user_input,
        ai_response=ai_response,
        memories=test_memories,
        session_id=session_id
    )
    
    print("✅ 评估上下文构建完成")
    
    # 2. 显示用户画像
    print("\n2. 用户画像:")
    user_profile = context['user_profile']
    for category, items in user_profile.items():
        if items:
            print(f"  {category}: {len(items)} 条信息")
            for item in items[:2]:  # 显示前2条
                print(f"    - {item[:50]}...")
    
    # 3. 显示话题上下文
    print("\n3. 话题上下文:")
    topic_context = context['topic_context']
    if topic_context:
        print(f"  当前关键词: {topic_context.get('current_keywords', [])}")
        print(f"  活跃话题: {topic_context.get('active_topics', [])}")
        print(f"  话题演进: {len(topic_context.get('topic_evolution', []))} 个话题轨迹")
    
    # 4. 显示情感上下文
    print("\n4. 情感上下文:")
    emotional_context = context['emotional_context']
    if emotional_context:
        print(f"  当前情感: {emotional_context.get('current_emotion', 'neutral')}")
        print(f"  历史情感: {emotional_context.get('historical_emotions', [])}")
        print(f"  情感模式: {emotional_context.get('emotion_pattern', 'stable')}")
    
    # 5. 显示对话历史
    print("\n5. 对话历史:")
    conversation_history = context['conversation_history']
    if conversation_history:
        print(f"  最近 {len(conversation_history)} 轮对话")
        for i, conv in enumerate(conversation_history):
            print(f"    第{i+1}轮:")
            print(f"      用户: {conv['user'][:40]}...")
            print(f"      AI: {conv['assistant'][:40]}...")
    else:
        print("  暂无对话历史")

async def demo_memory_archiving():
    """演示智能归档管理"""
    print("\n💾 智能归档管理演示")
    print("=" * 50)
    
    memory_system = create_estia_memory(enable_advanced=True)
    
    if not memory_system.initialized:
        print("❌ 记忆系统初始化失败")
        return
    
    # 1. 显示当前记忆状态
    print("\n1. 当前记忆系统状态:")
    stats = memory_system.get_system_stats()
    print(f"  系统初始化: {stats['initialized']}")
    print(f"  高级功能: {stats['advanced_features']}")
    
    # 2. 演示归档过期记忆
    print("\n2. 演示归档过期记忆...")
    
    # 归档30天前的短期记忆
    archive_result = memory_system.archive_old_memories(
        days_threshold=30,
        archive_weight_penalty=0.3
    )
    
    if archive_result['success']:
        print(f"✅ {archive_result['message']}")
        print(f"  归档数量: {archive_result['archived_count']}")
        print(f"  权重惩罚: {archive_result['weight_penalty']}")
    else:
        print(f"❌ 归档失败: {archive_result['message']}")
    
    # 3. 演示记忆恢复
    print("\n3. 演示记忆恢复...")
    
    # 恢复特定记忆
    test_memory_ids = ['mem_001', 'mem_002']  # 假设的记忆ID
    
    restore_result = memory_system.restore_archived_memories(
        memory_ids=test_memory_ids,
        restore_weight_bonus=1.5
    )
    
    if restore_result['success']:
        print(f"✅ {restore_result['message']}")
        print(f"  恢复数量: {restore_result['restored_count']}")
        print(f"  权重奖励: {restore_result['weight_bonus']}")
    else:
        print(f"❌ 恢复失败: {restore_result['message']}")
    
    # 4. 显示记忆生命周期统计
    print("\n4. 记忆生命周期统计:")
    lifecycle_stats = memory_system.get_memory_lifecycle_stats()
    
    if lifecycle_stats['success']:
        layer_stats = lifecycle_stats['layer_distribution']
        print("  分层分布:")
        for layer, count in layer_stats.items():
            print(f"    {layer}: {count} 条记忆")
        
        print(f"  总记忆数: {lifecycle_stats['total_memories']}")
        print(f"  归档记忆: {lifecycle_stats['archived_memories']}")
        print(f"  活跃记忆: {lifecycle_stats['active_memories']}")
    else:
        print(f"❌ 获取统计失败: {lifecycle_stats['message']}")

async def main():
    """主函数"""
    print("🚀 Estia高级记忆功能演示")
    print("=" * 60)
    
    try:
        # 1. 动态权重机制演示
        await demo_dynamic_weight_system()
        
        # 等待用户确认
        input("\n按回车键继续...")
        
        # 2. LLM主动记忆访问演示
        await demo_llm_memory_access()
        
        # 等待用户确认
        input("\n按回车键继续...")
        
        # 3. 增强评估上下文演示
        await demo_enhanced_evaluation_context()
        
        # 等待用户确认
        input("\n按回车键继续...")
        
        # 4. 智能归档管理演示
        await demo_memory_archiving()
        
        print("\n🎉 演示完成！")
        print("\n总结:")
        print("1. ✅ 动态权重机制 - 记忆权重随时间和上下文动态调整")
        print("2. ✅ LLM主动记忆访问 - 4种搜索工具支持深度思考")
        print("3. ✅ 增强评估上下文 - 基于用户画像和情感分析的精准评估")
        print("4. ✅ 智能归档管理 - 软删除机制保留所有记忆")
        print("\n这些功能让Estia从简单的记忆系统进化为智能记忆伙伴！")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 