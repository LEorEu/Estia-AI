#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的轻量级 EstiaMemorySystem v4.0
验证模块化重构的效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
logging.basicConfig(level=logging.INFO)

def test_v4_initialization():
    """测试v4版本初始化"""
    print("🔧 测试v4轻量级版本初始化...")
    
    try:
        from core.memory.estia_memory_v4 import EstiaMemorySystem
        
        # 测试基本初始化
        memory_system = EstiaMemorySystem(enable_advanced=False)
        
        # 验证协调器
        assert memory_system.initialized == True, "系统未正确初始化"
        assert memory_system.component_manager is not None, "ComponentManager未初始化"
        
        # 验证引擎组件
        assert memory_system.query_enhancer is not None, "QueryEnhancer未初始化"
        assert memory_system.interaction_manager is not None, "InteractionManager未初始化"
        assert memory_system.context_builder is not None, "ContextBuilder未初始化"
        assert memory_system.system_manager is not None, "SystemManager未初始化"
        
        print("✅ v4版本初始化测试通过")
        return True
        
    except Exception as e:
        print(f"❌ v4版本初始化测试失败: {e}")
        return False

def test_v4_api_delegation():
    """测试v4版本API委托"""
    print("🔧 测试v4版本API委托...")
    
    try:
        from core.memory.estia_memory_v4 import EstiaMemorySystem
        
        memory_system = EstiaMemorySystem(enable_advanced=False)
        
        # 测试会话管理
        session_id = memory_system.get_current_session_id()
        assert session_id is not None, "会话ID获取失败"
        assert session_id.startswith("sess_"), f"会话ID格式错误: {session_id}"
        
        # 测试查询增强（委托给QueryEnhancer）
        enhanced_context = memory_system.enhance_query("测试查询")
        assert enhanced_context is not None, "查询增强失败"
        assert "测试查询" in enhanced_context, "查询内容未包含在结果中"
        
        # 测试交互存储（委托给InteractionManager）
        result = memory_system.store_interaction("用户输入", "AI回复")
        assert result is not None, "交互存储失败"
        assert "status" in result, "存储结果格式错误"
        
        # 测试系统统计（委托给SystemManager）
        stats = memory_system.get_system_stats()
        assert stats is not None, "系统统计获取失败"
        
        print("✅ v4版本API委托测试通过")
        return True
        
    except Exception as e:
        print(f"❌ v4版本API委托测试失败: {e}")
        return False

def test_v4_component_engines():
    """测试v4版本组件引擎"""
    print("🔧 测试v4版本组件引擎...")
    
    try:
        from core.memory.engines import QueryEnhancer, InteractionManager, ContextBuilder, SystemManager
        
        # 创建模拟组件
        mock_components = {
            'db_manager': None,
            'vectorizer': None,
            'memory_store': None,
            'context_manager': None
        }
        
        # 测试引擎创建
        query_enhancer = QueryEnhancer(mock_components)
        assert query_enhancer is not None, "QueryEnhancer创建失败"
        
        interaction_manager = InteractionManager(mock_components)
        assert interaction_manager is not None, "InteractionManager创建失败"
        
        context_builder = ContextBuilder(mock_components)
        assert context_builder is not None, "ContextBuilder创建失败"
        
        system_manager = SystemManager(mock_components)
        assert system_manager is not None, "SystemManager创建失败"
        
        print("✅ v4版本组件引擎测试通过")
        return True
        
    except Exception as e:
        print(f"❌ v4版本组件引擎测试失败: {e}")
        return False

def compare_code_size():
    """比较代码大小"""
    print("📊 比较代码大小...")
    
    try:
        import subprocess
        
        # 获取原版本行数
        result_old = subprocess.run(['wc', '-l', '/home/estia/Estia-AI/core/memory/estia_memory.py'], 
                                   capture_output=True, text=True)
        old_lines = int(result_old.stdout.split()[0])
        
        # 获取新版本行数
        result_new = subprocess.run(['wc', '-l', '/home/estia/Estia-AI/core/memory/estia_memory_v4.py'], 
                                   capture_output=True, text=True)
        new_lines = int(result_new.stdout.split()[0])
        
        reduction = ((old_lines - new_lines) / old_lines) * 100
        
        print(f"原版本: {old_lines} 行")
        print(f"新版本: {new_lines} 行")
        print(f"减少: {old_lines - new_lines} 行 ({reduction:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ 代码大小比较失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试新的轻量级 EstiaMemorySystem v4.0...")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(test_v4_initialization())
    test_results.append(test_v4_api_delegation())
    test_results.append(test_v4_component_engines())
    test_results.append(compare_code_size())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！轻量级重构成功！")
        print("💡 EstiaMemorySystem 现在是一个真正的轻量级协调器")
        return 0
    else:
        print("❌ 部分测试失败，需要修复")
        return 1

if __name__ == "__main__":
    exit(main())