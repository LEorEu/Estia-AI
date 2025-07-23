#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控系统集成模块
================

将新的性能监控系统集成到现有的Flask Web仪表板中，
为Vue前端提供完整的监控数据API。
"""

import json
import time
import threading
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import Blueprint, jsonify, request

# 导入新的监控系统
from core.monitoring.memory_integration import MemorySystemMonitor
from core.monitoring.performance_monitor import PerformanceMonitor
from core.monitoring.metrics_collector import MetricsCollector
from core.monitoring.alert_manager import AlertManager

logger = logging.getLogger(__name__)

# 创建蓝图
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')

# 全局监控系统实例
_monitoring_system: Optional[MemorySystemMonitor] = None
_monitoring_lock = threading.RLock()


def initialize_monitoring_system(memory_system=None):
    """
    初始化监控系统
    
    Args:
        memory_system: Estia记忆系统实例
    """
    global _monitoring_system
    
    try:
        with _monitoring_lock:
            if _monitoring_system is None:
                _monitoring_system = MemorySystemMonitor(
                    memory_system=memory_system,
                    enable_dashboard=False,  # 不启用独立仪表板
                    dashboard_port=8080
                )
                
                # 启动监控
                _monitoring_system.start_monitoring()
                
                logger.info("🚀 监控系统集成完成")
                
            return _monitoring_system
            
    except Exception as e:
        logger.error(f"监控系统初始化失败: {e}")
        return None


def get_monitoring_system() -> Optional[MemorySystemMonitor]:
    """获取监控系统实例"""
    return _monitoring_system


@monitoring_bp.route('/status', methods=['GET'])
def get_monitoring_status():
    """获取监控系统状态"""
    try:
        monitor = get_monitoring_system()
        if not monitor:
            return jsonify({
                'error': '监控系统未初始化',
                'status': 'offline',
                'timestamp': time.time()
            }), 503
        
        status = monitor.get_monitoring_status()
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"获取监控状态失败: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': time.time()
        }), 500


@monitoring_bp.route('/metrics/current', methods=['GET'])
def get_current_metrics():
    """获取当前性能指标"""
    try:
        monitor = get_monitoring_system()
        if not monitor:
            return jsonify({'error': '监控系统未初始化'}), 503
        
        # 获取当前指标
        current_metrics = monitor.performance_monitor.get_current_metrics()
        
        # 转换为API响应格式
        metrics_data = {
            'cpu_usage': current_metrics.cpu_usage,
            'memory_usage_mb': current_metrics.memory_usage_mb,
            'memory_usage_percent': current_metrics.memory_usage_percent,
            'cache_hit_rate': current_metrics.cache_hit_rate,
            'active_sessions': current_metrics.active_sessions,
            'total_memories': current_metrics.total_memories,
            'avg_query_time_ms': current_metrics.avg_query_time_ms,
            'avg_storage_time_ms': current_metrics.avg_storage_time_ms,
            'queries_per_second': current_metrics.queries_per_second,
            'error_rate': current_metrics.error_rate,
            'failed_operations': current_metrics.failed_operations,
            'timestamp': current_metrics.timestamp
        }
        
        return jsonify({
            'success': True,
            'data': metrics_data,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"获取当前指标失败: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/metrics/history', methods=['GET'])
def get_metrics_history():
    """获取指标历史数据"""
    try:
        monitor = get_monitoring_system()
        if not monitor:
            return jsonify({'error': '监控系统未初始化'}), 503
        
        # 获取查询参数
        minutes = request.args.get('minutes', 60, type=int)
        metric_name = request.args.get('metric', None)
        
        if metric_name:
            # 获取特定指标的历史
            history = monitor.metrics_collector.get_metric_history(metric_name, minutes)
            history_data = [
                {
                    'timestamp': point.timestamp,
                    'value': point.value,
                    'labels': point.labels
                }
                for point in history
            ]
        else:
            # 获取性能监控历史
            history = monitor.performance_monitor.get_metrics_history(minutes)
            history_data = [
                {
                    'timestamp': m.timestamp,
                    'cpu_usage': m.cpu_usage,
                    'memory_usage_percent': m.memory_usage_percent,
                    'cache_hit_rate': m.cache_hit_rate,
                    'avg_query_time_ms': m.avg_query_time_ms,
                    'queries_per_second': m.queries_per_second,
                    'error_rate': m.error_rate
                }
                for m in history
            ]
        
        return jsonify({
            'success': True,
            'data': {
                'history': history_data,
                'period_minutes': minutes,
                'metric_name': metric_name
            },
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"获取指标历史失败: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/alerts', methods=['GET'])
def get_active_alerts():
    """获取活跃告警"""
    try:
        monitor = get_monitoring_system()
        if not monitor:
            return jsonify({'error': '监控系统未初始化'}), 503
        
        # 获取活跃告警
        active_alerts = monitor.alert_manager.get_active_alerts()
        
        alerts_data = []
        for alert in active_alerts:
            alerts_data.append({
                'alert_id': alert.alert_id,
                'rule_id': alert.rule.rule_id,
                'rule_name': alert.rule.name,
                'description': alert.rule.description,
                'severity': alert.rule.severity.value,
                'metric_name': alert.rule.metric_name,
                'threshold': alert.rule.threshold,
                'current_value': alert.current_value,
                'message': alert.message,
                'status': alert.status.value,
                'triggered_at': alert.triggered_at,
                'acknowledged_at': alert.acknowledged_at,
                'acknowledged_by': alert.acknowledged_by,
                'trigger_count': alert.trigger_count
            })
        
        # 获取告警统计
        alert_stats = monitor.alert_manager.get_alert_statistics()
        
        return jsonify({
            'success': True,
            'data': {
                'active_alerts': alerts_data,
                'statistics': alert_stats
            },
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"获取告警信息失败: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """确认告警"""
    try:
        monitor = get_monitoring_system()
        if not monitor:
            return jsonify({'error': '监控系统未初始化'}), 503
        
        # 获取确认人信息
        data = request.get_json() or {}
        acknowledged_by = data.get('acknowledged_by', 'web_user')
        
        success = monitor.alert_manager.acknowledge_alert(alert_id, acknowledged_by)
        
        if success:
            return jsonify({
                'success': True,
                'message': '告警已确认',
                'timestamp': time.time()
            })
        else:
            return jsonify({
                'success': False,
                'error': '告警确认失败',
                'timestamp': time.time()
            }), 400
        
    except Exception as e:
        logger.error(f"确认告警失败: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/performance/summary', methods=['GET'])
def get_performance_summary():
    """获取性能摘要"""
    try:
        monitor = get_monitoring_system()
        if not monitor:
            return jsonify({'error': '监控系统未初始化'}), 503
        
        summary = monitor.performance_monitor.get_performance_summary()
        
        return jsonify({
            'success': True,
            'data': summary,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"获取性能摘要失败: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/health', methods=['GET'])
def get_system_health():
    """获取系统健康状态"""
    try:
        monitor = get_monitoring_system()
        if not monitor:
            return jsonify({
                'success': False,
                'data': {
                    'health_score': 0,
                    'status': '监控系统离线',
                    'status_emoji': '❌',
                    'issues': ['监控系统未初始化'],
                    'error': '监控系统不可用'
                },
                'timestamp': time.time()
            })
        
        # 获取综合报告中的健康状态
        report = monitor.get_comprehensive_report()
        health_status = report.get('health_status', {})
        
        return jsonify({
            'success': True,
            'data': health_status,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"获取系统健康状态失败: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/comprehensive', methods=['GET'])
def get_comprehensive_report():
    """获取综合监控报告"""
    try:
        monitor = get_monitoring_system()
        if not monitor:
            return jsonify({'error': '监控系统未初始化'}), 503
        
        report = monitor.get_comprehensive_report()
        
        return jsonify({
            'success': True,
            'data': report,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"获取综合报告失败: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/metrics/collector/stats', methods=['GET'])
def get_collector_stats():
    """获取指标收集器统计"""
    try:
        monitor = get_monitoring_system()
        if not monitor:
            return jsonify({'error': '监控系统未初始化'}), 503
        
        stats = monitor.metrics_collector.get_collection_stats()
        
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"获取收集器统计失败: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/operation/start', methods=['POST'])
def start_operation_monitoring():
    """开始操作监控"""
    try:
        monitor = get_monitoring_system()
        if not monitor:
            return jsonify({'error': '监控系统未初始化'}), 503
        
        data = request.get_json() or {}
        operation_name = data.get('operation_name', 'unknown_operation')
        metadata = data.get('metadata', {})
        
        # 这个端点主要用于外部系统开始监控操作
        # 实际的监控通过context manager在代码中进行
        
        return jsonify({
            'success': True,
            'message': f'操作监控已开始: {operation_name}',
            'operation_name': operation_name,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"开始操作监控失败: {e}")
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/export', methods=['GET'])
def export_monitoring_data():
    """导出监控数据"""
    try:
        monitor = get_monitoring_system()
        if not monitor:
            return jsonify({'error': '监控系统未初始化'}), 503
        
        # 获取导出格式
        format_type = request.args.get('format', 'json')
        
        if format_type == 'json':
            # 导出JSON格式
            export_data = {
                'export_time': time.time(),
                'system_status': monitor.get_monitoring_status(),
                'performance_summary': monitor.performance_monitor.get_performance_summary(),
                'current_metrics': monitor.performance_monitor.get_current_metrics().__dict__,
                'active_alerts': [
                    {
                        'alert_id': alert.alert_id,
                        'rule_name': alert.rule.name,
                        'severity': alert.rule.severity.value,
                        'message': alert.message,
                        'triggered_at': alert.triggered_at
                    }
                    for alert in monitor.alert_manager.get_active_alerts()
                ]
            }
            
            return jsonify({
                'success': True,
                'data': export_data,
                'format': 'json',
                'timestamp': time.time()
            })
        
        elif format_type == 'csv':
            # 导出CSV格式（通过MetricsCollector）
            csv_data = monitor.metrics_collector.export_metrics('csv')
            
            return jsonify({
                'success': True,
                'data': csv_data,
                'format': 'csv',
                'timestamp': time.time()
            })
        
        else:
            return jsonify({
                'success': False,
                'error': f'不支持的导出格式: {format_type}'
            }), 400
        
    except Exception as e:
        logger.error(f"导出监控数据失败: {e}")
        return jsonify({'error': str(e)}), 500


# 辅助函数：为现有API端点提供扩展数据
def enhance_dashboard_data(dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    增强现有的仪表板数据，添加新的监控指标
    
    Args:
        dashboard_data: 原始仪表板数据
        
    Returns:
        增强后的仪表板数据
    """
    try:
        monitor = get_monitoring_system()
        if not monitor:
            logger.warning("监控系统不可用，无法增강仪表板数据")
            return dashboard_data
        
        # 获取当前指标
        current_metrics = monitor.performance_monitor.get_current_metrics()
        
        # 添加系统性能指标
        if 'performance' not in dashboard_data:
            dashboard_data['performance'] = {}
        
        dashboard_data['performance'].update({
            'cpu_usage': current_metrics.cpu_usage,
            'memory_usage_percent': current_metrics.memory_usage_percent,
            'cache_hit_rate': current_metrics.cache_hit_rate,
            'avg_query_time_ms': current_metrics.avg_query_time_ms,
            'queries_per_second': current_metrics.queries_per_second,
            'error_rate': current_metrics.error_rate
        })
        
        # 添加系统健康状态
        report = monitor.get_comprehensive_report()
        health_status = report.get('health_status', {})
        
        dashboard_data['system_health'] = {
            'health_score': health_status.get('health_score', 0),
            'status': health_status.get('status', '未知'),
            'status_emoji': health_status.get('status_emoji', '❓')
        }
        
        # 添加活跃告警数量
        active_alerts = monitor.alert_manager.get_active_alerts()
        dashboard_data['alerts_summary'] = {
            'active_count': len(active_alerts),
            'critical_count': len([a for a in active_alerts if a.rule.severity.value == 'critical']),
            'warning_count': len([a for a in active_alerts if a.rule.severity.value == 'warning'])
        }
        
        # 添加推荐优化建议
        recommendations = report.get('recommendations', [])
        dashboard_data['recommendations'] = recommendations[:3]  # 只显示前3个建议
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"增强仪表板数据失败: {e}")
        return dashboard_data


def register_monitoring_routes(app):
    """
    注册监控路由到Flask应用
    
    Args:
        app: Flask应用实例
    """
    app.register_blueprint(monitoring_bp)
    logger.info("✅ 监控API路由已注册")


# 监控系统状态检查装饰器
def monitoring_required(f):
    """装饰器：检查监控系统是否可用"""
    def wrapper(*args, **kwargs):
        if not get_monitoring_system():
            return jsonify({
                'error': '监控系统不可用',
                'timestamp': time.time()
            }), 503
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper