#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆流程监控器
==============

实现13步记忆处理流程的完整监控，包括状态跟踪、性能测量和错误监控。
"""

import time
import uuid
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MemoryPipelineStep(Enum):
    """13步记忆处理流程枚举"""
    # 阶段一：系统初始化 (Step 1-3)
    STEP_1_DB_INIT = "step_1_database_initialization"
    STEP_2_COMPONENT_INIT = "step_2_component_initialization" 
    STEP_3_ASYNC_INIT = "step_3_async_evaluator_initialization"
    
    # 阶段二：实时记忆增强 (Step 4-9) - 查询阶段
    STEP_4_CACHE_VECTORIZE = "step_4_unified_cache_vectorization"
    STEP_5_FAISS_SEARCH = "step_5_faiss_vector_retrieval"
    STEP_6_ASSOCIATION_EXPAND = "step_6_association_network_expansion"
    STEP_7_HISTORY_AGGREGATE = "step_7_history_dialogue_aggregation"
    STEP_8_WEIGHT_RANKING = "step_8_weight_ranking_deduplication"
    STEP_9_CONTEXT_BUILD = "step_9_final_context_assembly"
    
    # 阶段三：对话存储与异步评估 (Step 10-14) - 存储阶段
    STEP_10_LLM_GENERATE = "step_10_llm_response_generation"
    STEP_11_IMMEDIATE_STORE = "step_11_immediate_dialogue_storage"
    STEP_12_ASYNC_EVALUATE = "step_12_async_llm_evaluation"
    STEP_13_SAVE_RESULTS = "step_13_save_evaluation_results"
    STEP_14_CREATE_ASSOCIATIONS = "step_14_auto_association_creation"


class StepStatus(Enum):
    """步骤执行状态"""
    PENDING = "pending"          # 等待执行
    RUNNING = "running"          # 正在执行
    SUCCESS = "success"          # 执行成功
    FAILED = "failed"            # 执行失败
    SKIPPED = "skipped"          # 跳过执行
    TIMEOUT = "timeout"          # 执行超时


@dataclass
class MonitorMetrics:
    """监控指标数据类"""
    # 基础信息
    step: MemoryPipelineStep
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    status: StepStatus = StepStatus.PENDING
    
    # 性能指标
    duration: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    
    # 业务指标
    input_size: Optional[int] = None
    output_size: Optional[int] = None
    processed_count: Optional[int] = None
    cache_hit_rate: Optional[float] = None
    
    # 错误信息
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    
    # 扩展元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def finish(self, status: StepStatus, error: Optional[Exception] = None):
        """标记步骤完成"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status
        
        if error:
            self.error_message = str(error)
            self.error_traceback = getattr(error, '__traceback__', None)


@dataclass  
class PipelineSession:
    """流程会话，跟踪一次完整的记忆处理过程"""
    session_id: str
    start_time: float
    phase: str  # 'initialization', 'query_enhancement', 'storage_evaluation'
    
    # 步骤监控
    steps: Dict[MemoryPipelineStep, MonitorMetrics] = field(default_factory=dict)
    current_step: Optional[MemoryPipelineStep] = None
    
    # 会话级指标
    total_duration: Optional[float] = None
    success_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    
    # 业务上下文
    user_input: Optional[str] = None
    ai_response: Optional[str] = None
    enhanced_context_size: Optional[int] = None
    retrieved_memories_count: Optional[int] = None
    
    def get_phase_by_step(self, step: MemoryPipelineStep) -> str:
        """根据步骤获取所属阶段"""
        if step in [MemoryPipelineStep.STEP_1_DB_INIT, 
                   MemoryPipelineStep.STEP_2_COMPONENT_INIT,
                   MemoryPipelineStep.STEP_3_ASYNC_INIT]:
            return "initialization"
        elif step in [MemoryPipelineStep.STEP_4_CACHE_VECTORIZE,
                     MemoryPipelineStep.STEP_5_FAISS_SEARCH,
                     MemoryPipelineStep.STEP_6_ASSOCIATION_EXPAND,
                     MemoryPipelineStep.STEP_7_HISTORY_AGGREGATE, 
                     MemoryPipelineStep.STEP_8_WEIGHT_RANKING,
                     MemoryPipelineStep.STEP_9_CONTEXT_BUILD]:
            return "query_enhancement"
        else:
            return "storage_evaluation"


