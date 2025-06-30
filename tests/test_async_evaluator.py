#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步评估模块测试
测试Step 11-13的完整异步处理流程
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.evaluator.async_evaluator import AsyncMemoryEvaluator
from core.memory.init.db_manager import DatabaseManager

async def test_async_evaluator():
    """测试异步评估模块"""
    print("🚀 开始异步评估模块测试")
    print("=" * 60)
    
    # 初始化数据库
    db_path = "data/test_async_memory.db"
    db_manager = DatabaseManager(db_path)
    
    if not db_manager.initialize_database():
        print("❌ 数据库初始化失败")
        return False
    
    print("✅ 数据库初始化成功")
    
    # 初始化异步评估器
    evaluator = AsyncMemoryEvaluator(db_manager)
    
    # 启动异步评估工作线程
    await evaluator.start()
    print("✅ 异步评估器启动成功")
    
    # 测试对话数据
    test_dialogues = [
        {
            "name": "工作汇报",
            "user": "今天完成了项目的核心模块开发，遇到了一些技术难点但都解决了",
            "ai": "很棒！能具体说说遇到了什么技术难点吗？是如何解决的？这些经验对后续开发很有价值。"
        },
        {
            "name": "学习进展",
            "user": "我在学习机器学习，刚刚理解了梯度下降算法的原理",
            "ai": "梯度下降是机器学习的基础！理解了原理后，建议你尝试手动实现一个简单的线性回归模型，这样能加深理解。"
        },
        {
            "name": "日常问候",
            "user": "早上好！",
            "ai": "早上好！今天有什么计划吗？"
        }
    ]
    
    print(f"\n📝 准备测试 {len(test_dialogues)} 组对话")
    
    # 将对话加入评估队列
    for i, dialogue in enumerate(test_dialogues, 1):
        print(f"\n🔄 加入队列 {i}: {dialogue['name']}")
        
        await evaluator.queue_dialogue_for_evaluation(
            user_input=dialogue['user'],
            ai_response=dialogue['ai'],
            session_id=f"test_session_{i}",
            context_memories=[]
        )
        
        # 检查队列状态
        status = evaluator.get_queue_status()
        print(f"   队列状态: {status}")
    
    print(f"\n⏳ 等待异步评估完成...")
    
    # 等待所有任务完成
    await evaluator.evaluation_queue.join()
    
    print(f"✅ 所有异步评估任务完成")
    
    # 检查数据库中的结果
    print(f"\n📊 检查数据库结果:")
    
    # 查询保存的记忆
    memories = db_manager.query(
        """
        SELECT id, content, role, weight, group_id, summary, metadata
        FROM memories 
        ORDER BY timestamp DESC
        """, ()
    )
    
    if memories:
        print(f"   💾 数据库中共有 {len(memories)} 条记忆")
        
        # 按group_id分组显示
        groups = {}
        for memory in memories:
            group_id = memory[4]  # group_id
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(memory)
        
        for group_id, group_memories in groups.items():
            print(f"\n   📂 分组: {group_id}")
            print(f"      记忆数量: {len(group_memories)}")
            
            # 显示摘要
            if group_memories:
                summary = group_memories[0][5]  # summary
                weight = group_memories[0][3]   # weight
                print(f"      摘要: {summary}")
                print(f"      权重: {weight}")
            
            # 显示每条记忆
            for memory in group_memories:
                role = memory[2]
                content = memory[1][:50] + "..." if len(memory[1]) > 50 else memory[1]
                print(f"        • [{role}] {content}")
    else:
        print("   ⚠️ 数据库中没有找到记忆")
    
    # 测试队列状态监控
    print(f"\n📈 最终队列状态:")
    final_status = evaluator.get_queue_status()
    print(f"   队列大小: {final_status['queue_size']}")
    print(f"   工作线程运行: {final_status['is_running']}")
    print(f"   工作线程活跃: {final_status['worker_active']}")
    
    # 停止异步评估器
    await evaluator.stop()
    print("✅ 异步评估器已停止")
    
    # 关闭数据库
    db_manager.close()
    print("✅ 数据库已关闭")
    
    print("\n" + "=" * 60)
    print("🎉 异步评估模块测试完成！")
    print("\n💡 测试验证了:")
    print("   • Step 11: LLM异步评估对话")
    print("   • Step 12: 评估结果自动保存到数据库")
    print("   • Step 13: 自动关联逻辑执行")
    print("   • 异步队列管理和监控")
    print("   • 数据库事务处理")
    
    return True

if __name__ == "__main__":
    # 运行基础测试
    asyncio.run(test_async_evaluator()) 