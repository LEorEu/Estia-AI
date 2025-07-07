#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控数据分析模块
================

提供监控数据的分析、报告生成和性能优化建议功能。
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import logging

from .pipeline_monitor import (
    MemoryPipelineMonitor,
    MemoryPipelineStep,
    StepStatus,
    PipelineSession
)

logger = logging.getLogger(__name__)


@dataclass
class PerformanceReport:
    """性能报告数据类"""
    # 总体统计
    total_sessions: int
    total_duration: float
    average_duration: float
    success_rate: float
    
    # 步骤分析
    slowest_steps: List[Tuple[str, float]]  # (step_name, avg_duration)
    fastest_steps: List[Tuple[str, float]]
    failure_rates: Dict[str, float]  # step_name -> failure_rate
    
    # 阶段分析
    phase_performance: Dict[str, Dict[str, Any]]
    
    # 趋势分析
    performance_trends: Dict[str, List[float]]  # step_name -> [durations]
    
    # 告警和建议
    alerts: List[Dict[str, Any]]
    recommendations: List[str]


@dataclass
class BottleneckAnalysis:
    """瓶颈分析结果"""
    # 主要瓶颈
    primary_bottleneck: Optional[str]
    bottleneck_impact: float  # 对总时间的影响百分比
    
    # 瓶颈详情
    bottleneck_steps: List[Tuple[str, float, str]]  # (step, duration, impact_desc)
    
    # 优化建议
    optimization_suggestions: List[Dict[str, Any]]
    
    # 资源使用分析
    memory_usage_analysis: Dict[str, Any]
    cache_performance: Dict[str, Any]


