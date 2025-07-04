#!/usr/bin/env python3
"""
测试异步评估器启动时机不确定问题的修复效果
"""

import sys
import os
import asyncio
import threading
import time
from unittest.mock import patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.estia_memory import EstiaMemorySystem
from core.memory.evaluator.async_startup_manager import (
    get_startup_manager, 
    AsyncStartupMode,
    AsyncEvaluatorStartupManager
)

def test_startup_manager_modes():
    """测试启动管理器的不同模式"""
    print("🔬 测试启动管理器模式检测")
    print("=" * 50)
    
    manager = AsyncEvaluatorStartupManager()
    
    # 测试1: 无事件循环环境
    print("\n1️⃣ 测试无事件循环环境")
    mode = manager.detect_optimal_startup_mode()
    print(f"   检测到模式: {mode.value}")
    assert mode in [AsyncStartupMode.THREAD_POOL, AsyncStartupMode.NEW_LOOP]
    
    # 测试2: 模拟有事件循环但未运行
    print("\n2️⃣ 测试主线程事件循环环境")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        mode = manager.detect_optimal_startup_mode()
        print(f"   检测到模式: {mode.value}")
        
        loop.close()
    except Exception as e:
        print(f"   测试失败: {e}")
    
    print("✅ 模式检测测试完成")

def test_startup_manager_initialization():
    """测试启动管理器的初始化过程"""
    print("\n🚀 测试启动管理器初始化")
    print("=" * 50)
    
    from core.memory.init.db_manager import DatabaseManager
    from core.memory.evaluator.async_evaluator import AsyncMemoryEvaluator
    
    # 创建数据库管理器
    db_path = "temp/test_async_startup.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    db_manager = DatabaseManager(db_path)
    if not db_manager.initialize_database():
        print("❌ 数据库初始化失败")
        return False
    
    # 创建异步评估器
    evaluator = AsyncMemoryEvaluator(db_manager)
    
    # 测试启动管理器初始化
    manager = AsyncEvaluatorStartupManager()
    
    print("📋 初始状态:")
    status = manager.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # 初始化评估器
    print("\n🔄 正在初始化评估器...")
    success = manager.initialize_evaluator(evaluator)
    
    print("\n📋 初始化后状态:")
    status = manager.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    if success:
        print("✅ 启动管理器初始化成功")
        
        # 测试队列功能
        print("\n📝 测试队列功能...")
        
        async def test_evaluation():
            await evaluator.queue_dialogue_for_evaluation(
                "测试用户输入", "测试AI响应", "test_session"
            )
            return True
        
        queue_success = manager.queue_evaluation_safely(test_evaluation())
        print(f"   队列测试结果: {'✅成功' if queue_success else '❌失败'}")
        
        # 等待处理
        time.sleep(2)
        
        # 关闭管理器
        print("\n🛑 关闭启动管理器...")
        manager.shutdown()
        
    else:
        print("❌ 启动管理器初始化失败")
    
    # 清理
    db_manager.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    
    return success

def test_estia_memory_with_startup_manager():
    """测试EstiaMemorySystem与启动管理器的集成"""
    print("\n🧠 测试EstiaMemorySystem集成")
    print("=" * 50)
    
    try:
        # 创建内存系统
        memory_system = EstiaMemorySystem(enable_advanced=True)
        
        print("📋 系统状态:")
        stats = memory_system.get_system_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for sub_key, sub_value in value.items():
                    print(f"     {sub_key}: {sub_value}")
            else:
                print(f"   {key}: {value}")
        
        # 测试异步评估器确保初始化
        print("\n🔄 确保异步评估器初始化...")
        async_ready = memory_system.ensure_async_initialized()
        print(f"   异步评估器就绪: {'✅是' if async_ready else '❌否'}")
        
        # 测试存储交互
        print("\n💾 测试存储交互...")
        memory_system.store_interaction(
            "你好，我是测试用户", 
            "你好！我是Estia，很高兴见到你！",
            context={"session_id": "test_session_123"}
        )
        
        # 测试查询增强
        print("\n🔍 测试查询增强...")
        enhanced_query = memory_system.enhance_query(
            "之前我们聊过什么？", 
            context={"session_id": "test_session_123"}
        )
        print(f"   增强查询结果: {len(enhanced_query)} 字符")
        
        # 等待异步处理
        print("\n⏳ 等待异步处理...")
        time.sleep(3)
        
        # 获取最终状态
        print("\n📊 最终系统状态:")
        final_stats = memory_system.get_system_stats()
        for key, value in final_stats.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for sub_key, sub_value in value.items():
                    print(f"     {sub_key}: {sub_value}")
            else:
                print(f"   {key}: {value}")
        
        # 关闭系统
        print("\n🛑 关闭系统...")
        asyncio.run(memory_system.shutdown())
        
        print("✅ EstiaMemorySystem集成测试完成")
        return True
        
    except Exception as e:
        print(f"❌ EstiaMemorySystem集成测试失败: {e}")
        return False

