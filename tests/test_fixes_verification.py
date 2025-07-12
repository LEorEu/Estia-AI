#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速修复验证测试
验证我们修复的问题是否已经解决
"""

import os
import sys
import time
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_fixes():
    """测试修复的问题"""
    print("🔧 修复验证测试")
    print("=" * 40)
    
    fixes_status = {}
    
    try:
        # 测试1: 统一缓存管理器作用域问题
        print("\n1. 测试统一缓存管理器作用域问题修复...")
        try:
            from core.memory.estia_memory_v5 import create_estia_memory
            memory_system_v5 = create_estia_memory(enable_advanced=True)
            
            if memory_system_v5.initialized:
                print("   ✅ v5.0 统一缓存管理器问题已修复")
                fixes_status['v5_cache_scope'] = True
            else:
                print("   ❌ v5.0 统一缓存管理器问题未修复")
                fixes_status['v5_cache_scope'] = False
                
        except Exception as e:
            print(f"   ❌ v5.0 测试失败: {e}")
            fixes_status['v5_cache_scope'] = False
        
        # 测试2: 向量化器初始化问题
        print("\n2. 测试向量化器初始化问题修复...")
        try:
            from core.memory.estia_memory_v6 import create_estia_memory
            memory_system_v6 = create_estia_memory(enable_advanced=True)
            
            if memory_system_v6.initialized and memory_system_v6.vectorizer:
                print("   ✅ v6.0 向量化器初始化问题已修复")
                print(f"   📊 向量化器类型: {type(memory_system_v6.vectorizer).__name__}")
                fixes_status['v6_vectorizer'] = True
            else:
                print("   ❌ v6.0 向量化器初始化问题未修复")
                fixes_status['v6_vectorizer'] = False
                
        except Exception as e:
            print(f"   ❌ v6.0 测试失败: {e}")
            fixes_status['v6_vectorizer'] = False
        
        # 测试3: 异步评估机制
        print("\n3. 测试异步评估机制修复...")
        try:
            if 'memory_system_v6' in locals() and memory_system_v6.async_flow_manager:
                # 检查异步评估器是否存在
                if hasattr(memory_system_v6.async_flow_manager, 'async_evaluator'):
                    async_evaluator = memory_system_v6.async_flow_manager.async_evaluator
                    if async_evaluator:
                        print("   ✅ 异步评估机制已修复")
                        fixes_status['async_evaluation'] = True
                    else:
                        print("   ❌ 异步评估器未初始化")
                        fixes_status['async_evaluation'] = False
                else:
                    print("   ❌ 异步评估器不存在")
                    fixes_status['async_evaluation'] = False
            else:
                print("   ❌ 异步流程管理器不存在")
                fixes_status['async_evaluation'] = False
                
        except Exception as e:
            print(f"   ❌ 异步评估机制测试失败: {e}")
            fixes_status['async_evaluation'] = False
        
        # 测试4: 关联网络功能
        print("\n4. 测试关联网络功能修复...")
        try:
            if 'memory_system_v6' in locals() and memory_system_v6.sync_flow_manager:
                # 检查关联网络是否存在
                if hasattr(memory_system_v6.sync_flow_manager, 'association_network'):
                    association_network = memory_system_v6.sync_flow_manager.association_network
                    if association_network:
                        print("   ✅ 关联网络功能已修复")
                        print(f"   🕸️ 关联网络类型: {type(association_network).__name__}")
                        fixes_status['association_network'] = True
                    else:
                        print("   ❌ 关联网络未初始化")
                        fixes_status['association_network'] = False
                else:
                    print("   ❌ 关联网络不存在")
                    fixes_status['association_network'] = False
            else:
                print("   ❌ 同步流程管理器不存在")
                fixes_status['association_network'] = False
                
        except Exception as e:
            print(f"   ❌ 关联网络功能测试失败: {e}")
            fixes_status['association_network'] = False
        
        # 测试5: 基础功能测试
        print("\n5. 测试基础功能...")
        try:
            if 'memory_system_v6' in locals():
                # 测试查询增强
                test_query = "这是一个测试查询"
                enhanced_context = memory_system_v6.enhance_query(test_query)
                
                if enhanced_context and len(enhanced_context) > 0:
                    print("   ✅ 查询增强功能正常")
                    fixes_status['basic_query'] = True
                else:
                    print("   ❌ 查询增强功能异常")
                    fixes_status['basic_query'] = False
                
                # 测试交互存储
                test_response = "这是一个测试回复"
                store_result = memory_system_v6.store_interaction(test_query, test_response)
                
                if store_result and not store_result.get('error'):
                    print("   ✅ 交互存储功能正常")
                    fixes_status['basic_store'] = True
                else:
                    print("   ❌ 交互存储功能异常")
                    fixes_status['basic_store'] = False
            else:
                print("   ❌ 系统未初始化")
                fixes_status['basic_query'] = False
                fixes_status['basic_store'] = False
                
        except Exception as e:
            print(f"   ❌ 基础功能测试失败: {e}")
            fixes_status['basic_query'] = False
            fixes_status['basic_store'] = False
        
        # 总结
        print("\n📊 修复验证总结")
        print("=" * 40)
        
        total_fixes = len(fixes_status)
        successful_fixes = sum(1 for status in fixes_status.values() if status)
        
        print(f"总计修复项目: {total_fixes}")
        print(f"成功修复项目: {successful_fixes}")
        print(f"修复成功率: {successful_fixes/total_fixes*100:.1f}%")
        
        print("\n详细状态:")
        for fix_name, status in fixes_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {fix_name}: {'成功' if status else '失败'}")
        
        if successful_fixes == total_fixes:
            print("\n🎉 所有修复验证通过！")
            return True
        else:
            print(f"\n⚠️ 还有 {total_fixes - successful_fixes} 个问题需要修复")
            return False
            
    except Exception as e:
        print(f"❌ 修复验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 Estia记忆系统 修复验证测试")
    print("验证我们修复的问题是否已经解决")
    print("=" * 60)
    
    success = test_fixes()
    
    if success:
        print("\n🎉 所有修复验证通过！可以进行完整测试。")
        print("💡 建议运行: python test_complete_14_step_workflow.py")
    else:
        print("\n❌ 还有问题需要修复")
        print("💡 建议检查日志并修复剩余问题")

if __name__ == "__main__":
    main()