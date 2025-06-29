"""
记忆缓存系统 - 融合了旧系统的优秀特性
实现了多级缓存策略、关键词缓存和智能缓存提升机制
"""

import os
import json
import hashlib
import numpy as np
import time
import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from collections import OrderedDict

# 尝试导入日志工具
try:
    from core.utils.logger import get_logger
    logger = get_logger("estia.memory.embedding.cache")
except ImportError:
    # 如果还没有日志工具，使用标准日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("estia.memory.embedding.cache")

class EnhancedMemoryCache:
    """
    增强版记忆缓存系统，融合了旧系统的优秀特性：
    1. 多级缓存策略：热缓存 + 温缓存 + 持久化缓存
    2. 关键词缓存：加速文本检索
    3. 智能缓存提升机制：基于访问频率和重要性自动调整缓存级别
    """
    
    def __init__(self, cache_dir: Optional[str] = None, hot_capacity: int = 200, 
                 warm_capacity: int = 1000, persist: bool = True,
                 cache_file: str = "embedding_cache.json",
                 max_memory_size: Optional[int] = None):  # 向后兼容参数
        """
        初始化增强版缓存系统
        
        参数:
            cache_dir: 缓存目录
            hot_capacity: 热缓存容量，存储最常访问和最重要的记忆
            warm_capacity: 温缓存容量，存储次常访问的记忆
            persist: 是否启用持久化缓存
            cache_file: 缓存索引文件名
            max_memory_size: 向后兼容参数，如果提供则用作总缓存大小
        """
        # 向后兼容性处理
        if max_memory_size is not None:
            # 如果提供了旧参数，按比例分配热缓存和温缓存
            hot_capacity = max(50, max_memory_size // 10)  # 热缓存占10%，最少50
            warm_capacity = max_memory_size - hot_capacity
        
        self.hot_capacity = hot_capacity
        self.warm_capacity = warm_capacity
        self.persist = persist
        
        # 设置缓存目录
        if cache_dir is None:
            self.cache_dir = os.path.join("data", "memory", "cache")
        else:
            self.cache_dir = cache_dir
            
        # 确保目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.cache_file = os.path.join(self.cache_dir, cache_file)
        
        # 三级缓存系统
        self.hot_cache = OrderedDict()    # 热缓存：最常访问和最重要的记忆
        self.warm_cache = OrderedDict()   # 温缓存：次常访问的记忆
        
        # 关键词缓存：存储关键词到记忆键的映射，用于加速检索
        self.keyword_cache = {}
        
        # 记忆元数据：用于智能缓存提升决策
        self.memory_metadata = {}  # key -> {access_count, last_accessed, weight, created_at}
        
        # 统计信息
        self.stats = {
            "hot_hits": 0,
            "warm_hits": 0,
            "keyword_hits": 0,
            "persistent_hits": 0,
            "misses": 0,
            "promotions": 0,  # 缓存提升次数
            "evictions": 0,   # 缓存驱逐次数
            "last_maintenance": time.time()
        }
        
        # 配置参数
        self.promotion_threshold = 3      # 访问次数达到此值可能被提升
        self.importance_threshold = 7.0   # 重要性权重达到此值可能被提升
        self.maintenance_interval = 300   # 缓存维护间隔（秒）
        
        # 加载持久化缓存
        if persist:
            self._load_cache()
            
        logger.info(f"增强版缓存系统初始化完成 - 热缓存:{hot_capacity}, 温缓存:{warm_capacity}")
    
    def _text_to_key(self, text: str) -> str:
        """将文本转换为缓存键"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def get(self, text: str, memory_weight: float = 1.0) -> Optional[np.ndarray]:
        """
        从缓存中获取向量，支持智能缓存提升
        
        参数:
            text: 输入文本
            memory_weight: 记忆重要性权重
            
        返回:
            Optional[np.ndarray]: 缓存的向量或None
        """
        cache_key = self._text_to_key(text)
        current_time = time.time()
        
        # 1. 检查热缓存
        if cache_key in self.hot_cache:
            vector = self.hot_cache.pop(cache_key)
            self.hot_cache[cache_key] = vector  # 移至最近使用位置
            
            self._update_access_metadata(cache_key, memory_weight, current_time)
            self.stats["hot_hits"] += 1
            logger.debug(f"热缓存命中: {text[:30]}...")
            return vector
        
        # 2. 检查温缓存
        if cache_key in self.warm_cache:
            vector = self.warm_cache.pop(cache_key)
            
            self._update_access_metadata(cache_key, memory_weight, current_time)
            
            # 检查是否应该提升到热缓存
            if self._should_promote_to_hot(cache_key):
                self._promote_to_hot_cache(cache_key, vector)
                self.stats["promotions"] += 1
                logger.debug(f"记忆提升至热缓存: {text[:30]}...")
            else:
                self.warm_cache[cache_key] = vector  # 保留在温缓存
            
            self.stats["warm_hits"] += 1
            return vector
        
        # 3. 检查持久化缓存
        if self.persist:
            vector = self._load_from_persistent_cache(cache_key)
            if vector is not None:
                self._update_access_metadata(cache_key, memory_weight, current_time)
                
                # 决定添加到哪个缓存级别
                if self._should_promote_to_hot(cache_key):
                    self._promote_to_hot_cache(cache_key, vector)
                else:
                    self._add_to_warm_cache(cache_key, vector)
                
                self.stats["persistent_hits"] += 1
                logger.debug(f"持久化缓存命中: {text[:30]}...")
                return vector
        
        # 4. 缓存未命中
        self.stats["misses"] += 1
        return None
    
    def put(self, text: str, vector: np.ndarray, memory_weight: float = 1.0) -> None:
        """
        将向量添加到缓存，智能决定缓存级别
        
        参数:
            text: 输入文本
            vector: 对应的向量表示
            memory_weight: 记忆重要性权重
        """
        cache_key = self._text_to_key(text)
        current_time = time.time()
        
        # 初始化元数据
        if cache_key not in self.memory_metadata:
            self.memory_metadata[cache_key] = {
                "access_count": 1,
                "last_accessed": current_time,
                "weight": memory_weight,
                "created_at": current_time,
                "text_preview": text[:100]  # 保存文本预览用于调试
            }
        
        # 根据重要性决定初始缓存级别
        if memory_weight >= self.importance_threshold:
            # 重要记忆直接进入热缓存
            self._promote_to_hot_cache(cache_key, vector)
            logger.debug(f"重要记忆直接进入热缓存: {text[:30]}... (权重: {memory_weight})")
        else:
            # 普通记忆进入温缓存
            self._add_to_warm_cache(cache_key, vector)
        
        # 更新关键词缓存
        self._update_keyword_cache(cache_key, text)
        
        # 保存到持久化缓存
        if self.persist:
            self._save_to_persistent_cache(cache_key, vector, text)
        
        # 定期维护缓存
        if current_time - self.stats["last_maintenance"] > self.maintenance_interval:
            self._maintain_cache()
    
    def search_by_content(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        根据内容搜索缓存中的记忆，利用关键词缓存加速
        
        参数:
            query: 搜索查询
            limit: 最大返回条数
            
        返回:
            List[Dict]: 匹配的记忆列表，包含向量和元数据
        """
        # 1. 先尝试关键词缓存
        keywords = self._extract_keywords(query)
        candidates = set()
        
        for keyword in keywords:
            if keyword in self.keyword_cache:
                self.stats["keyword_hits"] += 1
                candidates.update(self.keyword_cache[keyword])
        
        # 2. 计算相关性分数
        results = []
        query_words = set(query.lower().split())
        
        # 搜索热缓存
        for cache_key in self.hot_cache:
            if not candidates or cache_key in candidates:
                score = self._calculate_relevance_score(cache_key, query, query_words)
                if score > 0:
                    results.append({
                        "key": cache_key,
                        "vector": self.hot_cache[cache_key],
                        "score": score,
                        "cache_level": "hot",
                        "metadata": self.memory_metadata.get(cache_key, {})
                    })
        
        # 如果结果不够，搜索温缓存
        if len(results) < limit:
            for cache_key in self.warm_cache:
                if not candidates or cache_key in candidates:
                    score = self._calculate_relevance_score(cache_key, query, query_words)
                    if score > 0:
                        results.append({
                            "key": cache_key,
                            "vector": self.warm_cache[cache_key],
                            "score": score,
                            "cache_level": "warm",
                            "metadata": self.memory_metadata.get(cache_key, {})
                        })
        
        # 按相关性排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # 更新访问统计
        for result in results[:limit]:
            cache_key = result["key"]
            self._update_access_metadata(cache_key, 
                                       result["metadata"].get("weight", 1.0), 
                                       time.time())
        
        return results[:limit]
    
    def _should_promote_to_hot(self, cache_key: str) -> bool:
        """判断是否应该提升到热缓存"""
        if cache_key not in self.memory_metadata:
            return False
            
        metadata = self.memory_metadata[cache_key]
        access_count = metadata.get("access_count", 0)
        weight = metadata.get("weight", 1.0)
        
        # 提升条件：访问频繁 OR 重要性高
        return (access_count >= self.promotion_threshold or 
                weight >= self.importance_threshold)
    
    def _promote_to_hot_cache(self, cache_key: str, vector: np.ndarray) -> None:
        """将记忆提升到热缓存"""
        # 确保热缓存有空间
        if len(self.hot_cache) >= self.hot_capacity:
            # 移除最久未使用的项到温缓存
            old_key, old_vector = self.hot_cache.popitem(last=False)
            self._add_to_warm_cache(old_key, old_vector)
            self.stats["evictions"] += 1
        
        self.hot_cache[cache_key] = vector
    
    def _add_to_warm_cache(self, cache_key: str, vector: np.ndarray) -> None:
        """添加到温缓存"""
        # 确保温缓存有空间
        if len(self.warm_cache) >= self.warm_capacity:
            # 移除最久未使用的项
            self.warm_cache.popitem(last=False)
            self.stats["evictions"] += 1
        
        self.warm_cache[cache_key] = vector
    
    def _update_access_metadata(self, cache_key: str, weight: float, current_time: float) -> None:
        """更新访问元数据"""
        if cache_key not in self.memory_metadata:
            self.memory_metadata[cache_key] = {
                "access_count": 0,
                "weight": weight,
                "created_at": current_time
            }
        
        metadata = self.memory_metadata[cache_key]
        metadata["access_count"] = metadata.get("access_count", 0) + 1
        metadata["last_accessed"] = current_time
        metadata["weight"] = max(metadata.get("weight", 1.0), weight)  # 保持最高权重
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取：去除停用词，保留有意义的词汇
        stop_words = {"的", "了", "在", "是", "我", "你", "他", "她", "它", "们", 
                     "这", "那", "有", "和", "与", "或", "但", "如果", "因为", "所以"}
        
        # 使用正则表达式分词（支持中英文）
        words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        
        # 过滤停用词和短词
        keywords = [word for word in words 
                   if len(word) > 1 and word not in stop_words]
        
        return keywords[:10]  # 限制关键词数量
    
    def _update_keyword_cache(self, cache_key: str, text: str) -> None:
        """更新关键词缓存"""
        keywords = self._extract_keywords(text)
        
        for keyword in keywords:
            if keyword not in self.keyword_cache:
                self.keyword_cache[keyword] = set()
            self.keyword_cache[keyword].add(cache_key)
    
    def _calculate_relevance_score(self, cache_key: str, query: str, query_words: set) -> float:
        """计算记忆与查询的相关性分数"""
        if cache_key not in self.memory_metadata:
            return 0.0
            
        metadata = self.memory_metadata[cache_key]
        text_preview = metadata.get("text_preview", "").lower()
        
        if not text_preview:
            return 0.0
        
        # 1. 直接包含查询
        if query.lower() in text_preview:
            return 3.0 * metadata.get("weight", 1.0)
        
        # 2. 词汇重叠率
        if not query_words:
            return 0.0
            
        text_words = set(re.findall(r'[\w\u4e00-\u9fff]+', text_preview))
        overlap_rate = len(query_words.intersection(text_words)) / len(query_words)
        
        # 3. 综合分数：重叠率 × 重要性权重 × 访问频率因子
        access_factor = min(2.0, 1.0 + metadata.get("access_count", 0) * 0.1)
        score = overlap_rate * metadata.get("weight", 1.0) * access_factor
        
        return score
    
    def _load_from_persistent_cache(self, cache_key: str) -> Optional[np.ndarray]:
        """从持久化缓存加载向量"""
        try:
            vector_file = os.path.join(self.cache_dir, f"{cache_key}.npy")
            if os.path.exists(vector_file):
                return np.load(vector_file)
        except Exception as e:
            logger.error(f"加载持久化缓存失败: {e}")
        return None
    
    def _save_to_persistent_cache(self, cache_key: str, vector: np.ndarray, text: str) -> None:
        """保存到持久化缓存"""
        try:
            vector_file = os.path.join(self.cache_dir, f"{cache_key}.npy")
            np.save(vector_file, vector)
            
            # 更新索引
            self._update_cache_index(cache_key, text)
        except Exception as e:
            logger.error(f"保存持久化缓存失败: {e}")
    
    def _load_cache(self) -> None:
        """加载缓存索引和元数据"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.memory_metadata = data.get("memory_metadata", {})
                self.keyword_cache = data.get("keyword_cache", {})
                
                # 将set转换回来（JSON不支持set）
                for keyword in self.keyword_cache:
                    self.keyword_cache[keyword] = set(self.keyword_cache[keyword])
                    
                logger.info(f"加载缓存索引: {len(self.memory_metadata)} 个记忆, "
                          f"{len(self.keyword_cache)} 个关键词")
            except Exception as e:
                logger.error(f"加载缓存索引失败: {e}")
    
    def _update_cache_index(self, cache_key: str, text: str) -> None:
        """更新缓存索引"""
        # 定期保存索引（避免频繁写入）
        current_time = time.time()
        if current_time - self.stats.get("last_save", 0) > 60:  # 每分钟保存一次
            self._save_cache_index()
            self.stats["last_save"] = current_time
    
    def _save_cache_index(self) -> None:
        """保存缓存索引"""
        try:
            # 将set转换为list（JSON不支持set）
            keyword_cache_serializable = {}
            for keyword, cache_keys in self.keyword_cache.items():
                keyword_cache_serializable[keyword] = list(cache_keys)
            
            data = {
                "memory_metadata": self.memory_metadata,
                "keyword_cache": keyword_cache_serializable,
                "stats": self.stats
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存缓存索引失败: {e}")
    
    def _maintain_cache(self) -> None:
        """定期维护缓存：清理过期项、优化缓存分布"""
        current_time = time.time()
        
        # 1. 清理长时间未访问的关键词缓存
        expired_keywords = []
        for keyword, cache_keys in self.keyword_cache.items():
            # 检查是否还有有效的缓存键
            valid_keys = set()
            for cache_key in cache_keys:
                if (cache_key in self.hot_cache or 
                    cache_key in self.warm_cache or
                    cache_key in self.memory_metadata):
                    valid_keys.add(cache_key)
            
            if valid_keys:
                self.keyword_cache[keyword] = valid_keys
            else:
                expired_keywords.append(keyword)
        
        # 删除过期关键词
        for keyword in expired_keywords:
            del self.keyword_cache[keyword]
        
        # 2. 清理过期元数据
        expired_metadata = []
        for cache_key in self.memory_metadata:
            metadata = self.memory_metadata[cache_key]
            last_accessed = metadata.get("last_accessed", 0)
            
            # 30天未访问且不在任何缓存中
            if (current_time - last_accessed > 30 * 24 * 3600 and
                cache_key not in self.hot_cache and
                cache_key not in self.warm_cache):
                expired_metadata.append(cache_key)
        
        for cache_key in expired_metadata:
            del self.memory_metadata[cache_key]
        
        # 3. 保存更新
        self._save_cache_index()
        
        self.stats["last_maintenance"] = current_time
        logger.info(f"缓存维护完成: 清理 {len(expired_keywords)} 个关键词, "
                   f"{len(expired_metadata)} 个过期元数据")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = (self.stats["hot_hits"] + self.stats["warm_hits"] + 
                         self.stats["persistent_hits"] + self.stats["misses"])
        
        hit_rate = 0.0
        if total_requests > 0:
            total_hits = (self.stats["hot_hits"] + self.stats["warm_hits"] + 
                         self.stats["persistent_hits"])
            hit_rate = total_hits / total_requests
        
        return {
            "cache_levels": {
                "hot_cache_size": len(self.hot_cache),
                "warm_cache_size": len(self.warm_cache),
                "hot_capacity": self.hot_capacity,
                "warm_capacity": self.warm_capacity
            },
            "hit_statistics": {
                "hot_hits": self.stats["hot_hits"],
                "warm_hits": self.stats["warm_hits"],
                "persistent_hits": self.stats["persistent_hits"],
                "keyword_hits": self.stats["keyword_hits"],
                "misses": self.stats["misses"],
                "total_requests": total_requests,
                "hit_rate": f"{hit_rate:.2%}"
            },
            "cache_management": {
                "promotions": self.stats["promotions"],
                "evictions": self.stats["evictions"],
                "keyword_count": len(self.keyword_cache),
                "metadata_count": len(self.memory_metadata)
            },
            "maintenance": {
                "last_maintenance": time.strftime("%Y-%m-%d %H:%M:%S", 
                                                 time.localtime(self.stats["last_maintenance"]))
            }
        }
    
    def clear_all_cache(self) -> None:
        """清空所有缓存"""
        self.hot_cache.clear()
        self.warm_cache.clear()
        self.keyword_cache.clear()
        self.memory_metadata.clear()
        
        # 重置统计
        self.stats = {
            "hot_hits": 0,
            "warm_hits": 0,
            "keyword_hits": 0,
            "persistent_hits": 0,
            "misses": 0,
            "promotions": 0,
            "evictions": 0,
            "last_maintenance": time.time()
        }
        
        logger.info("所有缓存已清空")


# 保持向后兼容性的别名
EmbeddingCache = EnhancedMemoryCache

# 模块测试代码
if __name__ == "__main__":
    import numpy as np
    
    print("测试Embedding缓存...")
    
    # 创建缓存实例
    cache = EmbeddingCache(max_memory_size=100)
    
    # 测试缓存功能
    test_text = "这是一个测试文本，用于验证缓存功能"
    test_vector = np.random.random(128).astype('float32')
    
    # 首次获取应该返回None
    result = cache.get(test_text)
    print(f"首次获取结果: {result}")
    
    # 添加到缓存
    cache.put(test_text, test_vector)
    print("向量已添加到缓存")
    
    # 再次获取应该返回向量
    result = cache.get(test_text)
    print(f"再次获取结果: {result is not None}")
    if result is not None:
        print(f"向量形状: {result.shape}")
        print(f"向量前5个元素: {result[:5]}")
        print(f"原始向量前5个元素: {test_vector[:5]}")
        print(f"向量匹配: {np.array_equal(result, test_vector)}")
    
    # 获取缓存统计
    stats = cache.get_stats()
    print("\n缓存统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n测试完成")
