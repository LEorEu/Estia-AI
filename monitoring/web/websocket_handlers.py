#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一监控系统WebSocket处理器
============================

为统一监控系统提供WebSocket实时通信功能。
"""

import logging
from flask_socketio import emit
from flask import request

logger = logging.getLogger(__name__)


def setup_websocket_events(socketio, monitoring_system):
    """
    设置WebSocket事件处理器
    
    Args:
        socketio: SocketIO实例
        monitoring_system: 监控系统实例
    """
    
    @socketio.on('connect')
    def handle_connect():
        """处理WebSocket连接"""
        sid = request.sid
        logger.info(f"🔗 WebSocket客户端连接: {sid}")
        
        emit('connection_status', {
            'status': 'connected',
            'message': '已连接到Estia统一监控系统',
            'system_info': {
                'name': monitoring_system.config.system_name,
                'version': monitoring_system.config.version
            }
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """处理WebSocket断开"""
        sid = request.sid
        logger.info(f"🔌 WebSocket客户端断开: {sid}")
    
    @socketio.on('subscribe_system_status')
    def handle_subscribe_status():
        """订阅系统状态更新"""
        try:
            status = monitoring_system.get_system_status()
            emit('system_status_update', status)
            logger.debug(f"📊 发送系统状态: {request.sid}")
        except Exception as e:
            emit('error', {'message': f'获取系统状态失败: {e}'})
    
    @socketio.on('subscribe_metrics')
    def handle_subscribe_metrics():
        """订阅指标更新"""
        try:
            metrics = monitoring_system.metrics_collector.get_all_current_metrics()
            emit('metrics_update', metrics)
            logger.debug(f"📈 发送指标数据: {request.sid}")
        except Exception as e:
            emit('error', {'message': f'获取指标失败: {e}'})
    
    @socketio.on('subscribe_alerts')
    def handle_subscribe_alerts():
        """订阅告警更新"""
        try:
            alerts = monitoring_system.alert_manager.get_active_alerts()
            alert_data = [
                {
                    'alert_id': alert.alert_id,
                    'rule_name': alert.rule.name,
                    'severity': alert.rule.severity.value,
                    'message': alert.message,
                    'status': alert.status.value
                }
                for alert in alerts
            ]
            emit('alerts_update', {'alerts': alert_data})
            logger.debug(f"🚨 发送告警数据: {request.sid}")
        except Exception as e:
            emit('error', {'message': f'获取告警失败: {e}'})
    
    @socketio.on('get_comprehensive_data')
    def handle_get_comprehensive_data():
        """获取综合数据"""
        try:
            data = monitoring_system.get_comprehensive_data()
            emit('comprehensive_data_update', data)
            logger.debug(f"📊 发送综合数据: {request.sid}")
        except Exception as e:
            emit('error', {'message': f'获取综合数据失败: {e}'})
    
    logger.info("✅ WebSocket事件处理器设置完成")
