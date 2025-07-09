#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆评估相关提示词
包含Step 11-13的所有LLM提示词模板
"""

from typing import Dict, Any, Optional

class MemoryEvaluationPrompts:
    """记忆评估提示词管理类"""
    
    @staticmethod
    def get_dialogue_evaluation_prompt(user_input: str, ai_response: str, 
                                     context_info: Optional[Dict[str, Any]] = None) -> str:
        """
        获取对话评估提示词 (Step 11)
        
        参数:
            user_input: 用户输入
            ai_response: AI响应
            context_info: 上下文信息
            
        返回:
            完整的评估提示词
        """
        
        # 基础提示词模板
        base_prompt = f"""请对以下对话进行深度分析，像人类一样理解用户的行为模式、情感变化和成长轨迹。

对话内容：
用户：{user_input}
助手：{ai_response}

请从以下维度进行"人类化"分析：

1. **行为模式分析**：用户的行为是否与历史模式一致？有什么变化？
2. **情感状态评估**：用户当前的情感状态如何？与历史相比有什么变化？
3. **成长轨迹识别**：这次对话反映了用户的什么成长或变化？
4. **关联性分析**：与历史记忆的关联程度如何？

请分析并返回：
1. summary: 深度对话摘要（结合历史上下文，分析行为变化和情感状态）
2. weight: 重要性评分（1-10分，考虑历史关联性和行为变化程度）
3. super_group: 大分类（工作/生活/学习/娱乐/健康/社交/其他）
4. behavior_change: 行为变化描述（如果有明显变化）
5. emotional_state: 情感状态描述
6. growth_indicator: 成长指标（如果有）

{MemoryEvaluationPrompts._get_summary_rules()}

{MemoryEvaluationPrompts._get_weight_criteria()}

请严格按照以下JSON格式返回：
{{
"summary": "深度对话摘要（结合历史上下文分析）",
"weight": 数字,
"super_group": "大分类",
"behavior_change": "行为变化描述（可选）",
"emotional_state": "情感状态描述",
"growth_indicator": "成长指标（可选）"
}}"""

        # 如果有上下文信息，添加到提示词中
        if context_info:
            context_section = MemoryEvaluationPrompts._format_context_info(context_info)
            if context_section:
                base_prompt = f"{context_section}\n\n{base_prompt}"
        
        return base_prompt
    
    @staticmethod
    def _get_summary_rules() -> str:
        """获取摘要生成规则"""
        return """摘要生成规则：
- 工作/学习类：详细记录关键信息、进展、问题、解决方案
- 重要决定/个人信息：完整记录决策过程、背景、后续计划
- 日常闲聊/简单问答：简洁记录要点即可
- 专业讨论：记录核心观点、技术要点、启发
- 情感表达：记录情感状态、原因、影响
- 计划制定：记录目标、步骤、时间安排、资源需求"""
    
    @staticmethod
    def _get_weight_criteria() -> str:
        """获取权重评分标准"""
        return """评分标准：
- 10分：核心个人信息、重要决定、人生转折
- 9分：重大项目进展、重要关系变化、重要学习突破
- 8分：专业技能进展、重要事件、深度思考
- 7分：有价值的工作学习交流、问题解决过程
- 6分：一般性工作学习讨论、日常计划安排
- 5分：兴趣爱好讨论、轻松的专业交流
- 4分：一般性讨论、日常分享、简单建议
- 3分：基础信息交换、简单问答
- 2分：简单问候、闲聊、礼貌性回应
- 1分：无意义对话、测试性输入"""
    
    @staticmethod
    def _format_context_info(context_info: Dict[str, Any]) -> str:
        """格式化上下文信息"""
        if not context_info:
            return ""
        
        context_parts = []
        
        # 添加会话上下文
        if context_info.get('session_history'):
            context_parts.append("📝 当前会话历史：")
            for msg in context_info['session_history'][-3:]:  # 最近3条
                context_parts.append(f"- {msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}...")
        
        # 添加相关记忆（增强版）
        if context_info.get('context_memories'):
            context_parts.append("\n🧠 相关历史记忆：")
            for memory in context_info['context_memories'][:3]:  # 最相关的3条
                weight = memory.get('weight', 0)
                timestamp = memory.get('timestamp', 0)
                content = memory.get('content', '')[:80]
                context_parts.append(f"- [{weight}分] {content}...")
        
        # 添加行为模式分析
        if context_info.get('behavior_patterns'):
            context_parts.append("\n📊 用户行为模式：")
            for pattern in context_info['behavior_patterns']:
                context_parts.append(f"- {pattern}")
        
        # 添加情感趋势
        if context_info.get('emotional_trends'):
            context_parts.append("\n💭 情感变化趋势：")
            for trend in context_info['emotional_trends']:
                context_parts.append(f"- {trend}")
        
        if context_parts:
            return "🎯 增强上下文信息：\n" + "\n".join(context_parts)
        
        return "" 