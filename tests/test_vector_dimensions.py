#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速测试向量维度问题修复
"""

import os
import sys
import numpy as np

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_vector_dimensions():
    """测试向量维度一致性"""
    print("🧪 测试向量维度一致性")
    print("=" * 60)
    
    try:
        # 测试TextVectorizer
        print("1. 测试TextVectorizer...")
        from core.memory.shared.embedding.vectorizer import TextVectorizer
        
        vectorizer = TextVectorizer(
            model_type="sentence-transformers",
            model_name="Qwen/Qwen3-Embedding-0.6B",
            use_cache=True
        )
        
        test_text = "这是一个测试文本"
        vector = vectorizer.encode(test_text)
        print(f"   TextVectorizer向量维度: {vector.shape}")
        print(f"   向量化器报告的维度: {vectorizer.vector_dim}")
        
        # 测试SimpleVectorizer
        print("\n2. 测试SimpleVectorizer...")
        from core.memory.shared.embedding.simple_vectorizer import SimpleVectorizer
        
        simple_vectorizer = SimpleVectorizer(dimension=1024, use_cache=True)
        simple_vector = simple_vectorizer.encode(test_text)
        print(f"   SimpleVectorizer向量维度: {simple_vector.shape}")
        print(f"   简化向量化器报告的维度: {simple_vectorizer.vector_dim}")
        
        # 检查一致性
        print("\n3. 检查维度一致性...")
        if vector.shape == simple_vector.shape:
            print("   ✅ 向量维度一致！")
        else:
            print("   ❌ 向量维度不一致！")
            print(f"   TextVectorizer: {vector.shape}")
            print(f"   SimpleVectorizer: {simple_vector.shape}")
        
        # 测试数组兼容性
        print("\n4. 测试数组兼容性...")
        try:
            # 尝试将向量reshape为相同形状
            reshaped_vector = vector.reshape(1, -1)
            reshaped_simple = simple_vector.reshape(1, -1)
            print(f"   Reshaped TextVectorizer: {reshaped_vector.shape}")
            print(f"   Reshaped SimpleVectorizer: {reshaped_simple.shape}")
            
            # 尝试创建数组
            combined = np.vstack([reshaped_vector, reshaped_simple])
            print(f"   Combined array: {combined.shape}")
            print("   ✅ 数组兼容性测试通过！")
            
        except Exception as e:
            print(f"   ❌ 数组兼容性测试失败: {e}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vector_dimensions()