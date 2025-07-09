#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一的SQL查询构建器
消除重复的查询逻辑，提供类型安全的查询构建
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from .memory_layer import MemoryLayer

class QueryBuilder:
    """统一的SQL查询构建器"""
    
    def __init__(self, table_name: str = "memories"):
        self.table_name = table_name
        self.base_columns = [
            'id', 'content', 'type', 'weight', 'timestamp', 
            'group_id', 'session_id', 'role', 'last_accessed', 'metadata'
        ]
    
    def build_select_query(self, 
                          columns: List[str] = None,
                          where_conditions: List[str] = None,
                          order_by: str = None,
                          limit: int = None,
                          include_archived: bool = False,
                          include_deleted: bool = False) -> Tuple[str, List[Any]]:
        """
        构建SELECT查询
        
        Args:
            columns: 选择的列
            where_conditions: WHERE条件列表
            order_by: 排序条件
            limit: 限制数量
            include_archived: 是否包含归档记忆
            include_deleted: 是否包含已删除记忆
            
        Returns:
            Tuple[str, List[Any]]: (查询语句, 参数列表)
        """
        # 构建SELECT子句
        if columns:
            select_clause = f"SELECT {', '.join(columns)}"
        else:
            select_clause = f"SELECT {', '.join(self.base_columns)}"
        
        # 构建FROM子句
        from_clause = f"FROM {self.table_name}"
        
        # 构建WHERE子句
        where_parts = []
        params = []
        
        # 默认过滤条件
        if not include_archived:
            where_parts.append("(archived IS NULL OR archived = 0)")
        
        if not include_deleted:
            where_parts.append("(deleted IS NULL OR deleted = 0)")
        
        # 添加自定义WHERE条件
        if where_conditions:
            where_parts.extend(where_conditions)
        
        where_clause = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
        
        # 构建ORDER BY子句
        order_clause = f"ORDER BY {order_by}" if order_by else ""
        
        # 构建LIMIT子句
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        # 组装完整查询
        query_parts = [select_clause, from_clause, where_clause, order_clause, limit_clause]
        query = " ".join(part for part in query_parts if part)
        
        return query, params
    
    def build_weight_distribution_query(self, 
                                      include_archived: bool = False,
                                      include_deleted: bool = False) -> Tuple[str, List[Any]]:
        """
        构建权重分布统计查询
        
        Args:
            include_archived: 是否包含归档记忆
            include_deleted: 是否包含已删除记忆
            
        Returns:
            Tuple[str, List[Any]]: (查询语句, 参数列表)
        """
        layer_case = MemoryLayer.get_layer_sql_case()
        
        query = f"""
            SELECT 
                {layer_case} as layer,
                COUNT(*) as count,
                AVG(weight) as avg_weight,
                MIN(weight) as min_weight,
                MAX(weight) as max_weight,
                MIN(timestamp) as oldest_timestamp,
                MAX(timestamp) as newest_timestamp
            FROM {self.table_name}
        """
        
        # 添加WHERE条件
        where_parts = []
        if not include_archived:
            where_parts.append("(archived IS NULL OR archived = 0)")
        if not include_deleted:
            where_parts.append("(deleted IS NULL OR deleted = 0)")
        
        if where_parts:
            query += f" WHERE {' AND '.join(where_parts)}"
        
        query += f"""
            GROUP BY {layer_case}
        """
        
        return query, []
    
    def build_keyword_search_query(self, 
                                  keywords: str,
                                  weight_threshold: float = 0.0,
                                  limit: int = 10,
                                  include_archived: bool = False) -> Tuple[str, List[Any]]:
        """
        构建关键词搜索查询
        
        Args:
            keywords: 搜索关键词
            weight_threshold: 权重阈值
            limit: 限制数量
            include_archived: 是否包含归档记忆
            
        Returns:
            Tuple[str, List[Any]]: (查询语句, 参数列表)
        """
        where_conditions = [
            "content LIKE ?",
            "weight >= ?"
        ]
        
        query, base_params = self.build_select_query(
            where_conditions=where_conditions,
            order_by="weight DESC, timestamp DESC",
            limit=limit,
            include_archived=include_archived
        )
        
        params = [f'%{keywords}%', weight_threshold] + base_params
        return query, params
    
    def build_timeframe_search_query(self, 
                                    start_timestamp: float,
                                    end_timestamp: float = None,
                                    limit: int = 10,
                                    include_archived: bool = False) -> Tuple[str, List[Any]]:
        """
        构建时间范围搜索查询
        
        Args:
            start_timestamp: 开始时间戳
            end_timestamp: 结束时间戳
            limit: 限制数量
            include_archived: 是否包含归档记忆
            
        Returns:
            Tuple[str, List[Any]]: (查询语句, 参数列表)
        """
        where_conditions = ["timestamp >= ?"]
        params = [start_timestamp]
        
        if end_timestamp:
            where_conditions.append("timestamp <= ?")
            params.append(end_timestamp)
        
        query, base_params = self.build_select_query(
            where_conditions=where_conditions,
            order_by="timestamp DESC",
            limit=limit,
            include_archived=include_archived
        )
        
        params.extend(base_params)
        return query, params
    
    def build_layer_search_query(self, 
                                layer_key: str,
                                limit: int = 10,
                                include_archived: bool = False) -> Tuple[str, List[Any]]:
        """
        构建层级搜索查询
        
        Args:
            layer_key: 层级键名
            limit: 限制数量
            include_archived: 是否包含归档记忆
            
        Returns:
            Tuple[str, List[Any]]: (查询语句, 参数列表)
        """
        min_weight, max_weight = MemoryLayer.get_weight_range(layer_key)
        
        where_conditions = [
            "weight >= ?",
            "weight < ?" if layer_key != 'core' else "weight <= ?"
        ]
        
        query, base_params = self.build_select_query(
            where_conditions=where_conditions,
            order_by="weight DESC, timestamp DESC",
            limit=limit,
            include_archived=include_archived
        )
        
        params = [min_weight, max_weight] + base_params
        return query, params
    
    def build_session_search_query(self, 
                                  session_id: str,
                                  limit: int = 10,
                                  include_archived: bool = False) -> Tuple[str, List[Any]]:
        """
        构建会话搜索查询
        
        Args:
            session_id: 会话ID
            limit: 限制数量
            include_archived: 是否包含归档记忆
            
        Returns:
            Tuple[str, List[Any]]: (查询语句, 参数列表)
        """
        where_conditions = ["session_id = ?"]
        
        query, base_params = self.build_select_query(
            where_conditions=where_conditions,
            order_by="timestamp ASC",
            limit=limit,
            include_archived=include_archived
        )
        
        params = [session_id] + base_params
        return query, params
    
    def build_update_query(self, 
                          memory_id: str,
                          updates: Dict[str, Any],
                          where_conditions: List[str] = None) -> Tuple[str, List[Any]]:
        """
        构建UPDATE查询
        
        Args:
            memory_id: 记忆ID
            updates: 更新的字段和值
            where_conditions: 额外的WHERE条件
            
        Returns:
            Tuple[str, List[Any]]: (查询语句, 参数列表)
        """
        if not updates:
            raise ValueError("更新字段不能为空")
        
        # 构建SET子句
        set_parts = []
        params = []
        
        for column, value in updates.items():
            if column == 'metadata' and isinstance(value, dict):
                # 处理JSON字段的更新
                set_parts.append(f"""
                    {column} = CASE 
                        WHEN {column} IS NULL THEN ?
                        ELSE json_patch({column}, ?)
                    END
                """)
                import json
                json_value = json.dumps(value)
                params.extend([json_value, json_value])
            else:
                set_parts.append(f"{column} = ?")
                params.append(value)
        
        # 构建WHERE子句
        where_parts = ["id = ?"]
        params.append(memory_id)
        
        if where_conditions:
            where_parts.extend(where_conditions)
        
        query = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_parts)}
            WHERE {' AND '.join(where_parts)}
        """
        
        return query, params
    
    def build_delete_query(self, 
                          memory_ids: List[str] = None,
                          where_conditions: List[str] = None,
                          soft_delete: bool = True) -> Tuple[str, List[Any]]:
        """
        构建DELETE查询
        
        Args:
            memory_ids: 要删除的记忆ID列表
            where_conditions: WHERE条件列表
            soft_delete: 是否软删除
            
        Returns:
            Tuple[str, List[Any]]: (查询语句, 参数列表)
        """
        params = []
        
        if soft_delete:
            # 软删除：更新deleted字段
            import time
            query = f"""
                UPDATE {self.table_name}
                SET deleted = 1,
                    metadata = CASE 
                        WHEN metadata IS NULL THEN ?
                        ELSE json_patch(metadata, ?)
                    END
            """
            
            import json
            delete_metadata = json.dumps({"deleted_at": time.time()})
            params.extend([delete_metadata, delete_metadata])
        else:
            # 硬删除：物理删除记录
            query = f"DELETE FROM {self.table_name}"
        
        # 构建WHERE子句
        where_parts = []
        
        if memory_ids:
            placeholders = ','.join(['?' for _ in memory_ids])
            where_parts.append(f"id IN ({placeholders})")
            params.extend(memory_ids)
        
        if where_conditions:
            where_parts.extend(where_conditions)
        
        if where_parts:
            query += f" WHERE {' AND '.join(where_parts)}"
        
        return query, params
    
    def build_count_query(self, 
                         where_conditions: List[str] = None,
                         include_archived: bool = False,
                         include_deleted: bool = False) -> Tuple[str, List[Any]]:
        """
        构建COUNT查询
        
        Args:
            where_conditions: WHERE条件列表
            include_archived: 是否包含归档记忆
            include_deleted: 是否包含已删除记忆
            
        Returns:
            Tuple[str, List[Any]]: (查询语句, 参数列表)
        """
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        
        # 构建WHERE子句
        where_parts = []
        
        if not include_archived:
            where_parts.append("(archived IS NULL OR archived = 0)")
        
        if not include_deleted:
            where_parts.append("(deleted IS NULL OR deleted = 0)")
        
        if where_conditions:
            where_parts.extend(where_conditions)
        
        if where_parts:
            query += f" WHERE {' AND '.join(where_parts)}"
        
        return query, []