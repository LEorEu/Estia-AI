#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆流程监控器 (MemoryFlowMonitor)
合并system_stats.py到monitoring/模块
职责：横切关注点，监控所有流程的性能和状态
"""

import time
import logging
from typing import Dict, Any, List, Optional
from ...shared.internal import handle_memory_errors, ErrorHandlerMixin

logger = logging.getLogger(__name__)

class MemoryFlowMonitor(ErrorHandlerMixin):
    """记忆流程监控器 - 横切关注点监控"""
    
    def __init__(self, components: Dict[str, Any]):
        """
        初始化流程监控器
        
        Args:
            components: 所需的组件字典
        """
        super().__init__()
        self.db_manager = components.get('db_manager')
        self.unified_cache = components.get('unified_cache')
        self.sync_flow_manager = components.get('sync_flow_manager')
        self.async_flow_manager = components.get('async_flow_manager')
        
        # 导入原system_stats功能
        from .system_stats import SystemStatsManager
        self.system_stats = SystemStatsManager(self.db_manager, self.unified_cache)
        
        # 导入monitoring模块功能
        try:
            from .monitoring.pipeline_monitor import PipelineMonitor
            from .monitoring.analytics import PerformanceAnalyzer
            
            self.pipeline_monitor = PipelineMonitor()
            self.performance_analyzer = PerformanceAnalyzer()
        except ImportError:
            self.pipeline_monitor = None
            self.performance_analyzer = None
            
        self.logger = logger
    
    @handle_memory_errors({'error': '获取系统统计失败'})
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        获取综合系统统计
        合并system_stats.py的功能
        
        Returns:
            Dict: 完整的系统统计信息
        """
        stats = {
            'timestamp': time.time(),
            'monitor_status': 'active'
        }
        
        try:
            # 1. 基础系统统计（来自原system_stats.py）
            basic_stats = self.system_stats.get_memory_statistics()
            stats['memory_overview'] = basic_stats
            
            # 2. 权重分布统计
            weight_stats = self.system_stats.get_weight_distribution()
            stats['weight_distribution'] = weight_stats
            
            # 3. 性能统计
            performance_stats = self.system_stats.get_performance_statistics()
            stats['performance_metrics'] = performance_stats
            
            # 4. 会话统计
            session_stats = self.system_stats.get_session_statistics()
            stats['session_statistics'] = session_stats
            
            # 5. 健康报告
            health_report = self.system_stats.get_health_report()
            stats['health_status'] = health_report
            
            # 6. 流程监控（新增）
            if self.pipeline_monitor:
                pipeline_stats = self.pipeline_monitor.get_pipeline_stats()
                stats['pipeline_monitoring'] = pipeline_stats
            
            # 7. 性能分析（新增）
            if self.performance_analyzer:
                analysis_report = self.performance_analyzer.get_analysis_report()
                stats['performance_analysis'] = analysis_report
                
            return stats
            
        except Exception as e:
            self.logger.error(f"获取综合统计失败: {e}")
            return {'error': str(e), 'timestamp': time.time()}
    
    @handle_memory_errors({'error': '流程监控失败'})
    def monitor_flow_execution(self, flow_type: str, operation: str, 
                              start_time: float, end_time: float, 
                              success: bool = True, metadata: Dict = None) -> bool:
        """
        监控流程执行
        
        Args:
            flow_type: 流程类型 ('sync', 'async')
            operation: 操作名称
            start_time: 开始时间
            end_time: 结束时间
            success: 是否成功
            metadata: 额外元数据
            
        Returns:
            bool: 监控记录是否成功
        """
        try:
            execution_time = end_time - start_time
            
            monitor_record = {
                'flow_type': flow_type,
                'operation': operation,
                'execution_time_ms': round(execution_time * 1000, 2),
                'success': success,
                'timestamp': start_time,
                'metadata': metadata or {}
            }
            
            # 记录到pipeline监控器
            if self.pipeline_monitor:
                self.pipeline_monitor.record_operation(monitor_record)
            
            # 性能分析
            if self.performance_analyzer:
                self.performance_analyzer.analyze_performance(monitor_record)
            
            # 日志记录
            status = "成功" if success else "失败"
            self.logger.debug(f"📊 {flow_type}流程监控: {operation} {status} ({execution_time*1000:.2f}ms)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"流程监控记录失败: {e}")
            return False
    
    def get_13_step_monitoring(self) -> Dict[str, Any]:
        """
        获取13步流程监控详情
        
        Returns:
            Dict: 13步流程的详细监控信息
        """
        try:
            if not self.pipeline_monitor:
                return {'error': 'Pipeline监控器未初始化'}
            
            # 获取每个步骤的监控数据
            step_stats = {}
            
            # 同步流程监控 (Step 1-9)
            sync_steps = [
                'system_init', 'component_init', 'async_evaluator_init',
                'cache_vectorization', 'faiss_search', 'association_expansion',
                'history_aggregation', 'weight_ranking', 'context_assembly'
            ]
            
            # 异步流程监控 (Step 10-15)
            async_steps = [
                'async_queue_trigger', 'llm_evaluation', 'weight_update',
                'layer_adjustment', 'summary_generation', 'association_creation'
            ]
            
            all_steps = sync_steps + async_steps
            
            for i, step in enumerate(all_steps, 1):
                step_data = self.pipeline_monitor.get_step_stats(step)
                step_stats[f'step_{i:02d}_{step}'] = step_data
            
            return {
                'timestamp': time.time(),
                'total_steps': len(all_steps),
                'sync_steps': len(sync_steps),
                'async_steps': len(async_steps),
                'step_details': step_stats,
                'overall_performance': self._calculate_overall_performance(step_stats)
            }
            
        except Exception as e:
            self.logger.error(f"获取13步监控失败: {e}")
            return {'error': str(e)}
    
    def _calculate_overall_performance(self, step_stats: Dict[str, Any]) -> Dict[str, Any]:
        """计算整体性能指标"""
        try:
            total_time = 0
            success_count = 0
            total_count = 0
            
            for step_name, stats in step_stats.items():
                if isinstance(stats, dict) and 'avg_time_ms' in stats:
                    total_time += stats.get('avg_time_ms', 0)
                    if stats.get('success_rate', 0) > 0.8:
                        success_count += 1
                    total_count += 1
            
            return {
                'total_avg_time_ms': round(total_time, 2),
                'overall_success_rate': round(success_count / total_count, 3) if total_count > 0 else 0,
                'performance_grade': self._get_performance_grade(total_time, success_count / total_count if total_count > 0 else 0)
            }
            
        except Exception as e:
            self.logger.error(f"计算整体性能失败: {e}")
            return {'error': str(e)}
    
    def _get_performance_grade(self, total_time: float, success_rate: float) -> str:
        """获取性能等级"""
        if total_time < 200 and success_rate > 0.95:
            return 'A'
        elif total_time < 500 and success_rate > 0.90:
            return 'B'
        elif total_time < 1000 and success_rate > 0.80:
            return 'C'
        else:
            return 'D'
    
    def start_monitoring(self, operation_name: str) -> str:
        """
        开始监控操作
        
        Args:
            operation_name: 操作名称
            
        Returns:
            str: 监控ID
        """
        try:
            monitor_id = f"{operation_name}_{int(time.time() * 1000)}"
            start_time = time.time()
            
            # 存储监控会话
            if not hasattr(self, '_active_monitors'):
                self._active_monitors = {}
            
            self._active_monitors[monitor_id] = {
                'operation': operation_name,
                'start_time': start_time,
                'status': 'active'
            }
            
            self.logger.debug(f"📊 开始监控: {operation_name} (ID: {monitor_id})")
            return monitor_id
            
        except Exception as e:
            self.logger.error(f"开始监控失败: {e}")
            return f"error_{int(time.time())}"
    
    def end_monitoring(self, operation_name: str, monitor_id: str = None) -> Dict[str, Any]:
        """
        结束监控操作
        
        Args:
            operation_name: 操作名称
            monitor_id: 监控ID，如果不提供则查找最近的
            
        Returns:
            Dict: 监控结果
        """
        try:
            end_time = time.time()
            
            if not hasattr(self, '_active_monitors'):
                self._active_monitors = {}
            
            # 查找对应的监控会话
            target_monitor = None
            target_id = None
            
            if monitor_id and monitor_id in self._active_monitors:
                target_monitor = self._active_monitors[monitor_id]
                target_id = monitor_id
            else:
                # 查找最近的同名操作
                for mid, monitor in self._active_monitors.items():
                    if monitor['operation'] == operation_name and monitor['status'] == 'active':
                        target_monitor = monitor
                        target_id = mid
                        break
            
            if target_monitor:
                # 计算执行时间
                execution_time = end_time - target_monitor['start_time']
                
                # 更新监控状态
                target_monitor['end_time'] = end_time
                target_monitor['execution_time'] = execution_time
                target_monitor['status'] = 'completed'
                
                # 记录监控结果
                self.monitor_flow_execution(
                    flow_type='sync',
                    operation=operation_name,
                    start_time=target_monitor['start_time'],
                    end_time=end_time,
                    success=True
                )
                
                # 清理监控会话
                del self._active_monitors[target_id]
                
                result = {
                    'operation': operation_name,
                    'execution_time_ms': round(execution_time * 1000, 2),
                    'status': 'success'
                }
                
                self.logger.debug(f"📊 结束监控: {operation_name} ({result['execution_time_ms']}ms)")
                return result
            else:
                self.logger.warning(f"未找到对应的监控会话: {operation_name}")
                return {'operation': operation_name, 'status': 'not_found'}
                
        except Exception as e:
            self.logger.error(f"结束监控失败: {e}")
            return {'operation': operation_name, 'status': 'error', 'error': str(e)}

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """获取实时性能指标"""
        try:
            return {
                'timestamp': time.time(),
                'cache_performance': self._get_cache_metrics(),
                'database_performance': self._get_database_metrics(),
                'queue_status': self._get_queue_metrics(),
                'memory_usage': self._get_memory_metrics()
            }
            
        except Exception as e:
            self.logger.error(f"获取实时指标失败: {e}")
            return {'error': str(e)}
    
    def _get_cache_metrics(self) -> Dict[str, Any]:
        """获取缓存性能指标"""
        if self.unified_cache:
            return self.unified_cache.get_performance_metrics()
        return {'status': 'unavailable'}
    
    def _get_database_metrics(self) -> Dict[str, Any]:
        """获取数据库性能指标"""
        return self.system_stats.get_database_performance()
    
    def _get_queue_metrics(self) -> Dict[str, Any]:
        """获取队列状态指标"""
        if self.async_flow_manager:
            return self.async_flow_manager.get_queue_status()
        return {'status': 'unavailable'}
    
    def _get_memory_metrics(self) -> Dict[str, Any]:
        """获取内存使用指标"""
        return self.system_stats.get_memory_performance()