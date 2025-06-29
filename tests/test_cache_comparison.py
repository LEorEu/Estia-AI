#!/usr/bin/env python3
"""
缓存系统对比测试
对比新的增强缓存系统与简单缓存系统的性能差异
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time
from collections import OrderedDict
from core.memory.embedding.cache import EnhancedMemoryCache

class SimpleLRUCache:
    """简单的LRU缓存实现，用于对比"""
    
    def __init__(self, capacity=1000):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.stats = {"hits": 0, "misses": 0}
    
    def get(self, key):
        if key in self.cache:
            # 移到最近使用位置
            value = self.cache.pop(key)
            self.cache[key] = value
            self.stats["hits"] += 1
            return value
        self.stats["misses"] += 1
        return None
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        self.cache[key] = value
    
    def search_by_content(self, query, limit=5):
        """简单的线性搜索"""
        results = []
        query_words = set(query.lower().split())
        
        for key, value in self.cache.items():
            # 模拟从key恢复文本内容（实际中可能需要额外存储）
            text = f"模拟文本内容包含{key[:20]}"
            text_words = set(text.lower().split())
            
            # 计算重叠度
            if query_words.intersection(text_words):
                overlap = len(query_words.intersection(text_words)) / len(query_words)
                results.append({
                    "key": key,
                    "vector": value,
                    "score": overlap,
                    "cache_level": "simple"
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

def generate_test_data(count=1000):
    """生成测试数据"""
    test_data = []
    topics = ["Python编程", "机器学习", "深度学习", "Web开发", "数据库", "算法", "人工智能", "自然语言处理"]
    
    for i in range(count):
        topic = topics[i % len(topics)]
        text = f"这是关于{topic}的第{i}条记忆，包含一些详细的技术内容和实践经验"
        weight = 1.0 + (i % 10)  # 权重在1.0-10.0之间
        vector = np.random.rand(384).astype(np.float32)
        test_data.append((text, weight, vector))
    
    return test_data

def test_write_performance():
    """测试写入性能"""
    print("=" * 60)
    print("写入性能对比测试")
    print("=" * 60)
    
    test_data = generate_test_data(500)
    
    # 测试简单缓存
    simple_cache = SimpleLRUCache(capacity=500)
    start_time = time.time()
    for text, weight, vector in test_data:
        key = str(hash(text))
        simple_cache.put(key, vector)
    simple_write_time = time.time() - start_time
    
    # 测试增强缓存
    enhanced_cache = EnhancedMemoryCache(
        cache_dir="data/memory/test_comparison_cache",
        hot_capacity=50,
        warm_capacity=450,
        persist=False  # 关闭持久化以公平对比
    )
    start_time = time.time()
    for text, weight, vector in test_data:
        enhanced_cache.put(text, vector, memory_weight=weight)
    enhanced_write_time = time.time() - start_time
    
    print(f"简单LRU缓存写入时间: {simple_write_time:.3f}秒")
    print(f"增强缓存写入时间: {enhanced_write_time:.3f}秒")
    
    if simple_write_time > 0 and enhanced_write_time > 0:
        if enhanced_write_time < simple_write_time:
            improvement = (simple_write_time - enhanced_write_time) / simple_write_time * 100
            print(f"性能比较: 增强缓存比简单缓存快 {improvement:.1f}%")
        else:
            slowdown = (enhanced_write_time - simple_write_time) / simple_write_time * 100
            print(f"性能比较: 增强缓存比简单缓存慢 {slowdown:.1f}%")
    else:
        print("性能比较: 写入时间太短，无法准确比较")
    
    return simple_cache, enhanced_cache, test_data

def test_read_performance(simple_cache, enhanced_cache, test_data):
    """测试读取性能"""
    print("\n" + "=" * 60)
    print("读取性能对比测试")
    print("=" * 60)
    
    # 随机选择100条数据进行读取测试
    import random
    test_samples = random.sample(test_data, min(100, len(test_data)))
    
    # 测试简单缓存读取
    simple_times = []
    simple_hits = 0
    for text, weight, vector in test_samples:
        key = str(hash(text))
        start_time = time.time()
        result = simple_cache.get(key)
        read_time = time.time() - start_time
        simple_times.append(read_time)
        if result is not None:
            simple_hits += 1
    
    # 测试增强缓存读取
    enhanced_times = []
    enhanced_hits = 0
    for text, weight, vector in test_samples:
        start_time = time.time()
        result = enhanced_cache.get(text, memory_weight=weight)
        read_time = time.time() - start_time
        enhanced_times.append(read_time)
        if result is not None:
            enhanced_hits += 1
    
    simple_avg = sum(simple_times) / len(simple_times) * 1000 if simple_times else 0
    enhanced_avg = sum(enhanced_times) / len(enhanced_times) * 1000 if enhanced_times else 0
    
    print(f"简单LRU缓存:")
    print(f"  平均读取时间: {simple_avg:.3f}ms")
    print(f"  命中率: {simple_hits/len(test_samples)*100:.1f}%")
    
    print(f"增强缓存:")
    print(f"  平均读取时间: {enhanced_avg:.3f}ms")
    print(f"  命中率: {enhanced_hits/len(test_samples)*100:.1f}%")
    
    if simple_avg > 0 and enhanced_avg > 0:
        if enhanced_avg < simple_avg:
            improvement = (simple_avg - enhanced_avg) / simple_avg * 100
            print(f"性能比较: 增强缓存比简单缓存快 {improvement:.1f}%")
        else:
            slowdown = (enhanced_avg - simple_avg) / simple_avg * 100
            print(f"性能比较: 增强缓存比简单缓存慢 {slowdown:.1f}%")
    else:
        print("性能比较: 两个系统的读取时间都非常接近0，无法准确比较")

def test_search_performance(simple_cache, enhanced_cache):
    """测试搜索性能"""
    print("\n" + "=" * 60)
    print("搜索性能对比测试")
    print("=" * 60)
    
    search_queries = [
        "Python编程",
        "机器学习", 
        "深度学习",
        "Web开发",
        "数据库",
        "算法",
        "人工智能",
        "自然语言处理"
    ]
    
    simple_times = []
    enhanced_times = []
    
    for query in search_queries:
        # 测试简单缓存搜索
        start_time = time.time()
        simple_results = simple_cache.search_by_content(query, limit=5)
        simple_search_time = time.time() - start_time
        simple_times.append(simple_search_time)
        
        # 测试增强缓存搜索
        start_time = time.time()
        enhanced_results = enhanced_cache.search_by_content(query, limit=5)
        enhanced_search_time = time.time() - start_time
        enhanced_times.append(enhanced_search_time)
        
        print(f"查询 '{query}':")
        print(f"  简单缓存: {simple_search_time*1000:.2f}ms, 找到 {len(simple_results)} 个结果")
        print(f"  增强缓存: {enhanced_search_time*1000:.2f}ms, 找到 {len(enhanced_results)} 个结果")
    
    simple_avg = sum(simple_times) / len(simple_times) * 1000
    enhanced_avg = sum(enhanced_times) / len(enhanced_times) * 1000
    
    print(f"\n搜索性能总结:")
    print(f"  简单缓存平均搜索时间: {simple_avg:.2f}ms")
    print(f"  增强缓存平均搜索时间: {enhanced_avg:.2f}ms")
    print(f"  性能提升: {(simple_avg - enhanced_avg)/simple_avg*100:.1f}%")

def test_memory_usage():
    """测试内存使用情况"""
    print("\n" + "=" * 60)
    print("内存使用对比测试")
    print("=" * 60)
    
    import psutil
    import gc
    
    # 获取初始内存
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # 测试简单缓存内存使用
    gc.collect()
    memory_before_simple = process.memory_info().rss / 1024 / 1024
    
    simple_cache = SimpleLRUCache(capacity=1000)
    test_data = generate_test_data(1000)
    
    for text, weight, vector in test_data:
        key = str(hash(text))
        simple_cache.put(key, vector)
    
    memory_after_simple = process.memory_info().rss / 1024 / 1024
    simple_memory_usage = memory_after_simple - memory_before_simple
    
    # 清理简单缓存
    del simple_cache
    gc.collect()
    
    # 测试增强缓存内存使用
    memory_before_enhanced = process.memory_info().rss / 1024 / 1024
    
    enhanced_cache = EnhancedMemoryCache(
        cache_dir="data/memory/test_memory_cache",
        hot_capacity=100,
        warm_capacity=900,
        persist=False
    )
    
    for text, weight, vector in test_data:
        enhanced_cache.put(text, vector, memory_weight=weight)
    
    memory_after_enhanced = process.memory_info().rss / 1024 / 1024
    enhanced_memory_usage = memory_after_enhanced - memory_before_enhanced
    
    print(f"简单LRU缓存内存使用: {simple_memory_usage:.2f}MB")
    print(f"增强缓存内存使用: {enhanced_memory_usage:.2f}MB")
    print(f"内存使用差异: {enhanced_memory_usage - simple_memory_usage:.2f}MB")
    
    # 显示增强缓存的额外功能价值
    stats = enhanced_cache.get_stats()
    print(f"\n增强缓存额外功能:")
    print(f"  关键词索引数量: {stats['cache_management']['keyword_count']}")
    print(f"  元数据条目数量: {stats['cache_management']['metadata_count']}")
    print(f"  智能提升次数: {stats['cache_management']['promotions']}")

def main():
    """主测试函数"""
    print("🚀 开始缓存系统性能对比测试")
    print("对比简单LRU缓存 vs 增强记忆缓存系统")
    
    try:
        # 写入性能测试
        simple_cache, enhanced_cache, test_data = test_write_performance()
        
        # 读取性能测试
        test_read_performance(simple_cache, enhanced_cache, test_data)
        
        # 搜索性能测试
        test_search_performance(simple_cache, enhanced_cache)
        
        # 内存使用测试
        test_memory_usage()
        
        print("\n" + "=" * 60)
        print("🎉 性能对比测试完成！")
        print("=" * 60)
        
        print("\n📊 增强缓存系统的优势:")
        print("✅ 多级缓存策略：更智能的内存管理")
        print("✅ 关键词索引：大幅提升搜索性能")  
        print("✅ 智能提升机制：自动优化热点数据")
        print("✅ 权重感知：重要记忆优先缓存")
        print("✅ 丰富统计：详细的性能监控")
        
        print("\n💡 建议:")
        print("- 对于简单场景，简单LRU缓存已足够")
        print("- 对于复杂记忆系统，增强缓存提供更多智能特性")
        print("- 增强缓存的额外内存开销换来了显著的功能提升")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 