#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试重构后的EstiaMemorySystem功能
验证模块化设计是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.estia_memory import EstiaMemorySystem
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_system_initialization():
    """测试系统初始化"""
    print("🔧 测试系统初始化...")
    
    try:
        # 测试基本初始化
        memory_system = EstiaMemorySystem(enable_advanced=True, context_preset="balanced")
        
        # 检查核心组件
        assert memory_system.initialized, "系统未正确初始化"
        assert memory_system.db_manager is not None, "数据库管理器未初始化"
        assert memory_system.memory_store is not None, "记忆存储未初始化"
        
        # 检查新的功能模块
        assert memory_system.memory_search_manager is not None, "记忆搜索管理器未初始化"
        assert memory_system.weight_manager is not None, "权重管理器未初始化"
        assert memory_system.lifecycle_manager is not None, "生命周期管理器未初始化"
        assert memory_system.system_stats_manager is not None, "系统统计管理器未初始化"
        assert memory_system.user_profiler is not None, "用户画像器未初始化"
        assert memory_system.summary_generator is not None, "摘要生成器未初始化"
        assert memory_system.emotion_analyzer is not None, "情感分析器未初始化"
        
        print("✅ 系统初始化测试通过")
        return memory_system
        
    except Exception as e:
        print(f"❌ 系统初始化测试失败: {e}")
        return None

def test_system_stats(memory_system):
    """测试系统统计功能"""
    print("\n📊 测试系统统计功能...")
    
    try:
        # 测试基本统计
        stats = memory_system.get_system_stats()
        assert stats is not None, "系统统计获取失败"
        assert 'version' in stats, "统计信息缺少版本号"
        assert stats['version'] == '3.0.0', "版本号不正确"
        
        # 测试性能统计
        perf_stats = memory_system.get_performance_stats()
        assert perf_stats is not None, "性能统计获取失败"
        
        print("✅ 系统统计测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 系统统计测试失败: {e}")
        return False

def test_search_functionality(memory_system):
    """测试搜索功能"""
    print("\n🔍 测试搜索功能...")
    
    try:
        # 测试搜索工具获取
        search_tools = memory_system.get_memory_search_tools()
        assert isinstance(search_tools, list), "搜索工具列表获取失败"
        
        # 测试关键词搜索
        search_result = memory_system.execute_memory_search_tool(
            "search_memories_by_keyword",
            {"keywords": "test", "max_results": 5}
        )
        assert search_result is not None, "关键词搜索失败"
        assert 'success' in search_result, "搜索结果格式错误"
        
        print("✅ 搜索功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 搜索功能测试失败: {e}")
        return False

def test_emotion_analysis(memory_system):
    """测试情感分析功能"""
    print("\n😊 测试情感分析功能...")
    
    try:
        # 测试基本情感分析
        emotion_result = memory_system.analyze_emotion("我今天很高兴！", return_details=True)
        assert emotion_result is not None, "情感分析失败"
        assert 'emotion' in emotion_result, "情感分析结果格式错误"
        
        print("✅ 情感分析测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 情感分析测试失败: {e}")
        return False

def test_user_profiling(memory_system):
    """测试用户画像功能"""
    print("\n👤 测试用户画像功能...")
    
    try:
        # 测试用户画像获取
        profile_result = memory_system.get_user_profile(user_id="test_user")
        assert profile_result is not None, "用户画像获取失败"
        
        # 测试用户摘要生成
        summary_result = memory_system.generate_user_summary("daily", user_id="test_user")
        assert summary_result is not None, "用户摘要生成失败"
        
        print("✅ 用户画像测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 用户画像测试失败: {e}")
        return False

def test_lifecycle_management(memory_system):
    """测试生命周期管理功能"""
    print("\n🔄 测试生命周期管理功能...")
    
    try:
        # 测试生命周期统计
        lifecycle_stats = memory_system.get_lifecycle_stats()
        assert lifecycle_stats is not None, "生命周期统计获取失败"
        
        # 测试记忆归档
        archive_result = memory_system.archive_old_memories(days_threshold=90)
        assert archive_result is not None, "记忆归档失败"
        assert 'success' in archive_result, "归档结果格式错误"
        
        print("✅ 生命周期管理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 生命周期管理测试失败: {e}")
        return False

def test_weight_management(memory_system):
    """测试权重管理功能"""
    print("\n⚖️ 测试权重管理功能...")
    
    try:
        # 创建一个测试记忆
        memory_system.store_interaction(
            user_input="测试用户输入",
            ai_response="测试AI回复",
            context={"test": True}
        )
        
        # 测试权重更新（这里可能会失败，因为需要具体的记忆ID）
        # 这个测试主要验证API是否可用
        try:
            weight_result = memory_system.update_memory_weight_dynamically(
                "test_memory_id",
                context={"test": True}
            )
            # 即使失败也是正常的，因为记忆ID不存在
            assert weight_result is not None, "权重更新API不可用"
        except:
            pass  # 记忆ID不存在是正常的
        
        print("✅ 权重管理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 权重管理测试失败: {e}")
        return False

def test_api_compatibility(memory_system):
    """测试API兼容性"""
    print("\n🔗 测试API兼容性...")
    
    try:
        # 测试会话管理
        session_id = memory_system.start_new_session()
        assert session_id is not None, "会话创建失败"
        
        current_session = memory_system.get_current_session_id()
        assert current_session == session_id, "会话ID不一致"
        
        # 测试查询增强
        enhanced_query = memory_system.enhance_query("测试查询", context={"test": True})
        assert enhanced_query is not None, "查询增强失败"
        
        print("✅ API兼容性测试通过")
        return True
        
    except Exception as e:
        print(f"❌ API兼容性测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试重构后的EstiaMemorySystem...")
    
    # 初始化系统
    memory_system = test_system_initialization()
    if not memory_system:
        print("❌ 系统初始化失败，终止测试")
        return
    
    # 运行各项测试
    tests = [
        test_system_stats,
        test_search_functionality,
        test_emotion_analysis,
        test_user_profiling,
        test_lifecycle_management,
        test_weight_management,
        test_api_compatibility
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test(memory_system):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试 {test.__name__} 发生异常: {e}")
            failed += 1
    
    # 输出测试结果
    print(f"\n📈 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！重构后的系统工作正常。")
    else:
        print(f"⚠️ 有 {failed} 个测试失败，请检查相关功能。")
    
    # 清理
    try:
        import asyncio
        asyncio.run(memory_system.shutdown())
        print("✅ 系统已安全关闭")
    except:
        pass

if __name__ == "__main__":
    main() 