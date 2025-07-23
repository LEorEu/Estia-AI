#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控系统测试
============

全面测试Estia AI性能监控系统的各个组件和功能。
"""

import os
import sys
import time
import unittest
import threading
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.monitoring.performance_monitor import PerformanceMonitor, PerformanceMetrics
from core.monitoring.metrics_collector import MetricsCollector, MetricPoint
from core.monitoring.alert_manager import AlertManager, AlertRule, AlertSeverity, Alert
from core.monitoring.dashboard_server import DashboardServer
from core.monitoring.memory_integration import MemorySystemMonitor


class TestPerformanceMonitor(unittest.TestCase):
    """测试性能监控器"""
    
    def setUp(self):
        """测试初始化"""
        self.monitor = PerformanceMonitor(collection_interval=0.1)
    
    def tearDown(self):
        """测试清理"""
        if self.monitor.monitoring_active:
            self.monitor.stop_monitoring()
    
    def test_monitor_initialization(self):
        """测试监控器初始化"""
        self.assertIsNotNone(self.monitor)
        self.assertFalse(self.monitor.monitoring_active)
        self.assertEqual(self.monitor.collection_interval, 0.1)
    
    def test_start_stop_monitoring(self):
        """测试启动和停止监控"""
        # 测试启动
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.monitoring_active)
        self.assertIsNotNone(self.monitor.monitoring_thread)
        
        # 等待一些监控数据收集
        time.sleep(0.5)
        
        # 测试停止
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring_active)
    
    def test_record_operation(self):
        """测试操作记录"""
        # 记录成功操作
        self.monitor.record_operation("test_operation", 100.5, True)
        
        # 记录失败操作
        self.monitor.record_operation("test_operation", 200.0, False)
        
        # 验证记录
        self.assertEqual(self.monitor.operation_counters["test_operation"], 2)
        self.assertEqual(len(self.monitor.operation_timings["test_operation"]), 2)
        self.assertEqual(self.monitor.error_counters["test_operation"], 1)
    
    def test_get_current_metrics(self):
        """测试获取当前指标"""
        metrics = self.monitor.get_current_metrics()
        self.assertIsInstance(metrics, PerformanceMetrics)
        self.assertGreaterEqual(metrics.timestamp, 0)
    
    def test_performance_summary(self):
        """测试性能摘要"""
        # 记录一些操作数据
        self.monitor.record_operation("query", 50.0, True)
        self.monitor.record_operation("query", 75.0, True)
        self.monitor.record_operation("storage", 25.0, False)
        
        summary = self.monitor.get_performance_summary()
        
        self.assertIn('current_metrics', summary)
        self.assertIn('operation_statistics', summary)
        self.assertIn('monitoring_active', summary)
        
        # 验证操作统计
        self.assertIn('query', summary['operation_statistics'])
        self.assertIn('storage', summary['operation_statistics'])


class TestMetricsCollector(unittest.TestCase):
    """测试指标收集器"""
    
    def setUp(self):
        """测试初始化"""
        self.collector = MetricsCollector(collection_interval=0.1)
    
    def tearDown(self):
        """测试清理"""
        if self.collector.collecting:
            self.collector.stop_collection()
    
    def test_collector_initialization(self):
        """测试收集器初始化"""
        self.assertIsNotNone(self.collector)
        self.assertFalse(self.collector.collecting)
        self.assertEqual(self.collector.collection_interval, 0.1)
    
    def test_start_stop_collection(self):
        """测试启动和停止收集"""
        # 测试启动
        self.collector.start_collection()
        self.assertTrue(self.collector.collecting)
        self.assertIsNotNone(self.collector.collection_thread)
        
        # 等待收集一些数据
        time.sleep(0.5)
        
        # 测试停止
        self.collector.stop_collection()
        self.assertFalse(self.collector.collecting)
    
    def test_record_metric(self):
        """测试记录指标"""
        # 记录指标
        self.collector.record_metric("test.metric", 42.5)
        self.collector.record_metric("test.metric", 43.0)
        
        # 验证记录
        self.assertEqual(self.collector.get_current_value("test.metric"), 43.0)
        
        history = self.collector.get_metric_history("test.metric", 60)
        self.assertEqual(len(history), 2)
        self.assertIsInstance(history[0], MetricPoint)
    
    def test_custom_collector(self):
        """测试自定义收集器"""
        def custom_metrics():
            return {
                "custom.cpu": 50.0,
                "custom.memory": 1024.0
            }
        
        # 添加自定义收集器
        self.collector.add_custom_collector(custom_metrics)
        self.assertEqual(len(self.collector.custom_collectors), 1)
        
        # 启动收集并验证
        self.collector.start_collection()
        time.sleep(0.3)
        
        # 检查自定义指标是否被收集
        self.assertIsNotNone(self.collector.get_current_value("custom.custom.cpu"))
        self.assertIsNotNone(self.collector.get_current_value("custom.custom.memory"))
    
    def test_metric_summary(self):
        """测试指标摘要"""
        # 记录一系列指标
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        for value in values:
            self.collector.record_metric("test.summary", value)
            time.sleep(0.01)  # 小延迟确保时间戳不同
        
        summary = self.collector.get_metric_summary("test.summary", 60)
        
        self.assertEqual(summary['count'], 5)
        self.assertEqual(summary['min'], 10.0)
        self.assertEqual(summary['max'], 50.0)
        self.assertEqual(summary['avg'], 30.0)
        self.assertEqual(summary['current'], 50.0)


class TestAlertManager(unittest.TestCase):
    """测试告警管理器"""
    
    def setUp(self):
        """测试初始化"""
        self.alert_manager = AlertManager()
    
    def test_alert_manager_initialization(self):
        """测试告警管理器初始化"""
        self.assertIsNotNone(self.alert_manager)
        self.assertGreater(len(self.alert_manager.rules), 0)  # 应该有默认规则
    
    def test_add_custom_rule(self):
        """测试添加自定义规则"""
        rule = AlertRule(
            rule_id="test_rule",
            name="测试规则",
            description="测试用的告警规则",
            metric_name="test.metric",
            condition="gt",
            threshold=100.0,
            severity=AlertSeverity.WARNING
        )
        
        success = self.alert_manager.add_rule(rule)
        self.assertTrue(success)
        self.assertIn("test_rule", self.alert_manager.rules)
    
    def test_check_metrics_no_violation(self):
        """测试指标检查 - 无违规"""
        metrics = {
            "cpu_usage": 50.0,  # 低于80%阈值
            "memory_usage_percent": 60.0,  # 低于85%阈值
            "error_rate": 0.01  # 低于5%阈值
        }
        
        alerts = self.alert_manager.check_metrics(metrics)
        self.assertEqual(len(alerts), 0)
    
    def test_check_metrics_with_violation(self):
        """测试指标检查 - 有违规"""
        # 添加一个容易触发的测试规则
        test_rule = AlertRule(
            rule_id="test_violation",
            name="测试违规",
            description="测试违规规则",
            metric_name="test_value",
            condition="gt",
            threshold=50.0,
            severity=AlertSeverity.WARNING,
            consecutive_violations=1,  # 立即触发
            cooldown_seconds=1  # 短冷却时间
        )
        
        self.alert_manager.add_rule(test_rule)
        
        # 触发违规
        metrics = {"test_value": 75.0}  # 超过50.0阈值
        alerts = self.alert_manager.check_metrics(metrics)
        
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0].rule.rule_id, "test_violation")
        self.assertEqual(alerts[0].current_value, 75.0)
    
    def test_acknowledge_resolve_alert(self):
        """测试确认和解决告警"""
        # 先创建一个告警
        test_rule = AlertRule(
            rule_id="test_ack",
            name="测试确认",
            description="测试确认规则",
            metric_name="test_ack",
            condition="gt",
            threshold=10.0,
            severity=AlertSeverity.INFO,
            consecutive_violations=1
        )
        
        self.alert_manager.add_rule(test_rule)
        
        # 触发告警
        alerts = self.alert_manager.check_metrics({"test_ack": 20.0})
        self.assertGreater(len(alerts), 0)
        
        alert_id = alerts[0].alert_id
        
        # 确认告警
        success = self.alert_manager.acknowledge_alert(alert_id, "test_user")
        self.assertTrue(success)
        
        # 解决告警
        success = self.alert_manager.resolve_alert(alert_id)
        self.assertTrue(success)
        
        # 验证告警不再活跃
        active_alerts = self.alert_manager.get_active_alerts()
        active_ids = [alert.alert_id for alert in active_alerts]
        self.assertNotIn(alert_id, active_ids)
    
    def test_alert_statistics(self):
        """测试告警统计"""
        stats = self.alert_manager.get_alert_statistics()
        
        self.assertIn('active_alerts', stats)
        self.assertIn('total_rules', stats)
        self.assertIn('enabled_rules', stats)
        self.assertIn('severity_distribution', stats)


class TestMemorySystemMonitor(unittest.TestCase):
    """测试记忆系统监控集成"""
    
    def setUp(self):
        """测试初始化"""
        # 创建模拟的记忆系统
        self.mock_memory_system = Mock()
        self.mock_memory_system.get_system_stats.return_value = {
            'total_memories': 100,
            'active_memories': 80,
            'archived_memories': 20,
            'unified_cache': {
                'hit_count': 90,
                'access_count': 100,
                'size': 50
            },
            'components': {
                'db_manager': True,
                'vectorizer': True,
                'faiss_retriever': True
            },
            'async_queue': {
                'active_sessions': ['session1', 'session2']
            }
        }
        
        self.monitor = MemorySystemMonitor(
            memory_system=self.mock_memory_system,
            enable_dashboard=False  # 禁用仪表板避免端口冲突
        )
    
    def tearDown(self):
        """测试清理"""
        if self.monitor.monitoring_active:
            self.monitor.stop_monitoring()
    
    def test_monitor_initialization(self):
        """测试监控器初始化"""
        self.assertIsNotNone(self.monitor)
        self.assertIsNotNone(self.monitor.metrics_collector)
        self.assertIsNotNone(self.monitor.performance_monitor)
        self.assertIsNotNone(self.monitor.alert_manager)
    
    def test_start_stop_monitoring(self):
        """测试启动和停止监控"""
        # 启动监控
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.monitoring_active)
        
        # 等待收集数据
        time.sleep(0.5)
        
        # 停止监控
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring_active)
    
    def test_monitor_operation_context(self):
        """测试操作监控上下文"""
        self.monitor.start_monitoring()
        
        # 使用监控上下文
        with self.monitor.monitor_operation("test_operation") as ctx:
            ctx.set_result_size(100)
            ctx.set_processed_count(50)
            ctx.set_cache_hit_rate(0.8)
            time.sleep(0.1)  # 模拟操作耗时
        
        # 验证指标被记录
        duration_metric = self.monitor.metrics_collector.get_current_value(
            'operations.test_operation.duration_ms'
        )
        self.assertIsNotNone(duration_metric)
        self.assertGreater(duration_metric, 50)  # 至少50ms
    
    def test_monitoring_status(self):
        """测试监控状态获取"""
        self.monitor.start_monitoring()
        time.sleep(0.3)
        
        status = self.monitor.get_monitoring_status()
        
        self.assertIn('monitoring_active', status)
        self.assertIn('current_metrics', status)
        self.assertIn('alert_summary', status)
        self.assertIn('collector_summary', status)
        self.assertTrue(status['monitoring_active'])
    
    def test_comprehensive_report(self):
        """测试综合报告生成"""
        self.monitor.start_monitoring()
        time.sleep(0.3)
        
        report = self.monitor.get_comprehensive_report()
        
        self.assertIn('system_overview', report)
        self.assertIn('performance_summary', report)
        self.assertIn('alert_statistics', report)
        self.assertIn('health_status', report)
        self.assertIn('recommendations', report)


class TestDashboardServer(unittest.TestCase):
    """测试仪表板服务器"""
    
    def setUp(self):
        """测试初始化"""
        # 使用一个不常用的端口避免冲突
        self.dashboard = DashboardServer(port=18080)
    
    def tearDown(self):
        """测试清理"""
        if self.dashboard.running:
            self.dashboard.stop()
    
    def test_dashboard_initialization(self):
        """测试仪表板初始化"""
        self.assertIsNotNone(self.dashboard)
        self.assertEqual(self.dashboard.port, 18080)
        self.assertFalse(self.dashboard.running)
    
    def test_start_stop_dashboard(self):
        """测试启动和停止仪表板"""
        # 启动仪表板
        self.dashboard.start()
        self.assertTrue(self.dashboard.running)
        
        # 等待启动完成
        time.sleep(0.5)
        
        # 停止仪表板
        self.dashboard.stop()
        self.assertFalse(self.dashboard.running)
    
    def test_dashboard_url(self):
        """测试仪表板URL生成"""
        url = self.dashboard.get_dashboard_url()
        self.assertEqual(url, "http://localhost:18080/dashboard")


def run_comprehensive_test():
    """运行综合测试"""
    print("🧪 开始Estia AI监控系统综合测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_classes = [
        TestPerformanceMonitor,
        TestMetricsCollector,
        TestAlertManager,
        TestMemorySystemMonitor,
        TestDashboardServer
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 测试结果摘要
    print("\n" + "=" * 60)
    print("📊 测试结果摘要:")
    print(f"总测试数: {result.testsRun}")
    print(f"成功数: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, trace in result.failures:
            print(f"  - {test}: {trace.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n🚨 错误的测试:")
        for test, trace in result.errors:
            print(f"  - {test}: {trace.split('Exception:')[-1].strip()}")
    
    # 总体结果
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！监控系统运行正常。")
        return True
    else:
        print("\n❌ 部分测试失败，请检查监控系统。")
        return False


if __name__ == "__main__":
    # 检查依赖
    try:
        import psutil
    except ImportError:
        print("⚠️ 缺少psutil依赖，某些系统指标测试可能失败")
        print("请运行: pip install psutil")
    
    # 运行测试
    success = run_comprehensive_test()
    
    if success:
        print("\n🎉 监控系统测试完成，所有功能正常！")
        print("\n📊 现在可以使用以下方式启动监控系统:")
        print("```python")
        print("from core.monitoring import MemorySystemMonitor")
        print("monitor = MemorySystemMonitor(memory_system=your_memory_system)")
        print("monitor.start_monitoring()")
        print("print(f'仪表板地址: {monitor.dashboard_server.get_dashboard_url()}')")
        print("```")
    else:
        sys.exit(1)