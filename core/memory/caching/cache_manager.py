#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一缓存管理器模块

提供统一的缓存管理、监控与协调功能，
作为所有缓存系统的中央管控点
"""

import time
import logging
import threading
from typing import Dict, List, Any, Optional, Set, TypeVar, Generic, Type, Union, Tuple
from pathlib import Path

from .cache_interface import (
    CacheInterface, CacheEvent, CacheEventType, CacheListener, CacheLevel
)

# 尝试导入日志工具
try:
    from core.utils.logger import get_logger
    logger = get_logger("estia.memory.caching.manager")
except ImportError:
    # 如果还没有日志工具，使用标准日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("estia.memory.caching.manager")

# 定义类型变量
K = TypeVar('K')  # 键类型
V = TypeVar('V')  # 值类型
M = TypeVar('M')  # 元数据类型


class CacheManagerStats:
    """缓存管理器统计信息类"""
    
    def __init__(self):
        """初始化统计信息"""
        # 计数器
        self.total_hits = 0
        self.total_misses = 0
        self.cache_hits: Dict[str, int] = {}  # 按缓存ID统计
        self.level_hits: Dict[str, int] = {}  # 按缓存级别统计
        self.operations: Dict[str, int] = {}  # 按操作类型统计
        
        # 性能统计
        self.access_times: List[float] = []
        self.last_maintenance = time.time()
        
    def record_hit(self, cache_id: str, cache_level: str, duration: float):
        """记录缓存命中"""
        self.total_hits += 1
        
        if cache_id in self.cache_hits:
            self.cache_hits[cache_id] += 1
        else:
            self.cache_hits[cache_id] = 1
            
        if cache_level in self.level_hits:
            self.level_hits[cache_level] += 1
        else:
            self.level_hits[cache_level] = 1
            
        self.access_times.append(duration)
        
    def record_miss(self):
        """记录缓存未命中"""
        self.total_misses += 1
        
    def record_operation(self, operation: str):
        """记录操作"""
        if operation in self.operations:
            self.operations[operation] += 1
        else:
            self.operations[operation] = 1
    
    def get_hit_ratio(self) -> float:
        """获取命中率"""
        total = self.total_hits + self.total_misses
        return self.total_hits / total if total > 0 else 0
        
    def get_average_access_time(self) -> float:
        """获取平均访问时间(毫秒)"""
        if not self.access_times:
            return 0
        return sum(self.access_times) / len(self.access_times) * 1000
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        return {
            "hit_ratio": self.get_hit_ratio(),
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "average_access_time_ms": self.get_average_access_time(),
            "cache_hits": self.cache_hits.copy(),
            "level_hits": self.level_hits.copy(),
            "operations": self.operations.copy()
        }
        
    def reset(self):
        """重置统计数据"""
        self.__init__()


class UnifiedCacheManager(CacheListener, Generic[K, V, M]):
    """
    统一缓存管理器
    
    负责协调多个缓存系统，提供透明的缓存访问接口，
    并处理缓存间的同步、事件传递和策略执行
    """
    
    # 单例模式支持
    _instance = None
    _lock = threading.RLock()
    
    @classmethod
    def get_instance(cls, *args, **kwargs):
        """获取单例实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(*args, **kwargs)
        return cls._instance
    
    def __init__(self):
        """初始化缓存管理器"""
        # 缓存注册表
        self.caches: Dict[str, CacheInterface] = {}
        self.level_caches: Dict[CacheLevel, List[CacheInterface]] = {
            level: [] for level in CacheLevel
        }
        
        # 统计与监控
        self.stats = CacheManagerStats()
        
        # 缓存键映射 (用于快速定位缓存项所在的缓存)
        self.key_cache_map: Dict[K, Set[str]] = {}
        
        # 缓存策略配置
        self.config = {
            "maintenance_interval": 300,  # 维护间隔(秒)
            "propagation_enabled": True,  # 是否启用跨缓存传播
            "auto_promote": True,         # 是否自动提升频繁使用的项
            "sync_on_write": True,        # 写操作是否同步到其他缓存
            "sync_on_delete": True        # 删除操作是否同步到其他缓存
        }
        
        # 初始化维护定时器
        self._schedule_maintenance()
        
        logger.info("统一缓存管理器初始化完成")
    
    def register_cache(self, cache: CacheInterface) -> None:
        """
        注册缓存系统
        
        参数:
            cache: 实现CacheInterface的缓存系统
        """
        cache_id = cache.cache_id
        
        if cache_id in self.caches:
            logger.warning(f"缓存系统 {cache_id} 已注册，将被替换")
            
        # 注册缓存
        self.caches[cache_id] = cache
        
        # 按缓存级别归类
        cache_level = cache.get_cache_level()
        self.level_caches[cache_level].append(cache)
        
        # 添加事件监听
        cache.add_listener(self)
        
        # 通知缓存初始化事件
        cache.notify_listeners(CacheEvent(
            event_type=CacheEventType.INIT,
            cache_id=cache_id,
            metadata={"manager_id": id(self)}
        ))
        
        logger.info(f"注册缓存系统: {cache_id}, 级别: {cache_level.value}")
    
    def unregister_cache(self, cache_id: str) -> bool:
        """
        注销缓存系统
        
        参数:
            cache_id: 缓存系统ID
            
        返回:
            是否成功注销
        """
        if cache_id not in self.caches:
            logger.warning(f"缓存系统 {cache_id} 未注册")
            return False
            
        cache = self.caches[cache_id]
        
        # 从级别列表中移除
        cache_level = cache.get_cache_level()
        if cache in self.level_caches[cache_level]:
            self.level_caches[cache_level].remove(cache)
        
        # 移除监听器
        cache.remove_listener(self)
        
        # 从注册表删除
        del self.caches[cache_id]
        
        # 更新键映射
        self._update_key_cache_map()
        
        logger.info(f"注销缓存系统: {cache_id}")
        return True
    
    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """
        从缓存获取值，按优先级顺序查找
        
        参数:
            key: 缓存键
            default: 默认返回值
            
        返回:
            缓存值或默认值
        """
        start_time = time.time()
        
        # 1. 如果键映射中有记录，优先查找已知缓存
        if key in self.key_cache_map:
            for cache_id in self.key_cache_map[key]:
                if cache_id in self.caches:
                    cache = self.caches[cache_id]
                    value = cache.get(key, None)
                    if value is not None:
                        duration = time.time() - start_time
                        self.stats.record_hit(cache_id, cache.get_cache_level().value, duration)
                        self.stats.record_operation("get")
                        return value
        
        # 2. 按缓存级别顺序查找
        for level in [CacheLevel.HOT, CacheLevel.WARM, CacheLevel.COLD, CacheLevel.PERSISTENT]:
            for cache in self.level_caches[level]:
                value = cache.get(key, None)
                if value is not None:
                    # 更新键映射
                    if key not in self.key_cache_map:
                        self.key_cache_map[key] = set()
                    self.key_cache_map[key].add(cache.cache_id)
                    
                    duration = time.time() - start_time
                    self.stats.record_hit(cache.cache_id, level.value, duration)
                    self.stats.record_operation("get")
                    
                    # 考虑是否需要将该项提升到更高级别缓存
                    if self.config["auto_promote"]:
                        self._consider_promotion(key, value, cache)
                        
                    return value
        
        # 未找到
        self.stats.record_miss()
        self.stats.record_operation("get_miss")
        return default
    
    def put(self, key: K, value: V, metadata: Optional[M] = None,
            target_levels: Optional[List[CacheLevel]] = None) -> None:
        """
        添加项到缓存，可指定目标缓存级别
        
        参数:
            key: 缓存键
            value: 缓存值
            metadata: 缓存元数据
            target_levels: 目标缓存级别列表，默认为[HOT]
        """
        # 默认放入HOT级别缓存
        if target_levels is None:
            target_levels = [CacheLevel.HOT]
            
        self.stats.record_operation("put")
        
        # 添加到指定级别的所有缓存
        for level in target_levels:
            for cache in self.level_caches[level]:
                cache.put(key, value, metadata)
                
                # 更新键映射
                if key not in self.key_cache_map:
                    self.key_cache_map[key] = set()
                self.key_cache_map[key].add(cache.cache_id)
                
        # 同步到其他缓存
        if self.config["sync_on_write"]:
            self._propagate_write(key, value, metadata, exclude_levels=target_levels)
    
    def delete(self, key: K) -> bool:
        """
        从所有缓存中删除项
        
        参数:
            key: 缓存键
            
        返回:
            是否成功删除(任一缓存删除成功即返回True)
        """
        self.stats.record_operation("delete")
        
        success = False
        
        # 如果键映射中有记录
        if key in self.key_cache_map:
            cache_ids = list(self.key_cache_map[key])
            for cache_id in cache_ids:
                if cache_id in self.caches:
                    if self.caches[cache_id].delete(key):
                        success = True
                        
            # 清除键映射
            del self.key_cache_map[key]
            
        # 从所有缓存中删除(以防万一)
        if self.config["sync_on_delete"]:
            for cache in self.caches.values():
                if cache.delete(key):
                    success = True
        
        return success
    
    def clear_all(self) -> None:
        """清空所有缓存"""
        self.stats.record_operation("clear_all")
        
        for cache in self.caches.values():
            cache.clear()
            
        # 清空键映射
        self.key_cache_map.clear()
        
        logger.info("已清空所有缓存")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取综合统计信息
        
        返回:
            统计信息字典
        """
        stats = {
            "manager": self.stats.get_stats_summary(),
            "caches": {}
        }
        
        # 收集各缓存的统计信息
        for cache_id, cache in self.caches.items():
            stats["caches"][cache_id] = cache.get_stats()
            
        return stats
    
    def on_event(self, event: CacheEvent) -> None:
        """
        处理缓存事件(实现CacheListener接口)
        
        参数:
            event: 缓存事件
        """
        # 记录事件
        self.stats.record_operation(f"event_{event.event_type.value}")
        
        # 处理特定事件
        if event.event_type == CacheEventType.PUT:
            # 更新键映射
            if event.key not in self.key_cache_map:
                self.key_cache_map[event.key] = set()
            self.key_cache_map[event.key].add(event.cache_id)
            
        elif event.event_type == CacheEventType.DELETE:
            # 更新键映射
            if event.key in self.key_cache_map and event.cache_id in self.key_cache_map[event.key]:
                self.key_cache_map[event.key].remove(event.cache_id)
                if not self.key_cache_map[event.key]:
                    del self.key_cache_map[event.key]
    
    def _update_key_cache_map(self) -> None:
        """更新键-缓存映射"""
        # 清空现有映射
        self.key_cache_map.clear()
        
        # 重建映射
        for cache_id, cache in self.caches.items():
            for key in cache.get_all_keys():
                if key not in self.key_cache_map:
                    self.key_cache_map[key] = set()
                self.key_cache_map[key].add(cache_id)
    
    def _consider_promotion(self, key: K, value: V, source_cache: CacheInterface) -> None:
        """
        考虑是否将缓存项提升到更高级别
        
        参数:
            key: 缓存键
            value: 缓存值
            source_cache: 源缓存
        """
        source_level = source_cache.get_cache_level()
        
        # 如果已经是最高级别，无需提升
        if source_level == CacheLevel.HOT:
            return
            
        # 获取元数据(如果有)
        metadata = source_cache.get_metadata(key)
        
        # 简单提升规则: 直接提升到HOT缓存
        target_level = CacheLevel.HOT
        
        # 执行提升
        for cache in self.level_caches[target_level]:
            if cache.cache_id != source_cache.cache_id:  # 避免提升到自己
                cache.put(key, value, metadata)
                
                # 更新键映射
                if key not in self.key_cache_map:
                    self.key_cache_map[key] = set()
                self.key_cache_map[key].add(cache.cache_id)
                
                logger.debug(f"提升缓存项 {key} 从 {source_level.value} 到 {target_level.value}")
    
    def _propagate_write(self, key: K, value: V, metadata: Optional[M],
                        exclude_levels: Optional[List[CacheLevel]] = None) -> None:
        """
        传播写操作到其他缓存
        
        参数:
            key: 缓存键
            value: 缓存值
            metadata: 元数据
            exclude_levels: 排除的缓存级别
        """
        exclude_levels = exclude_levels or []
        
        # 传播到持久化缓存
        if CacheLevel.PERSISTENT not in exclude_levels:
            for cache in self.level_caches[CacheLevel.PERSISTENT]:
                cache.put(key, value, metadata)
                
                # 更新键映射
                if key not in self.key_cache_map:
                    self.key_cache_map[key] = set()
                self.key_cache_map[key].add(cache.cache_id)
    
    def _schedule_maintenance(self) -> None:
        """调度定期维护"""
        interval = self.config["maintenance_interval"]
        
        # 执行维护
        self._perform_maintenance()
        
        # 计划下次维护
        threading.Timer(interval, self._schedule_maintenance).start()
    
    def _perform_maintenance(self) -> None:
        """执行缓存维护"""
        logger.debug("执行缓存维护...")
        
        # 记录维护操作
        self.stats.record_operation("maintenance")
        self.stats.last_maintenance = time.time()
        
        # 执行键映射清理
        self._clean_key_cache_map()
        
        # 通知所有缓存执行维护
        for cache in self.caches.values():
            try:
                # 发送维护事件
                cache.notify_listeners(CacheEvent(
                    event_type=CacheEventType.MAINTENANCE,
                    cache_id=cache.cache_id
                ))
            except Exception as e:
                logger.error(f"缓存 {cache.cache_id} 维护失败: {e}")
    
    def _clean_key_cache_map(self) -> None:
        """清理键映射中的无效引用"""
        to_remove = []
        
        for key, cache_ids in self.key_cache_map.items():
            valid_ids = set()
            for cache_id in cache_ids:
                if cache_id in self.caches and self.caches[cache_id].contains(key):
                    valid_ids.add(cache_id)
            
            if valid_ids:
                self.key_cache_map[key] = valid_ids
            else:
                to_remove.append(key)
        
        # 删除无效键
        for key in to_remove:
            del self.key_cache_map[key] 