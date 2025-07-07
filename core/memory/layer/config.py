#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层记忆系统配置管理

统一管理分层系统的配置参数和默认值
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from .types import MemoryLayer, LayerConfig

logger = logging.getLogger(__name__)


@dataclass
class LayerSystemConfig:
    """分层系统全局配置"""
    
    # 分层配置
    layer_configs: Dict[MemoryLayer, LayerConfig] = field(default_factory=dict)
    
    # 同步配置
    auto_sync_enabled: bool = True
    sync_batch_size: int = 1000
    sync_interval_hours: int = 24
    
    # 维护配置
    auto_maintenance_enabled: bool = True
    maintenance_interval_hours: int = 6
    cleanup_batch_size: int = 500
    
    # 检索配置
    default_max_per_layer: int = 50
    layer_priority_strategy: str = "weight_based"  # weight_based, access_based, balanced
    
    # 性能配置
    cache_layer_info: bool = True
    cache_ttl_seconds: int = 300
    enable_async_operations: bool = True
    
    def __post_init__(self):
        """初始化后设置默认层级配置"""
        if not self.layer_configs:
            self.layer_configs = self._get_default_layer_configs()
    
    def _get_default_layer_configs(self) -> Dict[MemoryLayer, LayerConfig]:
        """获取默认层级配置"""
        return {
            MemoryLayer.CORE: LayerConfig(
                max_memories=1000,
                cleanup_interval_hours=168,  # 7天
                auto_promotion=True,
                auto_demotion=False,
                retention_days=365,
                weight_threshold=9.0
            ),
            MemoryLayer.ARCHIVE: LayerConfig(
                max_memories=5000,
                cleanup_interval_hours=72,  # 3天
                auto_promotion=True,
                auto_demotion=True,
                retention_days=180,
                weight_threshold=7.0
            ),
            MemoryLayer.LONG_TERM: LayerConfig(
                max_memories=20000,
                cleanup_interval_hours=24,  # 1天
                auto_promotion=True,
                auto_demotion=True,
                retention_days=90,
                weight_threshold=4.0
            ),
            MemoryLayer.SHORT_TERM: LayerConfig(
                max_memories=50000,
                cleanup_interval_hours=6,  # 6小时
                auto_promotion=True,
                auto_demotion=False,
                retention_days=30,
                weight_threshold=1.0
            )
        }


