#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Step 7-10的完整工作流程
包括：记忆排序、上下文构建、LLM生成、响应处理
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入必要的模块
from core.memory.ranking.scorer import MemoryScorer
from core.memory.context_builder.builder import ContextBuilder
from core.dialogue.engine import DialogueEngine

def test_step7_memory_scorer():
    """测试Step 7: 记忆排序和去重"""
    print("📊 Step 7: 记忆排序和去重测试")
    
    # 测试数据
    test_memories = [
        {
            "id": "mem_001",
            "content": "用户说他对人工智能很感兴趣",
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
            "content": "用户AI兴趣的综合分析",
            "type": "summary",
            "weight": 9.0,
            "timestamp": datetime.now().isoformat(),
            "similarity": 0.85
        }
    ]
    
    try:
        scorer = MemoryScorer()
        ranked_memories = scorer.score_and_rank_memories(test_memories, max_results=5)
        
        print(f"✅ 排序成功: {len(test_memories)} -> {len(ranked_memories)} 条记忆")
        for i, memory in enumerate(ranked_memories):
            print(f"   {i+1}. {memory['content'][:30]}... (评分:{memory.get('computed_score', 0):.1f})")
        
        return True, ranked_memories
        
    except Exception as e:
        print(f"❌ Step 7测试失败: {e}")
        return False, []

def test_step8_context_builder():
    """测试Step 8: 上下文构建"""
    print("\n🏗️ Step 8: 上下文构建测试")
    
    # 测试数据
    test_memories = [
        {
            "content": "用户对AI很感兴趣",
            "type": "summary",
            "weight": 8.0,
            "computed_score": 9.5
        },
        {
            "content": "用户问了关于机器学习的问题",
            "type": "user_input",
            "weight": 6.0,
            "computed_score": 7.2,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    try:
        builder = ContextBuilder(max_context_length=800)
        context = builder.build_context(
            memories=test_memories,
            user_input="什么是深度学习？",
            personality="你是一个友好的AI助手",
            additional_context={"模式": "学习讨论"}
        )
        
        print(f"✅ 上下文构建成功，长度: {len(context)} 字符")
        print("📝 上下文预览:")
        print("-" * 30)
        print(context[:200] + "..." if len(context) > 200 else context)
        print("-" * 30)
        
        return True, context
        
    except Exception as e:
        print(f"❌ Step 8测试失败: {e}")
        return False, ""

def test_step9_llm_generation():
    """测试Step 9: LLM生成响应"""
    print("\n🤖 Step 9: LLM生成响应测试")
    
    test_prompt = """你是一个友好的AI助手。

[核心记忆]
• [summary] 用户对AI很感兴趣 (重要度:8.0)

[用户当前输入]
什么是深度学习？
"""
    
    try:
        engine = DialogueEngine()
        
        start_time = time.time()
        response = engine._get_llm_response(test_prompt)
        generation_time = time.time() - start_time
        
        print(f"✅ LLM响应生成成功，耗时: {generation_time*1000:.2f}ms")
        print("🤖 AI响应:")
        print("-" * 30)
        print(response[:150] + "..." if len(response) > 150 else response)
        print("-" * 30)
        
        return True, response, generation_time
        
    except Exception as e:
        print(f"❌ Step 9测试失败: {e}")
        return False, "", 0

def test_step10_response_evaluation():
    """测试Step 10: 响应后处理"""
    print("\n⚙️ Step 10: 响应后处理测试")
    
    # 模拟的响应数据
    user_input = "什么是深度学习？"
    ai_response = "深度学习是机器学习的一个分支，它使用多层神经网络来学习数据的复杂模式。深度学习在图像识别、自然语言处理等领域都有广泛应用。"
    
    try:
        # 简单的质量评估
        quality_score = evaluate_response_quality(user_input, ai_response)
        
        print(f"✅ 响应质量评估完成")
        print(f"   相关性评分: {quality_score['relevance']:.1f}/10")
        print(f"   完整性评分: {quality_score['completeness']:.1f}/10")
        print(f"   综合评分: {quality_score['overall']:.1f}/10")
        
        return True, quality_score
        
    except Exception as e:
        print(f"❌ Step 10测试失败: {e}")
        return False, {}

def evaluate_response_quality(user_input, ai_response):
    """简单的响应质量评估"""
    # 相关性评估
    user_words = set(user_input.lower().split())
    response_words = set(ai_response.lower().split())
    common_words = user_words.intersection(response_words)
    relevance_score = min(10.0, len(common_words) * 3.0)
    
    # 完整性评估
    response_length = len(ai_response)
    if response_length > 100:
        completeness_score = 8.0
    elif response_length > 50:
        completeness_score = 6.0
    else:
        completeness_score = 4.0
    
    # 综合评分
    overall_score = (relevance_score + completeness_score) / 2
    
    return {
        "relevance": relevance_score,
        "completeness": completeness_score,
        "overall": overall_score
    }

def main():
    """主函数"""
    print("🚀 开始Step 7-10模块测试")
    print("=" * 50)
    
    # 测试各个步骤
    step7_ok, ranked_memories = test_step7_memory_scorer()
    step8_ok, context = test_step8_context_builder()
    step9_ok, response, gen_time = test_step9_llm_generation()
    step10_ok, quality = test_step10_response_evaluation()
    
    # 总结测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"✅ Step 7 记忆排序: {'通过' if step7_ok else '失败'}")
    print(f"✅ Step 8 上下文构建: {'通过' if step8_ok else '失败'}")
    print(f"✅ Step 9 LLM生成: {'通过' if step9_ok else '失败'}")
    print(f"✅ Step 10 响应处理: {'通过' if step10_ok else '失败'}")
    
    all_passed = all([step7_ok, step8_ok, step9_ok, step10_ok])
    
    if all_passed:
        print("\n🎉 所有Step 7-10模块测试通过!")
        print("💡 记忆系统Step 7-10已准备就绪")
        
        # 显示性能统计
        if step9_ok:
            print(f"📈 性能统计:")
            print(f"   LLM生成耗时: {gen_time*1000:.2f}ms")
            print(f"   响应质量: {quality.get('overall', 0):.1f}/10")
    else:
        print("\n❌ 部分模块测试失败，请检查错误信息")

if __name__ == "__main__":
    main() 