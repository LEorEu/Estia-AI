#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版监控仪表板
================

使用模块化架构的简化版本，演示如何重构现有的web_dashboard.py
这个文件可以完全替代原有的web_dashboard.py，但采用了更清晰的架构。

**安全特性：**
- 非侵入式设计，不影响核心记忆系统
- 模块化架构，易于维护和扩展
- 保持所有原有功能
- 支持渐进式迁移
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, send_file, jsonify
from flask_socketio import SocketIO

# 设置路径
sys.path.append('.')

# 导入模块化组件
from web.modules import (
    APIHandlers, create_api_blueprint,
    V6DataAdapter, DataCache, KeywordAnalyzer, MemoryContentAnalyzer,
    PerformanceOptimizer, BackgroundMonitor, create_test_data_generator,
    WebSocketHandlers, setup_websocket_events
)

# 导入现有的监控系统（保持兼容性）
try:
    from core.memory.managers.monitor_flow.monitoring import (
        MemoryPipelineMonitor, MonitorAnalytics
    )
    from web.live_data_connector import live_connector
    from web.monitoring_integration import (
        initialize_monitoring_system, get_monitoring_system,
        enhance_dashboard_data, register_monitoring_routes
    )
    MONITORING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 监控系统导入失败: {e}")
    MONITORING_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vue前端路径配置
vue_dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web-vue', 'dist')

# 创建Flask应用
app = Flask(__name__, 
           template_folder=vue_dist_path,
           static_folder=vue_dist_path,
           static_url_path='')
app.config['SECRET_KEY'] = 'estia_monitoring_secret_v2'

# 创建SocketIO实例
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局组件实例
monitor = None
analytics = None
performance_optimizer = None
background_monitor = None
websocket_handlers = None


def initialize_components():
    """初始化所有组件"""
    global monitor, analytics, performance_optimizer, background_monitor
    
    logger.info("🚀 开始初始化监控仪表板组件...")
    
    # 1. 初始化性能优化器
    performance_optimizer = PerformanceOptimizer(cache_ttl=3)
    logger.info("✅ 性能优化器初始化完成")
    
    # 2. 初始化监控组件（如果可用）
    if MONITORING_AVAILABLE:
        try:
            # 尝试获取现有监控器
            monitor = MemoryPipelineMonitor.get_instance()
            analytics = MonitorAnalytics(monitor) if monitor else None
            
            # 初始化增强监控系统
            enhanced_monitor = initialize_monitoring_system()
            if enhanced_monitor:
                register_monitoring_routes(app)
                logger.info("✅ 增强监控系统集成完成")
            
            logger.info("✅ 监控组件初始化完成")
            
        except Exception as e:
            logger.error(f"⚠️ 监控组件初始化失败: {e}")
            # 使用模拟监控器
            monitor = create_mock_monitor()
            analytics = create_mock_analytics(monitor)
    else:
        # 创建模拟组件用于演示
        monitor = create_mock_monitor()
        analytics = create_mock_analytics(monitor)
        logger.info("✅ 使用模拟监控组件")
    
    # 3. 初始化后台监控
    background_monitor = BackgroundMonitor(interval=5.0)
    
    # 添加后台任务
    def background_task():
        """后台更新任务"""
        try:
            # 这里可以添加定期任务，如缓存刷新、数据同步等
            pass
        except Exception as e:
            logger.error(f"后台任务错误: {e}")
    
    background_monitor.add_callback(background_task)
    background_monitor.start()
    logger.info("✅ 后台监控启动完成")
    
    logger.info("🎉 所有组件初始化完成")


def create_mock_monitor():
    """创建模拟监控器"""
    class MockMonitor:
        def __init__(self):
            self.completed_sessions = []
            self.active_sessions = {}
        
        def get_performance_summary(self):
            return {
                'total_sessions': 0,
                'average_duration': 0.0,
                'success_rate': 0.0,
                'slowest_step': None
            }
    
    return MockMonitor()


def create_mock_analytics(monitor):
    """创建模拟分析器"""
    class MockAnalytics:
        def __init__(self, monitor):
            self.monitor = monitor
        
        def get_real_time_status(self):
            return {
                'status': 'idle',
                'session_id': None,
                'running_time': 0,
                'progress_percentage': 0
            }
        
        def generate_performance_report(self):
            from dataclasses import dataclass
            @dataclass
            class MockReport:
                total_sessions: int = 0
                avg_duration: float = 0.0
                success_rate: float = 0.0
            return MockReport()
        
        def analyze_bottlenecks(self):
            from dataclasses import dataclass
            @dataclass
            class MockBottlenecks:
                slowest_steps: list = None
                avg_bottleneck_time: float = 0.0
            return MockBottlenecks()
    
    return MockAnalytics(monitor)


