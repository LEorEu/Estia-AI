#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统监控接口
================

安全地封装对记忆系统监控功能的访问，绝不修改核心记忆系统。
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MemoryMonitorInterface:
    """
    记忆系统监控接口
    
    安全地访问记忆系统的监控功能，不修改任何记忆系统代码。
    """
    
    def __init__(self):
        """初始化监控接口"""
        self.memory_flow_monitor = None
        self.system_stats = None
        self._initialize_safely()
    
    def _initialize_safely(self):
        """安全地初始化记忆系统监控"""
        try:
            # 尝试导入记忆系统监控器（只读访问）
            from core.memory.managers.monitor_flow import MemoryFlowMonitor
            
            # 创建模拟的组件字典来初始化监控器
            mock_components = {
                'db_manager': None,
                'unified_cache': None, 
                'sync_flow_manager': None,
                'async_flow_manager': None
            }
            
            self.memory_flow_monitor = MemoryFlowMonitor(mock_components)
            logger.info("✅ 记忆系统监控接口初始化成功")
            
        except ImportError as e:
            logger.warning(f"记忆系统监控器导入失败: {e}")
            self.memory_flow_monitor = None
        except Exception as e:
            logger.error(f"记忆系统监控接口初始化失败: {e}")
            self.memory_flow_monitor = None
    
    def is_available(self) -> bool:
        """检查记忆系统监控是否可用"""
        return self.memory_flow_monitor is not None
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        获取记忆系统综合统计
        
        Returns:
            Dict: 统计信息，如果不可用则返回错误信息
        """
        if not self.is_available():
            return {
                'error': '记忆系统监控不可用',
                'available': False
            }
        
        try:
            return self.memory_flow_monitor.get_comprehensive_stats()
        except Exception as e:
            logger.error(f"获取记忆系统统计失败: {e}")
            return {
                'error': str(e),
                'available': False
            }
    
    def get_step_monitoring(self) -> Dict[str, Any]:
        """
        获取15步流程监控数据
        
        Returns:
            Dict: 步骤监控信息
        """
        if not self.is_available():
            return {
                'error': '记忆系统监控不可用',
                'available': False
            }
        
        try:
            return self.memory_flow_monitor.get_13_step_monitoring()
        except Exception as e:
            logger.error(f"获取步骤监控失败: {e}")
            return {
                'error': str(e),
                'available': False
            }
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """
        获取实时性能指标
        
        Returns:
            Dict: 实时指标
        """
        if not self.is_available():
            return {
                'error': '记忆系统监控不可用',
                'available': False
            }
        
        try:
            return self.memory_flow_monitor.get_real_time_metrics()
        except Exception as e:
            logger.error(f"获取实时指标失败: {e}")
            return {
                'error': str(e),
                'available': False
            }
    
    def monitor_operation(self, operation_name: str, start_time: float, 
                         end_time: float, success: bool = True, 
                         metadata: Dict = None) -> bool:
        """
        监控操作执行（如果可用）
        
        Args:
            operation_name: 操作名称
            start_time: 开始时间
            end_time: 结束时间
            success: 是否成功
            metadata: 额外元数据
            
        Returns:
            bool: 是否记录成功
        """
        if not self.is_available():
            logger.debug(f"记忆系统监控不可用，跳过操作监控: {operation_name}")
            return False
        
        try:
            return self.memory_flow_monitor.monitor_flow_execution(
                flow_type='unified',
                operation=operation_name,
                start_time=start_time,
                end_time=end_time,
                success=success,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"记录操作监控失败: {e}")
            return False
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        获取状态摘要
        
        Returns:
            Dict: 状态摘要
        """
        return {
            'interface_available': self.is_available(),
            'monitor_type': 'MemoryFlowMonitor' if self.is_available() else 'Unavailable',
            'features': {
                'comprehensive_stats': self.is_available(),
                'step_monitoring': self.is_available(),
                'real_time_metrics': self.is_available(),
                'operation_monitoring': self.is_available()
            }
        }