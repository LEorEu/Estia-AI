#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia记忆系统问题修复测试
专门解决发现的问题：
1. 存储交互失败 - memory_id变量作用域问题
2. 记忆排序失败 - 缺少rank_memories方法
3. 组件初始化失败 - 部分组件未正确初始化
"""

import os
import sys
import time
import traceback
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_memory_store_fix():
    """测试记忆存储修复"""
    print("🔧 测试记忆存储修复")
    print("="*40)
    
    try:
        from core.memory.storage.memory_store import MemoryStore
        from core.memory.init.db_manager import DatabaseManager
        
        # 创建数据库管理器
        db_manager = DatabaseManager()
        if not db_manager.connect():
            print("❌ 数据库连接失败")
            return False
        
        # 创建记忆存储
        memory_store = MemoryStore(db_manager=db_manager)
        
        # 测试存储交互记忆
        test_content = "这是一个测试记忆"
        memory_id = memory_store.add_interaction_memory(
            content=test_content,
            memory_type="test",
            role="user",
            session_id="test_session",
            timestamp=time.time(),
            weight=5.0
        )
        
        if memory_id:
            print(f"✅ 记忆存储成功，ID: {memory_id}")
            return True
        else:
            print("❌ 记忆存储失败")
            return False
            
    except Exception as e:
        print(f"❌ 记忆存储测试失败: {e}")
        traceback.print_exc()
        return False

def test_memory_scorer_fix():
    """测试记忆评分器修复"""
    print("\n📊 测试记忆评分器修复")
    print("="*40)
    
    try:
        from core.memory.ranking.scorer import MemoryScorer
        
        scorer = MemoryScorer()
        
        # 测试数据
        test_memories = [
            {
                "content": "用户说他对人工智能很感兴趣",
                "type": "user_input",
                "weight": 8.0,
                "timestamp": time.time(),
                "similarity": 0.9
            },
            {
                "content": "今天天气不错",
                "type": "user_input", 
                "weight": 3.0,
                "timestamp": time.time(),
                "similarity": 0.2
            }
        ]
        
        # 测试score_memories方法
        scored_memories = scorer.score_memories(test_memories, max_results=5)
        print(f"✅ score_memories方法正常，返回 {len(scored_memories)} 条记忆")
        
        # 测试rank_memories方法（新增的别名）
        ranked_memories = scorer.rank_memories(test_memories, max_results=5)
        print(f"✅ rank_memories方法正常，返回 {len(ranked_memories)} 条记忆")
        
        return True
        
    except Exception as e:
        print(f"❌ 记忆评分器测试失败: {e}")
        traceback.print_exc()
        return False

def test_component_initialization():
    """测试组件初始化"""
    print("\n🔧 测试组件初始化")
    print("="*40)
    
    try:
        from core.memory import create_estia_memory
        
        # 创建记忆系统
        memory_system = create_estia_memory(enable_advanced=True)
        
        # 检查组件状态
        stats = memory_system.get_system_stats()
        components = stats.get('components', {})
        
        print("📊 组件状态检查:")
        component_names = {
            'db_manager': '数据库管理器',
            'vectorizer': '向量化器', 
            'faiss_retriever': 'FAISS检索',
            'association_network': '关联网络',
            'history_retriever': '历史检索器',
            'memory_store': '记忆存储',
            'scorer': '记忆评分器',
            'async_evaluator': '异步评估器'
        }
        
        failed_components = []
        for comp_key, comp_name in component_names.items():
            status = components.get(comp_key, False)
            if status:
                print(f"   ✅ {comp_name}")
            else:
                print(f"   ❌ {comp_name}")
                failed_components.append(comp_name)
        
        if failed_components:
            print(f"\n⚠️ 失败的组件: {', '.join(failed_components)}")
            return False
        else:
            print(f"\n✅ 所有组件初始化成功")
            return True
            
    except Exception as e:
        print(f"❌ 组件初始化测试失败: {e}")
        traceback.print_exc()
        return False

def test_enhance_query_fix():
    """测试查询增强修复"""
    print("\n🧠 测试查询增强修复")
    print("="*40)
    
    try:
        from core.memory import create_estia_memory
        
        memory_system = create_estia_memory(enable_advanced=True)
        
        # 测试查询增强
        test_queries = [
            "你好，我叫张三",
            "我是一名软件工程师",
            "我喜欢人工智能"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔄 测试查询 {i}: {query}")
            
            try:
                start_time = time.time()
                enhanced_context = memory_system.enhance_query(query)
                enhance_time = time.time() - start_time
                
                print(f"   ✅ 查询增强成功")
                print(f"   ⏱️ 耗时: {enhance_time*1000:.2f}ms")
                print(f"   📝 上下文长度: {len(enhanced_context)} 字符")
                
                # 检查是否包含错误信息
                if "记忆排序失败" in enhanced_context:
                    print(f"   ⚠️ 仍然存在记忆排序问题")
                else:
                    print(f"   ✅ 记忆排序问题已修复")
                    
            except Exception as e:
                print(f"   ❌ 查询增强失败: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 查询增强测试失败: {e}")
        traceback.print_exc()
        return False

def test_store_interaction_fix():
    """测试存储交互修复"""
    print("\n💾 测试存储交互修复")
    print("="*40)
    
    try:
        from core.memory import create_estia_memory
        
        memory_system = create_estia_memory(enable_advanced=True)
        
        # 测试存储交互
        test_dialogues = [
            ("你好，我叫李华", "你好李华！很高兴认识你。"),
            ("我是一名程序员", "程序员是个很有前途的职业！"),
            ("我喜欢学习新技术", "学习新技术是很好的习惯！")
        ]
        
        for i, (user_input, ai_response) in enumerate(test_dialogues, 1):
            print(f"\n💬 测试存储对话 {i}:")
            print(f"   用户: {user_input}")
            print(f"   AI: {ai_response}")
            
            try:
                memory_system.store_interaction(user_input, ai_response)
                print(f"   ✅ 存储成功")
            except Exception as e:
                print(f"   ❌ 存储失败: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 存储交互测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🔧 Estia记忆系统问题修复测试")
    print("="*60)
    
    # 运行所有修复测试
    tests = [
        ("记忆存储修复", test_memory_store_fix),
        ("记忆评分器修复", test_memory_scorer_fix),
        ("组件初始化", test_component_initialization),
        ("查询增强修复", test_enhance_query_fix),
        ("存储交互修复", test_store_interaction_fix)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{status} {test_name}")
        except Exception as e:
            print(f"\n❌ {test_name} 异常: {e}")
            results[test_name] = False
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 修复测试总结")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有问题已修复！Estia记忆系统运行正常")
    else:
        print("⚠️ 仍有问题需要修复")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 