class MemoryPipelineMonitor:
    """
    记忆流程监控器
    
    负责监控13步记忆处理流程的执行状态、性能指标和错误信息。
    支持实时监控、历史分析和性能优化建议。
    """
    
    # 单例模式
    _instance = None
    _lock = threading.RLock()
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """初始化监控器"""
        # 会话管理
        self.sessions: Dict[str, PipelineSession] = {}
        self.current_session_id: Optional[str] = None
        
        # 历史数据
        self.completed_sessions: List[PipelineSession] = []
        self.max_history_size = 1000  # 最大历史记录数
        
        # 性能统计
        self.step_statistics: Dict[MemoryPipelineStep, Dict[str, Any]] = defaultdict(dict)
        self.phase_statistics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # 监控配置
        self.config = {
            "enable_memory_tracking": True,
            "enable_cpu_tracking": False,  # CPU跟踪可选，避免性能影响
            "step_timeout_seconds": 60,    # 步骤超时时间
            "enable_detailed_logging": True,
            "performance_threshold": {      # 性能告警阈值
                "step_duration_ms": 5000,   # 单步骤超过5秒告警
                "total_duration_ms": 30000, # 总流程超过30秒告警
                "memory_usage_mb": 500       # 内存使用超过500MB告警
            }
        }
        
        # 线程安全
        self._lock = threading.RLock()
        
        logger.info("📊 记忆流程监控器初始化完成")
    
    def start_session(self, session_id: Optional[str] = None, 
                     user_input: Optional[str] = None) -> str:
        """
        开始新的监控会话
        
        参数:
            session_id: 会话ID，如果为None则自动生成
            user_input: 用户输入内容
            
        返回:
            会话ID
        """
        with self._lock:
            if session_id is None:
                session_id = f"session_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
            
            session = PipelineSession(
                session_id=session_id,
                start_time=time.time(),
                phase="initialization",
                user_input=user_input
            )
            
            self.sessions[session_id] = session
            self.current_session_id = session_id
            
            logger.info(f"📊 开始监控会话: {session_id}")
            return session_id
    
    def start_step(self, step: MemoryPipelineStep, 
                   session_id: Optional[str] = None,
                   input_data: Optional[Any] = None) -> MonitorMetrics:
        """
        开始监控指定步骤
        
        参数:
            step: 流程步骤
            session_id: 会话ID，如果为None使用当前会话
            input_data: 输入数据，用于计算输入大小
            
        返回:
            监控指标对象
        """
        with self._lock:
            if session_id is None:
                session_id = self.current_session_id
                
            if session_id is None:
                logger.warning("没有活跃的监控会话，自动创建新会话")
                session_id = self.start_session()
            
            session = self.sessions.get(session_id)
            if session is None:
                logger.error(f"会话不存在: {session_id}")
                # 创建一个空的监控指标作为降级处理
                return MonitorMetrics(
                    step=step,
                    session_id=session_id or "unknown",
                    start_time=time.time(),
                    status=StepStatus.FAILED,
                    error_message="会话不存在"
                )
            
            # 更新会话阶段
            session.phase = session.get_phase_by_step(step)
            session.current_step = step
            
            # 创建步骤监控指标
            metrics = MonitorMetrics(
                step=step,
                session_id=session_id,
                start_time=time.time(),
                status=StepStatus.RUNNING
            )
            
            # 计算输入大小
            if input_data is not None:
                metrics.input_size = self._calculate_data_size(input_data)
            
            # 初始内存使用情况（如果启用）
            if self.config["enable_memory_tracking"]:
                metrics.memory_usage = self._get_memory_usage()
            
            session.steps[step] = metrics
            
            logger.debug(f"📊 开始监控步骤: {step.value} (会话: {session_id})")
            return metrics
    
    def finish_step(self, step: MemoryPipelineStep,
                   status: StepStatus = StepStatus.SUCCESS,
                   session_id: Optional[str] = None,
                   output_data: Optional[Any] = None,
                   error: Optional[Exception] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        完成步骤监控
        
        参数:
            step: 流程步骤
            status: 步骤状态
            session_id: 会话ID
            output_data: 输出数据
            error: 错误信息
            metadata: 扩展元数据
            
        返回:
            是否成功完成
        """
        with self._lock:
            if session_id is None:
                session_id = self.current_session_id
                
            if session_id is None:
                logger.error("没有活跃的监控会话")
                return False
                
            session = self.sessions.get(session_id)
            if session is None or step not in session.steps:
                logger.error(f"步骤监控不存在: {step.value} (会话: {session_id})")
                return False
            
            metrics = session.steps[step]
            metrics.finish(status, error)
            
            # 更新输出大小
            if output_data is not None:
                metrics.output_size = self._calculate_data_size(output_data)
            
            # 更新元数据
            if metadata:
                metrics.metadata.update(metadata)
            
            # 更新会话统计
            if status == StepStatus.SUCCESS:
                session.success_count += 1
            elif status == StepStatus.FAILED:
                session.failed_count += 1
            elif status == StepStatus.SKIPPED:
                session.skipped_count += 1
            
            # 更新统计信息
            self._update_step_statistics(step, metrics)
            
            # 性能告警检查
            self._check_performance_alerts(metrics)
            
            logger.debug(f"📊 完成步骤监控: {step.value} -> {status.value} "
                        f"(耗时: {metrics.duration:.3f}s)")
            
            return True
    
    def finish_session(self, session_id: Optional[str] = None,
                      ai_response: Optional[str] = None) -> Optional[PipelineSession]:
        """
        完成监控会话
        
        参数:
            session_id: 会话ID
            ai_response: AI回复内容
            
        返回:
            完成的会话对象
        """
        with self._lock:
            if session_id is None:
                session_id = self.current_session_id
                
            if session_id is None:
                logger.error("没有活跃的监控会话")
                return None
                
            session = self.sessions.pop(session_id, None)
            if session is None:
                logger.error(f"会话不存在: {session_id}")
                return None
            
            # 计算总耗时
            session.total_duration = time.time() - session.start_time
            session.ai_response = ai_response
            
            # 计算业务指标
            if session.steps:
                session.enhanced_context_size = sum(
                    step.output_size or 0 for step in session.steps.values()
                    if step.step == MemoryPipelineStep.STEP_9_CONTEXT_BUILD
                )
                
                session.retrieved_memories_count = sum(
                    step.processed_count or 0 for step in session.steps.values()
                    if step.step == MemoryPipelineStep.STEP_5_FAISS_SEARCH
                )
            
            # 更新阶段统计
            self._update_phase_statistics(session)
            
            # 添加到历史记录
            self.completed_sessions.append(session)
            
            # 限制历史记录大小
            if len(self.completed_sessions) > self.max_history_size:
                self.completed_sessions.pop(0)
            
            # 清除当前会话
            if self.current_session_id == session_id:
                self.current_session_id = None
            
            logger.info(f"📊 完成监控会话: {session_id} "
                       f"(总耗时: {session.total_duration:.3f}s, "
                       f"成功: {session.success_count}, 失败: {session.failed_count})")
            
            return session
    
    def get_current_session(self) -> Optional[PipelineSession]:
        """获取当前会话"""
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None
    
    def get_session_status(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取会话状态摘要
        
        参数:
            session_id: 会话ID，如果为None使用当前会话
            
        返回:
            会话状态字典
        """
        if session_id is None:
            session_id = self.current_session_id
            
        if session_id is None:
            return {"error": "没有活跃的监控会话"}
            
        session = self.sessions.get(session_id)
        if session is None:
            return {"error": "会话不存在"}
        
        running_time = time.time() - session.start_time
        completed_steps = [step for step, metrics in session.steps.items() 
                          if metrics.status in [StepStatus.SUCCESS, StepStatus.FAILED, StepStatus.SKIPPED]]
        
        return {
            "session_id": session_id,
            "phase": session.phase,
            "current_step": session.current_step.value if session.current_step else None,
            "running_time": running_time,
            "completed_steps": len(completed_steps),
            "total_steps": len(session.steps),
            "success_count": session.success_count,
            "failed_count": session.failed_count,
            "skipped_count": session.skipped_count
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        total_sessions = len(self.completed_sessions)
        if total_sessions == 0:
            return {"message": "暂无历史数据"}
        
        # 计算平均性能
        avg_duration = sum(s.total_duration or 0 for s in self.completed_sessions) / total_sessions
        success_rate = sum(1 for s in self.completed_sessions 
                          if s.failed_count == 0) / total_sessions
        
        # 最慢和最快的步骤
        step_durations = defaultdict(list)
        for session in self.completed_sessions:
            for step, metrics in session.steps.items():
                if metrics.duration:
                    step_durations[step].append(metrics.duration)
        
        slowest_step = None
        fastest_step = None
        if step_durations:
            avg_step_times = {step: sum(times) / len(times) 
                             for step, times in step_durations.items()}
            slowest_step = max(avg_step_times.items(), key=lambda x: x[1])
            fastest_step = min(avg_step_times.items(), key=lambda x: x[1])
        
        return {
            "total_sessions": total_sessions,
            "average_duration": avg_duration,
            "success_rate": success_rate,
            "slowest_step": {
                "step": slowest_step[0].value if slowest_step else None,
                "avg_duration": slowest_step[1] if slowest_step else None
            },
            "fastest_step": {
                "step": fastest_step[0].value if fastest_step else None,
                "avg_duration": fastest_step[1] if fastest_step else None
            },
            "step_statistics": dict(self.step_statistics),
            "phase_statistics": dict(self.phase_statistics)
        }
    
    def _calculate_data_size(self, data: Any) -> int:
        """计算数据大小（字节）"""
        try:
            if isinstance(data, str):
                return len(data.encode('utf-8'))
            elif isinstance(data, (list, tuple)):
                return sum(self._calculate_data_size(item) for item in data)
            elif isinstance(data, dict):
                return sum(self._calculate_data_size(k) + self._calculate_data_size(v) 
                          for k, v in data.items())
            else:
                return len(str(data).encode('utf-8'))
        except Exception:
            return 0
    
    def _get_memory_usage(self) -> float:
        """获取当前内存使用情况（MB）"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
        except Exception:
            return 0.0
    
    def _update_step_statistics(self, step: MemoryPipelineStep, metrics: MonitorMetrics):
        """更新步骤统计信息"""
        stats = self.step_statistics[step]
        
        # 执行次数
        stats["count"] = stats.get("count", 0) + 1
        
        # 平均耗时
        if metrics.duration:
            total_duration = stats.get("total_duration", 0) + metrics.duration
            stats["total_duration"] = total_duration
            stats["avg_duration"] = total_duration / stats["count"]
            stats["min_duration"] = min(stats.get("min_duration", float('inf')), metrics.duration)
            stats["max_duration"] = max(stats.get("max_duration", 0), metrics.duration)
        
        # 成功率
        if metrics.status == StepStatus.SUCCESS:
            stats["success_count"] = stats.get("success_count", 0) + 1
        elif metrics.status == StepStatus.FAILED:
            stats["failed_count"] = stats.get("failed_count", 0) + 1
        
        stats["success_rate"] = stats.get("success_count", 0) / stats["count"]
    
    def _update_phase_statistics(self, session: PipelineSession):
        """更新阶段统计信息"""
        for phase in ["initialization", "query_enhancement", "storage_evaluation"]:
            phase_steps = [metrics for step, metrics in session.steps.items()
                          if session.get_phase_by_step(step) == phase]
            
            if not phase_steps:
                continue
                
            stats = self.phase_statistics[phase]
            stats["count"] = stats.get("count", 0) + 1
            
            phase_duration = sum(m.duration or 0 for m in phase_steps)
            total_duration = stats.get("total_duration", 0) + phase_duration
            stats["total_duration"] = total_duration
            stats["avg_duration"] = total_duration / stats["count"]
    
    def _check_performance_alerts(self, metrics: MonitorMetrics):
        """检查性能告警"""
        threshold = self.config["performance_threshold"]
        
        # 步骤耗时告警
        if (metrics.duration and 
            metrics.duration * 1000 > threshold["step_duration_ms"]):
            logger.warning(f"⚠️ 步骤耗时告警: {metrics.step.value} "
                          f"耗时 {metrics.duration:.3f}s (阈值: {threshold['step_duration_ms']/1000}s)")
        
        # 内存使用告警
        if (metrics.memory_usage and 
            metrics.memory_usage > threshold["memory_usage_mb"]):
            logger.warning(f"⚠️ 内存使用告警: {metrics.step.value} "
                          f"使用 {metrics.memory_usage:.1f}MB (阈值: {threshold['memory_usage_mb']}MB)") 