#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统统计模块
负责收集和报告记忆系统的各种统计信息
"""

import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SystemStatsManager:
    """系统统计管理器"""
    
    def __init__(self, db_manager, unified_cache=None):
        """
        初始化系统统计管理器
        
        Args:
            db_manager: 数据库管理器
            unified_cache: 统一缓存管理器（可选）
        """
        self.db_manager = db_manager
        self.unified_cache = unified_cache
        self.logger = logger
    
    def get_system_stats(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取系统统计信息
        
        Args:
            components: 系统组件状态字典
            
        Returns:
            Dict: 系统统计信息
        """
        stats = {
            'system_status': {
                'initialized': components.get('initialized', False),
                'advanced_features': components.get('advanced_features', False),
                'async_evaluator_running': components.get('async_initialized', False),
                'timestamp': time.time()
            },
            'components': {
                'db_manager': components.get('db_manager') is not None,
                'vectorizer': components.get('vectorizer') is not None,
                'faiss_retriever': components.get('faiss_retriever') is not None,
                'association_network': components.get('association_network') is not None,
                'history_retriever': components.get('history_retriever') is not None,
                'memory_store': components.get('memory_store') is not None,
                'scorer': components.get('scorer') is not None,
                'async_evaluator': components.get('async_evaluator') is not None
            }
        }
        
        # 添加统一缓存统计
        if self.unified_cache:
            try:
                stats['unified_cache'] = self.unified_cache.get_stats()
            except Exception as e:
                stats['unified_cache'] = {"error": str(e)}
        
        # 获取记忆统计
        memory_stats = self.get_memory_statistics()
        stats.update(memory_stats)
        
        # 获取性能统计
        performance_stats = self.get_performance_statistics()
        stats['performance'] = performance_stats
        
        # 获取异步队列状态
        async_evaluator = components.get('async_evaluator')
        if async_evaluator:
            try:
                queue_stats = async_evaluator.get_queue_status()
                stats['async_queue'] = queue_stats
            except:
                stats['async_queue'] = {'status': 'unknown'}
        
        return stats
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """
        获取记忆统计信息
        
        Returns:
            Dict: 记忆统计信息
        """
        try:
            stats = {}
            
            # 总记忆数量
            total_query = "SELECT COUNT(*) FROM memories"
            result = self.db_manager.execute_query(total_query)
            stats['total_memories'] = result[0][0] if result else 0
            
            # 活跃记忆数量
            active_query = """
                SELECT COUNT(*) FROM memories 
                WHERE (archived IS NULL OR archived = 0)
                AND (deleted IS NULL OR deleted = 0)
            """
            result = self.db_manager.execute_query(active_query)
            stats['active_memories'] = result[0][0] if result else 0
            
            # 归档记忆数量
            archived_query = """
                SELECT COUNT(*) FROM memories 
                WHERE archived = 1
            """
            result = self.db_manager.execute_query(archived_query)
            stats['archived_memories'] = result[0][0] if result else 0
            
            # 按类型统计
            type_stats_query = """
                SELECT type, COUNT(*) as count 
                FROM memories 
                WHERE (archived IS NULL OR archived = 0)
                AND (deleted IS NULL OR deleted = 0)
                GROUP BY type
            """
            result = self.db_manager.execute_query(type_stats_query)
            
            type_stats = {}
            if result:
                for row in result:
                    type_stats[row[0]] = row[1]
            stats['memory_types'] = type_stats
            
            # 权重分布统计
            weight_stats = self.get_weight_distribution()
            stats['weight_distribution'] = weight_stats
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取记忆统计失败: {e}")
            return {'error': str(e)}
    
    def get_weight_distribution(self) -> Dict[str, Any]:
        """
        获取权重分布统计
        
        Returns:
            Dict: 权重分布信息
        """
        try:
            distribution_query = """
                SELECT 
                    CASE 
                        WHEN weight >= 9.0 THEN '核心记忆'
                        WHEN weight >= 7.0 THEN '归档记忆'
                        WHEN weight >= 4.0 THEN '长期记忆'
                        ELSE '短期记忆'
                    END as layer,
                    COUNT(*) as count,
                    AVG(weight) as avg_weight,
                    MIN(weight) as min_weight,
                    MAX(weight) as max_weight
                FROM memories 
                WHERE (archived IS NULL OR archived = 0)
                AND (deleted IS NULL OR deleted = 0)
                GROUP BY 
                    CASE 
                        WHEN weight >= 9.0 THEN '核心记忆'
                        WHEN weight >= 7.0 THEN '归档记忆'
                        WHEN weight >= 4.0 THEN '长期记忆'
                        ELSE '短期记忆'
                    END
            """
            
            result = self.db_manager.execute_query(distribution_query)
            
            distribution = {}
            if result:
                for row in result:
                    layer = row[0]
                    distribution[layer] = {
                        'count': row[1],
                        'avg_weight': round(row[2], 2),
                        'min_weight': round(row[3], 2),
                        'max_weight': round(row[4], 2)
                    }
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"获取权重分布失败: {e}")
            return {'error': str(e)}
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        获取性能统计信息
        
        Returns:
            Dict: 性能统计信息
        """
        try:
            performance_stats = {
                'timestamp': time.time(),
                'database_performance': self.get_database_performance(),
                'memory_performance': self.get_memory_performance(),
                'cache_performance': self.get_cache_performance()
            }
            
            return performance_stats
            
        except Exception as e:
            self.logger.error(f"获取性能统计失败: {e}")
            return {'error': str(e)}
    
    def get_database_performance(self) -> Dict[str, Any]:
        """
        获取数据库性能统计
        
        Returns:
            Dict: 数据库性能信息
        """
        try:
            # 测试数据库响应时间
            start_time = time.time()
            self.db_manager.execute_query("SELECT 1")
            response_time = time.time() - start_time
            
            # 获取数据库大小信息
            size_query = """
                SELECT 
                    COUNT(*) as total_rows,
                    SUM(LENGTH(content)) as total_content_size
                FROM memories
            """
            result = self.db_manager.execute_query(size_query)
            
            if result:
                total_rows = result[0][0]
                total_content_size = result[0][1] if result[0][1] else 0
            else:
                total_rows = 0
                total_content_size = 0
            
            return {
                'response_time_ms': round(response_time * 1000, 2),
                'total_rows': total_rows,
                'total_content_size_bytes': total_content_size,
                'avg_content_size_bytes': round(total_content_size / total_rows, 2) if total_rows > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"获取数据库性能统计失败: {e}")
            return {'error': str(e)}
    
    def get_memory_performance(self) -> Dict[str, Any]:
        """
        获取内存性能统计
        
        Returns:
            Dict: 内存性能信息
        """
        try:
            # 获取最近访问的记忆统计
            recent_access_query = """
                SELECT COUNT(*) as recent_access_count
                FROM memories 
                WHERE last_accessed > ?
            """
            
            one_hour_ago = time.time() - 3600
            result = self.db_manager.execute_query(recent_access_query, (one_hour_ago,))
            recent_access_count = result[0][0] if result else 0
            
            # 获取权重更新统计
            weight_update_query = """
                SELECT 
                    COUNT(*) as updated_count,
                    AVG(weight) as avg_weight
                FROM memories 
                WHERE metadata LIKE '%last_weight_update%'
            """
            
            result = self.db_manager.execute_query(weight_update_query)
            if result:
                updated_count = result[0][0]
                avg_weight = result[0][1] if result[0][1] else 0
            else:
                updated_count = 0
                avg_weight = 0
            
            return {
                'recent_access_count': recent_access_count,
                'weight_updated_count': updated_count,
                'avg_weight': round(avg_weight, 2)
            }
            
        except Exception as e:
            self.logger.error(f"获取内存性能统计失败: {e}")
            return {'error': str(e)}
    
    def get_cache_performance(self) -> Dict[str, Any]:
        """
        获取缓存性能统计
        
        Returns:
            Dict: 缓存性能信息
        """
        try:
            if self.unified_cache:
                cache_stats = self.unified_cache.get_stats()
                
                # 计算缓存命中率
                hit_rate = 0
                if cache_stats.get('access_count', 0) > 0:
                    hit_rate = cache_stats.get('hit_count', 0) / cache_stats.get('access_count', 1)
                
                return {
                    'hit_rate': round(hit_rate, 4),
                    'cache_size': cache_stats.get('size', 0),
                    'max_size': cache_stats.get('max_size', 0),
                    'hit_count': cache_stats.get('hit_count', 0),
                    'miss_count': cache_stats.get('miss_count', 0),
                    'access_count': cache_stats.get('access_count', 0)
                }
            else:
                return {'message': '统一缓存不可用'}
                
        except Exception as e:
            self.logger.error(f"获取缓存性能统计失败: {e}")
            return {'error': str(e)}
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        获取会话统计信息
        
        Returns:
            Dict: 会话统计信息
        """
        try:
            # 获取会话数量
            session_query = """
                SELECT 
                    session_id,
                    COUNT(*) as memory_count,
                    MIN(timestamp) as session_start,
                    MAX(timestamp) as session_end
                FROM memories 
                WHERE session_id IS NOT NULL
                AND (archived IS NULL OR archived = 0)
                AND (deleted IS NULL OR deleted = 0)
                GROUP BY session_id
                ORDER BY session_start DESC
                LIMIT 10
            """
            
            result = self.db_manager.execute_query(session_query)
            
            sessions = []
            if result:
                for row in result:
                    session_duration = row[3] - row[2] if row[3] and row[2] else 0
                    sessions.append({
                        'session_id': row[0],
                        'memory_count': row[1],
                        'session_start': row[2],
                        'session_end': row[3],
                        'duration_seconds': session_duration
                    })
            
            # 获取活跃会话统计
            active_session_query = """
                SELECT 
                    COUNT(DISTINCT session_id) as active_sessions,
                    AVG(memory_count) as avg_memories_per_session
                FROM (
                    SELECT 
                        session_id,
                        COUNT(*) as memory_count
                    FROM memories 
                    WHERE session_id IS NOT NULL
                    AND timestamp > ?
                    AND (archived IS NULL OR archived = 0)
                    AND (deleted IS NULL OR deleted = 0)
                    GROUP BY session_id
                ) as session_stats
            """
            
            one_day_ago = time.time() - 86400
            result = self.db_manager.execute_query(active_session_query, (one_day_ago,))
            
            if result:
                active_sessions = result[0][0]
                avg_memories_per_session = result[0][1] if result[0][1] else 0
            else:
                active_sessions = 0
                avg_memories_per_session = 0
            
            return {
                'recent_sessions': sessions,
                'active_sessions_24h': active_sessions,
                'avg_memories_per_session': round(avg_memories_per_session, 2),
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"获取会话统计失败: {e}")
            return {'error': str(e)}
    
    def get_health_report(self) -> Dict[str, Any]:
        """
        获取系统健康报告
        
        Returns:
            Dict: 系统健康报告
        """
        try:
            health_report = {
                'timestamp': time.time(),
                'overall_status': 'healthy',
                'issues': [],
                'warnings': [],
                'recommendations': []
            }
            
            # 检查数据库连接
            try:
                self.db_manager.execute_query("SELECT 1")
            except Exception as e:
                health_report['issues'].append(f"数据库连接问题: {e}")
                health_report['overall_status'] = 'unhealthy'
            
            # 检查记忆数量
            memory_stats = self.get_memory_statistics()
            if 'error' in memory_stats:
                health_report['issues'].append("无法获取记忆统计")
                health_report['overall_status'] = 'unhealthy'
            else:
                total_memories = memory_stats.get('total_memories', 0)
                active_memories = memory_stats.get('active_memories', 0)
                
                if total_memories == 0:
                    health_report['warnings'].append("系统中没有记忆")
                
                if active_memories > 0:
                    archived_ratio = memory_stats.get('archived_memories', 0) / total_memories
                    if archived_ratio > 0.8:
                        health_report['warnings'].append(f"归档记忆比例过高: {archived_ratio:.1%}")
                        health_report['recommendations'].append("考虑清理过期归档记忆")
            
            # 检查权重分布
            weight_distribution = self.get_weight_distribution()
            if 'error' not in weight_distribution:
                core_memories = weight_distribution.get('核心记忆', {}).get('count', 0)
                if active_memories > 0:
                    core_ratio = core_memories / active_memories
                    if core_ratio > 0.2:
                        health_report['warnings'].append(f"核心记忆比例过高: {core_ratio:.1%}")
                        health_report['recommendations'].append("检查权重管理策略")
            
            # 检查性能
            performance_stats = self.get_performance_statistics()
            if 'error' not in performance_stats:
                db_response_time = performance_stats.get('database_performance', {}).get('response_time_ms', 0)
                if db_response_time > 100:  # 响应时间超过100ms
                    health_report['warnings'].append(f"数据库响应时间较长: {db_response_time}ms")
                    health_report['recommendations'].append("优化数据库查询或考虑索引")
            
            # 更新总体状态
            if health_report['warnings'] and health_report['overall_status'] == 'healthy':
                health_report['overall_status'] = 'warning'
            
            return health_report
            
        except Exception as e:
            self.logger.error(f"获取健康报告失败: {e}")
            return {
                'timestamp': time.time(),
                'overall_status': 'error',
                'error': str(e)
            }
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        生成综合统计报告
        
        Returns:
            Dict: 综合统计报告
        """
        try:
            report = {
                'timestamp': time.time(),
                'memory_overview': self.get_memory_statistics(),
                'weight_distribution': self.get_weight_distribution(),
                'performance_metrics': self.get_performance_statistics(),
                'session_statistics': self.get_session_statistics(),
                'health_status': self.get_health_report()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成综合报告失败: {e}")
            return {
                'timestamp': time.time(),
                'error': str(e)
            } 