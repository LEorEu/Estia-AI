#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
告警管理器
==========

负责系统性能告警的管理，包括告警规则配置、告警触发、通知发送等功能。
"""

import time
import threading
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """告警严重程度"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """告警状态"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class AlertRule:
    """告警规则"""
    rule_id: str
    name: str
    description: str
    metric_name: str
    condition: str  # 'gt', 'lt', 'eq', 'gte', 'lte'
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    
    # 告警抑制配置
    cooldown_seconds: int = 300  # 冷却时间5分钟
    consecutive_violations: int = 1  # 连续违规次数
    
    # 扩展配置
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """告警实例"""
    alert_id: str
    rule: AlertRule
    triggered_at: float
    current_value: float
    message: str
    status: AlertStatus = AlertStatus.ACTIVE
    
    # 告警处理信息
    acknowledged_at: Optional[float] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[float] = None
    
    # 统计信息
    trigger_count: int = 1
    last_triggered: float = field(default_factory=time.time)
    
    # 扩展数据
    metadata: Dict[str, Any] = field(default_factory=dict)


class AlertManager:
    """
    告警管理器
    
    提供完整的告警管理功能：
    - 告警规则配置和管理
    - 实时指标监控和告警触发
    - 告警状态管理和历史记录
    - 告警通知和回调处理
    """
    
    def __init__(self):
        """初始化告警管理器"""
        # 告警规则管理
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        
        # 告警状态跟踪
        self.metric_violations: Dict[str, List[float]] = defaultdict(list)
        self.last_alert_time: Dict[str, float] = {}
        
        # 通知回调
        self.notification_callbacks: List[Callable] = []
        
        # 线程安全
        self._lock = threading.RLock()
        
        # 初始化默认告警规则
        self._initialize_default_rules()
        
        logger.info("🚨 告警管理器初始化完成")
    
    def _initialize_default_rules(self):
        """初始化默认告警规则"""
        default_rules = [
            AlertRule(
                rule_id="cpu_high",
                name="CPU使用率过高",
                description="CPU使用率超过阈值",
                metric_name="system.cpu.usage_percent",
                condition="gt",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                cooldown_seconds=300,
                consecutive_violations=2
            ),
            AlertRule(
                rule_id="cpu_critical",
                name="CPU使用率严重过高",
                description="CPU使用率严重超过阈值",
                metric_name="system.cpu.usage_percent",
                condition="gt",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                cooldown_seconds=180,
                consecutive_violations=1
            ),
            AlertRule(
                rule_id="memory_high",
                name="内存使用率过高",
                description="内存使用率超过阈值",
                metric_name="system.memory.usage_percent",
                condition="gt",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
                cooldown_seconds=300,
                consecutive_violations=2
            ),
            AlertRule(
                rule_id="memory_critical",
                name="内存使用率严重过高",
                description="内存使用率严重超过阈值",
                metric_name="system.memory.usage_percent",
                condition="gt",
                threshold=95.0,
                severity=AlertSeverity.CRITICAL,
                cooldown_seconds=120,
                consecutive_violations=1
            ),
            AlertRule(
                rule_id="cache_hit_low",
                name="缓存命中率过低",
                description="缓存命中率低于预期",
                metric_name="custom.memory_cache_hit_rate",
                condition="lt",
                threshold=0.6,
                severity=AlertSeverity.WARNING,
                cooldown_seconds=600,
                consecutive_violations=3
            ),
            AlertRule(
                rule_id="query_time_slow",
                name="查询响应时间过长",
                description="平均查询时间超过阈值",
                metric_name="custom.memory_db_query_time",
                condition="gt",
                threshold=1000.0,
                severity=AlertSeverity.WARNING,
                cooldown_seconds=300,
                consecutive_violations=2
            ),
            AlertRule(
                rule_id="error_rate_high",
                name="错误率过高",
                description="系统错误率超过阈值",
                metric_name="app.cpu.usage_percent",
                condition="gt",
                threshold=0.05,
                severity=AlertSeverity.CRITICAL,
                cooldown_seconds=180,
                consecutive_violations=1
            ),
            AlertRule(
                rule_id="qps_low",
                name="查询性能过低",
                description="每秒查询数低于预期",
                metric_name="custom.memory_queue_size",
                condition="lt",
                threshold=1.0,
                severity=AlertSeverity.INFO,
                cooldown_seconds=600,
                consecutive_violations=5
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.rule_id] = rule
        
        logger.info(f"🚨 已加载 {len(default_rules)} 个默认告警规则")
    
    def add_rule(self, rule: AlertRule) -> bool:
        """
        添加告警规则
        
        Args:
            rule: 告警规则
            
        Returns:
            是否添加成功
        """
        try:
            with self._lock:
                if rule.rule_id in self.rules:
                    logger.warning(f"告警规则已存在: {rule.rule_id}")
                    return False
                
                self.rules[rule.rule_id] = rule
                logger.info(f"✅ 已添加告警规则: {rule.name}")
                return True
                
        except Exception as e:
            logger.error(f"添加告警规则失败: {e}")
            return False
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新告警规则
        
        Args:
            rule_id: 规则ID
            updates: 更新内容
            
        Returns:
            是否更新成功
        """
        try:
            with self._lock:
                if rule_id not in self.rules:
                    logger.error(f"告警规则不存在: {rule_id}")
                    return False
                
                rule = self.rules[rule_id]
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                
                logger.info(f"✅ 已更新告警规则: {rule.name}")
                return True
                
        except Exception as e:
            logger.error(f"更新告警规则失败: {e}")
            return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        删除告警规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            是否删除成功
        """
        try:
            with self._lock:
                if rule_id not in self.rules:
                    logger.error(f"告警规则不存在: {rule_id}")
                    return False
                
                rule = self.rules.pop(rule_id)
                logger.info(f"✅ 已删除告警规则: {rule.name}")
                return True
                
        except Exception as e:
            logger.error(f"删除告警规则失败: {e}")
            return False
    
    def check_metrics(self, metrics: Dict[str, float]) -> List[Alert]:
        """
        检查指标并触发告警
        
        Args:
            metrics: 当前指标值
            
        Returns:
            新触发的告警列表
        """
        new_alerts = []
        current_time = time.time()
        
        try:
            with self._lock:
                for rule in self.rules.values():
                    if not rule.enabled:
                        continue
                    
                    metric_value = metrics.get(rule.metric_name)
                    if metric_value is None:
                        continue
                    
                    # 检查条件是否满足
                    violation = self._check_condition(metric_value, rule)
                    
                    if violation:
                        # 记录违规
                        self.metric_violations[rule.rule_id].append(current_time)
                        
                        # 清理过期的违规记录（5分钟内的）
                        cutoff_time = current_time - 300
                        self.metric_violations[rule.rule_id] = [
                            t for t in self.metric_violations[rule.rule_id] 
                            if t >= cutoff_time
                        ]
                        
                        # 检查是否满足连续违规条件
                        violation_count = len(self.metric_violations[rule.rule_id])
                        if violation_count >= rule.consecutive_violations:
                            # 检查冷却时间
                            last_alert = self.last_alert_time.get(rule.rule_id, 0)
                            if current_time - last_alert >= rule.cooldown_seconds:
                                # 触发告警
                                alert = self._create_alert(rule, metric_value, current_time)
                                new_alerts.append(alert)
                                
                                # 更新状态
                                self.active_alerts[alert.alert_id] = alert
                                self.last_alert_time[rule.rule_id] = current_time
                                self.metric_violations[rule.rule_id].clear()
                    else:
                        # 清理违规记录
                        if rule.rule_id in self.metric_violations:
                            self.metric_violations[rule.rule_id].clear()
                        
                        # 检查是否可以自动解决告警
                        self._auto_resolve_alerts(rule.rule_id, current_time)
            
            # 发送通知
            for alert in new_alerts:
                self._send_notifications(alert)
            
            return new_alerts
            
        except Exception as e:
            logger.error(f"检查指标告警失败: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """
        确认告警
        
        Args:
            alert_id: 告警ID
            acknowledged_by: 确认人
            
        Returns:
            是否确认成功
        """
        try:
            with self._lock:
                if alert_id not in self.active_alerts:
                    logger.error(f"活跃告警不存在: {alert_id}")
                    return False
                
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = time.time()
                alert.acknowledged_by = acknowledged_by
                
                logger.info(f"✅ 告警已确认: {alert.rule.name} (by {acknowledged_by})")
                return True
                
        except Exception as e:
            logger.error(f"确认告警失败: {e}")
            return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        解决告警
        
        Args:
            alert_id: 告警ID
            
        Returns:
            是否解决成功
        """
        try:
            with self._lock:
                if alert_id not in self.active_alerts:
                    logger.error(f"活跃告警不存在: {alert_id}")
                    return False
                
                alert = self.active_alerts.pop(alert_id)
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = time.time()
                
                # 添加到历史记录
                self.alert_history.append(alert)
                
                logger.info(f"✅ 告警已解决: {alert.rule.name}")
                return True
                
        except Exception as e:
            logger.error(f"解决告警失败: {e}")
            return False
    
    def get_active_alerts(self) -> List[Alert]:
        """获取所有活跃告警"""
        with self._lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """
        获取告警历史
        
        Args:
            limit: 返回数量限制
            
        Returns:
            告警历史列表
        """
        with self._lock:
            return list(self.alert_history)[-limit:]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """获取告警统计信息"""
        try:
            with self._lock:
                active_count = len(self.active_alerts)
                total_rules = len(self.rules)
                enabled_rules = sum(1 for rule in self.rules.values() if rule.enabled)
                
                # 按严重程度统计活跃告警
                severity_counts = {
                    AlertSeverity.INFO.value: 0,
                    AlertSeverity.WARNING.value: 0,
                    AlertSeverity.CRITICAL.value: 0
                }
                
                for alert in self.active_alerts.values():
                    severity_counts[alert.rule.severity.value] += 1
                
                # 最近24小时的告警统计
                cutoff_time = time.time() - 86400
                recent_alerts = [
                    alert for alert in self.alert_history
                    if alert.triggered_at >= cutoff_time
                ]
                
                return {
                    'active_alerts': active_count,
                    'total_rules': total_rules,
                    'enabled_rules': enabled_rules,
                    'severity_distribution': severity_counts,
                    'alerts_24h': len(recent_alerts),
                    'avg_resolution_time': self._calculate_avg_resolution_time(),
                    'top_alert_rules': self._get_top_alert_rules()
                }
                
        except Exception as e:
            logger.error(f"获取告警统计失败: {e}")
            return {'error': str(e)}
    
    def add_notification_callback(self, callback: Callable[[Alert], None]):
        """
        添加通知回调函数
        
        Args:
            callback: 通知回调函数
        """
        self.notification_callbacks.append(callback)
        logger.info("✅ 已添加告警通知回调")
    
    def _check_condition(self, value: float, rule: AlertRule) -> bool:
        """检查条件是否满足"""
        try:
            if rule.condition == "gt":
                return value > rule.threshold
            elif rule.condition == "gte":
                return value >= rule.threshold
            elif rule.condition == "lt":
                return value < rule.threshold
            elif rule.condition == "lte":
                return value <= rule.threshold
            elif rule.condition == "eq":
                return abs(value - rule.threshold) < 0.001
            else:
                logger.error(f"未知的条件类型: {rule.condition}")
                return False
        except Exception as e:
            logger.error(f"检查条件失败: {e}")
            return False
    
    def _create_alert(self, rule: AlertRule, current_value: float, 
                     triggered_at: float) -> Alert:
        """创建告警实例"""
        alert_id = f"{rule.rule_id}_{int(triggered_at)}"
        
        # 格式化消息
        if rule.condition in ["gt", "gte"]:
            message = f"{rule.description}: {current_value:.2f} > {rule.threshold}"
        elif rule.condition in ["lt", "lte"]:
            message = f"{rule.description}: {current_value:.2f} < {rule.threshold}"
        else:
            message = f"{rule.description}: {current_value:.2f}"
        
        alert = Alert(
            alert_id=alert_id,
            rule=rule,
            triggered_at=triggered_at,
            current_value=current_value,
            message=message
        )
        
        return alert
    
    def _auto_resolve_alerts(self, rule_id: str, current_time: float):
        """自动解决告警"""
        try:
            alerts_to_resolve = []
            
            for alert_id, alert in self.active_alerts.items():
                if (alert.rule.rule_id == rule_id and 
                    alert.status == AlertStatus.ACTIVE):
                    alerts_to_resolve.append(alert_id)
            
            for alert_id in alerts_to_resolve:
                self.resolve_alert(alert_id)
                
        except Exception as e:
            logger.error(f"自动解决告警失败: {e}")
    
    def _send_notifications(self, alert: Alert):
        """发送告警通知"""
        try:
            for callback in self.notification_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"告警通知回调失败: {e}")
        except Exception as e:
            logger.error(f"发送告警通知失败: {e}")
    
    def _calculate_avg_resolution_time(self) -> float:
        """计算平均解决时间"""
        try:
            resolved_alerts = [
                alert for alert in self.alert_history
                if alert.resolved_at and alert.triggered_at
            ]
            
            if not resolved_alerts:
                return 0.0
            
            total_time = sum(
                alert.resolved_at - alert.triggered_at
                for alert in resolved_alerts
            )
            
            return total_time / len(resolved_alerts)
            
        except Exception as e:
            logger.error(f"计算平均解决时间失败: {e}")
            return 0.0
    
    def _get_top_alert_rules(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最常触发的告警规则"""
        try:
            rule_counts = defaultdict(int)
            
            # 统计历史告警
            for alert in self.alert_history:
                rule_counts[alert.rule.rule_id] += 1
            
            # 统计活跃告警
            for alert in self.active_alerts.values():
                rule_counts[alert.rule.rule_id] += alert.trigger_count
            
            # 排序并返回前N个
            sorted_rules = sorted(
                rule_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
            
            result = []
            for rule_id, count in sorted_rules:
                if rule_id in self.rules:
                    rule = self.rules[rule_id]
                    result.append({
                        'rule_id': rule_id,
                        'rule_name': rule.name,
                        'trigger_count': count,
                        'severity': rule.severity.value
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"获取热门告警规则失败: {e}")
            return []


# 默认通知回调函数
def default_alert_callback(alert: Alert):
    """默认告警通知回调"""
    severity_emoji = {
        AlertSeverity.INFO: "ℹ️",
        AlertSeverity.WARNING: "⚠️",
        AlertSeverity.CRITICAL: "🔴"
    }
    
    emoji = severity_emoji.get(alert.rule.severity, "🚨")
    logger.warning(f"{emoji} 告警触发: {alert.rule.name} - {alert.message}")