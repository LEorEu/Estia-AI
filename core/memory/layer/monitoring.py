#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层记忆系统监控

提供分层系统的性能监控、统计分析和健康检查功能
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from .types import MemoryLayer
from .manager import LayeredMemoryManager
from .config import LayerConfigManager

logger = logging.getLogger(__name__)


@dataclass
class LayerMetrics:
    """层级指标"""
    layer: MemoryLayer
    total_memories: int
    capacity_usage: float  # 容量使用率 (0.0-1.0)
    avg_weight: float
    avg_access_count: float
    avg_promotion_score: float
    oldest_memory_age_days: int
    newest_memory_age_days: int
    last_cleanup_hours_ago: Optional[int]
    

@dataclass
class SystemMetrics:
    """系统指标"""
    total_memories: int
    total_layers: int
    sync_status: str  # "synced", "partial", "out_of_sync"
    last_sync_hours_ago: Optional[int]
    last_maintenance_hours_ago: Optional[int]
    layer_metrics: Dict[MemoryLayer, LayerMetrics]
    performance_stats: Dict[str, float]
    

class LayerMonitor:
    """分层系统监控器"""
    
    def __init__(self, layer_manager: LayeredMemoryManager, 
                 config_manager: LayerConfigManager):
        self.layer_manager = layer_manager
        self.config_manager = config_manager
        self.db_manager = layer_manager.db_manager
        self._performance_cache = {}
        self._last_metrics_time = 0
        self._metrics_cache_ttl = 60  # 缓存1分钟
    
    def get_system_metrics(self, use_cache: bool = True) -> SystemMetrics:
        """获取系统指标"""
        try:
            current_time = time.time()
            
            # 检查缓存
            if (use_cache and 
                current_time - self._last_metrics_time < self._metrics_cache_ttl and 
                'system_metrics' in self._performance_cache):
                return self._performance_cache['system_metrics']
            
            # 收集层级指标
            layer_metrics = {}
            total_memories = 0
            
            for layer in MemoryLayer:
                metrics = self._collect_layer_metrics(layer)
                layer_metrics[layer] = metrics
                total_memories += metrics.total_memories
            
            # 收集系统级指标
            sync_status = self._check_sync_status()
            last_sync_hours = self._get_last_sync_hours()
            last_maintenance_hours = self._get_last_maintenance_hours()
            performance_stats = self._collect_performance_stats()
            
            system_metrics = SystemMetrics(
                total_memories=total_memories,
                total_layers=len(MemoryLayer),
                sync_status=sync_status,
                last_sync_hours_ago=last_sync_hours,
                last_maintenance_hours_ago=last_maintenance_hours,
                layer_metrics=layer_metrics,
                performance_stats=performance_stats
            )
            
            # 更新缓存
            self._performance_cache['system_metrics'] = system_metrics
            self._last_metrics_time = current_time
            
            return system_metrics
            
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return self._get_fallback_metrics()
    
    def get_layer_health_status(self) -> Dict[MemoryLayer, str]:
        """获取各层级健康状态"""
        try:
            health_status = {}
            system_metrics = self.get_system_metrics()
            
            for layer, metrics in system_metrics.layer_metrics.items():
                status = self._evaluate_layer_health(layer, metrics)
                health_status[layer] = status
            
            return health_status
            
        except Exception as e:
            logger.error(f"获取层级健康状态失败: {e}")
            return {layer: "unknown" for layer in MemoryLayer}
    
    def get_capacity_alerts(self) -> List[Dict[str, Any]]:
        """获取容量告警"""
        try:
            alerts = []
            system_metrics = self.get_system_metrics()
            
            for layer, metrics in system_metrics.layer_metrics.items():
                # 容量告警阈值
                warning_threshold = 0.8
                critical_threshold = 0.95
                
                if metrics.capacity_usage >= critical_threshold:
                    alerts.append({
                        'level': 'critical',
                        'layer': layer.value,
                        'message': f'{layer.value} 层级容量使用率达到 {metrics.capacity_usage:.1%}',
                        'usage': metrics.capacity_usage,
                        'total_memories': metrics.total_memories
                    })
                elif metrics.capacity_usage >= warning_threshold:
                    alerts.append({
                        'level': 'warning',
                        'layer': layer.value,
                        'message': f'{layer.value} 层级容量使用率达到 {metrics.capacity_usage:.1%}',
                        'usage': metrics.capacity_usage,
                        'total_memories': metrics.total_memories
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"获取容量告警失败: {e}")
            return []
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        try:
            system_metrics = self.get_system_metrics()
            health_status = self.get_layer_health_status()
            capacity_alerts = self.get_capacity_alerts()
            
            # 计算总体健康分数
            health_scores = {
                'healthy': 100,
                'warning': 70,
                'critical': 30,
                'unknown': 0
            }
            
            total_score = sum(health_scores.get(status, 0) for status in health_status.values())
            avg_health_score = total_score / len(health_status) if health_status else 0
            
            # 生成建议
            recommendations = self._generate_recommendations(system_metrics, health_status, capacity_alerts)
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'overall_health_score': avg_health_score,
                'system_metrics': system_metrics,
                'layer_health': health_status,
                'capacity_alerts': capacity_alerts,
                'recommendations': recommendations,
                'summary': {
                    'total_memories': system_metrics.total_memories,
                    'healthy_layers': sum(1 for status in health_status.values() if status == 'healthy'),
                    'warning_layers': sum(1 for status in health_status.values() if status == 'warning'),
                    'critical_layers': sum(1 for status in health_status.values() if status == 'critical'),
                    'sync_status': system_metrics.sync_status
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成性能报告失败: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _collect_layer_metrics(self, layer: MemoryLayer) -> LayerMetrics:
        """收集单个层级的指标"""
        try:
            # 获取层级配置
            layer_config = self.config_manager.get_layer_config(layer)
            
            # 查询层级统计信息
            sql = """
                SELECT 
                    COUNT(*) as total_memories,
                    AVG(weight) as avg_weight,
                    AVG(access_count) as avg_access_count,
                    AVG(promotion_score) as avg_promotion_score,
                    MIN(created_at) as oldest_memory,
                    MAX(created_at) as newest_memory
                FROM memory_layers 
                WHERE layer = ?
            """
            
            result = self.db_manager.query(sql, [layer.value])
            
            if result and result[0][0] > 0:
                row = result[0]
                total_memories = row[0]
                avg_weight = row[1] or 0.0
                avg_access_count = row[2] or 0.0
                avg_promotion_score = row[3] or 0.0
                oldest_memory = row[4]
                newest_memory = row[5]
                
                # 计算记忆年龄
                now = datetime.now()
                oldest_age = (now - datetime.fromisoformat(oldest_memory)).days if oldest_memory else 0
                newest_age = (now - datetime.fromisoformat(newest_memory)).days if newest_memory else 0
            else:
                total_memories = 0
                avg_weight = 0.0
                avg_access_count = 0.0
                avg_promotion_score = 0.0
                oldest_age = 0
                newest_age = 0
            
            # 计算容量使用率
            capacity_usage = total_memories / layer_config.max_memories if layer_config.max_memories > 0 else 0.0
            
            # 获取最后清理时间
            last_cleanup_hours = self._get_last_cleanup_hours(layer)
            
            return LayerMetrics(
                layer=layer,
                total_memories=total_memories,
                capacity_usage=capacity_usage,
                avg_weight=avg_weight,
                avg_access_count=avg_access_count,
                avg_promotion_score=avg_promotion_score,
                oldest_memory_age_days=oldest_age,
                newest_memory_age_days=newest_age,
                last_cleanup_hours_ago=last_cleanup_hours
            )
            
        except Exception as e:
            logger.error(f"收集 {layer.value} 层级指标失败: {e}")
            return LayerMetrics(
                layer=layer,
                total_memories=0,
                capacity_usage=0.0,
                avg_weight=0.0,
                avg_access_count=0.0,
                avg_promotion_score=0.0,
                oldest_memory_age_days=0,
                newest_memory_age_days=0,
                last_cleanup_hours_ago=None
            )
    
    def _check_sync_status(self) -> str:
        """检查同步状态"""
        try:
            # 检查是否有记忆没有分层信息
            sql = """
                SELECT COUNT(*) FROM memories m
                LEFT JOIN memory_layers ml ON m.id = ml.memory_id
                WHERE ml.memory_id IS NULL
            """
            
            result = self.db_manager.query(sql)
            unsynced_count = result[0][0] if result else 0
            
            if unsynced_count == 0:
                return "synced"
            elif unsynced_count < 100:  # 少量未同步
                return "partial"
            else:
                return "out_of_sync"
                
        except Exception as e:
            logger.error(f"检查同步状态失败: {e}")
            return "unknown"
    
    def _get_last_sync_hours(self) -> Optional[int]:
        """获取最后同步时间（小时前）"""
        try:
            # 这里应该从同步日志或状态表中获取
            # 暂时返回 None，表示未知
            return None
        except Exception as e:
            logger.error(f"获取最后同步时间失败: {e}")
            return None
    
    def _get_last_maintenance_hours(self) -> Optional[int]:
        """获取最后维护时间（小时前）"""
        try:
            # 这里应该从维护日志中获取
            # 暂时返回 None，表示未知
            return None
        except Exception as e:
            logger.error(f"获取最后维护时间失败: {e}")
            return None
    
    def _get_last_cleanup_hours(self, layer: MemoryLayer) -> Optional[int]:
        """获取层级最后清理时间（小时前）"""
        try:
            # 这里应该从清理日志中获取
            # 暂时返回 None，表示未知
            return None
        except Exception as e:
            logger.error(f"获取 {layer.value} 层级最后清理时间失败: {e}")
            return None
    
    def _collect_performance_stats(self) -> Dict[str, float]:
        """收集性能统计"""
        try:
            stats = {}
            
            # 数据库查询性能
            start_time = time.time()
            self.db_manager.query("SELECT COUNT(*) FROM memories")
            stats['db_query_time_ms'] = (time.time() - start_time) * 1000
            
            # 分层查询性能
            start_time = time.time()
            self.db_manager.query("SELECT COUNT(*) FROM memory_layers")
            stats['layer_query_time_ms'] = (time.time() - start_time) * 1000
            
            return stats
            
        except Exception as e:
            logger.error(f"收集性能统计失败: {e}")
            return {}
    
    def _evaluate_layer_health(self, layer: MemoryLayer, metrics: LayerMetrics) -> str:
        """评估层级健康状态"""
        try:
            # 容量检查
            if metrics.capacity_usage >= 0.95:
                return "critical"
            elif metrics.capacity_usage >= 0.8:
                return "warning"
            
            # 记忆年龄检查
            layer_config = self.config_manager.get_layer_config(layer)
            if metrics.oldest_memory_age_days > layer_config.retention_days * 1.5:
                return "warning"
            
            # 权重分布检查
            expected_weight = layer_config.weight_threshold
            if abs(metrics.avg_weight - expected_weight) > 2.0:
                return "warning"
            
            return "healthy"
            
        except Exception as e:
            logger.error(f"评估 {layer.value} 层级健康状态失败: {e}")
            return "unknown"
    
    def _generate_recommendations(self, system_metrics: SystemMetrics, 
                                health_status: Dict[MemoryLayer, str],
                                capacity_alerts: List[Dict[str, Any]]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        try:
            # 容量建议
            for alert in capacity_alerts:
                if alert['level'] == 'critical':
                    recommendations.append(
                        f"紧急：{alert['layer']} 层级容量已满，建议立即清理或扩容"
                    )
                elif alert['level'] == 'warning':
                    recommendations.append(
                        f"警告：{alert['layer']} 层级容量使用率较高，建议安排清理"
                    )
            
            # 同步建议
            if system_metrics.sync_status == "out_of_sync":
                recommendations.append("建议执行完整的权重-分层同步操作")
            elif system_metrics.sync_status == "partial":
                recommendations.append("建议执行增量同步操作")
            
            # 健康状态建议
            critical_layers = [layer for layer, status in health_status.items() if status == "critical"]
            if critical_layers:
                layer_names = ", ".join([layer.value for layer in critical_layers])
                recommendations.append(f"关键：{layer_names} 层级状态异常，需要立即检查")
            
            # 维护建议
            if system_metrics.last_maintenance_hours_ago and system_metrics.last_maintenance_hours_ago > 24:
                recommendations.append("建议执行系统维护操作")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"生成建议失败: {e}")
            return ["系统监控异常，建议检查监控模块"]
    
    def _get_fallback_metrics(self) -> SystemMetrics:
        """获取降级指标"""
        fallback_layer_metrics = {}
        for layer in MemoryLayer:
            fallback_layer_metrics[layer] = LayerMetrics(
                layer=layer,
                total_memories=0,
                capacity_usage=0.0,
                avg_weight=0.0,
                avg_access_count=0.0,
                avg_promotion_score=0.0,
                oldest_memory_age_days=0,
                newest_memory_age_days=0,
                last_cleanup_hours_ago=None
            )
        
        return SystemMetrics(
            total_memories=0,
            total_layers=len(MemoryLayer),
            sync_status="unknown",
            last_sync_hours_ago=None,
            last_maintenance_hours_ago=None,
            layer_metrics=fallback_layer_metrics,
            performance_stats={}
        )