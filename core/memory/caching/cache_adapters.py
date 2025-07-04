# -*- coding: utf-8 -*-
"""缓存适配器模块
===================
为旧缓存系统提供 `CacheInterface` 适配，使其能被 `UnifiedCacheManager` 统一管理。
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import time

import numpy as np

from .cache_interface import CacheInterface, CacheEvent, CacheEventType, CacheLevel
from .cache_manager import UnifiedCacheManager

logger = logging.getLogger(__name__)


class EnhancedMemoryCacheAdapter(CacheInterface[str, np.ndarray, Dict[str, Any]]):
    """适配 `EnhancedMemoryCache`。"""

    def __init__(
        self,
        source_cache: Any,
        cache_id: str = "embedding_cache",
        auto_register: bool = True,
    ) -> None:
        super().__init__(cache_id)
        self._cache = source_cache
        if auto_register:
            try:
                UnifiedCacheManager.get_instance().register_cache(self)
            except Exception as exc:
                logger.warning("注册 EnhancedMemoryCacheAdapter 失败: %s", exc)

    # ------------------------------------------------------------------
    # CacheInterface 实现
    # ------------------------------------------------------------------
    def _emit(self, event_type: CacheEventType, key: str, value: Any | None = None) -> None:
        self.notify_listeners(CacheEvent(event_type, self.cache_id, key=key, value=value))

    def get(self, key: str, default: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        value = self._cache.get(key)
        if value is not None:
            self._emit(CacheEventType.GET, key, value)
            return value
        return default

    def put(self, key: str, value: np.ndarray, metadata: Optional[Dict[str, Any]] = None) -> None:
        # 从metadata中提取memory_weight，默认为1.0
        memory_weight = metadata.get("weight", 1.0) if metadata else 1.0
        self._cache.put(key, value, memory_weight)
        self._emit(CacheEventType.PUT, key, value)

    def delete(self, key: str) -> bool:
        """删除缓存项，包括持久化缓存"""
        removed = False
        hashed = self._cache._text_to_key(key)
        
        # 从hot缓存中删除
        if hashed in self._cache.hot_cache:
            del self._cache.hot_cache[hashed]
            removed = True
            
        # 从warm缓存中删除
        if hashed in self._cache.warm_cache:
            del self._cache.warm_cache[hashed]
            removed = True
            
        # 从元数据中删除
        if hashed in self._cache.memory_metadata:
            del self._cache.memory_metadata[hashed]
            
        # 🔥 关键修复：删除持久化缓存文件
        if self._cache.persist:
            try:
                import os
                vector_file = os.path.join(self._cache.cache_dir, f"{hashed}.npy")
                if os.path.exists(vector_file):
                    os.remove(vector_file)
                    removed = True
            except Exception as e:
                # 记录错误但不阻止删除操作
                pass
                
        # 从关键词缓存中清理
        keywords_to_clean = []
        for keyword, cache_keys in self._cache.keyword_cache.items():
            if hashed in cache_keys:
                cache_keys.discard(hashed)
                if not cache_keys:  # 如果关键词没有关联的缓存了
                    keywords_to_clean.append(keyword)
                    
        for keyword in keywords_to_clean:
            del self._cache.keyword_cache[keyword]
            
        if removed:
            self._emit(CacheEventType.DELETE, key)
            
        return removed

    def contains(self, key: str) -> bool:
        hashed = self._cache._text_to_key(key)
        return hashed in self._cache.hot_cache or hashed in self._cache.warm_cache

    def clear(self) -> None:
        self._cache.clear_all_cache()
        self._emit(CacheEventType.CLEAR, "*")

    def get_size(self) -> int:
        return len(self._cache.hot_cache) + len(self._cache.warm_cache)

    def get_stats(self) -> Dict[str, Any]:
        return self._cache.get_stats()

    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        hashed = self._cache._text_to_key(key)
        return self._cache.memory_metadata.get(hashed)

    def update_metadata(self, key: str, metadata: Dict[str, Any]) -> bool:
        hashed = self._cache._text_to_key(key)
        self._cache.memory_metadata[hashed] = metadata
        return True

    def get_all_keys(self) -> List[str]:
        return list(self._cache.memory_metadata.keys())

    def get_cache_level(self) -> CacheLevel:
        return CacheLevel.HOT


class DbCacheAdapter(CacheInterface[str, Dict[str, Any], Dict[str, Any]]):
    """适配基于数据库的 `CacheManager`。"""

    def __init__(
        self,
        db_cache: Any,
        cache_id: str = "db_memory_cache",
        auto_register: bool = True,
    ) -> None:
        super().__init__(cache_id)
        self._db_cache = db_cache
        if auto_register:
            try:
                UnifiedCacheManager.get_instance().register_cache(self)
            except Exception as exc:
                logger.warning("注册 DbCacheAdapter 失败: %s", exc)

    # ------------------------------------------------------------------
    def _entry_to_dict(self, entry: Any) -> Dict[str, Any]:
        return {
            "cache_id": getattr(entry, "cache_id", None),
            "memory_id": getattr(entry, "memory_id", None),
            "cache_level": getattr(entry, "cache_level", None),
            "priority": getattr(entry, "priority", None),
            "access_count": getattr(entry, "access_count", None),
            "last_accessed": getattr(entry, "last_accessed", None),
        }

    def get(self, key: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        entry = self._db_cache._memory_cache_map.get(key)
        if entry is not None:
            value = self._entry_to_dict(entry)
            self.notify_listeners(CacheEvent(CacheEventType.GET, self.cache_id, key, value))
            return value
        return default

    def put(self, key: str, value: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> None:
        weight = metadata.get("access_weight", 1.0) if metadata else 1.0
        self._db_cache.record_memory_access(key, access_weight=weight)
        self.notify_listeners(CacheEvent(CacheEventType.PUT, self.cache_id, key, value, metadata))

    def delete(self, key: str) -> bool:
        existed = key in self._db_cache._memory_cache_map
        if existed:
            self._db_cache._remove_cache_entry(key)
            self.notify_listeners(CacheEvent(CacheEventType.DELETE, self.cache_id, key))
        return existed

    def contains(self, key: str) -> bool:
        return key in self._db_cache._memory_cache_map

    def clear(self) -> None:
        for k in list(self._db_cache._memory_cache_map.keys()):
            self.delete(k)
        self.notify_listeners(CacheEvent(CacheEventType.CLEAR, self.cache_id))

    def get_size(self) -> int:
        return len(self._db_cache._memory_cache_map)

    def get_stats(self) -> Dict[str, Any]:
        try:
            return self._db_cache.get_cache_stats()
        except Exception:
            return {}

    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        return self.get(key)

    def update_metadata(self, key: str, metadata: Dict[str, Any]) -> bool:
        if key not in self._db_cache._memory_cache_map:
            return False
        entry = self._db_cache._memory_cache_map[key]
        for k, v in metadata.items():
            if hasattr(entry, k):
                setattr(entry, k, v)
        return True

    def get_all_keys(self) -> List[str]:
        return list(self._db_cache._memory_cache_map.keys())

    def get_cache_level(self) -> CacheLevel:
        return CacheLevel.WARM
    
    def get_cached_memories(self, cache_level: str = None, limit: int = 50) -> List[str]:
        """
        获取缓存的记忆ID列表
        
        参数:
            cache_level: 缓存级别 ('hot', 'warm')
            limit: 限制数量
            
        返回:
            记忆ID列表
        """
        try:
            return self._db_cache.get_cached_memories(cache_level, limit)
        except Exception as e:
            logger.warning(f"获取缓存记忆失败: {e}")
            return []


class SmartRetrieverCacheAdapter(CacheInterface[str, Dict[str, Any], Dict[str, Any]]):
    """
    SmartRetriever缓存适配器
    
    封装SmartRetriever的内部缓存功能，使其符合统一缓存接口
    """
    
    def __init__(self, smart_retriever):
        """
        初始化SmartRetriever缓存适配器
        
        参数:
            smart_retriever: SmartRetriever实例
        """
        super().__init__("smart_retriever_cache")
        self.smart_retriever = smart_retriever
        self.cache_level = CacheLevel.WARM
        self._internal_cache = {}  # 内部缓存存储
        self._access_stats = {}    # 访问统计
        
    def get(self, key: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """获取检索缓存"""
        if key in self._internal_cache:
            # 更新访问统计
            if key in self._access_stats:
                self._access_stats[key]['access_count'] += 1
                self._access_stats[key]['last_accessed'] = time.time()
            else:
                self._access_stats[key] = {
                    'access_count': 1,
                    'last_accessed': time.time()
                }
            
            # 通知事件
            self.notify_listeners(CacheEvent(
                event_type=CacheEventType.GET,
                cache_id=self.cache_id,
                key=key,
                metadata={'access_count': self._access_stats[key]['access_count']}
            ))
            
            return self._internal_cache[key]
        return default
    
    def put(self, key: str, value: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> None:
        """存储检索缓存"""
        self._internal_cache[key] = value
        
        # 更新访问统计
        if key not in self._access_stats:
            self._access_stats[key] = {
                'access_count': 0,
                'last_accessed': time.time(),
                'created_at': time.time()
            }
        
        # 通知事件
        self.notify_listeners(CacheEvent(
            event_type=CacheEventType.PUT,
            cache_id=self.cache_id,
            key=key,
            value=value,
            metadata=metadata
        ))
    
    def delete(self, key: str) -> bool:
        """删除检索缓存"""
        if key in self._internal_cache:
            del self._internal_cache[key]
            if key in self._access_stats:
                del self._access_stats[key]
            
            # 通知事件
            self.notify_listeners(CacheEvent(
                event_type=CacheEventType.DELETE,
                cache_id=self.cache_id,
                key=key
            ))
            return True
        return False
    
    def contains(self, key: str) -> bool:
        """检查键是否存在"""
        return key in self._internal_cache
    
    def clear(self) -> None:
        """清空检索缓存"""
        self._internal_cache.clear()
        self._access_stats.clear()
        
        # 通知事件
        self.notify_listeners(CacheEvent(
            event_type=CacheEventType.CLEAR,
            cache_id=self.cache_id
        ))
    
    def get_size(self) -> int:
        """获取缓存大小"""
        return len(self._internal_cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_access = sum(stats['access_count'] for stats in self._access_stats.values())
        return {
            "cache_id": self.cache_id,
            "cache_level": self.cache_level.value,
            "size": len(self._internal_cache),
            "total_access": total_access,
            "average_access": total_access / len(self._access_stats) if self._access_stats else 0
        }
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """获取键的元数据"""
        return self._access_stats.get(key)
    
    def update_metadata(self, key: str, metadata: Dict[str, Any]) -> bool:
        """更新键的元数据"""
        if key in self._access_stats:
            self._access_stats[key].update(metadata)
            return True
        return False
    
    def get_all_keys(self) -> List[str]:
        """获取所有键"""
        return list(self._internal_cache.keys())
    
    def get_cache_level(self) -> CacheLevel:
        """获取缓存级别"""
        return self.cache_level


__all__ = [
    "EnhancedMemoryCacheAdapter",
    "DbCacheAdapter",
    "SmartRetrieverCacheAdapter",
] 