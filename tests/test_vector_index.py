#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试向量索引管理器功能
"""

import os
import sys
import numpy as np
import time
import logging
import traceback

# 设置日志级别
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入向量索引管理器
from core.memory.init.vector_index import VectorIndexManager

def test_vector_index():
    """测试向量索引管理器的基本功能"""
    print("\n===== 测试向量索引管理器 =====")
    
    # 使用测试索引路径
    test_index_path = os.path.join("data", "vectors", "test_index.bin")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(test_index_path), exist_ok=True)
    
    # 如果测试索引已存在，先删除
    if os.path.exists(test_index_path):
        os.remove(test_index_path)
        print(f"已删除旧的测试索引文件: {test_index_path}")
    
    if os.path.exists(test_index_path + ".meta"):
        os.remove(test_index_path + ".meta")
        print(f"已删除旧的测试索引元数据文件: {test_index_path}.meta")
    
    # 创建向量索引管理器
    print("\n1. 初始化向量索引管理器")
    vector_dim = 128  # 使用较小的维度加快测试速度
    vector_manager = VectorIndexManager(test_index_path, vector_dim=vector_dim)
    
    if not vector_manager.available:
        print("错误: FAISS库未安装，测试终止")
        return False
    
    # 测试创建索引
    print("\n2. 测试创建索引")
    success = vector_manager.create_index()
    print(f"创建索引: {'成功' if success else '失败'}")
    
    if not success:
        print("错误: 创建索引失败，测试终止")
        return False
    
    # 生成测试向量
    print("\n3. 测试添加向量")
    num_vectors = 100
    test_vectors = np.random.random((num_vectors, vector_dim)).astype('float32')
    test_ids = [f"test_id_{i}" for i in range(num_vectors)]
    
    # 添加向量
    start_time = time.time()
    try:
        success = vector_manager.add_vectors(test_vectors, test_ids)
        add_time = time.time() - start_time
        print(f"添加 {num_vectors} 个向量: {'成功' if success else '失败'}, 耗时: {add_time:.4f}秒")
        
        if not success:
            print("错误: 添加向量失败，测试终止")
            # 检查索引类型和状态
            print(f"索引类型: {type(vector_manager.index)}")
            print(f"索引维度: {vector_manager.vector_dim}")
            print(f"向量维度: {test_vectors.shape}")
            return False
    except Exception as e:
        print(f"添加向量时发生异常: {str(e)}")
        traceback.print_exc()
        return False
    
    # 保存索引
    print("\n4. 测试保存索引")
    try:
        start_time = time.time()
        success = vector_manager.save_index()
        save_time = time.time() - start_time
        print(f"保存索引: {'成功' if success else '失败'}, 耗时: {save_time:.4f}秒")
        
        if not success:
            print("错误: 保存索引失败，测试终止")
            return False
    except Exception as e:
        print(f"保存索引时发生异常: {str(e)}")
        traceback.print_exc()
        return False
    
    # 获取索引信息
    print("\n5. 测试获取索引信息")
    try:
        info = vector_manager.get_index_info()
        print("索引信息:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"获取索引信息时发生异常: {str(e)}")
        traceback.print_exc()
    
    # 测试搜索向量
    print("\n6. 测试搜索向量")
    try:
        # 随机生成一个查询向量
        query_vector = np.random.random((1, vector_dim)).astype('float32')
        
        # 也可以使用已有的向量作为查询向量，应该能找到完全匹配
        exact_query = test_vectors[10:11]
        
        # 执行搜索
        start_time = time.time()
        ids, scores = vector_manager.search(query_vector, k=5)
        search_time = time.time() - start_time
        print(f"随机向量搜索耗时: {search_time:.4f}秒")
        print(f"搜索结果: {len(ids)} 个匹配项")
        for i, (id, score) in enumerate(zip(ids, scores)):
            print(f"  {i+1}. ID: {id}, 相似度: {score:.4f}")
        
        # 使用已知向量进行精确搜索
        start_time = time.time()
        exact_ids, exact_scores = vector_manager.search(exact_query, k=5)
        exact_search_time = time.time() - start_time
        print(f"\n精确向量搜索耗时: {exact_search_time:.4f}秒")
        print(f"搜索结果: {len(exact_ids)} 个匹配项")
        for i, (id, score) in enumerate(zip(exact_ids, exact_scores)):
            print(f"  {i+1}. ID: {id}, 相似度: {score:.4f}")
            if id == test_ids[10]:
                print(f"  --> 成功找到精确匹配项: {id}")
    except Exception as e:
        print(f"搜索向量时发生异常: {str(e)}")
        traceback.print_exc()
    
    # 测试批量搜索
    print("\n7. 测试批量搜索")
    try:
        batch_size = 5
        batch_queries = np.random.random((batch_size, vector_dim)).astype('float32')
        
        start_time = time.time()
        batch_results = vector_manager.batch_search(batch_queries, k=3)
        batch_time = time.time() - start_time
        print(f"批量搜索 {batch_size} 个查询: 耗时 {batch_time:.4f}秒")
        
        for i, (ids, scores) in enumerate(batch_results):
            print(f"\n查询 {i+1} 结果:")
            for j, (id, score) in enumerate(zip(ids, scores)):
                print(f"  {j+1}. ID: {id}, 相似度: {score:.4f}")
    except Exception as e:
        print(f"批量搜索时发生异常: {str(e)}")
        traceback.print_exc()
    
    # 测试加载索引
    print("\n8. 测试加载索引")
    try:
        # 创建新的管理器实例
        new_manager = VectorIndexManager(test_index_path, vector_dim=vector_dim)
        
        start_time = time.time()
        success = new_manager.load_index()
        load_time = time.time() - start_time
        print(f"加载索引: {'成功' if success else '失败'}, 耗时: {load_time:.4f}秒")
        
        if not success:
            print("错误: 加载索引失败")
        else:
            # 验证加载的索引
            info = new_manager.get_index_info()
            print("加载后的索引信息:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            
            # 使用加载的索引进行搜索
            ids, scores = new_manager.search(query_vector, k=5)
            print(f"\n使用加载的索引搜索，结果: {len(ids)} 个匹配项")
            for i, (id, score) in enumerate(zip(ids, scores)):
                print(f"  {i+1}. ID: {id}, 相似度: {score:.4f}")
    except Exception as e:
        print(f"加载索引时发生异常: {str(e)}")
        traceback.print_exc()
    
    # 测试删除向量
    print("\n9. 测试删除向量")
    try:
        # 选择几个ID进行删除
        ids_to_delete = test_ids[20:25]
        print(f"尝试删除 {len(ids_to_delete)} 个向量: {', '.join(ids_to_delete)}")
        
        success = new_manager.delete_vectors(ids_to_delete)
        print(f"删除向量: {'成功' if success else '失败或不支持'}")
        
        if success:
            # 检查删除后的索引信息
            info = new_manager.get_index_info()
            print("删除后的索引信息:")
            for key, value in info.items():
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"删除向量时发生异常: {str(e)}")
        traceback.print_exc()
    
    # 清理测试文件
    print("\n10. 清理测试文件")
    try:
        if os.path.exists(test_index_path):
            os.remove(test_index_path)
            print(f"已删除测试索引文件: {test_index_path}")
        
        if os.path.exists(test_index_path + ".meta"):
            os.remove(test_index_path + ".meta")
            print(f"已删除测试索引元数据文件: {test_index_path}.meta")
    except Exception as e:
        print(f"清理测试文件时发生异常: {str(e)}")
        traceback.print_exc()
    
    print("\n===== 向量索引管理器测试完成 =====")
    return True

if __name__ == "__main__":
    test_vector_index() 