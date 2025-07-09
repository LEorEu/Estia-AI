#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆监控系统演示脚本
==================

快速演示13步记忆处理流程监控的功能和效果。
直接运行此脚本即可看到监控数据的收集和展示。
"""

import time
import random
import json
from datetime import datetime
from typing import List, Dict, Any

# 导入监控系统
from core.memory.monitoring import (
    MemoryPipelineMonitor,
    MemoryPipelineStep,
    StepStatus,
    MonitorAnalytics,
    monitor_step,
    StepMonitorContext
)


class DemoMemorySystem:
    """演示用的记忆系统，模拟真实的处理流程"""
    
    def __init__(self):
        self.monitor = MemoryPipelineMonitor.get_instance()
        self.analytics = MonitorAnalytics(self.monitor)
        
        # 模拟数据
        self.sample_queries = [
            "今天天气怎么样？",
            "请帮我总结一下工作计划",
            "我们来聊聊人工智能的发展",
            "你能推荐一些好的学习资源吗？",
            "如何提高工作效率？",
            "最近有什么有趣的科技新闻？",
            "帮我分析一下这个项目的风险",
            "我想了解一下深度学习的应用"
        ]
        
        self.sample_memories = [
            "用户喜欢讨论技术话题",
            "工作中遇到项目管理问题",
            "对AI发展很感兴趣",
            "经常询问学习建议",
            "注重工作效率提升",
            "关注科技行业动态"
        ]
        
        print("🚀 演示记忆系统初始化完成")
    
    @monitor_step(MemoryPipelineStep.STEP_4_CACHE_VECTORIZE, 
                  capture_input=True, capture_output=True)
    def vectorize_query(self, user_input: str) -> List[float]:
        """Step 4: 模拟向量化过程"""
        print(f"  🔄 正在向量化: {user_input[:30]}...")
        
        # 模拟向量化时间
        time.sleep(random.uniform(0.05, 0.15))
        
        # 返回模拟向量
        vector = [random.random() for _ in range(512)]
        print(f"  ✅ 向量化完成，维度: {len(vector)}")
        return vector
    
    def faiss_search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Step 5: 模拟FAISS检索"""
        with StepMonitorContext(
            MemoryPipelineStep.STEP_5_FAISS_SEARCH,
            input_data={"vector_dim": len(query_vector), "k": k}
        ) as ctx:
            
            print(f"  🔍 FAISS检索 Top-{k} 相似记忆...")
            
            # 模拟检索时间
            time.sleep(random.uniform(0.03, 0.08))
            
            # 模拟检索结果
            results = []
            for i in range(k):
                memory = random.choice(self.sample_memories)
                similarity = random.uniform(0.6, 0.95)
                results.append({
                    "memory_id": f"mem_{i+1}",
                    "content": memory,
                    "similarity": similarity,
                    "timestamp": datetime.now().isoformat()
                })
            
            # 按相似度排序
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            # 设置监控数据
            ctx.set_output(results)
            ctx.set_metadata({
                "result_count": len(results),
                "avg_similarity": sum(r["similarity"] for r in results) / len(results),
                "max_similarity": max(r["similarity"] for r in results),
                "search_threshold": 0.5
            })
            
            print(f"  ✅ 找到 {len(results)} 条相关记忆")
            return results
    
    def expand_associations(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """Step 6: 模拟关联拓展"""
        self.monitor.start_step(MemoryPipelineStep.STEP_6_ASSOCIATION_EXPAND)
        
        try:
            print("  🔗 拓展关联网络...")
            time.sleep(random.uniform(0.02, 0.06))
            
            # 模拟关联拓展
            associations = []
            for result in search_results[:3]:  # 取前3个结果进行拓展
                associations.extend([
                    f"关联_{result['memory_id']}_1",
                    f"关联_{result['memory_id']}_2"
                ])
            
            self.monitor.finish_step(
                MemoryPipelineStep.STEP_6_ASSOCIATION_EXPAND,
                status=StepStatus.SUCCESS,
                output_data=associations,
                metadata={
                    "expansion_count": len(associations),
                    "source_count": len(search_results)
                }
            )
            
            print(f"  ✅ 拓展得到 {len(associations)} 个关联")
            return associations
            
        except Exception as e:
            self.monitor.finish_step(
                MemoryPipelineStep.STEP_6_ASSOCIATION_EXPAND,
                status=StepStatus.FAILED,
                error=e
            )
            raise
    
    def build_context(self, memories: List[Dict[str, Any]], 
                     associations: List[str], user_input: str) -> str:
        """Step 9: 模拟上下文构建"""
        with StepMonitorContext(
            MemoryPipelineStep.STEP_9_CONTEXT_BUILD,
            input_data={
                "memory_count": len(memories),
                "association_count": len(associations),
                "query_length": len(user_input)
            }
        ) as ctx:
            
            print("  📝 构建增强上下文...")
            time.sleep(random.uniform(0.01, 0.04))
            
            # 构建上下文
            context_parts = [
                f"用户查询: {user_input}",
                f"相关记忆 ({len(memories)}条):",
            ]
            
            for memory in memories[:3]:  # 显示前3条记忆
                context_parts.append(f"  - {memory['content']} (相似度: {memory['similarity']:.2f})")
            
            if associations:
                context_parts.append(f"关联信息 ({len(associations)}条): {', '.join(associations[:3])}")
            
            enhanced_context = "\n".join(context_parts)
            
            # 设置监控数据
            ctx.set_output(enhanced_context)
            ctx.set_metadata({
                "context_length": len(enhanced_context),
                "memory_used": len(memories),
                "associations_used": len(associations),
                "enhancement_ratio": len(enhanced_context) / len(user_input)
            })
            
            print(f"  ✅ 上下文构建完成，长度: {len(enhanced_context)} 字符")
            return enhanced_context
    
    def process_query(self, user_input: str) -> str:
        """完整的查询处理流程"""
        print(f"\n🎯 开始处理查询: {user_input}")
        print("="*60)
        
        # 开始监控会话
        session_id = self.monitor.start_session(user_input=user_input)
        
        try:
            # Step 4: 向量化
            query_vector = self.vectorize_query(user_input)
            
            # Step 5: FAISS检索
            search_results = self.faiss_search(query_vector)
            
            # Step 6: 关联拓展
            associations = self.expand_associations(search_results)
            
            # Step 9: 构建上下文
            enhanced_context = self.build_context(search_results, associations, user_input)
            
            print("\n💡 处理完成！")
            return enhanced_context
            
        except Exception as e:
            print(f"\n❌ 处理失败: {e}")
            return f"处理失败: {str(e)}"
        finally:
            # 完成会话
            self.monitor.finish_session(session_id)
    
    def print_live_monitoring(self):
        """打印实时监控信息"""
        status = self.analytics.get_real_time_status()
        
        print("\n" + "="*60)
        print("📊 实时监控状态")
        print("="*60)
        
        if status.get('status') == 'running':
            print(f"🟢 状态: 运行中")
            print(f"📋 会话ID: {status.get('session_id')}")
            print(f"⏱️  运行时间: {status.get('running_time', 0):.2f}s")
            print(f"📈 进度: {status.get('progress_percentage', 0):.1f}%")
            print(f"🎯 当前阶段: {status.get('current_phase')}")
            print(f"⚙️  当前步骤: {status.get('current_step')}")
        else:
            print(f"⚪ 状态: {status.get('status', 'idle')}")
            print(f"💬 信息: {status.get('message', '无活跃流程')}")
    
    def print_performance_summary(self):
        """打印性能摘要"""
        summary = self.monitor.get_performance_summary()
        
        print("\n" + "="*60)
        print("📈 性能摘要报告")
        print("="*60)
        
        if summary.get('total_sessions', 0) > 0:
            print(f"📊 总会话数: {summary.get('total_sessions')}")
            print(f"⏱️  平均耗时: {summary.get('average_duration', 0):.3f}s")
            print(f"✅ 成功率: {summary.get('success_rate', 0)*100:.1f}%")
            
            # 最慢的步骤
            slowest = summary.get('slowest_step', {})
            if slowest.get('step'):
                print(f"🐌 最慢步骤: {slowest['step']} ({slowest.get('avg_duration', 0):.3f}s)")
            
            # 最快的步骤
            fastest = summary.get('fastest_step', {})
            if fastest.get('step'):
                print(f"⚡ 最快步骤: {fastest['step']} ({fastest.get('avg_duration', 0):.3f}s)")
                
        else:
            print("📭 暂无历史数据")
    
    def print_detailed_analytics(self):
        """打印详细分析报告"""
        if len(self.monitor.completed_sessions) == 0:
            print("\n⚠️ 暂无足够数据进行详细分析")
            return
            
        print("\n" + "="*60)
        print("🔍 详细性能分析")
        print("="*60)
        
        # 生成性能报告
        report = self.analytics.generate_performance_report()
        
        print(f"📊 分析了 {report.total_sessions} 个会话")
        print(f"⏱️  总耗时: {report.total_duration:.3f}s")
        print(f"📈 平均耗时: {report.average_duration:.3f}s")
        print(f"✅ 成功率: {report.success_rate*100:.1f}%")
        
        # 最慢的步骤Top3
        if report.slowest_steps:
            print("\n🐌 最耗时步骤 (Top 3):")
            for i, (step, duration) in enumerate(report.slowest_steps[:3], 1):
                print(f"  {i}. {step}: {duration:.3f}s")
        
        # 失败率分析
        high_failure_steps = [(step, rate) for step, rate in report.failure_rates.items() if rate > 0]
        if high_failure_steps:
            print("\n⚠️ 存在失败的步骤:")
            for step, rate in high_failure_steps:
                print(f"  - {step}: {rate*100:.1f}% 失败率")
        
        # 优化建议
        if report.recommendations:
            print("\n💡 优化建议:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")
        
        # 瓶颈分析
        bottlenecks = self.analytics.analyze_bottlenecks()
        if bottlenecks.primary_bottleneck:
            print(f"\n🎯 主要瓶颈: {bottlenecks.primary_bottleneck}")
            print(f"📊 影响程度: {bottlenecks.bottleneck_impact:.1f}%")
            
            if bottlenecks.bottleneck_steps:
                print("\n🔧 瓶颈步骤详情:")
                for step, duration, impact in bottlenecks.bottleneck_steps:
                    print(f"  - {step}: {duration:.3f}s ({impact})")


def main():
    """主演示函数"""
    print("🎉 欢迎使用 Estia 记忆监控系统演示！")
    print("="*60)
    print("这个演示将展示13步记忆处理流程的监控功能")
    print("包括实时监控、性能分析和详细报告\n")
    
    # 创建演示系统
    demo_system = DemoMemorySystem()
    
    # 处理多个查询以生成监控数据
    print("🔄 开始处理演示查询...")
    
    for i, query in enumerate(demo_system.sample_queries[:4], 1):
        print(f"\n第 {i} 次查询 (共4次)")
        result = demo_system.process_query(query)
        
        # 显示实时监控（在处理过程中这会显示运行状态）
        time.sleep(0.1)  # 稍作延迟以便观察
    
    # 显示最终的监控报告
    demo_system.print_performance_summary()
    demo_system.print_detailed_analytics()
    
    print(f"\n" + "="*60)
    print("🎯 演示完成！")
    print("="*60)
    print("💡 接下来可以:")
    print("  1. 查看生成的监控数据")
    print("  2. 运行 Web 可视化界面 (稍后提供)")
    print("  3. 集成到实际的 EstiaMemorySystem 中")
    print("  4. 运行完整测试: python tests/test_memory_monitoring.py")
    
    # 返回监控数据供进一步分析
    return demo_system.monitor, demo_system.analytics


if __name__ == "__main__":
    main() 