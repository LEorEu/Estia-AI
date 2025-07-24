#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时数据推送器
==============

定期检查监控桥接器的数据变化，通过WebSocket推送到前端界面。
"""

import time
import json
import threading
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RealtimeDataPusher:
    """
    实时数据推送器
    
    定期检查监控数据变化，通过WebSocket推送更新到前端。
    """
    
    def __init__(self, socketio, monitoring_system, push_interval: float = 2.0):
        """
        初始化推送器
        
        Args:
            socketio: Flask-SocketIO实例
            monitoring_system: 监控系统实例
            push_interval: 推送间隔(秒)
        """
        self.socketio = socketio
        self.monitoring_system = monitoring_system
        self.push_interval = push_interval
        self.running = False
        self.thread = None
        self.last_data = None
        
    def start(self):
        """启动实时推送"""
        if self.running:
            logger.warning("实时推送器已经在运行")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._push_loop, daemon=True)
        self.thread.start()
        logger.info(f"✅ 实时数据推送器已启动，推送间隔: {self.push_interval}s")
    
    def stop(self):
        """停止实时推送"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
            logger.info("✅ 实时数据推送器已停止")
    
    def _push_loop(self):
        """推送主循环"""
        logger.info("实时数据推送循环已开始")
        
        while self.running:
            try:
                # 获取最新监控数据
                current_data = self._get_monitoring_data()
                
                # 检查数据是否有变化
                if self._data_changed(current_data):
                    self._push_data(current_data)
                    self.last_data = current_data
                    logger.debug("监控数据已推送到WebSocket客户端")
                else:
                    logger.debug("监控数据无变化，跳过推送")
                
                # 定期推送心跳和连接状态
                self._push_heartbeat()
                
            except Exception as e:
                logger.error(f"推送数据时出错: {e}")
            
            # 等待下次推送
            time.sleep(self.push_interval)
    
    def _get_monitoring_data(self) -> Dict[str, Any]:
        """获取监控数据"""
        try:
            # 从监控系统获取数据
            if hasattr(self.monitoring_system, 'memory_monitor') and self.monitoring_system.memory_monitor:
                memory_interface = self.monitoring_system.memory_monitor
                
                # 获取各种监控数据
                comprehensive_stats = memory_interface.get_comprehensive_stats()
                real_time_metrics = memory_interface.get_real_time_metrics()
                step_monitoring = memory_interface.get_step_monitoring()
                
                # 获取系统指标（如果可用）
                system_metrics = {}
                if hasattr(self.monitoring_system, 'metrics_collector'):
                    try:
                        system_metrics = self.monitoring_system.metrics_collector.get_latest_metrics()
                    except:
                        pass
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'system_status': {
                        'running': comprehensive_stats.get('system_running', False),
                        'available': comprehensive_stats.get('available', False),
                        'current_session': comprehensive_stats.get('current_session'),
                        'uptime_seconds': comprehensive_stats.get('uptime_seconds', 0)
                    },
                    'performance_metrics': {
                        'total_queries': comprehensive_stats.get('total_queries', 0),
                        'cache_hit_rate': comprehensive_stats.get('cache_hit_rate', 0) * 100,
                        'avg_response_time_ms': comprehensive_stats.get('avg_response_time', 0) * 1000,
                        'queries_per_second': real_time_metrics.get('queries_per_second', 0),
                        'success_rate': real_time_metrics.get('success_rate', 0)
                    },
                    'real_time_metrics': real_time_metrics,
                    'step_monitoring': step_monitoring,
                    'system_metrics': system_metrics,
                    'connection_status': {
                        'websocket': 'connected',
                        'api': 'normal',
                        'data_source': 'real_data' if comprehensive_stats.get('available') else 'mock_data'
                    }
                }
                
        except Exception as e:
            logger.error(f"获取监控数据失败: {e}")
        
        # 返回默认数据
        return {
            'timestamp': datetime.now().isoformat(),
            'system_status': {
                'running': False,
                'available': False,
                'current_session': None,
                'uptime_seconds': 0
            },
            'performance_metrics': {
                'total_queries': 0,
                'cache_hit_rate': 0,
                'avg_response_time_ms': 0,
                'queries_per_second': 0,
                'success_rate': 0
            },
            'connection_status': {
                'websocket': 'connected',
                'api': 'normal',
                'data_source': 'no_data'
            }
        }
    
    def _data_changed(self, current_data: Dict[str, Any]) -> bool:
        """检查数据是否有变化"""
        if self.last_data is None:
            return True
        
        # 比较关键字段
        key_fields = [
            'system_status.running',
            'system_status.current_session',
            'performance_metrics.total_queries',
            'performance_metrics.cache_hit_rate',
            'performance_metrics.avg_response_time_ms'
        ]
        
        for field in key_fields:
            keys = field.split('.')
            current_val = current_data
            last_val = self.last_data
            
            try:
                for key in keys:
                    current_val = current_val[key]
                    last_val = last_val[key]
                
                if current_val != last_val:
                    return True
            except (KeyError, TypeError):
                return True
        
        return False
    
    def _push_data(self, data: Dict[str, Any]):
        """推送数据到WebSocket客户端"""
        try:
            # 推送系统状态更新
            self.socketio.emit('system_status_update', {
                'running': data['system_status']['running'],
                'current_session': data['system_status']['current_session'],
                'uptime_seconds': data['system_status']['uptime_seconds'],
                'timestamp': data['timestamp']
            })
            
            # 推送性能指标更新
            self.socketio.emit('performance_metrics_update', {
                'metrics': data['performance_metrics'],
                'timestamp': data['timestamp']
            })
            
            # 推送连接状态更新
            self.socketio.emit('connection_status_update', {
                'status': data['connection_status'],
                'timestamp': data['timestamp']
            })
            
            # 推送完整数据更新
            self.socketio.emit('monitoring_data_update', data)
            
        except Exception as e:
            logger.error(f"推送WebSocket数据失败: {e}")
    
    def _push_heartbeat(self):
        """推送心跳信号"""
        try:
            heartbeat_data = {
                'timestamp': datetime.now().isoformat(),
                'pusher_status': 'running',
                'clients_connected': len(self.socketio.server.manager.rooms.get('/', {}).get('/', set()))
            }
            
            self.socketio.emit('heartbeat', heartbeat_data)
            
        except Exception as e:
            logger.debug(f"推送心跳失败: {e}")
    
    def force_push(self):
        """强制推送一次数据"""
        try:
            current_data = self._get_monitoring_data()
            self._push_data(current_data)
            self.last_data = current_data
            logger.info("已强制推送监控数据")
        except Exception as e:
            logger.error(f"强制推送失败: {e}")


def create_realtime_pusher(socketio, monitoring_system, push_interval: float = 2.0) -> RealtimeDataPusher:
    """
    创建实时数据推送器
    
    Args:
        socketio: Flask-SocketIO实例
        monitoring_system: 监控系统实例
        push_interval: 推送间隔(秒)
        
    Returns:
        RealtimeDataPusher: 推送器实例
    """
    return RealtimeDataPusher(socketio, monitoring_system, push_interval)