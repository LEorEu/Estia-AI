#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试缓存初始化问题
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_cache_initialization():
    """调试缓存初始化问题"""
    print("🔍 调试缓存初始化问题...")
    
    try:
        # 1. 检查EmbeddingCache导入
        print("1. 检查EmbeddingCache导入...")
        try:
            from core.memory.embedding.cache import EnhancedMemoryCache
            print("   ✅ EnhancedMemoryCache导入成功")
        except Exception as e:
            print(f"   ❌ EnhancedMemoryCache导入失败: {e}")
            return False
        
        # 2. 检查TextVectorizer缓存初始化
        print("2. 检查TextVectorizer缓存初始化...")
        try:
            from core.memory.embedding import TextVectorizer
            
            # 创建TextVectorizer实例
            vectorizer = TextVectorizer(
                model_type="sentence-transformers",
                model_name="paraphrase-multilingual-MiniLM-L12-v2",
                use_cache=True
            )
            
            print(f"   📊 vectorizer.use_cache: {vectorizer.use_cache}")
            print(f"   📊 vectorizer.cache: {vectorizer.cache}")
            
            if vectorizer.cache is None:
                print("   ❌ TextVectorizer缓存未初始化")
                return False
            else:
                print("   ✅ TextVectorizer缓存初始化成功")
                
        except Exception as e:
            print(f"   ❌ TextVectorizer缓存初始化失败: {e}")
            return False
        
        # 3. 检查统一缓存管理器
        print("3. 检查统一缓存管理器...")
        try:
            from core.memory.caching.cache_manager import UnifiedCacheManager
            
            unified_cache = UnifiedCacheManager.get_instance()
            print(f"   📊 已注册缓存: {list(unified_cache.caches.keys())}")
            
        except Exception as e:
            print(f"   ❌ 统一缓存管理器检查失败: {e}")
            return False
        
        # 4. 检查缓存适配器注册
        print("4. 检查缓存适配器注册...")
        try:
            from core.memory.caching.cache_adapters import EnhancedMemoryCacheAdapter
            from core.memory.caching.cache_manager import UnifiedCacheManager
            
            # 手动注册缓存适配器
            if vectorizer.cache:
                vector_adapter = EnhancedMemoryCacheAdapter(vectorizer.cache)
                UnifiedCacheManager.get_instance().register_cache(vector_adapter)
                print("   ✅ 手动注册缓存适配器成功")
                
                # 检查注册结果
                unified_cache = UnifiedCacheManager.get_instance()
                print(f"   📊 注册后缓存: {list(unified_cache.caches.keys())}")
            else:
                print("   ❌ 无法注册：vectorizer.cache为空")
                return False
                
        except Exception as e:
            print(f"   ❌ 缓存适配器注册失败: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 调试过程失败: {e}")
        return False

def test_cache_operation():
    """测试缓存操作"""
    print("🧪 测试缓存操作...")
    
    try:
        from core.memory.embedding import TextVectorizer
        from core.memory.caching.cache_manager import UnifiedCacheManager
        
        # 初始化
        vectorizer = TextVectorizer(use_cache=True)
        unified_cache = UnifiedCacheManager.get_instance()
        
        # 测试文本
        test_text = "这是一个测试文本"
        
        print("  📝 测试缓存写入...")
        
        # 编码文本（应该写入缓存）
        vector = vectorizer.encode(test_text)
        
        # 检查缓存统计
        stats = unified_cache.get_stats()
        print(f"    📊 缓存统计: {stats.get('total_hits', 0)} 命中, {stats.get('total_misses', 0)} 未命中")
        
        # 检查向量化器缓存统计
        vectorizer_stats = vectorizer.get_cache_stats()
        print(f"    📊 向量化器缓存类型: {vectorizer_stats.get('cache_type', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 缓存操作测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始缓存调试")
    print("=" * 60)
    
    # 运行调试
    debug_success = debug_cache_initialization()
    
    if debug_success:
        print("\n" + "=" * 60)
        test_success = test_cache_operation()
        
        if test_success:
            print("\n🎉 缓存调试完成，问题已解决！")
        else:
            print("\n⚠️ 缓存操作测试失败")
    else:
        print("\n❌ 缓存初始化调试失败")
    
    return debug_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 