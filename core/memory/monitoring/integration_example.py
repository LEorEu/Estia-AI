#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控系统集成示例
================

展示如何在EstiaMemorySystem中集成13步流程监控功能。
"""

from typing import Dict, Any, Optional, List
import logging

from .pipeline_monitor import MemoryPipelineMonitor, MemoryPipelineStep, StepStatus
from .decorators import monitor_step, StepMonitorContext
from .analytics import MonitorAnalytics

logger = logging.getLogger(__name__)


class EnhancedEstiaMemorySystem:
    """
    增强版记忆系统，集成了完整的流程监控功能
    
    这是一个示例类，展示如何在现有的EstiaMemorySystem中集成监控功能。
    """
    
    def __init__(self):
        """初始化增强版记忆系统"""
        # 初始化监控器
        self.monitor = MemoryPipelineMonitor.get_instance()
        self.analytics = MonitorAnalytics(self.monitor)
        
        # 原有组件初始化（示例）
        self.db_manager = None
        self.vectorizer = None
        self.faiss_retriever = None
        # ... 其他组件
        
        logger.info("💡 增强版记忆系统初始化完成，已集成流程监控")
    
    @monitor_step(MemoryPipelineStep.STEP_4_CACHE_VECTORIZE, 
                  capture_input=True, capture_output=True)
    def vectorize_query(self, user_input: str) -> Any:
        """
        Step 4: 统一缓存向量化
        
        使用装饰器自动监控这个步骤的执行情况
        """
        logger.debug(f"📊 开始向量化查询: {user_input[:50]}...")
        
        # 模拟向量化过程
        # vector = self.vectorizer.encode(user_input)
        vector = [0.1] * 1024  # 示例向量
        
        logger.debug(f"📊 向量化完成，维度: {len(vector)}")
        return vector
    
    def faiss_search_with_monitoring(self, query_vector: Any, k: int = 15) -> List[Dict[str, Any]]:
        """
        Step 5: FAISS向量检索（使用上下文管理器监控）
        """
        with StepMonitorContext(
            MemoryPipelineStep.STEP_5_FAISS_SEARCH,
            input_data={"vector_dim": len(query_vector), "k": k}
        ) as ctx:
            
            logger.debug(f"📊 开始FAISS检索，Top-{k}")
            
            # 模拟FAISS检索
            search_results = [
                {"memory_id": f"mem_{i}", "similarity": 0.9 - i*0.1}
                for i in range(k)
            ]
            
            # 设置输出和元数据
            ctx.set_output(search_results)
            ctx.set_metadata({
                "result_count": len(search_results),
                "avg_similarity": sum(r["similarity"] for r in search_results) / len(search_results),
                "search_threshold": 0.3
            })
            
            logger.debug(f"📊 FAISS检索完成，找到 {len(search_results)} 条结果")
            return search_results
    
    def enhance_query(self, user_input: str) -> str:
        """
        完整的查询增强流程（Steps 4-9）
        
        展示如何监控整个查询增强阶段
        """
        # Step 1: 开始监控会话
        session_id = self.monitor.start_session(user_input=user_input)
        
        try:
            # Step 4: 向量化（使用装饰器自动监控）
            query_vector = self.vectorize_query(user_input)
            
            # Step 5: FAISS检索（使用上下文管理器监控）
            search_results = self.faiss_search_with_monitoring(query_vector)
            
            # Step 6: 关联网络拓展（手动监控）
            self.monitor.start_step(MemoryPipelineStep.STEP_6_ASSOCIATION_EXPAND)
            try:
                # 模拟关联拓展
                expanded_memories = self._expand_associations(search_results)
                self.monitor.finish_step(
                    MemoryPipelineStep.STEP_6_ASSOCIATION_EXPAND,
                    output_data=expanded_memories,
                    metadata={"expansion_count": len(expanded_memories)}
                )
            except Exception as e:
                self.monitor.finish_step(
                    MemoryPipelineStep.STEP_6_ASSOCIATION_EXPAND,
                    status=StepStatus.FAILED,
                    error=e
                )
                raise
            
            # Step 7-9: 继续其他步骤...
            enhanced_context = self._build_context(expanded_memories, user_input)
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"查询增强失败: {e}")
            return f"增强失败: {str(e)}"
        finally:
            # 完成监控会话
            self.monitor.finish_session(session_id)
    
    def _expand_associations(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """模拟关联拓展"""
        return [f"assoc_{i}" for i in range(5)]
    
    def _build_context(self, memories: List[str], user_input: str) -> str:
        """模拟上下文构建"""
        return f"增强上下文：基于 {len(memories)} 条记忆，回应：{user_input}"
    
    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """
        获取监控仪表板数据
        
        返回:
            包含实时状态、性能报告和瓶颈分析的完整监控数据
        """
        dashboard = {
            "real_time_status": self.analytics.get_real_time_status(),
            "performance_summary": self.monitor.get_performance_summary()
        }
        
        # 如果有足够的历史数据，生成详细报告
        if len(self.monitor.completed_sessions) > 0:
            performance_report = self.analytics.generate_performance_report()
            bottleneck_analysis = self.analytics.analyze_bottlenecks()
            
            # 转换为字典格式
            import dataclasses
            dashboard["performance_report"] = dataclasses.asdict(performance_report)
            dashboard["bottleneck_analysis"] = dataclasses.asdict(bottleneck_analysis)
        
        return dashboard
    
    def print_monitoring_report(self):
        """打印监控报告"""
        print("\n" + "="*60)
        print("🔍 Estia 记忆系统监控报告")
        print("="*60)
        
        # 实时状态
        status = self.analytics.get_real_time_status()
        print(f"\n📊 实时状态: {status.get('status', 'unknown')}")
        
        if status.get('status') == 'running':
            print(f"   当前会话: {status.get('session_id')}")
            print(f"   当前阶段: {status.get('current_phase')}")
            print(f"   当前步骤: {status.get('current_step')}")
            print(f"   运行时间: {status.get('running_time', 0):.2f}s")
            print(f"   进度: {status.get('progress_percentage', 0):.1f}%")
        
        # 性能摘要
        summary = self.monitor.get_performance_summary()
        if summary.get('total_sessions', 0) > 0:
            print(f"\n📈 性能摘要:")
            print(f"   总会话数: {summary.get('total_sessions', 0)}")
            print(f"   平均耗时: {summary.get('average_duration', 0):.2f}s")
            print(f"   成功率: {summary.get('success_rate', 0)*100:.1f}%")
            
            if summary.get('slowest_step'):
                step_info = summary['slowest_step']
                print(f"   最慢步骤: {step_info.get('step', 'unknown')} "
                      f"({step_info.get('avg_duration', 0):.2f}s)")
        
        print("\n" + "="*60 + "\n")


# 使用示例
def demo_monitoring_system():
    """演示监控系统的使用"""
    print("🚀 启动 Estia 记忆系统监控演示")
    
    # 创建增强版记忆系统
    memory_system = EnhancedEstiaMemorySystem()
    
    # 模拟几次查询
    test_queries = [
        "今天天气怎么样？",
        "请帮我总结一下工作计划",
        "我们来聊聊人工智能的发展"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔄 执行第 {i} 次查询: {query}")
        
        try:
            result = memory_system.enhance_query(query)
            print(f"✅ 查询成功: {result}")
        except Exception as e:
            print(f"❌ 查询失败: {e}")
        
        # 打印实时监控报告
        memory_system.print_monitoring_report()
    
    # 获取完整的监控仪表板
    dashboard = memory_system.get_monitoring_dashboard()
    print("📊 完整监控数据已生成")
    
    return memory_system, dashboard


if __name__ == "__main__":
    demo_monitoring_system() 