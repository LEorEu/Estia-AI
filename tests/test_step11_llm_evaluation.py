#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Step 11测试：LLM评估和总结功能
测试对话的重要性评估、摘要生成、话题分组等功能
"""

import os
import sys
import time
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dialogue.engine import DialogueEngine
from config import settings

def test_step11_llm_evaluation():
    """测试Step 11：LLM评估和总结"""
    print("🧠 Step 11测试：LLM评估和总结功能")
    print("="*60)
    
    try:
        # 检查配置
        print(f"📋 当前配置:")
        print(f"   模型提供商: {settings.MODEL_PROVIDER}")
        
        if settings.MODEL_PROVIDER.lower() == "gemini":
            if not settings.GEMINI_API_KEY:
                print("❌ Gemini API密钥未配置！请在config/settings.py中设置GEMINI_API_KEY")
                return False
            print(f"   Gemini模型: {settings.GEMINI_MODEL}")
            print(f"   API基础URL: {settings.GEMINI_API_BASE}")
        
        # 初始化对话引擎
        engine = DialogueEngine()
        print("✅ 对话引擎初始化完成")
        
        # 准备测试对话数据
        test_dialogues = [
            {
                "user_input": "你怎么看待我今天没有摸鱼而是一直工作？",
                "ai_response": "很棒！专注工作是很好的习惯。不过也要注意劳逸结合，适当休息对提高效率也很重要。你今天完成了什么重要工作吗？",
                "expected_weight_range": (6.0, 8.0),  # 预期权重范围
                "expected_topics": ["工作", "效率", "习惯"]
            },
            {
                "user_input": "今天天气真好",
                "ai_response": "是的，好天气总是让人心情愉快。你有什么户外活动的计划吗？",
                "expected_weight_range": (3.0, 5.0),
                "expected_topics": ["天气", "心情"]
            },
            {
                "user_input": "请记住，我对人工智能和机器学习非常感兴趣，这是我的专业方向",
                "ai_response": "好的，我会记住你对AI和机器学习的专业兴趣。这个领域发展很快，你目前在关注哪些具体的技术方向呢？",
                "expected_weight_range": (8.0, 10.0),
                "expected_topics": ["人工智能", "机器学习", "专业", "兴趣"]
            }
        ]
        
        print(f"\n🧪 开始测试 {len(test_dialogues)} 组对话...")
        
        for i, dialogue in enumerate(test_dialogues, 1):
            print(f"\n--- 测试对话 {i} ---")
            print(f"用户输入: {dialogue['user_input']}")
            print(f"AI回复: {dialogue['ai_response']}")
            
            # 测试重要性评估
            print("\n🔍 测试重要性评估...")
            weight_result = test_importance_evaluation(
                engine, 
                dialogue['user_input'], 
                dialogue['ai_response']
            )
            
            if weight_result:
                weight = weight_result['weight']
                expected_min, expected_max = dialogue['expected_weight_range']
                
                print(f"   评估权重: {weight}")
                print(f"   预期范围: {expected_min}-{expected_max}")
                
                if expected_min <= weight <= expected_max:
                    print("   ✅ 权重评估合理")
                else:
                    print("   ⚠️ 权重评估可能需要调整")
            
            # 测试摘要生成
            print("\n📝 测试摘要生成...")
            summary_result = test_summary_generation(
                engine,
                dialogue['user_input'],
                dialogue['ai_response']
            )
            
            if summary_result:
                summary = summary_result['summary']
                print(f"   生成摘要: {summary}")
                
                # 检查摘要是否包含关键词
                contains_keywords = any(
                    keyword in summary 
                    for keyword in dialogue['expected_topics']
                )
                
                if contains_keywords:
                    print("   ✅ 摘要包含相关关键词")
                else:
                    print("   ⚠️ 摘要可能缺少关键信息")
            
            # 测试话题分组
            print("\n🏷️ 测试话题分组...")
            topic_result = test_topic_grouping(
                engine,
                dialogue['user_input'],
                dialogue['ai_response']
            )
            
            if topic_result:
                group_id = topic_result.get('group_id', '')
                super_group = topic_result.get('super_group', '')
                
                print(f"   分组ID: {group_id}")
                print(f"   超级分组: {super_group}")
                
                if group_id and super_group:
                    print("   ✅ 话题分组成功")
                else:
                    print("   ⚠️ 话题分组可能不完整")
            
            print("-" * 50)
        
        print(f"\n🎉 Step 11测试完成！")
        print("✅ LLM评估功能基本正常")
        print("💡 建议根据实际效果调整评估提示词")
        
        return True
        
    except Exception as e:
        print(f"❌ Step 11测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_importance_evaluation(engine, user_input, ai_response):
    """测试重要性评估"""
    try:
        evaluation_prompt = f"""请评估以下对话的重要性，给出1-10的分数。

