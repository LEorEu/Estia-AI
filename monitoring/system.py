#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一监控系统
============

整合所有监控组件的主系统。
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .config.monitoring_config import MonitoringConfig
from .core.performance_monitor import PerformanceMonitor
from .core.metrics_collector import MetricsCollector
from .core.alert_manager import AlertManager
from .memory.memory_monitor_interface import MemoryMonitorInterface

logger = logging.getLogger(__name__)


class MonitoringSystem:
    """
    统一监控系统
    
    整合所有监控组件，提供统一的接口。
    """
    
    def __init__(self, config: MonitoringConfig):
        """
        初始化监控系统
        
        Args:
            config: 监控配置
        """
        self.config = config
        self.started = False
        
        # 初始化组件
        self._initialize_logging()
        self._initialize_components()
        
        logger.info(f"🚀 {config.system_name} v{config.version} 初始化完成")
    
    def _initialize_logging(self):
        """初始化日志"""
        log_level = getattr(logging, self.config.logging.level.upper())
        logging.basicConfig(
            level=log_level,
            format=self.config.logging.format
        )
        
        if self.config.logging.file_enabled:
            file_handler = logging.FileHandler(self.config.logging.file_path)
            file_handler.setFormatter(logging.Formatter(self.config.logging.format))
            logging.getLogger().addHandler(file_handler)
    
    def _initialize_components(self):
        """初始化监控组件"""
        try:
            # 记忆系统监控接口
            self.memory_monitor = MemoryMonitorInterface()
            
            # 指标收集器
            self.metrics_collector = MetricsCollector(
                collection_interval=self.config.performance.collection_interval
            )
            
            # 性能监控器
            self.performance_monitor = PerformanceMonitor(
                memory_system=None,  # 通过memory_monitor访问
                collection_interval=self.config.performance.collection_interval
            )
            
            # 告警管理器
            self.alert_manager = AlertManager()
            
            # 添加记忆系统指标收集器
            if self.config.memory_system_integration and self.memory_monitor.is_available():
                self.metrics_collector.add_custom_collector(self._collect_memory_metrics)
            
            # 添加告警通知回调
            self.alert_manager.add_notification_callback(self._handle_alert_notification)
            
            logger.info("✅ 监控组件初始化完成")
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise
    
    def start(self):
        """启动监控系统"""
        if self.started:
            logger.warning("监控系统已启动")
            return
        
        try:
            # 启动指标收集
            if self.config.performance.collection_interval > 0:
                self.metrics_collector.start_collection()
                self.performance_monitor.start_monitoring()
            
            self.started = True
            logger.info("🚀 监控系统启动成功")
            
        except Exception as e:
            logger.error(f"监控系统启动失败: {e}")
            raise
    
    def stop(self):
        """停止监控系统"""
        if not self.started:
            return
        
        try:
            # 停止监控组件
            self.metrics_collector.stop_collection()
            self.performance_monitor.stop_monitoring()
            
            self.started = False
            logger.info("⏹️ 监控系统已停止")
            
        except Exception as e:
            logger.error(f"停止监控系统失败: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_name': self.config.system_name,
            'version': self.config.version,
            'started': self.started,
            'components': {
                'memory_monitor': {
                    'available': self.memory_monitor.is_available(),
                    'status': 'active' if self.memory_monitor.is_available() else 'unavailable'
                },
                'metrics_collector': {
                    'collecting': self.metrics_collector.collecting,
                    'stats': self.metrics_collector.get_collection_stats()
                },
                'performance_monitor': {
                    'monitoring': self.performance_monitor.monitoring_active,
                    'summary': self.performance_monitor.get_performance_summary()
                },
                'alert_manager': {
                    'active_alerts': len(self.alert_manager.get_active_alerts()),
                    'stats': self.alert_manager.get_alert_statistics()
                }
            },
            'config': {
                'web_port': self.config.web.port,
                'cache_enabled': self.config.cache.enabled,
                'alerts_enabled': self.config.alerts.enabled,
                'memory_integration': self.config.memory_system_integration
            }
        }
    
    def get_comprehensive_data(self) -> Dict[str, Any]:
        """获取综合监控数据"""
        try:
            # 当前指标
            current_metrics = self.metrics_collector.get_all_current_metrics()
            
            # 性能摘要
            performance_summary = self.performance_monitor.get_performance_summary()
            
            # 记忆系统数据
            memory_data = {}
            if self.memory_monitor.is_available():
                memory_data = self.memory_monitor.get_comprehensive_stats()
            
            # 活跃告警
            active_alerts = self.alert_manager.get_active_alerts()
            
            # 系统健康评分
            health_score = self._calculate_health_score(current_metrics, active_alerts)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system_status': self.get_system_status(),
                'current_metrics': current_metrics,
                'performance_summary': performance_summary,
                'memory_system_data': memory_data,
                'active_alerts': [
                    {
                        'alert_id': alert.alert_id,
                        'rule_name': alert.rule.name,
                        'severity': alert.rule.severity.value,
                        'message': alert.message,
                        'triggered_at': alert.triggered_at,
                        'status': alert.status.value
                    }
                    for alert in active_alerts
                ],
                'health_score': health_score,
                'recommendations': self._generate_recommendations(current_metrics, active_alerts)
            }
            
        except Exception as e:
            logger.error(f"获取综合数据失败: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _collect_memory_metrics(self) -> Dict[str, float]:
        """收集记忆系统指标"""
        try:
            if not self.memory_monitor.is_available():
                return {}
            
            # 获取记忆系统实时指标
            metrics = self.memory_monitor.get_real_time_metrics()
            
            # 转换为数值指标
            numeric_metrics = {}
            
            cache_perf = metrics.get('cache_performance', {})
            if isinstance(cache_perf, dict):
                numeric_metrics['memory_cache_hit_rate'] = cache_perf.get('hit_rate', 0.0)
                numeric_metrics['memory_cache_size'] = cache_perf.get('cache_size', 0.0)
            
            db_perf = metrics.get('database_performance', {})
            if isinstance(db_perf, dict):
                numeric_metrics['memory_db_connections'] = db_perf.get('active_connections', 0.0)
                numeric_metrics['memory_db_query_time'] = db_perf.get('avg_query_time', 0.0)
            
            queue_status = metrics.get('queue_status', {})
            if isinstance(queue_status, dict):
                numeric_metrics['memory_queue_size'] = queue_status.get('pending_tasks', 0.0)
            
            return numeric_metrics
            
        except Exception as e:
            logger.error(f"收集记忆系统指标失败: {e}")
            return {}
    
    def _handle_alert_notification(self, alert):
        """处理告警通知"""
        try:
            severity_emoji = {
                'info': 'ℹ️',
                'warning': '⚠️', 
                'critical': '🔴'
            }
            
            emoji = severity_emoji.get(alert.rule.severity.value, '🚨')
            logger.warning(f"{emoji} 告警触发: {alert.rule.name} - {alert.message}")
            
            # 这里可以添加其他通知渠道（邮件、微信等）
            
        except Exception as e:
            logger.error(f"处理告警通知失败: {e}")
    
    def _calculate_health_score(self, metrics: Dict[str, float], alerts: list) -> Dict[str, Any]:
        """计算系统健康评分"""
        try:
            score = 100.0
            issues = []
            
            # 根据指标扣分
            cpu_usage = metrics.get('system.cpu.usage_percent', 0)
            if cpu_usage > 80:
                score -= min(20, (cpu_usage - 80) * 2)
                issues.append(f"CPU使用率过高: {cpu_usage:.1f}%")
            
            memory_usage = metrics.get('system.memory.usage_percent', 0)
            if memory_usage > 85:
                score -= min(25, (memory_usage - 85) * 3)
                issues.append(f"内存使用率过高: {memory_usage:.1f}%")
            
            # 根据告警扣分
            critical_alerts = len([a for a in alerts if a.rule.severity.value == 'critical'])
            warning_alerts = len([a for a in alerts if a.rule.severity.value == 'warning'])
            
            score -= critical_alerts * 15
            score -= warning_alerts * 5
            
            if critical_alerts > 0:
                issues.append(f"{critical_alerts}个严重告警")
            if warning_alerts > 0:
                issues.append(f"{warning_alerts}个警告告警")
            
            score = max(0, score)
            
            # 健康等级
            if score >= 90:
                level = "优秀"
                emoji = "💚"
            elif score >= 75:
                level = "良好"
                emoji = "💛"
            elif score >= 60:
                level = "一般"
                emoji = "🧡"
            else:
                level = "需要关注"
                emoji = "❤️"
            
            return {
                'score': round(score, 1),
                'level': level,
                'emoji': emoji,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"计算健康评分失败: {e}")
            return {
                'score': 0,
                'level': "未知",
                'emoji': "❓",
                'issues': [f"评分计算失败: {e}"]
            }
    
    def _generate_recommendations(self, metrics: Dict[str, float], alerts: list) -> list:
        """生成优化建议"""
        recommendations = []
        
        try:
            # CPU相关建议
            cpu_usage = metrics.get('system.cpu.usage_percent', 0)
            if cpu_usage > 80:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high' if cpu_usage > 90 else 'medium',
                    'title': 'CPU使用率过高',
                    'description': f'当前CPU使用率为{cpu_usage:.1f}%，建议检查高耗CPU的进程',
                    'actions': ['检查后台进程', '优化查询逻辑', '考虑增加计算资源']
                })
            
            # 内存相关建议
            memory_usage = metrics.get('system.memory.usage_percent', 0)
            if memory_usage > 85:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high' if memory_usage > 95 else 'medium',
                    'title': '内存使用率过高',
                    'description': f'当前内存使用率为{memory_usage:.1f}%，建议清理缓存或增加内存',
                    'actions': ['清理缓存', '优化内存使用', '考虑增加内存容量']
                })
            
            # 缓存相关建议
            cache_hit_rate = metrics.get('memory_cache_hit_rate', 1.0)
            if cache_hit_rate < 0.8:
                recommendations.append({
                    'type': 'optimization',
                    'priority': 'medium',
                    'title': '缓存命中率偏低',
                    'description': f'当前缓存命中率为{cache_hit_rate:.1%}，建议优化缓存策略',
                    'actions': ['检查缓存配置', '优化缓存大小', '调整缓存策略']
                })
            
            # 告警相关建议
            if alerts:
                recommendations.append({
                    'type': 'alert',
                    'priority': 'high',
                    'title': '存在活跃告警',
                    'description': f'当前有{len(alerts)}个活跃告警需要处理',
                    'actions': ['查看告警详情', '处理告警原因', '优化告警规则']
                })
            
        except Exception as e:
            logger.error(f"生成建议失败: {e}")
        
        return recommendations