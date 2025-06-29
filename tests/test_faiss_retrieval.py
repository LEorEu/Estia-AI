#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FAISS检索功能测试脚本
测试Step 4：FAISS检索最相关记忆的核心功能
"""

import os
import sys
import time
import argparse
import shutil
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.storage.memory_store import MemoryStore

def test_faiss_retrieval(use_test_db=True, model_name=None, offline_mode=False):
    """
    测试FAISS向量检索功能
    
    参数:
        use_test_db: 是否使用测试数据库
        model_name: 向量化模型名称
        offline_mode: 是否使用离线模式
    """
    print("===== FAISS检索功能测试 =====")
    
    # 设置测试路径
    if use_test_db:
        test_db_path = os.path.join("assets", "test_faiss_memory.db")
        test_index_path = os.path.join("data", "vectors", "test_faiss_memory_index.bin")
        test_cache_dir = os.path.join("data", "memory", "test_faiss_cache")
        
        # 创建测试目录
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
        model_type = "sentence-transformers"
        model_name = "Qwen/Qwen3-Embedding-0.6B"
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
    
    # 准备测试数据 - 创建一个有意义的数据集
    print("\n2. 添加测试记忆数据")
    test_memories = [
        # 编程相关
        "我喜欢Python编程，特别是机器学习和人工智能领域",
        "最近在学习深度学习框架PyTorch，感觉很有趣",
        "正在用Flask开发一个Web应用，遇到了一些数据库问题",
        
        # 生活相关  
        "今天天气很好，去公园散步了一个小时",
        "昨天和朋友一起看了一部科幻电影，剧情很精彩",
        "周末计划去图书馆学习，准备下个月的考试",
        
        # 工作相关
        "公司最近启动了一个AI项目，我负责算法部分",
        "参加了技术分享会，学到了很多关于微服务架构的知识",
        "团队合作完成了一个重要的产品功能，很有成就感",
        
        # 学习相关
        "在coursera上学习机器学习课程，已经完成了60%",
        "读了一本关于算法设计的书，对动态规划有了更深理解",
        "参加了编程竞赛，虽然没有获奖但学到了很多",
        
        # 技术细节
        "使用FAISS进行向量相似性搜索，性能比传统方法快很多",
        "了解了Transformer架构的工作原理，注意力机制很巧妙",
        "学会了使用Docker部署应用，容器化技术真的很方便"
    ]
    
    memory_ids = []
    start_time = time.time()
    
    for i, content in enumerate(test_memories):
        # 设置不同的重要性分数
        importance = 0.3 + (i % 5) * 0.15  # 0.3, 0.45, 0.6, 0.75, 0.9
        
        memory_id = memory_store.add_memory(
            content=content,
            source="test_faiss",
            importance=importance,
            metadata={"category": ["programming", "life", "work", "study", "tech"][i % 5]}
        )
        
        if memory_id:
            memory_ids.append(memory_id)
            print(f"添加记忆 {i+1:2d}: [重要性:{importance:.2f}] {content[:30]}...")
    
    add_time = time.time() - start_time
    print(f"\n添加 {len(memory_ids)} 条记忆，耗时: {add_time:.4f}秒")
    
    if not memory_ids:
        print("添加记忆失败，测试终止")
        return False
    
    # 测试不同类型的查询
    print("\n3. 测试FAISS向量检索功能")
    
    test_queries = [
        # 精确匹配查询
        {
            "query": "Python编程和机器学习",
            "description": "精确匹配查询",
            "expected_keywords": ["Python", "机器学习", "人工智能"]
        },
        
        # 语义相似查询
        {
            "query": "深度学习和神经网络",
            "description": "语义相似查询", 
            "expected_keywords": ["PyTorch", "深度学习", "Transformer"]
        },
        
        # 领域相关查询
        {
            "query": "Web开发和数据库",
            "description": "领域相关查询",
            "expected_keywords": ["Flask", "Web", "数据库"]
        },
        
        # 生活场景查询
        {
            "query": "户外活动和休闲",
            "description": "生活场景查询",
            "expected_keywords": ["天气", "公园", "散步"]
        },
        
        # 抽象概念查询
        {
            "query": "学习和成长",
            "description": "抽象概念查询",
            "expected_keywords": ["学习", "课程", "考试"]
        }
    ]
    
    total_search_time = 0
    cache_hits = 0
    
    for i, test_case in enumerate(test_queries):
        query = test_case["query"]
        description = test_case["description"]
        expected_keywords = test_case["expected_keywords"]
        
        print(f"\n查询 {i+1}: {description}")
        print(f"查询内容: {query}")
        
        # 第一次查询 - 测试向量检索性能
        start_time = time.time()
        results = memory_store.search_similar(query, limit=5)
        search_time = time.time() - start_time
        total_search_time += search_time
        
        print(f"检索耗时: {search_time:.4f}秒")
        print(f"找到 {len(results)} 条相似记忆:")
        
        # 分析检索结果
        for j, memory in enumerate(results):
            similarity = memory.get('similarity', 0)
            content = memory.get('content', '')
            importance = memory.get('importance', 0)
            
            # 检查是否包含期望的关键词
            keyword_matches = sum(1 for keyword in expected_keywords if keyword in content)
            
            print(f"  结果 {j+1}: [相似度:{similarity:.4f}] [重要性:{importance:.2f}] [关键词匹配:{keyword_matches}]")
            print(f"         {content[:60]}...")
        
        # 第二次相同查询 - 测试缓存命中
        print(f"\n重复查询测试缓存命中:")
        start_time = time.time()
        cached_results = memory_store.search_similar(query, limit=5)
        cached_search_time = time.time() - start_time
        
        print(f"缓存查询耗时: {cached_search_time:.4f}秒")
        
        # 检查缓存效果
        if cached_search_time < search_time * 0.8:  # 如果缓存查询快20%以上
            cache_hits += 1
            print(f"✅ 缓存命中，速度提升: {((search_time - cached_search_time) / search_time * 100):.1f}%")
        else:
            print(f"⚠️ 缓存效果不明显")
        
        print("-" * 60)
    
    # 测试批量检索性能
    print("\n4. 测试批量检索性能")
    batch_queries = [
        "编程技术和开发",
        "工作项目和团队",
        "学习课程和考试",
        "生活日常和娱乐"
    ]
    
    print(f"批量查询 {len(batch_queries)} 个问题...")
    start_time = time.time()
    
    batch_results = []
    for query in batch_queries:
        results = memory_store.search_similar(query, limit=3)
        batch_results.append(results)
    
    batch_time = time.time() - start_time
    print(f"批量检索耗时: {batch_time:.4f}秒")
    print(f"平均每次查询: {batch_time/len(batch_queries):.4f}秒")
    
    # 测试不同limit参数的性能
    print("\n5. 测试不同检索数量的性能")
    test_query = "人工智能和机器学习技术"
    
    for limit in [1, 3, 5, 10, 20]:
        start_time = time.time()
        results = memory_store.search_similar(test_query, limit=limit)
        search_time = time.time() - start_time
        
        print(f"检索Top-{limit:2d}: {search_time:.4f}秒, 实际返回: {len(results)}条")
    
    # 输出总体统计
    print("\n6. 检索性能统计")
    print(f"总查询次数: {len(test_queries)}")
    print(f"总检索时间: {total_search_time:.4f}秒")
    print(f"平均检索时间: {total_search_time/len(test_queries):.4f}秒")
    print(f"缓存命中次数: {cache_hits}/{len(test_queries)}")
    print(f"缓存命中率: {cache_hits/len(test_queries)*100:.1f}%")
    
    # 关闭记忆存储管理器
    memory_store.close()
    print("\n记忆存储管理器已关闭")
    
    # 清理测试文件（可选）
    if use_test_db and False:  # 设置为True以启用清理
        print("\n7. 清理测试文件")
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
    
    print("\n===== FAISS检索功能测试完成 =====")
    return True

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="测试FAISS检索功能")
    parser.add_argument("--no-test-db", action="store_true", 
                      help="使用默认数据库路径而不是测试数据库")
    parser.add_argument("--model", help="指定向量化模型名称")
    parser.add_argument("--offline", action="store_true",
                      help="离线模式，使用随机向量而不是预训练模型")
    
    args = parser.parse_args()
    
    # 运行测试
    test_faiss_retrieval(
        use_test_db=not args.no_test_db,
        model_name=args.model,
        offline_mode=args.offline
    ) 