def setup_routes():
    """设置路由"""
    
    # 注册API蓝图
    api_blueprint = create_api_blueprint(monitor, analytics, performance_optimizer)
    app.register_blueprint(api_blueprint)
    
    # 添加额外的路由
    @app.route('/api/dashboard_data')
    def get_dashboard_data():
        """获取仪表板综合数据"""
        try:
            # 检查缓存
            if performance_optimizer:
                cached_data = performance_optimizer.data_cache.get('dashboard_batch')
                if cached_data:
                    return jsonify(cached_data)
            
            # 首先尝试获取实时数据
            if MONITORING_AVAILABLE and live_connector.check_system_running():
                logger.info("🔄 使用实时数据")
                return get_live_data()
            
            logger.info("⚠️ 使用模拟数据")
            
            # 使用测试数据生成器
            test_generator = create_test_data_generator()
            result = test_generator()
            
            # 缓存结果
            if performance_optimizer:
                performance_optimizer.data_cache.set('dashboard_batch', result)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"获取仪表板数据失败: {e}")
            return jsonify({
                'error': f'获取仪表板数据失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/api/live_data')
    def get_live_data():
        """获取实时数据"""
        try:
            if not MONITORING_AVAILABLE:
                return jsonify({
                    'error': '监控系统不可用',
                    'timestamp': datetime.now().isoformat()
                }), 503
                
            # 获取实时数据
            live_data = live_connector.get_comprehensive_data()
            
            if not live_data.get('system_running', False):
                return jsonify({
                    'error': 'Estia系统未运行',
                    'system_status': 'offline',
                    'timestamp': datetime.now().isoformat()
                }), 503
            
            # 处理实时数据（简化实现）
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'has_data': True,
                'live_mode': True,
                'data_source': 'live_system'
            }
            
            # 使用增强监控系统增强数据
            try:
                dashboard_data = enhance_dashboard_data(dashboard_data)
                logger.info("✅ 实时数据已增强")
            except Exception as e:
                logger.warning(f"数据增强失败: {e}")
            
            return jsonify(dashboard_data)
            
        except Exception as e:
            logger.error(f"获取实时数据失败: {e}")
            return jsonify({
                'error': f'获取实时数据失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500
    
    # Vue前端路由
    @app.route('/')
    def serve_vue_app():
        """服务Vue应用主页"""
        try:
            index_path = os.path.join(vue_dist_path, 'index.html')
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
            file_path = os.path.join(vue_dist_path, path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return send_file(file_path)
            
            # 如果不是API路径且不是静态文件，返回index.html（用于Vue路由）
            if not path.startswith('api/') and not path.startswith('socket.io/'):
                index_path = os.path.join(vue_dist_path, 'index.html')
                if os.path.exists(index_path):
                    return send_file(index_path)
            
            return "Not Found", 404
            
        except Exception as e:
            return f"资源不可用: {e}", 404
    
    logger.info("✅ 路由设置完成")


def setup_websockets():
    """设置WebSocket处理"""
    global websocket_handlers
    
    websocket_handlers = setup_websocket_events(
        socketio, monitor, analytics, performance_optimizer
    )
    
    logger.info("✅ WebSocket设置完成")


def run_dashboard(host='127.0.0.1', port=5000, debug=False):
    """运行仪表板"""
    
    print("🚀 启动 Estia AI 简化版监控仪表板")
    print("="*60)
    print(f"🏗️ 架构: 模块化设计 (非侵入式)")
    print(f"🌐 Vue前端 + Flask后端 集成服务")
    print(f"📊 主界面: http://{host}:{port}")
    print(f"⚡ 特性: 性能优化 + 智能缓存 + 实时推送")
    print(f"🔄 状态: {'监控系统可用' if MONITORING_AVAILABLE else '使用模拟数据'}")
    print()
    print("📡 主要API端点:")
    print(f"  • 仪表板数据: http://{host}:{port}/api/dashboard_data")
    print(f"  • 系统状态: http://{host}:{port}/api/status")
    print(f"  • 会话列表: http://{host}:{port}/api/sessions")
    print(f"  • 健康检查: http://{host}:{port}/api/health")
    if MONITORING_AVAILABLE:
        print(f"  • 监控状态: http://{host}:{port}/api/monitoring/status")
        print(f"  • 系统健康: http://{host}:{port}/api/monitoring/health")
    print()
    print("💡 模块化特性:")
    print("  ✅ 安全的非侵入式设计")
    print("  ✅ 智能性能优化和缓存")
    print("  ✅ 模块化API处理器")
    print("  ✅ WebSocket实时推送")
    print("  ✅ 后台监控任务")
    print("="*60)
    
    # 初始化所有组件
    initialize_components()
    
    # 设置路由和WebSocket
    setup_routes()
    setup_websockets()
    
    try:
        # 启动Flask-SocketIO服务器
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n👋 正在关闭仪表板...")
        
        # 清理资源
        if background_monitor:
            background_monitor.stop()
        if performance_optimizer:
            performance_optimizer.shutdown()
        
        print("✅ 仪表板已安全关闭")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 提示:")
        print("  - 检查端口5000是否被占用")
        print("  - 确保Vue前端已构建: cd web-vue && npm run build")
        print("  - 检查Python依赖: pip install flask flask-socketio")


if __name__ == '__main__':
    run_dashboard(debug=False)