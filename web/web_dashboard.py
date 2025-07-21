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
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import threading

# 导入监控系统
from core.memory.managers.monitor_flow.monitoring import (
    MemoryPipelineMonitor,
    MemoryPipelineStep,
    StepStatus,
    MonitorAnalytics
)

# 导入实时数据连接器
from .live_data_connector import live_connector

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = 'estia_monitoring_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局监控实例
try:
    monitor = MemoryPipelineMonitor.get_instance()
    analytics = MonitorAnalytics(monitor)
    print("✅ 监控系统初始化成功")

    # 检查是否有数据
    session_count = len(monitor.completed_sessions)
    print(f"📊 当前会话数量: {session_count}")

    if session_count == 0:
        print("⚠️ 暂无监控数据，将显示空状态")

except Exception as e:
    print(f"❌ 监控系统初始化失败: {e}")
    # 创建一个模拟的监控器用于测试
    class MockMonitor:
        def __init__(self):
            self.completed_sessions = []

        def get_performance_summary(self):
            return {
                'total_sessions': 0,
                'average_duration': 0.0,
                'success_rate': 0.0,
                'slowest_step': None
            }

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

    monitor = MockMonitor()
    analytics = MockAnalytics(monitor)
    print("🔄 使用模拟监控器")

# 尝试连接v6.0的MemoryFlowMonitor（增强错误处理）
flow_monitor = None
flow_monitor_error = None

try:
    from core.memory.managers.monitor_flow import MemoryFlowMonitor

    # 创建模拟的组件字典来初始化MemoryFlowMonitor
    # 在实际使用中，这些组件应该来自真实的v6.0系统
    mock_components = {
        'db_manager': None,  # 数据库管理器
        'unified_cache': None,  # 统一缓存
        'sync_flow_manager': None,  # 同步流程管理器
        'async_flow_manager': None  # 异步流程管理器
    }

    flow_monitor = MemoryFlowMonitor(mock_components)
    print("✅ v6.0 MemoryFlowMonitor 初始化成功")

    # 测试基本功能
    try:
        test_stats = flow_monitor.get_comprehensive_stats()
        if 'error' in test_stats:
            print(f"⚠️ v6.0监控器功能测试失败: {test_stats['error']}")
        else:
            print("✅ v6.0监控器功能测试通过")
    except Exception as test_error:
        print(f"⚠️ v6.0监控器功能测试异常: {test_error}")

except ImportError as e:
    flow_monitor_error = f"导入失败: {e}"
    print(f"⚠️ v6.0 MemoryFlowMonitor 导入失败: {e}")
except Exception as e:
    flow_monitor_error = f"初始化失败: {e}"
    print(f"⚠️ v6.0 MemoryFlowMonitor 初始化失败: {e}")


class FallbackMonitor:
    """降级监控器，当v6.0监控器不可用时使用"""

    def __init__(self):
        self.start_time = time.time()

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """提供基础的统计信息"""
        return {
            'timestamp': time.time(),
            'monitor_status': 'fallback',
            'performance_summary': {
                'cache_hit_rate': 0.0,
                'cache_efficiency': 0.0,
                'system_health': 'unknown'
            },
            'memory_overview': {
                'total_memories': 0,
                'active_sessions': 0
            },
            'session_statistics': {
                'total_sessions': 0,
                'avg_duration': 0.0
            },
            'health_status': {
                'status': 'degraded',
                'message': 'v6.0监控器不可用，使用降级模式'
            },
            'error': flow_monitor_error
        }

    def get_13_step_monitoring(self) -> Dict[str, Any]:
        """提供基础的步骤监控信息"""
        return {
            'error': 'v6.0监控器不可用',
            'fallback_mode': True,
            'message': '14步流程监控需要v6.0监控器支持'
        }

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """提供基础的实时指标"""
        return {
            'timestamp': time.time(),
            'cache_performance': {'status': 'unavailable'},
            'database_performance': {'status': 'unavailable'},
            'queue_status': {'status': 'unavailable'},
            'memory_usage': {'status': 'unavailable'},
            'error': 'v6.0监控器不可用'
        }


