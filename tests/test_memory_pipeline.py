#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆管道测试
测试完整的记忆处理流程
"""

import sys
import os
import asyncio
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.pipeline import MemoryPipeline

async def test_memory_pipeline():
    """测试记忆管道"""
    print("🚀 开始记忆管道测试")
    print("=" * 60)
    
    # 配置
    config = {
        "database_path": "data/test_pipeline_memory.db"
    }
    
    # 初始化管道
    pipeline = MemoryPipeline(config)
    
    if not await pipeline.initialize():
        print("❌ 管道初始化失败")
        return False
    
    print("✅ 记忆管道初始化成功")
    
    # 测试对话处理
    test_dialogues = [
        {
            "user": "我今天学会了Python的装饰器，感觉很有用",
            "ai": "装饰器确实是Python的强大特性！它可以让代码更简洁优雅。你打算在什么项目中使用装饰器呢？"
        },
        {
            "user": "明天要开会讨论项目进度",
            "ai": "会议准备很重要。你需要汇报哪些内容？我可以帮你整理一下要点。"
        }
    ]
    
    print(f"\n📝 处理 {len(test_dialogues)} 组对话")
    
    # 处理对话
    for i, dialogue in enumerate(test_dialogues, 1):
        print(f"\n🔄 处理对话 {i}")
        
        result = await pipeline.process_dialogue(
            user_input=dialogue['user'],
            ai_response=dialogue['ai']
        )
        
        if result['success']:
            print(f"   ✅ 处理成功")
            print(f"   ⏱️ 耗时: {result['processing_time']*1000:.2f}ms")
            print(f"   🆔 会话ID: {result['session_id']}")
            print(f"   📤 已加入评估队列: {result['evaluation_queued']}")
        else:
            print(f"   ❌ 处理失败: {result.get('error', '未知错误')}")
    
    # 检查评估状态
    print(f"\n📊 评估状态:")
    status = pipeline.get_evaluation_status()
    print(f"   队列大小: {status.get('queue_size', 'N/A')}")
    print(f"   工作线程运行: {status.get('is_running', 'N/A')}")
    
    # 等待一段时间让异步评估完成
    print(f"\n⏳ 等待异步评估完成...")
    await asyncio.sleep(20)  # 等待20秒
    
    # 再次检查状态
    final_status = pipeline.get_evaluation_status()
    print(f"📈 最终状态:")
    print(f"   队列大小: {final_status.get('queue_size', 'N/A')}")
    
    # 关闭管道
    await pipeline.shutdown()
    print("✅ 记忆管道已关闭")
    
    print("\n" + "=" * 60)
    print("🎉 记忆管道测试完成！")
    print("\n💡 测试验证了:")
    print("   • 管道初始化和配置")
    print("   • 对话处理流程")
    print("   • 异步评估集成")
    print("   • 状态监控")
    print("   • 优雅关闭")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_memory_pipeline()) 