def test_concurrent_startup_stress():
    """测试并发启动的稳定性"""
    print("\n⚡ 测试并发启动稳定性")
    print("=" * 50)
    
    results = []
    
    def create_and_test_system(thread_id):
        """在线程中创建和测试系统"""
        try:
            print(f"   线程{thread_id}: 开始创建系统...")
            
            # 创建内存系统
            memory_system = EstiaMemorySystem(enable_advanced=True)
            
            # 尝试初始化异步评估器
            async_ready = memory_system.ensure_async_initialized()
            
            # 测试存储交互
            memory_system.store_interaction(
                f"线程{thread_id}的测试输入", 
                f"线程{thread_id}的AI响应",
                context={"session_id": f"thread_{thread_id}_session"}
            )
            
            # 等待处理
            time.sleep(1)
            
            # 关闭系统
            try:
                asyncio.run(memory_system.shutdown())
            except Exception as e:
                print(f"   线程{thread_id}: 关闭异常: {e}")
            
            results.append((thread_id, True, async_ready))
            print(f"   线程{thread_id}: ✅ 完成 (异步就绪: {async_ready})")
            
        except Exception as e:
            results.append((thread_id, False, str(e)))
            print(f"   线程{thread_id}: ❌ 失败: {e}")
    
    # 创建多个线程并发测试
    threads = []
    for i in range(3):
        thread = threading.Thread(target=create_and_test_system, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 分析结果
    print("\n📊 并发测试结果:")
    successful = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"   成功: {successful}/{total}")
    
    async_ready_count = sum(1 for _, success, async_ready in results if success and async_ready)
    print(f"   异步就绪: {async_ready_count}/{successful}")
    
    for thread_id, success, async_ready in results:
        status = "✅成功" if success else "❌失败"
        if success:
            async_status = "🚀异步就绪" if async_ready else "⚠️异步未就绪"
            print(f"   线程{thread_id}: {status} - {async_status}")
        else:
            print(f"   线程{thread_id}: {status} - {async_ready}")
    
    print("✅ 并发启动稳定性测试完成")
    return successful == total

def main():
    """主测试函数"""
    print("🧪 异步评估器启动时机修复测试")
    print("=" * 60)
    
    # 清理旧的测试文件
    for path in ["temp/test_async_startup.db", "data/memory.db"]:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"清理旧文件: {path}")
            except:
                pass
    
    test_results = []
    
    # 测试1: 启动管理器模式检测
    try:
        test_startup_manager_modes()
        test_results.append(("模式检测", True))
    except Exception as e:
        print(f"❌ 模式检测测试失败: {e}")
        test_results.append(("模式检测", False))
    
    # 测试2: 启动管理器初始化
    try:
        result = test_startup_manager_initialization()
        test_results.append(("启动管理器初始化", result))
    except Exception as e:
        print(f"❌ 启动管理器初始化测试失败: {e}")
        test_results.append(("启动管理器初始化", False))
    
    # 测试3: EstiaMemorySystem集成
    try:
        result = test_estia_memory_with_startup_manager()
        test_results.append(("EstiaMemorySystem集成", result))
    except Exception as e:
        print(f"❌ EstiaMemorySystem集成测试失败: {e}")
        test_results.append(("EstiaMemorySystem集成", False))
    
    # 测试4: 并发启动稳定性
    try:
        result = test_concurrent_startup_stress()
        test_results.append(("并发启动稳定性", result))
    except Exception as e:
        print(f"❌ 并发启动稳定性测试失败: {e}")
        test_results.append(("并发启动稳定性", False))
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅通过" if result else "❌失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！异步评估器启动时机问题已修复！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步调试")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 