# 如果v6.0监控器不可用，使用降级监控器
if flow_monitor is None:
    flow_monitor = FallbackMonitor()
    print("🔄 启用降级监控模式")


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


class V6DataAdapter:
    """v6.0数据适配器，将v6.0监控数据转换为仪表板期望的格式（增强版）"""

    def __init__(self, flow_monitor):
        self.flow_monitor = flow_monitor
        self.is_fallback_mode = isinstance(flow_monitor, FallbackMonitor)

    def adapt_comprehensive_stats(self) -> Dict[str, Any]:
        """适配综合统计数据（增强错误处理）"""
        if not self.flow_monitor:
            return {'error': 'v6.0监控器不可用'}

        try:
            stats = self.flow_monitor.get_comprehensive_stats()

            # 检查是否是错误响应
            if 'error' in stats:
                return {
                    'error': stats['error'],
                    'fallback_mode': self.is_fallback_mode,
                    'timestamp': stats.get('timestamp', time.time())
                }

            # 转换为仪表板期望的格式
            adapted_stats = {
                'timestamp': stats.get('timestamp', time.time()),
                'monitor_status': stats.get('monitor_status', 'unknown'),
                'fallback_mode': self.is_fallback_mode,
                'performance_summary': {
                    'cache_hit_rate': stats.get('performance_metrics', {}).get('cache_hit_rate', 0),
                    'cache_efficiency': stats.get('performance_metrics', {}).get('cache_efficiency', 0),
                    'system_health': stats.get('health_status', {}).get('status', 'unknown')
                },
                'memory_overview': stats.get('memory_overview', {}),
                'session_stats': stats.get('session_statistics', {})
            }

            # 如果是降级模式，添加警告信息
            if self.is_fallback_mode:
                adapted_stats['warning'] = 'v6.0监控器不可用，显示降级数据'

            return adapted_stats

        except Exception as e:
            return {
                'error': f'适配综合统计失败: {str(e)}',
                'fallback_mode': self.is_fallback_mode,
                'timestamp': time.time()
            }
    
    def adapt_13_step_monitoring(self) -> Dict[str, Any]:
        """适配13步流程监控数据（修复版）"""
        if not self.flow_monitor:
            return {'error': 'v6.0监控器不可用'}

        try:
            step_data = self.flow_monitor.get_13_step_monitoring()

            # 转换为仪表板期望的格式
            if 'error' in step_data:
                return step_data

            # 修正步骤数量 - 实际是14步
            adapted_data = {
                'total_steps': step_data.get('total_steps', 14),
                'sync_steps': step_data.get('sync_steps', 9),  # Step 1-9
                'async_steps': step_data.get('async_steps', 5),  # Step 10-14
                'step_performance': step_data.get('overall_performance', {}),
                'step_details': step_data.get('step_details', {}),
                'timestamp': step_data.get('timestamp', 0)
            }

            # 添加步骤名称映射
            step_mapping = {
                'step_01_database_initialization': 'DB初始化',
                'step_02_component_initialization': '组件初始化',
                'step_03_async_evaluator_initialization': '异步评估器初始化',
                'step_04_unified_cache_vectorization': '缓存向量化',
                'step_05_faiss_vector_retrieval': 'FAISS检索',
                'step_06_association_network_expansion': '关联拓展',
                'step_07_history_dialogue_aggregation': '历史聚合',
                'step_08_weight_ranking_deduplication': '权重排序',
                'step_09_final_context_assembly': '上下文构建',
                'step_10_llm_response_generation': 'LLM生成',
                'step_11_immediate_dialogue_storage': '对话存储',
                'step_12_async_llm_evaluation': '异步评估',
                'step_13_save_evaluation_results': '保存结果',
                'step_14_auto_association_creation': '关联创建'
            }

            adapted_data['step_mapping'] = step_mapping

            return adapted_data

        except Exception as e:
            return {'error': f'适配13步监控失败: {str(e)}'}
    
    def adapt_real_time_metrics(self) -> Dict[str, Any]:
        """适配实时性能指标"""
        if not self.flow_monitor:
            return {'error': 'v6.0监控器不可用'}
        
        try:
            metrics = self.flow_monitor.get_real_time_metrics()
            
            # 转换为仪表板期望的格式
            if 'error' in metrics:
                return metrics
            
            adapted_metrics = {
                'cache_performance': metrics.get('cache_performance', {}),
                'database_performance': metrics.get('database_performance', {}),
                'queue_status': metrics.get('queue_status', {}),
                'memory_usage': metrics.get('memory_usage', {}),
                'timestamp': metrics.get('timestamp', 0)
            }
            
            return adapted_metrics
            
        except Exception as e:
            return {'error': f'适配实时指标失败: {str(e)}'}


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

