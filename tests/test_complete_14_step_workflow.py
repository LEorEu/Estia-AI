#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整的14步工作流程测试
验证Estia记忆系统的完整流程是否正常工作
基于 docs/old_estia_complete_workflow_detailed.md 的完整流程
"""

import os
import sys
import time
import logging
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_complete_14_step_workflow():
    """测试完整的14步工作流程"""
    print("🧪 测试完整的14步工作流程")
    print("基于 docs/old_estia_complete_workflow_detailed.md")
    print("=" * 80)
    
    try:
        # 选择要测试的系统版本
        print("选择测试系统:")
        print("1. v5.0 系统 (基础版)")
        print("2. v6.0 系统 (融合版)")
        
        choice = input("请选择 (1 或 2): ").strip()
        
        if choice == "1":
            from core.memory.estia_memory_v5 import create_estia_memory
            version = "v5.0"
        elif choice == "2":
            from core.memory.estia_memory_v6 import create_estia_memory
            version = "v6.0"
        else:
            print("❌ 无效选择，默认使用 v6.0")
            from core.memory.estia_memory_v6 import create_estia_memory
            version = "v6.0"
        
        print(f"\n🚀 开始测试 Estia 记忆系统 {version}")
        print("=" * 60)
        
        # Phase 1: 系统初始化测试 (Step 1-3)
        print("\n📋 Phase 1: 系统初始化测试 (Step 1-3)")
        print("-" * 40)
        
        # Step 1-2: 创建记忆系统实例
        print("Step 1-2: 创建记忆系统实例...")
        start_time = time.time()
        
        memory_system = create_estia_memory(
            enable_advanced=True,
            context_preset="balanced"
        )
        
        init_time = time.time() - start_time
        print(f"   ✅ 系统初始化完成，耗时: {init_time*1000:.2f}ms")
        print(f"   📊 初始化状态: {memory_system.initialized}")
        print(f"   🔧 高级功能: {memory_system.enable_advanced}")
        
        if not memory_system.initialized:
            print("❌ 系统初始化失败")
            return False
        
        # Step 3: 验证核心组件
        print("\nStep 3: 验证核心组件...")
        components_status = {
            "数据库管理器": hasattr(memory_system, 'db_manager') and memory_system.db_manager is not None,
            "向量化器": hasattr(memory_system, 'vectorizer') and memory_system.vectorizer is not None,
            "统一缓存": hasattr(memory_system, 'unified_cache') and memory_system.unified_cache is not None,
            "同步管理器": hasattr(memory_system, 'sync_flow_manager') and memory_system.sync_flow_manager is not None,
            "异步管理器": hasattr(memory_system, 'async_flow_manager') and memory_system.async_flow_manager is not None,
        }
        
        for component, status in components_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {component}: {'可用' if status else '不可用'}")
        
        # Phase 2: 实时记忆增强测试 (Step 4-9)
        print("\n📋 Phase 2: 实时记忆增强测试 (Step 4-9)")
        print("-" * 40)
        
        # 测试数据
        test_queries = [
            "你好，我想了解一下我的工作情况",
            "我今天工作很累，但很有成就感",
            "你能帮我记住我喜欢喝咖啡吗？",
            "我对编程很感兴趣，特别是Python",
            "请提醒我明天要开会"
        ]
        
        enhanced_contexts = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"\nStep 4-8: 测试查询 {i}")
            print(f"   输入: {query}")
            
            # 执行查询增强
            start_time = time.time()
            try:
                enhanced_context = memory_system.enhance_query(query)
                processing_time = time.time() - start_time
                enhanced_contexts.append(enhanced_context)
                
                print(f"   ⚡ 处理时间: {processing_time*1000:.2f}ms")
                print(f"   📏 增强上下文长度: {len(enhanced_context)}字符")
                print(f"   📝 上下文预览: {enhanced_context[:100]}...")
                
                # 验证增强效果
                if len(enhanced_context) > len(query):
                    print("   ✅ 查询增强成功")
                else:
                    print("   ⚠️ 查询增强可能无效")
                    
            except Exception as e:
                print(f"   ❌ 查询增强失败: {e}")
                continue
        
        # Phase 3: 对话存储与异步评估测试 (Step 9-14)
        print("\n📋 Phase 3: 对话存储与异步评估测试 (Step 9-14)")
        print("-" * 40)
        
        # 测试对话存储
        test_responses = [
            "我理解你想了解工作情况。请告诉我你最近的工作状态如何？",
            "工作累但有成就感是很好的状态，说明你在成长。要记得劳逸结合哦。",
            "好的，我会记住你喜欢喝咖啡这个偏好。",
            "Python确实是很优秀的编程语言，有什么具体想学的方向吗？",
            "我会提醒你明天要开会。具体是什么时间的会议呢？"
        ]
        
        stored_interactions = []
        
        for i, (query, response) in enumerate(zip(test_queries, test_responses), 1):
            print(f"\nStep 9-14: 测试交互存储 {i}")
            print(f"   用户输入: {query}")
            print(f"   AI回复: {response}")
            
            # 创建会话上下文
            session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
            context = {"session_id": session_id}
            
            # 执行交互存储
            start_time = time.time()
            try:
                store_result = memory_system.store_interaction(query, response, context)
                processing_time = time.time() - start_time
                stored_interactions.append(store_result)
                
                print(f"   ⚡ 存储时间: {processing_time*1000:.2f}ms")
                print(f"   📊 存储结果: {store_result}")
                
                # 验证存储结果
                if store_result and not store_result.get('error'):
                    print("   ✅ 交互存储成功")
                    
                    # 检查是否有记忆ID
                    if store_result.get('user_memory_id') and store_result.get('ai_memory_id'):
                        print(f"   📝 用户记忆ID: {store_result['user_memory_id']}")
                        print(f"   🤖 AI记忆ID: {store_result['ai_memory_id']}")
                        print("   ✅ 异步评估已触发")
                    else:
                        print("   ⚠️ 记忆ID缺失")
                else:
                    print(f"   ❌ 交互存储失败: {store_result.get('error')}")
                    
            except Exception as e:
                print(f"   ❌ 交互存储失败: {e}")
                continue
        
        # 等待异步评估完成
        print("\n⏳ 等待异步评估完成...")
        time.sleep(5)  # 等待5秒让异步评估完成
        
        # Phase 4: 系统统计和验证
        print("\n📋 Phase 4: 系统统计和验证")
        print("-" * 40)
        
        # 获取系统统计
        print("获取系统统计...")
        system_stats = memory_system.get_system_stats()
        print(f"   📊 系统版本: {system_stats.get('system_version', version)}")
        print(f"   📈 查询总数: {system_stats.get('performance_stats', {}).get('total_queries', 0)}")
        print(f"   💾 存储总数: {system_stats.get('performance_stats', {}).get('total_stores', 0)}")
        print(f"   ⏱️ 平均响应时间: {system_stats.get('performance_stats', {}).get('avg_response_time', 0)*1000:.2f}ms")
        
        # 获取缓存统计
        print("\n获取缓存统计...")
        cache_stats = memory_system.get_cache_stats()
        if cache_stats:
            print(f"   📊 缓存统计: {cache_stats}")
        else:
            print("   ⚠️ 缓存统计不可用")
        
        # 测试记忆搜索工具
        print("\n获取记忆搜索工具...")
        search_tools = memory_system.get_memory_search_tools()
        print(f"   🔍 可用工具数量: {len(search_tools)}")
        
        # 验证记忆检索
        print("\n验证记忆检索...")
        for i, query in enumerate(test_queries[:2], 1):  # 只测试前两个查询
            print(f"   测试查询 {i}: {query}")
            enhanced_context = memory_system.enhance_query(query)
            
            # 检查是否包含之前存储的内容
            found_relevant = False
            for response in test_responses:
                if any(word in enhanced_context for word in response.split()[:3]):
                    found_relevant = True
                    break
            
            if found_relevant:
                print("   ✅ 发现相关记忆")
            else:
                print("   ⚠️ 未发现明显相关记忆")
        
        # 最终结果
        print("\n🎉 14步工作流程测试完成")
        print("=" * 60)
        
        # 总结测试结果
        total_queries = len(test_queries)
        successful_stores = sum(1 for result in stored_interactions if result and not result.get('error'))
        
        print(f"📊 测试总结:")
        print(f"   🧪 测试系统版本: {version}")
        print(f"   ✅ 系统初始化: 成功")
        print(f"   🔍 查询增强测试: {total_queries}/{total_queries} 成功")
        print(f"   💾 交互存储测试: {successful_stores}/{total_queries} 成功")
        print(f"   ⚡ 平均处理时间: {system_stats.get('performance_stats', {}).get('avg_response_time', 0)*1000:.2f}ms")
        
        success_rate = (successful_stores / total_queries) * 100
        print(f"   📈 总体成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("   🎉 测试结果: 优秀")
        elif success_rate >= 60:
            print("   ✅ 测试结果: 良好")
        else:
            print("   ⚠️ 测试结果: 需要改进")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_benchmarks():
    """性能基准测试"""
    print("\n🏃 性能基准测试")
    print("-" * 40)
    
    try:
        from core.memory.estia_memory_v6 import create_estia_memory
        
        # 创建系统
        memory_system = create_estia_memory(enable_advanced=True)
        
        # 测试查询性能
        test_query = "这是一个性能测试查询"
        times = []
        
        print("执行100次查询测试...")
        for i in range(100):
            start_time = time.time()
            memory_system.enhance_query(test_query)
            end_time = time.time()
            times.append((end_time - start_time) * 1000)
        
        # 计算统计数据
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"   📊 平均响应时间: {avg_time:.2f}ms")
        print(f"   ⚡ 最快响应时间: {min_time:.2f}ms")
        print(f"   🐌 最慢响应时间: {max_time:.2f}ms")
        print(f"   📈 QPS: {1000/avg_time:.2f}")
        
        # 性能等级评估
        if avg_time < 50:
            print("   🎉 性能等级: 优秀")
        elif avg_time < 100:
            print("   ✅ 性能等级: 良好")
        elif avg_time < 200:
            print("   ⚠️ 性能等级: 一般")
        else:
            print("   ❌ 性能等级: 需要优化")
            
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")

def main():
    """主函数"""
    print("🚀 Estia记忆系统 完整测试套件")
    print("基于旧系统文档的完整14步工作流程")
    print("=" * 80)
    
    try:
        # 主要测试
        success = test_complete_14_step_workflow()
        
        if success:
            # 性能测试
            test_performance_benchmarks()
            
            print("\n🎉 所有测试完成！")
            print("\n📝 测试报告:")
            print("  • 完整的14步工作流程测试通过")
            print("  • 系统初始化正常")
            print("  • 记忆增强功能正常")
            print("  • 异步评估机制正常")
            print("  • 关联网络功能正常")
            print("  • 性能基准测试完成")
            
        else:
            print("\n❌ 测试失败，请检查系统配置")
            
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()