对话：
用户：{user_input}
助手：{ai_response}

评估标准：
- 10分：核心个人信息、明确指令
- 8分：重要事件、专业兴趣
- 6分：有意义交流
- 4分：普通问答
- 2分：简单问候

请直接返回数字分数，比如：7"""

        start_time = time.time()
        response = engine._get_llm_response(evaluation_prompt)
        evaluation_time = time.time() - start_time
        
        print(f"   ⏱️ 评估耗时: {evaluation_time*1000:.2f}ms")
        print(f"   🔍 原始响应: {response}")
        
        # 尝试提取数字
        import re
        
        # 首先尝试直接转换为数字
        try:
            weight = float(response.strip())
            if 1 <= weight <= 10:
                return {"weight": weight, "reason": "直接解析"}
        except ValueError:
            pass
        
        # 尝试从文本中提取数字
        number_matches = re.findall(r'\b(\d+(?:\.\d+)?)\b', response)
        for match in number_matches:
            weight = float(match)
            if 1 <= weight <= 10:
                return {"weight": weight, "reason": "从文本提取"}
        
        print(f"   ⚠️ 无法从响应中提取有效分数")
        return None
                
    except Exception as e:
        print(f"   ❌ 重要性评估失败: {e}")
        return None

def test_summary_generation(engine, user_input, ai_response):
    """测试摘要生成"""
    try:
        summary_prompt = f"""请为以下对话生成简洁摘要：

用户：{user_input}
助手：{ai_response}

请用一句话总结对话要点。"""

        start_time = time.time()
        response = engine._get_llm_response(summary_prompt)
        summary_time = time.time() - start_time
        
        print(f"   ⏱️ 摘要耗时: {summary_time*1000:.2f}ms")
        print(f"   📝 原始响应: {response}")
        
        # 尝试解析JSON
        try:
            if response.strip().startswith('```json'):
                # 提取JSON部分
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    result = json.loads(json_str)
                    return result
            elif response.strip().startswith('{'):
                result = json.loads(response)
                return result
            else:
                # 直接使用响应作为摘要
                return {"summary": response.strip()}
        except json.JSONDecodeError:
            # 如果不是JSON，直接使用响应作为摘要
            return {"summary": response.strip()}
            
    except Exception as e:
        print(f"   ❌ 摘要生成失败: {e}")
        return None

def test_topic_grouping(engine, user_input, ai_response):
    """测试话题分组"""
    try:
        current_date = datetime.now().strftime("%Y_%m_%d")
        
        grouping_prompt = f"""请为以下对话确定话题分组：

用户：{user_input}
助手：{ai_response}

请分析主题，返回：
1. 具体话题（如：工作状态、天气、学习等）
2. 大分类（如：工作、生活、学习、娱乐）

格式：话题名称|大分类
例如：工作状态|工作"""

        start_time = time.time()
        response = engine._get_llm_response(grouping_prompt)
        grouping_time = time.time() - start_time
        
        print(f"   ⏱️ 分组耗时: {grouping_time*1000:.2f}ms")
        print(f"   🏷️ 原始响应: {response}")
        
        # 尝试解析JSON
        try:
            if response.strip().startswith('```json'):
                # 提取JSON部分
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    result = json.loads(json_str)
                    return result
            elif response.strip().startswith('{'):
                result = json.loads(response)
                return result
            else:
                # 尝试解析简单格式 "话题|分类"
                if '|' in response:
                    parts = response.strip().split('|')
                    if len(parts) >= 2:
                        topic = parts[0].strip()
                        category = parts[1].strip()
                        return {
                            "group_id": f"{topic}_{current_date}",
                            "super_group": category
                        }
                
                # 如果都失败，返回默认值
                return {
                    "group_id": f"未分类_{current_date}",
                    "super_group": "其他"
                }
        except json.JSONDecodeError:
            print(f"   ⚠️ JSON解析失败，尝试简单格式解析")
            return None
            
    except Exception as e:
        print(f"   ❌ 话题分组失败: {e}")
        return None

def test_complete_step11_evaluation(engine, user_input, ai_response):
    """完整的Step 11评估 - 一次性获得所有字段"""
    try:
        current_date = datetime.now().strftime("%Y_%m_%d")
        
        complete_prompt = f"""请对以下对话进行完整分析，返回JSON格式结果：

