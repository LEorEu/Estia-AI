#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试文本向量化模块功能
"""

import os
import sys
import numpy as np
import time
import argparse

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入文本向量化器
from core.memory.embedding import TextVectorizer, EmbeddingCache

def test_vectorizer(model_type="sentence-transformers", model_name=None, use_cache=True):
    """测试文本向量化器的基本功能"""
    print(f"\n===== 测试文本向量化器 ({model_type}) =====")
    
    # 设置测试缓存目录
    test_cache_dir = os.path.join("data", "memory", "test_vectorizer_cache")
    
    # 确保目录存在
    os.makedirs(test_cache_dir, exist_ok=True)
    
    # 初始化向量化器
    print("\n1. 初始化文本向量化器")
    try:
        vectorizer = TextVectorizer(
            model_type=model_type,
            model_name=model_name,
            cache_dir=test_cache_dir,
            use_cache=use_cache
        )
        print(f"向量化器初始化成功，模型: {vectorizer.model_type}/{vectorizer.model_name}")
        print(f"向量维度: {vectorizer.get_vector_dimension()}")
    except ImportError as e:
        print(f"导入错误: {e}")
        print(f"请安装所需的库: pip install {'sentence-transformers' if model_type == 'sentence-transformers' else 'openai'}")
        return False
    except Exception as e:
        print(f"初始化向量化器失败: {e}")
        return False
    
    # 准备测试文本
    print("\n2. 准备测试文本")
    test_texts = [
        "这是第一个测试文本，用于验证向量化功能",
        "This is a test text for verifying vectorization functionality",
        "这是另一个相似的测试文本，与第一个有一些相似之处",
        "这是完全不同的内容，讨论的是天气和自然环境"
    ]
    print(f"准备了 {len(test_texts)} 个测试文本")
    
    # 测试文本编码
    print("\n3. 测试文本编码")
    try:
        # 首次编码，应该不会命中缓存
        start_time = time.time()
        vectors = vectorizer.encode(test_texts, show_progress=True)
        encode_time = time.time() - start_time
        
        print(f"编码 {len(test_texts)} 个文本，耗时: {encode_time:.4f}秒")
        print(f"向量形状: {vectors.shape}")
        
        # 如果使用缓存，再次编码应该更快
        if use_cache:
            print("\n4. 测试缓存效果")
            start_time = time.time()
            cached_vectors = vectorizer.encode(test_texts)
            cache_time = time.time() - start_time
            
            print(f"从缓存获取向量，耗时: {cache_time:.4f}秒")
            print(f"缓存加速比: {encode_time / max(cache_time, 0.0001):.2f}倍")
            
            # 验证向量一致性
            is_equal = np.array_equal(vectors, cached_vectors)
            print(f"向量一致性: {is_equal}")
    except Exception as e:
        print(f"编码文本失败: {e}")
        return False
    
    # 测试相似度计算
    print("\n5. 测试相似度计算")
    try:
        print("文本对相似度:")
        for i in range(len(test_texts)):
            for j in range(i+1, len(test_texts)):
                sim = vectorizer.compute_similarity(vectors[i], vectors[j])
                print(f"  文本 {i+1} 和文本 {j+1}: {sim:.4f}")
        
        # 测试批量相似度计算
        print("\n批量相似度计算:")
        query_vec = vectors[0]  # 使用第一个文本作为查询
        similarities = vectorizer.batch_compute_similarity(query_vec, vectors)
        
        # 打印结果并排序
        results = [(i, sim) for i, sim in enumerate(similarities)]
        results.sort(key=lambda x: x[1], reverse=True)
        
        for i, sim in results:
            print(f"  查询与文本 {i+1}: {sim:.4f} - {'自身' if i == 0 else ''}")
    except Exception as e:
        print(f"计算相似度失败: {e}")
        return False
    
    # 测试单个文本编码
    print("\n6. 测试单个文本编码")
    try:
        single_text = "这是一个单独的测试文本"
        
        start_time = time.time()
        single_vector = vectorizer.encode(single_text)
        single_time = time.time() - start_time
        
        print(f"编码单个文本，耗时: {single_time:.4f}秒")
        print(f"向量形状: {single_vector.shape}")
        
        # 计算与其他文本的相似度
        print("\n单个文本与测试文本的相似度:")
        for i, vec in enumerate(vectors):
            sim = vectorizer.compute_similarity(single_vector, vec)
            print(f"  与文本 {i+1}: {sim:.4f}")
    except Exception as e:
        print(f"单个文本编码失败: {e}")
        return False
    
    print("\n===== 文本向量化器测试完成 =====")
    return True

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="测试文本向量化模块")
    parser.add_argument("--model", choices=["sentence-transformers", "openai"], 
                      default="sentence-transformers", help="选择模型类型")
    parser.add_argument("--model-name", help="指定模型名称")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    
    args = parser.parse_args()
    
    # 运行测试
    test_vectorizer(
        model_type=args.model,
        model_name=args.model_name,
        use_cache=not args.no_cache
    ) 