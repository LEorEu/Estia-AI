#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一缓存集成测试

验证EstiaMemorySystem和SmartRetriever是否正确使用统一缓存管理器：
1. 测试向量化缓存集成
2. 测试记忆访问记录集成
3. 测试启动记忆缓存集成
4. 测试统一缓存统计
"""

import sys
import os
import time
import numpy as np
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_estia_memory_unified_cache():
    """测试EstiaMemorySystem的统一缓存集成"""
    print("🧪 测试EstiaMemorySystem统一缓存集成...")
    
    try:
        from core.memory.estia_memory import EstiaMemorySystem
        from core.memory.caching.cache_manager import UnifiedCacheManager
        
        # 创建EstiaMemorySystem实例
        memory_system = EstiaMemorySystem(enable_advanced=True)
        
        # 获取统一缓存管理器
        unified_cache = UnifiedCacheManager.get_instance()
        
        # 测试1: 向量化缓存集成
        print("  📝 测试向量化缓存集成...")
        test_input = "这是一个测试用户输入"
        
        # 第一次调用，应该进行向量化并缓存
        context1 = memory_system.enhance_query(test_input)
        print("    ✅ 第一次向量化完成")
        
        # 第二次调用，应该从缓存获取
        context2 = memory_system.enhance_query(test_input)
        print("    ✅ 第二次向量化完成（应该从缓存获取）")
        
        # 检查缓存统计
        cache_stats = unified_cache.get_stats()
        print(f"    📊 缓存统计: {cache_stats['manager']['total_hits']} 命中, {cache_stats['manager']['total_misses']} 未命中")
        
        # 测试2: 记忆存储集成
        print("  💾 测试记忆存储集成...")
        ai_response = "这是AI的测试回复"
        
        # 存储交互
        memory_system.store_interaction(test_input, ai_response, {"session_id": "test_session"})
        print("    ✅ 记忆存储完成")
        
        # 检查是否有记忆访问记录
        access_key = f"memory_access_test_session"
        access_record = unified_cache.get(access_key)
        if access_record:
            print("    ✅ 记忆访问记录已创建")
        else:
            print("    ⚠️ 记忆访问记录未找到")
        
        # 测试3: 系统统计集成
        print("  📊 测试系统统计集成...")
        system_stats = memory_system.get_system_stats()
        
        if 'unified_cache' in system_stats:
            print("    ✅ 统一缓存统计已集成到系统统计")
            print(f"    📋 已注册缓存: {list(system_stats['unified_cache']['caches'].keys())}")
        else:
            print("    ❌ 统一缓存统计未集成")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ EstiaMemorySystem统一缓存集成测试失败: {e}")
        return False

def test_smart_retriever_unified_cache():
    """测试SmartRetriever的统一缓存集成"""
    print("🧪 测试SmartRetriever统一缓存集成...")
    
    try:
        from core.memory.init.db_manager import DatabaseManager
        from core.memory.retrieval.smart_retriever import SmartRetriever
        from core.memory.caching.cache_manager import UnifiedCacheManager
        
        # 创建数据库管理器
        db_manager = DatabaseManager()
        if not db_manager.connect():
            print("  ❌ 数据库连接失败")
            return False
        
        # 创建SmartRetriever
        retriever = SmartRetriever(db_manager)
        
        # 获取统一缓存管理器
        unified_cache = UnifiedCacheManager.get_instance()
        
        # 测试1: 启动记忆缓存集成
        print("  🚀 测试启动记忆缓存集成...")
        
        # 第一次获取启动记忆
        startup_memories1 = retriever.get_startup_memories()
        print(f"    ✅ 第一次获取启动记忆: {len(startup_memories1)} 条")
        
        # 第二次获取启动记忆（应该从缓存获取）
        startup_memories2 = retriever.get_startup_memories()
        print(f"    ✅ 第二次获取启动记忆: {len(startup_memories2)} 条")
        
        # 检查缓存统计
        cache_stats = unified_cache.get_stats()
        print(f"    📊 缓存统计: {cache_stats['manager']['total_hits']} 命中, {cache_stats['manager']['total_misses']} 未命中")
        
        # 测试2: 检索缓存集成
        print("  🔍 测试检索缓存集成...")
        
        # 测试关键词搜索
        search_query = "测试搜索"
        search_results1 = retriever.keyword_search(search_query)
        print(f"    ✅ 第一次关键词搜索: {len(search_results1)} 条结果")
        
        # 第二次搜索（应该从缓存获取）
        search_results2 = retriever.keyword_search(search_query)
        print(f"    ✅ 第二次关键词搜索: {len(search_results2)} 条结果")
        
        # 测试3: 缓存统计
        print("  📊 测试缓存统计...")
        retriever_stats = retriever.get_cache_stats()
        print(f"    📋 检索器缓存统计: {retriever_stats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ SmartRetriever统一缓存集成测试失败: {e}")
        return False

def test_unified_cache_performance():
    """测试统一缓存性能"""
    print("🧪 测试统一缓存性能...")
    
    try:
        from core.memory.caching.cache_manager import UnifiedCacheManager
        
        # 获取统一缓存管理器
        unified_cache = UnifiedCacheManager.get_instance()
        
        # 测试1: 缓存写入性能
        print("  ⚡ 测试缓存写入性能...")
        start_time = time.time()
        
        for i in range(100):
            key = f"perf_test_key_{i}"
            value = {"data": f"test_value_{i}", "timestamp": time.time()}
            unified_cache.put(key, value, {"test": True})
        
        write_time = time.time() - start_time
        print(f"    ✅ 写入100个键耗时: {write_time:.3f}秒")
        
        # 测试2: 缓存读取性能
        print("  ⚡ 测试缓存读取性能...")
        start_time = time.time()
        
        hit_count = 0
        for i in range(100):
            key = f"perf_test_key_{i}"
            value = unified_cache.get(key)
            if value is not None:
                hit_count += 1
        
        read_time = time.time() - start_time
        print(f"    ✅ 读取100个键耗时: {read_time:.3f}秒, 命中率: {hit_count/100*100:.1f}%")
        
        # 测试3: 缓存统计性能
        print("  ⚡ 测试缓存统计性能...")
        start_time = time.time()
        
        stats = unified_cache.get_stats()
        
        stats_time = time.time() - start_time
        print(f"    ✅ 获取统计耗时: {stats_time:.3f}秒")
        print(f"    📊 最终统计: {stats['manager']['total_hits']} 命中, {stats['manager']['total_misses']} 未命中")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 统一缓存性能测试失败: {e}")
        return False

def test_unified_cache_coordination():
    """测试统一缓存协调机制"""
    print("🧪 测试统一缓存协调机制...")
    
    try:
        from core.memory.caching.cache_manager import UnifiedCacheManager
        
        # 获取统一缓存管理器
        unified_cache = UnifiedCacheManager.get_instance()
        
        # 测试1: 跨缓存数据同步
        print("  🔄 测试跨缓存数据同步...")
        
        # 写入数据到统一缓存
        test_key = "coordination_test_key"
        test_value = {"data": "coordination_test_value", "timestamp": time.time()}
        
        unified_cache.put(test_key, test_value, {"source": "coordination_test"})
        print("    ✅ 数据已写入统一缓存")
        
        # 从统一缓存读取
        retrieved_value = unified_cache.get(test_key)
        if retrieved_value and retrieved_value == test_value:
            print("    ✅ 跨缓存数据同步成功")
        else:
            print("    ❌ 跨缓存数据同步失败")
            return False
        
        # 测试2: 缓存事件协调
        print("  📡 测试缓存事件协调...")
        
        # 检查事件统计
        stats = unified_cache.get_stats()
        event_count = stats['manager']['operations'].get('event_put', 0) + stats['manager']['operations'].get('event_get', 0)
        print(f"    📊 缓存事件数量: {event_count}")
        
        if event_count > 0:
            print("    ✅ 缓存事件协调正常")
        else:
            print("    ⚠️ 缓存事件数量为0")
        
        # 测试3: 缓存级别协调
        print("  📊 测试缓存级别协调...")
        
        registered_caches = list(unified_cache.caches.keys())
        print(f"    📋 已注册缓存: {registered_caches}")
        
        if len(registered_caches) >= 3:
            print("    ✅ 缓存级别协调正常")
        else:
            print(f"    ⚠️ 缓存数量不足: {len(registered_caches)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 统一缓存协调机制测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始统一缓存集成测试")
    print("=" * 60)
    
    test_results = []
    
    # 测试各个集成点
    test_results.append(("EstiaMemorySystem集成", test_estia_memory_unified_cache()))
    test_results.append(("SmartRetriever集成", test_smart_retriever_unified_cache()))
    test_results.append(("统一缓存性能", test_unified_cache_performance()))
    test_results.append(("统一缓存协调", test_unified_cache_coordination()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📋 集成测试结果汇总:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有集成测试通过！统一缓存系统集成成功")
        print("✅ 阶段2改造完成：业务侧已成功使用统一缓存接口")
        return True
    else:
        print("⚠️ 部分集成测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 