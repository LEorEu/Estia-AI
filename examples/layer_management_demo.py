#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版分层记忆管理演示

展示如何在现有EstiaMemorySystem中使用分层管理功能，
无需复杂的layer模块
"""

import sys
import os
import time
import asyncio
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.estia_memory import create_estia_memory

async def demo_layered_memory_management():
    """演示分层记忆管理功能"""
    print("🧠 简化版分层记忆管理演示")
    print("=" * 50)
    
    # 1. 初始化记忆系统
    print("\n1. 初始化记忆系统...")
    memory_system = create_estia_memory(enable_advanced=True)
    
    if not memory_system.initialized:
        print("❌ 记忆系统初始化失败")
        return
    
    print("✅ 记忆系统初始化成功")
    
    # 2. 模拟不同权重的记忆
    print("\n2. 添加不同层级的测试记忆...")
    
    test_memories = [
        {"content": "用户的真实姓名是张三", "weight": 9.5, "type": "user_info"},
        {"content": "用户是一名Python开发者", "weight": 9.0, "type": "user_info"},
        {"content": "用户喜欢喝咖啡，特别是拿铁", "weight": 8.5, "type": "preference"},
        {"content": "用户住在北京朝阳区", "weight": 8.0, "type": "user_info"},
        {"content": "用户最近在学习机器学习", "weight": 7.5, "type": "interest"},
        {"content": "用户今天工作很忙", "weight": 5.0, "type": "daily_status"},
        {"content": "用户说今天天气不错", "weight": 3.0, "type": "casual"},
        {"content": "用户打了个招呼", "weight": 2.0, "type": "greeting"},
    ]
    
    # 添加测试记忆
    session_id = memory_system.get_current_session_id()
    for i, memory_data in enumerate(test_memories):
        memory_id = f"test_memory_{i+1}"
        
        # 直接添加到数据库进行测试
        timestamp = time.time()
        try:
            query = """
                INSERT OR REPLACE INTO memories 
                (id, content, type, role, session_id, timestamp, weight, last_accessed) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            memory_system.db_manager.execute_query(
                query, 
                (memory_id, memory_data["content"], memory_data["type"], 
                 "user", session_id, timestamp, memory_data["weight"], timestamp)
            )
            
            layer = memory_system.get_memory_layer(memory_data["weight"])
            print(f"   • {memory_data['content'][:40]}... → {layer} (权重: {memory_data['weight']})")
            
        except Exception as e:
            print(f"   ❌ 添加记忆失败: {e}")
    
    # 3. 获取并显示分层统计
    print("\n3. 分层统计信息...")
    layer_stats = memory_system.get_memory_lifecycle_stats()
    
    if layer_stats:
        print(f"   总记忆数量: {layer_stats.get('total_memories', 0)}")
        print(f"   分层分布:")
        
        for layer, stats in layer_stats.get('layer_statistics', {}).items():
            print(f"     • {layer}: {stats['count']}条记忆 (平均权重: {stats['avg_weight']})")
    
    # 4. 演示分层检索
    print("\n4. 测试分层检索功能...")
    
    # 获取所有测试记忆
    query = "SELECT * FROM memories WHERE id LIKE 'test_memory_%' ORDER BY weight DESC"
    results = memory_system.db_manager.execute_query(query)
    
    if results:
        memories = []
        for row in results:
            memories.append({
                'id': row[0],
                'content': row[1],
                'type': row[2],
                'weight': row[6]
            })
        
        # 获取分层信息
        layered_info = memory_system.get_layered_context_info(memories)
        
        print("   分层检索结果:")
        for layer, memory_list in layered_info.get('layered_memories', {}).items():
            if memory_list:
                print(f"     {layer} ({len(memory_list)}条):")
                for memory in memory_list:
                    print(f"       - [权重: {memory['weight']:.1f}] {memory['content'][:50]}...")
    
    # 5. 演示增强上下文构建
    print("\n5. 测试增强上下文构建...")
    
    if results:
        memories = [{'id': row[0], 'content': row[1], 'weight': row[6]} for row in results[:5]]
        
        enhanced_context = memory_system._build_enhanced_context(
            user_input="介绍一下我自己",
            memories=memories,
            historical_context={}
        )
        
        print("   增强上下文预览:")
        context_lines = enhanced_context.split('\n')
        for line in context_lines[:15]:  # 只显示前15行
            print(f"     {line}")
        if len(context_lines) > 15:
            print(f"     ... (共{len(context_lines)}行)")
    
    # 6. 演示过期记忆清理
    print("\n6. 测试过期记忆清理...")
    
    cleanup_result = memory_system.cleanup_expired_memories(days_threshold=0)  # 测试用：0天阈值
    print(f"   清理结果: {cleanup_result['message']}")
    
    # 7. 获取完整系统统计
    print("\n7. 完整系统统计...")
    
    system_stats = memory_system.get_system_stats()
    
    print(f"   系统状态:")
    print(f"     • 初始化状态: {system_stats['initialized']}")
    print(f"     • 高级功能: {system_stats['advanced_features']}")
    print(f"     • 总记忆数: {system_stats.get('total_memories', 0)}")
    
    layer_statistics = system_stats.get('layer_statistics', {})
    if layer_statistics and 'layer_statistics' in layer_statistics:
        print(f"   分层分布:")
        for layer, stats in layer_statistics['layer_statistics'].items():
            print(f"     • {layer}: {stats['count']}条")
    
    # 8. 清理测试数据
    print("\n8. 清理测试数据...")
    try:
        cleanup_query = "DELETE FROM memories WHERE id LIKE 'test_memory_%'"
        memory_system.db_manager.execute_query(cleanup_query)
        print("   ✅ 测试数据已清理")
    except Exception as e:
        print(f"   ⚠️ 清理测试数据失败: {e}")
    
    # 关闭系统
    await memory_system.shutdown()
    print("\n✅ 演示完成！")

async def demo_query_enhancement():
    """演示查询增强功能"""
    print("\n🔍 查询增强演示")
    print("=" * 30)
    
    memory_system = create_estia_memory(enable_advanced=True)
    
    if not memory_system.initialized:
        print("❌ 记忆系统初始化失败")
        return
    
    # 模拟用户查询
    user_queries = [
        "我是谁？",
        "我喜欢什么？",
        "告诉我今天的情况",
        "我的工作是什么？"
    ]
    
    for query in user_queries:
        print(f"\n用户查询: {query}")
        
        try:
            enhanced_context = memory_system.enhance_query(
                user_input=query,
                context={"session_id": memory_system.get_current_session_id()}
            )
            
            print("增强上下文预览:")
            context_lines = enhanced_context.split('\n')
            for line in context_lines[:10]:
                print(f"  {line}")
            if len(context_lines) > 10:
                print(f"  ... (共{len(context_lines)}行)")
                
        except Exception as e:
            print(f"查询增强失败: {e}")
    
    await memory_system.shutdown()

if __name__ == "__main__":
    print("🚀 启动简化版分层记忆管理演示")
    
    try:
        # 运行主演示
        asyncio.run(demo_layered_memory_management())
        
        # 运行查询演示
        asyncio.run(demo_query_enhancement())
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示运行失败: {e}")
        import traceback
        traceback.print_exc() 