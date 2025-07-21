#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时数据连接器
==============

连接到正在运行的Estia记忆系统，获取实时监控数据
"""

import os
import sys
import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

class LiveDataConnector:
    """实时数据连接器，从正在运行的Estia系统获取数据"""
    
    def __init__(self):
        self.db_path = "assets/memory.db"
        self.vector_path = "data/vectors/memory_index.bin"
        self.cache_path = "cache"
        
    def check_system_running(self) -> bool:
        """检查Estia系统是否正在运行"""
        try:
            # 检查数据库文件是否存在且可访问
            if not os.path.exists(self.db_path):
                return False
            
            # 尝试连接数据库
            conn = sqlite3.connect(self.db_path, timeout=1.0)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories")
            conn.close()
            return True
            
        except Exception as e:
            print(f"系统检查失败: {e}")
            return False
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = conn.cursor()
            
            # 获取记忆总数
            cursor.execute("SELECT COUNT(*) FROM memories")
            total_memories = cursor.fetchone()[0]
            
            # 获取最近的记忆
            cursor.execute("""
                SELECT timestamp, weight, content, type, role, session_id
                FROM memories
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            recent_memories = cursor.fetchall()

            # 获取权重分布
            cursor.execute("""
                SELECT
                    COUNT(CASE WHEN weight >= 8.0 THEN 1 END) as high_weight,
                    COUNT(CASE WHEN weight >= 5.0 AND weight < 8.0 THEN 1 END) as medium_weight,
                    COUNT(CASE WHEN weight < 5.0 THEN 1 END) as low_weight
                FROM memories
            """)
            weight_dist = cursor.fetchone()

            # 获取今天创建的记忆数量（timestamp是Unix时间戳）
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
            cursor.execute("""
                SELECT COUNT(*) FROM memories
                WHERE timestamp >= ?
            """, (today_start,))
            today_memories = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_memories': total_memories,
                'today_memories': today_memories,
                'recent_memories': [
                    {
                        'timestamp': mem[0],
                        'created_at': datetime.fromtimestamp(mem[0]).isoformat(),
                        'weight': mem[1],
                        'content': mem[2][:100] + '...' if len(mem[2]) > 100 else mem[2],
                        'type': mem[3],
                        'role': mem[4],
                        'session_id': mem[5]
                    }
                    for mem in recent_memories
                ],
                'weight_distribution': {
                    'high_weight': weight_dist[0],
                    'medium_weight': weight_dist[1],
                    'low_weight': weight_dist[2]
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"获取记忆统计失败: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """获取会话统计信息"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = conn.cursor()
            
            # 获取不同会话ID的记忆
            cursor.execute("""
                SELECT DISTINCT session_id, MIN(timestamp) as first_time, COUNT(*) as memory_count
                FROM memories
                WHERE session_id IS NOT NULL AND session_id != ''
                GROUP BY session_id
                ORDER BY first_time DESC
                LIMIT 20
            """)
            session_data = cursor.fetchall()

            # 构建会话信息
            sessions = []
            for session in session_data:
                sessions.append({
                    'session_id': session[0],
                    'created_at': datetime.fromtimestamp(session[1]).isoformat(),
                    'memory_count': session[2],
                    'first_timestamp': session[1]
                })

            # 获取最近的对话记录（用户输入和AI回复）
            cursor.execute("""
                SELECT content, timestamp, weight, type, role, session_id
                FROM memories
                WHERE type IN ('user_input', 'assistant_reply')
                ORDER BY timestamp DESC
                LIMIT 20
            """)
            recent_dialogues = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_sessions': len(sessions),
                'recent_sessions': sessions[:5],  # 最近5个会话
                'recent_dialogues': [
                    {
                        'content': dialogue[0][:200] + '...' if len(dialogue[0]) > 200 else dialogue[0],
                        'created_at': datetime.fromtimestamp(dialogue[1]).isoformat(),
                        'timestamp': dialogue[1],
                        'weight': dialogue[2],
                        'type': dialogue[3],
                        'role': dialogue[4],
                        'session_id': dialogue[5]
                    }
                    for dialogue in recent_dialogues
                ],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"获取会话统计失败: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_health(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        try:
            health_info = {
                'database_accessible': False,
                'vector_index_exists': False,
                'cache_directory_exists': False,
                'last_activity': None,
                'system_status': 'unknown'
            }
            
            # 检查数据库
            if os.path.exists(self.db_path):
                try:
                    conn = sqlite3.connect(self.db_path, timeout=1.0)
                    cursor = conn.cursor()
                    cursor.execute("SELECT MAX(timestamp) FROM memories")
                    last_activity_timestamp = cursor.fetchone()[0]
                    conn.close()

                    health_info['database_accessible'] = True
                    if last_activity_timestamp:
                        health_info['last_activity'] = datetime.fromtimestamp(last_activity_timestamp).isoformat()
                    else:
                        health_info['last_activity'] = None
                except Exception as e:
                    print(f"数据库检查失败: {e}")
                    pass
            
            # 检查向量索引
            health_info['vector_index_exists'] = os.path.exists(self.vector_path)
            
            # 检查缓存目录
            health_info['cache_directory_exists'] = os.path.exists(self.cache_path)
            
            # 判断系统状态
            if health_info['database_accessible']:
                if health_info['last_activity']:
                    try:
                        last_time = datetime.fromisoformat(health_info['last_activity'])
                        time_diff = datetime.now() - last_time

                        if time_diff.total_seconds() < 300:  # 5分钟内有活动
                            health_info['system_status'] = 'active'
                        elif time_diff.total_seconds() < 3600:  # 1小时内有活动
                            health_info['system_status'] = 'idle'
                        else:
                            health_info['system_status'] = 'inactive'
                    except Exception as e:
                        print(f"时间解析失败: {e}")
                        health_info['system_status'] = 'unknown'
                else:
                    health_info['system_status'] = 'no_data'
            else:
                health_info['system_status'] = 'offline'
            
            health_info['timestamp'] = datetime.now().isoformat()
            return health_info
            
        except Exception as e:
            return {
                'error': str(e),
                'system_status': 'error',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_comprehensive_data(self) -> Dict[str, Any]:
        """获取综合数据"""
        return {
            'system_running': self.check_system_running(),
            'memory_stats': self.get_memory_statistics(),
            'session_stats': self.get_session_statistics(),
            'system_health': self.get_system_health(),
            'timestamp': datetime.now().isoformat()
        }


# 全局实例
live_connector = LiveDataConnector()
