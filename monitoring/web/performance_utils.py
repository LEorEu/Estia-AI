#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化工具模块
================

提供性能优化、后台监控、数据缓存等功能。
"""

import time
import threading
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """性能优化器"""

    def __init__(self, cache_ttl: int = 3):
        """
        初始化性能优化器
        
        Args:
            cache_ttl: 缓存生存时间（秒）
        """
        self.executor = ThreadPoolExecutor(max_workers=4)
        from .data_adapters import DataCache
        self.data_cache = DataCache(cache_ttl)
        self.last_session_count = 0
        self.last_update_time = 0
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'computations_saved': 0
        }

    def should_update_data(self, data_type: str, monitor=None) -> bool:
        """
        判断是否需要更新数据
        
        Args:
            data_type: 数据类型
            monitor: 监控器实例
            
        Returns:
            是否需要更新
        """
        try:
            if not monitor:
                return True
                
            current_session_count = len(getattr(monitor, 'completed_sessions', []))
            current_time = time.time()

            # 如果会话数量没有变化且距离上次更新不到3秒，跳过更新
            if (data_type in ['sessions', 'keywords', 'memory'] and
                current_session_count == self.last_session_count and
                current_time - self.last_update_time < 3):
                
                self._stats['computations_saved'] += 1
                return False

            return True
            
        except Exception as e:
            logger.error(f"检查数据更新状态失败: {e}")
            return True

    def update_session_tracking(self, monitor=None):
        """更新会话跟踪信息"""
        try:
            if monitor:
                self.last_session_count = len(getattr(monitor, 'completed_sessions', []))
            self.last_update_time = time.time()
        except Exception as e:
            logger.error(f"更新会话跟踪失败: {e}")

    async def get_cached_or_compute(self, key: str, compute_func: Callable, *args, **kwargs):
        """
        获取缓存数据或计算新数据
        
        Args:
            key: 缓存键
            compute_func: 计算函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            计算结果
        """
        try:
            # 检查缓存
            cached_data = self.data_cache.get(key)
            if cached_data is not None:
                self._stats['cache_hits'] += 1
                return cached_data

            self._stats['cache_misses'] += 1

            # 在线程池中执行计算
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.executor, compute_func, *args, **kwargs)

            # 缓存结果
            self.data_cache.set(key, result)
            return result
            
        except Exception as e:
            logger.error(f"缓存计算失败: {e}")
            # 如果异步计算失败，直接执行同步计算
            try:
                return compute_func(*args, **kwargs)
            except Exception as sync_error:
                logger.error(f"同步计算也失败: {sync_error}")
                return None

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        cache_stats = self.data_cache.get_stats()
        total_requests = self._stats['cache_hits'] + self._stats['cache_misses']
        
        return {
            'cache_hit_rate': (
                self._stats['cache_hits'] / total_requests 
                if total_requests > 0 else 0
            ),
            'cache_hits': self._stats['cache_hits'],
            'cache_misses': self._stats['cache_misses'],
            'computations_saved': self._stats['computations_saved'],
            'cache_stats': cache_stats,
            'executor_threads': 4,
            'last_update_time': self.last_update_time
        }

    def clear_cache(self):
        """清空缓存"""
        self.data_cache.clear()
        logger.info("性能优化器缓存已清空")

    def shutdown(self):
        """关闭性能优化器"""
        try:
            self.executor.shutdown(wait=True, timeout=10)
            logger.info("性能优化器已关闭")
        except Exception as e:
            logger.error(f"关闭性能优化器失败: {e}")


class BackgroundMonitor:
    """后台监控器，处理定期任务和WebSocket推送"""
    
    def __init__(self, interval: float = 5.0):
        """
        初始化后台监控器
        
        Args:
            interval: 监控间隔（秒）
        """
        self.interval = interval
        self.running = False
        self.monitor_thread = None
        self.callbacks = []
        self._stats = {
            'iterations': 0,
            'errors': 0,
            'last_run': None
        }

    def add_callback(self, callback: Callable):
        """
        添加回调函数
        
        Args:
            callback: 回调函数
        """
        self.callbacks.append(callback)
        logger.info(f"添加后台监控回调: {callback.__name__}")

    def start(self):
        """启动后台监控"""
        if self.running:
            logger.warning("后台监控已在运行")
            return

        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="BackgroundMonitor"
        )
        self.monitor_thread.start()
        logger.info("🔄 后台监控已启动")

    def stop(self):
        """停止后台监控"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        logger.info("⏹️ 后台监控已停止")

    def _monitoring_loop(self):
        """监控循环"""
        logger.info("🔄 后台监控循环开始")
        
        while self.running:
            try:
                self._stats['iterations'] += 1
                self._stats['last_run'] = time.time()
                
                # 执行所有回调
                for callback in self.callbacks:
                    try:
                        callback()
                    except Exception as e:
                        logger.error(f"后台监控回调失败 {callback.__name__}: {e}")
                        self._stats['errors'] += 1
                
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"后台监控循环错误: {e}")
                self._stats['errors'] += 1
                time.sleep(self.interval)
        
        logger.info("🔄 后台监控循环结束")

    def get_stats(self) -> Dict[str, Any]:
        """获取监控统计信息"""
        return {
            'running': self.running,
            'interval': self.interval,
            'iterations': self._stats['iterations'],
            'errors': self._stats['errors'],
            'error_rate': (
                self._stats['errors'] / self._stats['iterations'] 
                if self._stats['iterations'] > 0 else 0
            ),
            'last_run': self._stats['last_run'],
            'callbacks_count': len(self.callbacks)
        }


def create_test_data_generator():
    """创建测试数据生成器"""
    
    def generate_test_dashboard_data() -> Dict[str, Any]:
        """生成测试仪表板数据"""
        try:
            import random
            from datetime import timedelta
            
            # 生成模拟会话数据
            test_sessions = []
            for i in range(10):
                session_time = datetime.now() - timedelta(minutes=random.randint(1, 60))
                test_sessions.append({
                    'session_id': f'test_session_{i+1}',
                    'start_time': session_time.isoformat(),
                    'duration': random.uniform(0.5, 3.0),
                    'success_count': random.randint(8, 15),
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

            return {
                'timestamp': datetime.now().isoformat(),
                'has_data': True,
                'test_mode': True,
                'data_source': 'test_generator',
                'status': test_status,
                'keywords': test_keywords,
                'sessions': {
                    'sessions': test_sessions,
                    'total': len(test_sessions)
                },
                'memory': test_memory
            }

        except Exception as e:
            logger.error(f"生成测试数据失败: {e}")
            return {
                'error': f'生成测试数据失败: {str(e)}',
                'timestamp': datetime.now().isoformat(),
                'test_mode': True
            }
    
    return generate_test_dashboard_data