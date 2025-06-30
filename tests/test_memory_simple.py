# -*- coding: utf-8 -*-
"""
Estia记忆系统简化集成测试

专注测试核心功能，避免复杂的导入问题
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_basic_imports():
    """测试基本导入"""
    print("🔧 测试基本导入...")
    try:
        from core.app import EstiaApp
        print("✅ EstiaApp导入成功")
        
        from core.memory.pipeline import MemoryPipeline
        print("✅ MemoryPipeline导入成功")
        
        from core.memory.init.db_manager import DatabaseManager
        print("✅ DatabaseManager导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_app_initialization():
    """测试应用初始化"""
    print("\n🚀 测试应用初始化...")
    try:
        from core.app import EstiaApp
        
        app = EstiaApp(show_startup_progress=False)
        print("✅ 应用初始化成功")
        
        if hasattr(app, 'memory') and app.memory:
            print("✅ 记忆系统已初始化")
            return app
        else:
            print("❌ 记忆系统未初始化")
            return None
            
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return None

def test_memory_stats(app):
    """测试记忆统计"""
    print("\n📊 测试记忆统计...")
    try:
        stats = app.memory.get_memory_stats()
        print(f"✅ 记忆统计: {stats}")
        
        # 检查关键字段
        required_fields = ['initialized', 'database_connected']
        missing = [f for f in required_fields if f not in stats]
        
        if not missing:
            print("✅ 统计信息完整")
            return True
        else:
            print(f"⚠️ 缺少字段: {missing}")
            return False
            
    except Exception as e:
        print(f"❌ 统计测试失败: {e}")
        return False

def test_query_enhancement(app):
    """测试查询增强"""
    print("\n🔍 测试查询增强...")
    try:
        test_queries = [
            "你好，今天天气如何？",
            "我想学习Python编程",
            "请介绍一下人工智能"
        ]
        
        for query in test_queries:
            start_time = time.time()
            enhanced_context = app.memory.enhance_query(query)
            process_time = (time.time() - start_time) * 1000
            
            print(f"✅ 查询: {query}")
            print(f"   增强上下文长度: {len(enhanced_context)} 字符")
            print(f"   处理时间: {process_time:.2f}ms")
            
            if len(enhanced_context) < 10:
                print(f"   ⚠️ 上下文较短: {enhanced_context}")
        
        return True
        
    except Exception as e:
        print(f"❌ 查询增强失败: {e}")
        return False

def test_dialogue_processing(app):
    """测试对话处理"""
    print("\n💬 测试对话处理...")
    try:
        test_queries = [
            "你好，我是新用户",
            "请介绍一下你的功能",
            "我想了解Python编程"
        ]
        
        for query in test_queries:
            start_time = time.time()
            response = app.process_query(query)
            process_time = (time.time() - start_time) * 1000
            
            print(f"✅ 用户: {query}")
            print(f"   AI响应长度: {len(response)} 字符")
            print(f"   处理时间: {process_time:.2f}ms")
            print(f"   响应预览: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 对话处理失败: {e}")
        return False

async def test_async_processing(app):
    """测试异步处理"""
    print("\n⚡ 测试异步处理...")
    try:
        # 获取初始统计
        initial_stats = app.memory.get_memory_stats()
        print(f"   初始统计: {initial_stats}")
        
        # 模拟一些对话存储
        test_interactions = [
            ("用户: 我想学习编程", "助手: 编程是很有趣的技能..."),
            ("用户: 今天天气如何", "助手: 我无法获取实时天气..."),
            ("用户: 什么是AI", "助手: 人工智能是计算机科学...")
        ]
        
        for user_input, ai_response in test_interactions:
            app.memory.store_interaction(user_input, ai_response)
        
        print(f"✅ 已提交 {len(test_interactions)} 个对话到异步队列")
        
        # 等待异步处理
        print("   等待异步处理...")
        await asyncio.sleep(3)
        
        # 检查最终统计
        final_stats = app.memory.get_memory_stats()
        print(f"   最终统计: {final_stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 异步处理失败: {e}")
        return False

def test_performance(app):
    """测试性能"""
    print("\n⚡ 测试性能...")
    try:
        query = "性能测试查询"
        iterations = 5
        
        # 测试查询增强性能
        enhance_times = []
        for i in range(iterations):
            start_time = time.time()
            app.memory.enhance_query(query)
            enhance_times.append((time.time() - start_time) * 1000)
        
        avg_enhance_time = sum(enhance_times) / len(enhance_times)
        print(f"✅ 查询增强平均耗时: {avg_enhance_time:.2f}ms")
        
        # 测试完整对话性能
        dialogue_times = []
        for i in range(iterations):
            start_time = time.time()
            app.process_query(f"{query} {i}")
            dialogue_times.append((time.time() - start_time) * 1000)
        
        avg_dialogue_time = sum(dialogue_times) / len(dialogue_times)
        print(f"✅ 完整对话平均耗时: {avg_dialogue_time:.2f}ms")
        
        # 性能评估
        if avg_enhance_time < 100:
            print("✅ 查询增强性能优秀")
        elif avg_enhance_time < 500:
            print("⚠️ 查询增强性能一般")
        else:
            print("❌ 查询增强性能较差")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 Estia记忆系统简化集成测试")
    print("="*60)
    
    # 测试结果统计
    tests_passed = 0
    total_tests = 0
    
    # 基本导入测试
    total_tests += 1
    if test_basic_imports():
        tests_passed += 1
    
    # 应用初始化测试
    total_tests += 1
    app = test_app_initialization()
    if app:
        tests_passed += 1
        
        # 只有应用初始化成功才继续其他测试
        test_functions = [
            test_memory_stats,
            test_query_enhancement,
            test_dialogue_processing,
            test_performance
        ]
        
        for test_func in test_functions:
            total_tests += 1
            try:
                if test_func(app):
                    tests_passed += 1
            except Exception as e:
                print(f"❌ 测试 {test_func.__name__} 异常: {e}")
        
        # 异步测试
        total_tests += 1
        try:
            if await test_async_processing(app):
                tests_passed += 1
        except Exception as e:
            print(f"❌ 异步测试异常: {e}")
    
    # 打印总结
    print("\n" + "="*60)
    print("📋 测试总结")
    print("="*60)
    print(f"总测试数: {total_tests}")
    print(f"通过数: {tests_passed} ✅")
    print(f"失败数: {total_tests - tests_passed} ❌")
    print(f"通过率: {(tests_passed/total_tests*100):.1f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 所有测试通过！记忆系统集成成功！")
    else:
        print(f"\n⚠️ {total_tests - tests_passed} 个测试失败，需要进一步调试")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main()) 