#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一缓存系统测试

测试三个缓存系统的适配器是否正常工作：
1. EnhancedMemoryCacheAdapter - 向量缓存适配器
2. DbCacheAdapter - 数据库缓存适配器  
3. SmartRetrieverCacheAdapter - 检索缓存适配器
"""

import sys
import os
import time
import numpy as np
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_enhanced_memory_cache_adapter():
    """测试向量缓存适配器"""
    print("🧪 测试向量缓存适配器...")
    
    try:
        from core.memory.embedding.cache import EnhancedMemoryCache
        from core.memory.caching.cache_adapters import EnhancedMemoryCacheAdapter
        from core.memory.caching.cache_manager import UnifiedCacheManager
        
        # 创建原始缓存
        original_cache = EnhancedMemoryCache(hot_capacity=10, warm_capacity=20)
        
        # 创建适配器
        adapter = EnhancedMemoryCacheAdapter(original_cache)
        
        # 注册到统一管理器
        manager = UnifiedCacheManager.get_instance()
        manager.register_cache(adapter)
        
        # 测试基本操作
        test_text = "这是一个测试文本"
        test_vector = np.random.rand(1024).astype(np.float32)
        
        # 测试写入
        adapter.put(test_text, test_vector, {"weight": 1.0})
        print("  ✅ 向量缓存写入成功")
        
        # 测试读取
        retrieved_vector = adapter.get(test_text)
        if retrieved_vector is not None and np.array_equal(test_vector, retrieved_vector):
            print("  ✅ 向量缓存读取成功")
        else:
            print("  ❌ 向量缓存读取失败")
            return False
        
        # 测试统计
        stats = adapter.get_stats()
        print(f"  📊 向量缓存统计: {stats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 向量缓存适配器测试失败: {e}")
        return False

def test_db_cache_adapter():
    """测试数据库缓存适配器"""
    print("🧪 测试数据库缓存适配器...")
    
    try:
        from core.memory.init.db_manager import DatabaseManager
        from core.memory.memory_cache.cache_manager import CacheManager
        from core.memory.caching.cache_adapters import DbCacheAdapter
        from core.memory.caching.cache_manager import UnifiedCacheManager
        
        # 创建数据库管理器
        db_manager = DatabaseManager()
        if not db_manager.connect():
            print("  ❌ 数据库连接失败")
            return False
        
        # 创建原始缓存管理器
        original_cache = CacheManager(db_manager)
        original_cache.initialize_cache()
        
        # 创建适配器
        adapter = DbCacheAdapter(original_cache)
        
        # 注册到统一管理器
        manager = UnifiedCacheManager.get_instance()
        manager.register_cache(adapter)
        
        # 测试基本操作
        test_memory_id = "test_memory_001"
        test_data = {"content": "测试记忆内容", "weight": 5.0}
        
        # 测试写入（通过原始缓存管理器）
        original_cache.record_memory_access(test_memory_id, 1.0)
        print("  ✅ 数据库缓存写入成功")
        
        # 测试读取
        cached_memories = adapter.get_cached_memories('hot', limit=5)
        print(f"  📊 热缓存记忆数量: {len(cached_memories)}")
        
        # 测试统计
        stats = adapter.get_stats()
        print(f"  📊 数据库缓存统计: {stats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 数据库缓存适配器测试失败: {e}")
        return False

def test_smart_retriever_cache_adapter():
    """测试检索缓存适配器"""
    print("🧪 测试检索缓存适配器...")
    
    try:
        from core.memory.init.db_manager import DatabaseManager
        from core.memory.retrieval.smart_retriever import SmartRetriever
        from core.memory.caching.cache_adapters import SmartRetrieverCacheAdapter
        from core.memory.caching.cache_manager import UnifiedCacheManager
        
        # 创建数据库管理器
        db_manager = DatabaseManager()
        if not db_manager.connect():
            print("  ❌ 数据库连接失败")
            return False
        
        # 创建SmartRetriever
        retriever = SmartRetriever(db_manager)
        
        # 创建适配器
        adapter = SmartRetrieverCacheAdapter(retriever)
        
        # 注册到统一管理器
        manager = UnifiedCacheManager.get_instance()
        manager.register_cache(adapter)
        
        # 测试基本操作
        test_key = "test_search_query"
        test_result = {"memories": [{"id": "1", "content": "测试记忆"}]}
        
        # 测试写入
        adapter.put(test_key, test_result, {"query_type": "keyword"})
        print("  ✅ 检索缓存写入成功")
        
        # 测试读取
        retrieved_result = adapter.get(test_key)
        if retrieved_result and retrieved_result == test_result:
            print("  ✅ 检索缓存读取成功")
        else:
            print("  ❌ 检索缓存读取失败")
            return False
        
        # 测试统计
        stats = adapter.get_stats()
        print(f"  📊 检索缓存统计: {stats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 检索缓存适配器测试失败: {e}")
        return False

def test_unified_cache_manager():
    """测试统一缓存管理器"""
    print("🧪 测试统一缓存管理器...")
    
    try:
        from core.memory.caching.cache_manager import UnifiedCacheManager
        
        # 获取统一缓存管理器实例
        manager = UnifiedCacheManager.get_instance()
        
        # 测试统计
        stats = manager.get_stats()
        print(f"  📊 统一缓存管理器统计: {stats}")
        
        # 测试缓存注册情况
        registered_caches = list(manager.caches.keys())
        print(f"  📋 已注册的缓存: {registered_caches}")
        
        # 测试跨缓存操作
        test_key = "unified_test_key"
        test_value = {"data": "统一测试数据"}
        
        # 写入到所有缓存
        manager.put(test_key, test_value, {"source": "unified_test"})
        print("  ✅ 统一缓存写入成功")
        
        # 从所有缓存读取
        retrieved_value = manager.get(test_key)
        if retrieved_value and retrieved_value == test_value:
            print("  ✅ 统一缓存读取成功")
        else:
            print("  ❌ 统一缓存读取失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ 统一缓存管理器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始统一缓存系统测试")
    print("=" * 50)
    
    test_results = []
    
    # 测试各个适配器
    test_results.append(("向量缓存适配器", test_enhanced_memory_cache_adapter()))
    test_results.append(("数据库缓存适配器", test_db_cache_adapter()))
    test_results.append(("检索缓存适配器", test_smart_retriever_cache_adapter()))
    test_results.append(("统一缓存管理器", test_unified_cache_manager()))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📋 测试结果汇总:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！统一缓存系统工作正常")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 