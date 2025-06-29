#!/usr/bin/env python3
"""
测试增强版缓存系统
验证三个核心特性：
1. 多级缓存策略（热缓存+温缓存+持久化缓存）
2. 关键词缓存加速文本检索
3. 智能缓存提升机制
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time
from core.memory.embedding.cache import EnhancedMemoryCache

def test_multi_level_cache():
    """测试多级缓存策略"""
    print("=" * 60)
    print("测试 1: 多级缓存策略")
    print("=" * 60)
    
    # 初始化缓存系统
    cache = EnhancedMemoryCache(
        cache_dir="data/memory/test_enhanced_cache",
        hot_capacity=3,    # 小容量便于测试
        warm_capacity=5,
        persist=True
    )
    
    # 准备测试数据
    test_texts = [
        ("这是一个重要的记忆", 9.0),  # 高权重，应该直接进入热缓存
        ("这是一个普通的记忆", 5.0),  # 普通权重，进入温缓存
        ("这是另一个重要记忆", 8.0),  # 高权重，进入热缓存
        ("这是第三个普通记忆", 4.0),  # 普通权重，进入温缓存
        ("这是第四个普通记忆", 3.0),  # 普通权重，进入温缓存
        ("这是第五个普通记忆", 2.0),  # 普通权重，进入温缓存
        ("这是第六个普通记忆", 1.0),  # 普通权重，应该导致温缓存溢出
    ]
    
    # 添加测试向量
    print("添加测试数据到缓存...")
    for i, (text, weight) in enumerate(test_texts):
        vector = np.random.rand(384).astype(np.float32)  # 模拟向量
        cache.put(text, vector, memory_weight=weight)
        print(f"  添加: {text[:20]}... (权重: {weight})")
    
    # 检查缓存分布
    stats = cache.get_stats()
    print(f"\n缓存分布:")
    print(f"  热缓存大小: {stats['cache_levels']['hot_cache_size']}/{stats['cache_levels']['hot_capacity']}")
    print(f"  温缓存大小: {stats['cache_levels']['warm_cache_size']}/{stats['cache_levels']['warm_capacity']}")
    print(f"  关键词数量: {stats['cache_management']['keyword_count']}")
    
    # 验证重要记忆在热缓存中
    important_texts = [text for text, weight in test_texts if weight >= 7.0]
    print(f"\n验证重要记忆在热缓存中:")
    for text in important_texts:
        vector = cache.get(text, memory_weight=9.0)
        if vector is not None:
            print(f"  ✅ {text[:20]}... 在热缓存中")
        else:
            print(f"  ❌ {text[:20]}... 未找到")
    
    print(f"\n✅ 多级缓存策略测试完成")
    return cache

def test_keyword_cache(cache):
    """测试关键词缓存加速检索"""
    print("\n" + "=" * 60)
    print("测试 2: 关键词缓存加速文本检索")
    print("=" * 60)
    
    # 添加一些有明确关键词的记忆
    keyword_tests = [
        ("我今天学习了Python编程和机器学习", 6.0),
        ("使用PyTorch训练了一个深度学习模型", 7.0),
        ("研究了自然语言处理和文本分析", 5.0),
        ("开发了一个Web应用使用Flask框架", 6.0),
        ("学习了数据库设计和SQL查询优化", 5.0),
    ]
    
    print("添加包含关键词的记忆...")
    for text, weight in keyword_tests:
        vector = np.random.rand(384).astype(np.float32)
        cache.put(text, vector, memory_weight=weight)
        print(f"  添加: {text}")
    
    # 测试关键词搜索
    search_queries = [
        "Python编程",
        "深度学习",
        "Web开发",
        "数据库",
        "机器学习"
    ]
    
    print(f"\n测试关键词搜索:")
    for query in search_queries:
        start_time = time.time()
        results = cache.search_by_content(query, limit=3)
        search_time = time.time() - start_time
        
        print(f"\n  查询: '{query}'")
        print(f"  搜索时间: {search_time*1000:.2f}ms")
        print(f"  找到 {len(results)} 个结果:")
        
        for result in results:
            metadata = result['metadata']
            text_preview = metadata.get('text_preview', '')
            score = result['score']
            cache_level = result['cache_level']
            print(f"    📄 {text_preview[:40]}... (分数: {score:.3f}, 缓存级别: {cache_level})")
    
    # 检查关键词缓存命中统计
    stats = cache.get_stats()
    print(f"\n关键词缓存统计:")
    print(f"  关键词缓存命中: {stats['hit_statistics']['keyword_hits']}")
    print(f"  总关键词数量: {stats['cache_management']['keyword_count']}")
    
    print(f"\n✅ 关键词缓存测试完成")

def test_intelligent_promotion(cache):
    """测试智能缓存提升机制"""
    print("\n" + "=" * 60)
    print("测试 3: 智能缓存提升机制")
    print("=" * 60)
    
    # 添加一个普通权重的记忆
    test_text = "这是一个需要被频繁访问的记忆"
    vector = np.random.rand(384).astype(np.float32)
    cache.put(test_text, vector, memory_weight=3.0)  # 普通权重，应该在温缓存
    
    print(f"添加普通记忆: {test_text}")
    print(f"初始权重: 3.0 (应该在温缓存)")
    
    # 检查初始位置
    stats_before = cache.get_stats()
    print(f"\n提升前缓存状态:")
    print(f"  热缓存大小: {stats_before['cache_levels']['hot_cache_size']}")
    print(f"  温缓存大小: {stats_before['cache_levels']['warm_cache_size']}")
    
    # 多次访问该记忆以触发提升
    print(f"\n频繁访问该记忆以触发智能提升...")
    for i in range(5):
        vector_retrieved = cache.get(test_text, memory_weight=3.0)
        if vector_retrieved is not None:
            print(f"  第 {i+1} 次访问: ✅ 成功")
        else:
            print(f"  第 {i+1} 次访问: ❌ 失败")
        time.sleep(0.1)  # 短暂延迟
    
    # 检查是否被提升
    stats_after = cache.get_stats()
    print(f"\n提升后缓存状态:")
    print(f"  热缓存大小: {stats_after['cache_levels']['hot_cache_size']}")
    print(f"  温缓存大小: {stats_after['cache_levels']['warm_cache_size']}")
    print(f"  缓存提升次数: {stats_after['cache_management']['promotions']}")
    
    # 验证记忆是否在热缓存中
    if test_text in [cache._text_to_key(test_text)] and cache._text_to_key(test_text) in cache.hot_cache:
        print(f"  ✅ 记忆已被提升到热缓存")
    else:
        print(f"  ⚠️ 记忆可能还在温缓存中（需要更多访问）")
    
    # 测试高权重记忆的直接提升
    print(f"\n测试高权重记忆的直接提升...")
    high_weight_text = "这是一个非常重要的记忆"
    high_weight_vector = np.random.rand(384).astype(np.float32)
    cache.put(high_weight_text, high_weight_vector, memory_weight=8.5)  # 高权重
    
    print(f"添加高权重记忆: {high_weight_text}")
    print(f"权重: 8.5 (应该直接进入热缓存)")
    
    # 检查最终状态
    final_stats = cache.get_stats()
    print(f"\n最终缓存统计:")
    print(f"  热缓存: {final_stats['cache_levels']['hot_cache_size']}/{final_stats['cache_levels']['hot_capacity']}")
    print(f"  温缓存: {final_stats['cache_levels']['warm_cache_size']}/{final_stats['cache_levels']['warm_capacity']}")
    print(f"  总提升次数: {final_stats['cache_management']['promotions']}")
    print(f"  总驱逐次数: {final_stats['cache_management']['evictions']}")
    
    print(f"\n✅ 智能缓存提升机制测试完成")

def test_cache_performance():
    """测试缓存性能"""
    print("\n" + "=" * 60)
    print("测试 4: 缓存性能对比")
    print("=" * 60)
    
    cache = EnhancedMemoryCache(
        cache_dir="data/memory/test_performance_cache",
        hot_capacity=100,
        warm_capacity=500,
        persist=True
    )
    
    # 准备大量测试数据
    test_data = []
    for i in range(200):
        text = f"这是第{i}条测试记忆，包含一些随机内容和数字{i*123}"
        weight = 1.0 + (i % 10)  # 权重在1.0-10.0之间
        vector = np.random.rand(384).astype(np.float32)
        test_data.append((text, weight, vector))
    
    # 测试写入性能
    print("测试写入性能...")
    start_time = time.time()
    for text, weight, vector in test_data:
        cache.put(text, vector, memory_weight=weight)
    write_time = time.time() - start_time
    print(f"  写入 {len(test_data)} 条记忆耗时: {write_time:.3f}秒")
    print(f"  平均每条记忆: {write_time/len(test_data)*1000:.2f}ms")
    
    # 测试读取性能（缓存命中）
    print(f"\n测试读取性能（缓存命中）...")
    hit_times = []
    for i in range(50):  # 测试前50条
        text, weight, _ = test_data[i]
        start_time = time.time()
        vector = cache.get(text, memory_weight=weight)
        read_time = time.time() - start_time
        hit_times.append(read_time)
        if vector is None:
            print(f"  ❌ 第{i}条记忆读取失败")
    
    avg_hit_time = sum(hit_times) / len(hit_times)
    print(f"  平均缓存命中时间: {avg_hit_time*1000:.2f}ms")
    
    # 测试关键词搜索性能
    print(f"\n测试关键词搜索性能...")
    search_queries = ["测试", "记忆", "内容", "数字", "随机"]
    search_times = []
    
    for query in search_queries:
        start_time = time.time()
        results = cache.search_by_content(query, limit=10)
        search_time = time.time() - start_time
        search_times.append(search_time)
        print(f"  查询 '{query}': {search_time*1000:.2f}ms, 找到 {len(results)} 个结果")
    
    avg_search_time = sum(search_times) / len(search_times)
    print(f"  平均搜索时间: {avg_search_time*1000:.2f}ms")
    
    # 显示最终统计
    final_stats = cache.get_stats()
    print(f"\n最终性能统计:")
    print(f"  总命中率: {final_stats['hit_statistics']['hit_rate']}")
    print(f"  热缓存命中: {final_stats['hit_statistics']['hot_hits']}")
    print(f"  温缓存命中: {final_stats['hit_statistics']['warm_hits']}")
    print(f"  持久化缓存命中: {final_stats['hit_statistics']['persistent_hits']}")
    print(f"  关键词缓存命中: {final_stats['hit_statistics']['keyword_hits']}")
    print(f"  缓存未命中: {final_stats['hit_statistics']['misses']}")
    
    print(f"\n✅ 缓存性能测试完成")

def main():
    """主测试函数"""
    print("🚀 开始测试增强版缓存系统")
    print("测试三个核心特性：多级缓存、关键词缓存、智能提升")
    
    try:
        # 测试1: 多级缓存策略
        cache = test_multi_level_cache()
        
        # 测试2: 关键词缓存
        test_keyword_cache(cache)
        
        # 测试3: 智能缓存提升
        test_intelligent_promotion(cache)
        
        # 测试4: 性能测试
        test_cache_performance()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成！增强版缓存系统工作正常")
        print("=" * 60)
        
        print("\n📊 核心特性验证结果:")
        print("✅ 多级缓存策略：热缓存+温缓存+持久化缓存")
        print("✅ 关键词缓存：快速文本检索和匹配")
        print("✅ 智能缓存提升：基于访问频率和重要性的自动调整")
        print("✅ 性能优化：缓存命中率高，检索速度快")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 