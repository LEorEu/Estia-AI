"""
关键词缓存系统
基于旧系统 core/old_memory/embedding/cache.py 的实现
"""

import re
import threading
import time
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict

class KeywordCache:
    """
    关键词缓存系统
    提供基于关键词的快速内容检索功能
    """
    
    def __init__(self, max_keywords: int = 10000):
        """初始化关键词缓存"""
        self.max_keywords = max_keywords
        self.keyword_cache: Dict[str, Set[str]] = defaultdict(set)
        self.keyword_metadata: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        
        # 中文停用词
        self.stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看',
            '好', '自己', '这', '那', '什么', '可以', '这个', '还', '时候', '如果'
        }
        
        # 英文停用词
        self.stop_words.update({
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'this', 'that', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall'
        })
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词
        基于旧系统的实现，支持中英文混合文本
        """
        if not text:
            return []
            
        # 提取中文和英文词汇
        words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        
        # 过滤停用词和短词
        keywords = []
        for word in words:
            if (len(word) > 1 and 
                word not in self.stop_words and 
                not word.isdigit()):
                keywords.append(word)
        
        # 限制关键词数量
        return keywords[:10]
    
    def add_to_keyword_cache(self, cache_key: str, text: str, weight: float = 1.0):
        """
        添加到关键词缓存
        
        Args:
            cache_key: 缓存键
            text: 文本内容
            weight: 权重
        """
        with self.lock:
            keywords = self._extract_keywords(text)
            
            for keyword in keywords:
                # 添加到关键词映射
                self.keyword_cache[keyword].add(cache_key)
                
                # 更新元数据
                if keyword not in self.keyword_metadata:
                    self.keyword_metadata[keyword] = {
                        'count': 0,
                        'weight': 0.0,
                        'last_updated': None
                    }
                
                # 更新统计信息
                self.keyword_metadata[keyword]['count'] += 1
                self.keyword_metadata[keyword]['weight'] = max(
                    self.keyword_metadata[keyword]['weight'], weight
                )
                self.keyword_metadata[keyword]['last_updated'] = time.time()
    
    def search_by_keywords(self, query: str, limit: int = 10) -> List[str]:
        """
        基于关键词搜索缓存项
        
        Args:
            query: 搜索查询
            limit: 返回结果数量限制
            
        Returns:
            相关的缓存键列表
        """
        with self.lock:
            keywords = self._extract_keywords(query)
            
            if not keywords:
                return []
            
            # 收集候选项
            candidates = defaultdict(float)
            
            for keyword in keywords:
                if keyword in self.keyword_cache:
                    # 获取包含此关键词的缓存项
                    cache_keys = self.keyword_cache[keyword]
                    keyword_weight = self.keyword_metadata[keyword]['weight']
                    
                    for cache_key in cache_keys:
                        # 计算相关性分数
                        candidates[cache_key] += keyword_weight
            
            # 按分数排序
            sorted_candidates = sorted(
                candidates.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return [cache_key for cache_key, score in sorted_candidates[:limit]]
    
    def remove_from_keyword_cache(self, cache_key: str):
        """
        从关键词缓存中移除项
        
        Args:
            cache_key: 要移除的缓存键
        """
        with self.lock:
            # 查找并移除包含此cache_key的关键词
            keywords_to_clean = []
            
            for keyword, cache_keys in self.keyword_cache.items():
                if cache_key in cache_keys:
                    cache_keys.remove(cache_key)
                    
                    # 如果该关键词没有其他缓存项，标记为待清理
                    if not cache_keys:
                        keywords_to_clean.append(keyword)
            
            # 清理空的关键词条目
            for keyword in keywords_to_clean:
                del self.keyword_cache[keyword]
                if keyword in self.keyword_metadata:
                    del self.keyword_metadata[keyword]
    
    def get_keyword_stats(self) -> Dict[str, Any]:
        """
        获取关键词缓存统计信息
        
        Returns:
            统计信息字典
        """
        with self.lock:
            return {
                'total_keywords': len(self.keyword_cache),
                'total_cache_items': sum(len(cache_keys) for cache_keys in self.keyword_cache.values()),
                'top_keywords': sorted(
                    [(keyword, len(cache_keys)) for keyword, cache_keys in self.keyword_cache.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }
    
    def clear_keyword_cache(self):
        """清理关键词缓存"""
        with self.lock:
            self.keyword_cache.clear()
            self.keyword_metadata.clear()
    
    def _maintain_keyword_cache(self):
        """
        维护关键词缓存
        清理过期和低权重的关键词
        """
        with self.lock:
            current_time = time.time()
            keywords_to_remove = []
            
            for keyword, metadata in self.keyword_metadata.items():
                # 检查是否过期（30天）
                if (current_time - metadata['last_updated']) > (30 * 24 * 3600):
                    keywords_to_remove.append(keyword)
                # 检查是否权重过低
                elif metadata['weight'] < 0.1 and metadata['count'] < 2:
                    keywords_to_remove.append(keyword)
            
            # 移除过期关键词
            for keyword in keywords_to_remove:
                if keyword in self.keyword_cache:
                    del self.keyword_cache[keyword]
                if keyword in self.keyword_metadata:
                    del self.keyword_metadata[keyword]
