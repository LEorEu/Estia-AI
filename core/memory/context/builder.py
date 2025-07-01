#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Step 8: 上下文构建器
智能的上下文组装和管理
"""

import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextBuilder:
    """上下文构建器 - Step 8核心组件"""
    
    def __init__(self, 
                 max_context_length: int = 1500,
                 max_memories: int = 10,
                 core_memory_threshold: float = 8.0):
        """
        初始化上下文构建器
        
        参数:
            max_context_length: 最大上下文长度
            max_memories: 最大记忆数量
            core_memory_threshold: 核心记忆阈值
        """
        self.max_context_length = max_context_length
        self.max_memories = max_memories
        self.core_memory_threshold = core_memory_threshold
        
        logger.debug(f"上下文构建器初始化完成 (最大长度: {max_context_length}, 最大记忆数: {max_memories})")
    
    def build_context(self, 
                     memories: List[Dict[str, Any]], 
                     user_input: str,
                     personality: Optional[str] = None,
                     system_context: Optional[str] = None) -> str:
        """
        构建增强上下文
        
        参数:
            memories: 排序后的记忆列表
            user_input: 用户输入
            personality: 角色设定
            system_context: 系统上下文
            
        返回:
            构建好的上下文字符串
        """
        start_time = time.time()
        logger.debug(f"开始构建上下文，记忆数: {len(memories)}")
        
        try:
            context_parts = []
            current_length = 0
            
            # 1. 添加系统角色设定
            if personality:
                role_section = f"[系统角色设定]\n{personality}\n"
                context_parts.append(role_section)
                current_length += len(role_section)
            else:
                default_role = "[系统角色设定]\n你是Estia，一个智能、友好、乐于助人的AI助手。\n"
                context_parts.append(default_role)
                current_length += len(default_role)
            
            # 2. 添加系统上下文（如果有）
            if system_context:
                sys_section = f"[系统上下文]\n{system_context}\n"
                if current_length + len(sys_section) < self.max_context_length:
                    context_parts.append(sys_section)
                    current_length += len(sys_section)
            
            # 3. 按重要性分层组织记忆
            if memories:
                memory_sections = self._organize_memories_by_importance(memories)
                
                for section_title, section_memories in memory_sections.items():
                    if not section_memories:
                        continue
                    
                    section_content = self._build_memory_section(section_title, section_memories)
                    section_length = len(section_content)
                    
                    # 检查长度限制
                    if current_length + section_length < self.max_context_length:
                        context_parts.append(section_content)
                        current_length += section_length
                    else:
                        # 尝试添加部分内容
                        remaining_space = self.max_context_length - current_length - 100  # 预留空间
                        if remaining_space > 200:  # 至少需要200字符才有意义
                            truncated_section = self._truncate_section(section_content, remaining_space)
                            context_parts.append(truncated_section)
                            current_length += len(truncated_section)
                        break
            
            # 4. 添加用户当前输入
            user_input_section = f"[用户当前输入]\n{user_input}"
            
            # 确保用户输入总是被包含，必要时截断其他部分
            if current_length + len(user_input_section) > self.max_context_length:
                # 需要截断前面的内容
                available_space = self.max_context_length - len(user_input_section) - 50
                truncated_parts = self._truncate_context_parts(context_parts, available_space)
                context_parts = truncated_parts
            
            context_parts.append(user_input_section)
            
            # 组装最终上下文
            final_context = "\n".join(context_parts)
            
            processing_time = time.time() - start_time
            logger.debug(f"上下文构建完成，耗时: {processing_time*1000:.2f}ms，长度: {len(final_context)}")
            
            return final_context
            
        except Exception as e:
            logger.error(f"上下文构建失败: {e}")
            # 返回基础上下文
            fallback = f"[系统角色设定]\n你是Estia，一个智能、友好、乐于助人的AI助手。\n\n[用户当前输入]\n{user_input}"
            return fallback
    
    def _organize_memories_by_importance(self, memories: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按重要性分层组织记忆"""
        sections = {
            "核心记忆": [],
            "近期记忆": [],
            "相关记忆": [],
            "背景信息": []
        }
        
        for memory in memories[:self.max_memories]:
            importance = memory.get('importance', memory.get('weight', 0))
            
            if importance >= 9.0:
                sections["核心记忆"].append(memory)
            elif importance >= 7.0:
                sections["近期记忆"].append(memory)
            elif importance >= 5.0:
                sections["相关记忆"].append(memory)
            else:
                sections["背景信息"].append(memory)
        
        return sections
    
    def _build_memory_section(self, title: str, memories: List[Dict[str, Any]]) -> str:
        """构建记忆段落"""
        if not memories:
            return ""
        
        section_lines = [f"[{title}]"]
        
        for memory in memories:
            content = memory.get('content', '')
            role = memory.get('role', 'system')
            importance = memory.get('importance', memory.get('weight', 0))
            
            # 根据段落类型调整格式
            if title == "核心记忆":
                # 核心记忆显示重要性
                content_preview = content[:120] if len(content) > 120 else content
                line = f"• [重要性: {importance:.1f}] {content_preview}"
            elif title == "近期记忆":
                # 近期记忆显示角色
                content_preview = content[:100] if len(content) > 100 else content
                line = f"• [{role}] {content_preview}"
            else:
                # 其他记忆简化显示
                content_preview = content[:80] if len(content) > 80 else content
                line = f"• {content_preview}"
            
            section_lines.append(line)
        
        section_lines.append("")  # 添加空行分隔
        return "\n".join(section_lines)
    
    def _truncate_section(self, section_content: str, max_length: int) -> str:
        """截断段落内容"""
        if len(section_content) <= max_length:
            return section_content
        
        lines = section_content.split('\n')
        truncated_lines = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) + 1 <= max_length - 20:  # 预留省略号空间
                truncated_lines.append(line)
                current_length += len(line) + 1
            else:
                break
        
        if truncated_lines:
            truncated_lines.append("...")
            return "\n".join(truncated_lines)
        else:
            return section_content[:max_length-3] + "..."
    
    def _truncate_context_parts(self, context_parts: List[str], max_total_length: int) -> List[str]:
        """截断上下文部分"""
        if not context_parts:
            return []
        
        # 保留角色设定，尽量保留其他部分
        truncated_parts = [context_parts[0]]  # 保留角色设定
        current_length = len(context_parts[0])
        
        for part in context_parts[1:]:
            if current_length + len(part) <= max_total_length:
                truncated_parts.append(part)
                current_length += len(part)
            else:
                # 尝试截断这个部分
                remaining_space = max_total_length - current_length
                if remaining_space > 100:
                    truncated_part = self._truncate_section(part, remaining_space)
                    truncated_parts.append(truncated_part)
                break
        
        return truncated_parts

# 便捷函数
def build_context(memories: List[Dict[str, Any]], 
                 user_input: str,
                 personality: Optional[str] = None,
                 max_length: int = 1500) -> str:
    """
    快速构建上下文的便捷函数
    
    参数:
        memories: 记忆列表
        user_input: 用户输入
        personality: 角色设定
        max_length: 最大长度
        
    返回:
        构建好的上下文
    """
    builder = ContextBuilder(max_context_length=max_length)
    return builder.build_context(memories, user_input, personality) 