#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆监控系统测试
================

测试13步记忆处理流程监控功能的完整性和性能影响。
"""

import time
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory.monitoring import (
    MemoryPipelineMonitor,
    MemoryPipelineStep,
    StepStatus,
    MonitorAnalytics,
    monitor_step,
    StepMonitorContext
)


class TestMemoryMonitoring:
    """记忆监控系统测试类"""
    
    def __init__(self):
        self.monitor = MemoryPipelineMonitor.get_instance()
        self.analytics = MonitorAnalytics(self.monitor)
        self.test_results = []
    
    def test_basic_monitoring(self):
        """测试基础监控功能"""
        print("🧪 测试1: 基础监控功能")
        
        try:
            # 开始会话
            session_id = self.monitor.start_session(user_input="测试查询")
            assert session_id is not None, "会话创建失败"
            
            # 测试步骤监控
            metrics = self.monitor.start_step(
                MemoryPipelineStep.STEP_4_CACHE_VECTORIZE,
                input_data="测试输入"
            )
            assert metrics is not None, "步骤监控启动失败"
            
            # 模拟处理时间
            time.sleep(0.1)
            
            # 完成步骤
            success = self.monitor.finish_step(
                MemoryPipelineStep.STEP_4_CACHE_VECTORIZE,
                status=StepStatus.SUCCESS,
                output_data="测试输出",
                metadata={"test_key": "test_value"}
            )
            assert success, "步骤监控完成失败"
            
            # 完成会话
            completed_session = self.monitor.finish_session(session_id)
            assert completed_session is not None, "会话完成失败"
            assert completed_session.total_duration > 0, "会话耗时计算错误"
            
            print("✅ 基础监控功能测试通过")
            self.test_results.append(("basic_monitoring", True, ""))
            
        except Exception as e:
            print(f"❌ 基础监控功能测试失败: {e}")
            self.test_results.append(("basic_monitoring", False, str(e)))
    
    def test_decorator_monitoring(self):
        """测试装饰器监控"""
        print("\n🧪 测试2: 装饰器监控功能")
        
        try:
            # 创建测试函数并应用装饰器
            @monitor_step(MemoryPipelineStep.STEP_5_FAISS_SEARCH)
            def test_search_function(query: str, k: int = 5):
                """测试搜索函数"""
                time.sleep(0.05)  # 模拟处理时间
                return [f"result_{i}" for i in range(k)]
            
            # 开始监控会话
            session_id = self.monitor.start_session(user_input="装饰器测试")
            
            # 执行被装饰的函数
            results = test_search_function("test query", k=3)
            assert len(results) == 3, "函数执行结果错误"
            
            # 检查监控数据
            session = self.monitor.get_current_session()
            assert session is not None, "当前会话不存在"
            assert MemoryPipelineStep.STEP_5_FAISS_SEARCH in session.steps, "步骤监控未记录"
            
            step_metrics = session.steps[MemoryPipelineStep.STEP_5_FAISS_SEARCH]
            assert step_metrics.status == StepStatus.SUCCESS, "步骤状态不正确"
            assert step_metrics.duration > 0, "步骤耗时未记录"
            
            # 完成会话
            self.monitor.finish_session(session_id)
            
            print("✅ 装饰器监控功能测试通过")
            self.test_results.append(("decorator_monitoring", True, ""))
            
        except Exception as e:
            print(f"❌ 装饰器监控功能测试失败: {e}")
            self.test_results.append(("decorator_monitoring", False, str(e)))
    
    def test_context_monitoring(self):
        """测试上下文管理器监控"""
        print("\n🧪 测试3: 上下文管理器监控功能")
        
        try:
            # 开始监控会话
            session_id = self.monitor.start_session(user_input="上下文测试")
            
            # 使用上下文管理器
            with StepMonitorContext(
                MemoryPipelineStep.STEP_6_ASSOCIATION_EXPAND,
                input_data={"input_count": 10},
                metadata={"test_context": True}
            ) as ctx:
                
                # 模拟处理
                time.sleep(0.03)
                processed_data = ["association_1", "association_2", "association_3"]
                
                # 设置输出和元数据
                ctx.set_output(processed_data)
                ctx.set_metadata({"output_count": len(processed_data)})
            
            # 检查监控数据
            session = self.monitor.get_current_session()
            assert session is not None, "当前会话不存在"
            assert MemoryPipelineStep.STEP_6_ASSOCIATION_EXPAND in session.steps, "步骤监控未记录"
            
            step_metrics = session.steps[MemoryPipelineStep.STEP_6_ASSOCIATION_EXPAND]
            assert step_metrics.status == StepStatus.SUCCESS, "步骤状态不正确"
            assert "test_context" in step_metrics.metadata, "元数据未记录"
            assert "output_count" in step_metrics.metadata, "输出元数据未记录"
            
            # 完成会话
            self.monitor.finish_session(session_id)
            
            print("✅ 上下文管理器监控功能测试通过")
            self.test_results.append(("context_monitoring", True, ""))
            
        except Exception as e:
            print(f"❌ 上下文管理器监控功能测试失败: {e}")
            self.test_results.append(("context_monitoring", False, str(e)))
    
    def test_performance_analytics(self):
        """测试性能分析功能"""
        print("\n🧪 测试4: 性能分析功能")
        
        try:
            # 生成一些测试数据
            for i in range(3):
                session_id = self.monitor.start_session(user_input=f"分析测试 {i+1}")
                
                # 模拟几个步骤
                steps = [
                    MemoryPipelineStep.STEP_4_CACHE_VECTORIZE,
                    MemoryPipelineStep.STEP_5_FAISS_SEARCH,
                    MemoryPipelineStep.STEP_9_CONTEXT_BUILD
                ]
                
                for step in steps:
                    self.monitor.start_step(step)
                    time.sleep(0.01 + i * 0.005)  # 递增的处理时间
                    self.monitor.finish_step(step, StepStatus.SUCCESS)
                
                self.monitor.finish_session(session_id)
            
            # 测试性能摘要
            summary = self.monitor.get_performance_summary()
            assert summary.get("total_sessions", 0) >= 3, "会话数量不正确"
            assert summary.get("average_duration", 0) > 0, "平均耗时计算错误"
            
            # 测试性能报告
            report = self.analytics.generate_performance_report()
            assert report.total_sessions >= 3, "报告会话数量不正确"
            assert len(report.slowest_steps) > 0, "最慢步骤未识别"
            
            # 测试瓶颈分析
            bottlenecks = self.analytics.analyze_bottlenecks()
            assert bottlenecks is not None, "瓶颈分析失败"
            
            print("✅ 性能分析功能测试通过")
            self.test_results.append(("performance_analytics", True, ""))
            
        except Exception as e:
            print(f"❌ 性能分析功能测试失败: {e}")
            self.test_results.append(("performance_analytics", False, str(e)))
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n🧪 测试5: 错误处理功能")
        
        try:
            # 测试步骤失败处理
            session_id = self.monitor.start_session(user_input="错误测试")
            
            self.monitor.start_step(MemoryPipelineStep.STEP_7_HISTORY_AGGREGATE)
            
            # 模拟错误
            test_error = ValueError("测试错误")
            self.monitor.finish_step(
                MemoryPipelineStep.STEP_7_HISTORY_AGGREGATE,
                status=StepStatus.FAILED,
                error=test_error
            )
            
            # 检查错误记录
            session = self.monitor.get_current_session()
            step_metrics = session.steps[MemoryPipelineStep.STEP_7_HISTORY_AGGREGATE]
            assert step_metrics.status == StepStatus.FAILED, "错误状态未记录"
            assert step_metrics.error_message == str(test_error), "错误信息未记录"
            
            # 完成会话
            completed_session = self.monitor.finish_session(session_id)
            assert completed_session.failed_count == 1, "失败计数不正确"
            
            print("✅ 错误处理功能测试通过")
            self.test_results.append(("error_handling", True, ""))
            
        except Exception as e:
            print(f"❌ 错误处理功能测试失败: {e}")
            self.test_results.append(("error_handling", False, str(e)))
    
    def test_performance_impact(self):
        """测试监控对性能的影响"""
        print("\n🧪 测试6: 监控性能影响评估")
        
        try:
            # 测试无监控的执行时间
            def simple_task():
                time.sleep(0.01)
                return "completed"
            
            # 无监控版本
            start_time = time.time()
            for _ in range(100):
                simple_task()
            no_monitor_time = time.time() - start_time
            
            # 有监控版本
            @monitor_step(MemoryPipelineStep.STEP_8_WEIGHT_RANKING)
            def monitored_task():
                time.sleep(0.01)
                return "completed"
            
            # 创建会话
            session_id = self.monitor.start_session(user_input="性能测试")
            
            start_time = time.time()
            for _ in range(100):
                monitored_task()
            monitor_time = time.time() - start_time
            
            self.monitor.finish_session(session_id)
            
            # 计算性能开销
            overhead = ((monitor_time - no_monitor_time) / no_monitor_time) * 100
            
            print(f"   无监控耗时: {no_monitor_time:.4f}s")
            print(f"   有监控耗时: {monitor_time:.4f}s")
            print(f"   性能开销: {overhead:.2f}%")
            
            # 检查开销是否在可接受范围内（<20%）
            assert overhead < 20, f"监控性能开销过高: {overhead:.2f}%"
            
            print("✅ 监控性能影响评估通过")
            self.test_results.append(("performance_impact", True, f"开销: {overhead:.2f}%"))
            
        except Exception as e:
            print(f"❌ 监控性能影响评估失败: {e}")
            self.test_results.append(("performance_impact", False, str(e)))
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始记忆监控系统完整测试")
        print("="*60)
        
        # 运行各项测试
        self.test_basic_monitoring()
        self.test_decorator_monitoring()
        self.test_context_monitoring()
        self.test_performance_analytics()
        self.test_error_handling()
        self.test_performance_impact()
        
        # 输出测试总结
        print("\n" + "="*60)
        print("📊 测试结果总结")
        print("="*60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, success, details in self.test_results:
            status = "✅ 通过" if success else "❌ 失败"
            details_str = f" ({details})" if details else ""
            print(f"{status} {test_name}{details_str}")
            if success:
                passed += 1
        
        print(f"\n测试通过率: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 所有测试通过！监控系统运行正常。")
        else:
            print("⚠️ 部分测试失败，请检查相关功能。")
        
        return passed, total


def main():
    """主测试函数"""
    try:
        # 创建并运行测试
        test_suite = TestMemoryMonitoring()
        passed, total = test_suite.run_all_tests()
        
        # 根据测试结果返回适当的退出码
        exit_code = 0 if passed == total else 1
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"\n❌ 测试运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 