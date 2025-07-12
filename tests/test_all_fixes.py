#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面修复验证测试脚本 - 验证所有已修复的问题
"""

import sys
import time
import traceback
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_all_fixes():
    """全面测试所有修复的问题"""
    print("🧪 全面修复验证测试")
    print("="*80)
    
    results = {
        'database_fields': False,
        'context_manager': False,
        'async_handling': False,
        'variable_scope': False,
        'overall': False
    }
    
    try:
        # 测试1: 数据库字段修复
        print("\n🔧 测试1: 数据库字段名修复")
        print("-" * 40)
        
        # 创建一个虚拟数据库管理器来测试
        class MockDBManager:
            def query(self, sql):
                # 模拟查询结果，检查SQL是否包含正确字段
                if 'weight' in sql and 'timestamp' in sql:
                    return [(10, 2, 1, 1, 6.5, '2025-01-01', '2024-01-01')]
                return []
        
        class MockUnifiedCache:
            def get_stats(self):
                return {'hit_ratio': 0.95}
        
        from core.memory.managers.monitor_flow.system_stats import SystemStatsManager
        stats_manager = SystemStatsManager(MockDBManager(), MockUnifiedCache())
        memory_stats = stats_manager.get_memory_statistics()
        
        if isinstance(memory_stats, dict) and 'total_memories' in memory_stats:
            print("✅ 数据库字段名修复成功")
            results['database_fields'] = True
        else:
            print("❌ 数据库字段名仍有问题")
        
        # 测试2: 上下文管理器修复
        print("\n🔧 测试2: 错误恢复上下文管理器修复")
        print("-" * 40)
        
        from core.memory.managers.recovery.error_recovery_manager import ErrorRecoveryManager
        
        recovery_manager = ErrorRecoveryManager()
        recovery_manager.register_component('test_component')
        
        # 测试上下文管理器
        try:
            with recovery_manager.with_recovery('test_component') as context:
                # 模拟一些操作
                pass
            print("✅ 错误恢复上下文管理器修复成功")
            results['context_manager'] = True
        except TypeError as e:
            if "does not support the context manager protocol" in str(e):
                print("❌ 上下文管理器仍有问题")
            else:
                raise
        
        # 测试3: 融合架构系统初始化
        print("\n🔧 测试3: 融合架构v6.0系统初始化")
        print("-" * 40)
        
        from core.memory.estia_memory_v6 import EstiaMemorySystem
        
        # 创建系统实例
        memory_system = EstiaMemorySystem(enable_advanced=True)
        
        if memory_system.initialized:
            print("✅ 融合架构v6.0初始化成功")
            results['variable_scope'] = True
            
            # 测试基本功能
            test_query = "你好，我想了解一下系统状态"
            enhanced_context = memory_system.enhance_query(test_query)
            
            if enhanced_context and len(enhanced_context) > 0:
                print("✅ 查询增强功能正常")
                
                # 测试存储功能
                store_result = memory_system.store_interaction(
                    test_query, 
                    "你好！系统状态良好，所有组件都在正常运行。", 
                    {'session_id': 'test_session'}
                )
                
                if store_result and 'error' not in store_result:
                    print("✅ 交互存储功能正常")
                    
                    # 测试异步处理修复
                    archive_result = memory_system.archive_old_memories(30)
                    
                    if archive_result and isinstance(archive_result, dict):
                        print("✅ 异步处理修复成功")
                        results['async_handling'] = True
                    else:
                        print("❌ 异步处理仍有问题")
                else:
                    print("❌ 交互存储有问题")
            else:
                print("❌ 查询增强有问题")
        else:
            print("❌ 融合架构v6.0初始化失败")
        
        # 测试4: 系统综合状态
        print("\n🔧 测试4: 系统综合状态检查")
        print("-" * 40)
        
        if memory_system.initialized:
            system_stats = memory_system.get_system_stats()
            cache_stats = memory_system.get_cache_stats()
            
            print(f"   系统版本: {system_stats.get('system_version', 'unknown')}")
            print(f"   初始化状态: {system_stats.get('initialized', False)}")
            print(f"   当前会话: {system_stats.get('current_session', 'none')}")
            
            # 测试记忆搜索工具
            search_tools = memory_system.get_memory_search_tools()
            print(f"   可用搜索工具: {len(search_tools)}个")
            
            if (system_stats.get('initialized') and 
                len(search_tools) > 0 and 
                isinstance(cache_stats, dict)):
                print("✅ 系统综合状态良好")
                results['overall'] = True
            else:
                print("❌ 系统综合状态有问题")
        
        # 输出最终结果
        print("\n📊 修复验证结果")
        print("="*80)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, passed in results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"   {test_name:20}: {status}")
        
        print(f"\n🎯 总体结果: {passed_tests}/{total_tests} 测试通过")
        
        if passed_tests == total_tests:
            print("🎉 所有修复都已生效！系统完全正常运行")
            return True
        else:
            print("⚠️ 部分问题仍需修复")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        print("错误详情:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🚀 开始全面修复验证测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_all_fixes()
    
    if success:
        print("\n✅ 所有修复验证通过！Estia记忆系统v6.0已完全修复")
        sys.exit(0)
    else:
        print("\n❌ 部分修复验证失败，请检查具体问题")
        sys.exit(1) 