对话内容：
用户：{user_input}
助手：{ai_response}

请分析并返回：
1. summary: 对话的简洁摘要
2. weight: 重要性评分（1-10分，10分最重要）
3. group_id: 话题分组ID（格式：话题名称_{current_date}）
4. super_group: 大分类（工作/生活/学习/娱乐/健康/社交/其他）

评分标准：
- 10分：核心个人信息、重要决定
- 8分：专业兴趣、重要事件
- 6分：有意义交流
- 4分：普通问答
- 2分：简单问候

请严格按照以下JSON格式返回：
{{
  "summary": "对话摘要",
  "weight": 数字,
  "group_id": "话题名称_{current_date}",
  "super_group": "大分类"
}}"""

        start_time = time.time()
        response = engine._get_llm_response(complete_prompt)
        evaluation_time = time.time() - start_time
        
        print(f"   ⏱️ 完整评估耗时: {evaluation_time*1000:.2f}ms")
        print(f"   📋 原始响应: {response}")
        
        # 尝试解析JSON
        try:
            # 提取JSON部分
            if '```json' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    raise ValueError("无法找到JSON内容")
            elif response.strip().startswith('{'):
                result = json.loads(response.strip())
            else:
                raise ValueError("响应不是JSON格式")
            
            # 验证必需字段
            required_fields = ['summary', 'weight', 'group_id', 'super_group']
            for field in required_fields:
                if field not in result:
                    print(f"   ⚠️ 缺少字段: {field}")
                    return None
            
            # 验证权重范围
            if not (1 <= result['weight'] <= 10):
                print(f"   ⚠️ 权重超出范围: {result['weight']}")
                result['weight'] = max(1, min(10, result['weight']))
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"   ❌ JSON解析失败: {e}")
            print(f"   尝试备用解析...")
            
            # 备用解析方法
            import re
            
            # 提取各个字段
            summary_match = re.search(r'summary["\']?\s*:\s*["\']([^"\']+)["\']', response, re.IGNORECASE)
            weight_match = re.search(r'weight["\']?\s*:\s*(\d+(?:\.\d+)?)', response, re.IGNORECASE)
            group_match = re.search(r'group_id["\']?\s*:\s*["\']([^"\']+)["\']', response, re.IGNORECASE)
            super_match = re.search(r'super_group["\']?\s*:\s*["\']([^"\']+)["\']', response, re.IGNORECASE)
            
            if all([summary_match, weight_match, group_match, super_match]):
                return {
                    "summary": summary_match.group(1) if summary_match else "",
                    "weight": float(weight_match.group(1)) if weight_match else 5.0,
                    "group_id": group_match.group(1) if group_match else f"未分类_{current_date}",
                    "super_group": super_match.group(1) if super_match else "其他"
                }
            else:
                print(f"   ❌ 备用解析也失败")
                return None
                
    except Exception as e:
        print(f"   ❌ 完整评估失败: {e}")
        return None

def test_simplified_step11_evaluation(engine, user_input, ai_response):
    """简化的Step 11评估 - LLM只需提供核心字段，group_id自动生成"""
    try:
        current_date = datetime.now().strftime("%Y_%m_%d")
        
        simplified_prompt = f"""请对以下对话进行分析，返回JSON格式：

对话内容：
用户：{user_input}
助手：{ai_response}

请分析并返回：
1. summary: 对话摘要（根据内容类型灵活调整长度和详细程度）
2. weight: 重要性评分（1-10分，10分最重要）
3. super_group: 大分类（工作/生活/学习/娱乐/健康/社交/其他）

摘要生成规则：
- 工作/学习类：详细记录关键信息、进展、问题、解决方案
- 重要决定/个人信息：完整记录决策过程、背景、后续计划
- 日常闲聊/简单问答：简洁记录要点即可
- 专业讨论：记录核心观点、技术要点、启发