class LayerConfigManager:
    """分层配置管理器"""
    
    def __init__(self, config: Optional[LayerSystemConfig] = None):
        self.config = config or LayerSystemConfig()
        self._validate_config()
    
    def get_layer_config(self, layer: MemoryLayer) -> LayerConfig:
        """获取指定层级的配置"""
        return self.config.layer_configs.get(layer, self._get_fallback_config(layer))
    
    def update_layer_config(self, layer: MemoryLayer, config: LayerConfig) -> bool:
        """更新层级配置"""
        try:
            self.config.layer_configs[layer] = config
            self._validate_layer_config(layer, config)
            logger.info(f"已更新 {layer.value} 层级配置")
            return True
        except Exception as e:
            logger.error(f"更新层级配置失败: {e}")
            return False
    
    def get_system_config(self) -> LayerSystemConfig:
        """获取系统配置"""
        return self.config
    
    def update_system_config(self, **kwargs) -> bool:
        """更新系统配置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    logger.warning(f"未知配置项: {key}")
            
            self._validate_config()
            logger.info("系统配置已更新")
            return True
        except Exception as e:
            logger.error(f"更新系统配置失败: {e}")
            return False
    
    def get_maintenance_schedule(self) -> Dict[MemoryLayer, int]:
        """获取维护调度配置"""
        schedule = {}
        for layer, config in self.config.layer_configs.items():
            schedule[layer] = config.cleanup_interval_hours
        return schedule
    
    def get_capacity_limits(self) -> Dict[MemoryLayer, int]:
        """获取容量限制配置"""
        limits = {}
        for layer, config in self.config.layer_configs.items():
            limits[layer] = config.max_memories
        return limits
    
    def get_weight_thresholds(self) -> Dict[MemoryLayer, float]:
        """获取权重阈值配置"""
        thresholds = {}
        for layer, config in self.config.layer_configs.items():
            thresholds[layer] = config.weight_threshold
        return thresholds
    
    def is_auto_promotion_enabled(self, layer: MemoryLayer) -> bool:
        """检查是否启用自动提升"""
        config = self.get_layer_config(layer)
        return config.auto_promotion
    
    def is_auto_demotion_enabled(self, layer: MemoryLayer) -> bool:
        """检查是否启用自动降级"""
        config = self.get_layer_config(layer)
        return config.auto_demotion
    
    def get_retention_policy(self) -> Dict[MemoryLayer, int]:
        """获取保留策略"""
        policy = {}
        for layer, config in self.config.layer_configs.items():
            policy[layer] = config.retention_days
        return policy
    
    def export_config(self) -> Dict[str, Any]:
        """导出配置为字典"""
        try:
            config_dict = {
                'system': {
                    'auto_sync_enabled': self.config.auto_sync_enabled,
                    'sync_batch_size': self.config.sync_batch_size,
                    'sync_interval_hours': self.config.sync_interval_hours,
                    'auto_maintenance_enabled': self.config.auto_maintenance_enabled,
                    'maintenance_interval_hours': self.config.maintenance_interval_hours,
                    'cleanup_batch_size': self.config.cleanup_batch_size,
                    'default_max_per_layer': self.config.default_max_per_layer,
                    'layer_priority_strategy': self.config.layer_priority_strategy,
                    'cache_layer_info': self.config.cache_layer_info,
                    'cache_ttl_seconds': self.config.cache_ttl_seconds,
                    'enable_async_operations': self.config.enable_async_operations
                },
                'layers': {}
            }
            
            for layer, layer_config in self.config.layer_configs.items():
                config_dict['layers'][layer.value] = {
                    'max_memories': layer_config.max_memories,
                    'cleanup_interval_hours': layer_config.cleanup_interval_hours,
                    'auto_promotion': layer_config.auto_promotion,
                    'auto_demotion': layer_config.auto_demotion,
                    'retention_days': layer_config.retention_days,
                    'weight_threshold': layer_config.weight_threshold
                }
            
            return config_dict
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            return {}
    
    def import_config(self, config_dict: Dict[str, Any]) -> bool:
        """从字典导入配置"""
        try:
            # 导入系统配置
            if 'system' in config_dict:
                system_config = config_dict['system']
                for key, value in system_config.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
            
            # 导入层级配置
            if 'layers' in config_dict:
                for layer_name, layer_data in config_dict['layers'].items():
                    try:
                        layer = MemoryLayer(layer_name)
                        layer_config = LayerConfig(
                            max_memories=layer_data.get('max_memories', 1000),
                            cleanup_interval_hours=layer_data.get('cleanup_interval_hours', 24),
                            auto_promotion=layer_data.get('auto_promotion', True),
                            auto_demotion=layer_data.get('auto_demotion', True),
                            retention_days=layer_data.get('retention_days', 30),
                            weight_threshold=layer_data.get('weight_threshold', 1.0)
                        )
                        self.config.layer_configs[layer] = layer_config
                    except ValueError:
                        logger.warning(f"未知层级: {layer_name}")
            
            self._validate_config()
            logger.info("配置导入成功")
            return True
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False
    
    def _validate_config(self):
        """验证配置有效性"""
        # 验证系统配置
        if self.config.sync_batch_size <= 0:
            raise ValueError("sync_batch_size 必须大于 0")
        
        if self.config.cleanup_batch_size <= 0:
            raise ValueError("cleanup_batch_size 必须大于 0")
        
        if self.config.cache_ttl_seconds < 0:
            raise ValueError("cache_ttl_seconds 不能为负数")
        
        # 验证层级配置
        for layer, config in self.config.layer_configs.items():
            self._validate_layer_config(layer, config)
    
    def _validate_layer_config(self, layer: MemoryLayer, config: LayerConfig):
        """验证层级配置"""
        if config.max_memories <= 0:
            raise ValueError(f"{layer.value} 层级的 max_memories 必须大于 0")
        
        if config.cleanup_interval_hours <= 0:
            raise ValueError(f"{layer.value} 层级的 cleanup_interval_hours 必须大于 0")
        
        if config.retention_days <= 0:
            raise ValueError(f"{layer.value} 层级的 retention_days 必须大于 0")
        
        if not (0.0 <= config.weight_threshold <= 10.0):
            raise ValueError(f"{layer.value} 层级的 weight_threshold 必须在 0.0-10.0 范围内")
    
    def _get_fallback_config(self, layer: MemoryLayer) -> LayerConfig:
        """获取降级配置"""
        return LayerConfig(
            max_memories=10000,
            cleanup_interval_hours=24,
            auto_promotion=True,
            auto_demotion=True,
            retention_days=30,
            weight_threshold=1.0
        )


# 全局配置实例
_global_config_manager: Optional[LayerConfigManager] = None


def get_config_manager() -> LayerConfigManager:
    """获取全局配置管理器"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = LayerConfigManager()
    return _global_config_manager


def set_config_manager(config_manager: LayerConfigManager):
    """设置全局配置管理器"""
    global _global_config_manager
    _global_config_manager = config_manager