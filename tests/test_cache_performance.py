#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia-AI缓存性能专项测试脚本
专门测试588倍缓存性能提升是否生效
使用本地缓存模型，避免网络下载问题
"""

import time
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def force_offline_mode():
    """强制使用离线模式，避免网络下载"""
    print("🔧 设置离线模式...")
    
    # 设置Hugging Face离线模式
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    
    # 设置模型缓存目录为项目本地cache
    project_cache = os.path.join(os.path.dirname(__file__), "core", "cache")
    os.environ['HUGGINGFACE_HUB_CACHE'] = project_cache
    os.environ['SENTENCE_TRANSFORMERS_HOME'] = project_cache
    os.environ['HF_HOME'] = project_cache
    
    print(f"   ✅ 模型缓存目录: {project_cache}")
    print("   ✅ 离线模式已启用")

def test_cache_performance_detailed():
    """详细测试缓存性能"""
    print("🧪 Estia-AI 缓存性能专项测试")
    print("=" * 60)
    
    # 强制离线模式
    force_offline_mode()
    
    try:
        # 1. 测试模块导入
        print("\n1. 测试模块导入...")
        from core.memory.estia_memory_v5 import EstiaMemorySystem
        from core.memory.shared.caching.cache_manager import UnifiedCacheManager
        print("   ✅ 核心模块导入成功")
        
        # 2. 初始化系统（禁用高级功能避免复杂依赖）
        print("\n2. 初始化记忆系统...")
        memory_system = EstiaMemorySystem(enable_advanced=False)
        
        if not memory_system.initialized:
            print("   ❌ 系统初始化失败")
            return False
            
        print("   ✅ 系统初始化成功")
        
        # 3. 获取缓存管理器
        print("\n3. 获取缓存管理器...")
        cache_manager = UnifiedCacheManager.get_instance()
        print(f"   ✅ 缓存管理器实例: {type(cache_manager).__name__}")
        
        # 4. 测试缓存基本功能
        print("\n4. 测试缓存基本功能...")
        
        # 测试简单的缓存操作
        test_key = "cache_test_key"
        test_value = {"test": "data", "timestamp": time.time()}
        
        # 存储
        cache_manager.put(test_key, test_value)
        print("   ✅ 缓存存储成功")
        
        # 读取
        cached_result = cache_manager.get(test_key)
        if cached_result == test_value:
            print("   ✅ 缓存读取成功")
        else:
            print("   ❌ 缓存读取失败")
            
        # 5. 测试查询增强的缓存性能
        print("\n5. 测试查询增强缓存性能...")
        
        test_queries = [
            "你好世界",
            "今天天气如何",
            "请帮我解决问题",
            "我想学习编程",
            "谢谢你的帮助"
        ]
        
        cold_times = []
        warm_times = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   测试查询 {i}: '{query}'")
            
            # 第一次执行（冷启动）
            start_time = time.time()
            try:
                result1 = memory_system.enhance_query(query)
                cold_time = time.time() - start_time
                cold_times.append(cold_time)
                print(f"     第一次执行: {cold_time*1000:.2f}ms")
            except Exception as e:
                print(f"     第一次执行失败: {e}")
                continue
            
            # 稍微等待一下
            time.sleep(0.1)
            
            # 第二次执行（应该命中缓存）
            start_time = time.time()
            try:
                result2 = memory_system.enhance_query(query)
                warm_time = time.time() - start_time
                warm_times.append(warm_time)
                print(f"     第二次执行: {warm_time*1000:.2f}ms")
                
                # 计算性能提升
                if warm_time > 0:
                    speedup = cold_time / warm_time
                    print(f"     性能提升: {speedup:.1f}x")
                    
                    if speedup > 1.5:
                        print("     ✅ 缓存生效")
                    else:
                        print("     ⚠️ 缓存效果不明显")
                else:
                    print("     ⚠️ 执行时间过短，无法准确测量")
                    
            except Exception as e:
                print(f"     第二次执行失败: {e}")
                continue
        
        # 6. 计算总体性能提升
        print(f"\n6. 总体性能分析...")
        
        if cold_times and warm_times:
            avg_cold = sum(cold_times) / len(cold_times)
            avg_warm = sum(warm_times) / len(warm_times)
            
            print(f"   平均冷启动时间: {avg_cold*1000:.2f}ms")
            print(f"   平均缓存命中时间: {avg_warm*1000:.2f}ms")
            
            if avg_warm > 0:
                overall_speedup = avg_cold / avg_warm
                print(f"   总体性能提升: {overall_speedup:.1f}x")
                
                if overall_speedup > 2:
                    print("   ✅ 缓存性能提升显著！")
                elif overall_speedup > 1.2:
                    print("   ⚠️ 缓存有一定效果，但未达到预期")
                else:
                    print("   ❌ 缓存效果不明显")
            else:
                print("   ⚠️ 无法计算性能提升")
        else:
            print("   ❌ 性能测试数据不足")
            
        # 7. 获取详细的缓存统计
        print(f"\n7. 缓存统计信息...")
        
        try:
            cache_stats = memory_system.get_cache_stats()
            if cache_stats:
                print("   ✅ 缓存统计获取成功")
                print(f"   统计数据: {json.dumps(cache_stats, indent=2, ensure_ascii=False)}")
            else:
                print("   ⚠️ 缓存统计为空")
                
        except Exception as e:
            print(f"   ❌ 获取缓存统计失败: {e}")
            
        # 8. 测试缓存清理
        print(f"\n8. 测试缓存清理...")
        
        try:
            clear_result = memory_system.clear_cache()
            if clear_result and clear_result.get('success'):
                print("   ✅ 缓存清理成功")
                print(f"   清理结果: {clear_result}")
            else:
                print("   ⚠️ 缓存清理结果异常")
                
        except Exception as e:
            print(f"   ❌ 缓存清理失败: {e}")
            
        print(f"\n✅ 缓存性能测试完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_cache_specifically():
    """专门测试向量缓存性能"""
    print(f"\n" + "=" * 60)
    print("🔍 向量缓存专项测试")
    print("=" * 60)
    
    try:
        # 强制离线模式
        force_offline_mode()
        
        # 导入向量化器
        from core.memory.shared.embedding.vectorizer import TextVectorizer
        
        print("\n1. 初始化向量化器...")
        
        # 使用本地缓存的模型
        vectorizer = TextVectorizer(
            model_type="sentence-transformers",
            model_name="Qwen/Qwen3-Embedding-0.6B",  # 使用本地缓存的模型
            use_cache=True,
            device="cpu"
        )
        
        print("   ✅ 向量化器初始化成功")
        
        # 测试向量化性能
        test_texts = [
            "测试向量化性能",
            "Hello world",
            "Python编程语言",
            "人工智能技术",
            "缓存系统优化"
        ]
        
        print("\n2. 测试向量化缓存性能...")
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n   测试文本 {i}: '{text}'")
            
            # 第一次向量化（可能需要计算）
            start_time = time.time()
            vector1 = vectorizer.encode(text)
            first_time = time.time() - start_time
            
            # 第二次向量化（应该命中缓存）
            start_time = time.time()
            vector2 = vectorizer.encode(text)
            second_time = time.time() - start_time
            
            print(f"     第一次: {first_time*1000:.2f}ms")
            print(f"     第二次: {second_time*1000:.2f}ms")
            
            # 验证向量一致性
            if vector1 is not None and vector2 is not None:
                import numpy as np
                if np.array_equal(vector1, vector2):
                    print("     ✅ 向量一致性检查通过")
                else:
                    print("     ❌ 向量一致性检查失败")
                    
                # 计算性能提升
                if second_time > 0:
                    speedup = first_time / second_time
                    print(f"     性能提升: {speedup:.1f}x")
                    
                    if speedup > 2:
                        print("     ✅ 向量缓存效果显著")
                    else:
                        print("     ⚠️ 向量缓存效果不明显")
                else:
                    print("     ⚠️ 第二次执行时间过短")
            else:
                print("     ❌ 向量化失败")
                
        print(f"\n✅ 向量缓存测试完成！")
        
    except Exception as e:
        print(f"\n❌ 向量缓存测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 启动Estia-AI缓存性能专项测试")
    
    # 运行详细的缓存性能测试
    success = test_cache_performance_detailed()
    
    # 运行向量缓存专项测试
    test_vector_cache_specifically()
    
    print(f"\n🎯 测试总结:")
    if success:
        print("✅ 基础缓存功能正常")
    else:
        print("❌ 基础缓存功能存在问题")
    
    print("\n📋 后续建议:")
    print("1. 如果缓存性能提升不明显，需要检查缓存键的生成逻辑")
    print("2. 如果向量缓存不生效，需要检查向量化器的缓存集成")
    print("3. 如果系统初始化失败，需要检查数据库和组件依赖")
    print("4. 考虑继续修复Phase 1的其他组件（会话管理、权重管理等）")
    
    print(f"\n🎉 测试完成！")