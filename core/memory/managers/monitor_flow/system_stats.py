#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统统计管理器 - 为监控流程提供统计数据
"""

import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SystemStatsManager:
    """系统统计管理器"""
    
    def __init__(self, db_manager, unified_cache):
        """
        初始化系统统计管理器
        
        Args:
            db_manager: 数据库管理器
            unified_cache: 统一缓存管理器
        """
        self.db_manager = db_manager
        self.unified_cache = unified_cache
        self.logger = logger
        
    def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        try:
            if not self.db_manager:
                return {"error": "数据库管理器未初始化"}
            
            # 获取基本统计（使用正确的字段名）
            stats = self.db_manager.query(
                """
                SELECT 
                    COUNT(*) as total_memories,
                    COUNT(CASE WHEN weight >= 8.0 THEN 1 END) as high_importance,
                    COUNT(CASE WHEN weight >= 6.0 AND weight < 8.0 THEN 1 END) as medium_importance,
                    COUNT(CASE WHEN weight < 6.0 THEN 1 END) as low_importance,
                    AVG(weight) as avg_importance,
                    MAX(timestamp) as latest_memory,
                    MIN(timestamp) as earliest_memory
                FROM memories
                """
            )
            
            if stats:
                return {
                    "total_memories": stats[0][0],
                    "high_importance": stats[0][1],
                    "medium_importance": stats[0][2],
                    "low_importance": stats[0][3],
                    "avg_importance": round(stats[0][4] or 0, 3),
                    "latest_memory": stats[0][5],
                    "earliest_memory": stats[0][6]
                }
            else:
                return {"total_memories": 0}
                
        except Exception as e:
            self.logger.error(f"获取记忆统计失败: {e}")
            return {"error": str(e)}
    
    def get_weight_distribution(self) -> Dict[str, Any]:
        """获取权重分布统计"""
        try:
            if not self.db_manager:
                return {"error": "数据库管理器未初始化"}
            
            # 获取权重分布（使用正确的字段名）
            stats = self.db_manager.query(
                """
                SELECT 
                    COUNT(CASE WHEN weight >= 9.0 THEN 1 END) as critical,
                    COUNT(CASE WHEN weight >= 7.0 AND weight < 9.0 THEN 1 END) as high,
                    COUNT(CASE WHEN weight >= 5.0 AND weight < 7.0 THEN 1 END) as medium,
                    COUNT(CASE WHEN weight >= 3.0 AND weight < 5.0 THEN 1 END) as low,
                    COUNT(CASE WHEN weight < 3.0 THEN 1 END) as minimal
                FROM memories
                """
            )
            
            if stats:
                return {
                    "critical": stats[0][0],
                    "high": stats[0][1],
                    "medium": stats[0][2],
                    "low": stats[0][3],
                    "minimal": stats[0][4]
                }
            else:
                return {"critical": 0, "high": 0, "medium": 0, "low": 0, "minimal": 0}
                
        except Exception as e:
            self.logger.error(f"获取权重分布失败: {e}")
            return {"error": str(e)}
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """获取性能统计"""
        try:
            cache_stats = {}
            if self.unified_cache:
                cache_stats = self.unified_cache.get_stats()
            
            return {
                "cache_hit_rate": cache_stats.get("hit_rate", 0),
                "cache_size": cache_stats.get("total_size", 0),
                "cache_efficiency": cache_stats.get("efficiency", 0),
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"获取性能统计失败: {e}")
            return {"error": str(e)}
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """获取会话统计"""
        try:
            if not self.db_manager:
                return {"error": "数据库管理器未初始化"}
            
            # 获取会话统计（使用正确的字段名）
            stats = self.db_manager.query(
                """
                SELECT 
                    COUNT(DISTINCT session_id) as total_sessions,
                    COUNT(*) as total_interactions,
                    AVG(LENGTH(content)) as avg_content_length,
                    COUNT(CASE WHEN role = 'user' THEN 1 END) as user_messages,
                    COUNT(CASE WHEN role = 'assistant' THEN 1 END) as assistant_messages
                FROM memories
                WHERE session_id IS NOT NULL
                """
            )
            
            if stats:
                return {
                    "total_sessions": stats[0][0] or 0,
                    "total_interactions": stats[0][1] or 0,
                    "avg_content_length": round(stats[0][2] or 0, 1),
                    "user_messages": stats[0][3] or 0,
                    "assistant_messages": stats[0][4] or 0
                }
            else:
                return {"total_sessions": 0, "total_interactions": 0}
                
        except Exception as e:
            self.logger.error(f"获取会话统计失败: {e}")
            return {"error": str(e)}
    
    def get_health_report(self) -> Dict[str, Any]:
        """获取系统健康报告"""
        try:
            health_report = {
                "timestamp": time.time(),
                "status": "healthy",
                "issues": []
            }
            
            # 检查数据库连接
            if not self.db_manager:
                health_report["status"] = "unhealthy"
                health_report["issues"].append("数据库管理器未初始化")
            
            # 检查缓存状态
            if not self.unified_cache:
                health_report["status"] = "degraded"
                health_report["issues"].append("统一缓存管理器未初始化")
            
            # 检查记忆数量
            try:
                memory_count = self.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
                if memory_count == 0:
                    health_report["status"] = "degraded"
                    health_report["issues"].append("没有记忆数据")
            except:
                health_report["status"] = "unhealthy"
                health_report["issues"].append("无法访问记忆数据")
            
            return health_report
            
        except Exception as e:
            self.logger.error(f"获取健康报告失败: {e}")
            return {"status": "error", "error": str(e)} 