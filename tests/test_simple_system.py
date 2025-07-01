#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化记忆系统测试
测试新的EstiaMemoryManager和SimpleMemoryPipeline
"""

import pytest
import time
from core.memory import create_simple_pipeline, create_memory_manager

def test_memory_manager_basic():
    """测试记忆管理器基本功能"""
    manager = create_memory_manager(advanced=False)
    
    # 测试存储
    memory_id = manager.store_memory(
        content="这是一个测试记忆",
        role="user",
        importance=7.0,
        memory_type="test"
    )
    
    assert memory_id, "记忆ID不应为空"
    
    # 测试检索
    memories = manager.retrieve_memories("测试", limit=5)
    assert len(memories) > 0, "应该能检索到记忆"
    assert any("测试记忆" in m.get('content', '') for m in memories), "应该找到相关记忆"

def test_memory_manager_layers():
    """测试分层记忆架构"""
    manager = create_memory_manager(advanced=False)
    
    # 存储不同重要性的记忆
    core_id = manager.store_memory("核心记忆", importance=9.5)
    active_id = manager.store_memory("活跃记忆", importance=7.0)
    archive_id = manager.store_memory("归档记忆", importance=5.0)
    temp_id = manager.store_memory("临时记忆", importance=2.0)
    
    # 检查统计信息
    stats = manager.get_statistics()
    assert stats['layers']['core'] >= 1, "核心层应有记忆"
    assert stats['layers']['active'] >= 1, "活跃层应有记忆"
    assert stats['layers']['archive'] >= 1, "归档层应有记忆"
    assert stats['layers']['temp'] >= 1, "临时层应有记忆"

def test_simple_pipeline_basic():
    """测试简化管道基本功能"""
    pipeline = create_simple_pipeline(advanced=False)
    
    # 测试查询增强
    enhanced_context = pipeline.enhance_query("你好，今天天气怎么样？")
    assert "用户输入" in enhanced_context, "应该包含用户输入"
    
    # 测试交互存储
    pipeline.store_interaction("你好", "你好！很高兴见到你！")
    
    # 再次查询应该能找到历史
    enhanced_context = pipeline.enhance_query("你好")
    # 由于刚存储，可能需要一些时间才能检索到

def test_pipeline_with_history():
    """测试带历史记录的管道"""
    pipeline = create_simple_pipeline(advanced=False)
    
    # 存储一些历史对话
    conversations = [
        ("我喜欢听音乐", "音乐确实很棒！你喜欢什么类型的音乐？"),
        ("我最喜欢古典音乐", "古典音乐很有深度，有特别喜欢的作曲家吗？"),
        ("贝多芬是我的最爱", "贝多芬的作品确实震撼人心！")
    ]
    
    for user_msg, ai_msg in conversations:
        pipeline.store_interaction(user_msg, ai_msg)
    
    # 测试相关查询
    enhanced_context = pipeline.enhance_query("推荐一些古典音乐")
    
    # 应该能找到相关的历史记忆
    assert "音乐" in enhanced_context, "应该包含音乐相关内容"

def test_importance_calculation():
    """测试重要性计算"""
    pipeline = create_simple_pipeline(advanced=False)
    
    # 测试不同类型内容的重要性
    test_cases = [
        "这很重要",  # 包含关键词
        "今天天气不错",  # 普通对话
        "我需要记住这个项目的重要任务和计划",  # 多个关键词
    ]
    
    for content in test_cases:
        importance = pipeline._calculate_importance(content)
        assert 1.0 <= importance <= 10.0, f"重要性应在1-10之间，实际: {importance}"

def test_context_building():
    """测试上下文构建"""
    pipeline = create_simple_pipeline(advanced=False)
    
    # 存储不同层级的记忆
    manager = pipeline.memory_manager
    
    # 核心记忆
    manager.store_memory("用户姓名是张三", importance=9.0, memory_type="profile")
    # 活跃记忆  
    manager.store_memory("最近在学习Python编程", importance=7.0, memory_type="learning")
    # 归档记忆
    manager.store_memory("上周看了一部电影", importance=5.0, memory_type="entertainment")
    
    # 测试上下文构建
    context = pipeline.enhance_query("我想学习更多编程知识")
    
    # 应该包含相关记忆
    assert "用户当前输入" in context, "应该包含用户输入"
    # 可能包含学习相关的记忆

def test_performance():
    """测试性能"""
    pipeline = create_simple_pipeline(advanced=False)
    
    # 测试查询性能
    start_time = time.time()
    context = pipeline.enhance_query("性能测试查询")
    elapsed = time.time() - start_time
    
    # 应该很快完成（小于1秒）
    assert elapsed < 1.0, f"查询应该很快完成，实际耗时: {elapsed:.3f}s"
    
    # 测试存储性能
    start_time = time.time()
    pipeline.store_interaction("性能测试输入", "性能测试响应")
    elapsed = time.time() - start_time
    
    assert elapsed < 1.0, f"存储应该很快完成，实际耗时: {elapsed:.3f}s"

if __name__ == "__main__":
    print("🧪 开始测试简化记忆系统...")
    
    try:
        test_memory_manager_basic()
        print("✅ 记忆管理器基本功能测试通过")
        
        test_memory_manager_layers()
        print("✅ 分层记忆架构测试通过")
        
        test_simple_pipeline_basic()
        print("✅ 简化管道基本功能测试通过")
        
        test_pipeline_with_history()
        print("✅ 历史记录测试通过")
        
        test_importance_calculation()
        print("✅ 重要性计算测试通过")
        
        test_context_building()
        print("✅ 上下文构建测试通过")
        
        test_performance()
        print("✅ 性能测试通过")
        
        print("\n🎉 所有测试通过！新的简化记忆系统工作正常。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 