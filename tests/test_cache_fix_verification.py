#!/usr/bin/env python3
"""
缓存系统修复验证脚本
验证关键词缓存功能和增强的缓存管理器
"""

import sys
import os
import time
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

def test_keyword_cache():
    """测试关键词缓存功能"""
    print("🔍 测试关键词缓存功能...")
    
    try:
        from core.memory.shared.caching.keyword_cache import KeywordCache
        
        # 创建关键词缓存实例
        keyword_cache = KeywordCache()
        
        # 测试关键词提取
        test_text = "今天天气很好，我想出去散步，享受阳光"
        keywords = keyword_cache._extract_keywords(test_text)
        print(f"   关键词提取: {keywords}")
        
        # 测试添加到缓存
        keyword_cache.add_to_keyword_cache("test_key_1", test_text, 5.0)
        keyword_cache.add_to_keyword_cache("test_key_2", "散步是很好的运动", 3.0)
        
        # 测试搜索
        search_results = keyword_cache.search_by_keywords("散步", 5)
        print(f"   搜索结果: {search_results}")
        
        # 测试统计
        stats = keyword_cache.get_keyword_stats()
        print(f"   统计信息: {stats}")
        
        print("✅ 关键词缓存功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 关键词缓存功能测试失败: {e}")
        return False

def test_enhanced_cache_manager():
    """测试增强的缓存管理器"""
    print("🔍 测试增强的缓存管理器...")
    
    try:
        from core.memory.shared.caching.cache_manager import UnifiedCacheManager
        
        # 创建管理器实例
        cache_manager = UnifiedCacheManager.get_instance()
        
        # 测试关键词缓存是否集成
        if hasattr(cache_manager, 'keyword_cache'):
            print("   ✅ 关键词缓存已集成")
        else:
            print("   ❌ 关键词缓存未集成")
            return False
        
        # 测试clear方法
        if hasattr(cache_manager, 'clear'):
            print("   ✅ clear方法已添加")
            cache_manager.clear()
            print("   ✅ 缓存清理成功")
        else:
            print("   ❌ clear方法缺失")
            return False
        
        # 测试search_by_content方法
        results = cache_manager.search_by_content("测试查询", 5)
        print(f"   内容搜索结果: {len(results)} 个")
        
        # 测试统计信息
        stats = cache_manager.get_stats()
        print(f"   统计信息获取: {'✅' if stats else '❌'}")
        
        print("✅ 增强缓存管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 增强缓存管理器测试失败: {e}")
        return False

def test_system_integration():
    """测试系统集成"""
    print("🔍 测试系统集成...")
    
    try:
        from core.memory.estia_memory_v5 import EstiaMemorySystem
        
        # 创建记忆系统实例
        memory_system = EstiaMemorySystem()
        
        # 测试统一缓存是否正确初始化
        if hasattr(memory_system, 'unified_cache') and memory_system.unified_cache:
            print("   ✅ 统一缓存正确初始化")
        else:
            print("   ❌ 统一缓存未正确初始化")
            return False
        
        # 测试基本功能
        test_query = "这是一个测试查询"
        
        try:
            result = memory_system.enhance_query(test_query)
            print("   ✅ enhance_query方法正常工作")
        except Exception as e:
            print(f"   ❌ enhance_query方法失败: {e}")
            return False
        
        print("✅ 系统集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 系统集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 缓存系统修复验证测试")
    print("=" * 60)
    
    test_results = {
        "keyword_cache": test_keyword_cache(),
        "enhanced_manager": test_enhanced_cache_manager(),
        "system_integration": test_system_integration()
    }
    
    # 计算总体成功率
    success_rate = sum(test_results.values()) / len(test_results)
    
    print("\n" + "=" * 60)
    print("📊 修复验证结果")
    print("=" * 60)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总体成功率: {success_rate:.2%}")
    
    if success_rate == 1.0:
        print("🎉 所有修复验证通过！")
    elif success_rate >= 0.8:
        print("✅ 大部分修复验证通过，少数问题待解决")
    else:
        print("❌ 修复验证失败较多，需要进一步调试")

if __name__ == "__main__":
    main()
