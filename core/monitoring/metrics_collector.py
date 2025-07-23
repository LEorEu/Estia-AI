#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标收集器
==========

负责从各个系统组件收集性能指标和统计数据，为监控系统提供数据源。
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from collections import defaultdict, deque
import psutil
import os

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """指标数据点"""
    timestamp: float
    value: float
    labels: Dict[str, str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}


class MetricsCollector:
    """
    指标收集器
    
    从各个系统组件收集性能指标：
    - 系统资源指标 (CPU, 内存, 磁盘等)
    - 应用程序指标 (记忆系统性能)
    - 业务指标 (查询量, 错误率等)
    - 自定义指标
    """
    
    def __init__(self, collection_interval: float = 5.0):
        """
        初始化指标收集器
        
        Args:
            collection_interval: 收集间隔 (秒)
        """
        self.collection_interval = collection_interval
        
        # 指标存储
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.current_values: Dict[str, float] = {}
        
        # 收集器状态
        self.collecting = False
        self.collection_thread = None
        self._lock = threading.RLock()
        
        # 自定义收集器
        self.custom_collectors: List[Callable[[], Dict[str, float]]] = []
        
        # 系统进程信息
        self.process = psutil.Process()
        
        logger.info("📊 指标收集器初始化完成")
    
    def start_collection(self):
        """开始指标收集"""
        if self.collecting:
            logger.warning("指标收集已在运行")
            return
        
        self.collecting = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True,
            name="MetricsCollector"
        )
        self.collection_thread.start()
        
        logger.info("📊 开始指标收集")
    
    def stop_collection(self):
        """停止指标收集"""
        self.collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=10)
        
        logger.info("📊 停止指标收集")
    
    def add_custom_collector(self, collector: Callable[[], Dict[str, float]]):
        """
        添加自定义指标收集器
        
        Args:
            collector: 返回指标字典的函数
        """
        self.custom_collectors.append(collector)
        logger.info("✅ 已添加自定义指标收集器")
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """
        记录指标值
        
        Args:
            name: 指标名称
            value: 指标值
            labels: 标签
        """
        try:
            with self._lock:
                point = MetricPoint(
                    timestamp=time.time(),
                    value=value,
                    labels=labels or {}
                )
                
                self.metrics[name].append(point)
                self.current_values[name] = value
                
        except Exception as e:
            logger.error(f"记录指标失败 {name}: {e}")
    
    def get_current_value(self, name: str) -> Optional[float]:
        """获取指标当前值"""
        with self._lock:
            return self.current_values.get(name)
    
    def get_metric_history(self, name: str, minutes: int = 60) -> List[MetricPoint]:
        """
        获取指标历史数据
        
        Args:
            name: 指标名称
            minutes: 历史时间范围 (分钟)
            
        Returns:
            指标历史数据
        """
        cutoff_time = time.time() - (minutes * 60)
        
        with self._lock:
            if name not in self.metrics:
                return []
            
            return [
                point for point in self.metrics[name]
                if point.timestamp >= cutoff_time
            ]
    
    def get_all_current_metrics(self) -> Dict[str, float]:
        """获取所有当前指标值"""
        with self._lock:
            return dict(self.current_values)
    
    def get_metric_summary(self, name: str, minutes: int = 60) -> Dict[str, Any]:
        """
        获取指标摘要统计
        
        Args:
            name: 指标名称  
            minutes: 统计时间范围 (分钟)
            
        Returns:
            指标摘要统计
        """
        history = self.get_metric_history(name, minutes)
        
        if not history:
            return {
                'name': name,
                'count': 0,
                'current': self.get_current_value(name),
                'error': '无历史数据'
            }
        
        values = [point.value for point in history]
        
        return {
            'name': name,
            'count': len(values),
            'current': values[-1] if values else None,
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'first': values[0] if values else None,
            'last': values[-1] if values else None,
            'trend': self._calculate_trend(values[-10:]) if len(values) >= 2 else 0.0
        }
    
    def _collection_loop(self):
        """指标收集主循环"""
        logger.info("📊 指标收集循环开始")
        
        while self.collecting:
            try:
                # 收集系统指标
                self._collect_system_metrics()
                
                # 收集应用指标
                self._collect_application_metrics()
                
                # 收集自定义指标
                self._collect_custom_metrics()
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"指标收集循环错误: {e}")
                time.sleep(self.collection_interval)
        
        logger.info("📊 指标收集循环结束")
    
    def _collect_system_metrics(self):
        """收集系统资源指标"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.record_metric('system.cpu.usage_percent', cpu_percent)
            
            # CPU 核心数
            cpu_count = psutil.cpu_count()
            self.record_metric('system.cpu.count', cpu_count)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            self.record_metric('system.memory.total_bytes', memory.total)
            self.record_metric('system.memory.used_bytes', memory.used)
            self.record_metric('system.memory.available_bytes', memory.available)
            self.record_metric('system.memory.usage_percent', memory.percent)
            
            # 磁盘使用情况
            disk = psutil.disk_usage(os.getcwd())
            self.record_metric('system.disk.total_bytes', disk.total)
            self.record_metric('system.disk.used_bytes', disk.used)
            self.record_metric('system.disk.free_bytes', disk.free)
            self.record_metric('system.disk.usage_percent', (disk.used / disk.total) * 100)
            
            # 网络统计
            try:
                net_io = psutil.net_io_counters()
                self.record_metric('system.network.bytes_sent', net_io.bytes_sent)
                self.record_metric('system.network.bytes_recv', net_io.bytes_recv)
                self.record_metric('system.network.packets_sent', net_io.packets_sent)
                self.record_metric('system.network.packets_recv', net_io.packets_recv)
            except:
                pass  # 网络统计可能在某些系统上不可用
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
    
    def _collect_application_metrics(self):
        """收集应用程序指标"""
        try:
            # 进程资源使用
            memory_info = self.process.memory_info()
            self.record_metric('app.memory.rss_bytes', memory_info.rss)
            self.record_metric('app.memory.vms_bytes', memory_info.vms)
            
            # 进程CPU时间
            cpu_times = self.process.cpu_times()
            self.record_metric('app.cpu.user_time', cpu_times.user)
            self.record_metric('app.cpu.system_time', cpu_times.system)
            
            # 进程CPU使用率
            try:
                cpu_percent = self.process.cpu_percent()
                self.record_metric('app.cpu.usage_percent', cpu_percent)
            except:
                pass
            
            # 线程数
            try:
                num_threads = self.process.num_threads()
                self.record_metric('app.threads.count', num_threads)
            except:
                pass
            
            # 文件描述符数量 (仅Unix系统)
            try:
                if hasattr(self.process, 'num_fds'):
                    num_fds = self.process.num_fds()
                    self.record_metric('app.fds.count', num_fds)
            except:
                pass
            
        except Exception as e:
            logger.error(f"收集应用程序指标失败: {e}")
    
    def _collect_custom_metrics(self):
        """收集自定义指标"""
        try:
            for collector in self.custom_collectors:
                try:
                    custom_metrics = collector()
                    if isinstance(custom_metrics, dict):
                        for name, value in custom_metrics.items():
                            if isinstance(value, (int, float)):
                                self.record_metric(f'custom.{name}', float(value))
                except Exception as e:
                    logger.error(f"自定义指标收集器失败: {e}")
                    
        except Exception as e:
            logger.error(f"收集自定义指标失败: {e}")
    
    def _calculate_trend(self, values: List[float]) -> float:
        """
        计算趋势 (-1 到 1)
        
        Args:
            values: 数值列表
            
        Returns:
            趋势值
        """
        if len(values) < 2:
            return 0.0
        
        try:
            # 简单线性回归
            n = len(values)
            x = list(range(n))
            
            x_mean = sum(x) / n
            y_mean = sum(values) / n
            
            numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
            x_var = sum((x[i] - x_mean) ** 2 for i in range(n))
            y_var = sum((values[i] - y_mean) ** 2 for i in range(n))
            
            if x_var == 0 or y_var == 0:
                return 0.0
            
            correlation = numerator / (x_var * y_var) ** 0.5
            return max(-1.0, min(1.0, correlation))
            
        except Exception as e:
            logger.error(f"计算趋势失败: {e}")
            return 0.0
    
    def export_metrics(self, format_type: str = 'json') -> str:
        """
        导出指标数据
        
        Args:
            format_type: 导出格式 ('json', 'csv')
            
        Returns:
            导出的数据字符串
        """
        try:
            with self._lock:
                if format_type == 'json':
                    import json
                    export_data = {
                        'timestamp': time.time(),
                        'current_metrics': dict(self.current_values),
                        'collection_interval': self.collection_interval,
                        'metrics_count': len(self.metrics)
                    }
                    return json.dumps(export_data, indent=2, ensure_ascii=False)
                
                elif format_type == 'csv':
                    lines = ['metric_name,current_value,data_points']
                    for name, current_value in self.current_values.items():
                        data_points = len(self.metrics.get(name, []))
                        lines.append(f'{name},{current_value},{data_points}')
                    return '\n'.join(lines)
                
                else:
                    return f"不支持的导出格式: {format_type}"
                    
        except Exception as e:
            logger.error(f"导出指标数据失败: {e}")
            return f"导出失败: {e}"
    
    def clear_history(self, older_than_minutes: int = 60):
        """
        清理历史数据
        
        Args:
            older_than_minutes: 清理多少分钟前的数据
        """
        try:
            cutoff_time = time.time() - (older_than_minutes * 60)
            
            with self._lock:
                for name, points in self.metrics.items():
                    # 过滤掉过期数据
                    filtered_points = deque(
                        [point for point in points if point.timestamp >= cutoff_time],
                        maxlen=points.maxlen
                    )
                    self.metrics[name] = filtered_points
                
                logger.info(f"✅ 已清理 {older_than_minutes} 分钟前的历史数据")
                
        except Exception as e:
            logger.error(f"清理历史数据失败: {e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取收集器统计信息"""
        try:
            with self._lock:
                total_points = sum(len(points) for points in self.metrics.values())
                
                return {
                    'collecting': self.collecting,
                    'collection_interval': self.collection_interval,
                    'metrics_count': len(self.metrics),
                    'total_data_points': total_points,
                    'custom_collectors': len(self.custom_collectors),
                    'current_metrics_count': len(self.current_values)
                }
                
        except Exception as e:
            logger.error(f"获取收集器统计失败: {e}")
            return {'error': str(e)}