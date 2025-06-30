#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆系统集成测试
测试完整的记忆管道功能
"""

import os
import sys
import asyncio
import time
import logging

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.memory.pipeline import MemoryPipeline

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_memory_pipeline():
    """测试记忆管道完整功能"""
    print("=" * 50)
    print("记忆系统集成测试")
    print("=" * 50)
    
    # 初始化管道
    print("\n1. 初始化记忆管道...")
    pipeline = MemoryPipeline()
    
    # 确保异步组件初始化
    print("2. 初始化异步组件...")
    await pipeline.ensure_async_initialized()
    
    # 等待异步评估器启动
    await asyncio.sleep(2)
    
    # 获取系统状态
    print("\n3. 检查系统状态...")
    stats = pipeline.get_memory_stats()
    print(f"   系统状态: {stats}")
    
    # 测试对话序列
    test_dialogues = [
        ("你好，今天天气怎么样？", "你好！今天天气很不错，阳光明媚，适合外出活动。"),
        ("我在学习Python编程", "很好！Python是一门很实用的编程语言，有什么具体问题我可以帮助你。"),
        ("明天我要去面试一个软件工程师的职位", "祝你面试顺利！建议提前准备一些技术问题和项目经验分享。")
    ]
    
    print("\n4. 测试对话处理...")
    for i, (user_input, ai_response) in enumerate(test_dialogues, 1):
        print(f"\n   对话 {i}:")
        print(f"   用户: {user_input}")
        print(f"   AI: {ai_response}")
        
        # 测试查询增强
        enhanced_context = pipeline.enhance_query(user_input)
        print(f"   增强上下文长度: {len(enhanced_context)} 字符")
        
        # 存储交互
        pipeline.store_interaction(user_input, ai_response)
        print("   ✓ 已加入异步评估队列")
        
        # 短暂等待
        await asyncio.sleep(1)
    
    # 等待异步处理完成
    print("\n5. 等待异步处理完成...")
    await asyncio.sleep(10)  # 给足够时间让LLM处理
    
    # 检查最终状态
    print("\n6. 检查处理结果...")
    final_stats = pipeline.get_memory_stats()
    print(f"   最终状态: {final_stats}")
    
    # 测试记忆检索
    print("\n7. 测试记忆检索...")
    test_queries = ["Python", "面试", "天气"]
    
    for query in test_queries:
        enhanced_context = pipeline.enhance_query(query)
        lines = enhanced_context.split('\n')
        relevant_lines = [line for line in lines if line.strip() and not line.startswith('[')]
        print(f"   查询 '{query}' -> 找到 {len(relevant_lines)} 条相关信息")
    
    # 关闭管道
    print("\n8. 关闭管道...")
    await pipeline.shutdown()
    
    print("\n✓ 记忆系统集成测试完成")
    print("=" * 50)

async def test_async_evaluator_only():
    """仅测试异步评估器"""
    print("\n" + "=" * 50)
    print("异步评估器单独测试")
    print("=" * 50)
    
    from core.memory.init.db_manager import DatabaseManager
    from core.memory.evaluator.async_evaluator import AsyncMemoryEvaluator
    
    # 初始化数据库
    db_manager = DatabaseManager("data/memory.db")
    if not db_manager.initialize_database():
        print("❌ 数据库初始化失败")
        return
    
    # 初始化异步评估器
    evaluator = AsyncMemoryEvaluator(db_manager)
    await evaluator.start()
    
    print("✓ 异步评估器启动成功")
    
    # 测试数据
    test_data = [
        ("今天学习了Python的异步编程", "很好！异步编程是Python的重要特性，可以提高程序性能。"),
        ("明天要去公司面试", "祝你面试成功！记得准备好自我介绍和技术问题。"),
        ("你好", "你好！有什么可以帮助你的吗？")
    ]
    
    # 加入评估队列
    for user_input, ai_response in test_data:
        await evaluator.queue_dialogue_for_evaluation(user_input, ai_response)
        print(f"✓ 已加入队列: {user_input[:20]}...")
    
    # 等待处理完成
    print("\n等待评估完成...")
    await asyncio.sleep(15)
    
    # 检查队列状态
    status = evaluator.get_queue_status()
    print(f"队列状态: {status}")
    
    # 查询保存的记忆
    memories = db_manager.query("""
        SELECT content, weight, group_id, summary 
        FROM memories 
        ORDER BY timestamp DESC 
        LIMIT 10
    """)
    
    print(f"\n已保存记忆数量: {len(memories) if memories else 0}")
    if memories:
        for memory in memories:
            print(f"  - [{memory[1]}分] {memory[2]}: {memory[0][:30]}...")
    
    # 关闭
    await evaluator.stop()
    db_manager.close()
    
    print("✓ 异步评估器测试完成")

async def main():
    """主测试函数"""
    try:
        # 选择测试模式
        print("选择测试模式:")
        print("1. 完整集成测试")
        print("2. 仅测试异步评估器")
        
        choice = input("请选择 (1/2): ").strip()
        
        if choice == "1":
            await test_memory_pipeline()
        elif choice == "2":
            await test_async_evaluator_only()
        else:
            print("无效选择，运行完整测试...")
            await test_memory_pipeline()
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 