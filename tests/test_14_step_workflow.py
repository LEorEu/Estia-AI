#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试14步工作流程 - 验证文档标准的完整流程
"""

import sys
import os
import time

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_14_step_workflow():
    """测试完整的14步工作流程"""
    
    print("🚀 开始测试14步工作流程...")
    
    try:
        # 导入系统
        from core.memory.estia_memory_v5 import EstiaMemorySystem
        
        # 创建系统实例
        memory_system = EstiaMemorySystem(enable_advanced=True)
        
        print(f"📊 系统初始化状态: {memory_system.initialized}")
        
        # 检查核心组件
        components_status = {
            'sync_flow_manager': memory_system.sync_flow_manager is not None,
            'async_flow_manager': memory_system.async_flow_manager is not None
        }
        
        print("🔍 核心管理器状态:")
        for component, status in components_status.items():
            status_symbol = "✅" if status else "❌"
            print(f"   - {component}: {status_symbol}")
        
        if not memory_system.sync_flow_manager:
            print("❌ 同步流程管理器未初始化，无法继续测试")
            return False
        
        # 检查同步流程管理器的组件
        sync_manager = memory_system.sync_flow_manager
        sync_components = {
            'db_manager': sync_manager.db_manager is not None,
            'vectorizer': sync_manager.vectorizer is not None,
            'memory_store': sync_manager.memory_store is not None,
            'unified_cache': sync_manager.unified_cache is not None,
            'association_network': sync_manager.association_network is not None,  # 新修复
            'history_retriever': sync_manager.history_retriever is not None,      # 新修复
            'scorer': sync_manager.scorer is not None,                            # 新修复
            'faiss_retriever': sync_manager.faiss_retriever is not None,
            'smart_retriever': sync_manager.smart_retriever is not None
        }
        
        print("\n🔍 同步流程组件状态 (文档标准14步工作流程):")
        critical_components = 0
        working_components = 0
        
        for component, status in sync_components.items():
            status_symbol = "✅" if status else "❌"
            print(f"   - {component}: {status_symbol}")
            
            # 关键组件计数
            if component in ['db_manager', 'vectorizer', 'memory_store', 'unified_cache']:
                critical_components += 1 if status else 0
            else:
                working_components += 1 if status else 0
        
        # 评估状态
        print(f"\n📊 组件评估:")
        print(f"   - 关键组件 (4/4): {critical_components}/4")
        print(f"   - 工作组件 (5/5): {working_components}/5")
        
        if critical_components < 4:
            print("❌ 关键组件不完整，系统无法正常工作")
            return False
        
        # 测试查询增强 (Step 4-9)
        print("\n🧪 测试查询增强流程 (Step 4-9)...")
        
        test_query = "今天工作压力很大，需要一些建议"
        start_time = time.time()
        
        try:
            enhanced_context = memory_system.enhance_query(test_query)
            processing_time = (time.time() - start_time) * 1000
            
            print(f"✅ 查询增强成功")
            print(f"   - 处理时间: {processing_time:.2f}ms")
            print(f"   - 输入长度: {len(test_query)} 字符")
            print(f"   - 输出长度: {len(enhanced_context)} 字符")
            print(f"   - 增强比例: {len(enhanced_context)/len(test_query):.1f}x")
            
            # 显示部分增强内容
            preview = enhanced_context[:200] + "..." if len(enhanced_context) > 200 else enhanced_context
            print(f"   - 内容预览: {preview}")
            
        except Exception as e:
            print(f"❌ 查询增强失败: {e}")
            return False
        
        # 测试交互存储 (Step 11-14)
        print("\n🧪 测试交互存储流程 (Step 11-14)...")
        
        try:
            ai_response = "我理解你的工作压力。建议你可以..."
            store_result = memory_system.store_interaction(test_query, ai_response)
            
            if store_result.get('error'):
                print(f"❌ 交互存储失败: {store_result['error']}")
                return False
            else:
                print(f"✅ 交互存储成功")
                print(f"   - 用户记忆ID: {store_result.get('user_memory_id')}")
                print(f"   - AI记忆ID: {store_result.get('ai_memory_id')}")
                print(f"   - 状态: {store_result.get('status')}")
                
        except Exception as e:
            print(f"❌ 交互存储失败: {e}")
            return False
        
        # 测试缓存性能
        print("\n🧪 测试缓存性能...")
        
        try:
            cache_stats = memory_system.get_cache_stats()
            
            if cache_stats.get('error'):
                print(f"⚠️ 缓存统计获取失败: {cache_stats['error']}")
            else:
                print(f"✅ 缓存系统正常")
                hit_ratio = cache_stats.get('cache_performance', {}).get('hit_ratio', 0)
                total_hits = cache_stats.get('cache_performance', {}).get('total_hits', 0)
                print(f"   - 缓存命中率: {hit_ratio*100:.1f}%")
                print(f"   - 总命中次数: {total_hits}")
                
        except Exception as e:
            print(f"⚠️ 缓存性能测试失败: {e}")
        
        # 最终评估
        print("\n" + "="*60)
        print("📋 14步工作流程测试结果:")
        print("="*60)
        
        step_status = {
            "Step 1-3: 系统初始化": critical_components == 4,
            "Step 4-9: 查询增强": enhanced_context and len(enhanced_context) > len(test_query),
            "Step 11-14: 交互存储": store_result and not store_result.get('error'),
            "缓存系统": not cache_stats.get('error') if cache_stats else False,
            "关键组件完整性": working_components >= 3  # 至少3个工作组件
        }
        
        passed_tests = sum(step_status.values())
        total_tests = len(step_status)
        
        for step, status in step_status.items():
            status_symbol = "✅" if status else "❌"
            print(f"{status_symbol} {step}")
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n🎯 总体成功率: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if success_rate >= 80:
            print("\n🎉 14步工作流程基本恢复成功!")
            print("   符合文档标准，可以继续使用")
        elif success_rate >= 60:
            print("\n⚠️ 14步工作流程部分恢复")
            print("   基本功能可用，但仍有改进空间")
        else:
            print("\n❌ 14步工作流程恢复失败")
            print("   需要进一步修复")
        
        return success_rate >= 60
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_14_step_workflow()
    exit_code = 0 if success else 1
    print(f"\n📤 退出代码: {exit_code}")
    sys.exit(exit_code)
