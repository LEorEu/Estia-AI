#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
上下文长度管理器
负责管理记忆系统的上下文长度配置和自适应调整
"""

import logging
from typing import Dict, List, Any, Optional
from core.dialogue.personality import get_role_setting_for_context
from config.settings import (
    MEMORY_CONTEXT_LIMITS, 
    MEMORY_CONTEXT_ADAPTIVE,
    MEMORY_CONTEXT_PRESETS,
    MEMORY_CONTEXT_PRESET,
    MEMORY_CONTEXT_DEFAULT_LIMITS as DEFAULT_LIMITS,
    MEMORY_CONTEXT_DEFAULT_ADAPTIVE as DEFAULT_ADAPTIVE
)

logger = logging.getLogger(__name__)

class ContextLengthManager:
    """上下文长度管理器"""
    
    def __init__(self, preset: Optional[str] = None):
        """
        初始化上下文长度管理器
        
        参数:
            preset: 预设配置名称，可选: "compact", "balanced", "detailed"
        """
        self.preset = preset or MEMORY_CONTEXT_PRESET
        self.limits = self._load_preset_config()
        self.adaptive_config = MEMORY_CONTEXT_ADAPTIVE
        
        logger.debug(f"上下文长度管理器初始化完成，使用预设: {self.preset}")
    
    def _load_preset_config(self) -> Dict[str, Any]:
        """加载预设配置"""
        base_limits = MEMORY_CONTEXT_LIMITS.copy()
        
        if self.preset in MEMORY_CONTEXT_PRESETS:
            preset_config = MEMORY_CONTEXT_PRESETS[self.preset]
            
            # 合并预设配置
            for section, config in preset_config.items():
                if section in base_limits:
                    base_limits[section].update(config)
                else:
                    base_limits[section] = config
        
        return base_limits
    
    def get_section_limit(self, section: str) -> Dict[str, Any]:
        """获取指定部分的长度限制"""
        return self.limits.get(section, {})
    
    def truncate_text(self, text: str, max_chars: int) -> str:
        """截断文本到指定长度"""
        if len(text) <= max_chars:
            return text
        
        # 智能截断：尽量在句号、逗号等标点处截断
        truncated = text[:max_chars]
        
        # 查找最后一个标点符号
        punctuation_marks = ['。', '！', '？', '；', '，', '.', '!', '?', ';', ',']
        last_punct = -1
        
        for punct in punctuation_marks:
            pos = truncated.rfind(punct)
            if pos > last_punct:
                last_punct = pos
        
        if last_punct > max_chars * 0.7:  # 如果标点在70%位置之后
            return truncated[:last_punct + 1]
        else:
            return truncated + "..."
    
    def format_current_session(self, dialogues: List[Dict[str, Any]]) -> str:
        """格式化当前会话对话"""
        limit = self.get_section_limit("current_session")
        max_dialogues = limit.get("max_dialogues", DEFAULT_LIMITS["current_session"]["max_dialogues"])
        max_chars = limit.get("max_chars_per_dialogue", DEFAULT_LIMITS["current_session"]["max_chars_per_dialogue"])
        
        formatted_parts = []
        for dialogue in dialogues[-max_dialogues:]:
            user_text = self.truncate_text(dialogue.get("user", ""), max_chars)
            assistant_text = self.truncate_text(dialogue.get("assistant", ""), max_chars)
            
            formatted_parts.append(f"  你: {user_text}")
            formatted_parts.append(f"  我: {assistant_text}")
        
        return "\n".join(formatted_parts)
    
    def format_core_memories(self, memories: List[Dict[str, Any]]) -> str:
        """格式化核心记忆"""
        limit = self.get_section_limit("core_memories")
        max_count = limit.get("max_count", DEFAULT_LIMITS["core_memories"]["max_count"])
        max_chars = limit.get("max_chars_per_memory", DEFAULT_LIMITS["core_memories"]["max_chars_per_memory"])
        min_weight = limit.get("min_weight", DEFAULT_LIMITS["core_memories"]["min_weight"])
        
        # 筛选高权重记忆
        core_memories = [m for m in memories if m.get('weight', 0) >= min_weight]
        core_memories = core_memories[:max_count]
        
        formatted_parts = []
        for memory in core_memories:
            content = self.truncate_text(memory.get('content', ''), max_chars)
            weight = memory.get('weight', 0)
            formatted_parts.append(f"• [权重: {weight:.1f}] {content}")
        
        return "\n".join(formatted_parts)
    
    def format_historical_dialogues(self, session_dialogues: Dict[str, Any]) -> str:
        """格式化历史对话"""
        limit = self.get_section_limit("historical_dialogues")
        max_sessions = limit.get("max_sessions", DEFAULT_LIMITS["historical_dialogues"]["max_sessions"])
        max_dialogues_per_session = limit.get("max_dialogues_per_session", DEFAULT_LIMITS["historical_dialogues"]["max_dialogues_per_session"])
        max_chars = limit.get("max_chars_per_dialogue", DEFAULT_LIMITS["historical_dialogues"]["max_chars_per_dialogue"])
        
        formatted_parts = []
        session_count = 0
        
        for session_id, session_data in session_dialogues.items():
            if session_count >= max_sessions:
                break
                
            dialogue_pairs = session_data.get('dialogue_pairs', [])
            if dialogue_pairs:
                formatted_parts.append(f"会话 {session_id}:")
                
                for i, pair in enumerate(dialogue_pairs[-max_dialogues_per_session:]):
                    user_content = self.truncate_text(pair['user']['content'], max_chars)
                    ai_content = self.truncate_text(pair['assistant']['content'], max_chars)
                    formatted_parts.append(f"  {i+1}. 你: {user_content}")
                    formatted_parts.append(f"     我: {ai_content}")
                
                session_count += 1
        
        return "\n".join(formatted_parts)
    
    def format_relevant_memories(self, memories: List[Dict[str, Any]]) -> str:
        """格式化相关记忆"""
        limit = self.get_section_limit("relevant_memories")
        max_count = limit.get("max_count", DEFAULT_LIMITS["relevant_memories"]["max_count"])
        max_chars = limit.get("max_chars_per_memory", DEFAULT_LIMITS["relevant_memories"]["max_chars_per_memory"])
        min_weight = limit.get("min_weight", DEFAULT_LIMITS["relevant_memories"]["min_weight"])
        
        # 筛选中等权重记忆
        relevant_memories = [m for m in memories if m.get('weight', 0) >= min_weight]
        relevant_memories = relevant_memories[:max_count]
        
        formatted_parts = []
        for memory in relevant_memories:
            content = self.truncate_text(memory.get('content', ''), max_chars)
            timestamp = memory.get('timestamp', 0)
            try:
                from datetime import datetime
                time_str = datetime.fromtimestamp(timestamp).strftime('%m-%d %H:%M')
            except:
                time_str = "未知时间"
            formatted_parts.append(f"• [{time_str}] {content}")
        
        return "\n".join(formatted_parts)
    
    def format_summaries(self, summaries: List[Dict[str, Any]]) -> str:
        """格式化总结内容"""
        limit = self.get_section_limit("summaries")
        max_count = limit.get("max_count", DEFAULT_LIMITS["summaries"]["max_count"])
        max_chars = limit.get("max_chars_per_summary", DEFAULT_LIMITS["summaries"]["max_chars_per_summary"])
        
        formatted_parts = []
        for summary in summaries[:max_count]:
            content = self.truncate_text(summary.get('content', ''), max_chars)
            formatted_parts.append(f"• {content}")
        
        return "\n".join(formatted_parts)
    
    def build_enhanced_context(self, 
                             user_input: str,
                             memories: List[Dict[str, Any]],
                             historical_context: Dict[str, Any],
                             current_session_id: Optional[str] = None,
                             current_session_dialogues: Optional[List[Dict[str, Any]]] = None) -> str:
        """构建增强上下文"""
        context_parts = []
        current_length = 0
        
        # 1. 角色设定（固定，最高优先级）
        role_limit = self.get_section_limit("role_setting")
        role_setting = get_role_setting_for_context()
        
        context_parts.append(role_setting)
        current_length += len(role_setting)
        context_parts.append("")
        
        # 2. 当前会话对话（最高优先级）
        if current_session_dialogues:
            current_session_text = self.format_current_session(current_session_dialogues)
            if current_session_text:
                context_parts.append("[当前会话]")
                context_parts.append(current_session_text)
                context_parts.append("")
                current_length += len(current_session_text) + 20
        
        # 3. 核心记忆
        core_memories_text = self.format_core_memories(memories)
        if core_memories_text:
            context_parts.append("[核心记忆]")
            context_parts.append(core_memories_text)
            context_parts.append("")
            current_length += len(core_memories_text) + 20
        
        # 4. 相关历史对话
        session_dialogues = historical_context.get('session_dialogues', {})
        if session_dialogues:
            historical_text = self.format_historical_dialogues(session_dialogues)
            if historical_text:
                context_parts.append("[相关历史对话]")
                context_parts.append(historical_text)
                context_parts.append("")
                current_length += len(historical_text) + 30
        
        # 5. 相关记忆
        relevant_memories_text = self.format_relevant_memories(memories)
        if relevant_memories_text:
            context_parts.append("[相关记忆]")
            context_parts.append(relevant_memories_text)
            context_parts.append("")
            current_length += len(relevant_memories_text) + 20
        
        # 6. 重要总结
        summaries_data = historical_context.get('summaries', {})
        all_summaries = []
        all_summaries.extend(summaries_data.get('direct_summaries', []))
        all_summaries.extend(summaries_data.get('memory_summaries', []))
        
        if all_summaries:
            summaries_text = self.format_summaries(all_summaries)
            if summaries_text:
                context_parts.append("[重要总结]")
                context_parts.append(summaries_text)
                context_parts.append("")
                current_length += len(summaries_text) + 20
        
        # 7. 当前用户输入
        context_parts.append(f"[当前输入] {user_input}")
        context_parts.append("")
        context_parts.append("请基于以上记忆和历史对话，给出自然、连贯的回复：")
        
        # 8. 自适应长度调整
        if self.adaptive_config.get("enabled", True):
            final_context = self._adaptive_length_adjustment(context_parts, current_length)
        else:
            final_context = "\n".join(context_parts)
        
        logger.debug(f"上下文构建完成，长度: {len(final_context)} 字符，预设: {self.preset}")
        return final_context
    
    def _adaptive_length_adjustment(self, context_parts: List[str], current_length: int) -> str:
        """自适应长度调整"""
        max_length = self.adaptive_config.get("max_length", DEFAULT_ADAPTIVE["max_length"])
        target_length = self.adaptive_config.get("target_length", DEFAULT_ADAPTIVE["target_length"])
        compression_ratio = self.adaptive_config.get("compression_ratio", DEFAULT_ADAPTIVE["compression_ratio"])
        
        full_context = "\n".join(context_parts)
        
        if len(full_context) <= max_length:
            return full_context
        
        # 超出长度限制，进行压缩
        logger.warning(f"上下文长度超出限制: {len(full_context)} > {max_length}，进行压缩")
        
        # 按优先级压缩各部分
        compressed_parts = []
        remaining_length = max_length - 200  # 保留200字符给角色设定和当前输入
        
        # 保留角色设定和当前输入
        for i, part in enumerate(context_parts):
            if "[系统角色设定]" in part or "[当前输入]" in part:
                compressed_parts.append(part)
                remaining_length -= len(part)
        
        # 按优先级添加其他部分
        priority_sections = [
            ("[当前会话]", 1),
            ("[核心记忆]", 2),
            ("[相关历史对话]", 3),
            ("[相关记忆]", 4),
            ("[重要总结]", 5)
        ]
        
        for section_marker, priority in priority_sections:
            for part in context_parts:
                if section_marker in part:
                    if len(part) <= remaining_length:
                        compressed_parts.append(part)
                        remaining_length -= len(part)
                    else:
                        # 压缩这个部分
                        compressed_part = self._compress_section(part, remaining_length, compression_ratio)
                        if compressed_part:
                            compressed_parts.append(compressed_part)
                            remaining_length -= len(compressed_part)
                    break
        
        return "\n".join(compressed_parts)
    
    def _compress_section(self, section_text: str, max_length: int, compression_ratio: float) -> str:
        """压缩指定部分"""
        if len(section_text) <= max_length:
            return section_text
        
        # 简单的压缩策略：截断到指定长度
        compressed_length = int(max_length * compression_ratio)
        return self.truncate_text(section_text, compressed_length)
    
    def get_context_stats(self) -> Dict[str, Any]:
        """获取上下文统计信息"""
        return {
            "preset": self.preset,
            "limits": self.limits,
            "adaptive_enabled": self.adaptive_config.get("enabled", True),
            "max_length": self.adaptive_config.get("max_length", DEFAULT_ADAPTIVE["max_length"]),
            "target_length": self.adaptive_config.get("target_length", DEFAULT_ADAPTIVE["target_length"])
        }