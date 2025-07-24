#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据适配器模块
==============

处理不同数据源的适配和转换，包括v6.0监控系统、关键词分析、
记忆内容分析等功能。
"""

import time
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import Counter, defaultdict, deque
from threading import RLock

logger = logging.getLogger(__name__)


class DataCache:
    """数据缓存管理器，减少重复计算"""
    
    def __init__(self, cache_ttl: int = 3):
        """
        初始化缓存管理器
        
        Args:
            cache_ttl: 缓存生存时间（秒）
        """
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._timestamps = {}
        self._lock = RLock()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        with self._lock:
            if key not in self._cache:
                return None

            # 检查是否过期
            if time.time() - self._timestamps[key] > self.cache_ttl:
                del self._cache[key]
                del self._timestamps[key]
                return None

            return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        """设置缓存数据"""
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = time.time()

    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            return {
                'cache_size': len(self._cache),
                'cache_ttl': self.cache_ttl,
                'oldest_entry': min(self._timestamps.values()) if self._timestamps else None
            }


class KeywordAnalyzer:
    """关键词分析器"""
    
    def __init__(self):
        """初始化关键词分析器"""
        # 中文停用词
        self.stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '什么', '我们', '他们', '她们', '它们', '这个', '那个',
            '怎么', '为什么', '如何', '吗', '呢', '吧', '啊', '呀'
        }
        
        # 英文停用词
        self.stop_words.update({
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'me', 'him', 'her', 'us', 'them'
        })
    
    def extract_keywords(self, text: str, min_length: int = 2) -> List[str]:
        """
        提取关键词
        
        Args:
            text: 输入文本
            min_length: 最小关键词长度
            
        Returns:
            关键词列表
        """
        if not text:
            return []
        
        try:
            # 清理文本
            text = text.lower()
            # 保留中文、英文和数字
            text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
            
            # 分词（简单的基于空格和标点的分词）
            words = text.split()
            
            # 过滤关键词
            keywords = []
            for word in words:
                word = word.strip()
                if (len(word) >= min_length and 
                    word not in self.stop_words and
                    not word.isdigit()):
                    keywords.append(word)
            
            return keywords
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return []
    
    def analyze_keyword_trends(self, sessions: List) -> Dict[str, Any]:
        """
        分析关键词趋势
        
        Args:
            sessions: 会话列表
            
        Returns:
            关键词趋势分析结果
        """
        try:
            keyword_counts = Counter()
            time_series = defaultdict(list)
            
            for session in sessions:
                session_time = getattr(session, 'start_time', time.time())
                
                # 分析用户输入
                user_input = getattr(session, 'user_input', '')
                if user_input:
                    keywords = self.extract_keywords(user_input)
                    for keyword in keywords:
                        keyword_counts[keyword] += 1
                        time_series[keyword].append(session_time)
                
                # 分析AI回复中的关键词（取前5个避免过多）
                ai_response = getattr(session, 'ai_response', '')
                if ai_response:
                    response_keywords = self.extract_keywords(ai_response)[:5]
                    for keyword in response_keywords:
                        keyword_counts[f"回复_{keyword}"] += 1
            
            # 计算趋势
            trending_keywords = []
            for keyword, count in keyword_counts.most_common(20):
                if count >= 2:  # 至少出现2次
                    trending_keywords.append({
                        'word': keyword,
                        'count': count,
                        'frequency': count / len(sessions) if sessions else 0
                    })
            
            return {
                'top_keywords': trending_keywords,
                'total_unique_keywords': len(keyword_counts),
                'keyword_distribution': dict(keyword_counts.most_common(10))
            }
            
        except Exception as e:
            logger.error(f"关键词趋势分析失败: {e}")
            return {
                'top_keywords': [],
                'total_unique_keywords': 0,
                'keyword_distribution': {},
                'error': str(e)
            }


class MemoryContentAnalyzer:
    """记忆内容分析器"""
    
    def analyze_memory_patterns(self, sessions: List) -> Dict[str, Any]:
        """
        分析记忆模式
        
        Args:
            sessions: 会话列表
            
        Returns:
            记忆模式分析结果
        """
        try:
            memory_types = Counter()
            similarity_scores = []
            memory_usage = defaultdict(int)
            
            for session in sessions:
                # 尝试从session中提取步骤信息
                steps = getattr(session, 'steps', {})
                
                for step_name, metrics in steps.items():
                    step_str = str(step_name)
                    metadata = getattr(metrics, 'metadata', {})
                    
                    # 分析FAISS检索步骤
                    if 'faiss' in step_str.lower() or 'search' in step_str.lower():
                        if 'avg_similarity' in metadata:
                            similarity_scores.append(metadata['avg_similarity'])
                        if 'result_count' in metadata:
                            memory_usage['retrieved'] += metadata['result_count']
                    
                    # 分析关联扩展步骤
                    elif 'association' in step_str.lower() or 'expand' in step_str.lower():
                        if 'expansion_count' in metadata:
                            memory_usage['associations'] += metadata['expansion_count']
                    
                    # 分析上下文构建步骤
                    elif 'context' in step_str.lower() or 'build' in step_str.lower():
                        if 'memory_used' in metadata:
                            memory_usage['context_memories'] += metadata['memory_used']
            
            avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
            
            return {
                'average_similarity': avg_similarity,
                'memory_usage_stats': dict(memory_usage),
                'total_retrievals': len(similarity_scores),
                'similarity_distribution': self._calculate_similarity_distribution(similarity_scores)
            }
            
        except Exception as e:
            logger.error(f"记忆模式分析失败: {e}")
            return {
                'average_similarity': 0,
                'memory_usage_stats': {},
                'total_retrievals': 0,
                'similarity_distribution': {},
                'error': str(e)
            }
    
    def _calculate_similarity_distribution(self, scores: List[float]) -> Dict[str, int]:
        """计算相似度分布"""
        if not scores:
            return {'高 (>0.8)': 0, '中 (0.6-0.8)': 0, '低 (<0.6)': 0}
        
        bins = {'高 (>0.8)': 0, '中 (0.6-0.8)': 0, '低 (<0.6)': 0}
        
        for score in scores:
            if score > 0.8:
                bins['高 (>0.8)'] += 1
            elif score > 0.6:
                bins['中 (0.6-0.8)'] += 1
            else:
                bins['低 (<0.6)'] += 1
        
        return bins


class V6DataAdapter:
    """v6.0数据适配器，将v6.0监控数据转换为仪表板期望的格式"""
    
    def __init__(self, flow_monitor):
        """
        初始化v6.0数据适配器
        
        Args:
            flow_monitor: v6.0流程监控器实例
        """
        self.flow_monitor = flow_monitor
        self.is_fallback_mode = self._check_fallback_mode()
    
    def _check_fallback_mode(self) -> bool:
        """检查是否为降级模式"""
        try:
            return self.flow_monitor.__class__.__name__ == 'FallbackMonitor'
        except:
            return True
    
    def adapt_comprehensive_stats(self) -> Dict[str, Any]:
        """适配综合统计数据"""
        if not self.flow_monitor:
            return {'error': 'v6.0监控器不可用'}

        try:
            stats = self.flow_monitor.get_comprehensive_stats()

            # 检查是否是错误响应
            if 'error' in stats:
                return {
                    'error': stats['error'],
                    'fallback_mode': self.is_fallback_mode,
                    'timestamp': stats.get('timestamp', time.time())
                }

            # 转换为仪表板期望的格式
            adapted_stats = {
                'timestamp': stats.get('timestamp', time.time()),
                'monitor_status': stats.get('monitor_status', 'unknown'),
                'fallback_mode': self.is_fallback_mode,
                'performance_summary': {
                    'cache_hit_rate': stats.get('performance_metrics', {}).get('cache_hit_rate', 0),
                    'cache_efficiency': stats.get('performance_metrics', {}).get('cache_efficiency', 0),
                    'system_health': stats.get('health_status', {}).get('status', 'unknown')
                },
                'memory_overview': stats.get('memory_overview', {}),
                'session_stats': stats.get('session_statistics', {})
            }

            # 如果是降级模式，添加警告信息
            if self.is_fallback_mode:
                adapted_stats['warning'] = 'v6.0监控器不可用，显示降级数据'

            return adapted_stats

        except Exception as e:
            logger.error(f"适配综合统计失败: {e}")
            return {
                'error': f'适配综合统计失败: {str(e)}',
                'fallback_mode': self.is_fallback_mode,
                'timestamp': time.time()
            }
    
    def adapt_step_monitoring(self) -> Dict[str, Any]:
        """适配15步流程监控数据"""
        if not self.flow_monitor:
            return {'error': 'v6.0监控器不可用'}

        try:
            step_data = self.flow_monitor.get_13_step_monitoring()

            # 转换为仪表板期望的格式
            if 'error' in step_data:
                return step_data

            # 修正步骤数量 - 实际是15步
            adapted_data = {
                'total_steps': step_data.get('total_steps', 15),
                'sync_steps': step_data.get('sync_steps', 9),  # Step 1-9
                'async_steps': step_data.get('async_steps', 6),  # Step 10-15
                'step_performance': step_data.get('overall_performance', {}),
                'step_details': step_data.get('step_details', {}),
                'timestamp': step_data.get('timestamp', 0),
                'fallback_mode': self.is_fallback_mode
            }

            return adapted_data

        except Exception as e:
            logger.error(f"适配步骤监控失败: {e}")
            return {'error': f'适配步骤监控失败: {str(e)}'}
    
    def adapt_real_time_metrics(self) -> Dict[str, Any]:
        """适配实时性能指标"""
        if not self.flow_monitor:
            return {'error': 'v6.0监控器不可用'}
        
        try:
            metrics = self.flow_monitor.get_real_time_metrics()
            
            # 转换为仪表板期望的格式
            if 'error' in metrics:
                return metrics
            
            adapted_metrics = {
                'cache_performance': metrics.get('cache_performance', {}),
                'database_performance': metrics.get('database_performance', {}),
                'queue_status': metrics.get('queue_status', {}),
                'memory_usage': metrics.get('memory_usage', {}),
                'timestamp': metrics.get('timestamp', 0),
                'fallback_mode': self.is_fallback_mode
            }
            
            return adapted_metrics
            
        except Exception as e:
            logger.error(f"适配实时指标失败: {e}")
            return {'error': f'适配实时指标失败: {str(e)}'}