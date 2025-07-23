#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统监控集成
================

将性能监控系统集成到Estia AI记忆系统中，提供无缝的监控体验。
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, List
from contextlib import contextmanager

from .performance_monitor import PerformanceMonitor
from .metrics_collector import MetricsCollector
from .dashboard_server import DashboardServer
from .alert_manager import AlertManager, default_alert_callback

logger = logging.getLogger(__name__)


class MemorySystemMonitor:
    """
    记忆系统监控集成器
    
    集成所有监控组件，为记忆系统提供完整的监控解决方案：
    - 性能监控
    - 指标收集
    - 告警管理
    - Web仪表板
    """
    
    def __init__(self, memory_system=None, enable_dashboard=True, dashboard_port=8080):
        """
        初始化监控集成器
        
        Args:
            memory_system: Estia记忆系统实例
            enable_dashboard: 是否启用Web仪表板
            dashboard_port: 仪表板端口
        """
        self.memory_system = memory_system
        self.enable_dashboard = enable_dashboard
        self.dashboard_port = dashboard_port
        
        # 初始化监控组件
        self.metrics_collector = MetricsCollector(collection_interval=5.0)
        self.performance_monitor = PerformanceMonitor(
            memory_system=memory_system,
            collection_interval=5.0
        )
        self.alert_manager = AlertManager()
        
        # Web仪表板
        self.dashboard_server = None
        if enable_dashboard:
            self.dashboard_server = DashboardServer(
                performance_monitor=self.performance_monitor,
                port=dashboard_port
            )
        
        # 监控状态
        self.monitoring_active = False
        self._lock = threading.RLock()
        
        # 设置监控集成
        self._setup_integration()
        
        logger.info("🔍 记忆系统监控集成器初始化完成")
    
    def _setup_integration(self):
        """设置监控集成"""
        try:
            # 添加记忆系统指标收集器
            self.metrics_collector.add_custom_collector(self._collect_memory_metrics)
            
            # 添加性能监控告警回调
            self.performance_monitor.add_alert_callback(self._handle_performance_alert)
            
            # 添加默认告警通知
            self.alert_manager.add_notification_callback(default_alert_callback)
            
            logger.info("✅ 监控集成设置完成")
            
        except Exception as e:
            logger.error(f"设置监控集成失败: {e}")
    
    def start_monitoring(self):
        """启动完整监控系统"""
        if self.monitoring_active:
            logger.warning("监控系统已在运行")
            return
        
        try:
            with self._lock:
                # 启动指标收集
                self.metrics_collector.start_collection()
                
                # 启动性能监控
                self.performance_monitor.start_monitoring()
                
                # 启动Web仪表板
                if self.dashboard_server:
                    self.dashboard_server.start()
                
                self.monitoring_active = True
                
                logger.info("🚀 监控系统已全面启动")
                if self.dashboard_server:
                    logger.info(f"📊 仪表板地址: {self.dashboard_server.get_dashboard_url()}")
                
        except Exception as e:
            logger.error(f"启动监控系统失败: {e}")
            self.stop_monitoring()  # 清理部分启动的组件
            raise
    
    def stop_monitoring(self):
        """停止监控系统"""
        if not self.monitoring_active:
            return
        
        try:
            with self._lock:
                # 停止指标收集
                self.metrics_collector.stop_collection()
                
                # 停止性能监控
                self.performance_monitor.stop_monitoring()
                
                # 停止Web仪表板
                if self.dashboard_server:
                    self.dashboard_server.stop()
                
                self.monitoring_active = False
                
                logger.info("🛑 监控系统已停止")
                
        except Exception as e:
            logger.error(f"停止监控系统失败: {e}")
    
    @contextmanager
    def monitor_operation(self, operation_name: str, metadata: Dict[str, Any] = None):
        """
        操作监控上下文管理器
        
        用法:
        with monitor.monitor_operation('query_enhancement') as ctx:
            # 执行操作
            result = do_something()
            ctx.set_result_size(len(result))
        """
        start_time = time.time()
        operation_id = f"{operation_name}_{int(start_time * 1000)}"
        
        class OperationContext:
            def __init__(self, monitor, op_name, op_id, start):
                self.monitor = monitor
                self.operation_name = op_name
                self.operation_id = op_id
                self.start_time = start
                self.metadata = metadata or {}
                self.success = True
                self.error = None
            
            def set_result_size(self, size: int):
                self.metadata['result_size'] = size
            
            def set_processed_count(self, count: int):
                self.metadata['processed_count'] = count
            
            def set_cache_hit_rate(self, rate: float):
                self.metadata['cache_hit_rate'] = rate
            
            def mark_error(self, error: Exception):
                self.success = False
                self.error = error
        
        context = OperationContext(self, operation_name, operation_id, start_time)
        
        try:
            logger.debug(f"🔍 开始监控操作: {operation_name}")
            yield context
            
        except Exception as e:
            context.mark_error(e)
            raise
            
        finally:
            # 记录操作性能
            duration_ms = (time.time() - start_time) * 1000
            
            self.performance_monitor.record_operation(
                operation=operation_name,
                duration_ms=duration_ms,
                success=context.success,
                metadata=context.metadata
            )
            
            # 记录自定义指标
            self.metrics_collector.record_metric(
                f'operations.{operation_name}.duration_ms',
                duration_ms
            )
            
            if context.success:
                self.metrics_collector.record_metric(
                    f'operations.{operation_name}.success_count',
                    1
                )
            else:
                self.metrics_collector.record_metric(
                    f'operations.{operation_name}.error_count',
                    1
                )
            
            logger.debug(f"🔍 完成操作监控: {operation_name} "
                        f"({'成功' if context.success else '失败'}, {duration_ms:.1f}ms)")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """获取监控系统状态"""
        try:
            # 获取当前性能指标
            current_metrics = self.performance_monitor.get_current_metrics()
            
            # 获取告警统计
            alert_stats = self.alert_manager.get_alert_statistics()
            
            # 获取收集器统计
            collector_stats = self.metrics_collector.get_collection_stats()
            
            return {
                'monitoring_active': self.monitoring_active,
                'dashboard_enabled': self.enable_dashboard,
                'dashboard_url': self.dashboard_server.get_dashboard_url() if self.dashboard_server else None,
                'current_metrics': {
                    'cpu_usage': current_metrics.cpu_usage,
                    'memory_usage_percent': current_metrics.memory_usage_percent,
                    'cache_hit_rate': current_metrics.cache_hit_rate,
                    'avg_query_time_ms': current_metrics.avg_query_time_ms,
                    'queries_per_second': current_metrics.queries_per_second,
                    'error_rate': current_metrics.error_rate
                },
                'alert_summary': {
                    'active_alerts': alert_stats.get('active_alerts', 0),
                    'alerts_24h': alert_stats.get('alerts_24h', 0)
                },
                'collector_summary': {
                    'metrics_count': collector_stats.get('metrics_count', 0),
                    'total_data_points': collector_stats.get('total_data_points', 0)
                },
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"获取监控状态失败: {e}")
            return {
                'monitoring_active': self.monitoring_active,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """获取综合监控报告"""
        try:
            return {
                'system_overview': self.get_monitoring_status(),
                'performance_summary': self.performance_monitor.get_performance_summary(),
                'alert_statistics': self.alert_manager.get_alert_statistics(),
                'active_alerts': [
                    {
                        'alert_id': alert.alert_id,
                        'rule_name': alert.rule.name,
                        'severity': alert.rule.severity.value,
                        'message': alert.message,
                        'triggered_at': alert.triggered_at,
                        'current_value': alert.current_value
                    }
                    for alert in self.alert_manager.get_active_alerts()
                ],
                'top_metrics': self._get_top_metrics(),
                'health_status': self._assess_system_health(),
                'recommendations': self._generate_recommendations(),
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"生成综合报告失败: {e}")
            return {
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _collect_memory_metrics(self) -> Dict[str, float]:
        """收集记忆系统专用指标"""
        try:
            if not self.memory_system:
                return {}
            
            # 获取记忆系统统计
            stats = self.memory_system.get_system_stats()
            
            metrics = {}
            
            # 缓存指标
            cache_stats = stats.get('unified_cache', {})
            if cache_stats and not isinstance(cache_stats, dict) or 'error' not in cache_stats:
                if cache_stats.get('access_count', 0) > 0:
                    hit_rate = cache_stats.get('hit_count', 0) / cache_stats.get('access_count', 1)
                    metrics['memory.cache.hit_rate'] = hit_rate
                
                metrics['memory.cache.size'] = cache_stats.get('size', 0)
                metrics['memory.cache.hit_count'] = cache_stats.get('hit_count', 0)
                metrics['memory.cache.miss_count'] = cache_stats.get('miss_count', 0)
            
            # 记忆统计
            metrics['memory.total_memories'] = stats.get('total_memories', 0)
            metrics['memory.active_memories'] = stats.get('active_memories', 0)
            metrics['memory.archived_memories'] = stats.get('archived_memories', 0)
            
            # 会话统计
            async_queue = stats.get('async_queue', {})
            if isinstance(async_queue, dict):
                metrics['memory.active_sessions'] = len(async_queue.get('active_sessions', []))
            
            # 组件状态
            components = stats.get('components', {})
            if isinstance(components, dict):
                active_components = sum(1 for active in components.values() if active)
                metrics['memory.active_components'] = active_components
            
            return metrics
            
        except Exception as e:
            logger.error(f"收集记忆系统指标失败: {e}")
            return {}
    
    def _handle_performance_alert(self, alert_data: Dict[str, Any]):
        """处理性能告警"""
        try:
            # 将性能监控的告警转换为告警管理器格式
            metric_name = alert_data.get('type', 'unknown').replace('_', '.')
            current_value = alert_data.get('value', 0)
            
            # 构建指标字典用于告警检查
            metrics = {metric_name: current_value}
            
            # 触发告警检查
            new_alerts = self.alert_manager.check_metrics(metrics)
            
            if new_alerts:
                logger.info(f"🚨 触发了 {len(new_alerts)} 个新告警")
            
        except Exception as e:
            logger.error(f"处理性能告警失败: {e}")
    
    def _get_top_metrics(self) -> List[Dict[str, Any]]:
        """获取重要指标摘要"""
        try:
            important_metrics = [
                'system.cpu.usage_percent',
                'system.memory.usage_percent', 
                'memory.cache.hit_rate',
                'memory.total_memories',
                'operations.query_enhancement.duration_ms'
            ]
            
            top_metrics = []
            for metric_name in important_metrics:
                summary = self.metrics_collector.get_metric_summary(metric_name, 60)
                if summary.get('count', 0) > 0:
                    top_metrics.append(summary)
            
            return top_metrics
            
        except Exception as e:
            logger.error(f"获取重要指标失败: {e}")
            return []
    
    def _assess_system_health(self) -> Dict[str, Any]:
        """评估系统健康状态"""
        try:
            current_metrics = self.performance_monitor.get_current_metrics()
            active_alerts = self.alert_manager.get_active_alerts()
            
            # 健康评分 (0-100)
            health_score = 100
            health_issues = []
            
            # CPU使用率影响
            if current_metrics.cpu_usage > 90:
                health_score -= 30
                health_issues.append("CPU使用率严重过高")
            elif current_metrics.cpu_usage > 80:
                health_score -= 15
                health_issues.append("CPU使用率过高")
            
            # 内存使用率影响
            if current_metrics.memory_usage_percent > 95:
                health_score -= 25
                health_issues.append("内存使用率严重过高")
            elif current_metrics.memory_usage_percent > 85:
                health_score -= 10
                health_issues.append("内存使用率过高")
            
            # 错误率影响
            if current_metrics.error_rate > 0.1:
                health_score -= 40
                health_issues.append("错误率严重过高")
            elif current_metrics.error_rate > 0.05:
                health_score -= 20
                health_issues.append("错误率过高")
            
            # 缓存命中率影响
            if current_metrics.cache_hit_rate < 0.5:
                health_score -= 15
                health_issues.append("缓存命中率过低")
            
            # 活跃告警影响
            critical_alerts = len([a for a in active_alerts if a.rule.severity.value == 'critical'])
            warning_alerts = len([a for a in active_alerts if a.rule.severity.value == 'warning'])
            
            health_score -= critical_alerts * 20
            health_score -= warning_alerts * 5
            
            health_score = max(0, health_score)
            
            # 健康状态分级
            if health_score >= 90:
                status = "优秀"
                status_emoji = "🟢"
            elif health_score >= 70:
                status = "良好"
                status_emoji = "🟡"
            elif health_score >= 50:
                status = "一般"
                status_emoji = "🟠"
            else:
                status = "需要关注"
                status_emoji = "🔴"
            
            return {
                'health_score': health_score,
                'status': status,
                'status_emoji': status_emoji,
                'issues': health_issues,
                'critical_alerts': critical_alerts,
                'warning_alerts': warning_alerts,
                'assessment_time': time.time()
            }
            
        except Exception as e:
            logger.error(f"评估系统健康状态失败: {e}")
            return {
                'health_score': 0,
                'status': "评估失败",
                'status_emoji': "❌",
                'error': str(e)
            }
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        try:
            recommendations = []
            current_metrics = self.performance_monitor.get_current_metrics()
            
            # CPU优化建议
            if current_metrics.cpu_usage > 80:
                recommendations.append("考虑优化CPU密集型操作或增加计算资源")
            
            # 内存优化建议
            if current_metrics.memory_usage_percent > 85:
                recommendations.append("检查内存泄漏，考虑增加内存或优化内存使用")
            
            # 缓存优化建议
            if current_metrics.cache_hit_rate < 0.7:
                recommendations.append("优化缓存策略，检查缓存键设计和过期策略")
            
            # 性能优化建议
            if current_metrics.avg_query_time_ms > 500:
                recommendations.append("优化查询性能，检查数据库索引和查询逻辑")
            
            # 错误处理建议
            if current_metrics.error_rate > 0.01:
                recommendations.append("检查错误日志，改进错误处理和系统稳定性")
            
            # 通用建议
            if not recommendations:
                recommendations.append("系统运行良好，建议定期监控和维护")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"生成优化建议失败: {e}")
            return ["无法生成建议，请检查监控系统"]