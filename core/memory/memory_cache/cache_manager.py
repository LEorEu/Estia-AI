#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能缓存管理器
实现memory_cache表的智能缓存策略和访问优化
"""

import time
import math
import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """缓存条目数据类"""
    cache_id: str
    memory_id: str
    cache_level: str  # 'hot', 'warm'
    priority: float
    access_count: int
    last_accessed: float
    
class CacheManager:
    """智能缓存管理器"""
    
    # 缓存配置
    HOT_CACHE_THRESHOLD = 8.0      # 热缓存优先级阈值
    WARM_CACHE_THRESHOLD = 4.0     # 温缓存优先级阈值  
    MAX_HOT_CACHE_SIZE = 50        # 最大热缓存数量
    MAX_WARM_CACHE_SIZE = 200      # 最大温缓存数量
    TIME_DECAY_DAYS = 60           # 时间衰减周期(天)
    
    def __init__(self, db_manager=None):
        """
        初始化缓存管理器
        
        参数:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager
        self.logger = logger
        
        # 内存缓存映射
        self._memory_cache_map = {}  # memory_id -> CacheEntry
        self._cache_initialized = False
        
    def initialize_cache(self):
        """初始化缓存系统"""
        try:
            if not self.db_manager:
                self.logger.warning("数据库管理器未初始化")
                return False
            
            # 加载现有缓存数据
            self._load_existing_cache()
            
            # 分析现有记忆，建立初始缓存
            self._build_initial_cache()
            
            self._cache_initialized = True
            self.logger.info("智能缓存系统初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"缓存系统初始化失败: {e}")
            return False
    
    def _load_existing_cache(self):
        """加载现有缓存记录"""
        try:
            cache_records = self.db_manager.query("""
                SELECT id, memory_id, cache_level, priority, access_count, last_accessed
                FROM memory_cache
                ORDER BY priority DESC
            """)
            
            for record in cache_records:
                cache_entry = CacheEntry(
                    cache_id=record[0],
                    memory_id=record[1],
                    cache_level=record[2],
                    priority=record[3],
                    access_count=record[4],
                    last_accessed=record[5]
                )
                self._memory_cache_map[record[1]] = cache_entry
            
            self.logger.info(f"加载了 {len(cache_records)} 条现有缓存记录")
            
        except Exception as e:
            self.logger.error(f"加载现有缓存失败: {e}")
    
    def _build_initial_cache(self):
        """为现有记忆建立初始缓存"""
        try:
            # 获取所有记忆的基础信息
            memories = self.db_manager.query("""
                SELECT id, weight, last_accessed, timestamp
                FROM memories
                ORDER BY weight DESC, last_accessed DESC
                LIMIT 300
            """)
            
            if not memories:
                self.logger.info("没有记忆需要建立缓存")
                return
            
            created_count = 0
            for memory in memories:
                memory_id, weight, last_accessed, timestamp = memory
                
                # 如果已经在缓存中，跳过
                if memory_id in self._memory_cache_map:
                    continue
                
                # 计算初始优先级
                priority = self._calculate_priority(
                    weight=weight,
                    access_count=1,  # 初始访问计数
                    last_accessed=last_accessed or timestamp
                )
                
                # 确定缓存级别
                cache_level = self._determine_cache_level(priority)
                
                # 只缓存达到阈值的记忆
                if priority >= self.WARM_CACHE_THRESHOLD:
                    self._create_cache_entry(memory_id, cache_level, priority, 1, last_accessed or timestamp)
                    created_count += 1
            
            self.logger.info(f"为 {created_count} 条记忆建立了初始缓存")
            
        except Exception as e:
            self.logger.error(f"建立初始缓存失败: {e}")
    
    def record_memory_access(self, memory_id: str, access_weight: float = 1.0) -> bool:
        """
        记录记忆访问，更新缓存策略
        
        参数:
            memory_id: 记忆ID
            access_weight: 访问权重因子
            
        返回:
            是否成功记录
        """
        try:
            current_time = time.time()
            
            # 获取记忆基本信息
            memory_info = self.db_manager.query(
                "SELECT weight FROM memories WHERE id = ?", 
                (memory_id,)
            )
            
            if not memory_info:
                self.logger.warning(f"记忆不存在: {memory_id}")
                return False
            
            memory_weight = memory_info[0][0]
            
            # 检查是否已在缓存中
            if memory_id in self._memory_cache_map:
                # 更新现有缓存
                self._update_existing_cache(memory_id, access_weight, current_time)
            else:
                # 创建新缓存条目
                self._create_new_cache(memory_id, memory_weight, access_weight, current_time)
            
            # 定期清理缓存
            if len(self._memory_cache_map) % 50 == 0:
                self._cleanup_cache()
            
            return True
            
        except Exception as e:
            self.logger.error(f"记录访问失败: {e}")
            return False
    
    def _update_existing_cache(self, memory_id: str, access_weight: float, current_time: float):
        """更新现有缓存条目"""
        cache_entry = self._memory_cache_map[memory_id]
        
        # 更新访问计数和时间
        cache_entry.access_count += 1
        cache_entry.last_accessed = current_time
        
        # 获取记忆权重
        memory_info = self.db_manager.query("SELECT weight FROM memories WHERE id = ?", (memory_id,))
        memory_weight = memory_info[0][0] if memory_info else 5.0
        
        # 重新计算优先级
        cache_entry.priority = self._calculate_priority(
            weight=memory_weight,
            access_count=cache_entry.access_count,
            last_accessed=current_time,
            access_weight=access_weight
        )
        
        # 更新缓存级别
        new_cache_level = self._determine_cache_level(cache_entry.priority)
        if new_cache_level != cache_entry.cache_level:
            cache_entry.cache_level = new_cache_level
            self.logger.debug(f"记忆 {memory_id} 缓存级别更新为: {new_cache_level}")
        
        # 更新数据库
        self.db_manager.execute_query("""
            UPDATE memory_cache 
            SET cache_level = ?, priority = ?, access_count = ?, last_accessed = ?
            WHERE memory_id = ?
        """, (cache_entry.cache_level, cache_entry.priority, cache_entry.access_count, 
              cache_entry.last_accessed, memory_id))
    
    def _create_new_cache(self, memory_id: str, memory_weight: float, access_weight: float, current_time: float):
        """创建新缓存条目"""
        # 计算优先级
        priority = self._calculate_priority(
            weight=memory_weight,
            access_count=1,
            last_accessed=current_time,
            access_weight=access_weight
        )
        
        # 确定缓存级别
        cache_level = self._determine_cache_level(priority)
        
        # 只缓存达到阈值的记忆
        if priority >= self.WARM_CACHE_THRESHOLD:
            self._create_cache_entry(memory_id, cache_level, priority, 1, current_time)
            self.logger.debug(f"为记忆 {memory_id} 创建 {cache_level} 缓存，优先级: {priority:.2f}")
    
    def _create_cache_entry(self, memory_id: str, cache_level: str, priority: float, 
                           access_count: int, last_accessed: float):
        """创建缓存条目"""
        cache_id = str(uuid.uuid4())
        
        # 插入数据库
        self.db_manager.execute_query("""
            INSERT INTO memory_cache (id, memory_id, cache_level, priority, access_count, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cache_id, memory_id, cache_level, priority, access_count, last_accessed))
        
        # 更新内存映射
        cache_entry = CacheEntry(
            cache_id=cache_id,
            memory_id=memory_id,
            cache_level=cache_level,
            priority=priority,
            access_count=access_count,
            last_accessed=last_accessed
        )
        self._memory_cache_map[memory_id] = cache_entry
        
        # 提交事务
        if self.db_manager.conn:
            self.db_manager.conn.commit()
    
    def _calculate_priority(self, weight: float, access_count: int, last_accessed: float, 
                          access_weight: float = 1.0) -> float:
        """
        计算缓存优先级
        
        优化算法：priority = weight * (1 + log(access_count)) * time_factor * access_weight
        """
        try:
            # 权重因子 - 直接使用权重值
            weight_factor = weight
            
            # 访问频率因子
            frequency_factor = 1 + math.log(max(access_count, 1))
            
            # 时间因子 - 减少衰减影响
            current_time = time.time()
            days_elapsed = (current_time - last_accessed) / (24 * 3600)
            
            # 更宽松的时间衰减：7天内权重1.0，30天内0.8，之后逐渐衰减
            if days_elapsed <= 7:
                time_factor = 1.0
            elif days_elapsed <= 30:
                time_factor = 0.8
            else:
                time_factor = max(0.3, math.exp(-(days_elapsed - 30) / self.TIME_DECAY_DAYS))
            
            # 综合优先级
            priority = weight_factor * frequency_factor * time_factor * access_weight
            
            return min(priority, 20.0)  # 提高最高优先级限制
            
        except Exception as e:
            self.logger.error(f"优先级计算失败: {e}")
            return weight  # 降级为原始权重
    
    def _determine_cache_level(self, priority: float) -> str:
        """确定缓存级别"""
        if priority >= self.HOT_CACHE_THRESHOLD:
            return 'hot'
        elif priority >= self.WARM_CACHE_THRESHOLD:
            return 'warm'
        else:
            return 'none'  # 不缓存
    
    def get_cached_memories(self, cache_level: str = None, limit: int = 50) -> List[str]:
        """
        获取缓存的记忆ID列表
        
        参数:
            cache_level: 缓存级别过滤('hot', 'warm', None为全部)
            limit: 返回数量限制
            
        返回:
            记忆ID列表
        """
        try:
            cached_entries = list(self._memory_cache_map.values())
            
            # 过滤缓存级别
            if cache_level:
                cached_entries = [entry for entry in cached_entries if entry.cache_level == cache_level]
            
            # 按优先级排序
            cached_entries.sort(key=lambda x: x.priority, reverse=True)
            
            # 返回记忆ID
            return [entry.memory_id for entry in cached_entries[:limit]]
            
        except Exception as e:
            self.logger.error(f"获取缓存记忆失败: {e}")
            return []
    
    def _cleanup_cache(self):
        """清理低优先级缓存"""
        try:
            hot_entries = [entry for entry in self._memory_cache_map.values() if entry.cache_level == 'hot']
            warm_entries = [entry for entry in self._memory_cache_map.values() if entry.cache_level == 'warm']
            
            # 清理过多的热缓存
            if len(hot_entries) > self.MAX_HOT_CACHE_SIZE:
                hot_entries.sort(key=lambda x: x.priority, reverse=True)
                for entry in hot_entries[self.MAX_HOT_CACHE_SIZE:]:
                    self._remove_cache_entry(entry.memory_id)
            
            # 清理过多的温缓存
            if len(warm_entries) > self.MAX_WARM_CACHE_SIZE:
                warm_entries.sort(key=lambda x: x.priority, reverse=True)
                for entry in warm_entries[self.MAX_WARM_CACHE_SIZE:]:
                    self._remove_cache_entry(entry.memory_id)
            
            self.logger.debug("缓存清理完成")
            
        except Exception as e:
            self.logger.error(f"缓存清理失败: {e}")
    
    def _remove_cache_entry(self, memory_id: str):
        """移除缓存条目"""
        try:
            if memory_id in self._memory_cache_map:
                cache_entry = self._memory_cache_map[memory_id]
                
                # 从数据库删除
                self.db_manager.execute_query(
                    "DELETE FROM memory_cache WHERE memory_id = ?",
                    (memory_id,)
                )
                
                # 从内存移除
                del self._memory_cache_map[memory_id]
                
                self.logger.debug(f"移除缓存条目: {memory_id}")
            
        except Exception as e:
            self.logger.error(f"移除缓存条目失败: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            hot_count = len([e for e in self._memory_cache_map.values() if e.cache_level == 'hot'])
            warm_count = len([e for e in self._memory_cache_map.values() if e.cache_level == 'warm'])
            total_count = len(self._memory_cache_map)
            
            avg_priority = sum(e.priority for e in self._memory_cache_map.values()) / total_count if total_count > 0 else 0
            
            return {
                "total_cached": total_count,
                "hot_cache": hot_count,
                "warm_cache": warm_count,
                "average_priority": round(avg_priority, 2),
                "cache_initialized": self._cache_initialized
            }
            
        except Exception as e:
            self.logger.error(f"获取缓存统计失败: {e}")
            return {"error": str(e)} 