class MonitorAnalytics:
    """
    监控数据分析器
    
    提供性能分析、瓶颈识别和优化建议功能。
    """
    
    def __init__(self, monitor: Optional[MemoryPipelineMonitor] = None):
        """
        初始化分析器
        
        参数:
            monitor: 监控器实例，如果为None则使用单例
        """
        self.monitor = monitor or MemoryPipelineMonitor.get_instance()
        
    def generate_performance_report(self, 
                                  recent_sessions_only: bool = True,
                                  session_limit: int = 100) -> PerformanceReport:
        """
        生成性能报告
        
        参数:
            recent_sessions_only: 是否只分析最近的会话
            session_limit: 分析的会话数量限制
            
        返回:
            性能报告对象
        """
        sessions = self._get_analysis_sessions(recent_sessions_only, session_limit)
        
        if not sessions:
            return PerformanceReport(
                total_sessions=0,
                total_duration=0.0,
                average_duration=0.0,
                success_rate=0.0,
                slowest_steps=[],
                fastest_steps=[],
                failure_rates={},
                phase_performance={},
                performance_trends={},
                alerts=[],
                recommendations=["暂无历史数据，建议运行更多查询以收集性能数据"]
            )
        
        # 总体统计
        total_sessions = len(sessions)
        total_duration = sum(s.total_duration or 0 for s in sessions)
        average_duration = total_duration / total_sessions if total_sessions > 0 else 0
        success_rate = sum(1 for s in sessions if s.failed_count == 0) / total_sessions
        
        # 步骤性能分析
        step_stats = self._analyze_step_performance(sessions)
        slowest_steps = sorted(step_stats.items(), key=lambda x: x[1]['avg_duration'], reverse=True)[:5]
        fastest_steps = sorted(step_stats.items(), key=lambda x: x[1]['avg_duration'])[:5]
        
        slowest_steps = [(step, stats['avg_duration']) for step, stats in slowest_steps]
        fastest_steps = [(step, stats['avg_duration']) for step, stats in fastest_steps]
        
        # 失败率分析
        failure_rates = {step: stats.get('failure_rate', 0.0) for step, stats in step_stats.items()}
        
        # 阶段性能分析
        phase_performance = self._analyze_phase_performance(sessions)
        
        # 趋势分析
        performance_trends = self._analyze_performance_trends(sessions)
        
        # 生成告警和建议
        alerts = self._generate_alerts(step_stats, average_duration)
        recommendations = self._generate_recommendations(step_stats, phase_performance, success_rate)
        
        return PerformanceReport(
            total_sessions=total_sessions,
            total_duration=total_duration,
            average_duration=average_duration,
            success_rate=success_rate,
            slowest_steps=slowest_steps,
            fastest_steps=fastest_steps,
            failure_rates=failure_rates,
            phase_performance=phase_performance,
            performance_trends=performance_trends,
            alerts=alerts,
            recommendations=recommendations
        )
    
    def analyze_bottlenecks(self, 
                           recent_sessions_only: bool = True,
                           session_limit: int = 50) -> BottleneckAnalysis:
        """
        分析性能瓶颈
        
        参数:
            recent_sessions_only: 是否只分析最近的会话
            session_limit: 分析的会话数量限制
            
        返回:
            瓶颈分析结果
        """
        sessions = self._get_analysis_sessions(recent_sessions_only, session_limit)
        
        if not sessions:
            return BottleneckAnalysis(
                primary_bottleneck=None,
                bottleneck_impact=0.0,
                bottleneck_steps=[],
                optimization_suggestions=[],
                memory_usage_analysis={},
                cache_performance={}
            )
        
        # 分析步骤耗时
        step_stats = self._analyze_step_performance(sessions)
        
        # 识别主要瓶颈
        primary_bottleneck = None
        max_impact = 0.0
        total_avg_duration = sum(stats['avg_duration'] for stats in step_stats.values())
        
        for step, stats in step_stats.items():
            impact = (stats['avg_duration'] / total_avg_duration) * 100 if total_avg_duration > 0 else 0
            if impact > max_impact:
                max_impact = impact
                primary_bottleneck = step
        
        # 识别瓶颈步骤
        bottleneck_steps = []
        for step, stats in step_stats.items():
            duration = stats['avg_duration']
            impact = (duration / total_avg_duration) * 100 if total_avg_duration > 0 else 0
            
            if impact > 20:  # 超过20%的时间占比认为是瓶颈
                impact_desc = self._get_impact_description(impact)
                bottleneck_steps.append((step, duration, impact_desc))
        
        bottleneck_steps.sort(key=lambda x: x[1], reverse=True)
        
        # 生成优化建议
        optimization_suggestions = self._generate_optimization_suggestions(step_stats, bottleneck_steps)
        
        # 内存使用分析
        memory_usage_analysis = self._analyze_memory_usage(sessions)
        
        # 缓存性能分析
        cache_performance = self._analyze_cache_performance(sessions)
        
        return BottleneckAnalysis(
            primary_bottleneck=primary_bottleneck,
            bottleneck_impact=max_impact,
            bottleneck_steps=bottleneck_steps,
            optimization_suggestions=optimization_suggestions,
            memory_usage_analysis=memory_usage_analysis,
            cache_performance=cache_performance
        )
    
    def get_real_time_status(self) -> Dict[str, Any]:
        """获取实时状态信息"""
        current_session = self.monitor.get_current_session()
        
        if current_session is None:
            return {
                "status": "idle",
                "message": "没有活跃的处理流程"
            }
        
        session_status = self.monitor.get_session_status()
        running_time = time.time() - current_session.start_time
        
        # 预测剩余时间
        estimated_total_time = self._estimate_total_time(current_session)
        estimated_remaining = max(0, estimated_total_time - running_time)
        
        return {
            "status": "running",
            "session_id": current_session.session_id,
            "current_phase": current_session.phase,
            "current_step": current_session.current_step.value if current_session.current_step else None,
            "running_time": running_time,
            "estimated_remaining": estimated_remaining,
            "completed_steps": session_status.get("completed_steps", 0),
            "success_count": current_session.success_count,
            "failed_count": current_session.failed_count,
            "progress_percentage": self._calculate_progress(current_session)
        }
    
    def export_performance_data(self, format: str = "dict") -> Any:
        """
        导出性能数据
        
        参数:
            format: 导出格式 ("dict", "json", "csv")
            
        返回:
            导出的数据
        """
        performance_summary = self.monitor.get_performance_summary()
        
        if format == "dict":
            return performance_summary
        elif format == "json":
            import json
            return json.dumps(performance_summary, indent=2, ensure_ascii=False)
        elif format == "csv":
            return self._export_to_csv(performance_summary)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def _get_analysis_sessions(self, recent_only: bool, limit: int) -> List[PipelineSession]:
        """获取用于分析的会话列表"""
        sessions = self.monitor.completed_sessions
        
        if recent_only and sessions:
            # 按时间排序，取最近的会话
            sessions = sorted(sessions, key=lambda s: s.start_time, reverse=True)
        
        return sessions[:limit] if limit > 0 else sessions
    
    def _analyze_step_performance(self, sessions: List[PipelineSession]) -> Dict[str, Dict[str, Any]]:
        """分析步骤性能"""
        step_data = defaultdict(list)
        step_failures = defaultdict(int)
        step_total = defaultdict(int)
        
        for session in sessions:
            for step, metrics in session.steps.items():
                step_name = step.value
                step_total[step_name] += 1
                
                if metrics.duration:
                    step_data[step_name].append(metrics.duration)
                
                if metrics.status == StepStatus.FAILED:
                    step_failures[step_name] += 1
        
        # 计算统计信息
        step_stats = {}
        for step_name, durations in step_data.items():
            if durations:
                step_stats[step_name] = {
                    'count': len(durations),
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'failure_rate': step_failures[step_name] / step_total[step_name] if step_total[step_name] > 0 else 0
                }
        
        return step_stats
    
    def _analyze_phase_performance(self, sessions: List[PipelineSession]) -> Dict[str, Dict[str, Any]]:
        """分析阶段性能"""
        phase_durations = defaultdict(list)
        
        for session in sessions:
            phase_times = {"initialization": 0.0, "query_enhancement": 0.0, "storage_evaluation": 0.0}
            
            for step, metrics in session.steps.items():
                if metrics.duration:
                    phase = session.get_phase_by_step(step)
                    phase_times[phase] += metrics.duration
            
            for phase, duration in phase_times.items():
                if duration > 0:
                    phase_durations[phase].append(duration)
        
        # 计算阶段统计
        phase_stats = {}
        for phase, durations in phase_durations.items():
            if durations:
                phase_stats[phase] = {
                    'count': len(durations),
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'total_duration': sum(durations)
                }
        
        return phase_stats
    
    def _analyze_performance_trends(self, sessions: List[PipelineSession]) -> Dict[str, List[float]]:
        """分析性能趋势"""
        trends = defaultdict(list)
        
        # 按时间排序会话
        sorted_sessions = sorted(sessions, key=lambda s: s.start_time)
        
        for session in sorted_sessions:
            for step, metrics in session.steps.items():
                if metrics.duration:
                    trends[step.value].append(metrics.duration)
        
        return dict(trends)
    
    def _generate_alerts(self, step_stats: Dict[str, Dict[str, Any]], avg_duration: float) -> List[Dict[str, Any]]:
        """生成性能告警"""
        alerts = []
        
        # 超时告警
        for step_name, stats in step_stats.items():
            if stats['avg_duration'] > 5.0:  # 超过5秒
                alerts.append({
                    "type": "performance",
                    "level": "warning",
                    "step": step_name,
                    "message": f"步骤 {step_name} 平均耗时过长: {stats['avg_duration']:.2f}s",
                    "suggestion": "考虑优化该步骤的实现或增加缓存"
                })
        
        # 失败率告警
        for step_name, stats in step_stats.items():
            if stats['failure_rate'] > 0.1:  # 失败率超过10%
                alerts.append({
                    "type": "reliability",
                    "level": "error",
                    "step": step_name,
                    "message": f"步骤 {step_name} 失败率过高: {stats['failure_rate']*100:.1f}%",
                    "suggestion": "检查该步骤的错误处理和容错机制"
                })
        
        return alerts
    
    def _generate_recommendations(self, step_stats: Dict[str, Dict[str, Any]], 
                                phase_stats: Dict[str, Dict[str, Any]], 
                                success_rate: float) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于成功率的建议
        if success_rate < 0.9:
            recommendations.append("系统成功率偏低，建议检查错误处理机制和系统稳定性")
        
        # 基于步骤性能的建议
        slow_steps = [(name, stats) for name, stats in step_stats.items() 
                     if stats['avg_duration'] > 2.0]
        
        if slow_steps:
            recommendations.append("以下步骤耗时较长，建议优化：" + 
                                 ", ".join([f"{name}({stats['avg_duration']:.2f}s)" 
                                           for name, stats in slow_steps[:3]]))
        
        # 基于阶段性能的建议
        if phase_stats:
            slowest_phase = max(phase_stats.items(), key=lambda x: x[1]['avg_duration'])
            recommendations.append(f"阶段 {slowest_phase[0]} 是主要性能瓶颈，"
                                 f"平均耗时 {slowest_phase[1]['avg_duration']:.2f}s")
        
        return recommendations
    
    def _generate_optimization_suggestions(self, step_stats: Dict[str, Dict[str, Any]], 
                                         bottleneck_steps: List[Tuple[str, float, str]]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []
        
        for step_name, duration, impact_desc in bottleneck_steps:
            suggestion = {
                "step": step_name,
                "impact": impact_desc,
                "suggestions": []
            }
            
            # 根据步骤类型生成具体建议
            if "vectorize" in step_name.lower():
                suggestion["suggestions"].extend([
                    "增加向量缓存容量",
                    "使用更快的向量化模型",
                    "实现批量向量化"
                ])
            elif "search" in step_name.lower():
                suggestion["suggestions"].extend([
                    "优化FAISS索引配置",
                    "调整检索参数",
                    "增加并行检索"
                ])
            elif "association" in step_name.lower():
                suggestion["suggestions"].extend([
                    "限制关联深度",
                    "优化关联算法",
                    "增加关联缓存"
                ])
            
            suggestions.append(suggestion)
        
        return suggestions
    
    def _analyze_memory_usage(self, sessions: List[PipelineSession]) -> Dict[str, Any]:
        """分析内存使用情况"""
        memory_data = []
        
        for session in sessions:
            for metrics in session.steps.values():
                if metrics.memory_usage:
                    memory_data.append(metrics.memory_usage)
        
        if not memory_data:
            return {"message": "没有内存使用数据"}
        
        return {
            "avg_memory_usage": sum(memory_data) / len(memory_data),
            "max_memory_usage": max(memory_data),
            "min_memory_usage": min(memory_data),
            "memory_trend": "stable"  # 简化实现
        }
    
    def _analyze_cache_performance(self, sessions: List[PipelineSession]) -> Dict[str, Any]:
        """分析缓存性能"""
        cache_data = []
        
        for session in sessions:
            for metrics in session.steps.values():
                if metrics.cache_hit_rate is not None:
                    cache_data.append(metrics.cache_hit_rate)
        
        if not cache_data:
            return {"message": "没有缓存性能数据"}
        
        return {
            "avg_hit_rate": sum(cache_data) / len(cache_data),
            "cache_efficiency": "good" if sum(cache_data) / len(cache_data) > 0.8 else "needs_improvement"
        }
    
    def _estimate_total_time(self, session: PipelineSession) -> float:
        """估算总完成时间"""
        # 基于历史数据估算，简化实现
        if not self.monitor.completed_sessions:
            return 10.0  # 默认估算
        
        avg_duration = sum(s.total_duration or 0 for s in self.monitor.completed_sessions) / len(self.monitor.completed_sessions)
        return avg_duration
    
    def _calculate_progress(self, session: PipelineSession) -> float:
        """计算进度百分比"""
        total_steps = 14  # 总共14个步骤
        completed = session.success_count + session.failed_count + session.skipped_count
        return min(100.0, (completed / total_steps) * 100)
    
    def _get_impact_description(self, impact_percentage: float) -> str:
        """获取影响程度描述"""
        if impact_percentage > 50:
            return "严重影响"
        elif impact_percentage > 30:
            return "中等影响"
        elif impact_percentage > 20:
            return "轻微影响"
        else:
            return "影响较小"
    
    def _export_to_csv(self, data: Dict[str, Any]) -> str:
        """导出为CSV格式"""
        # 简化的CSV导出实现
        lines = ["metric,value"]
        
        def flatten_dict(d, prefix=""):
            result = []
            for k, v in d.items():
                key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    result.extend(flatten_dict(v, key))
                else:
                    result.append(f"{key},{v}")
            return result
        
        csv_lines = flatten_dict(data)
        lines.extend(csv_lines)
        return "\n".join(lines) 