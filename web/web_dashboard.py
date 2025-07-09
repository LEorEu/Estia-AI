#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estia 记忆监控 Web 仪表板
========================

基于Flask的实时监控可视化界面，包含：
- 实时流程监控
- 性能图表和分析
- 关键词云和趋势分析
- 记忆内容可视化
"""

import json
import time
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import threading

# 导入监控系统
from core.memory.monitoring import (
    MemoryPipelineMonitor,
    MemoryPipelineStep,
    StepStatus,
    MonitorAnalytics
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'estia_monitoring_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局监控实例
monitor = MemoryPipelineMonitor.get_instance()
analytics = MonitorAnalytics(monitor)


class KeywordAnalyzer:
    """关键词分析器"""
    
    def __init__(self):
        # 中文停用词
        self.stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '什么', '我们', '他们', '她们', '它们', '这个', '那个',
            '怎么', '为什么', '如何', '吗', '呢', '吧', '啊', '呀'
        }
        
        # 英文停用词
        self.stop_words.update({
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'me', 'him', 'her', 'us', 'them'
        })
    
    def extract_keywords(self, text: str, min_length: int = 2) -> List[str]:
        """提取关键词"""
        if not text:
            return []
        
        # 清理文本
        text = text.lower()
        # 保留中文、英文和数字
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        
        # 分词（简单的基于空格和标点的分词）
        words = text.split()
        
        # 过滤关键词
        keywords = []
        for word in words:
            word = word.strip()
            if (len(word) >= min_length and 
                word not in self.stop_words and
                not word.isdigit()):
                keywords.append(word)
        
        return keywords
    
    def analyze_keyword_trends(self, sessions: List) -> Dict[str, Any]:
        """分析关键词趋势"""
        keyword_counts = Counter()
        time_series = defaultdict(list)
        
        for session in sessions:
            if hasattr(session, 'user_input') and session.user_input:
                keywords = self.extract_keywords(session.user_input)
                
                for keyword in keywords:
                    keyword_counts[keyword] += 1
                    time_series[keyword].append(session.start_time)
            
            # 分析AI回复中的关键词
            if hasattr(session, 'ai_response') and session.ai_response:
                response_keywords = self.extract_keywords(session.ai_response)
                for keyword in response_keywords[:5]:  # 只取前5个避免过多
                    keyword_counts[f"回复_{keyword}"] += 1
        
        # 计算趋势
        trending_keywords = []
        for keyword, count in keyword_counts.most_common(20):
            if count >= 2:  # 至少出现2次
                trending_keywords.append({
                    'word': keyword,
                    'count': count,
                    'frequency': count / len(sessions) if sessions else 0
                })
        
        return {
            'top_keywords': trending_keywords,
            'total_unique_keywords': len(keyword_counts),
            'keyword_distribution': dict(keyword_counts.most_common(10))
        }


class MemoryContentAnalyzer:
    """记忆内容分析器"""
    
    def analyze_memory_patterns(self, sessions: List) -> Dict[str, Any]:
        """分析记忆模式"""
        memory_types = Counter()
        similarity_scores = []
        memory_usage = defaultdict(int)
        
        for session in sessions:
            for step, metrics in session.steps.items():
                if step == MemoryPipelineStep.STEP_5_FAISS_SEARCH:
                    # 分析检索结果
                    if 'avg_similarity' in metrics.metadata:
                        similarity_scores.append(metrics.metadata['avg_similarity'])
                    
                    if 'result_count' in metrics.metadata:
                        memory_usage['retrieved'] += metrics.metadata['result_count']
                
                elif step == MemoryPipelineStep.STEP_6_ASSOCIATION_EXPAND:
                    # 分析关联拓展
                    if 'expansion_count' in metrics.metadata:
                        memory_usage['associations'] += metrics.metadata['expansion_count']
                
                elif step == MemoryPipelineStep.STEP_9_CONTEXT_BUILD:
                    # 分析上下文构建
                    if 'memory_used' in metrics.metadata:
                        memory_usage['context_memories'] += metrics.metadata['memory_used']
        
        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
        
        return {
            'average_similarity': avg_similarity,
            'memory_usage_stats': dict(memory_usage),
            'total_retrievals': len(similarity_scores),
            'similarity_distribution': self._calculate_similarity_distribution(similarity_scores)
        }
    
    def _calculate_similarity_distribution(self, scores: List[float]) -> Dict[str, int]:
        """计算相似度分布"""
        if not scores:
            return {}
        
        bins = {'高 (>0.8)': 0, '中 (0.6-0.8)': 0, '低 (<0.6)': 0}
        
        for score in scores:
            if score > 0.8:
                bins['高 (>0.8)'] += 1
            elif score > 0.6:
                bins['中 (0.6-0.8)'] += 1
            else:
                bins['低 (<0.6)'] += 1
        
        return bins


# 初始化分析器
keyword_analyzer = KeywordAnalyzer()
memory_analyzer = MemoryContentAnalyzer()


@app.route('/')
def dashboard():
    """主仪表板页面"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """获取实时状态"""
    status = analytics.get_real_time_status()
    summary = monitor.get_performance_summary()
    
    return jsonify({
        'status': status,
        'summary': summary,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/performance')
def get_performance():
    """获取性能数据"""
    if len(monitor.completed_sessions) == 0:
        return jsonify({'error': '暂无数据'})
    
    report = analytics.generate_performance_report()
    bottlenecks = analytics.analyze_bottlenecks()
    
    # 转换为字典格式
    import dataclasses
    return jsonify({
        'report': dataclasses.asdict(report),
        'bottlenecks': dataclasses.asdict(bottlenecks),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/keywords')
def get_keywords():
    """获取关键词分析"""
    sessions = monitor.completed_sessions
    
    if not sessions:
        return jsonify({'error': '暂无数据'})
    
    keyword_data = keyword_analyzer.analyze_keyword_trends(sessions)
    
    return jsonify({
        'keywords': keyword_data,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/memory_analysis')
def get_memory_analysis():
    """获取记忆分析"""
    sessions = monitor.completed_sessions
    
    if not sessions:
        return jsonify({'error': '暂无数据'})
    
    memory_data = memory_analyzer.analyze_memory_patterns(sessions)
    
    return jsonify({
        'memory': memory_data,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/sessions')
def get_sessions():
    """获取会话列表"""
    sessions = monitor.completed_sessions[-20:]  # 最近20个会话
    
    session_data = []
    for session in sessions:
        session_info = {
            'session_id': session.session_id,
            'start_time': datetime.fromtimestamp(session.start_time).isoformat(),
            'duration': session.total_duration or 0,
            'success_count': session.success_count,
            'failed_count': session.failed_count,
            'user_input': session.user_input or '',
            'ai_response': (session.ai_response or '')[:100] + '...' if session.ai_response and len(session.ai_response) > 100 else session.ai_response or ''
        }
        session_data.append(session_info)
    
    return jsonify({
        'sessions': session_data,
        'total': len(monitor.completed_sessions),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/step_details/<step_name>')
def get_step_details(step_name):
    """获取特定步骤的详细信息"""
    step_data = []
    
    for session in monitor.completed_sessions:
        for step, metrics in session.steps.items():
            if step.value == step_name:
                step_info = {
                    'session_id': session.session_id,
                    'duration': metrics.duration or 0,
                    'status': metrics.status.value,
                    'input_size': metrics.input_size or 0,
                    'output_size': metrics.output_size or 0,
                    'metadata': metrics.metadata,
                    'timestamp': datetime.fromtimestamp(metrics.start_time).isoformat()
                }
                step_data.append(step_info)
    
    return jsonify({
        'step_name': step_name,
        'executions': step_data,
        'count': len(step_data),
        'timestamp': datetime.now().isoformat()
    })


@socketio.on('connect')
def handle_connect():
    """WebSocket连接处理"""
    print('客户端已连接')
    emit('message', {'data': '监控连接已建立'})


@socketio.on('start_monitoring')
def handle_start_monitoring():
    """开始实时监控"""
    print('开始实时监控')
    
    def monitoring_loop():
        while True:
            try:
                # 获取实时状态
                status = analytics.get_real_time_status()
                summary = monitor.get_performance_summary()
                
                # 发送实时数据
                socketio.emit('status_update', {
                    'status': status,
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                })
                
                time.sleep(2)  # 每2秒更新一次
                
            except Exception as e:
                print(f"监控循环错误: {e}")
                break
    
    # 在后台线程中运行监控
    monitoring_thread = threading.Thread(target=monitoring_loop)
    monitoring_thread.daemon = True
    monitoring_thread.start()


# 创建HTML模板
def create_dashboard_template():
    """创建仪表板HTML模板"""
    template_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estia 记忆监控仪表板</title>
    
    <!-- 引入Chart.js和其他依赖 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/socket.io-client@4.0.0/dist/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/wordcloud@1.2.2/src/wordcloud2.js"></script>
    
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .header {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        
        .header h1 {
            color: white;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: rgba(255,255,255,0.8);
            font-size: 1.2em;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .card h3 {
            color: #4a5568;
            margin-bottom: 20px;
            font-size: 1.3em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-running { background: #48bb78; }
        .status-idle { background: #a0aec0; }
        .status-error { background: #f56565; }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .metric:last-child { border-bottom: none; }
        
        .metric-value {
            font-weight: bold;
            color: #2d3748;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        
        .wordcloud-container {
            height: 300px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .session-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .session-item {
            padding: 15px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin-bottom: 10px;
            background: #f8f9fa;
        }
        
        .session-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .session-id { 
            font-family: monospace;
            color: #6b7280;
            font-size: 0.9em;
        }
        
        .session-duration {
            color: #059669;
            font-weight: bold;
        }
        
        .session-query {
            color: #374151;
            font-style: italic;
            margin-bottom: 5px;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #4299e1;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 15px 25px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(66,153,225,0.4);
            transition: all 0.3s ease;
        }
        
        .refresh-btn:hover {
            background: #3182ce;
            transform: translateY(-2px);
        }
        
        .alert {
            padding: 12px;
            border-radius: 6px;
            margin: 10px 0;
            border-left: 4px solid;
        }
        
        .alert-warning {
            background: #fef5e7;
            border-color: #f6ad55;
            color: #c53030;
        }
        
        .alert-info {
            background: #ebf8ff;
            border-color: #4299e1;
            color: #2b6cb0;
        }
        
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 2em; }
            .container { padding: 10px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Estia 记忆监控仪表板</h1>
        <p class="subtitle">13步记忆处理流程实时监控与分析</p>
    </div>
    
    <div class="container">
        <div class="grid">
            <!-- 实时状态卡片 -->
            <div class="card">
                <h3>📊 实时状态</h3>
                <div id="status-content">
                    <div class="metric">
                        <span>系统状态</span>
                        <span class="metric-value">
                            <span class="status-indicator status-idle"></span>
                            <span id="system-status">加载中...</span>
                        </span>
                    </div>
                    <div class="metric">
                        <span>当前会话</span>
                        <span class="metric-value" id="current-session">无</span>
                    </div>
                    <div class="metric">
                        <span>运行时间</span>
                        <span class="metric-value" id="runtime">0s</span>
                    </div>
                    <div class="metric">
                        <span>进度</span>
                        <span class="metric-value" id="progress">0%</span>
                    </div>
                </div>
            </div>
            
            <!-- 性能统计卡片 -->
            <div class="card">
                <h3>📈 性能统计</h3>
                <div id="performance-content">
                    <div class="metric">
                        <span>总会话数</span>
                        <span class="metric-value" id="total-sessions">0</span>
                    </div>
                    <div class="metric">
                        <span>平均耗时</span>
                        <span class="metric-value" id="avg-duration">0s</span>
                    </div>
                    <div class="metric">
                        <span>成功率</span>
                        <span class="metric-value" id="success-rate">0%</span>
                    </div>
                    <div class="metric">
                        <span>最慢步骤</span>
                        <span class="metric-value" id="slowest-step">无</span>
                    </div>
                </div>
            </div>
            
            <!-- 关键词云 -->
            <div class="card">
                <h3>☁️ 关键词云</h3>
                <div class="wordcloud-container" id="wordcloud"></div>
                <div id="keyword-stats" style="margin-top: 15px;">
                    <div class="metric">
                        <span>热门词汇</span>
                        <span class="metric-value" id="top-keywords">加载中...</span>
                    </div>
                </div>
            </div>
            
            <!-- 性能趋势图 -->
            <div class="card">
                <h3>📊 性能趋势</h3>
                <div class="chart-container">
                    <canvas id="performance-chart"></canvas>
                </div>
            </div>
            
            <!-- 记忆分析 -->
            <div class="card">
                <h3>🧠 记忆分析</h3>
                <div id="memory-analysis">
                    <div class="metric">
                        <span>平均相似度</span>
                        <span class="metric-value" id="avg-similarity">0</span>
                    </div>
                    <div class="metric">
                        <span>检索次数</span>
                        <span class="metric-value" id="retrieval-count">0</span>
                    </div>
                    <div class="metric">
                        <span>关联拓展</span>
                        <span class="metric-value" id="associations-count">0</span>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="memory-chart"></canvas>
                </div>
            </div>
            
            <!-- 最近会话 -->
            <div class="card">
                <h3>💬 最近会话</h3>
                <div class="session-list" id="session-list">
                    <p>加载中...</p>
                </div>
            </div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="refreshAllData()">
        🔄 刷新数据
    </button>
    
    <script>
        // WebSocket连接
        const socket = io();
        
        // 图表实例
        let performanceChart, memoryChart;
        
        // 初始化图表
        function initCharts() {
            // 性能趋势图
            const perfCtx = document.getElementById('performance-chart').getContext('2d');
            performanceChart = new Chart(perfCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '会话耗时 (秒)',
                        data: [],
                        borderColor: '#4299e1',
                        backgroundColor: 'rgba(66,153,225,0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
            
            // 记忆分析图
            const memCtx = document.getElementById('memory-chart').getContext('2d');
            memoryChart = new Chart(memCtx, {
                type: 'doughnut',
                data: {
                    labels: ['高相似度', '中相似度', '低相似度'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#48bb78', '#ed8936', '#f56565']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        // 更新状态显示
        function updateStatus(data) {
            const status = data.status;
            const summary = data.summary;
            
            // 更新系统状态
            const statusEl = document.getElementById('system-status');
            const indicatorEl = statusEl.previousElementSibling;
            
            if (status.status === 'running') {
                statusEl.textContent = '运行中';
                indicatorEl.className = 'status-indicator status-running';
            } else {
                statusEl.textContent = '空闲';
                indicatorEl.className = 'status-indicator status-idle';
            }
            
            // 更新其他信息
            document.getElementById('current-session').textContent = 
                status.session_id || '无';
            document.getElementById('runtime').textContent = 
                (status.running_time || 0).toFixed(2) + 's';
            document.getElementById('progress').textContent = 
                (status.progress_percentage || 0).toFixed(1) + '%';
            
            // 更新性能统计
            if (summary.total_sessions !== undefined) {
                document.getElementById('total-sessions').textContent = summary.total_sessions;
                document.getElementById('avg-duration').textContent = 
                    (summary.average_duration || 0).toFixed(3) + 's';
                document.getElementById('success-rate').textContent = 
                    ((summary.success_rate || 0) * 100).toFixed(1) + '%';
                
                const slowest = summary.slowest_step;
                document.getElementById('slowest-step').textContent = 
                    slowest && slowest.step ? 
                    `${slowest.step.split('_').pop()} (${(slowest.avg_duration || 0).toFixed(3)}s)` : '无';
            }
        }
        
        // 更新关键词云
        function updateWordCloud(keywords) {
            const container = document.getElementById('wordcloud');
            container.innerHTML = '';
            
            if (keywords && keywords.top_keywords && keywords.top_keywords.length > 0) {
                const wordList = keywords.top_keywords.map(item => [
                    item.word, Math.max(12, Math.min(40, item.count * 8))
                ]);
                
                WordCloud(container, {
                    list: wordList,
                    gridSize: 8,
                    weightFactor: 2,
                    fontFamily: 'Microsoft YaHei, sans-serif',
                    color: function() {
                        const colors = ['#4299e1', '#48bb78', '#ed8936', '#9f7aea', '#f56565'];
                        return colors[Math.floor(Math.random() * colors.length)];
                    },
                    rotateRatio: 0.2,
                    backgroundColor: '#f8f9fa'
                });
                
                // 更新热门关键词
                const topWords = keywords.top_keywords.slice(0, 3)
                    .map(item => item.word).join(', ');
                document.getElementById('top-keywords').textContent = topWords;
            } else {
                container.innerHTML = '<p style="text-align: center; margin-top: 100px; color: #a0aec0;">暂无关键词数据</p>';
                document.getElementById('top-keywords').textContent = '暂无数据';
            }
        }
        
        // 更新会话列表
        function updateSessionList(sessions) {
            const container = document.getElementById('session-list');
            
            if (!sessions || sessions.length === 0) {
                container.innerHTML = '<p>暂无会话数据</p>';
                return;
            }
            
            const html = sessions.map(session => `
                <div class="session-item">
                    <div class="session-header">
                        <span class="session-id">${session.session_id}</span>
                        <span class="session-duration">${session.duration.toFixed(3)}s</span>
                    </div>
                    <div class="session-query">"${session.user_input}"</div>
                    <div style="font-size: 0.9em; color: #6b7280;">
                        成功: ${session.success_count} | 失败: ${session.failed_count}
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = html;
        }
        
        // 刷新所有数据
        async function refreshAllData() {
            try {
                // 获取状态数据
                const statusRes = await fetch('/api/status');
                const statusData = await statusRes.json();
                updateStatus(statusData);
                
                // 获取关键词数据
                const keywordRes = await fetch('/api/keywords');
                if (keywordRes.ok) {
                    const keywordData = await keywordRes.json();
                    if (keywordData.keywords) {
                        updateWordCloud(keywordData.keywords);
                    }
                }
                
                // 获取会话数据
                const sessionRes = await fetch('/api/sessions');
                if (sessionRes.ok) {
                    const sessionData = await sessionRes.json();
                    updateSessionList(sessionData.sessions);
                    
                    // 更新性能图表
                    if (sessionData.sessions.length > 0) {
                        const labels = sessionData.sessions.map((_, i) => `会话${i+1}`);
                        const durations = sessionData.sessions.map(s => s.duration);
                        
                        performanceChart.data.labels = labels.slice(-10); // 最近10个
                        performanceChart.data.datasets[0].data = durations.slice(-10);
                        performanceChart.update();
                    }
                }
                
                // 获取记忆分析数据
                const memoryRes = await fetch('/api/memory_analysis');
                if (memoryRes.ok) {
                    const memoryData = await memoryRes.json();
                    if (memoryData.memory) {
                        const memory = memoryData.memory;
                        document.getElementById('avg-similarity').textContent = 
                            (memory.average_similarity || 0).toFixed(3);
                        document.getElementById('retrieval-count').textContent = 
                            memory.total_retrievals || 0;
                        document.getElementById('associations-count').textContent = 
                            memory.memory_usage_stats?.associations || 0;
                        
                        // 更新相似度分布图
                        if (memory.similarity_distribution) {
                            const dist = memory.similarity_distribution;
                            memoryChart.data.datasets[0].data = [
                                dist['高 (>0.8)'] || 0,
                                dist['中 (0.6-0.8)'] || 0,
                                dist['低 (<0.6)'] || 0
                            ];
                            memoryChart.update();
                        }
                    }
                }
                
            } catch (error) {
                console.error('刷新数据失败:', error);
            }
        }
        
        // WebSocket事件处理
        socket.on('connect', function() {
            console.log('连接到监控服务器');
            socket.emit('start_monitoring');
        });
        
        socket.on('status_update', function(data) {
            updateStatus(data);
        });
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            refreshAllData();
            
            // 定期刷新数据
            setInterval(refreshAllData, 5000); // 每5秒刷新一次
        });
    </script>
</body>
</html>
    """
    
    # 创建模板目录
    import os
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # 写入模板文件
    with open(os.path.join(template_dir, 'dashboard.html'), 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ 仪表板模板已创建")


def run_dashboard(host='127.0.0.1', port=5000, debug=True):
    """运行Web仪表板"""
    # 创建模板
    create_dashboard_template()
    
    print(f"🚀 启动 Estia 记忆监控仪表板")
    print(f"📊 访问地址: http://{host}:{port}")
    print(f"🔄 实时监控: WebSocket 连接已启用")
    print("="*60)
    
    # 启动Flask应用
    socketio.run(app, host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard() 