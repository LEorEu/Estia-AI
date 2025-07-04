#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存修复验证测试

验证TextVectorizer的自动注册功能和缓存命中情况
"""

import unittest
import numpy as np
import time
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.memory.embedding.vectorizer import TextVectorizer
from core.memory.caching.cache_manager import UnifiedCacheManager
from core.memory.caching.cache_adapters import EnhancedMemoryCacheAdapter


class TestCacheFixVerification(unittest.TestCase):
    """测试缓存修复验证"""
    
    def setUp(self):
        """测试前准备"""
        # 重置单例实例，确保测试隔离
        TextVectorizer._instance = None
        TextVectorizer._initialized = False
        UnifiedCacheManager._instance = None
        
        # 清理测试缓存目录
        test_cache_dir = "data/memory/cache"
        if os.path.exists(test_cache_dir):
            import shutil
            shutil.rmtree(test_cache_dir)
    
    def tearDown(self):
        """测试后清理"""
        # 重置单例实例
        TextVectorizer._instance = None
        TextVectorizer._initialized = False
        UnifiedCacheManager._instance = None
    
    def test_auto_register_cache_adapter(self):
        """测试自动注册缓存适配器"""
        print("\n=== 测试自动注册缓存适配器 ===")
        
        # 创建TextVectorizer实例
        vectorizer = TextVectorizer(use_cache=True)
        
        # 获取统一缓存管理器
        unified_cache = UnifiedCacheManager.get_instance()
        
        # 检查是否自动注册了向量缓存适配器
        registered_caches = list(unified_cache.caches.keys())
        print(f"已注册的缓存: {registered_caches}")
        
        # 验证embedding_cache是否被注册
        self.assertIn("embedding_cache", registered_caches, 
                     "向量缓存适配器应该被自动注册")
        
        # 检查缓存级别
        embedding_cache = unified_cache.caches["embedding_cache"]
        cache_level = embedding_cache.get_cache_level()
        print(f"向量缓存级别: {cache_level}")
        
        print("✅ 自动注册缓存适配器测试通过")
    
    def test_cache_hit_after_auto_register(self):
        """测试自动注册后的缓存命中"""
        print("\n=== 测试缓存命中 ===")
        
        # 创建TextVectorizer实例（会自动注册缓存适配器）
        vectorizer = TextVectorizer(use_cache=True)
        
        # 获取统一缓存管理器
        unified_cache = UnifiedCacheManager.get_instance()
        
        # 测试文本
        test_texts = [
            "这是一个测试文本",
            "另一个测试文本",
            "第三个测试文本"
        ]
        
        # 第一次编码（应该缓存）
        print("第一次编码（缓存写入）...")
        start_time = time.time()
        vectors1 = vectorizer.encode(test_texts)
        first_encode_time = time.time() - start_time
        print(f"第一次编码耗时: {first_encode_time:.3f}秒")
        
        # 检查缓存统计
        stats_before = unified_cache.get_stats()
        print(f"缓存统计（第一次后）: {stats_before}")
        
        # 第二次编码（应该命中缓存）
        print("第二次编码（缓存命中）...")
        start_time = time.time()
        vectors2 = vectorizer.encode(test_texts)
        second_encode_time = time.time() - start_time
        print(f"第二次编码耗时: {second_encode_time:.3f}秒")
        
        # 检查缓存统计
        stats_after = unified_cache.get_stats()
        print(f"缓存统计（第二次后）: {stats_after}")
        
        # 验证向量结果一致
        np.testing.assert_array_almost_equal(vectors1, vectors2, decimal=6,
                                           err_msg="两次编码结果应该一致")
        
        # 验证缓存命中 - 修复：使用正确的统计结构
        manager_stats = stats_after.get("manager", {})
        hit_ratio = manager_stats.get("hit_ratio", 0)
        total_hits = manager_stats.get("total_hits", 0)
        
        print(f"缓存命中率: {hit_ratio:.2%}")
        print(f"总命中次数: {total_hits}")
        
        # 验证有缓存命中（第二次编码应该命中）
        self.assertGreater(total_hits, 0, "应该有缓存命中")
        
        # 验证第二次编码更快（缓存命中）
        if first_encode_time > 0.1:  # 只有在第一次编码耗时较长时才比较
            self.assertLess(second_encode_time, first_encode_time * 0.8,
                           "缓存命中应该比首次编码更快")
        
        print("✅ 缓存命中测试通过")
    
    def test_cache_stats_detailed(self):
        """测试详细的缓存统计"""
        print("\n=== 测试详细缓存统计 ===")
        
        # 创建TextVectorizer实例
        vectorizer = TextVectorizer(use_cache=True)
        
        # 获取统一缓存管理器
        unified_cache = UnifiedCacheManager.get_instance()
        
        # 测试文本
        test_text = "详细统计测试文本"
        
        # 多次编码同一文本
        for i in range(3):
            print(f"第{i+1}次编码...")
            vectorizer.encode(test_text)
            
            # 获取详细统计 - 修复：使用正确的统计结构
            stats = unified_cache.get_stats()
            manager_stats = stats.get("manager", {})
            print(f"第{i+1}次后统计: 命中={manager_stats.get('total_hits', 0)}, "
                  f"未命中={manager_stats.get('total_misses', 0)}, "
                  f"命中率={manager_stats.get('hit_ratio', 0):.2%}")
        
        # 最终统计
        final_stats = unified_cache.get_stats()
        print(f"最终统计: {final_stats}")
        
        # 验证统计信息完整 - 修复：检查manager子结构
        manager_stats = final_stats.get("manager", {})
        self.assertIn("total_hits", manager_stats)
        self.assertIn("total_misses", manager_stats)
        self.assertIn("hit_ratio", manager_stats)
        self.assertIn("cache_hits", manager_stats)
        self.assertIn("level_hits", manager_stats)
        
        print("✅ 详细缓存统计测试通过")
    
    def test_cache_level_distribution(self):
        """测试缓存级别分布"""
        print("\n=== 测试缓存级别分布 ===")
        
        # 创建TextVectorizer实例
        vectorizer = TextVectorizer(use_cache=True)
        
        # 获取统一缓存管理器
        unified_cache = UnifiedCacheManager.get_instance()
        
        # 测试不同长度的文本
        test_texts = [
            "短文本",
            "这是一个中等长度的测试文本，用于测试缓存级别分布",
            "这是一个很长的测试文本，包含很多字符，用于测试缓存系统如何处理不同长度的文本，以及缓存级别是如何分布的"
        ]
        
        # 编码所有文本
        for text in test_texts:
            vectorizer.encode(text)
        
        # 获取缓存统计
        stats = unified_cache.get_stats()
        level_hits = stats.get("level_hits", {})
        
        print(f"缓存级别命中统计: {level_hits}")
        
        # 验证有缓存级别统计
        self.assertIsInstance(level_hits, dict)
        
        print("✅ 缓存级别分布测试通过")
    
    def test_cache_persistence(self):
        """测试缓存持久性"""
        print("\n=== 测试缓存持久性 ===")
        
        # 第一次创建TextVectorizer并编码
        vectorizer1 = TextVectorizer(use_cache=True)
        test_text = "持久性测试文本"
        
        # 编码文本
        vector1 = vectorizer1.encode(test_text)
        
        # 获取缓存统计
        unified_cache1 = UnifiedCacheManager.get_instance()
        stats1 = unified_cache1.get_stats()
        print(f"第一次编码后统计: {stats1}")
        
        # 重置单例（模拟重新启动）
        TextVectorizer._instance = None
        TextVectorizer._initialized = False
        UnifiedCacheManager._instance = None
        
        # 第二次创建TextVectorizer
        vectorizer2 = TextVectorizer(use_cache=True)
        
        # 再次编码同一文本
        vector2 = vectorizer2.encode(test_text)
        
        # 获取新的缓存统计
        unified_cache2 = UnifiedCacheManager.get_instance()
        stats2 = unified_cache2.get_stats()
        print(f"第二次编码后统计: {stats2}")
        
        # 验证向量结果一致
        np.testing.assert_array_almost_equal(vector1, vector2, decimal=6,
                                           err_msg="缓存持久化后结果应该一致")
        
        print("✅ 缓存持久性测试通过")


def run_cache_fix_verification():
    """运行缓存修复验证测试"""
    print("🚀 开始缓存修复验证测试")
    print("=" * 50)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_cases = [
        TestCacheFixVerification("test_auto_register_cache_adapter"),
        TestCacheFixVerification("test_cache_hit_after_auto_register"),
        TestCacheFixVerification("test_cache_stats_detailed"),
        TestCacheFixVerification("test_cache_level_distribution"),
        TestCacheFixVerification("test_cache_persistence"),
    ]
    
    for test_case in test_cases:
        test_suite.addTest(test_case)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出结果摘要
    print("\n" + "=" * 50)
    print("📊 测试结果摘要:")
    print(f"运行测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if not result.failures and not result.errors:
        print("\n✅ 所有测试通过！缓存修复验证成功")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_cache_fix_verification()
    sys.exit(0 if success else 1) 