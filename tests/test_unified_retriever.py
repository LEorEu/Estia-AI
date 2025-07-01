#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一检索引擎测试
"""

import asyncio
import time
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_unified_retriever():
    """测试统一检索引擎"""
    
    print("🧪 统一检索引擎测试")
    print("=" * 50)
    
    try:
        # 1. 导入组件
        print("📦 导入组件...")
        from core.memory.manager import create_memory_manager
        from core.memory.unified_retriever import create_unified_retriever
        
        # 2. 创建记忆管理器
        print("🧠 创建记忆管理器...")
        memory_manager = create_memory_manager(advanced=True)
        
        # 3. 创建统一检索引擎
        print("🔍 创建统一检索引擎...")
        retriever = create_unified_retriever(memory_manager, enable_batch=True)
        
        # 4. 添加测试数据
        print("📝 添加测试数据...")
        test_memories = [
            "我喜欢学习人工智能和机器学习",
            "今天天气很好，适合出去散步",
            "Python是一门很棒的编程语言",
            "深度学习在图像识别方面表现出色",
            "我正在开发一个AI助手项目"
        ]
        
        for i, content in enumerate(test_memories):
            memory_id = memory_manager.store_memory(
                content=content,
                role="user",
                importance=5.0 + i,
                memory_type="test"
            )
            print(f"  ✅ 存储记忆: {memory_id}")
        
        # 5. 测试单个查询
        print("\n🔍 测试单个查询...")
        start_time = time.time()
        
        results = await retriever.unified_search(
            query="人工智能学习",
            limit=3,
            min_importance=4.0
        )
        
        query_time = time.time() - start_time
        print(f"⚡ 查询耗时: {query_time*1000:.2f}ms")
        print(f"📊 检索结果: {len(results)}条")
        
        for i, result in enumerate(results):
            print(f"  {i+1}. [{result.layer}] 重要性:{result.importance:.1f} 相关性:{result.relevance_score:.3f}")
            print(f"     内容: {result.content[:50]}...")
        
        # 6. 测试批量查询
        print("\n📦 测试批量查询...")
        batch_queries = [
            "编程语言",
            "天气情况", 
            "AI项目开发"
        ]
        
        start_time = time.time()
        batch_results = await retriever.batch_unified_search(batch_queries, limit=2)
        batch_time = time.time() - start_time
        
        print(f"⚡ 批量查询耗时: {batch_time*1000:.2f}ms")
        print(f"📊 批量结果:")
        
        for query, results in batch_results.items():
            print(f"  查询: '{query}' -> {len(results)}条结果")
        
        # 7. 检索统计
        print("\n📈 检索统计:")
        stats = retriever.get_retrieval_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
        
        print("\n✅ 统一检索引擎测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_unified_retriever()) 