#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Monitor
==================

Main performance monitoring coordinator that integrates with the existing
memory system monitoring and provides enhanced real-time metrics.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Real-time performance metrics"""
    timestamp: float
    
    # System metrics
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    memory_usage_percent: float = 0.0
    
    # Memory system metrics
    cache_hit_rate: float = 0.0
    active_sessions: int = 0
    total_memories: int = 0
    
    # Performance metrics
    avg_query_time_ms: float = 0.0
    avg_storage_time_ms: float = 0.0
    queries_per_second: float = 0.0
    
    # Error metrics
    error_rate: float = 0.0
    failed_operations: int = 0
    
    # Custom metrics
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """
    Main performance monitoring system
    
    Integrates with existing memory system monitoring to provide:
    - Real-time performance tracking
    - Historical data collection
    - Performance alerting
    - Dashboard data aggregation
    """
    
    def __init__(self, memory_system=None, collection_interval=5.0):
        """
        Initialize performance monitor
        
        Args:
            memory_system: Estia memory system instance
            collection_interval: Metrics collection interval in seconds
        """
        self.memory_system = memory_system
        self.collection_interval = collection_interval
        
        # Metrics storage
        self.current_metrics = PerformanceMetrics(timestamp=time.time())
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 samples
        
        # Performance counters
        self.operation_counters = defaultdict(int)
        self.operation_timings = defaultdict(list)
        self.error_counters = defaultdict(int)
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self._lock = threading.RLock()
        
        # Alert thresholds
        self.alert_thresholds = {
            'cpu_usage': 80.0,          # CPU usage > 80%
            'memory_usage': 85.0,       # Memory usage > 85%
            'cache_hit_rate': 0.6,      # Cache hit rate < 60%
            'avg_query_time_ms': 1000,  # Query time > 1000ms
            'error_rate': 0.05,         # Error rate > 5%
            'queries_per_second': 1.0   # QPS < 1.0
        }
        
        # Alert callbacks
        self.alert_callbacks = []
        
        logger.info("🔍 Performance monitor initialized")
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if self.monitoring_active:
            logger.warning("Performance monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="PerformanceMonitor"
        )
        self.monitoring_thread.start()
        
        logger.info("🔍 Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        logger.info("🔍 Performance monitoring stopped")
    
    def record_operation(self, operation: str, duration_ms: float, 
                        success: bool = True, metadata: Dict[str, Any] = None):
        """
        Record an operation for performance tracking
        
        Args:
            operation: Operation name
            duration_ms: Operation duration in milliseconds
            success: Whether operation succeeded
            metadata: Additional metadata
        """
        with self._lock:
            self.operation_counters[operation] += 1
            self.operation_timings[operation].append(duration_ms)
            
            # Keep only recent timings (last 100)
            if len(self.operation_timings[operation]) > 100:
                self.operation_timings[operation].pop(0)
            
            if not success:
                self.error_counters[operation] += 1
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        with self._lock:
            return self.current_metrics
    
    def get_metrics_history(self, minutes: int = 60) -> List[PerformanceMetrics]:
        """
        Get metrics history for the specified time period
        
        Args:
            minutes: Number of minutes of history to return
            
        Returns:
            List of performance metrics
        """
        cutoff_time = time.time() - (minutes * 60)
        
        with self._lock:
            return [
                metric for metric in self.metrics_history
                if metric.timestamp >= cutoff_time
            ]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        current = self.get_current_metrics()
        history = self.get_metrics_history(60)
        
        # Calculate trends
        if len(history) >= 2:
            cpu_trend = self._calculate_trend([m.cpu_usage for m in history[-10:]])
            memory_trend = self._calculate_trend([m.memory_usage_percent for m in history[-10:]])
            qps_trend = self._calculate_trend([m.queries_per_second for m in history[-10:]])
        else:
            cpu_trend = memory_trend = qps_trend = 0.0
        
        # Operation statistics
        operation_stats = {}
        with self._lock:
            for operation, timings in self.operation_timings.items():
                if timings:
                    operation_stats[operation] = {
                        'count': self.operation_counters[operation],
                        'avg_time_ms': sum(timings) / len(timings),
                        'min_time_ms': min(timings),
                        'max_time_ms': max(timings),
                        'error_count': self.error_counters[operation],
                        'error_rate': self.error_counters[operation] / self.operation_counters[operation]
                    }
        
        return {
            'timestamp': current.timestamp,
            'current_metrics': {
                'cpu_usage': current.cpu_usage,
                'memory_usage_mb': current.memory_usage_mb,
                'memory_usage_percent': current.memory_usage_percent,
                'cache_hit_rate': current.cache_hit_rate,
                'active_sessions': current.active_sessions,
                'total_memories': current.total_memories,
                'avg_query_time_ms': current.avg_query_time_ms,
                'queries_per_second': current.queries_per_second,
                'error_rate': current.error_rate
            },
            'trends': {
                'cpu_trend': cpu_trend,
                'memory_trend': memory_trend,
                'qps_trend': qps_trend
            },
            'operation_statistics': operation_stats,
            'alert_thresholds': self.alert_thresholds,
            'monitoring_active': self.monitoring_active,
            'history_size': len(history)
        }
    
    def add_alert_callback(self, callback):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance alerts"""
        alerts = []
        current = self.current_metrics
        
        # CPU usage alert
        if current.cpu_usage > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'cpu_high',
                'message': f"High CPU usage: {current.cpu_usage:.1f}%",
                'value': current.cpu_usage,
                'threshold': self.alert_thresholds['cpu_usage'],
                'severity': 'warning' if current.cpu_usage < 90 else 'critical'
            })
        
        # Memory usage alert
        if current.memory_usage_percent > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'memory_high',
                'message': f"High memory usage: {current.memory_usage_percent:.1f}%",
                'value': current.memory_usage_percent,
                'threshold': self.alert_thresholds['memory_usage'],
                'severity': 'warning' if current.memory_usage_percent < 95 else 'critical'
            })
        
        # Cache hit rate alert
        if current.cache_hit_rate < self.alert_thresholds['cache_hit_rate']:
            alerts.append({
                'type': 'cache_low',
                'message': f"Low cache hit rate: {current.cache_hit_rate:.1%}",
                'value': current.cache_hit_rate,
                'threshold': self.alert_thresholds['cache_hit_rate'],
                'severity': 'warning'
            })
        
        # Query performance alert
        if current.avg_query_time_ms > self.alert_thresholds['avg_query_time_ms']:
            alerts.append({
                'type': 'query_slow',
                'message': f"Slow query performance: {current.avg_query_time_ms:.0f}ms",
                'value': current.avg_query_time_ms,
                'threshold': self.alert_thresholds['avg_query_time_ms'],
                'severity': 'warning'
            })
        
        # Error rate alert
        if current.error_rate > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'error_high',
                'message': f"High error rate: {current.error_rate:.1%}",
                'value': current.error_rate,
                'threshold': self.alert_thresholds['error_rate'],
                'severity': 'critical'
            })
        
        # Fire alert callbacks
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
        
        return alerts
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("🔍 Performance monitoring loop started")
        
        while self.monitoring_active:
            try:
                self._collect_metrics()
                alerts = self.check_alerts()
                
                if alerts:
                    logger.debug(f"🚨 {len(alerts)} performance alert(s) detected")
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.collection_interval)
        
        logger.info("🔍 Performance monitoring loop stopped")
    
    def _collect_metrics(self):
        """Collect current performance metrics"""
        try:
            # System metrics
            cpu_usage, memory_info = self._get_system_metrics()
            
            # Memory system metrics
            memory_stats = self._get_memory_system_metrics()
            
            # Performance metrics
            perf_metrics = self._calculate_performance_metrics()
            
            # Create new metrics object
            new_metrics = PerformanceMetrics(
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage_mb=memory_info['used_mb'],
                memory_usage_percent=memory_info['percent'],
                cache_hit_rate=memory_stats.get('cache_hit_rate', 0.0),
                active_sessions=memory_stats.get('active_sessions', 0),
                total_memories=memory_stats.get('total_memories', 0),
                avg_query_time_ms=perf_metrics.get('avg_query_time_ms', 0.0),
                avg_storage_time_ms=perf_metrics.get('avg_storage_time_ms', 0.0),
                queries_per_second=perf_metrics.get('queries_per_second', 0.0),
                error_rate=perf_metrics.get('error_rate', 0.0),
                failed_operations=perf_metrics.get('failed_operations', 0)
            )
            
            with self._lock:
                self.current_metrics = new_metrics
                self.metrics_history.append(new_metrics)
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    def _get_system_metrics(self) -> tuple:
        """Get system CPU and memory metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_info = {
                'used_mb': memory.used / 1024 / 1024,
                'percent': memory.percent
            }
            
            return cpu_usage, memory_info
            
        except ImportError:
            logger.warning("psutil not available, using mock system metrics")
            return 0.0, {'used_mb': 0.0, 'percent': 0.0}
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return 0.0, {'used_mb': 0.0, 'percent': 0.0}
    
    def _get_memory_system_metrics(self) -> Dict[str, Any]:
        """Get memory system specific metrics"""
        try:
            if not self.memory_system:
                return {}
            
            # Get stats from memory system
            system_stats = self.memory_system.get_system_stats()
            
            cache_stats = system_stats.get('unified_cache', {})
            cache_hit_rate = 0.0
            if cache_stats.get('access_count', 0) > 0:
                cache_hit_rate = cache_stats.get('hit_count', 0) / cache_stats.get('access_count', 1)
            
            return {
                'cache_hit_rate': cache_hit_rate,
                'active_sessions': len(system_stats.get('async_queue', {}).get('active_sessions', [])),
                'total_memories': system_stats.get('total_memories', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting memory system metrics: {e}")
            return {}
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics from operation data"""
        try:
            current_time = time.time()
            
            with self._lock:
                # Calculate average query time
                query_timings = self.operation_timings.get('query_enhancement', [])
                avg_query_time = sum(query_timings) / len(query_timings) if query_timings else 0.0
                
                # Calculate average storage time
                storage_timings = self.operation_timings.get('memory_storage', [])
                avg_storage_time = sum(storage_timings) / len(storage_timings) if storage_timings else 0.0
                
                # Calculate QPS (queries in last minute)
                total_operations = sum(self.operation_counters.values())
                qps = total_operations / 60.0  # Rough estimate
                
                # Calculate error rate
                total_errors = sum(self.error_counters.values())
                error_rate = (total_errors / total_operations) if total_operations > 0 else 0.0
                
                return {
                    'avg_query_time_ms': avg_query_time,
                    'avg_storage_time_ms': avg_storage_time,
                    'queries_per_second': qps,
                    'error_rate': error_rate,
                    'failed_operations': total_errors
                }
        
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction (-1 to 1)"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        
        # Calculate correlation coefficient
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        x_var = sum((x[i] - x_mean) ** 2 for i in range(n))
        y_var = sum((values[i] - y_mean) ** 2 for i in range(n))
        
        if x_var == 0 or y_var == 0:
            return 0.0
        
        correlation = numerator / (x_var * y_var) ** 0.5
        return correlation