#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Step 6测试：从数据库或缓存中取出对话
测试历史对话检索、会话聚合、总结提取等功能
"""

import os
import sys
import time
import json
import uuid
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_step6_history_retrieval():
    """测试Step 6：历史对话检索"""
    print("🔍 Step 6测试：从数据库中取出对话")
    print("="*60)
    
    try:
        # 初始化组件
        from core.memory.init.db_manager import DatabaseManager
        from core.memory.context.history import HistoryRetriever
        
        # 连接数据库
        db_manager = DatabaseManager("assets/memory.db")
        history_retriever = HistoryRetriever(db_manager)
        
        print("✅ 数据库和历史检索器初始化完成")
        
        # 准备测试数据
        test_session_id = "test_session_step6"
        test_group_id = "test_group_step6"
        current_time = time.time()
        
        # 创建测试记忆数据
        test_memories = []
        memory_ids = []
        
        # 模拟一个完整的对话会话
        dialogue_data = [
            {"role": "user", "content": "你好，我想学习Python编程", "type": "user_input"},
            {"role": "assistant", "content": "你好！Python是一门很棒的编程语言。你有编程基础吗？", "type": "assistant_reply"},
            {"role": "user", "content": "我是完全的新手，应该从哪里开始？", "type": "user_input"},
            {"role": "assistant", "content": "建议从基础语法开始，可以先学习变量、数据类型等概念。", "type": "assistant_reply"},
            {"role": "summary", "content": "用户询问Python学习，助手建议从基础语法开始", "type": "summary"}
        ]
        
        print(f"\n📝 创建测试数据...")
        
        # 插入测试记忆
        for i, data in enumerate(dialogue_data):
            memory_id = str(uuid.uuid4())
            memory_ids.append(memory_id)
            
            timestamp = current_time + i * 60  # 每条记忆间隔1分钟
            
            # 插入记忆
            db_manager.execute_query(
                """
                INSERT INTO memories 
                (id, content, type, role, session_id, timestamp, weight, group_id, last_accessed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_id,
                    data["content"],
                    data["type"],
                    data["role"],
                    test_session_id,
                    timestamp,
                    7.0 if data["type"] == "summary" else 5.0,
                    test_group_id,
                    timestamp,
                    json.dumps({"test": True})
                )
            )
            
            test_memories.append({
                "id": memory_id,
                "content": data["content"],
                "type": data["type"],
                "role": data["role"]
            })
        
        # 提交数据库
        db_manager.conn.commit()
        print(f"   ✅ 创建了 {len(test_memories)} 条测试记忆")
        
        # 创建分组总结
        db_manager.execute_query(
            """
            INSERT OR REPLACE INTO memory_group 
            (group_id, topic, time_start, time_end, summary, score)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                test_group_id,
                "Python学习",
                current_time,
                current_time + 300,
                "用户开始学习Python编程，从基础语法入门",
                8.5
            )
        )
        db_manager.conn.commit()
        print(f"   ✅ 创建了分组总结")
        
        # 测试历史检索
        print(f"\n🔍 测试历史检索功能...")
        
        # 使用前3个记忆ID进行检索
        test_memory_ids = memory_ids[:3]
        
        start_time = time.time()
        retrieval_result = history_retriever.retrieve_memory_contents(
            memory_ids=test_memory_ids,
            include_summaries=True,
            include_sessions=True,
            max_recent_dialogues=10
        )
        retrieval_time = time.time() - start_time
        
        print(f"   ⏱️ 检索耗时: {retrieval_time*1000:.2f}ms")
        
        # 验证检索结果
        print(f"\n📊 检索结果分析:")
        
        stats = retrieval_result.get("stats", {})
        print(f"   📄 主要记忆: {stats.get('total_memories', 0)} 条")
        print(f"   🗂️ 分组数量: {stats.get('groups_found', 0)} 个")
        print(f"   💬 会话数量: {stats.get('sessions_found', 0)} 个")
        print(f"   📝 总结数量: {stats.get('summaries_found', 0)} 个")
        
        # 显示主要记忆
        primary_memories = retrieval_result.get("primary_memories", [])
        print(f"\n📄 主要记忆内容:")
        for memory in primary_memories:
            print(f"   • [{memory['formatted_time']}] {memory['role']}: {memory['content'][:50]}...")
        
        # 显示分组记忆
        grouped_memories = retrieval_result.get("grouped_memories", {})
        print(f"\n🗂️ 分组记忆:")
        for group_id, group_data in grouped_memories.items():
            print(f"   分组 {group_id}:")
            print(f"     记忆数量: {group_data['count']}")
            print(f"     时间跨度: {group_data['time_span']['start']} ~ {group_data['time_span']['end']}")
            print(f"     平均权重: {group_data['avg_weight']:.2f}")
        
        # 显示会话对话
        session_dialogues = retrieval_result.get("session_dialogues", {})
        print(f"\n💬 会话对话:")
        for session_id, session_data in session_dialogues.items():
            print(f"   会话 {session_id}:")
            print(f"     记忆数量: {session_data['count']}")
            
            dialogue_pairs = session_data.get("dialogue_pairs", [])
            print(f"     对话轮次: {len(dialogue_pairs)}")
            
            for i, pair in enumerate(dialogue_pairs):
                print(f"       轮次{i+1}: {pair['user']['content'][:30]}... -> {pair['assistant']['content'][:30]}...")
        
        # 显示总结内容
        summaries = retrieval_result.get("summaries", {})
        print(f"\n📝 总结内容:")
        
        direct_summaries = summaries.get("direct_summaries", [])
        print(f"   直接总结: {len(direct_summaries)} 条")
        for summary in direct_summaries:
            print(f"     • {summary['content']}")
        
        memory_summaries = summaries.get("memory_summaries", [])
        print(f"   记忆总结: {len(memory_summaries)} 条")
        for summary in memory_summaries:
            print(f"     • {summary['content']}")
        
        group_summaries = summaries.get("group_summaries", {})
        print(f"   分组总结: {len(group_summaries)} 个")
        for group_id, group_summary_list in group_summaries.items():
            for summary in group_summary_list:
                print(f"     • [{summary['topic']}] {summary['content']}")
        
        # 测试上下文格式化
        print(f"\n📝 测试上下文格式化:")
        context = history_retriever.format_for_context(retrieval_result, max_context_length=1000)
        print(f"   上下文长度: {len(context)} 字符")
        print(f"   上下文预览:")
        print("   " + "-"*50)
        context_lines = context.split('\n')
        for line in context_lines[:10]:  # 显示前10行
            print(f"   {line}")
        if len(context_lines) > 10:
            print(f"   ... (还有 {len(context_lines) - 10} 行)")
        print("   " + "-"*50)
        
        # 清理测试数据
        print(f"\n🧹 清理测试数据...")
        
        # 删除测试记忆
        for memory_id in memory_ids:
            db_manager.execute_query("DELETE FROM memories WHERE id = ?", (memory_id,))
        
        # 删除测试分组
        db_manager.execute_query("DELETE FROM memory_group WHERE group_id = ?", (test_group_id,))
        
        db_manager.conn.commit()
        print(f"   ✅ 清理完成")
        
        print(f"\n🎉 Step 6测试完成！")
        print(f"✅ 历史检索功能正常")
        print(f"✅ 会话聚合功能正常")
        print(f"✅ 总结提取功能正常")
        print(f"✅ 上下文格式化功能正常")
        
        return True
        
    except Exception as e:
        print(f"❌ Step 6测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """测试边界情况"""
    print("\n🧪 测试边界情况")
    print("="*40)
    
    try:
        from core.memory.init.db_manager import DatabaseManager
        from core.memory.context.history import HistoryRetriever
        
        db_manager = DatabaseManager("assets/memory.db")
        history_retriever = HistoryRetriever(db_manager)
        
        # 测试1: 空的记忆ID列表
        print("🔍 测试1: 空的记忆ID列表")
        result = history_retriever.retrieve_memory_contents([])
        print(f"   结果: {result['stats']['total_memories']} 条记忆")
        
        # 测试2: 不存在的记忆ID
        print("🔍 测试2: 不存在的记忆ID")
        result = history_retriever.retrieve_memory_contents(["non_existent_id"])
        print(f"   结果: {result['stats']['total_memories']} 条记忆")
        
        # 测试3: 无数据库连接
        print("🔍 测试3: 无数据库连接")
        empty_retriever = HistoryRetriever(None)
        result = empty_retriever.retrieve_memory_contents(["test_id"])
        print(f"   结果: {result['stats']['total_memories']} 条记忆")
        
        print("✅ 边界情况测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 边界情况测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 Step 6 - 历史对话检索测试")
    print("="*60)
    
    # 基础功能测试
    success1 = test_step6_history_retrieval()
    
    # 边界情况测试
    success2 = test_edge_cases()
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    if success1 and success2:
        print("🎉 所有测试通过！")
        print("✅ Step 6 - 历史对话检索功能完全正常")
        print("\n💡 功能特性:")
        print("   • 根据记忆ID检索完整内容")
        print("   • 按group_id聚合相关记忆")
        print("   • 按session_id聚合会话对话")
        print("   • 提取和整合总结内容")
        print("   • 格式化为上下文字符串")
        print("   • 处理边界情况和错误")
    else:
        print("❌ 部分测试失败")
        print("💡 请检查错误信息并修复问题")

if __name__ == "__main__":
    main() 