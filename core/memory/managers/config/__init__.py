#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理器 (ConfigManager) - 新增模块
统一管理记忆系统配置，从config/settings.py中分离记忆相关配置
职责：配置统一管理、动态配置更新和验证
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from ...internal import handle_memory_errors, ErrorHandlerMixin

logger = logging.getLogger(__name__)

class ConfigManager(ErrorHandlerMixin):
    """配置管理器 - 统一管理记忆系统配置"""
    
    DEFAULT_CONFIG = {
        # 数据库配置
        'database': {
            'path': 'assets/memory.db',
            'backup_interval': 3600,  # 1小时
            'auto_vacuum': True
        },
        
        # 向量化配置
        'vectorization': {
            'model_name': 'text-embedding-3-small',
            'dimension': 1536,
            'batch_size': 32,
            'cache_size': 10000
        },
        
        # FAISS配置
        'faiss': {
            'index_type': 'IndexFlatIP',
            'search_k': 15,
            'similarity_threshold': 0.3,
            'rebuild_threshold': 10000
        },
        
        # 记忆分层配置
        'memory_layers': {
            'core_memory': {'min_weight': 9.0, 'max_weight': 10.0},
            'archive_memory': {'min_weight': 7.0, 'max_weight': 8.9},
            'long_term_memory': {'min_weight': 4.0, 'max_weight': 6.9},
            'short_term_memory': {'min_weight': 1.0, 'max_weight': 3.9}
        },
        
        # 权重算法配置
        'weight_algorithm': {
            'time_decay_rate': 0.995,
            'access_frequency_boost': 1.1,
            'contextual_relevance_boost': 1.2,
            'emotional_intensity_boost': 1.15,
            'recency_boost': 1.3
        },
        
        # 异步评估配置
        'async_evaluation': {
            'queue_size': 1000,
            'batch_size': 10,
            'evaluation_timeout': 30,
            'retry_attempts': 3
        },
        
        # 缓存配置
        'cache': {
            'l1_size': 1000,
            'l2_size': 5000,
            'l3_size': 10000,
            'ttl_seconds': 3600
        },
        
        # 性能配置
        'performance': {
            'max_search_time_ms': 500,
            'max_context_length': 8000,
            'concurrent_limit': 10,
            'monitoring_enabled': True
        },
        
        # 生命周期配置
        'lifecycle': {
            'cleanup_interval': 86400,  # 24小时
            'archive_threshold_days': 30,
            'delete_threshold_days': 90,
            'compression_enabled': True
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为None使用内置配置
        """
        super().__init__()
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        self.logger = logger
        
        # 加载配置文件
        if config_path:
            self.load_config(config_path)
    
    @handle_memory_errors({})
    def load_config(self, config_path: str) -> bool:
        """
        从文件加载配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 深度合并配置
                self.config = self._deep_merge(self.DEFAULT_CONFIG, user_config)
                self.logger.info(f"✅ 配置文件加载成功: {config_path}")
                return True
            else:
                self.logger.warning(f"配置文件不存在: {config_path}, 使用默认配置")
                return False
                
        except Exception as e:
            self.logger.error(f"配置文件加载失败: {e}")
            return False
    
    @handle_memory_errors(False)
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径，默认使用初始化时的路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            save_path = config_path or self.config_path
            if not save_path:
                self.logger.error("保存配置失败: 未指定配置文件路径")
                return False
            
            config_file = Path(save_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ 配置文件保存成功: {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"配置文件保存失败: {e}")
            return False
    
    def get_config(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径，用.分隔，如 'database.path'
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    @handle_memory_errors(False)
    def set_config(self, key_path: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key_path: 配置键路径，用.分隔
            value: 配置值
            
        Returns:
            bool: 设置是否成功
        """
        try:
            keys = key_path.split('.')
            config = self.config
            
            # 导航到目标位置
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # 设置值
            config[keys[-1]] = value
            
            self.logger.debug(f"配置更新: {key_path} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"配置设置失败: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """
        验证配置完整性和合理性
        
        Returns:
            Dict: 验证结果
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # 验证必需的配置项
            required_paths = [
                'database.path',
                'vectorization.model_name',
                'faiss.index_type',
                'memory_layers.core_memory.min_weight'
            ]
            
            for path in required_paths:
                if self.get_config(path) is None:
                    validation_result['errors'].append(f"缺少必需配置: {path}")
                    validation_result['valid'] = False
            
            # 验证数值范围
            faiss_k = self.get_config('faiss.search_k', 15)
            if faiss_k <= 0 or faiss_k > 100:
                validation_result['warnings'].append(f"FAISS搜索数量可能不合理: {faiss_k}")
            
            # 验证权重范围
            layers = self.get_config('memory_layers', {})
            for layer_name, layer_config in layers.items():
                min_weight = layer_config.get('min_weight', 0)
                max_weight = layer_config.get('max_weight', 0)
                if min_weight >= max_weight:
                    validation_result['errors'].append(f"权重范围错误 {layer_name}: min({min_weight}) >= max({max_weight})")
                    validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"配置验证异常: {e}")
            return validation_result
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.get_config('database', {})
    
    def get_vectorization_config(self) -> Dict[str, Any]:
        """获取向量化配置"""
        return self.get_config('vectorization', {})
    
    def get_faiss_config(self) -> Dict[str, Any]:
        """获取FAISS配置"""
        return self.get_config('faiss', {})
    
    def get_memory_layer_config(self) -> Dict[str, Any]:
        """获取记忆分层配置"""
        return self.get_config('memory_layers', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能配置"""
        return self.get_config('performance', {})
    
    def update_runtime_config(self, updates: Dict[str, Any]) -> bool:
        """
        运行时配置更新
        
        Args:
            updates: 配置更新字典
            
        Returns:
            bool: 更新是否成功
        """
        try:
            for key_path, value in updates.items():
                self.set_config(key_path, value)
            
            # 验证更新后的配置
            validation = self.validate_config()
            if not validation['valid']:
                self.logger.warning(f"配置更新后验证失败: {validation['errors']}")
                return False
            
            self.logger.info("✅ 运行时配置更新成功")
            return True
            
        except Exception as e:
            self.logger.error(f"运行时配置更新失败: {e}")
            return False