#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控系统配置
============

统一的监控系统配置管理。
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class WebConfig:
    """Web服务配置"""
    host: str = '127.0.0.1'
    port: int = 5000
    debug: bool = False
    vue_dist_path: str = ''
    
    def __post_init__(self):
        if not self.vue_dist_path:
            # 自动检测Vue构建路径
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.vue_dist_path = os.path.join(project_root, 'web-vue', 'dist')


@dataclass 
class CacheConfig:
    """缓存配置"""
    enabled: bool = True
    ttl_seconds: int = 3
    max_size: int = 1000
    cleanup_interval: int = 300  # 5分钟


@dataclass
class PerformanceConfig:
    """性能监控配置"""
    collection_interval: float = 5.0  # 收集间隔（秒）
    max_history: int = 1000           # 最大历史记录数
    thread_pool_size: int = 4         # 线程池大小


@dataclass
class AlertConfig:
    """告警配置"""
    enabled: bool = True
    default_rules_enabled: bool = True
    notification_channels: List[str] = field(default_factory=lambda: ['console'])
    
    # 默认阈值
    cpu_warning_threshold: float = 80.0
    cpu_critical_threshold: float = 90.0
    memory_warning_threshold: float = 85.0
    memory_critical_threshold: float = 95.0
    cache_hit_rate_threshold: float = 0.6
    query_time_threshold: float = 1000.0  # 毫秒
    error_rate_threshold: float = 0.05


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_enabled: bool = False
    file_path: str = 'monitoring.log'


@dataclass
class MonitoringConfig:
    """监控系统主配置"""
    
    # 子配置
    web: WebConfig = field(default_factory=WebConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # 功能开关
    memory_system_integration: bool = True
    websocket_enabled: bool = True
    background_monitoring: bool = True
    auto_optimization: bool = True
    
    # 系统设置
    system_name: str = "Estia AI 监控系统"
    version: str = "1.0.0"
    
    @classmethod
    def from_env(cls) -> 'MonitoringConfig':
        """从环境变量创建配置"""
        config = cls()
        
        # Web配置
        config.web.host = os.getenv('MONITORING_HOST', config.web.host)
        config.web.port = int(os.getenv('MONITORING_PORT', str(config.web.port)))
        config.web.debug = os.getenv('MONITORING_DEBUG', 'false').lower() == 'true'
        
        # 缓存配置
        config.cache.enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        config.cache.ttl_seconds = int(os.getenv('CACHE_TTL', str(config.cache.ttl_seconds)))
        
        # 性能配置
        config.performance.collection_interval = float(os.getenv('COLLECTION_INTERVAL', str(config.performance.collection_interval)))
        
        # 告警配置
        config.alerts.enabled = os.getenv('ALERTS_ENABLED', 'true').lower() == 'true'
        config.alerts.cpu_warning_threshold = float(os.getenv('CPU_WARNING_THRESHOLD', str(config.alerts.cpu_warning_threshold)))
        config.alerts.memory_warning_threshold = float(os.getenv('MEMORY_WARNING_THRESHOLD', str(config.alerts.memory_warning_threshold)))
        
        # 日志配置
        config.logging.level = os.getenv('LOG_LEVEL', config.logging.level)
        config.logging.file_enabled = os.getenv('LOG_FILE_ENABLED', 'false').lower() == 'true'
        config.logging.file_path = os.getenv('LOG_FILE_PATH', config.logging.file_path)
        
        return config
    
    @classmethod
    def from_file(cls, config_path: str) -> 'MonitoringConfig':
        """从配置文件创建配置"""
        import json
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            config = cls()
            
            # 更新配置
            if 'web' in config_data:
                for key, value in config_data['web'].items():
                    if hasattr(config.web, key):
                        setattr(config.web, key, value)
            
            if 'cache' in config_data:
                for key, value in config_data['cache'].items():
                    if hasattr(config.cache, key):
                        setattr(config.cache, key, value)
            
            if 'performance' in config_data:
                for key, value in config_data['performance'].items():
                    if hasattr(config.performance, key):
                        setattr(config.performance, key, value)
            
            if 'alerts' in config_data:
                for key, value in config_data['alerts'].items():
                    if hasattr(config.alerts, key):
                        setattr(config.alerts, key, value)
            
            if 'logging' in config_data:
                for key, value in config_data['logging'].items():
                    if hasattr(config.logging, key):
                        setattr(config.logging, key, value)
            
            # 更新顶级配置
            for key in ['memory_system_integration', 'websocket_enabled', 'background_monitoring', 'auto_optimization']:
                if key in config_data:
                    setattr(config, key, config_data[key])
            
            return config
            
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'web': {
                'host': self.web.host,
                'port': self.web.port,
                'debug': self.web.debug,
                'vue_dist_path': self.web.vue_dist_path
            },
            'cache': {
                'enabled': self.cache.enabled,
                'ttl_seconds': self.cache.ttl_seconds,
                'max_size': self.cache.max_size,
                'cleanup_interval': self.cache.cleanup_interval
            },
            'performance': {
                'collection_interval': self.performance.collection_interval,
                'max_history': self.performance.max_history,
                'thread_pool_size': self.performance.thread_pool_size
            },
            'alerts': {
                'enabled': self.alerts.enabled,
                'default_rules_enabled': self.alerts.default_rules_enabled,
                'notification_channels': self.alerts.notification_channels,
                'cpu_warning_threshold': self.alerts.cpu_warning_threshold,
                'memory_warning_threshold': self.alerts.memory_warning_threshold
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file_enabled': self.logging.file_enabled,
                'file_path': self.logging.file_path
            },
            'memory_system_integration': self.memory_system_integration,
            'websocket_enabled': self.websocket_enabled,
            'background_monitoring': self.background_monitoring,
            'auto_optimization': self.auto_optimization,
            'system_name': self.system_name,
            'version': self.version
        }
    
    def save_to_file(self, config_path: str):
        """保存配置到文件"""
        import json
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"配置已保存到: {config_path}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def validate(self) -> List[str]:
        """验证配置，返回错误列表"""
        errors = []
        
        # 验证端口
        if not (1 <= self.web.port <= 65535):
            errors.append(f"无效的端口号: {self.web.port}")
        
        # 验证Vue路径
        if not os.path.exists(self.web.vue_dist_path):
            errors.append(f"Vue构建路径不存在: {self.web.vue_dist_path}")
        
        # 验证缓存配置
        if self.cache.ttl_seconds <= 0:
            errors.append(f"缓存TTL必须大于0: {self.cache.ttl_seconds}")
        
        # 验证性能配置
        if self.performance.collection_interval <= 0:
            errors.append(f"收集间隔必须大于0: {self.performance.collection_interval}")
        
        # 验证告警阈值
        if not (0 <= self.alerts.cpu_warning_threshold <= 100):
            errors.append(f"CPU告警阈值必须在0-100之间: {self.alerts.cpu_warning_threshold}")
        
        return errors