#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控数据桥接器
==============

在不修改core/memory代码的前提下，实现主程序与监控系统的数据共享。
通过JSON文件和共享内存机制传递监控数据。
"""

import json
import os
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MonitoringDataBridge:
    """
    监控数据桥接器
    
    主程序通过此类更新监控数据，监控系统通过此类读取真实数据。
    """
    
    def __init__(self, data_file: str = "monitoring_data.json"):
        """
        初始化桥接器
        
        Args:
            data_file: 数据共享文件路径
        """
        self.data_file = os.path.join(os.getcwd(), data_file)
        self.lock = threading.Lock()
        self.data = {
            'system_status': {
                'running': False,
                'current_session': None,
                'uptime_seconds': 0,
                'last_update': None
            },
            'performance_metrics': {
                'queries_per_second': 0.0,
                'avg_response_time_ms': 0.0,
                'cache_hit_rate': 0.0,
                'success_rate': 0.0,
                'total_queries': 0,
                'failed_queries': 0
            },
            'memory_stats': {
                'total_memories': 0,
                'cache_size': 0,
                'vector_cache_hits': 0,
                'vector_cache_misses': 0,
                'active_sessions': 0
            },
            'recent_sessions': [],
            'real_time_metrics': {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'response_times': [],
                'error_count': 0
            }
        }
        self._start_time = time.time()
        
        # 确保数据文件存在
        self._initialize_data_file()
    
    def _initialize_data_file(self):
        """初始化数据文件"""
        try:
            if not os.path.exists(self.data_file):
                self._write_data_safe()
                logger.info(f"✅ 监控数据文件已创建: {self.data_file}")
            else:
                # 读取现有数据
                loaded_data = self._read_data()
                if loaded_data:
                    self.data = loaded_data
                logger.info(f"✅ 监控数据文件已加载: {self.data_file}")
        except Exception as e:
            logger.error(f"初始化数据文件失败: {e}")
    
    def _write_data(self):
        """写入数据到文件（需要在锁内调用）"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"写入监控数据失败: {e}")
    
    def _write_data_safe(self):
        """安全写入数据到文件（带锁保护）"""
        try:
            with self.lock:
                self._write_data()
        except Exception as e:
            logger.error(f"安全写入监控数据失败: {e}")
    
    def _read_data(self) -> Dict[str, Any]:
        """从文件读取数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
            return self.data
        except Exception as e:
            logger.error(f"读取监控数据失败: {e}")
            return self.data
    
    def update_system_status(self, running: bool = True, session_id: str = None):
        """
        更新系统状态
        
        Args:
            running: 系统是否运行中
            session_id: 当前会话ID
        """
        try:
            with self.lock:
                self.data['system_status'].update({
                    'running': running,
                    'current_session': session_id,
                    'uptime_seconds': int(time.time() - self._start_time),
                    'last_update': datetime.now().isoformat()
                })
                self._write_data()
                logger.debug(f"系统状态已更新: running={running}, session={session_id}")
        except Exception as e:
            logger.error(f"更新系统状态失败: {e}")
    
    def update_performance_metrics(self, response_time: float = None, 
                                 success: bool = True, cache_hit: bool = None):
        """
        更新性能指标
        
        Args:
            response_time: 响应时间(秒)
            success: 是否成功
            cache_hit: 是否缓存命中
        """
        try:
            with self.lock:
                metrics = self.data['performance_metrics']
                
                # 更新总查询数
                metrics['total_queries'] += 1
                
                # 更新失败查询数
                if not success:
                    metrics['failed_queries'] += 1
                
                # 更新成功率 
                metrics['success_rate'] = (
                    (metrics['total_queries'] - metrics['failed_queries']) / 
                    max(metrics['total_queries'], 1) * 100
                )
                
                # 更新响应时间
                if response_time is not None:
                    # 简单移动平均
                    current_avg = metrics['avg_response_time_ms']
                    new_time_ms = response_time * 1000
                    metrics['avg_response_time_ms'] = (
                        (current_avg * 0.8 + new_time_ms * 0.2)
                        if current_avg > 0 else new_time_ms
                    )
                
                # 更新QPS（简单估算）
                uptime = max(time.time() - self._start_time, 1)
                metrics['queries_per_second'] = metrics['total_queries'] / uptime
                
                # 更新缓存命中率
                if cache_hit is not None:
                    memory_stats = self.data['memory_stats']
                    if cache_hit:
                        memory_stats['vector_cache_hits'] += 1
                    else:
                        memory_stats['vector_cache_misses'] += 1
                    
                    total_cache_requests = (
                        memory_stats['vector_cache_hits'] + 
                        memory_stats['vector_cache_misses']
                    )
                    if total_cache_requests > 0:
                        metrics['cache_hit_rate'] = (
                            memory_stats['vector_cache_hits'] / total_cache_requests * 100
                        )
                
                self._write_data()
                logger.debug(f"性能指标已更新: 响应时间={response_time}s, 成功={success}")
                
        except Exception as e:
            logger.error(f"更新性能指标失败: {e}")
    
    def update_memory_stats(self, memory_system_stats: Dict[str, Any]):
        """
        更新记忆系统统计信息
        
        Args:
            memory_system_stats: 从记忆系统获取的统计信息
        """
        try:
            with self.lock:
                memory_stats = self.data['memory_stats'] 
                
                # 从记忆系统统计信息中提取关键数据
                if 'total_queries' in memory_system_stats:
                    memory_stats['total_memories'] = memory_system_stats['total_queries']
                
                if 'cache_hit_rate' in memory_system_stats:
                    self.data['performance_metrics']['cache_hit_rate'] = (
                        memory_system_stats['cache_hit_rate'] * 100
                    )
                
                if 'avg_response_time' in memory_system_stats:
                    self.data['performance_metrics']['avg_response_time_ms'] = (
                        memory_system_stats['avg_response_time'] * 1000
                    )
                
                if 'current_session' in memory_system_stats:
                    self.data['system_status']['current_session'] = (
                        memory_system_stats['current_session']
                    )
                
                memory_stats['active_sessions'] = 1 if memory_system_stats.get('current_session') else 0
                
                self._write_data()
                logger.debug("记忆系统统计信息已更新")
                
        except Exception as e:
            logger.error(f"更新记忆统计失败: {e}")
    
    def add_session_record(self, user_input: str, ai_response: str, 
                          response_time: float, session_id: str = None):
        """
        添加会话记录
        
        Args:
            user_input: 用户输入
            ai_response: AI响应  
            response_time: 响应时间
            session_id: 会话ID
        """
        try:
            with self.lock:
                session_record = {
                    'session_id': session_id or f"session_{int(time.time())}",
                    'user_input': user_input[:100],  # 限制长度
                    'ai_response': ai_response[:200],  # 限制长度
                    'response_time': response_time,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
                
                # 保持最近10条记录
                recent_sessions = self.data['recent_sessions']
                recent_sessions.append(session_record)
                if len(recent_sessions) > 10:
                    recent_sessions.pop(0)
                
                self._write_data()
                logger.debug(f"会话记录已添加: {session_id}")
                
        except Exception as e:
            logger.error(f"添加会话记录失败: {e}")
    
    def get_monitoring_data(self) -> Dict[str, Any]:
        """
        获取完整的监控数据（供监控系统使用）
        
        Returns:
            Dict: 完整的监控数据
        """
        try:
            # 读取最新数据
            data = self._read_data()
            
            # 添加实时计算的数据
            uptime = time.time() - self._start_time
            data['system_status']['uptime_seconds'] = int(uptime)
            data['system_status']['last_update'] = datetime.now().isoformat()
            
            logger.debug("监控数据已读取")
            return data
            
        except Exception as e:
            logger.error(f"获取监控数据失败: {e}")
            return self.data
    
    def is_main_program_running(self) -> bool:
        """
        检查主程序是否在运行
        
        Returns:
            bool: 主程序是否运行中
        """
        try:
            data = self._read_data()
            last_update = data['system_status'].get('last_update')
            if not last_update:
                return False
            
            # 检查最后更新时间是否在30秒内
            last_time = datetime.fromisoformat(last_update)
            now = datetime.now()
            time_diff = (now - last_time).total_seconds()
            
            return time_diff < 30 and data['system_status'].get('running', False)
            
        except Exception as e:
            logger.error(f"检查主程序状态失败: {e}")
            return False


# 全局桥接器实例
_bridge_instance = None

def get_monitoring_bridge() -> MonitoringDataBridge:
    """获取全局监控桥接器实例"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = MonitoringDataBridge()
    return _bridge_instance

def initialize_monitoring_bridge():
    """初始化监控桥接器"""
    return get_monitoring_bridge()