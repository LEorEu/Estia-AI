#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Embedding缓存模块功能
"""

import os
import sys
import numpy as np
import time
import shutil

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入Embedding缓存
from core.memory.embedding.cache import EmbeddingCache

def test_embedding_cache():
    """测试Embedding缓存的基本功能"""
    print("\n===== 测试Embedding缓存 =====")
    
    # 使用测试缓存目录
    test_cache_dir = os.path.join("data", "memory", "test_cache")
    
    # 确保目录存在
    os.makedirs(test_cache_dir, exist_ok=True)
    
    # 清理可能存在的旧测试文件
    if os.path.exists(test_cache_dir):
        for filename in os.listdir(test_cache_dir):
            file_path = os.path.join(test_cache_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"清理文件失败: {e}")
    
    print("\n1. 初始化Embedding缓存")
    cache = EmbeddingCache(
        cache_dir=test_cache_dir,
        max_memory_size=100,  # 小一点，方便测试LRU逻辑
        persist=True
    )
    
    print("\n2. 测试缓存未命中")
    test_texts = [
        "这是第一个测试文本，用于验证缓存功能",
        "这是第二个测试文本，内容不同",
        "第三个测试文本，完全不同的内容"
    ]
    
    for i, text in enumerate(test_texts):
        result = cache.get(text)
        print(f"文本 {i+1} 缓存结果: {'命中' if result is not None else '未命中'}")
    
    print("\n3. 测试添加到缓存")
    # 为每个文本生成随机向量
    test_vectors = []
    for i, text in enumerate(test_texts):
        # 生成随机向量
        vector = np.random.random(128).astype('float32')
        test_vectors.append(vector)
        
        # 添加到缓存
        cache.put(text, vector)
        print(f"文本 {i+1} 已添加到缓存")
    
    print("\n4. 测试缓存命中")
    for i, text in enumerate(test_texts):
        start_time = time.time()
        result = cache.get(text)
        query_time = time.time() - start_time
        
        print(f"文本 {i+1} 缓存结果: {'命中' if result is not None else '未命中'}, 查询时间: {query_time:.6f}秒")
        
        if result is not None:
            # 验证向量是否正确
            original_vector = test_vectors[i]
            is_equal = np.array_equal(result, original_vector)
            print(f"  向量匹配: {is_equal}")
            if not is_equal:
                print(f"  原始向量前5个元素: {original_vector[:5]}")
                print(f"  缓存向量前5个元素: {result[:5]}")
    
    print("\n5. 测试LRU逻辑")
    # 添加更多文本，超过最大内存缓存大小
    print(f"添加 {cache.max_memory_size + 10} 个新文本到缓存...")
    for i in range(cache.max_memory_size + 10):
        text = f"LRU测试文本 {i}"
        vector = np.random.random(128).astype('float32')
        cache.put(text, vector)
    
    # 检查第一个文本是否还在内存缓存中
    # 注意：这个测试可能不准确，因为我们无法直接检查内存缓存的内容
    # 但我们可以通过时间差来推断
    start_time = time.time()
    result = cache.get(test_texts[0])
    query_time = time.time() - start_time
    
    print(f"第一个文本缓存结果: {'命中' if result is not None else '未命中'}, 查询时间: {query_time:.6f}秒")
    print("(如果查询时间明显长于之前，可能表示从文件缓存中加载，而不是内存缓存)")
    
    print("\n6. 测试缓存统计")
    stats = cache.get_stats()
    print("缓存统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n7. 测试清空内存缓存")
    cache.clear_memory_cache()
    print("内存缓存已清空")
    
    # 验证文本仍然可以从文件缓存中获取
    for i, text in enumerate(test_texts):
        start_time = time.time()
        result = cache.get(text)
        query_time = time.time() - start_time
        
        print(f"文本 {i+1} 缓存结果: {'命中' if result is not None else '未命中'}, 查询时间: {query_time:.6f}秒")
    
    print("\n8. 测试清空所有缓存")
    cache.clear_all_cache()
    print("所有缓存已清空")
    
    # 验证文本无法从缓存中获取
    for i, text in enumerate(test_texts):
        result = cache.get(text)
        print(f"文本 {i+1} 缓存结果: {'命中' if result is not None else '未命中'}")
    
    print("\n9. 测试缓存清理")
    # 添加一些文本到缓存
    for i, text in enumerate(test_texts):
        cache.put(text, test_vectors[i])
        print(f"文本 {i+1} 已重新添加到缓存")
    
    # 模拟清理过期缓存
    print("执行缓存清理（模拟过期）...")
    # 这里我们不等待实际过期，而是直接调用清理函数
    # 在实际使用中，应该设置合理的max_age_days参数
    cleaned = cache.cleanup(max_age_days=0)  # 0表示所有缓存都"过期"
    print(f"清理了 {cleaned} 个过期条目")
    
    # 清理测试目录
    print("\n10. 清理测试文件")
    try:
        shutil.rmtree(test_cache_dir)
        print(f"已删除测试缓存目录: {test_cache_dir}")
    except Exception as e:
        print(f"清理测试目录失败: {e}")
    
    print("\n===== Embedding缓存测试完成 =====")
    return True

if __name__ == "__main__":
    test_embedding_cache() 