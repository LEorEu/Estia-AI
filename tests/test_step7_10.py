# -*- coding: utf-8 -*-
"""
测试Step 7-10的完整工作流程
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.ranking.scorer import MemoryScorer
from core.memory.context_builder.builder import ContextBuilder
from core.dialogue.engine import DialogueEngine

def test_memory_scorer():
    """测试记忆排序器"""
    print("📊 测试记忆排序器...")
    
    test_memories = [
        {
            "id": "mem_001",
            "content": "用户对AI很感兴趣",
            "type": "user_input",
            "weight": 8.0,
            "timestamp": datetime.now().isoformat(),
            "similarity": 0.9
        },
        {
            "id": "mem_002", 
            "content": "今天天气不错",
            "type": "user_input",
            "weight": 3.0,
            "timestamp": datetime.now().isoformat(),
            "similarity": 0.2
        },
        {
            "id": "mem_003",
            "content": "AI兴趣分析总结",
            "type": "summary",
            "weight": 9.0,
            "timestamp": datetime.now().isoformat(),
            "similarity": 0.85
        }
    ]
    
    try:
        scorer = MemoryScorer()
        ranked = scorer.score_and_rank_memories(test_memories, max_results=5)
        
        print(f"✅ 排序成功: {len(test_memories)} -> {len(ranked)} 条记忆")
        for i, memory in enumerate(ranked):
            score = memory.get('computed_score', 0)
            content = memory['content'][:25] + "..."
            print(f"   {i+1}. {content} (评分:{score:.1f})")
        
        return True
        
    except Exception as e:
        print(f"❌ 排序测试失败: {e}")
        return False

def test_context_builder():
    """测试上下文构建器"""
    print("\n🏗️ 测试上下文构建器...")
    
    test_memories = [
        {
            "content": "用户对AI很感兴趣",
            "type": "summary", 
            "weight": 8.0,
            "computed_score": 9.5
        },
        {
            "content": "用户问了ML问题",
            "type": "user_input",
            "weight": 6.0,
            "computed_score": 7.2,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    try:
        builder = ContextBuilder(max_context_length=600)
        context = builder.build_context(
            memories=test_memories,
            user_input="什么是深度学习？",
            personality="你是友好的AI助手"
        )
        
        print(f"✅ 上下文构建成功，长度: {len(context)} 字符")
        print(f"📝 预览: {context[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 上下文构建失败: {e}")
        return False

def test_llm_generation():
    """测试LLM生成"""
    print("\n🤖 测试LLM生成...")
    
    test_prompt = """你是友好的AI助手。

[核心记忆]
• 用户对AI很感兴趣

[用户当前输入]
什么是深度学习？
"""
    
    try:
        engine = DialogueEngine()
        
        start_time = time.time()
        response = engine._get_llm_response(test_prompt)
        gen_time = time.time() - start_time
        
        print(f"✅ LLM生成成功，耗时: {gen_time*1000:.2f}ms")
        print(f"🤖 响应预览: {response[:80]}...")
        
        return True, gen_time
        
    except Exception as e:
        print(f"❌ LLM生成失败: {e}")
        return False, 0

def main():
    """主函数"""
    print("🚀 Step 7-10模块测试")
    print("=" * 40)
    
    # 测试各个模块
    scorer_ok = test_memory_scorer()
    builder_ok = test_context_builder() 
    llm_ok, gen_time = test_llm_generation()
    
    # 总结结果
    print("\n" + "=" * 40)
    print("📊 测试结果:")
    print(f"Step 7 记忆排序: {'✅ 通过' if scorer_ok else '❌ 失败'}")
    print(f"Step 8 上下文构建: {'✅ 通过' if builder_ok else '❌ 失败'}")  
    print(f"Step 9 LLM生成: {'✅ 通过' if llm_ok else '❌ 失败'}")
    
    all_passed = scorer_ok and builder_ok and llm_ok
    
    if all_passed:
        print(f"\n🎉 所有测试通过!")
        print(f"💡 Step 7-10模块已准备就绪")
        if llm_ok:
            print(f"📈 LLM生成耗时: {gen_time*1000:.2f}ms")
    else:
        print(f"\n❌ 部分测试失败")

if __name__ == "__main__":
    main()
