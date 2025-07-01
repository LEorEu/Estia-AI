#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Step 7: 记忆排序和去重模块
智能的记忆排序、评分和去重处理
"""

import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class MemoryScorer:
    """记忆评分器 - Step 7核心组件"""
    
    def __init__(self, 
                 weight_factor: float = 0.3,
                 time_factor: float = 0.2,
                 similarity_factor: float = 0.4,
                 type_factor: float = 0.1):
        """
        初始化记忆评分器
        
        参数:
            weight_factor: 权重因子
            time_factor: 时间因子  
            similarity_factor: 相似度因子
            type_factor: 类型因子
        """
        self.weight_factor = weight_factor
        self.time_factor = time_factor
        self.similarity_factor = similarity_factor
        self.type_factor = type_factor
        
        # 记忆类型权重
        self.type_weights = {
            'core': 1.0,
            'profile': 0.95,
            'summary': 0.9,
            'learning': 0.85,
            'dialogue': 0.8,
            'user_input': 0.75,
            'ai_response': 0.7,
            'system': 0.6,
            'temp': 0.4
        }
        
        logger.debug(f"记忆评分器初始化完成 (权重配置: w={weight_factor}, t={time_factor}, s={similarity_factor}, tp={type_factor})")
    
    def score_memories(self, memories: List[Dict[str, Any]], 
                      query: str = "", 
                      max_results: int = 10) -> List[Dict[str, Any]]:
        """
        对记忆进行评分和排序
        
        参数:
            memories: 记忆列表
            query: 查询文本（用于相似度计算）
            max_results: 最大返回结果数
            
        返回:
            排序后的记忆列表
        """
        if not memories:
            logger.debug("没有记忆需要评分")
            return []
        
        start_time = time.time()
        logger.debug(f"开始对 {len(memories)} 条记忆进行评分排序...")
        
        # 计算分数
        scored_memories = []
        current_time = time.time()
        
        for memory in memories:
            try:
                score = self._calculate_score(memory, query, current_time)
                memory_copy = memory.copy()
                memory_copy['computed_score'] = score
                scored_memories.append(memory_copy)
            except Exception as e:
                logger.warning(f"记忆评分失败: {e}")
                memory_copy = memory.copy()
                memory_copy['computed_score'] = 0.0
                scored_memories.append(memory_copy)
        
        # 去重处理
        deduplicated_memories = self._deduplicate_memories(scored_memories)
        
        # 按分数排序
        sorted_memories = sorted(deduplicated_memories, 
                               key=lambda m: m.get('computed_score', 0.0), 
                               reverse=True)
        
        # 限制结果数量
        result = sorted_memories[:max_results]
        
        processing_time = time.time() - start_time
        logger.debug(f"记忆评分完成，耗时: {processing_time*1000:.2f}ms，返回: {len(result)}/{len(memories)} 条")
        
        return result
    
    def _calculate_score(self, memory: Dict[str, Any], query: str, current_time: float) -> float:
        """计算单个记忆的综合分数"""
        try:
            # 基础权重分数
            weight_score = memory.get('importance', memory.get('weight', 5.0))
            
            # 时间衰减分数
            timestamp = memory.get('timestamp', current_time)
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).timestamp()
                except:
                    timestamp = current_time
            
            time_diff = max(current_time - timestamp, 0)
            time_score = self._calculate_time_decay(time_diff)
            
            # 相似度分数
            similarity_score = memory.get('similarity', memory.get('similarity_score', 0.5))
            if query and 'content' in memory:
                similarity_score = max(similarity_score, self._simple_similarity(query, memory['content']))
            
            # 类型权重分数
            memory_type = memory.get('type', memory.get('memory_type', 'dialogue'))
            type_score = self.type_weights.get(memory_type, 0.5)
            
            # 综合分数计算
            final_score = (
                weight_score * self.weight_factor +
                time_score * self.time_factor +
                similarity_score * 10 * self.similarity_factor +  # 相似度转换为10分制
                type_score * 10 * self.type_factor  # 类型分数转换为10分制
            )
            
            return round(final_score, 2)
            
        except Exception as e:
            logger.warning(f"分数计算失败: {e}")
            return 0.0
    
    def _calculate_time_decay(self, time_diff_seconds: float) -> float:
        """计算时间衰减分数"""
        hours = time_diff_seconds / 3600
        
        if hours < 1:      # 1小时内
            return 10.0
        elif hours < 24:   # 24小时内
            return 9.0 - (hours - 1) * 0.3
        elif hours < 168:  # 1周内
            return 7.0 - (hours - 24) / 24 * 0.2
        elif hours < 720:  # 1个月内
            return 5.0 - (hours - 168) / 24 * 0.1
        else:              # 1个月以上
            return max(2.0, 5.0 - (hours - 720) / 24 * 0.05)
    
    def _simple_similarity(self, query: str, content: str) -> float:
        """简单的文本相似度计算"""
        try:
            query_lower = query.lower()
            content_lower = content.lower()
            
            # 完全匹配
            if query_lower == content_lower:
                return 1.0
            
            # 包含关系
            if query_lower in content_lower:
                return 0.8
            
            # 关键词匹配
            query_words = set(query_lower.split())
            content_words = set(content_lower.split())
            
            if not query_words:
                return 0.0
            
            intersection = query_words.intersection(content_words)
            similarity = len(intersection) / len(query_words)
            
            return min(similarity, 1.0)
            
        except Exception as e:
            logger.warning(f"相似度计算失败: {e}")
            return 0.0
    
    def _deduplicate_memories(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """记忆去重处理"""
        if not memories:
            return []
        
        # 按内容分组
        content_groups = defaultdict(list)
        
        for memory in memories:
            content = memory.get('content', '').strip()
            if content:
                # 使用内容的前50个字符作为去重键
                dedup_key = content[:50].lower().replace(' ', '')
                content_groups[dedup_key].append(memory)
        
        # 每组保留分数最高的记忆
        deduplicated = []
        for group in content_groups.values():
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                # 保留分数最高的
                best_memory = max(group, key=lambda m: m.get('computed_score', 0.0))
                deduplicated.append(best_memory)
        
        # 如果去重效果明显，记录日志
        original_count = len(memories)
        final_count = len(deduplicated)
        if original_count > final_count:
            logger.debug(f"去重处理: {original_count} → {final_count} (-{original_count - final_count})")
        
        return deduplicated

# 便捷函数
def rank_memories(memories: List[Dict[str, Any]], 
                 query: str = "", 
                 max_results: int = 10) -> List[Dict[str, Any]]:
    """
    快速排序记忆的便捷函数
    
    参数:
        memories: 记忆列表
        query: 查询文本
        max_results: 最大结果数
        
    返回:
        排序后的记忆列表
    """
    scorer = MemoryScorer()
    return scorer.score_memories(memories, query, max_results)
