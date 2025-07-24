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
    
    # API路由
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