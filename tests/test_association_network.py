#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
关联网络功能测试脚本
测试Step 5：关联网络拓展的核心功能
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
from core.memory.association.network import AssociationNetwork

def test_association_network(use_test_db=True, model_name=None, offline_mode=False):
    """
    测试关联网络功能
    
    参数:
        use_test_db: 是否使用测试数据库
        model_name: 向量化模型名称
        offline_mode: 是否使用离线模式
    """
    print("===== 关联网络功能测试 =====")
    
    # 设置测试路径
    if use_test_db:
        test_db_path = os.path.join("assets", "test_association_memory.db")
        test_index_path = os.path.join("data", "vectors", "test_association_memory_index.bin")
        test_cache_dir = os.path.join("data", "memory", "test_association_cache")
        
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
    
    # 初始化关联网络
    print("\n2. 初始化关联网络")
    try:
        association_network = AssociationNetwork(db_manager=memory_store.db_manager)
        print("关联网络初始化成功")
    except Exception as e:
        print(f"初始化关联网络失败: {e}")
        return False
    
    # 准备测试数据 - 创建有关联性的记忆数据
    print("\n3. 添加有关联性的测试记忆")
    test_memories = [
        # Python学习主题群
        {
            "content": "开始学习Python编程，从基础语法开始",
            "category": "programming",
            "importance": 0.7
        },
        {
            "content": "学会了Python的列表和字典操作，很有用",
            "category": "programming", 
            "importance": 0.6
        },
        {
            "content": "用Python写了第一个爬虫程序，抓取网页数据",
            "category": "programming",
            "importance": 0.8
        },
        
        # 机器学习主题群
        {
            "content": "开始学习机器学习，了解了监督学习和无监督学习",
            "category": "ai",
            "importance": 0.8
        },
        {
            "content": "学习了线性回归算法，用Python实现了一个简单的模型",
            "category": "ai",
            "importance": 0.7
        },
        {
            "content": "尝试用scikit-learn库做数据分析，感觉很强大",
            "category": "ai", 
            "importance": 0.6
        },
        
        # 项目经验主题群
        {
            "content": "参与了公司的AI项目，负责数据预处理部分",
            "category": "work",
            "importance": 0.9
        },
        {
            "content": "项目中遇到了数据清洗的问题，学会了pandas的使用",
            "category": "work",
            "importance": 0.7
        },
        {
            "content": "项目成功上线，获得了团队的认可，很有成就感",
            "category": "work",
            "importance": 0.8
        },
        
        # 生活记录
        {
            "content": "今天天气不错，去公园散步思考编程问题",
            "category": "life",
            "importance": 0.4
        },
        {
            "content": "和朋友讨论了人工智能的发展前景，很有启发",
            "category": "life",
            "importance": 0.6
        },
        {
            "content": "看了一本关于算法的书，对递归有了更深的理解",
            "category": "study",
            "importance": 0.7
        }
    ]
    
    memory_ids = []
    memories_data = []
    
    # 添加记忆并收集数据
    for i, memory_data in enumerate(test_memories):
        memory_id = memory_store.add_memory(
            content=memory_data["content"],
            source="test_association",
            importance=memory_data["importance"],
            metadata={"category": memory_data["category"]}
        )
        
        if memory_id:
            memory_ids.append(memory_id)
            
            # 获取完整的记忆数据
            full_memory = memory_store.get_memory(memory_id)
            if full_memory:
                memories_data.append(full_memory)
                print(f"添加记忆 {i+1:2d}: [{memory_data['category']}] {memory_data['content'][:40]}...")
    
    print(f"\n成功添加 {len(memory_ids)} 条记忆")
    
    if not memory_ids:
        print("添加记忆失败，测试终止")
        return False
    
    # 测试自动关联建立
    print("\n4. 测试自动关联建立")
    
    # 为每个记忆建立关联
    total_associations = 0
    for i, memory_id in enumerate(memory_ids):
        memory_content = memories_data[i]
        
        # 获取其他记忆作为候选
        other_memories = [m for j, m in enumerate(memories_data) if j != i]
        
        # 自动创建关联
        associations = association_network.auto_create_associations(
            memory_id, memory_content, other_memories
        )
        
        total_associations += len(associations)
        
        if associations:
            print(f"记忆 {i+1} 建立了 {len(associations)} 个关联:")
            for assoc in associations[:3]:  # 只显示前3个
                target_memory = next((m for m in other_memories if m["memory_id"] == assoc["target_id"]), None)
                if target_memory:
                    print(f"  → [{assoc['association_type']}] 强度:{assoc['strength']:.3f} | {target_memory['content'][:30]}...")
    
    print(f"\n总共建立了 {total_associations} 个关联")
    
    # 测试直接关联检索
    print("\n5. 测试直接关联检索 (depth=1)")
    
    test_memory_index = 0  # 测试第一个记忆的关联
    test_memory_id = memory_ids[test_memory_index]
    test_memory_content = memories_data[test_memory_index]["content"]
    
    print(f"测试记忆: {test_memory_content}")
    
    direct_associations = association_network.get_related_memories(
        test_memory_id, depth=1, min_strength=0.3
    )
    
    print(f"找到 {len(direct_associations)} 个直接关联:")
    for i, assoc in enumerate(direct_associations):
        print(f"  关联 {i+1}: [{assoc['association_type']}] 强度:{assoc['strength']:.3f}")
        print(f"           路径: {' → '.join(assoc['association_path'])}")
        print(f"           内容: {assoc['content'][:50]}...")
        print()
    
    # 测试二度关联检索
    print("\n6. 测试二度关联检索 (depth=2)")
    
    two_hop_associations = association_network.get_related_memories(
        test_memory_id, depth=2, min_strength=0.2
    )
    
    print(f"找到 {len(two_hop_associations)} 个关联记忆 (包含直接和间接):")
    
    direct_count = 0
    indirect_count = 0
    
    for i, assoc in enumerate(two_hop_associations):
        is_two_hop = assoc.get("is_two_hop", False)
        if is_two_hop:
            indirect_count += 1
            hop_type = "二度关联"
        else:
            direct_count += 1
            hop_type = "直接关联"
        
        print(f"  {hop_type} {i+1}: [{assoc['association_type']}] 强度:{assoc['strength']:.3f}")
        print(f"               路径: {' → '.join(assoc['association_path'])}")
        print(f"               内容: {assoc['content'][:50]}...")
        print()
    
    print(f"统计: 直接关联 {direct_count} 个，二度关联 {indirect_count} 个")
    
    # 测试关联强度计算
    print("\n7. 测试关联强度计算")
    
    if len(memories_data) >= 2:
        memory1 = memories_data[0]
        memory2 = memories_data[1]
        
        strength = association_network.calculate_association_strength(memory1, memory2)
        
        print(f"记忆1: {memory1['content'][:40]}...")
        print(f"记忆2: {memory2['content'][:40]}...")
        print(f"计算得到的关联强度: {strength:.4f}")
        
        # 测试不同类别记忆的关联强度
        programming_memory = next((m for m in memories_data if m.get("metadata", {}).get("category") == "programming"), None)
        life_memory = next((m for m in memories_data if m.get("metadata", {}).get("category") == "life"), None)
        
        if programming_memory and life_memory:
            cross_strength = association_network.calculate_association_strength(programming_memory, life_memory)
            print(f"\n跨类别关联强度测试:")
            print(f"编程记忆: {programming_memory['content'][:40]}...")
            print(f"生活记忆: {life_memory['content'][:40]}...")
            print(f"跨类别关联强度: {cross_strength:.4f}")
    
    # 测试关联网络统计
    print("\n8. 测试关联网络统计")
    
    stats = association_network.get_association_stats()
    
    print("关联网络统计信息:")
    print(f"  总关联数: {stats.get('total_associations', 0)}")
    
    type_dist = stats.get('type_distribution', {})
    if type_dist:
        print("  关联类型分布:")
        for assoc_type, count in type_dist.items():
            print(f"    {assoc_type}: {count}")
    
    strength_dist = stats.get('strength_distribution', {})
    if strength_dist:
        print("  关联强度分布:")
        print(f"    强关联 (≥0.8): {strength_dist.get('strong', 0)}")
        print(f"    中等关联 (0.6-0.8): {strength_dist.get('medium', 0)}")
        print(f"    弱关联 (<0.6): {strength_dist.get('weak', 0)}")
    
    # 测试关联强度更新
    print("\n9. 测试关联强度动态更新")
    
    if len(memory_ids) >= 2:
        source_id = memory_ids[0]
        target_id = memory_ids[1]
        
        # 获取更新前的关联强度
        before_associations = association_network.get_related_memories(source_id, depth=1)
        before_strength = None
        for assoc in before_associations:
            if assoc["memory_id"] == target_id:
                before_strength = assoc["strength"]
                break
        
        if before_strength is not None:
            print(f"更新前关联强度: {before_strength:.4f}")
            
            # 模拟使用频率增加
            association_network.update_association_strength(source_id, target_id, 0.05)
            
            # 获取更新后的关联强度
            after_associations = association_network.get_related_memories(source_id, depth=1)
            after_strength = None
            for assoc in after_associations:
                if assoc["memory_id"] == target_id:
                    after_strength = assoc["strength"]
                    break
            
            if after_strength is not None:
                print(f"更新后关联强度: {after_strength:.4f}")
                print(f"强度变化: +{after_strength - before_strength:.4f}")
    
    # 测试查询融合评分
    print("\n10. 测试查询融合评分")
    
    query = "Python机器学习项目"
    print(f"查询: {query}")
    
    # 获取直接相似度搜索结果
    direct_results = memory_store.search_similar(query, limit=5)
    
    # 获取关联拓展结果
    if direct_results:
        primary_memory_id = direct_results[0]["memory_id"]
        associated_memories = association_network.get_related_memories(
            primary_memory_id, depth=2, min_strength=0.3
        )
        
        print(f"\n直接搜索结果:")
        for i, result in enumerate(direct_results[:3]):
            print(f"  结果 {i+1}: [相似度:{result['similarity']:.4f}] {result['content'][:50]}...")
        
        print(f"\n关联拓展结果:")
        for i, assoc in enumerate(associated_memories[:3]):
            # 模拟融合评分计算
            direct_similarity = 0.4  # 假设的直接相似度
            association_strength = assoc["strength"]
            
            # 融合评分: 直接相似度 × 0.7 + 关联强度 × 0.3
            fusion_score = direct_similarity * 0.7 + association_strength * 0.3
            
            print(f"  关联 {i+1}: [融合分:{fusion_score:.4f}] [关联强度:{association_strength:.4f}]")
            print(f"           {assoc['content'][:50]}...")
    
    # 关闭记忆存储管理器
    memory_store.close()
    print("\n记忆存储管理器已关闭")
    
    # 清理测试文件（可选）
    if use_test_db and False:  # 设置为True以启用清理
        print("\n11. 清理测试文件")
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
    
    print("\n===== 关联网络功能测试完成 =====")
    return True

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="测试关联网络功能")
    parser.add_argument("--no-test-db", action="store_true", 
                      help="使用默认数据库路径而不是测试数据库")
    parser.add_argument("--model", help="指定向量化模型名称")
    parser.add_argument("--offline", action="store_true",
                      help="离线模式，使用随机向量而不是预训练模型")
    
    args = parser.parse_args()
    
    # 运行测试
    test_association_network(
        use_test_db=not args.no_test_db,
        model_name=args.model,
        offline_mode=args.offline
    )