"""
ErrorRecoveryManager - 错误恢复管理器
负责组件故障检测和恢复，降级策略管理，自动重试机制
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable, List, Tuple
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps

logger = logging.getLogger(__name__)

class ComponentStatus(Enum):
    """组件状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"
    DISABLED = "disabled"

class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorRecord:
    """错误记录"""
    timestamp: float
    component: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComponentHealth:
    """组件健康状态"""
    name: str
    status: ComponentStatus
    last_check: float
    error_count: int = 0
    last_error: Optional[ErrorRecord] = None
    recovery_attempts: int = 0
    downtime_start: Optional[float] = None

class ErrorRecoveryManager:
    """错误恢复管理器"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.component_health: Dict[str, ComponentHealth] = {}
        self.error_history: List[ErrorRecord] = []
        self.recovery_strategies: Dict[str, Callable] = {}
        self.fallback_handlers: Dict[str, Callable] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.logger = logger
        
    def register_component(self, name: str, recovery_strategy: Optional[Callable] = None, 
                          fallback_handler: Optional[Callable] = None):
        """注册组件"""
        self.component_health[name] = ComponentHealth(
            name=name,
            status=ComponentStatus.HEALTHY,
            last_check=time.time()
        )
        
        if recovery_strategy:
            self.recovery_strategies[name] = recovery_strategy
        
        if fallback_handler:
            self.fallback_handlers[name] = fallback_handler
            
        # 初始化断路器
        self.circuit_breakers[name] = {
            'failures': 0,
            'last_failure': 0,
            'state': 'closed',  # closed, open, half-open
            'threshold': 5,
            'timeout': 60
        }
        
        self.logger.info(f"✅ 组件已注册: {name}")
    
    def record_error(self, component: str, error: Exception, severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    context: Dict[str, Any] = None):
        """记录错误"""
        error_record = ErrorRecord(
            timestamp=time.time(),
            component=component,
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            stack_trace=str(error),
            context=context or {}
        )
        
        self.error_history.append(error_record)
        
        # 更新组件健康状态
        if component in self.component_health:
            health = self.component_health[component]
            health.error_count += 1
            health.last_error = error_record
            
            # 根据错误严重程度调整状态
            if severity == ErrorSeverity.CRITICAL:
                health.status = ComponentStatus.FAILED
                health.downtime_start = time.time()
            elif severity == ErrorSeverity.HIGH:
                health.status = ComponentStatus.DEGRADED
            
            # 更新断路器状态
            self._update_circuit_breaker(component)
            
        self.logger.error(f"🔥 错误记录: {component} - {error_record.error_message}")
        
        # 限制错误历史大小
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-500:]
    
    def _update_circuit_breaker(self, component: str):
        """更新断路器状态"""
        if component not in self.circuit_breakers:
            return
            
        breaker = self.circuit_breakers[component]
        current_time = time.time()
        
        breaker['failures'] += 1
        breaker['last_failure'] = current_time
        
        # 检查是否需要打开断路器
        if breaker['failures'] >= breaker['threshold'] and breaker['state'] == 'closed':
            breaker['state'] = 'open'
            self.logger.warning(f"🔴 断路器打开: {component}")
    
    def is_circuit_open(self, component: str) -> bool:
        """检查断路器是否打开"""
        if component not in self.circuit_breakers:
            return False
            
        breaker = self.circuit_breakers[component]
        current_time = time.time()
        
        if breaker['state'] == 'open':
            # 检查是否可以进入半开状态
            if current_time - breaker['last_failure'] > breaker['timeout']:
                breaker['state'] = 'half-open'
                self.logger.info(f"🟡 断路器半开: {component}")
                return False
            return True
            
        return False
    
    def reset_circuit_breaker(self, component: str):
        """重置断路器"""
        if component in self.circuit_breakers:
            breaker = self.circuit_breakers[component]
            breaker['failures'] = 0
            breaker['state'] = 'closed'
            self.logger.info(f"✅ 断路器重置: {component}")
    
    async def attempt_recovery(self, component: str) -> bool:
        """尝试恢复组件"""
        if component not in self.component_health:
            return False
            
        health = self.component_health[component]
        health.status = ComponentStatus.RECOVERING
        health.recovery_attempts += 1
        
        try:
            # 如果有自定义恢复策略，使用它
            if component in self.recovery_strategies:
                recovery_func = self.recovery_strategies[component]
                if asyncio.iscoroutinefunction(recovery_func):
                    success = await recovery_func()
                else:
                    success = recovery_func()
                
                if success:
                    health.status = ComponentStatus.HEALTHY
                    health.downtime_start = None
                    health.error_count = 0
                    self.reset_circuit_breaker(component)
                    self.logger.info(f"✅ 组件恢复成功: {component}")
                    return True
            
            # 默认恢复策略：等待一段时间后重试
            await asyncio.sleep(self.retry_delay)
            health.status = ComponentStatus.HEALTHY
            self.logger.info(f"✅ 组件默认恢复: {component}")
            return True
            
        except Exception as e:
            health.status = ComponentStatus.FAILED
            self.record_error(component, e, ErrorSeverity.HIGH, 
                            {'recovery_attempt': health.recovery_attempts})
            self.logger.error(f"❌ 组件恢复失败: {component} - {e}")
            return False
    
    def get_fallback_result(self, component: str, default_value: Any = None) -> Any:
        """获取降级结果"""
        if component in self.fallback_handlers:
            try:
                return self.fallback_handlers[component]()
            except Exception as e:
                self.logger.error(f"降级处理失败: {component} - {e}")
                return default_value
        return default_value
    
    def with_recovery(self, component: str, fallback_value: Any = None):
        """错误恢复上下文管理器"""
        return ErrorRecoveryContext(self, component, fallback_value)
    
    def as_decorator(self, component: str, fallback_value: Any = None):
        """错误恢复装饰器（保持向后兼容）"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 检查断路器状态
                if self.is_circuit_open(component):
                    self.logger.warning(f"断路器打开，使用降级处理: {component}")
                    return self.get_fallback_result(component, fallback_value)
                
                for attempt in range(self.max_retries + 1):
                    try:
                        result = await func(*args, **kwargs)
                        
                        # 成功后重置断路器
                        if component in self.circuit_breakers:
                            breaker = self.circuit_breakers[component]
                            if breaker['state'] == 'half-open':
                                self.reset_circuit_breaker(component)
                        
                        return result
                        
                    except Exception as e:
                        severity = ErrorSeverity.MEDIUM if attempt < self.max_retries else ErrorSeverity.HIGH
                        self.record_error(component, e, severity, 
                                        {'attempt': attempt, 'max_retries': self.max_retries})
                        
                        if attempt < self.max_retries:
                            await asyncio.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
                        else:
                            # 最后一次尝试失败，启动恢复
                            recovery_task = asyncio.create_task(self.attempt_recovery(component))
                            return self.get_fallback_result(component, fallback_value)
                            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 检查断路器状态
                if self.is_circuit_open(component):
                    self.logger.warning(f"断路器打开，使用降级处理: {component}")
                    return self.get_fallback_result(component, fallback_value)
                
                for attempt in range(self.max_retries + 1):
                    try:
                        result = func(*args, **kwargs)
                        
                        # 成功后重置断路器
                        if component in self.circuit_breakers:
                            breaker = self.circuit_breakers[component]
                            if breaker['state'] == 'half-open':
                                self.reset_circuit_breaker(component)
                        
                        return result
                        
                    except Exception as e:
                        severity = ErrorSeverity.MEDIUM if attempt < self.max_retries else ErrorSeverity.HIGH
                        self.record_error(component, e, severity, 
                                        {'attempt': attempt, 'max_retries': self.max_retries})
                        
                        if attempt < self.max_retries:
                            time.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
                        else:
                            # 最后一次尝试失败，启动恢复
                            asyncio.create_task(self.attempt_recovery(component))
                            return self.get_fallback_result(component, fallback_value)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def get_system_health(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        healthy_count = sum(1 for h in self.component_health.values() 
                          if h.status == ComponentStatus.HEALTHY)
        total_count = len(self.component_health)
        
        recent_errors = [e for e in self.error_history 
                        if time.time() - e.timestamp < 3600]  # 最近1小时
        
        return {
            'overall_health': healthy_count / total_count if total_count > 0 else 1.0,
            'healthy_components': healthy_count,
            'total_components': total_count,
            'recent_errors': len(recent_errors),
            'component_status': {
                name: {
                    'status': health.status.value,
                    'error_count': health.error_count,
                    'last_check': health.last_check,
                    'recovery_attempts': health.recovery_attempts,
                    'downtime': time.time() - health.downtime_start if health.downtime_start else 0
                }
                for name, health in self.component_health.items()
            },
            'circuit_breakers': self.circuit_breakers.copy()
        }
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取错误摘要"""
        cutoff_time = time.time() - (hours * 3600)
        recent_errors = [e for e in self.error_history if e.timestamp > cutoff_time]
        
        # 按组件分组
        by_component = {}
        for error in recent_errors:
            if error.component not in by_component:
                by_component[error.component] = []
            by_component[error.component].append(error)
        
        # 按类型分组
        by_type = {}
        for error in recent_errors:
            if error.error_type not in by_type:
                by_type[error.error_type] = []
            by_type[error.error_type].append(error)
        
        return {
            'total_errors': len(recent_errors),
            'time_window_hours': hours,
            'by_component': {
                comp: len(errors) for comp, errors in by_component.items()
            },
            'by_type': {
                error_type: len(errors) for error_type, errors in by_type.items()
            },
            'by_severity': {
                severity.value: len([e for e in recent_errors if e.severity == severity])
                for severity in ErrorSeverity
            }
        }
    
    def cleanup_old_errors(self, days: int = 7):
        """清理旧错误记录"""
        cutoff_time = time.time() - (days * 24 * 3600)
        original_count = len(self.error_history)
        self.error_history = [e for e in self.error_history if e.timestamp > cutoff_time]
        cleaned_count = original_count - len(self.error_history)
        
        if cleaned_count > 0:
            self.logger.info(f"🧹 清理了 {cleaned_count} 条旧错误记录")

# 全局错误恢复管理器实例
_error_recovery_manager = None

def get_error_recovery_manager() -> ErrorRecoveryManager:
    """获取全局错误恢复管理器实例"""
    global _error_recovery_manager
    if _error_recovery_manager is None:
        _error_recovery_manager = ErrorRecoveryManager()
    return _error_recovery_manager

def with_error_recovery(component: str, fallback_value: Any = None):
    """错误恢复装饰器的快捷方式"""
    return get_error_recovery_manager().with_recovery(component, fallback_value)


class ErrorRecoveryContext:
    """错误恢复上下文管理器"""
    
    def __init__(self, recovery_manager: ErrorRecoveryManager, component: str, fallback_value: Any = None):
        self.recovery_manager = recovery_manager
        self.component = component
        self.fallback_value = fallback_value
        self.error_occurred = False
        
    def __enter__(self):
        """进入上下文"""
        # 检查断路器状态
        if self.recovery_manager.is_circuit_open(self.component):
            logger.warning(f"🔴 断路器已打开，将返回降级结果: {self.component}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if exc_type is not None:
            # 发生了异常
            self.error_occurred = True
            severity = ErrorSeverity.HIGH if isinstance(exc_val, (SystemError, MemoryError)) else ErrorSeverity.MEDIUM
            self.recovery_manager.record_error(self.component, exc_val, severity)
            
            # 不抑制异常，让调用者处理
            return False
        
        # 成功执行，重置断路器（如果需要）
        if self.recovery_manager.circuit_breakers.get(self.component, {}).get('state') == 'half-open':
            self.recovery_manager.reset_circuit_breaker(self.component)
        
        return False  # 不抑制任何异常