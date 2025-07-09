#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试重构后的Estia记忆系统
验证ComponentManager重构的功能完整性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
logging.basicConfig(level=logging.INFO)

def test_basic_initialization():
    """测试基本初始化"""
    print("🔧 测试基本初始化...")
    
    try:
        from core.memory.estia_memory import EstiaMemorySystem
        
        # 测试基本初始化
        memory_system = EstiaMemorySystem(enable_advanced=False)
        
        # 验证核心组件
        assert memory_system.db_manager is not None, "数据库管理器未初始化"
        assert memory_system.memory_store is not None, "记忆存储未初始化"
        assert memory_system.component_manager is not None, "ComponentManager未初始化"
        
        # 验证功能模块
        assert memory_system.memory_search_manager is not None, "记忆搜索管理器未初始化"
        assert memory_system.weight_manager is not None, "权重管理器未初始化"
        assert memory_system.lifecycle_manager is not None, "生命周期管理器未初始化"
        assert memory_system.system_stats_manager is not None, "系统统计管理器未初始化"
        
        print("✅ 基本初始化测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 基本初始化测试失败: {e}")
        return False

def test_advanced_initialization():
    """测试高级功能初始化"""
    print("🔧 测试高级功能初始化...")
    
    try:
        from core.memory.estia_memory import EstiaMemorySystem
        
        # 测试高级功能初始化
        memory_system = EstiaMemorySystem(enable_advanced=True)
        
        # 验证高级组件
        if memory_system.enable_advanced:
            assert memory_system.vectorizer is not None, "向量化器未初始化"
            assert memory_system.faiss_retriever is not None, "FAISS检索器未初始化"
            assert memory_system.association_network is not None, "关联网络未初始化"
            assert memory_system.history_retriever is not None, "历史检索器未初始化"
            assert memory_system.smart_retriever is not None, "智能检索器未初始化"
            assert memory_system.scorer is not None, "评分器未初始化"
            print("✅ 高级组件初始化成功")
        else:
            print("⚠️ 高级功能被禁用")
        
        print("✅ 高级功能初始化测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 高级功能初始化测试失败: {e}")
        return False

def test_component_manager():
    """测试ComponentManager功能"""
    print("🔧 测试ComponentManager功能...")
    
    try:
        from core.memory.estia_memory import EstiaMemorySystem
        
        memory_system = EstiaMemorySystem(enable_advanced=False)
        
        # 验证ComponentManager
        cm = memory_system.component_manager
        assert cm is not None, "ComponentManager未初始化"
        
        # 验证组件注册
        assert 'db_manager' in cm.components, "db_manager未注册"
        assert 'memory_store' in cm.components, "memory_store未注册"
        assert 'memory_search_manager' in cm.components, "memory_search_manager未注册"
        
        # 验证组件获取
        db_manager = cm.get_component('db_manager')
        assert db_manager is not None, "无法获取db_manager"
        
        memory_store = cm.get_component('memory_store')
        assert memory_store is not None, "无法获取memory_store"
        
        print("✅ ComponentManager功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ ComponentManager功能测试失败: {e}")
        return False

def test_api_compatibility():
    """测试API兼容性"""
    print("🔧 测试API兼容性...")
    
    try:
        from core.memory.estia_memory import EstiaMemorySystem
        
        memory_system = EstiaMemorySystem(enable_advanced=False)
        
        # 测试核心API方法
        session_id = memory_system.get_current_session_id()
        assert session_id is not None, "获取会话ID失败"
        
        # 测试enhance_query方法
        enhanced_context = memory_system.enhance_query("测试查询")
        assert enhanced_context is not None, "enhance_query方法失败"
        
        # 测试store_interaction方法
        result = memory_system.store_interaction("用户输入", "AI回复")
        assert result is not None, "store_interaction方法失败"
        
        # 测试get_system_stats方法
        stats = memory_system.get_system_stats()
        assert stats is not None, "get_system_stats方法失败"
        assert 'system_status' in stats, "系统统计信息不完整"
        
        print("✅ API兼容性测试通过")
        return True
        
    except Exception as e:
        print(f"❌ API兼容性测试失败: {e}")
        return False

def test_internal_tools():
    """测试内部工具模块"""
    print("🔧 测试内部工具模块...")
    
    try:
        from core.memory.internal import MemoryLayer, ErrorHandlerMixin, ComponentManager, QueryBuilder
        
        # 测试MemoryLayer
        layer_name = MemoryLayer.get_layer_name(8.5)
        assert layer_name == "归档记忆", f"权重分层错误: {layer_name}"
        
        # 测试QueryBuilder
        query_builder = QueryBuilder()
        query, params = query_builder.build_select_query(limit=10)
        assert "SELECT" in query, "查询构建失败"
        assert "LIMIT 10" in query, "查询限制失败"
        
        # 测试ErrorHandlerMixin
        class TestClass(ErrorHandlerMixin):
            def __init__(self):
                super().__init__()
                
        test_instance = TestClass()
        assert hasattr(test_instance, 'logger'), "ErrorHandlerMixin初始化失败"
        
        print("✅ 内部工具模块测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 内部工具模块测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试重构后的Estia记忆系统...")
    print("=" * 50)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(test_basic_initialization())
    test_results.append(test_advanced_initialization())
    test_results.append(test_component_manager())
    test_results.append(test_api_compatibility())
    test_results.append(test_internal_tools())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！重构成功！")
        return 0
    else:
        print("❌ 部分测试失败，需要修复")
        return 1

if __name__ == "__main__":
    exit(main())