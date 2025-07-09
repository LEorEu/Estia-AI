#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一的错误处理机制
提供装饰器和混入类，消除重复的错误处理代码
"""

import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

logger = logging.getLogger(__name__)

def handle_memory_errors(
    fallback_return: Any = None,
    error_message: str = "操作失败",
    log_level: str = "error"
):
    """
    记忆系统错误处理装饰器
    
    Args:
        fallback_return: 错误时的返回值
        error_message: 错误信息前缀
        log_level: 日志级别
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 记录错误日志
                log_func = getattr(logger, log_level, logger.error)
                log_func(f"{func.__name__} {error_message}: {e}")
                
                # 返回标准化的错误响应
                if isinstance(fallback_return, dict):
                    return {
                        'success': False,
                        'message': f'{error_message}: {str(e)}',
                        'error_type': type(e).__name__,
                        **fallback_return
                    }
                return fallback_return
        return wrapper
    return decorator

def handle_async_memory_errors(
    fallback_return: Any = None,
    error_message: str = "异步操作失败",
    log_level: str = "error"
):
    """
    异步记忆系统错误处理装饰器
    
    Args:
        fallback_return: 错误时的返回值
        error_message: 错误信息前缀
        log_level: 日志级别
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 记录错误日志
                log_func = getattr(logger, log_level, logger.error)
                log_func(f"{func.__name__} {error_message}: {e}")
                
                # 返回标准化的错误响应
                if isinstance(fallback_return, dict):
                    return {
                        'success': False,
                        'message': f'{error_message}: {str(e)}',
                        'error_type': type(e).__name__,
                        **fallback_return
                    }
                return fallback_return
        return wrapper
    return decorator

class ErrorHandlerMixin:
    """错误处理混入类"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._error_logger = logging.getLogger(self.__class__.__name__)
    
    def _handle_error(self, 
                     operation: str, 
                     error: Exception, 
                     fallback_return: Any = None,
                     log_level: str = "error") -> Any:
        """
        统一的错误处理方法
        
        Args:
            operation: 操作名称
            error: 异常对象
            fallback_return: 错误时的返回值
            log_level: 日志级别
            
        Returns:
            标准化的错误响应或fallback_return
        """
        # 记录错误日志
        log_func = getattr(self._error_logger, log_level, self._error_logger.error)
        log_func(f"{operation}失败: {error}")
        
        # 返回标准化的错误响应
        if isinstance(fallback_return, dict):
            return {
                'success': False,
                'message': f'{operation}失败: {str(error)}',
                'error_type': type(error).__name__,
                **fallback_return
            }
        return fallback_return
    
    def _safe_execute(self, 
                     operation: Callable, 
                     fallback_return: Any = None,
                     operation_name: str = None,
                     *args, **kwargs) -> Any:
        """
        安全执行操作
        
        Args:
            operation: 要执行的操作
            fallback_return: 错误时的返回值
            operation_name: 操作名称
            *args, **kwargs: 传递给operation的参数
            
        Returns:
            操作结果或错误响应
        """
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            operation_name = operation_name or operation.__name__
            return self._handle_error(operation_name, e, fallback_return)
    
    async def _safe_execute_async(self, 
                                 operation: Callable, 
                                 fallback_return: Any = None,
                                 operation_name: str = None,
                                 *args, **kwargs) -> Any:
        """
        安全执行异步操作
        
        Args:
            operation: 要执行的异步操作
            fallback_return: 错误时的返回值
            operation_name: 操作名称
            *args, **kwargs: 传递给operation的参数
            
        Returns:
            操作结果或错误响应
        """
        try:
            return await operation(*args, **kwargs)
        except Exception as e:
            operation_name = operation_name or operation.__name__
            return self._handle_error(operation_name, e, fallback_return)
    
    def _create_success_response(self, 
                               message: str, 
                               data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建成功响应
        
        Args:
            message: 成功消息
            data: 响应数据
            
        Returns:
            标准化的成功响应
        """
        response = {
            'success': True,
            'message': message
        }
        
        if data:
            response.update(data)
        
        return response
    
    def _create_error_response(self, 
                              message: str, 
                              error_type: str = None,
                              data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建错误响应
        
        Args:
            message: 错误消息
            error_type: 错误类型
            data: 响应数据
            
        Returns:
            标准化的错误响应
        """
        response = {
            'success': False,
            'message': message
        }
        
        if error_type:
            response['error_type'] = error_type
        
        if data:
            response.update(data)
        
        return response

class DatabaseErrorHandler(ErrorHandlerMixin):
    """数据库错误处理器"""
    
    def _handle_db_error(self, operation: str, error: Exception, default_return: Any = None) -> Any:
        """
        处理数据库错误
        
        Args:
            operation: 数据库操作名称
            error: 异常对象
            default_return: 默认返回值
            
        Returns:
            错误响应或默认值
        """
        # 特殊处理不同类型的数据库错误
        if "database is locked" in str(error).lower():
            return self._handle_error(
                operation, 
                error, 
                {'retry_after': 1, 'reason': 'database_locked'}
            )
        elif "no such table" in str(error).lower():
            return self._handle_error(
                operation, 
                error, 
                {'reason': 'table_missing', 'recoverable': True}
            )
        else:
            return self._handle_error(operation, error, default_return)
    
    def _safe_db_execute(self, 
                        db_operation: Callable, 
                        operation_name: str,
                        fallback_return: Any = None,
                        *args, **kwargs) -> Any:
        """
        安全执行数据库操作
        
        Args:
            db_operation: 数据库操作
            operation_name: 操作名称
            fallback_return: 错误时的返回值
            *args, **kwargs: 传递给数据库操作的参数
            
        Returns:
            操作结果或错误响应
        """
        try:
            return db_operation(*args, **kwargs)
        except Exception as e:
            return self._handle_db_error(operation_name, e, fallback_return)