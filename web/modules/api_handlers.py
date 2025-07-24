#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API处理器模块
=============

从web_dashboard.py中提取的API路由处理逻辑，
使代码更清晰、更易维护。
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)


class APIHandlers:
    """API处理器类，封装所有API端点的处理逻辑"""
    
    def __init__(self, monitor=None, analytics=None, performance_optimizer=None):
        """
        初始化API处理器
        
        Args:
            monitor: 监控系统实例
            analytics: 分析器实例  
            performance_optimizer: 性能优化器实例
        """
        self.monitor = monitor
        self.analytics = analytics
        self.performance_optimizer = performance_optimizer
        
    def get_status(self):
        """获取系统状态"""
        try:
            # 检查缓存
            if self.performance_optimizer:
                cached_data = self.performance_optimizer.data_cache.get('status')
                if cached_data:
                    return jsonify(cached_data)

            # 获取状态数据
            status = self.analytics.get_real_time_status() if self.analytics else {}
            summary = self.monitor.get_performance_summary() if self.monitor else {}

            result = {
                'status': status,
                'summary': summary,
                'timestamp': datetime.now().isoformat()
            }

            # 缓存结果
            if self.performance_optimizer:
                self.performance_optimizer.data_cache.set('status', result)
            
            return jsonify(result)

        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return jsonify({
                'error': f'获取状态失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500

    def get_performance(self):
        """获取性能数据"""
        try:
            if not self.monitor or not hasattr(self.monitor, 'completed_sessions'):
                return jsonify({'error': '监控系统未初始化或暂无数据'}), 503
                
            if len(self.monitor.completed_sessions) == 0:
                return jsonify({'error': '暂无性能数据'}), 404

            # 检查缓存
            if (self.performance_optimizer and 
                not self.performance_optimizer.should_update_data('performance')):
                cached_data = self.performance_optimizer.data_cache.get('performance')
                if cached_data:
                    return jsonify(cached_data)

            # 生成性能报告
            report = self.analytics.generate_performance_report() if self.analytics else None
            bottlenecks = self.analytics.analyze_bottlenecks() if self.analytics else None

            # 转换为字典格式
            result = {
                'report': self._convert_to_dict(report),
                'bottlenecks': self._convert_to_dict(bottlenecks),
                'timestamp': datetime.now().isoformat()
            }

            # 缓存结果
            if self.performance_optimizer:
                self.performance_optimizer.data_cache.set('performance', result)
                self.performance_optimizer.update_session_tracking()

            return jsonify(result)

        except Exception as e:
            logger.error(f"获取性能数据失败: {e}")
            return jsonify({
                'error': f'获取性能数据失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500

    def get_sessions(self):
        """获取会话列表"""
        try:
            if not self.monitor or not hasattr(self.monitor, 'completed_sessions'):
                return jsonify({
                    'sessions': [],
                    'total': 0,
                    'timestamp': datetime.now().isoformat(),
                    'message': '监控系统未初始化'
                }), 503

            sessions = self.monitor.completed_sessions
            if not sessions:
                return jsonify({
                    'sessions': [],
                    'total': 0,
                    'timestamp': datetime.now().isoformat(),
                    'message': '暂无会话数据'
                })

            # 检查缓存
            if (self.performance_optimizer and 
                not self.performance_optimizer.should_update_data('sessions')):
                cached_data = self.performance_optimizer.data_cache.get('sessions')
                if cached_data:
                    return jsonify(cached_data)

            # 处理会话数据（最近20个）
            recent_sessions = sessions[-20:]
            session_data = []
            
            for session in recent_sessions:
                session_info = {
                    'session_id': getattr(session, 'session_id', '未知'),
                    'start_time': datetime.fromtimestamp(
                        getattr(session, 'start_time', time.time())
                    ).isoformat(),
                    'duration': getattr(session, 'total_duration', 0) or 0,
                    'success_count': getattr(session, 'success_count', 0),
                    'failed_count': getattr(session, 'failed_count', 0),
                    'user_input': self._truncate_text(
                        getattr(session, 'user_input', ''), 100
                    ),
                    'ai_response': self._truncate_text(
                        getattr(session, 'ai_response', ''), 100
                    )
                }
                session_data.append(session_info)

            result = {
                'sessions': session_data,
                'total': len(sessions),
                'timestamp': datetime.now().isoformat()
            }

            # 缓存结果
            if self.performance_optimizer:
                self.performance_optimizer.data_cache.set('sessions', result)
                self.performance_optimizer.update_session_tracking()

            return jsonify(result)

        except Exception as e:
            logger.error(f"获取会话列表失败: {e}")
            return jsonify({
                'error': f'获取会话列表失败: {str(e)}',
                'sessions': [],
                'total': 0,
                'timestamp': datetime.now().isoformat()
            }), 500

    def get_health_check(self):
        """API健康检查"""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'monitor_available': self.monitor is not None,
            'monitor_type': type(self.monitor).__name__ if self.monitor else 'None',
            'analytics_available': self.analytics is not None
        })

    def get_session_context(self, session_id: str):
        """获取会话上下文详情"""
        try:
            if not self.monitor:
                return jsonify({
                    'error': '监控系统未初始化',
                    'timestamp': datetime.now().isoformat()
                }), 503

            # 查找会话
            sessions = getattr(self.monitor, 'completed_sessions', [])
            target_session = self._find_session(sessions, session_id)
            
            if not target_session:
                return jsonify({
                    'error': f'会话 {session_id} 未找到',
                    'available_sessions': [
                        getattr(s, 'session_id', '未知') for s in sessions[:10]
                    ]
                }), 404

            # 提取上下文数据
            context_data = self._extract_context_data(target_session, session_id)
            return jsonify(context_data)

        except Exception as e:
            logger.error(f"获取会话上下文失败: {e}")
            return jsonify({
                'error': f'获取会话上下文失败: {str(e)}',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }), 500

    def _convert_to_dict(self, obj):
        """将对象转换为字典"""
        if obj is None:
            return {}
        
        try:
            import dataclasses
            if dataclasses.is_dataclass(obj):
                return dataclasses.asdict(obj)
            return obj if isinstance(obj, dict) else str(obj)
        except:
            return str(obj)

    def _truncate_text(self, text: str, max_length: int) -> str:
        """截断文本"""
        if not text:
            return ''
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length] + '...'

    def _find_session(self, sessions, session_id: str):
        """查找指定会话"""
        for session in sessions:
            if hasattr(session, 'session_id') and session.session_id == session_id:
                return session
        return None

    def _extract_context_data(self, session, session_id: str) -> Dict[str, Any]:
        """提取会话上下文数据"""
        # 这里简化实现，实际项目中会更复杂
        return {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'preprocessing': {},
            'memory_retrieval': {},
            'history_aggregation': {},
            'final_context': {},
            'message': '上下文数据提取功能正在重构中'
        }


def create_api_blueprint(monitor=None, analytics=None, performance_optimizer=None) -> Blueprint:
    """创建API蓝图"""
    
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    handlers = APIHandlers(monitor, analytics, performance_optimizer)
    
    # 注册路由
    api_bp.add_url_rule('/status', 'status', handlers.get_status, methods=['GET'])
    api_bp.add_url_rule('/performance', 'performance', handlers.get_performance, methods=['GET'])
    api_bp.add_url_rule('/sessions', 'sessions', handlers.get_sessions, methods=['GET'])
    api_bp.add_url_rule('/health', 'health', handlers.get_health_check, methods=['GET'])
    api_bp.add_url_rule('/session/<session_id>/context', 'session_context', 
                       handlers.get_session_context, methods=['GET'])
    
    logger.info("✅ API蓝图创建完成")
    return api_bp