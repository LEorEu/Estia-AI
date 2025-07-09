"""
ConfigManager - 统一配置管理器
负责管理Estia AI记忆系统的所有配置参数
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class MemoryConfig:
    """记忆系统配置"""
    # 数据库配置
    db_path: str = "data/memory.db"
    
    # 向量化配置
    embedding_model: str = "Qwen3-Embedding-0.6B"
    vector_dimension: int = 1024
    
    # 缓存配置
    cache_enabled: bool = True
    cache_size: int = 1000
    cache_ttl: int = 3600
    
    # 权重配置
    weight_decay_rate: float = 0.995
    max_weight: float = 10.0
    min_weight: float = 0.1
    
    # 检索配置
    retrieval_top_k: int = 15
    similarity_threshold: float = 0.3
    association_depth: int = 2
    
    # 异步评估配置
    async_evaluation_enabled: bool = True
    evaluation_batch_size: int = 10
    evaluation_timeout: int = 30
    
    # 监控配置
    monitoring_enabled: bool = True
    performance_logging: bool = True
    
    # 生命周期配置
    archive_after_days: int = 30
    cleanup_after_days: int = 90
    
    # 错误恢复配置
    max_retries: int = 3
    retry_delay: float = 1.0
    fallback_enabled: bool = True

class ConfigManager:
    """配置管理器 - 统一管理所有配置"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/memory_config.json"
        self.config = MemoryConfig()
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._update_config(config_data)
        except Exception as e:
            print(f"Warning: Failed to load config file {self.config_file}: {e}")
            print("Using default configuration")
    
    def _update_config(self, config_data: Dict[str, Any]):
        """更新配置"""
        for key, value in config_data.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def save_config(self):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            config_data = self.config.__dict__
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save config file: {e}")
    
    def get_config(self) -> MemoryConfig:
        """获取配置对象"""
        return self.config
    
    def update_config(self, **kwargs):
        """动态更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.save_config()
    
    def get_db_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            'db_path': self.config.db_path
        }
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """获取向量化配置"""
        return {
            'model': self.config.embedding_model,
            'dimension': self.config.vector_dimension
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """获取缓存配置"""
        return {
            'enabled': self.config.cache_enabled,
            'size': self.config.cache_size,
            'ttl': self.config.cache_ttl
        }
    
    def get_weight_config(self) -> Dict[str, Any]:
        """获取权重配置"""
        return {
            'decay_rate': self.config.weight_decay_rate,
            'max_weight': self.config.max_weight,
            'min_weight': self.config.min_weight
        }
    
    def get_retrieval_config(self) -> Dict[str, Any]:
        """获取检索配置"""
        return {
            'top_k': self.config.retrieval_top_k,
            'similarity_threshold': self.config.similarity_threshold,
            'association_depth': self.config.association_depth
        }
    
    def get_async_config(self) -> Dict[str, Any]:
        """获取异步评估配置"""
        return {
            'enabled': self.config.async_evaluation_enabled,
            'batch_size': self.config.evaluation_batch_size,
            'timeout': self.config.evaluation_timeout
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """获取监控配置"""
        return {
            'enabled': self.config.monitoring_enabled,
            'performance_logging': self.config.performance_logging
        }
    
    def get_lifecycle_config(self) -> Dict[str, Any]:
        """获取生命周期配置"""
        return {
            'archive_after_days': self.config.archive_after_days,
            'cleanup_after_days': self.config.cleanup_after_days
        }
    
    def get_recovery_config(self) -> Dict[str, Any]:
        """获取错误恢复配置"""
        return {
            'max_retries': self.config.max_retries,
            'retry_delay': self.config.retry_delay,
            'fallback_enabled': self.config.fallback_enabled
        }
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        try:
            # 验证数据路径
            if not self.config.db_path:
                return False
            
            # 验证权重范围
            if self.config.max_weight <= self.config.min_weight:
                return False
            
            # 验证向量维度
            if self.config.vector_dimension <= 0:
                return False
            
            # 验证检索参数
            if self.config.retrieval_top_k <= 0:
                return False
                
            return True
            
        except Exception:
            return False
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.config = MemoryConfig()
        self.save_config()

# 全局配置实例
_config_manager = None

def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_memory_config() -> MemoryConfig:
    """获取记忆系统配置"""
    return get_config_manager().get_config()