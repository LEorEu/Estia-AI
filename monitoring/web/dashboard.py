#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一监控仪表板
==============

整合所有Web功能的统一仪表板。
"""

import os
from flask import Flask, send_file, jsonify
from flask_socketio import SocketIO
from typing import Tuple

from .api_handlers import APIHandlers
from .websocket_handlers import setup_websocket_events
from ..config.monitoring_config import MonitoringConfig


def create_unified_dashboard(monitoring_system, config: MonitoringConfig) -> Tuple[Flask, SocketIO]:
    """
    创建统一的监控仪表板
    
    Args:
        monitoring_system: 监控系统实例
        config: 配置对象
        
    Returns:
        Tuple[Flask, SocketIO]: Flask应用和SocketIO实例
    """
    
    # 创建Flask应用
    app = Flask(__name__,
               template_folder=config.web.vue_dist_path,
               static_folder=config.web.vue_dist_path,
               static_url_path='')
    app.config['SECRET_KEY'] = 'estia_unified_monitoring_secret'
    
    # 创建SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # 创建API处理器
    api_handlers = APIHandlers(monitoring_system)
    
    # 注册路由
    _register_routes(app, api_handlers, config)
    
    # 设置WebSocket事件
    if config.websocket_enabled:
        setup_websocket_events(socketio, monitoring_system)
    
    return app, socketio


def _register_routes(app: Flask, api_handlers: APIHandlers, config: MonitoringConfig):
    """注册所有路由"""
    
    # API路由 (原版路径)
    @app.route('/api/status')
    def get_status():
        return api_handlers.get_system_status()
    
    @app.route('/api/health')
    def get_health():
        return api_handlers.get_health_check()
    
    @app.route('/api/dashboard_data')
    def get_dashboard_data():
        return api_handlers.get_comprehensive_data()
    
    @app.route('/api/metrics/current')
    def get_current_metrics():
        return api_handlers.get_current_metrics()
    
    @app.route('/api/metrics/history')
    def get_metrics_history():
        return api_handlers.get_metrics_history()
    
    @app.route('/api/alerts')
    def get_alerts():
        return api_handlers.get_active_alerts()
    
    @app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
    def acknowledge_alert(alert_id):
        return api_handlers.acknowledge_alert(alert_id)
    
    @app.route('/api/performance/summary')
    def get_performance_summary():
        return api_handlers.get_performance_summary()
    
    @app.route('/api/memory/stats')
    def get_memory_stats():
        return api_handlers.get_memory_system_stats()
    
    @app.route('/api/memory/step_monitoring')
    def get_step_monitoring():
        return api_handlers.get_step_monitoring()
    
    @app.route('/api/recommendations')
    def get_recommendations():
        return api_handlers.get_recommendations()
    
    @app.route('/api/pipeline/status')
    def get_pipeline_status():
        return api_handlers.get_pipeline_status()
    
    # 新增监控API路由 (Vue前端期望的路径)
    @app.route('/api/monitoring/status')
    def get_monitoring_status():
        return api_handlers.get_system_status()
    
    @app.route('/api/monitoring/health')
    def get_monitoring_health():
        # 临时调试：直接返回测试数据
        from flask import jsonify
        from datetime import datetime
        return jsonify({
            'success': True,
            'data': {
                'health_score': 95,
                'status': '优秀',
                'status_emoji': '🟢',
                'issues': [],
                'last_update': datetime.now().isoformat(),
                'debug': 'called_get_monitoring_health'
            },
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/monitoring/comprehensive')
    def get_monitoring_comprehensive():
        return api_handlers.get_comprehensive_data()
    
    @app.route('/api/monitoring/test')
    def test_monitoring_route():
        from flask import jsonify
        return jsonify({
            'message': 'test endpoint works',
            'route': '/api/monitoring/test'
        })
    
    @app.route('/api/monitoring/metrics/current')
    def get_monitoring_current_metrics():
        return api_handlers.get_current_metrics()
    
    @app.route('/api/monitoring/metrics/history')
    def get_monitoring_metrics_history():
        return api_handlers.get_metrics_history()
    
    @app.route('/api/monitoring/alerts')
    def get_monitoring_alerts():
        return api_handlers.get_active_alerts()
    
    @app.route('/api/monitoring/alerts/<alert_id>/acknowledge', methods=['POST'])
    def acknowledge_monitoring_alert(alert_id):
        return api_handlers.acknowledge_alert(alert_id)
    
    @app.route('/api/monitoring/performance/summary')
    def get_monitoring_performance_summary():
        return api_handlers.get_performance_summary()
    
    # 额外的Vue前端期望路径
    @app.route('/api/live_data')
    def get_live_data():
        return api_handlers.get_comprehensive_data()
    
    # Vue前端路由
    @app.route('/')
    def serve_vue_app():
        """服务Vue应用主页"""
        try:
            index_path = os.path.join(config.web.vue_dist_path, 'index.html')
            if os.path.exists(index_path):
                return send_file(index_path)
            else:
                return "Vue前端未构建，请运行: cd web-vue && npm run build", 404
        except Exception as e:
            return f"Vue前端不可用: {e}", 404

    @app.route('/<path:path>')
    def serve_vue_static(path):
        """服务Vue应用的静态资源和路由"""
        try:
            # 首先尝试作为静态文件
            file_path = os.path.join(config.web.vue_dist_path, path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return send_file(file_path)
            
            # 如果不是API路径且不是静态文件，返回index.html（用于Vue路由）
            if not path.startswith('api/') and not path.startswith('socket.io/'):
                index_path = os.path.join(config.web.vue_dist_path, 'index.html')
                if os.path.exists(index_path):
                    return send_file(index_path)
            
            return "Not Found", 404
            
        except Exception as e:
            return f"资源不可用: {e}", 404