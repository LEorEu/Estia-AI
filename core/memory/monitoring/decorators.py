#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控装饰器和上下文管理器
========================

提供方便的装饰器和上下文管理器，用于在现有代码中无侵入式地集成流程监控。
"""

import functools
import traceback
from contextlib import contextmanager
from typing import Any, Optional, Dict, Callable
import logging

from .pipeline_monitor import (
    MemoryPipelineMonitor, 
    MemoryPipelineStep, 
    StepStatus, 
    MonitorMetrics
)

logger = logging.getLogger(__name__)


def monitor_step(step: MemoryPipelineStep, 
                session_id: Optional[str] = None,
                capture_input: bool = True,
                capture_output: bool = True,
                on_error: str = "log",  # "log", "raise", "ignore"
                metadata: Optional[Dict[str, Any]] = None):
    """
    监控装饰器，用于监控函数执行的步骤
    
    参数:
        step: 流程步骤枚举
        session_id: 会话ID，如果为None则使用当前会话
        capture_input: 是否捕获输入参数大小
        capture_output: 是否捕获输出结果大小
        on_error: 错误处理方式 ("log", "raise", "ignore")
        metadata: 额外的元数据
        
    使用示例:
        @monitor_step(MemoryPipelineStep.STEP_4_CACHE_VECTORIZE)
        def vectorize_text(self, text: str):
            return self.vectorizer.encode(text)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = MemoryPipelineMonitor.get_instance()
            
            try:
                # 准备输入数据
                input_data = None
                if capture_input:
                    input_data = {"args": args, "kwargs": kwargs}
                
                # 开始监控步骤
                metrics = monitor.start_step(
                    step=step,
                    session_id=session_id,
                    input_data=input_data
                )
                
                if metrics is None:
                    logger.warning(f"无法开始监控步骤: {step.value}")
                    return func(*args, **kwargs)
                
                try:
                    # 执行原函数
                    result = func(*args, **kwargs)
                    
                    # 准备输出数据
                    output_data = None
                    if capture_output:
                        output_data = result
                    
                    # 完成步骤监控
                    step_metadata = metadata.copy() if metadata else {}
                    step_metadata.update({
                        "function_name": func.__name__,
                        "function_module": func.__module__
                    })
                    
                    monitor.finish_step(
                        step=step,
                        status=StepStatus.SUCCESS,
                        session_id=session_id,
                        output_data=output_data,
                        metadata=step_metadata
                    )
                    
                    return result
                    
                except Exception as e:
                    # 处理函数执行错误
                    step_metadata = metadata.copy() if metadata else {}
                    step_metadata.update({
                        "function_name": func.__name__,
                        "function_module": func.__module__,
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    })
                    
                    monitor.finish_step(
                        step=step,
                        status=StepStatus.FAILED,
                        session_id=session_id,
                        error=e,
                        metadata=step_metadata
                    )
                    
                    # 根据错误处理策略决定是否抛出异常
                    if on_error == "raise":
                        raise
                    elif on_error == "log":
                        logger.error(f"步骤 {step.value} 执行失败: {e}", exc_info=True)
                        return None
                    else:  # ignore
                        return None
                        
            except Exception as monitor_error:
                # 监控系统本身的错误，不应影响主流程
                logger.error(f"监控步骤 {step.value} 时发生错误: {monitor_error}")
                return func(*args, **kwargs)
                
        return wrapper
    return decorator


@contextmanager
def StepMonitorContext(step: MemoryPipelineStep,
                      session_id: Optional[str] = None,
                      input_data: Optional[Any] = None,
                      metadata: Optional[Dict[str, Any]] = None):
    """
    步骤监控上下文管理器
    
    参数:
        step: 流程步骤
        session_id: 会话ID
        input_data: 输入数据
        metadata: 元数据
        
    使用示例:
        with StepMonitorContext(MemoryPipelineStep.STEP_5_FAISS_SEARCH, 
                               input_data=query_vector) as ctx:
            search_results = self.faiss_retriever.search(query_vector)
            ctx.set_output(search_results)
            ctx.set_metadata({"result_count": len(search_results)})
    """
    monitor = MemoryPipelineMonitor.get_instance()
    
    try:
        # 开始监控步骤
        metrics = monitor.start_step(
            step=step,
            session_id=session_id,
            input_data=input_data
        )
        
        # 创建上下文对象
        context = StepContext(step, session_id, metrics, metadata)
        
        try:
            yield context
            
            # 成功完成
            monitor.finish_step(
                step=step,
                status=StepStatus.SUCCESS,
                session_id=session_id,
                output_data=context.output_data,
                metadata=context.metadata
            )
            
        except Exception as e:
            # 执行失败
            monitor.finish_step(
                step=step,
                status=StepStatus.FAILED,
                session_id=session_id,
                error=e,
                metadata=context.metadata
            )
            raise
            
    except Exception as monitor_error:
        # 监控错误，记录但不影响主流程
        logger.error(f"监控上下文错误: {monitor_error}")
        yield DummyContext()  # 返回一个虚拟上下文


class StepContext:
    """步骤监控上下文对象"""
    
    def __init__(self, step: MemoryPipelineStep, 
                 session_id: Optional[str],
                 metrics: Optional[MonitorMetrics],
                 metadata: Optional[Dict[str, Any]] = None):
        self.step = step
        self.session_id = session_id
        self.metrics = metrics
        self.metadata = metadata.copy() if metadata else {}
        self.output_data: Optional[Any] = None
        
    def set_output(self, output_data: Any):
        """设置输出数据"""
        self.output_data = output_data
        
    def set_metadata(self, metadata: Dict[str, Any]):
        """更新元数据"""
        self.metadata.update(metadata)
        
    def add_metadata(self, key: str, value: Any):
        """添加单个元数据项"""
        self.metadata[key] = value
        
    def get_metrics(self) -> Optional[MonitorMetrics]:
        """获取监控指标"""
        return self.metrics


class DummyContext:
    """虚拟上下文，用于监控系统错误时的降级处理"""
    
    def set_output(self, output_data: Any):
        pass
        
    def set_metadata(self, metadata: Dict[str, Any]):
        pass
        
    def add_metadata(self, key: str, value: Any):
        pass
        
    def get_metrics(self):
        return None 