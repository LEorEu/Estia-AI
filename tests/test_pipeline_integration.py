#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试记忆管道集成
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append('.')

def test_memory_pipeline():
    """测试记忆管道基本功能"""
    print("=== 测试记忆管道集成 ===")
    
    try:
        # 导入记忆管道
        from core.memory.pipeline import MemoryPipeline
        print("✅ MemoryPipeline导入成功")
        
        # 初始化管道
        pipeline = MemoryPipeline()
        print("✅ MemoryPipeline初始化成功")
        print(f"使用真实存储: {pipeline.use_real_store}")
        
        # 测试存储交互
        print("\n--- 测试存储交互 ---")
        pipeline.store_interaction("你好，我是用户", "你好！我是Estia，很高兴认识你！")
        pipeline.store_interaction("今天天气怎么样？", "今天天气很好，阳光明媚。")
        pipeline.store_interaction("你能帮我做什么？", "我可以帮你回答问题、聊天、记住我们的对话等等。")
        print("✅ 交互存储测试完成")
        
        # 测试查询增强
        print("\n--- 测试查询增强 ---")
        queries = ["天气", "你好", "帮助"]
        
        for query in queries:
            context = pipeline.enhance_query(query)
            print(f"查询: {query}")
            print(f"增强上下文: {context[:100]}...")
            print()
        
        print("✅ 查询增强测试完成")
        
        print("\n🎉 记忆管道集成测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_integration():
    """测试应用集成"""
    print("\n=== 测试应用集成 ===")
    
    try:
        # 导入应用
        from core.app import EstiaApp
        print("✅ EstiaApp导入成功")
        
        # 初始化应用
        app = EstiaApp()
        print("✅ EstiaApp初始化成功")
        
        # 测试查询处理
        print("\n--- 测试查询处理 ---")
        response = app.process_query("你好，测试一下记忆功能")
        print(f"用户: 你好，测试一下记忆功能")
        print(f"AI: {response}")
        
        response = app.process_query("你还记得我刚才说了什么吗？")
        print(f"用户: 你还记得我刚才说了什么吗？")
        print(f"AI: {response}")
        
        print("✅ 应用集成测试完成")
        
        print("\n🎉 应用集成测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 应用集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始集成测试...")
    
    # 测试记忆管道
    pipeline_success = test_memory_pipeline()
    
    # 测试应用集成
    if pipeline_success:
        app_success = test_app_integration()
    else:
        print("跳过应用集成测试")
        app_success = False
    
    print(f"\n=== 测试结果 ===")
    print(f"记忆管道: {'✅ 成功' if pipeline_success else '❌ 失败'}")
    print(f"应用集成: {'✅ 成功' if app_success else '❌ 失败'}") 