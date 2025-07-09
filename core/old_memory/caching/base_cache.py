"""
基础缓存实现

提供基础的缓存功能实现，作为具体缓存类的基类
"""

import time
import logging
from typing import Dict, List, Any, Optional, TypeVar, Generic, Set
from threading import RLock

from .cache_interface import (
    CacheInterface, 
    CacheEvent, 
    CacheEventType, 
    CacheLevel
)

# 尝试导入日志工具
try:
    from core.utils.logger import get_logger
    logger = get_logger("estia.memory.caching.base")
except ImportError:
    # 如果还没有日志工具，使用标准日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("estia.memory.caching.base")

# 定义类型变量
K = TypeVar('K')  # 键类型
V = TypeVar('V')  # 值类型
M = TypeVar('M')  # 元数据类型


class BaseCache(CacheInterface[K, V, M], Generic[K, V, M]):
    """
    基础缓存实现
    
    提供通用的缓存功能和事件处理，作为其他具体缓存类的基类
    """
    
    def __init__(self, cache_id: str, cache_level: CacheLevel = CacheLevel.EXTERNAL,
                max_size: int = 1000, ttl: Optional[int] = None):
        """
        初始化基础缓存
        
        参数:
            cache_id: 缓存唯一标识
            cache_level: 缓存级别
            max_size: 最大容量
            ttl: 条目生存时间(秒)，None表示永不过期
        """
        super().__init__(cache_id)
        
        # 基本配置
        self._cache_level = cache_level
        self._max_size = max_size
        self._ttl = ttl
        
        # 缓存存储
        self._cache: Dict[K, V] = {}
        self._metadata: Dict[K, M] = {}
        self._access_times: Dict[K, float] = {}
        self._creation_times: Dict[K, float] = {}
        self._access_counts: Dict[K, int] = {}
        
        # 线程安全锁
        self._lock = RLock()
        
        # 统计信息
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "operations": {
                "get": 0,
                "put": 0,
                "delete": 0
            },
            "creation_time": time.time()
        }
        
        logger.debug(f"基础缓存初始化 - ID:{cache_id}, 级别:{cache_level.value}, 容量:{max_size}")
    
    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """获取缓存项"""
        with self._lock:
            self._stats["operations"]["get"] += 1
            
            # 检查键是否存在
            if key not in self._cache:
                self._stats["misses"] += 1
                
                # 通知缓存未命中事件
                self.notify_listeners(CacheEvent(
                    event_type=CacheEventType.GET,
                    cache_id=self.cache_id,
                    key=key,
                    metadata={"hit": False}
                ))
                
                return default
            
            # 检查是否过期
            if self._ttl is not None:
                creation_time = self._creation_times.get(key, 0)
                if time.time() - creation_time > self._ttl:
                    # 已过期，删除并返回默认值
                    self.delete(key)
                    return default
            
            # 更新访问计数和时间
            self._update_access_stats(key)
            
            # 获取缓存值
            value = self._cache[key]
            self._stats["hits"] += 1
            
            # 通知缓存命中事件
            self.notify_listeners(CacheEvent(
                event_type=CacheEventType.GET,
                cache_id=self.cache_id,
                key=key,
                value=value,
                metadata={"hit": True}
            ))
            
            return value
    
    def put(self, key: K, value: V, metadata: Optional[M] = None) -> None:
        """添加或更新缓存项"""
        with self._lock:
            self._stats["operations"]["put"] += 1
            
            current_time = time.time()
            is_update = key in self._cache
            
            # 检查是否需要淘汰
            if not is_update and len(self._cache) >= self._max_size:
                self._evict_item()
            
            # 存储值和元数据
            self._cache[key] = value
            
            if metadata is not None:
                self._metadata[key] = metadata
            elif key not in self._metadata:
                self._metadata[key] = {} if isinstance({}, M) else None  # type: ignore
            
            # 更新时间信息
            if not is_update:
                self._creation_times[key] = current_time
                self._access_counts[key] = 0
                
            self._access_times[key] = current_time
            self._access_counts[key] += 1
            
            # 通知添加事件
            self.notify_listeners(CacheEvent(
                event_type=CacheEventType.PUT,
                cache_id=self.cache_id,
                key=key,
                value=value,
                metadata={
                    "is_update": is_update,
                    "user_metadata": metadata
                }
            ))
    
    def delete(self, key: K) -> bool:
        """删除缓存项"""
        with self._lock:
            self._stats["operations"]["delete"] += 1
            
            if key not in self._cache:
                return False
            
            # 保留待删除的值用于事件通知
            value = self._cache[key]
            metadata = self._metadata.get(key, None)
            
            # 删除所有相关数据
            del self._cache[key]
            
            if key in self._metadata:
                del self._metadata[key]
                
            if key in self._access_times:
                del self._access_times[key]
                
            if key in self._creation_times:
                del self._creation_times[key]
                
            if key in self._access_counts:
                del self._access_counts[key]
            
            # 通知删除事件
            self.notify_listeners(CacheEvent(
                event_type=CacheEventType.DELETE,
                cache_id=self.cache_id,
                key=key,
                value=value,
                metadata={"user_metadata": metadata}
            ))
            
            return True
    
    def contains(self, key: K) -> bool:
        """检查键是否存在"""
        with self._lock:
            if key not in self._cache:
                return False
                
            # 检查是否过期
            if self._ttl is not None:
                creation_time = self._creation_times.get(key, 0)
                if time.time() - creation_time > self._ttl:
                    return False
                    
            return True
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            # 通知清空事件
            self.notify_listeners(CacheEvent(
                event_type=CacheEventType.CLEAR,
                cache_id=self.cache_id,
                metadata={"size_before_clear": len(self._cache)}
            ))
            
            self._cache.clear()
            self._metadata.clear()
            self._access_times.clear()
            self._creation_times.clear()
            self._access_counts.clear()
    
    def get_size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            # 计算命中率
            total_gets = self._stats["hits"] + self._stats["misses"]
            hit_ratio = self._stats["hits"] / total_gets if total_gets > 0 else 0
            
            return {
                "size": len(self._cache),
                "capacity": self._max_size,
                "usage": len(self._cache) / self._max_size if self._max_size > 0 else 0,
                "ttl": self._ttl,
                "level": self._cache_level.value,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_ratio": hit_ratio,
                "evictions": self._stats["evictions"],
                "operations": self._stats["operations"].copy(),
                "uptime": time.time() - self._stats["creation_time"]
            }
    
    def get_metadata(self, key: K) -> Optional[M]:
        """获取缓存项元数据"""
        with self._lock:
            if key not in self._cache or key not in self._metadata:
                return None
                
            # 检查是否过期
            if self._ttl is not None:
                creation_time = self._creation_times.get(key, 0)
                if time.time() - creation_time > self._ttl:
                    return None
                    
            return self._metadata[key]
    
    def update_metadata(self, key: K, metadata: M) -> bool:
        """更新缓存项元数据"""
        with self._lock:
            if key not in self._cache:
                return False
                
            # 检查是否过期
            if self._ttl is not None:
                creation_time = self._creation_times.get(key, 0)
                if time.time() - creation_time > self._ttl:
                    return False
                    
            # 更新元数据
            self._metadata[key] = metadata
            
            # 通知元数据更新事件
            self.notify_listeners(CacheEvent(
                event_type=CacheEventType.PUT,
                cache_id=self.cache_id,
                key=key,
                metadata={"metadata_update": True, "user_metadata": metadata}
            ))
            
            return True
    
    def get_all_keys(self) -> List[K]:
        """获取所有缓存键"""
        with self._lock:
            current_time = time.time()
            
            # 如果设置了TTL，排除过期的键
            if self._ttl is not None:
                return [
                    key for key in self._cache.keys() 
                    if current_time - self._creation_times.get(key, 0) <= self._ttl
                ]
            else:
                return list(self._cache.keys())
    
    def get_cache_level(self) -> CacheLevel:
        """获取缓存级别"""
        return self._cache_level
    
    def _update_access_stats(self, key: K) -> None:
        """更新访问统计"""
        self._access_times[key] = time.time()
        self._access_counts[key] = self._access_counts.get(key, 0) + 1
    
    def _evict_item(self) -> bool:
        """淘汰缓存项"""
        # 默认使用LRU策略：淘汰最长时间未访问的项
        if not self._access_times:
            return False
            
        # 找出最长时间未访问的键
        oldest_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        
        # 删除该项
        result = self.delete(oldest_key)
        if result:
            self._stats["evictions"] += 1
            
            # 通知驱逐事件
            self.notify_listeners(CacheEvent(
                event_type=CacheEventType.EVICT,
                cache_id=self.cache_id,
                key=oldest_key,
                metadata={"strategy": "lru"}
            ))
            
        return result
    
    def __len__(self) -> int:
        """支持len()操作"""
        return self.get_size()
    
    def __contains__(self, key: K) -> bool:
        """支持in操作符"""
        return self.contains(key) 