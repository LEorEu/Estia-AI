#!/usr/bin/env python3
"""
Estia-AI 缓存性能修复测试脚本
重点解决缓存性能不稳定问题
"""

import time
import logging
from pathlib import Path
import sys
import os

# 设置项目根目录
sys.path.insert(0, str(Path(__file__).parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s:%(message)s'
)

def test_cache_performance_fix():
    """测试缓存性能修复"""
    print("🚀 Estia-AI 缓存性能深度修复测试")
    print("=" * 60)
    
    results = {}
    
    # 1. 测试缓存预热
    print("🔧 测试缓存预热...")
    try:
        from core.memory.estia_memory_v5 import EstiaMemorySystem
        
        # 创建新的系统实例
        system = EstiaMemorySystem()
        
        # 预热缓存 - 添加多个测试记忆
        warmup_queries = [
            "缓存预热测试1",
            "缓存预热测试2", 
            "缓存预热测试3",
            "缓存预热测试4",
            "缓存预热测试5"
        ]
        
        print(f"📊 准备预热 {len(warmup_queries)} 个查询...")
        
        for i, query in enumerate(warmup_queries):
            system.enhance_query(query)
            print(f"✅ 预热完成 {i+1}/{len(warmup_queries)}")
            
        results["cache_warmup"] = True
        print("✅ 缓存预热成功")
        
    except Exception as e:
        results["cache_warmup"] = False
        print(f"❌ 缓存预热失败: {e}")
    
    # 2. 测试缓存命中率
    print("\n🎯 测试缓存命中率...")
    try:
        # 测试重复查询的性能
        test_query = "重复查询性能测试"
        
        # 第一次查询 - 应该较慢
        start = time.perf_counter()
        result1 = system.enhance_query(test_query)
        time1 = (time.perf_counter() - start) * 1000
        
        # 第二次查询 - 应该很快（缓存命中）
        start = time.perf_counter()
        result2 = system.enhance_query(test_query)
        time2 = (time.perf_counter() - start) * 1000
        
        # 第三次查询 - 确认缓存稳定
        start = time.perf_counter()
        result3 = system.enhance_query(test_query)
        time3 = (time.perf_counter() - start) * 1000
        
        print(f"第一次查询: {time1:.2f}ms")
        print(f"第二次查询: {time2:.2f}ms")
        print(f"第三次查询: {time3:.2f}ms")
        
        # 计算缓存效果
        if time1 > 0:
            improvement_2 = time1 / max(time2, 0.001)
            improvement_3 = time1 / max(time3, 0.001)
            avg_improvement = (improvement_2 + improvement_3) / 2
            
            print(f"第二次提升: {improvement_2:.1f}x")
            print(f"第三次提升: {improvement_3:.1f}x")
            print(f"平均提升: {avg_improvement:.1f}x")
            
            # 判断缓存性能是否合格
            if avg_improvement >= 5.0:
                results["cache_hit_rate"] = True
                print("✅ 缓存命中率良好")
            else:
                results["cache_hit_rate"] = False
                print("⚠️ 缓存命中率需要改进")
        else:
            results["cache_hit_rate"] = False
            print("❌ 缓存性能测试失败")
            
    except Exception as e:
        results["cache_hit_rate"] = False
        print(f"❌ 缓存命中率测试失败: {e}")
    
    # 3. 测试缓存统计
    print("\n📊 测试缓存统计...")
    try:
        # 获取缓存统计信息
        cache_stats = system.get_cache_stats()
        
        print(f"缓存统计信息:")
        for key, value in cache_stats.items():
            print(f"  {key}: {value}")
            
        # 检查是否有缓存命中
        if cache_stats.get('hit_count', 0) > 0:
            hit_rate = cache_stats.get('hit_count', 0) / max(cache_stats.get('total_requests', 1), 1)
            print(f"缓存命中率: {hit_rate:.1%}")
            
            if hit_rate >= 0.5:  # 50%以上命中率
                results["cache_stats"] = True
                print("✅ 缓存统计正常")
            else:
                results["cache_stats"] = False
                print("⚠️ 缓存命中率偏低")
        else:
            results["cache_stats"] = False
            print("❌ 缓存无命中记录")
            
    except Exception as e:
        results["cache_stats"] = False
        print(f"❌ 缓存统计测试失败: {e}")
    
    # 4. 测试缓存清理和重建
    print("\n🔄 测试缓存清理和重建...")
    try:
        # 清理缓存
        system.clear_cache()
        print("✅ 缓存清理成功")
        
        # 重新预热
        test_query = "缓存重建测试"
        system.enhance_query(test_query)
        system.enhance_query(test_query)  # 第二次应该更快
        
        results["cache_rebuild"] = True
        print("✅ 缓存重建成功")
        
    except Exception as e:
        results["cache_rebuild"] = False
        print(f"❌ 缓存重建失败: {e}")
    
    # 5. 批量性能测试
    print("\n⚡ 批量性能测试...")
    try:
        batch_queries = [
            "批量测试1",
            "批量测试2", 
            "批量测试3",
            "批量测试4",
            "批量测试5"
        ]
        
        # 第一轮 - 建立缓存
        print("第一轮查询（建立缓存）...")
        first_round_times = []
        for query in batch_queries:
            start = time.perf_counter()
            system.enhance_query(query)
            elapsed = (time.perf_counter() - start) * 1000
            first_round_times.append(elapsed)
            
        # 第二轮 - 测试缓存效果
        print("第二轮查询（测试缓存）...")
        second_round_times = []
        for query in batch_queries:
            start = time.perf_counter()
            system.enhance_query(query)
            elapsed = (time.perf_counter() - start) * 1000
            second_round_times.append(elapsed)
            
        # 计算批量性能提升
        avg_first = sum(first_round_times) / len(first_round_times)
        avg_second = sum(second_round_times) / len(second_round_times)
        
        if avg_first > 0:
            batch_improvement = avg_first / max(avg_second, 0.001)
            
            print(f"第一轮平均: {avg_first:.2f}ms")
            print(f"第二轮平均: {avg_second:.2f}ms")
            print(f"批量提升: {batch_improvement:.1f}x")
            
            if batch_improvement >= 3.0:
                results["batch_performance"] = True
                print("✅ 批量性能良好")
            else:
                results["batch_performance"] = False
                print("⚠️ 批量性能需要改进")
        else:
            results["batch_performance"] = False
            print("❌ 批量性能测试失败")
            
    except Exception as e:
        results["batch_performance"] = False
        print(f"❌ 批量性能测试失败: {e}")
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 缓存性能修复测试结果")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n成功率: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("✅ 缓存性能修复成功")
        status = "成功"
    elif success_rate >= 60:
        print("⚠️ 缓存性能部分修复")
        status = "部分成功"
    else:
        print("❌ 缓存性能修复失败")
        status = "失败"
    
    print(f"\n🎯 缓存性能修复测试完成！{status}")
    
    return results

if __name__ == "__main__":
    test_cache_performance_fix()