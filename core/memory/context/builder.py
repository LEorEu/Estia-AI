#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
上下文构建器 (Step 8)
将检索到的记忆组织成结构化的上下文
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ContextBuilder:
    """上下文构建器类"""
    
    def __init__(self, max_context_length: int = 2000, max_memories: int = 15):
        """
        初始化上下文构建器
        
        参数:
            max_context_length: 最大上下文长度（字符）
            max_memories: 最大记忆数量
        """
        self.max_context_length = max_context_length
        self.max_memories = max_memories
        self.logger = logger
    
    def build_enhanced_context(self, user_input: str, ranked_memories: List[Dict[str, Any]], 
                             personality_info: Optional[str] = None) -> str:
        """
        构建增强的上下文 (Step 8主函数)
        
        参数:
            user_input: 用户输入
            ranked_memories: 排序后的记忆列表
            personality_info: 个性化信息
            
        返回:
            构建好的上下文字符串
        """
        try:
            context_parts = []
            current_length = 0
            
            # 1. 角色设定部分
            if personality_info:
                role_section = self._build_role_section(personality_info)
                if self._can_add_section(current_length, role_section):
                    context_parts.append(role_section)
                    current_length += len(role_section)
            
            # 2. 核心记忆部分（高权重记忆）
            core_memories = [m for m in ranked_memories if m.get('computed_score', 0) >= 8.0]
            if core_memories:
                core_section = self._build_core_memories_section(core_memories[:5])
                if self._can_add_section(current_length, core_section):
                    context_parts.append(core_section)
                    current_length += len(core_section)
            
            # 3. 相关记忆部分（中等权重记忆）
            relevant_memories = [m for m in ranked_memories if 5.0 <= m.get('computed_score', 0) < 8.0]
            if relevant_memories:
                relevant_section = self._build_relevant_memories_section(relevant_memories[:8])
                if self._can_add_section(current_length, relevant_section):
                    context_parts.append(relevant_section)
                    current_length += len(relevant_section)
            
            # 4. 话题摘要部分
            topic_summary = self._build_topic_summary(ranked_memories)
            if topic_summary and self._can_add_section(current_length, topic_summary):
                context_parts.append(topic_summary)
                current_length += len(topic_summary)
            
            # 5. 时间相关信息
            time_context = self._build_time_context(ranked_memories)
            if time_context and self._can_add_section(current_length, time_context):
                context_parts.append(time_context)
                current_length += len(time_context)
            
            # 6. 用户当前输入
            user_section = f"[用户当前输入]\n{user_input}"
            context_parts.append(user_section)
            
            # 组装最终上下文
            final_context = "\n\n".join(context_parts)
            
            # 如果超长，进行智能截断
            if len(final_context) > self.max_context_length:
                final_context = self._smart_truncate(final_context, user_input)
            
            self.logger.debug(f"上下文构建完成: {len(final_context)} 字符, {len(context_parts)} 个部分")
            return final_context
            
        except Exception as e:
            self.logger.error(f"上下文构建失败: {e}")
            return f"[用户当前输入]\n{user_input}"
    
    def _build_role_section(self, personality_info: str) -> str:
        """构建角色设定部分"""
        return f"[角色设定]\n{personality_info}"
    
    def _build_core_memories_section(self, core_memories: List[Dict[str, Any]]) -> str:
        """构建核心记忆部分"""
        if not core_memories:
            return ""
        
        lines = ["[重要记忆]"]
        for memory in core_memories:
            weight = memory.get('weight', 0)
            summary = memory.get('summary', memory.get('content', ''))
            timestamp = self._format_timestamp(memory.get('timestamp'))
            
            # 限制每条记忆的长度
            if len(summary) > 120:
                summary = summary[:120] + "..."
            
            lines.append(f"• [{weight}分] {summary} ({timestamp})")
        
        return "\n".join(lines)
    
    def _build_relevant_memories_section(self, relevant_memories: List[Dict[str, Any]]) -> str:
        """构建相关记忆部分"""
        if not relevant_memories:
            return ""
        
        lines = ["[相关记忆]"]
        for memory in relevant_memories:
            summary = memory.get('summary', memory.get('content', ''))
            super_group = memory.get('super_group', '其他')
            
            # 限制每条记忆的长度
            if len(summary) > 100:
                summary = summary[:100] + "..."
            
            lines.append(f"• [{super_group}] {summary}")
        
        return "\n".join(lines)
    
    def _build_topic_summary(self, memories: List[Dict[str, Any]]) -> str:
        """构建话题摘要"""
        if not memories:
            return ""
        
        # 按super_group分组统计
        topic_counts = {}
        for memory in memories:
            super_group = memory.get('super_group', '其他')
            topic_counts[super_group] = topic_counts.get(super_group, 0) + 1
        
        if len(topic_counts) <= 1:
            return ""
        
        # 生成话题摘要
        topic_list = []
        for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 1:
                topic_list.append(f"{topic}({count}条)")
        
        if topic_list:
            return f"[话题分布]\n涉及话题: {', '.join(topic_list[:5])}"
        
        return ""
    
    def _build_time_context(self, memories: List[Dict[str, Any]]) -> str:
        """构建时间相关信息"""
        if not memories:
            return ""
        
        now = time.time()
        recent_memories = []
        old_memories = []
        
        for memory in memories:
            timestamp = memory.get('timestamp')
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.timestamp()
                    
                    time_diff_hours = (now - timestamp) / 3600
                    
                    if time_diff_hours < 24:
                        recent_memories.append(memory)
                    elif time_diff_hours > 168:  # 一周前
                        old_memories.append(memory)
                except:
                    continue
        
        time_info = []
        if recent_memories:
            time_info.append(f"最近24小时内: {len(recent_memories)}条记忆")
        if old_memories:
            time_info.append(f"一周前: {len(old_memories)}条记忆")
        
        if time_info:
            return f"[时间分布]\n{', '.join(time_info)}"
        
        return ""
    
    def _format_timestamp(self, timestamp) -> str:
        """格式化时间戳"""
        if not timestamp:
            return "未知时间"
        
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp = dt.timestamp()
            
            dt = datetime.fromtimestamp(timestamp)
            now = datetime.now()
            
            # 计算时间差
            diff = now - dt
            
            if diff.days > 7:
                return dt.strftime("%m-%d")
            elif diff.days > 0:
                return f"{diff.days}天前"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours}小时前"
            else:
                minutes = diff.seconds // 60
                return f"{minutes}分钟前"
                
        except Exception:
            return "未知时间"
    
    def _can_add_section(self, current_length: int, section: str) -> bool:
        """检查是否可以添加新的部分"""
        return current_length + len(section) < self.max_context_length * 0.9  # 留10%缓冲
    
    def _smart_truncate(self, context: str, user_input: str) -> str:
        """智能截断上下文"""
        try:
            lines = context.split('\n')
            
            # 确保用户输入部分总是保留
            user_section_start = -1
            for i, line in enumerate(lines):
                if line.startswith('[用户当前输入]'):
                    user_section_start = i
                    break
            
            if user_section_start == -1:
                # 如果没找到用户输入部分，添加它
                lines.append(f"[用户当前输入]\n{user_input}")
                user_section_start = len(lines) - 2
            
            # 从用户输入部分往前保留内容
            current_length = 0
            result_lines = []
            
            # 先添加用户输入部分
            for i in range(user_section_start, len(lines)):
                result_lines.append(lines[i])
                current_length += len(lines[i])
            
            # 从前面的部分选择性添加
            for i in range(user_section_start - 1, -1, -1):
                line_length = len(lines[i])
                if current_length + line_length < self.max_context_length:
                    result_lines.insert(0, lines[i])
                    current_length += line_length
                else:
                    break
            
            return '\n'.join(result_lines)
            
        except Exception as e:
            self.logger.error(f"智能截断失败: {e}")
            return f"[用户当前输入]\n{user_input}"
    
    def build_simple_context(self, user_input: str, memories: List[Dict[str, Any]]) -> str:
        """
        构建简单上下文（快速版本）
        
        参数:
            user_input: 用户输入
            memories: 记忆列表
            
        返回:
            简单的上下文字符串
        """
        try:
            if not memories:
                return f"[用户当前输入]\n{user_input}"
            
            context_parts = []
            
            # 选择最相关的几条记忆
            top_memories = memories[:5]
            
            if top_memories:
                context_parts.append("[相关记忆]")
                for memory in top_memories:
                    content = memory.get('content', memory.get('summary', ''))
                    if len(content) > 80:
                        content = content[:80] + "..."
                    context_parts.append(f"• {content}")
                context_parts.append("")
            
            # 添加用户输入
            context_parts.append(f"[用户当前输入]\n{user_input}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            self.logger.error(f"简单上下文构建失败: {e}")
            return f"[用户当前输入]\n{user_input}"
    
    def get_context_stats(self, context: str) -> Dict[str, Any]:
        """获取上下文统计信息"""
        try:
            lines = context.split('\n')
            sections = {}
            current_section = None
            
            for line in lines:
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    sections[current_section] = 0
                elif current_section:
                    sections[current_section] += 1
            
            return {
                "total_length": len(context),
                "total_lines": len(lines),
                "sections": sections,
                "within_limit": len(context) <= self.max_context_length
            }
            
        except Exception as e:
            self.logger.error(f"获取上下文统计失败: {e}")
            return {"error": str(e)} 