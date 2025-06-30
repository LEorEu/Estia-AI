#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
上下文构建器测试
测试Step 8的上下文构建功能
"""

import os
import sys
import time
import logging

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.memory.context.builder import ContextBuilder

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_context_builder():
    """测试上下文构建器功能"""
    print("=" * 50)
    print("上下文构建器测试 (Step 8)")
    print("=" * 50)
    
    # 初始化构建器
    print("\n1. 初始化上下文构建器...")
    builder = ContextBuilder(max_context_length=1500, max_memories=10)
    print("✓ 上下文构建器初始化成功")
    
    # 准备测试数据
    print("\n2. 准备测试数据...")
    test_memories = [
        {
            "memory_id": "mem_1",
            "content": "用户询问Python编程的基础语法，我详细介绍了变量、数据类型和控制结构。",
            "summary": "Python基础语法介绍：变量、数据类型、控制结构",
            "weight": 6.0,
            "computed_score": 8.5,
            "super_group": "学习",
            "group_id": "学习_2025_01_01",
            "timestamp": time.time() - 3600,  # 1小时前
            "type": "dialogue",
            "role": "assistant"
        },
        {
            "memory_id": "mem_2", 
            "content": "用户分享了今天面试软件工程师职位的经历，我给出了一些建议。",
            "summary": "软件工程师面试经历分享和建议",
            "weight": 7.0,
            "computed_score": 9.0,
            "super_group": "工作",
            "group_id": "工作_2025_01_01",
            "timestamp": time.time() - 7200,  # 2小时前
            "type": "dialogue",
            "role": "assistant"
        },
        {
            "memory_id": "mem_3",
            "content": "用户询问今天天气如何，我说无法获取实时天气信息。",
            "summary": "天气询问",
            "weight": 2.0,
            "computed_score": 3.0,
            "super_group": "生活",
            "group_id": "生活_2025_01_01",
            "timestamp": time.time() - 1800,  # 30分钟前
            "type": "dialogue",
            "role": "assistant"
        },
        {
            "memory_id": "mem_4",
            "content": "用户询问机器学习算法的分类，我介绍了监督学习、无监督学习和强化学习。",
            "summary": "机器学习算法分类：监督、无监督、强化学习",
            "weight": 8.0,
            "computed_score": 9.5,
            "super_group": "学习",
            "group_id": "学习_2025_01_01",
            "timestamp": time.time() - 86400,  # 1天前
            "type": "dialogue",
            "role": "assistant"
        },
        {
            "memory_id": "mem_5",
            "content": "用户说要开始健身计划，我给出了一些初学者建议。",
            "summary": "健身计划制定和初学者建议",
            "weight": 5.0,
            "computed_score": 6.5,
            "super_group": "健康",
            "group_id": "健康_2025_01_01",
            "timestamp": time.time() - 172800,  # 2天前
            "type": "dialogue",
            "role": "assistant"
        }
    ]
    
    print(f"✓ 准备了 {len(test_memories)} 条测试记忆")
    
    # 测试用例
    test_cases = [
        {
            "name": "Python学习相关查询",
            "user_input": "我想深入学习Python的面向对象编程",
            "personality": "你是一个专业的编程导师，善于用简单易懂的方式解释复杂概念。"
        },
        {
            "name": "工作面试相关查询", 
            "user_input": "明天还有一场技术面试，有什么需要特别注意的吗？",
            "personality": None
        },
        {
            "name": "综合性查询",
            "user_input": "我想制定一个平衡工作、学习和健康的计划",
            "personality": "你是一个生活规划专家，善于帮助用户制定平衡的生活计划。"
        }
    ]
    
    print("\n3. 开始上下文构建测试...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   测试用例 {i}: {test_case['name']}")
        print(f"   用户输入: {test_case['user_input']}")
        
        # 构建增强上下文
        start_time = time.time()
        enhanced_context = builder.build_enhanced_context(
            user_input=test_case['user_input'],
            ranked_memories=test_memories,
            personality_info=test_case['personality']
        )
        build_time = (time.time() - start_time) * 1000
        
        print(f"   ✓ 上下文构建完成，耗时: {build_time:.2f}ms")
        print(f"   ✓ 上下文长度: {len(enhanced_context)} 字符")
        
        # 获取上下文统计
        stats = builder.get_context_stats(enhanced_context)
        print(f"   ✓ 包含部分: {list(stats.get('sections', {}).keys())}")
        print(f"   ✓ 总行数: {stats.get('total_lines', 0)}")
        print(f"   ✓ 长度限制: {'✓ 符合' if stats.get('within_limit') else '✗ 超出'}")
        
        # 显示部分上下文内容
        lines = enhanced_context.split('\n')
        preview_lines = []
        for line in lines:
            if line.startswith('[') and line.endswith(']'):
                preview_lines.append(line)
            if len(preview_lines) >= 5:
                break
        
        if preview_lines:
            print(f"   ✓ 上下文结构: {' -> '.join(preview_lines)}")
        
        print("   " + "-" * 40)
    
    # 测试简单上下文构建
    print("\n4. 测试简单上下文构建...")
    simple_context = builder.build_simple_context(
        user_input="这是一个简单测试",
        memories=test_memories[:3]
    )
    print(f"   ✓ 简单上下文长度: {len(simple_context)} 字符")
    
    # 测试极限情况
    print("\n5. 测试极限情况...")
    
    # 空记忆列表
    empty_context = builder.build_enhanced_context(
        user_input="没有相关记忆的查询",
        ranked_memories=[],
        personality_info=None
    )
    print(f"   ✓ 空记忆上下文: {len(empty_context)} 字符")
    
    # 超长记忆
    long_memories = []
    for i in range(20):
        long_memory = test_memories[0].copy()
        long_memory['memory_id'] = f"long_mem_{i}"
        long_memory['content'] = "这是一段很长的记忆内容。" * 20  # 很长的内容
        long_memory['summary'] = "这是一段很长的记忆摘要。" * 10   # 很长的摘要
        long_memories.append(long_memory)
    
    long_context = builder.build_enhanced_context(
        user_input="测试超长记忆处理",
        ranked_memories=long_memories,
        personality_info="你是一个测试助手。" * 10  # 很长的个性化信息
    )
    print(f"   ✓ 超长记忆上下文: {len(long_context)} 字符")
    print(f"   ✓ 智能截断: {'✓ 已截断' if len(long_context) <= builder.max_context_length else '✗ 未截断'}")
    
    print("\n6. 性能测试...")
    
    # 批量构建测试
    start_time = time.time()
    for _ in range(100):
        builder.build_enhanced_context(
            user_input="性能测试查询",
            ranked_memories=test_memories,
            personality_info=None
        )
    batch_time = (time.time() - start_time) * 1000
    avg_time = batch_time / 100
    
    print(f"   ✓ 100次构建总耗时: {batch_time:.2f}ms")
    print(f"   ✓ 平均每次耗时: {avg_time:.2f}ms")
    print(f"   ✓ 性能评级: {'优秀' if avg_time < 5 else '良好' if avg_time < 10 else '一般'}")
    
    print("\n✓ 上下文构建器测试完成")
    print("=" * 50)

def main():
    """主测试函数"""
    try:
        test_context_builder()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 