评分标准：
- 10分：核心个人信息、重要决定、人生转折
- 8分：专业技能进展、重要事件、深度思考
- 6分：有意义的工作学习交流、问题解决
- 4分：一般性讨论、日常分享
- 2分：简单问候、闲聊

请严格按照以下JSON格式返回：
{{
  "summary": "对话摘要（长度和详细程度根据重要性调整）",
  "weight": 数字,
  "super_group": "大分类"
}}"""

        start_time = time.time()
        response = engine._get_llm_response(simplified_prompt)
        evaluation_time = time.time() - start_time
        
        print(f"   ⏱️ 简化评估耗时: {evaluation_time*1000:.2f}ms")
        print(f"   📋 原始响应: {response}")
        
        # 解析JSON
        try:
            # 提取JSON部分
            if '```json' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    raise ValueError("无法找到JSON内容")
            elif response.strip().startswith('{'):
                result = json.loads(response.strip())
            else:
                raise ValueError("响应不是JSON格式")
            
            # 验证必需字段
            required_fields = ['summary', 'weight', 'super_group']
            for field in required_fields:
                if field not in result:
                    print(f"   ⚠️ 缺少字段: {field}")
                    return None
            
            # 验证权重范围
            if not (1 <= result['weight'] <= 10):
                print(f"   ⚠️ 权重超出范围: {result['weight']}")
                result['weight'] = max(1, min(10, result['weight']))
            
            # 自动生成group_id
            super_group = result['super_group']
            result['group_id'] = f"{super_group}_{current_date}"
            
            print(f"   🏷️ 自动生成group_id: {result['group_id']}")
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"   ❌ JSON解析失败: {e}")
            return None
                
    except Exception as e:
        print(f"   ❌ 简化评估失败: {e}")
        return None

def main():
    """主函数"""
    print("🚀 开始Step 11 LLM评估测试")
    print("=" * 50)
    
    # 初始化对话引擎
    try:
        engine = DialogueEngine()
        print("✅ 对话引擎初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 测试数据
    test_conversations = [
        {
            "name": "工作专注度",
            "user": "今天整天都在专注工作，一次都没摸鱼",
            "ai": "哇，这种专注度真的很难得！你今天的工作效率一定很高。不过也要记得适当休息，劳逸结合才能长期保持高效哦。今天完成了什么重要的工作吗？"
        },
        {
            "name": "日常闲聊",
            "user": "今天天气不错",
            "ai": "是的呢，好天气总是让人心情愉快。你今天有什么特别的安排吗？"
        },
        {
            "name": "个人信息",
            "user": "我决定换工作了，已经投了几家公司的简历",
            "ai": "这是个重要的决定！换工作确实需要勇气。你主要看重新工作的哪些方面呢？是薪资、发展空间还是工作环境？我可以帮你分析一下面试准备的要点。"
        }
    ]
    
    print("\n🧪 === 简化Step 11评估测试 ===")
    for i, conv in enumerate(test_conversations, 1):
        print(f"\n📝 测试 {i}: {conv['name']}")
        print(f"   用户: {conv['user']}")
        print(f"   助手: {conv['ai']}")
        
        result = test_simplified_step11_evaluation(engine, conv['user'], conv['ai'])
        
        if result:
            print(f"   ✅ 评估成功!")
            print(f"   📄 摘要: {result['summary']}")
            print(f"   ⚖️ 权重: {result['weight']}")
            print(f"   📂 超级分组: {result['super_group']}")
            print(f"   🏷️ 分组ID: {result['group_id']}")
            
            # 验证结果
            expected_weights = [6, 4, 8]  # 预期权重范围
            if abs(result['weight'] - expected_weights[i-1]) <= 2:
                print(f"   ✅ 权重评估合理 (预期约{expected_weights[i-1]}分)")
            else:
                print(f"   ⚠️ 权重可能偏差较大 (预期约{expected_weights[i-1]}分)")
        else:
            print(f"   ❌ 评估失败")
    
    print("\n" + "=" * 50)
    print("✅ 简化Step 11测试完成")
    print("💡 设计逻辑验证:")
    print("   • LLM只需提供: summary, weight, super_group")
    print("   • group_id自动生成: super_group + 日期")
    print("   • 减少LLM负担，提高成功率")
    print("📊 这就是我们需要保存到数据库的最终JSON格式!")

if __name__ == "__main__":
    main() 