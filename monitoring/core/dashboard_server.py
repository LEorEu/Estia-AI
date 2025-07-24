#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能监控仪表板服务器
==================

提供基于Web的实时性能监控仪表板，展示系统性能指标、图表和告警信息。
"""

import json
import time
import threading
import logging
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socketserver

logger = logging.getLogger(__name__)


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """仪表板HTTP请求处理器"""
    
    def __init__(self, *args, dashboard_server=None, **kwargs):
        self.dashboard_server = dashboard_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            if path == '/' or path == '/dashboard':
                self._serve_dashboard()
            elif path == '/api/metrics':
                self._serve_metrics_api()
            elif path == '/api/history':
                self._serve_history_api(parsed_path.query)
            elif path == '/api/alerts':
                self._serve_alerts_api()
            elif path == '/api/summary':
                self._serve_summary_api()
            elif path.startswith('/static/'):
                self._serve_static_file(path)
            else:
                self._send_404()
                
        except Exception as e:
            logger.error(f"处理请求出错: {e}")
            self._send_500(str(e))
    
    def do_POST(self):
        """处理POST请求"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            if path == '/api/alerts/acknowledge':
                self._acknowledge_alerts()
            elif path == '/api/thresholds':
                self._update_thresholds()
            else:
                self._send_404()
                
        except Exception as e:
            logger.error(f"处理POST请求出错: {e}")
            self._send_500(str(e))
    
    def _serve_dashboard(self):
        """提供仪表板HTML页面"""
        html_content = self._generate_dashboard_html()
        self._send_response(200, html_content, 'text/html; charset=utf-8')
    
    def _serve_metrics_api(self):
        """提供当前指标API"""
        if self.dashboard_server and self.dashboard_server.performance_monitor:
            metrics = self.dashboard_server.performance_monitor.get_current_metrics()
            response_data = {
                'timestamp': metrics.timestamp,
                'cpu_usage': metrics.cpu_usage,
                'memory_usage_mb': metrics.memory_usage_mb,
                'memory_usage_percent': metrics.memory_usage_percent,
                'cache_hit_rate': metrics.cache_hit_rate,
                'active_sessions': metrics.active_sessions,
                'total_memories': metrics.total_memories,
                'avg_query_time_ms': metrics.avg_query_time_ms,
                'queries_per_second': metrics.queries_per_second,
                'error_rate': metrics.error_rate,
                'failed_operations': metrics.failed_operations
            }
        else:
            response_data = {'error': '性能监控器不可用'}
        
        self._send_json_response(response_data)
    
    def _serve_history_api(self, query_string):
        """提供历史数据API"""
        params = parse_qs(query_string)
        minutes = int(params.get('minutes', ['60'])[0])
        
        if self.dashboard_server and self.dashboard_server.performance_monitor:
            history = self.dashboard_server.performance_monitor.get_metrics_history(minutes)
            response_data = {
                'history': [
                    {
                        'timestamp': m.timestamp,
                        'cpu_usage': m.cpu_usage,
                        'memory_usage_percent': m.memory_usage_percent,
                        'cache_hit_rate': m.cache_hit_rate,
                        'avg_query_time_ms': m.avg_query_time_ms,
                        'queries_per_second': m.queries_per_second,
                        'error_rate': m.error_rate
                    } for m in history
                ]
            }
        else:
            response_data = {'error': '性能监控器不可用'}
        
        self._send_json_response(response_data)
    
    def _serve_alerts_api(self):
        """提供告警信息API"""
        if self.dashboard_server and self.dashboard_server.performance_monitor:
            alerts = self.dashboard_server.performance_monitor.check_alerts()
            response_data = {'alerts': alerts}
        else:
            response_data = {'error': '性能监控器不可用'}
        
        self._send_json_response(response_data)
    
    def _serve_summary_api(self):
        """提供性能摘要API"""
        if self.dashboard_server and self.dashboard_server.performance_monitor:
            summary = self.dashboard_server.performance_monitor.get_performance_summary()
            response_data = summary
        else:
            response_data = {'error': '性能监控器不可用'}
        
        self._send_json_response(response_data)
    
    def _send_response(self, status_code, content, content_type):
        """发送HTTP响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def _send_json_response(self, data):
        """发送JSON响应"""
        json_content = json.dumps(data, ensure_ascii=False, indent=2)
        self._send_response(200, json_content, 'application/json; charset=utf-8')
    
    def _send_404(self):
        """发送404响应"""
        self._send_response(404, '页面未找到', 'text/plain; charset=utf-8')
    
    def _send_500(self, error_msg):
        """发送500响应"""
        self._send_response(500, f'服务器内部错误: {error_msg}', 'text/plain; charset=utf-8')
    
    def _generate_dashboard_html(self):
        """生成仪表板HTML"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estia AI 性能监控仪表板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .header {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 10px;
        }
        .status-bar {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #27ae60;
        }
        .status-dot.warning { background: #f39c12; }
        .status-dot.error { background: #e74c3c; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 18px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
        }
        .metric:last-child { border-bottom: none; }
        .metric-label { color: #7f8c8d; }
        .metric-value { 
            font-weight: bold;
            color: #2c3e50;
        }
        .metric-value.good { color: #27ae60; }
        .metric-value.warning { color: #f39c12; }
        .metric-value.danger { color: #e74c3c; }
        .chart-container {
            height: 200px;
            margin-top: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #7f8c8d;
        }
        .alerts {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .alert {
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .alert.warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }
        .alert.critical {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .alert-icon {
            font-size: 18px;
        }
        .refresh-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }
        .refresh-btn:hover {
            background: #2980b9;
        }
        .auto-refresh {
            margin-left: 10px;
            color: #7f8c8d;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Estia AI 性能监控仪表板</h1>
            <div class="status-bar">
                <div class="status-item">
                    <div class="status-dot" id="systemStatus"></div>
                    <span id="systemStatusText">系统运行正常</span>
                </div>
                <div class="status-item">
                    <span id="lastUpdate">最后更新: --</span>
                </div>
                <button class="refresh-btn" onclick="refreshData()">🔄 刷新数据</button>
                <span class="auto-refresh" id="autoRefreshStatus">自动刷新: 开启</span>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📊 系统资源</h3>
                <div class="metric">
                    <span class="metric-label">CPU 使用率</span>
                    <span class="metric-value" id="cpuUsage">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">内存使用率</span>
                    <span class="metric-value" id="memoryUsage">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">内存使用量</span>
                    <span class="metric-value" id="memoryUsageMB">--</span>
                </div>
            </div>

            <div class="card">
                <h3>🧠 记忆系统</h3>
                <div class="metric">
                    <span class="metric-label">缓存命中率</span>
                    <span class="metric-value" id="cacheHitRate">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">活跃会话</span>
                    <span class="metric-value" id="activeSessions">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">总记忆数</span>
                    <span class="metric-value" id="totalMemories">--</span>
                </div>
            </div>

            <div class="card">
                <h3>⚡ 性能指标</h3>
                <div class="metric">
                    <span class="metric-label">平均查询时间</span>
                    <span class="metric-value" id="avgQueryTime">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">每秒查询数</span>
                    <span class="metric-value" id="queriesPerSecond">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">错误率</span>
                    <span class="metric-value" id="errorRate">--</span>
                </div>
            </div>

            <div class="card">
                <h3>📈 性能趋势</h3>
                <div class="chart-container">
                    <span>实时图表 (待实现)</span>
                </div>
            </div>
        </div>

        <div class="alerts" id="alertsSection">
            <h3>🚨 系统告警</h3>
            <div id="alertsList">
                <p style="color: #7f8c8d; text-align: center; padding: 20px;">暂无告警信息</p>
            </div>
        </div>
    </div>

    <script>
        let autoRefresh = true;
        let refreshInterval;

        function formatBytes(bytes) {
            return (bytes / 1024 / 1024).toFixed(1) + ' MB';
        }

        function formatPercent(value) {
            return (value * 100).toFixed(1) + '%';
        }

        function formatNumber(value, suffix = '') {
            return value.toFixed(1) + suffix;
        }

        function getMetricClass(value, thresholds) {
            if (value >= thresholds.danger) return 'danger';
            if (value >= thresholds.warning) return 'warning';
            return 'good';
        }

        function updateMetrics(data) {
            document.getElementById('cpuUsage').textContent = formatNumber(data.cpu_usage, '%');
            document.getElementById('cpuUsage').className = 'metric-value ' + 
                getMetricClass(data.cpu_usage, {warning: 70, danger: 85});

            document.getElementById('memoryUsage').textContent = formatNumber(data.memory_usage_percent, '%');
            document.getElementById('memoryUsage').className = 'metric-value ' + 
                getMetricClass(data.memory_usage_percent, {warning: 75, danger: 90});

            document.getElementById('memoryUsageMB').textContent = formatBytes(data.memory_usage_mb);
            
            document.getElementById('cacheHitRate').textContent = formatPercent(data.cache_hit_rate);
            document.getElementById('cacheHitRate').className = 'metric-value ' + 
                (data.cache_hit_rate >= 0.8 ? 'good' : data.cache_hit_rate >= 0.6 ? 'warning' : 'danger');

            document.getElementById('activeSessions').textContent = data.active_sessions;
            document.getElementById('totalMemories').textContent = data.total_memories;
            document.getElementById('avgQueryTime').textContent = formatNumber(data.avg_query_time_ms, 'ms');
            document.getElementById('queriesPerSecond').textContent = formatNumber(data.queries_per_second);
            document.getElementById('errorRate').textContent = formatPercent(data.error_rate);
            
            document.getElementById('lastUpdate').textContent = 
                '最后更新: ' + new Date().toLocaleTimeString();
        }

        function updateAlerts(alerts) {
            const alertsList = document.getElementById('alertsList');
            
            if (alerts.length === 0) {
                alertsList.innerHTML = '<p style="color: #7f8c8d; text-align: center; padding: 20px;">✅ 暂无告警信息</p>';
                document.getElementById('systemStatus').className = 'status-dot';
                document.getElementById('systemStatusText').textContent = '系统运行正常';
            } else {
                let alertsHtml = '';
                let hasWarning = false;
                let hasCritical = false;
                
                alerts.forEach(alert => {
                    const severity = alert.severity || 'warning';
                    if (severity === 'critical') hasCritical = true;
                    if (severity === 'warning') hasWarning = true;
                    
                    const icon = severity === 'critical' ? '🔴' : '⚠️';
                    alertsHtml += `
                        <div class="alert ${severity}">
                            <span class="alert-icon">${icon}</span>
                            <span>${alert.message}</span>
                        </div>
                    `;
                });
                
                alertsList.innerHTML = alertsHtml;
                
                if (hasCritical) {
                    document.getElementById('systemStatus').className = 'status-dot error';
                    document.getElementById('systemStatusText').textContent = '系统异常';
                } else if (hasWarning) {
                    document.getElementById('systemStatus').className = 'status-dot warning';
                    document.getElementById('systemStatusText').textContent = '系统告警';
                }
            }
        }

        async function refreshData() {
            try {
                // 获取当前指标
                const metricsResponse = await fetch('/api/metrics');
                const metricsData = await metricsResponse.json();
                
                if (!metricsData.error) {
                    updateMetrics(metricsData);
                }

                // 获取告警信息
                const alertsResponse = await fetch('/api/alerts');
                const alertsData = await alertsResponse.json();
                
                if (!alertsData.error) {
                    updateAlerts(alertsData.alerts || []);
                }

            } catch (error) {
                console.error('刷新数据失败:', error);
                document.getElementById('systemStatus').className = 'status-dot error';
                document.getElementById('systemStatusText').textContent = '连接失败';
            }
        }

        function startAutoRefresh() {
            if (refreshInterval) clearInterval(refreshInterval);
            refreshInterval = setInterval(refreshData, 5000); // 每5秒刷新
            document.getElementById('autoRefreshStatus').textContent = '自动刷新: 开启';
        }

        function stopAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
            document.getElementById('autoRefreshStatus').textContent = '自动刷新: 关闭';
        }

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            refreshData();
            startAutoRefresh();
        });

        // 页面隐藏时停止刷新，显示时恢复
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                stopAutoRefresh();
            } else {
                startAutoRefresh();
            }
        });
    </script>
</body>
</html>
        """

    def log_message(self, format, *args):
        """重写日志方法，避免控制台输出过多信息"""
        return


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """支持多线程的HTTP服务器"""
    allow_reuse_address = True


class DashboardServer:
    """
    性能监控仪表板服务器
    
    提供基于Web的实时性能监控界面，包括：
    - 实时系统指标显示
    - 性能图表和趋势
    - 告警信息展示
    - 历史数据查询
    """
    
    def __init__(self, performance_monitor=None, host='localhost', port=8080):
        """
        初始化仪表板服务器
        
        Args:
            performance_monitor: 性能监控器实例
            host: 服务器主机地址
            port: 服务器端口
        """
        self.performance_monitor = performance_monitor
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
        
        logger.info(f"📊 仪表板服务器初始化完成: http://{host}:{port}")
    
    def start(self):
        """启动仪表板服务器"""
        if self.running:
            logger.warning("仪表板服务器已在运行")
            return
        
        try:
            # 创建请求处理器工厂
            def handler_factory(*args, **kwargs):
                return DashboardRequestHandler(*args, dashboard_server=self, **kwargs)
            
            # 创建服务器
            self.server = ThreadedHTTPServer((self.host, self.port), handler_factory)
            
            # 启动服务器线程
            self.server_thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True,
                name="DashboardServer"
            )
            self.server_thread.start()
            
            self.running = True
            logger.info(f"📊 仪表板服务器已启动: http://{self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"启动仪表板服务器失败: {e}")
            raise
    
    def stop(self):
        """停止仪表板服务器"""
        if not self.running:
            return
        
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            if self.server_thread:
                self.server_thread.join(timeout=5)
            
            self.running = False
            logger.info("📊 仪表板服务器已停止")
            
        except Exception as e:
            logger.error(f"停止仪表板服务器失败: {e}")
    
    def is_running(self) -> bool:
        """检查服务器是否运行"""
        return self.running
    
    def get_dashboard_url(self) -> str:
        """获取仪表板URL"""
        return f"http://{self.host}:{self.port}/dashboard"