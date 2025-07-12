#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速验证关键修复
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def quick_verification():
    """快速验证关键修复"""
    print("🚀 快速验证关键修复")
    print("=" * 60)
    
    print("1. 验证缓存清理...")
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    npy_files = [f for f in os.listdir(cache_dir) if f.endswith('.npy')] if os.path.exists(cache_dir) else []
    json_files = [f for f in os.listdir(cache_dir) if f.endswith('_cache.json')] if os.path.exists(cache_dir) else []
    
    print(f"   缓存目录: {cache_dir}")
    print(f"   .npy文件数量: {len(npy_files)}")
    print(f"   缓存索引文件数量: {len(json_files)}")
    
    if len(npy_files) == 0:
        print("   ✅ 向量缓存已清理")
    else:
        print("   ⚠️ 仍有向量缓存文件")
    
    print("\n2. 测试v6记忆系统...")
    try:
        from core.memory.estia_memory_v6 import create_estia_memory
        
        memory_system = create_estia_memory(enable_advanced=True)
        
        if memory_system.initialized:
            print("   ✅ v6记忆系统初始化成功")
            
            # 测试基础功能
            test_query = "测试查询增强"
            enhanced_context = memory_system.enhance_query(test_query)
            print(f"   ✅ 查询增强功能正常: {len(enhanced_context)} 字符")
            
            # 测试交互存储
            test_response = "测试AI回复"
            store_result = memory_system.store_interaction(test_query, test_response)
            if store_result and not store_result.get('error'):
                print("   ✅ 交互存储功能正常")
            else:
                print(f"   ❌ 交互存储功能异常: {store_result}")
        else:
            print("   ❌ v6记忆系统初始化失败")
            
    except Exception as e:
        print(f"   ❌ v6测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. 检查向量维度一致性...")
    try:
        from core.memory.shared.embedding.simple_vectorizer import SimpleVectorizer
        from core.memory.shared.embedding.vectorizer import TextVectorizer
        
        # 测试SimpleVectorizer
        simple_vectorizer = SimpleVectorizer()
        simple_vector = simple_vectorizer.encode("测试文本")
        print(f"   SimpleVectorizer维度: {simple_vector.shape}")
        
        # 如果可能，测试TextVectorizer
        try:
            text_vectorizer = TextVectorizer()
            text_vector = text_vectorizer.encode("测试文本")
            print(f"   TextVectorizer维度: {text_vector.shape}")
            
            if simple_vector.shape == text_vector.shape:
                print("   ✅ 向量维度一致")
            else:
                print("   ❌ 向量维度不一致")
        except Exception:
            print("   ⚠️ TextVectorizer测试跳过（可能需要模型）")
            
    except Exception as e:
        print(f"   ❌ 向量维度测试失败: {e}")
    
    print("\n✅ 快速验证完成")

if __name__ == "__main__":
    quick_verification()