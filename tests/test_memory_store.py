#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试记忆存储管理器功能
"""

import os
import sys
import time
import shutil
import argparse

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入记忆存储管理器
from core.memory.storage.memory_store import MemoryStore

def test_memory_store(use_test_db=True, model_name=None, offline_mode=False):
    """测试记忆存储管理器的基本功能"""
    print("\n===== 测试记忆存储管理器 =====")
    
    # 设置测试路径
    if use_test_db:
        test_db_path = os.path.join("assets", "test_memory.db")
        test_index_path = os.path.join("data", "vectors", "test_memory_index.bin")
        test_cache_dir = os.path.join("data", "memory", "test_cache")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(test_db_path), exist_ok=True)
        os.makedirs(os.path.dirname(test_index_path), exist_ok=True)
        os.makedirs(test_cache_dir, exist_ok=True)
        
        # 如果测试数据库已存在，先删除
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print(f"已删除旧的测试数据库: {test_db_path}")
            
        if os.path.exists(test_index_path):
            os.remove(test_index_path)
            print(f"已删除旧的测试索引: {test_index_path}")
            
        if os.path.exists(test_index_path + ".meta"):
            os.remove(test_index_path + ".meta")
    else:
        # 使用默认路径
        test_db_path = os.path.join("assets", "memory.db")
        test_index_path = os.path.join("data", "vectors", "memory_index.bin")
        test_cache_dir = os.path.join("data", "memory", "cache")
    
    # 设置默认模型
    if model_name is None:
        # 在线模式使用预训练模型
        model_type = "sentence-transformers"
        model_name = "Qwen/Qwen3-Embedding-0.6B"  # 使用阿里巴巴的Qwen模型
        print(f"使用在线模型: {model_name}")
    else:
        model_type = "sentence-transformers"
        print(f"使用指定模型: {model_name}")
    
    # 初始化记忆存储管理器
    print("\n1. 初始化记忆存储管理器")
    try:
        memory_store = MemoryStore(
            db_path=test_db_path,
            index_path=test_index_path,
            cache_dir=test_cache_dir,
            model_type=model_type,
            model_name=model_name
        )
        print(f"记忆存储管理器初始化成功")
    except Exception as e:
        print(f"初始化记忆存储管理器失败: {e}")
        return False
    
    # 测试添加记忆
    print("\n2. 测试添加记忆")
    test_memories = [
        "今天天气真好，阳光明媚",
        "我喜欢编程，尤其是Python和人工智能",
        "记忆系统是AI助手的重要组成部分",
        "向量数据库可以高效地进行相似性搜索",
        "大语言模型需要长期记忆来提高交互体验"
    ]
    
    memory_ids = []
    start_time = time.time()
    for i, content in enumerate(test_memories):
        memory_id = memory_store.add_memory(
            content=content,
            source="test",
            importance=0.5 + i * 0.1,
            metadata={"test_index": i}
        )
        if memory_id:
            memory_ids.append(memory_id)
            print(f"添加记忆成功: {memory_id[:8]}..., 内容: {content}")
    
    add_time = time.time() - start_time
    print(f"添加 {len(memory_ids)} 条记忆，耗时: {add_time:.4f}秒")
    
    if not memory_ids:
        print("添加记忆失败，测试终止")
        return False
    
    # 测试获取记忆
    print("\n3. 测试获取记忆")
    memory = memory_store.get_memory(memory_ids[0])
    if memory:
        print(f"获取记忆成功:")
        print(f"  ID: {memory['memory_id'][:8]}...")
        print(f"  内容: {memory['content']}")
        print(f"  时间: {memory['timestamp']}")
        print(f"  重要性: {memory['importance']}")
    else:
        print("获取记忆失败")
    
    # 测试搜索相似记忆
    print("\n4. 测试搜索相似记忆")
    queries = [
        "AI系统中的记忆功能",
        "编程和人工智能技术",
        "今天的天气情况"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        start_time = time.time()
        similar_memories = memory_store.search_similar(query, limit=3)
        search_time = time.time() - start_time
        
        print(f"搜索耗时: {search_time:.4f}秒")
        print(f"找到 {len(similar_memories)} 条相似记忆:")
        
        for i, memory in enumerate(similar_memories):
            print(f"  结果 {i+1}: [{memory['similarity']:.4f}] {memory['content']}")
    
    # 测试添加关联
    print("\n5. 测试添加关联")
    if len(memory_ids) >= 2:
        success = memory_store.add_association(
            source_id=memory_ids[0],
            target_id=memory_ids[1],
            association_type="related",
            strength=0.8
        )
        print(f"添加关联: {'成功' if success else '失败'}")
        
        # 获取关联记忆
        associations = memory_store.get_associated_memories(memory_ids[0])
        print(f"获取关联记忆: {len(associations)} 条")
        
        for i, assoc in enumerate(associations):
            print(f"  关联 {i+1}: [{assoc['strength']:.2f}] {assoc['content']}")
    
    # 测试更新记忆重要性
    print("\n6. 测试更新记忆重要性")
    if memory_ids:
        new_importance = 0.9
        success = memory_store.update_memory_importance(memory_ids[0], new_importance)
        print(f"更新记忆重要性: {'成功' if success else '失败'}")
        
        # 验证更新
        updated_memory = memory_store.get_memory(memory_ids[0])
        if updated_memory:
            print(f"  新重要性: {updated_memory['importance']} (预期: {new_importance})")
    
    # 测试获取最近记忆
    print("\n7. 测试获取最近记忆")
    recent_memories = memory_store.get_recent_memories(limit=5)
    print(f"获取最近 {len(recent_memories)} 条记忆:")
    
    for i, memory in enumerate(recent_memories):
        print(f"  记忆 {i+1}: [{memory['timestamp']}] {memory['content']}")
    
    # 测试删除记忆
    print("\n8. 测试删除记忆")
    if memory_ids:
        delete_id = memory_ids[-1]
        success = memory_store.delete_memory(delete_id)
        print(f"删除记忆 {delete_id[:8]}...: {'成功' if success else '失败'}")
        
        # 验证删除
        deleted_memory = memory_store.get_memory(delete_id)
        print(f"  验证删除: {'成功' if deleted_memory is None else '失败'}")
    
    # 关闭记忆存储管理器
    memory_store.close()
    print("\n记忆存储管理器已关闭")
    
    # 清理测试文件（可选）
    if use_test_db and False:  # 设置为True以启用清理
        print("\n9. 清理测试文件")
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print(f"已删除测试数据库: {test_db_path}")
            
        if os.path.exists(test_index_path):
            os.remove(test_index_path)
            print(f"已删除测试索引: {test_index_path}")
            
        if os.path.exists(test_index_path + ".meta"):
            os.remove(test_index_path + ".meta")
            print(f"已删除测试索引元数据: {test_index_path}.meta")
            
        if os.path.exists(test_cache_dir):
            shutil.rmtree(test_cache_dir)
            print(f"已删除测试缓存目录: {test_cache_dir}")
    
    print("\n===== 记忆存储管理器测试完成 =====")
    return True

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="测试记忆存储管理器")
    parser.add_argument("--no-test-db", action="store_true", 
                      help="使用默认数据库路径而不是测试数据库")
    parser.add_argument("--model", help="指定向量化模型名称")
    parser.add_argument("--offline", action="store_true",
                      help="离线模式，使用随机向量而不是预训练模型")
    
    args = parser.parse_args()
    
    # 运行测试
    test_memory_store(
        use_test_db=not args.no_test_db,
        model_name=args.model,
        offline_mode=args.offline
    ) 