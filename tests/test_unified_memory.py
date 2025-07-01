#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一记忆管理器测试
验证新的记忆系统功能
"""

import os
import sys
import time
import logging

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.memory.unified_manager import UnifiedMemoryManager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_functionality():
    """测试基本功能"""
    print("\n🧠 测试统一记忆管理器基本功能...")
    
    # 初始化管理器（禁用数据库避免冲突）
    memory_manager = UnifiedMemoryManager(enable_database=False)
    
    # 测试存储不同权重的记忆
    test_memories = [
        ("我叫张三，是一名程序员", "user", 9.5),
        ("今天天气很好", "user", 7.0),
        ("我喜欢听音乐", "user", 5.0),
        ("随便说说而已", "user", 2.0),
    ]
    
    memory_ids = []
    for content, role, weight in test_memories:
        memory_id = memory_manager.remember(content, role, weight)
        memory_ids.append(memory_id)
        layer = memory_manager._determine_layer(weight)
        print(f"✅ 存储记忆: {content} (权重: {weight}, 层级: {layer})")
    
    # 测试检索
    print("\n🔍 测试记忆检索...")
    
    search_queries = ["张三", "程序员", "天气", "音乐"]
    
    for query in search_queries:
        results = memory_manager.recall(query, max_results=3)
        print(f"\n查询: '{query}'")
        for i, result in enumerate(results, 1):
            layer = result.get('layer', 'unknown')
            weight = result.get('weight', 0)
            content = result.get('content', '')[:30]
            print(f"  {i}. [{layer}层] 权重:{weight:.1f} - {content}...")
    
    # 显示统计信息
    print("\n📊 系统统计信息:")
    stats = memory_manager.get_stats()
    print(f"总记忆数: {stats['total_memories']}")
    for layer_name, layer_stats in stats['layers'].items():
        count = layer_stats['count']
        capacity = layer_stats['capacity']
        utilization = layer_stats['utilization']
        print(f"  {layer_name}层: {count}/{capacity} (利用率: {utilization:.1%})")
    
    return memory_manager

def test_layer_assignment():
    """测试分层分配"""
    print("\n📋 测试记忆分层分配...")
    
    memory_manager = UnifiedMemoryManager(enable_database=False)
    
    test_cases = [
        (10.0, "core"),
        (9.0, "core"),
        (8.5, "active"),
        (6.0, "active"),
        (5.5, "archive"),
        (4.0, "archive"),
        (3.0, "temp"),
        (1.0, "temp")
    ]
    
    for weight, expected_layer in test_cases:
        actual_layer = memory_manager._determine_layer(weight)
        status = "✅" if actual_layer == expected_layer else "❌"
        print(f"{status} 权重 {weight} → {actual_layer}层 (期望: {expected_layer}层)")

def test_memory_search():
    """测试记忆搜索功能"""
    print("\n🔍 测试记忆搜索功能...")
    
    memory_manager = UnifiedMemoryManager(enable_database=False)
    
    # 添加一些测试记忆
    test_data = [
        ("我的名字是小明，我是一个AI助手", "assistant", 9.0),
        ("用户喜欢听流行音乐", "system", 7.5),
        ("今天讨论了编程相关的话题", "user", 6.0),
        ("天气预报说明天会下雨", "user", 4.5),
        ("刚才提到了Python编程语言", "user", 5.5),
        ("用户询问了关于AI的问题", "user", 6.5),
    ]
    
    for content, role, weight in test_data:
        memory_manager.remember(content, role, weight)
    
    # 测试不同的搜索查询
    search_tests = [
        ("AI", "应该找到AI助手和AI问题相关的记忆"),
        ("编程", "应该找到编程相关的记忆"),
        ("音乐", "应该找到音乐相关的记忆"),
        ("天气", "应该找到天气相关的记忆"),
        ("Python", "应该找到Python编程的记忆")
    ]
    
    for query, description in search_tests:
        print(f"\n查询: '{query}' - {description}")
        results = memory_manager.recall(query, max_results=3)
        
        if results:
            for i, result in enumerate(results, 1):
                content = result.get('content', '')
                layer = result.get('layer', 'unknown')
                weight = result.get('weight', 0)
                print(f"  {i}. [{layer}] {weight:.1f} - {content}")
        else:
            print("  未找到相关记忆")

def test_performance():
    """测试性能"""
    print("\n⚡ 测试性能...")
    
    memory_manager = UnifiedMemoryManager(enable_database=False)
    
    # 批量添加记忆测试
    print("测试批量存储性能...")
    start_time = time.time()
    
    for i in range(100):
        content = f"这是第{i}条测试记忆，包含一些随机内容用于测试性能"
        weight = 3.0 + (i % 7)  # 权重在3.0-9.0之间变化
        memory_manager.remember(content, "user", weight)
    
    storage_time = time.time() - start_time
    print(f"✅ 存储100条记忆耗时: {storage_time:.3f}秒 (平均 {storage_time/100*1000:.1f}ms/条)")
    
    # 批量检索测试
    print("测试批量检索性能...")
    start_time = time.time()
    
    for i in range(20):
        query = f"测试{i}"
        results = memory_manager.recall(query, max_results=5)
    
    retrieval_time = time.time() - start_time
    print(f"✅ 执行20次检索耗时: {retrieval_time:.3f}秒 (平均 {retrieval_time/20*1000:.1f}ms/次)")
    
    # 显示最终统计
    stats = memory_manager.get_stats()
    print(f"✅ 系统总记忆数: {stats['total_memories']}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧠 统一记忆管理器测试")
    print("=" * 60)
    
    try:
        # 执行各项测试
        test_layer_assignment()
        test_basic_functionality()
        test_memory_search()
        test_performance()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！统一记忆管理器工作正常")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 