# 初始化v6.0数据适配器
v6_adapter = V6DataAdapter(flow_monitor) if flow_monitor else None


class DataCache:
    """数据缓存管理器，减少重复计算和API调用"""

    def __init__(self, cache_ttl: int = 3):
        self.cache_ttl = cache_ttl  # 缓存生存时间（秒）
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key not in self._cache:
            return None

        # 检查是否过期
        if time.time() - self._timestamps[key] > self.cache_ttl:
            del self._cache[key]
            del self._timestamps[key]
            return None

        return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        """设置缓存数据"""
        self._cache[key] = value
        self._timestamps[key] = time.time()

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._timestamps.clear()


class PerformanceOptimizer:
    """性能优化器"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.data_cache = DataCache()
        self.last_session_count = 0
        self.last_update_time = 0

    def should_update_data(self, data_type: str) -> bool:
        """判断是否需要更新数据"""
        current_session_count = len(monitor.completed_sessions)
        current_time = time.time()

        # 如果会话数量没有变化且距离上次更新不到3秒，跳过更新
        if (data_type in ['sessions', 'keywords', 'memory'] and
            current_session_count == self.last_session_count and
            current_time - self.last_update_time < 3):
            return False

        return True

    def update_session_tracking(self):
        """更新会话跟踪信息"""
        self.last_session_count = len(monitor.completed_sessions)
        self.last_update_time = time.time()

    async def get_cached_or_compute(self, key: str, compute_func, *args, **kwargs):
        """获取缓存数据或计算新数据"""
        cached_data = self.data_cache.get(key)
        if cached_data is not None:
            return cached_data

        # 在线程池中执行计算
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, compute_func, *args, **kwargs)

        self.data_cache.set(key, result)
        return result


# 初始化性能优化器
performance_optimizer = PerformanceOptimizer()


@app.route('/')
def dashboard():
    """主仪表板页面"""
    return render_template('dashboard.html')


@app.route('/simple')
def simple_dashboard():
    """简化版仪表板页面"""
    return render_template('simple_dashboard.html')


@app.route('/fixed')
def fixed_dashboard():
    """修复版仪表板页面"""
    return render_template('dashboard_fixed.html')


@app.route('/api/status')
def get_status():
    """获取实时状态（优化版）"""
    # 检查缓存
    cached_data = performance_optimizer.data_cache.get('status')
    if cached_data:
        return jsonify(cached_data)

    try:
        status = analytics.get_real_time_status()
        summary = monitor.get_performance_summary()

        result = {
            'status': status,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }

        # 缓存结果
        performance_optimizer.data_cache.set('status', result)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'获取状态失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })


@app.route('/api/performance')
def get_performance():
    """获取性能数据（优化版）"""
    if len(monitor.completed_sessions) == 0:
        return jsonify({'error': '暂无数据'})

    # 检查是否需要更新
    if not performance_optimizer.should_update_data('performance'):
        cached_data = performance_optimizer.data_cache.get('performance')
        if cached_data:
            return jsonify(cached_data)

    try:
        report = analytics.generate_performance_report()
        bottlenecks = analytics.analyze_bottlenecks()

        # 转换为字典格式
        import dataclasses
        result = {
            'report': dataclasses.asdict(report),
            'bottlenecks': dataclasses.asdict(bottlenecks),
            'timestamp': datetime.now().isoformat()
        }

        # 缓存结果
        performance_optimizer.data_cache.set('performance', result)
        performance_optimizer.update_session_tracking()

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'获取性能数据失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })


@app.route('/api/dashboard_data')
def get_dashboard_data():
    """批量获取仪表板数据（优先使用实时数据）"""
    try:
        # 检查缓存
        cached_data = performance_optimizer.data_cache.get('dashboard_batch')
        if cached_data:
            return jsonify(cached_data)

        # 首先尝试获取实时数据
        if live_connector.check_system_running():
            print("🔄 检测到Estia系统正在运行，使用实时数据")
            return get_live_data()

        print("⚠️ Estia系统未运行，使用模拟监控数据")

        # 批量获取所有数据
        sessions = monitor.completed_sessions if hasattr(monitor, 'completed_sessions') else []
        result = {
            'timestamp': datetime.now().isoformat(),
            'has_data': len(sessions) > 0,
            'data_source': 'mock_monitor'
        }

        # 即使没有数据也返回空结构，而不是错误
        if len(sessions) == 0:
            result.update({
                'status': {
                    'status': analytics.get_real_time_status(),
                    'summary': monitor.get_performance_summary()
                },
                'keywords': {
                    'top_keywords': [],
                    'total_unique_keywords': 0,
                    'keyword_distribution': {}
                },
                'sessions': {
                    'sessions': [],
                    'total': 0
                },
                'memory': {
                    'average_similarity': 0,
                    'memory_usage_stats': {},
                    'total_retrievals': 0,
                    'similarity_distribution': {}
                }
            })
            return jsonify(result)

        # 状态数据
        try:
            status = analytics.get_real_time_status()
            summary = monitor.get_performance_summary()
            result['status'] = {'status': status, 'summary': summary}
        except Exception as e:
            result['status'] = {'error': str(e)}

        # 关键词数据
        try:
            keyword_data = keyword_analyzer.analyze_keyword_trends(sessions)
            result['keywords'] = keyword_data
        except Exception as e:
            result['keywords'] = {'error': str(e)}

        # 会话数据（只返回最近20个）
        try:
            recent_sessions = sessions[-20:]
            session_data = []
            for session in recent_sessions:
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

            result['sessions'] = {
                'sessions': session_data,
                'total': len(sessions)
            }
        except Exception as e:
            result['sessions'] = {'error': str(e)}

        # 记忆分析数据
        try:
            memory_data = memory_analyzer.analyze_memory_patterns(sessions)
            result['memory'] = memory_data
        except Exception as e:
            result['memory'] = {'error': str(e)}

        # 缓存结果
        performance_optimizer.data_cache.set('dashboard_batch', result)
        performance_optimizer.update_session_tracking()

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'批量获取数据失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })


@app.route('/api/keywords')
def get_keywords():
    """获取关键词分析（优化版）"""
    sessions = monitor.completed_sessions

    if not sessions:
        return jsonify({'error': '暂无数据'})

    # 检查是否需要更新
    if not performance_optimizer.should_update_data('keywords'):
        cached_data = performance_optimizer.data_cache.get('keywords')
        if cached_data:
            return jsonify(cached_data)

    try:
        keyword_data = keyword_analyzer.analyze_keyword_trends(sessions)

        result = {
            'keywords': keyword_data,
            'timestamp': datetime.now().isoformat()
        }

        # 缓存结果
        performance_optimizer.data_cache.set('keywords', result)
        performance_optimizer.update_session_tracking()

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'关键词分析失败: {str(e)}',
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
    """获取会话列表（优化版）"""
    sessions = monitor.completed_sessions

    if not sessions:
        return jsonify({
            'sessions': [],
            'total': 0,
            'timestamp': datetime.now().isoformat()
        })

    # 检查是否需要更新
    if not performance_optimizer.should_update_data('sessions'):
        cached_data = performance_optimizer.data_cache.get('sessions')
        if cached_data:
            return jsonify(cached_data)

    try:
        recent_sessions = sessions[-20:]  # 最近20个会话

        session_data = []
        for session in recent_sessions:
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

        result = {
            'sessions': session_data,
            'total': len(sessions),
            'timestamp': datetime.now().isoformat()
        }

        # 缓存结果
        performance_optimizer.data_cache.set('sessions', result)
        performance_optimizer.update_session_tracking()

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'获取会话列表失败: {str(e)}',
            'sessions': [],
            'total': 0,
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


@app.route('/api/v6_comprehensive_stats')
def get_v6_comprehensive_stats():
    """获取v6.0系统的综合统计信息"""
    if v6_adapter is None:
        return jsonify({'error': 'v6.0数据适配器不可用'})
    
    try:
        adapted_stats = v6_adapter.adapt_comprehensive_stats()
        return jsonify({
            'v6_stats': adapted_stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'获取v6.0统计失败: {str(e)}'})


@app.route('/api/13_step_monitoring')
def get_13_step_monitoring():
    """获取13步流程监控详情"""
    if v6_adapter is None:
        return jsonify({'error': 'v6.0数据适配器不可用'})
    
    try:
        adapted_data = v6_adapter.adapt_13_step_monitoring()
        return jsonify({
            '13_step_data': adapted_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'获取13步监控失败: {str(e)}'})


@socketio.on('connect')
def handle_connect():
    """WebSocket连接处理"""
    print('客户端已连接')
    emit('message', {'data': '监控连接已建立'})


@socketio.on('start_monitoring')
def handle_start_monitoring():
    """开始实时监控（优化版）"""
    print('开始实时监控')

    def monitoring_loop():
        error_count = 0
        max_errors = 5
        base_interval = 3  # 基础间隔3秒

        while error_count < max_errors:
            try:
                # 检查缓存，避免重复计算
                cached_status = performance_optimizer.data_cache.get('websocket_status')
                if cached_status:
                    socketio.emit('status_update', cached_status)
                else:
                    # 获取实时状态
                    status = analytics.get_real_time_status()
                    summary = monitor.get_performance_summary()

                    status_data = {
                        'status': status,
                        'summary': summary,
                        'timestamp': datetime.now().isoformat()
                    }

                    # 缓存状态数据（短时间缓存）
                    performance_optimizer.data_cache.set('websocket_status', status_data)

                    # 发送实时数据
                    socketio.emit('status_update', status_data)

                # 重置错误计数
                error_count = 0

                # 动态调整更新间隔
                session_count = len(monitor.completed_sessions)
                if session_count == 0:
                    interval = base_interval * 2  # 无数据时降低频率
                else:
                    interval = base_interval

                time.sleep(interval)

            except Exception as e:
                error_count += 1
                print(f"监控循环错误 ({error_count}/{max_errors}): {e}")

                # 发送错误状态
                socketio.emit('monitoring_error', {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })

                # 指数退避
                time.sleep(min(base_interval * (2 ** error_count), 30))

        print("监控循环因错误过多而停止")

    # 在后台线程中运行监控
    monitoring_thread = threading.Thread(target=monitoring_loop)
    monitoring_thread.daemon = True
    monitoring_thread.start()


# 注意：现在使用独立的模板文件 templates/dashboard.html


@app.route('/api/live_data')
def get_live_data():
    """获取实时系统数据"""
    try:
        # 获取实时数据
        live_data = live_connector.get_comprehensive_data()

        if not live_data['system_running']:
            return jsonify({
                'error': 'Estia系统未运行或数据库不可访问',
                'system_status': 'offline',
                'timestamp': datetime.now().isoformat()
            })

        # 转换为仪表板格式
        memory_stats = live_data.get('memory_stats', {})
        session_stats = live_data.get('session_stats', {})
        health = live_data.get('system_health', {})

        # 构建仪表板数据
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'has_data': True,
            'live_mode': True,
            'status': {
                'status': {
                    'status': 'running' if health.get('system_status') == 'active' else 'idle',
                    'session_id': session_stats.get('recent_sessions', [{}])[0].get('session_id', '无') if session_stats.get('recent_sessions') else '无',
                    'running_time': 0,  # 无法从数据库获取运行时间
                    'progress_percentage': 0
                },
                'summary': {
                    'total_sessions': session_stats.get('total_sessions', 0),
                    'average_duration': 0,  # 无法从当前数据计算
                    'success_rate': 1.0,  # 假设成功率
                    'slowest_step': None
                }
            },
            'keywords': extract_keywords_from_memories(memory_stats.get('recent_memories', [])),
            'sessions': {
                'sessions': format_sessions_for_display(session_stats.get('recent_dialogues', [])),
                'total': session_stats.get('total_sessions', 0)
            },
            'memory': {
                'average_similarity': 0.75,  # 估算值
                'memory_usage_stats': {
                    'retrieved': memory_stats.get('total_memories', 0),
                    'associations': memory_stats.get('today_memories', 0)
                },
                'total_retrievals': memory_stats.get('total_memories', 0),
                'similarity_distribution': {
                    '高 (>0.8)': memory_stats.get('weight_distribution', {}).get('high_weight', 0),
                    '中 (0.6-0.8)': memory_stats.get('weight_distribution', {}).get('medium_weight', 0),
                    '低 (<0.6)': memory_stats.get('weight_distribution', {}).get('low_weight', 0)
                }
            }
        }

        return jsonify(dashboard_data)

    except Exception as e:
        return jsonify({
            'error': f'获取实时数据失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })


def extract_keywords_from_memories(memories: List[Dict]) -> Dict[str, Any]:
    """从记忆中提取关键词"""
    try:
        import re
        from collections import Counter

        # 提取所有文本内容
        all_text = ' '.join([mem.get('content', '') for mem in memories])

        # 简单的中文分词（提取2-4字的词汇）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', all_text)

        # 统计词频
        word_counts = Counter(chinese_words)

        # 过滤常见停用词
        stop_words = {'这个', '那个', '可以', '需要', '应该', '因为', '所以', '但是', '然后', '现在', '时候', '问题', '方法', '系统', '功能'}
        filtered_words = {word: count for word, count in word_counts.items() if word not in stop_words and count > 1}

        # 获取前10个关键词
        top_words = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'top_keywords': [
                {'word': word, 'count': count, 'frequency': count / len(memories) if memories else 0}
                for word, count in top_words
            ],
            'total_unique_keywords': len(filtered_words),
            'keyword_distribution': dict(top_words)
        }

    except Exception as e:
        return {
            'top_keywords': [],
            'total_unique_keywords': 0,
            'keyword_distribution': {},
            'error': str(e)
        }


def format_sessions_for_display(dialogues: List[Dict]) -> List[Dict]:
    """格式化会话数据用于显示"""
    try:
        formatted_sessions = []

        # 按会话ID分组对话
        session_groups = {}
        for dialogue in dialogues:
            session_id = dialogue.get('session_id', 'unknown')
            if session_id not in session_groups:
                session_groups[session_id] = []
            session_groups[session_id].append(dialogue)

        # 为每个会话创建显示条目
        for session_id, session_dialogues in list(session_groups.items())[:10]:  # 最多显示10个会话
            # 按时间排序
            session_dialogues.sort(key=lambda x: x.get('timestamp', 0))

            # 找到用户输入和AI回复
            user_inputs = [d for d in session_dialogues if d.get('type') == 'user_input']
            ai_responses = [d for d in session_dialogues if d.get('type') == 'assistant_reply']

            # 获取最新的用户输入和AI回复
            latest_user_input = user_inputs[-1] if user_inputs else None
            latest_ai_response = ai_responses[-1] if ai_responses else None

            user_content = latest_user_input.get('content', '无用户输入') if latest_user_input else '无用户输入'
            ai_content = latest_ai_response.get('content', '无AI回复') if latest_ai_response else '无AI回复'

            # 计算会话持续时间
            if session_dialogues:
                start_time = min(d.get('timestamp', 0) for d in session_dialogues)
                end_time = max(d.get('timestamp', 0) for d in session_dialogues)
                duration = max(0.1, end_time - start_time)  # 至少0.1秒
                start_time_str = datetime.fromtimestamp(start_time).isoformat()
            else:
                duration = 0.1
                start_time_str = datetime.now().isoformat()

            formatted_sessions.append({
                'session_id': session_id,
                'start_time': start_time_str,
                'duration': duration,
                'success_count': len(ai_responses),
                'failed_count': 0,  # 假设没有失败
                'user_input': user_content[:100] + '...' if len(user_content) > 100 else user_content,
                'ai_response': ai_content[:100] + '...' if len(ai_content) > 100 else ai_content
            })

        return formatted_sessions

    except Exception as e:
        print(f"格式化会话数据失败: {e}")
        return []


@app.route('/api/generate_test_data')
def generate_test_data():
    """生成测试数据（仅用于演示）"""
    try:
        import random

        # 生成模拟会话数据
        test_sessions = []
        for i in range(10):
            session_time = datetime.now() - timedelta(minutes=random.randint(1, 60))
            test_sessions.append({
                'session_id': f'test_session_{i+1}',
                'start_time': session_time.isoformat(),
                'duration': random.uniform(0.5, 3.0),
                'success_count': random.randint(8, 14),
                'failed_count': random.randint(0, 2),
                'user_input': f'测试查询 {i+1}: 这是一个示例查询',
                'ai_response': f'这是测试回复 {i+1}...'
            })

        # 生成模拟关键词数据
        test_keywords = {
            'top_keywords': [
                {'word': '测试', 'count': 15, 'frequency': 0.8},
                {'word': '查询', 'count': 12, 'frequency': 0.6},
                {'word': '数据', 'count': 10, 'frequency': 0.5},
                {'word': '监控', 'count': 8, 'frequency': 0.4},
                {'word': '系统', 'count': 6, 'frequency': 0.3}
            ],
            'total_unique_keywords': 25,
            'keyword_distribution': {
                '测试': 15, '查询': 12, '数据': 10, '监控': 8, '系统': 6
            }
        }

        # 生成模拟记忆分析数据
        test_memory = {
            'average_similarity': 0.75,
            'memory_usage_stats': {
                'retrieved': 45,
                'associations': 23,
                'context_memories': 12
            },
            'total_retrievals': 45,
            'similarity_distribution': {
                '高 (>0.8)': 15,
                '中 (0.6-0.8)': 20,
                '低 (<0.6)': 10
            }
        }

        # 生成模拟状态数据
        test_status = {
            'status': {
                'status': 'idle',
                'session_id': None,
                'running_time': random.uniform(10, 100),
                'progress_percentage': 0
            },
            'summary': {
                'total_sessions': 10,
                'average_duration': 1.5,
                'success_rate': 0.92,
                'slowest_step': {
                    'step': 'step_5_faiss_search',
                    'avg_duration': 0.234
                }
            }
        }

        result = {
            'timestamp': datetime.now().isoformat(),
            'has_data': True,
            'test_mode': True,
            'status': test_status,
            'keywords': test_keywords,
            'sessions': {
                'sessions': test_sessions,
                'total': len(test_sessions)
            },
            'memory': test_memory
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': f'生成测试数据失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })


def run_dashboard(host='127.0.0.1', port=5000, debug=True):
    """运行Web仪表板"""
    print(f"🚀 启动 Estia 记忆监控仪表板")
    print(f"📊 访问地址: http://{host}:{port}")
    print(f"🔄 实时监控: WebSocket 连接已启用")
    print(f"🧪 测试数据: http://{host}:{port}/api/generate_test_data")
    print("="*60)

    # 启动Flask应用
    socketio.run(app, host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard()