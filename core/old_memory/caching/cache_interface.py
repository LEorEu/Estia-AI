"""
统一缓存接口定义模块

为系统中的各种缓存系统提供统一的API和事件系统，
解决多缓存系统间的冲突与协调问题。
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
import time

# 定义泛型类型变量
K = TypeVar('K')  # 键类型
V = TypeVar('V')  # 值类型
M = TypeVar('M')  # 元数据类型


class CacheEventType(Enum):
    """缓存事件类型枚举"""
    GET = "get"                  # 获取项
    PUT = "put"                  # 放入项
    DELETE = "delete"            # 删除项
    CLEAR = "clear"              # 清空缓存
    PROMOTE = "promote"          # 提升项到更高级别缓存
    DEMOTE = "demote"            # 降级项到低级别缓存
    EVICT = "evict"              # 驱逐项
    MAINTENANCE = "maintenance"  # 维护操作
    ERROR = "error"              # 错误事件
    INIT = "init"                # 初始化事件


class CacheEvent:
    """缓存事件数据类"""
    
    def __init__(self, 
                 event_type: CacheEventType,
                 cache_id: str,
                 key: Optional[Any] = None,
                 value: Optional[Any] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 timestamp: Optional[float] = None):
        """
        初始化缓存事件
        
        参数:
            event_type: 事件类型
            cache_id: 缓存ID，标识事件源
            key: 相关的缓存键
            value: 相关的缓存值
            metadata: 事件相关的元数据
            timestamp: 事件时间戳，默认为当前时间
        """
        self.event_type = event_type
        self.cache_id = cache_id
        self.key = key
        self.value = value
        self.metadata = metadata or {}
        self.timestamp = timestamp or time.time()
        
    def __repr__(self) -> str:
        """字符串表示"""
        return f"CacheEvent({self.event_type.value}, cache={self.cache_id}, key={self.key}, ts={self.timestamp})"


class CacheListener(ABC):
    """缓存事件监听器接口"""
    
    @abstractmethod
    def on_event(self, event: CacheEvent) -> None:
        """
        处理缓存事件
        
        参数:
            event: 缓存事件对象
        """
        pass


class CacheLevel(Enum):
    """缓存级别枚举"""
    HOT = "hot"       # 热缓存，最高优先级
    WARM = "warm"     # 温缓存，中等优先级
    COLD = "cold"     # 冷缓存，低优先级
    PERSISTENT = "persistent"  # 持久化缓存
    EXTERNAL = "external"  # 外部缓存


class CacheInterface(Generic[K, V, M], ABC):
    """
    统一缓存接口
    
    定义了缓存系统应实现的基本操作和事件机制
    """
    
    def __init__(self, cache_id: str):
        """
        初始化缓存接口
        
        参数:
            cache_id: 缓存系统唯一标识符
        """
        self.cache_id = cache_id
        self.listeners: List[CacheListener] = []
        
    def add_listener(self, listener: CacheListener) -> None:
        """
        添加事件监听器
        
        参数:
            listener: 事件监听器对象
        """
        if listener not in self.listeners:
            self.listeners.append(listener)
            
    def remove_listener(self, listener: CacheListener) -> None:
        """
        移除事件监听器
        
        参数:
            listener: 要移除的事件监听器
        """
        if listener in self.listeners:
            self.listeners.remove(listener)
            
    def notify_listeners(self, event: CacheEvent) -> None:
        """
        通知所有监听器
        
        参数:
            event: 缓存事件
        """
        for listener in self.listeners:
            try:
                listener.on_event(event)
            except Exception as e:
                # 记录错误但继续通知其他监听器
                print(f"缓存事件监听器错误: {e}")
                
    @abstractmethod
    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """
        获取缓存项
        
        参数:
            key: 缓存键
            default: 未找到时返回的默认值
            
        返回:
            缓存值或默认值
        """
        pass
    
    @abstractmethod
    def put(self, key: K, value: V, metadata: Optional[M] = None) -> None:
        """
        添加或更新缓存项
        
        参数:
            key: 缓存键
            value: 缓存值
            metadata: 与缓存项关联的元数据
        """
        pass
    
    @abstractmethod
    def delete(self, key: K) -> bool:
        """
        删除缓存项
        
        参数:
            key: 缓存键
            
        返回:
            是否成功删除
        """
        pass
    
    @abstractmethod
    def contains(self, key: K) -> bool:
        """
        检查键是否存在于缓存中
        
        参数:
            key: 缓存键
            
        返回:
            键是否存在
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        清空缓存
        """
        pass
    
    @abstractmethod
    def get_size(self) -> int:
        """
        获取当前缓存项数量
        
        返回:
            缓存中的项数
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        返回:
            包含缓存统计数据的字典
        """
        pass
    
    @abstractmethod
    def get_metadata(self, key: K) -> Optional[M]:
        """
        获取缓存项的元数据
        
        参数:
            key: 缓存键
            
        返回:
            缓存项的元数据或None
        """
        pass
    
    @abstractmethod
    def update_metadata(self, key: K, metadata: M) -> bool:
        """
        更新缓存项元数据
        
        参数:
            key: 缓存键
            metadata: 新元数据
            
        返回:
            是否成功更新
        """
        pass
    
    @abstractmethod
    def get_all_keys(self) -> List[K]:
        """
        获取所有缓存键
        
        返回:
            所有缓存键的列表
        """
        pass
    
    def get_cache_level(self) -> CacheLevel:
        """
        获取缓存级别
        
        返回:
            当前缓存级别
        """
        return CacheLevel.EXTERNAL  # 默认实现，子类可覆盖 