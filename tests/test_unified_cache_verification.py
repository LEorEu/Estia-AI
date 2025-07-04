#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证统一缓存系统是否真正工作

这个测试会：
1. 清空所有缓存
2. 使用全新的文本进行测试
3. 验证缓存命中情况
"""

import os
import sys
import time
import numpy as np
import uuid

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_unified_cache_verification():
    """验证统一缓存是否真正工作"""
    print("🧪 验证统一缓存系统是否真正工作...")
    
    try:
        from core.memory.embedding import TextVectorizer
        from core.memory.caching.cache_manager import UnifiedCacheManager
        
        # 初始化统一缓存管理器
        unified_cache = UnifiedCacheManager.get_instance()
        
        # 清空所有缓存
        print("  🗑️ 清空所有缓存...")
        unified_cache.clear_all()
        
        # 初始化TextVectorizer
        vectorizer = TextVectorizer(
            model_type="sentence-transformers",
            model_name="paraphrase-multilingual-MiniLM-L12-v2",
            use_cache=True
        )
        
        # 清空向量化器缓存
        vectorizer.clear_cache()
        
        # 生成唯一的测试文本（确保不在缓存中）
        unique_id = str(uuid.uuid4())[:8]
        test_texts = [
            f"这是第一个独特的测试文本{unique_id}，用于验证统一缓存功能",
            f"This is a unique test text {unique_id} for verifying unified cache functionality",
            f"这是另一个独特的测试文本{unique_id}，与第一个有一些相似之处"
        ]
        
        print(f"  📝 使用唯一测试文本 (ID: {unique_id})...")
        
        # 检查初始缓存状态
        initial_stats = unified_cache.get_stats()
        print(f"    📊 初始缓存状态: {initial_stats.get('total_hits', 0)} 命中, {initial_stats.get('total_misses', 0)} 未命中")
        
        # 第一次编码（应该写入缓存）
        print("  🔄 第一次编码（应该写入缓存）...")
        start_time = time.time()
        vectors1 = vectorizer.encode(test_texts)
        first_encode_time = time.time() - start_time
        
        # 检查第一次编码后的缓存状态
        after_first_stats = unified_cache.get_stats()
        print(f"    📊 第一次编码后: {after_first_stats.get('total_hits', 0)} 命中, {after_first_stats.get('total_misses', 0)} 未命中")
        print(f"    ⏱️ 第一次编码耗时: {first_encode_time:.4f}秒")
        
        # 第二次编码（应该从缓存获取）
        print("  🔄 第二次编码（应该从缓存获取）...")
        start_time = time.time()
        vectors2 = vectorizer.encode(test_texts)
        second_encode_time = time.time() - start_time
        
        # 检查第二次编码后的缓存状态
        after_second_stats = unified_cache.get_stats()
        print(f"    📊 第二次编码后: {after_second_stats.get('total_hits', 0)} 命中, {after_second_stats.get('total_misses', 0)} 未命中")
        print(f"    ⏱️ 第二次编码耗时: {second_encode_time:.4f}秒")
        
        # 验证向量一致性
        is_consistent = np.array_equal(vectors1, vectors2)
        print(f"    ✅ 向量一致性: {is_consistent}")
        
        # 计算缓存命中情况
        hits_before_second = after_first_stats.get('total_hits', 0)
        hits_after_second = after_second_stats.get('total_hits', 0)
        actual_hits = hits_after_second - hits_before_second
        
        print(f"    📊 实际缓存命中: {actual_hits}")
        
        # 计算缓存加速比
        if second_encode_time > 0:
            speedup = first_encode_time / second_encode_time
            print(f"    📊 缓存加速比: {speedup:.2f}倍")
        else:
            print(f"    📊 缓存加速比: 无法计算（第二次编码时间为0）")
        
        # 检查TextVectorizer缓存统计
        vectorizer_stats = vectorizer.get_cache_stats()
        print(f"    📊 向量化器缓存类型: {vectorizer_stats.get('cache_type', 'unknown')}")
        
        # 验证结果
        success = True
        issues = []
        
        if actual_hits == 0:
            issues.append("❌ 没有检测到缓存命中")
            success = False
        
        if not is_consistent:
            issues.append("❌ 向量不一致")
            success = False
        
        if vectorizer_stats.get('cache_type') != 'unified':
            issues.append("❌ 向量化器未使用统一缓存")
            success = False
        
        if success:
            print("    ✅ 统一缓存验证成功！")
        else:
            print("    ❌ 统一缓存验证失败:")
            for issue in issues:
                print(f"      {issue}")
        
        return success
        
    except Exception as e:
        print(f"    ❌ 统一缓存验证失败: {e}")
        return False

def test_cache_registration():
    """测试缓存注册情况"""
    print("🧪 测试缓存注册情况...")
    
    try:
        from core.memory.caching.cache_manager import UnifiedCacheManager
        
        unified_cache = UnifiedCacheManager.get_instance()
        
        # 获取已注册的缓存
        registered_caches = list(unified_cache.caches.keys())
        print(f"  📋 已注册的缓存: {registered_caches}")
        
        # 检查是否有向量缓存适配器
        if 'embedding_cache' in registered_caches:
            print("    ✅ 向量缓存适配器已注册")
        else:
            print("    ❌ 向量缓存适配器未注册")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ❌ 缓存注册测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始统一缓存系统验证")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("缓存注册情况", test_cache_registration()))
    test_results.append(("统一缓存验证", test_unified_cache_verification()))
    
    print("\n" + "=" * 60)
    print("📋 统一缓存验证结果汇总:")
    
    passed_tests = 0
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\n🎯 总体结果: {passed_tests}/{len(test_results)} 个测试通过")
    
    if passed_tests == len(test_results):
        print("🎉 统一缓存系统验证成功！")
        print("✅ 缓存注册正常")
        print("✅ 缓存命中正常")
        print("✅ 系统工作正常")
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
    
    return passed_tests == len(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 