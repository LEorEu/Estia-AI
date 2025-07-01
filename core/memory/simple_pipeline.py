#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化记忆管道
"""

import time
import logging
from typing import Dict, Any, Optional

from .manager import EstiaMemoryManager, create_memory_manager

logger = logging.getLogger(__name__)

class SimpleMemoryPipeline:
    """简化记忆管道"""
    
    def __init__(self, enable_advanced: bool = True):
        logger.info("正在初始化简化记忆管道...")
        
        self.memory_manager = create_memory_manager(advanced=enable_advanced)
        self.enable_advanced = enable_advanced
        self.is_initialized = True
        
        logger.info(f"简化记忆管道初始化完成 (高级功能: {'启用' if enable_advanced else '禁用'})")
    
    def enhance_query(self, user_input: str, context: Optional[Dict] = None, personality: Optional[str] = None) -> str:
        """增强用户查询"""
        try:
            start_time = time.time()
            logger.debug(f"开始增强查询: {user_input[:30]}...")
            
            memories = self.memory_manager.retrieve_memories(
                query=user_input,
                limit=8,
                min_importance=4.0
            )
            
            enhanced_context = self._build_context(memories, user_input, personality)
            
            processing_time = time.time() - start_time
            logger.debug(f"查询增强完成，耗时: {processing_time*1000:.2f}ms，记忆数: {len(memories)}")
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"查询增强失败: {e}")
            # 即使失败，也要包含基本角色设定
            fallback = "[系统角色设定]\n你是Estia，一个智能、友好、乐于助人的AI助手。\n\n"
            fallback += f"[用户当前输入]\n{user_input}"
            return fallback
    
    def store_interaction(self, user_input: str, ai_response: str, context: Optional[Dict] = None):
        """存储交互记录"""
        try:
            user_importance = self._calculate_importance(user_input)
            ai_importance = self._calculate_importance(ai_response, is_ai=True)
            
            user_memory_id = self.memory_manager.store_memory(
                content=user_input,
                role="user",
                importance=user_importance,
                memory_type="dialogue",
                metadata={
                    "interaction_type": "user_input",
                    "timestamp": time.time()
                }
            )
            
            ai_memory_id = self.memory_manager.store_memory(
                content=ai_response,
                role="assistant",
                importance=ai_importance,
                memory_type="dialogue",
                metadata={
                    "interaction_type": "ai_response",
                    "timestamp": time.time(),
                    "related_user_memory": user_memory_id
                }
            )
            
            logger.debug(f"交互记录已存储: 用户={user_memory_id}, AI={ai_memory_id}")
            
        except Exception as e:
            logger.error(f"存储交互记录失败: {e}")
    
    def _build_context(self, memories: list, user_input: str, personality: Optional[str] = None) -> str:
        """构建增强上下文"""
        try:
            context_parts = []
            
            # 添加角色设定 (如果有)
            if personality:
                context_parts.append("[系统角色设定]")
                context_parts.append(personality)
                context_parts.append("")
            else:
                # 使用默认角色设定
                try:
                    from config import settings
                    from core.dialogue.personality import PERSONAS
                    active_persona = getattr(settings, 'ACTIVE_PERSONA', 'default')
                    default_personality = PERSONAS.get(active_persona, PERSONAS.get('default', ''))
                    if default_personality:
                        context_parts.append("[系统角色设定]")
                        context_parts.append(default_personality)
                        context_parts.append("")
                except ImportError:
                    # 如果无法导入配置，使用基础角色设定
                    context_parts.append("[系统角色设定]")
                    context_parts.append("你是Estia，一个智能、友好、乐于助人的AI助手。")
                    context_parts.append("")
            
            if not memories:
                # 即使没有记忆，也要包含角色设定
                context_parts.append(f"[用户当前输入]\n{user_input}")
                return "\n".join(context_parts)
            
            # 按层级分组记忆
            core_memories = [m for m in memories if m.get('layer') == 'core']
            active_memories = [m for m in memories if m.get('layer') == 'active']
            archive_memories = [m for m in memories if m.get('layer') == 'archive']
            
            # 核心记忆
            if core_memories:
                context_parts.append("[核心记忆]")
                for memory in core_memories[:2]:
                    content = memory.get('content', '')[:120]
                    importance = memory.get('importance', 0)
                    context_parts.append(f"• [重要性: {importance:.1f}] {content}")
                context_parts.append("")
            
            # 活跃记忆
            if active_memories:
                context_parts.append("[近期记忆]")
                for memory in active_memories[:3]:
                    content = memory.get('content', '')[:100]
                    role = memory.get('role', 'system')
                    context_parts.append(f"• [{role}] {content}")
                context_parts.append("")
            
            # 归档记忆
            if archive_memories:
                context_parts.append("[相关记忆]")
                for memory in archive_memories[:2]:
                    content = memory.get('content', '')[:80]
                    context_parts.append(f"• {content}")
                context_parts.append("")
            
            # 用户输入
            context_parts.append(f"[用户当前输入]\n{user_input}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"构建上下文失败: {e}")
            # 即使出错，也要确保有基本的角色设定
            fallback_context = "[系统角色设定]\n你是Estia，一个智能、友好、乐于助人的AI助手。\n\n"
            fallback_context += f"[用户当前输入]\n{user_input}"
            return fallback_context
    
    def _calculate_importance(self, content: str, is_ai: bool = False) -> float:
        """计算重要性"""
        try:
            base_importance = 5.0
            
            # 长度因素
            length_factor = min(len(content) / 100, 1.5)
            
            # 关键词因素
            important_keywords = [
                '重要', '关键', '必须', '紧急', '记住', '注意', 
                '项目', '工作', '任务', '计划', '问题', '解决'
            ]
            keyword_count = sum(1 for kw in important_keywords if kw in content)
            keyword_factor = min(keyword_count * 0.5, 2.0)
            
            # AI回复重要性调整
            ai_factor = 0.8 if is_ai else 1.0
            
            importance = (base_importance + length_factor + keyword_factor) * ai_factor
            return min(max(importance, 1.0), 10.0)
            
        except Exception as e:
            logger.warning(f"计算重要性失败: {e}")
            return 5.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.memory_manager.get_statistics()
    
    async def ensure_async_initialized(self):
        """确保异步组件初始化 (兼容性方法)"""
        try:
            logger.debug("异步组件初始化检查...")
            # 简化版本不需要复杂的异步初始化
            # 这里只是为了兼容现有的调用
            if not hasattr(self, '_async_initialized'):
                self._async_initialized = True
                logger.info("异步组件初始化完成")
        except Exception as e:
            logger.error(f"异步组件初始化失败: {e}")
            # 即使失败也不影响基本功能
            self._async_initialized = False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息 (兼容性方法)"""
        try:
            stats = self.memory_manager.get_statistics()
            
            # 转换为兼容格式
            layers_info = {}
            for layer_name, count in stats.get('layers', {}).items():
                capacity_map = {
                    'core': 100,
                    'active': 500, 
                    'archive': 2000,
                    'temp': 200
                }
                capacity = capacity_map.get(layer_name, 1000)
                utilization = count / capacity if capacity > 0 else 0
                
                layers_info[layer_name] = {
                    'count': count,
                    'capacity': capacity,
                    'utilization': utilization
                }
            
            return {
                'total_memories': stats.get('total_memories', 0),
                'layers': layers_info,
                'database_connected': stats.get('advanced_features', False),
                'async_evaluator_running': getattr(self, '_async_initialized', False)
            }
            
        except Exception as e:
            logger.error(f"获取记忆统计失败: {e}")
            return {
                'total_memories': 0,
                'layers': {},
                'database_connected': False,
                'async_evaluator_running': False
            }

def create_simple_pipeline(advanced: bool = True) -> SimpleMemoryPipeline:
    """创建简化记忆管道"""
    return SimpleMemoryPipeline(enable_advanced=advanced)