"""
智能记忆检索器

提供多种检索策略：
- 启动时记忆检索（最近+高权重）
- 历史回顾查询检索
- 关键词搜索
- 最近记忆检索
"""

import logging
from typing import List, Dict, Any, Optional
from ..init.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class SmartRetriever:
    """智能记忆检索器"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化智能检索器
        
        参数:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager
        self.logger = logger
    
    def get_startup_memories(self) -> List[Dict[str, Any]]:
        """
        获取启动时的记忆（最近5条 + 高权重5条）
        
        返回:
            记忆列表
        """
        try:
            memories = []
            
            # 1. 获取最近5条记忆
            recent_query = """
            SELECT id, content, type, role, weight, group_id, 
                   summary, timestamp, last_accessed, 'recent' as source
            FROM memories 
            ORDER BY timestamp DESC 
            LIMIT 5
            """
            recent_rows = self.db_manager.query(recent_query)
            
            # 2. 获取权重最高的5条记忆（排除已经在最近记忆中的）
            recent_ids = [row[0] for row in recent_rows] if recent_rows else []
            
            if recent_ids:
                placeholders = ','.join(['?' for _ in recent_ids])
                weight_query = f"""
                SELECT id, content, type, role, weight, group_id, 
                       summary, timestamp, last_accessed, 'important' as source
                FROM memories 
                WHERE id NOT IN ({placeholders}) AND weight >= 6.0
                ORDER BY weight DESC, timestamp DESC 
                LIMIT 5
                """
                weight_rows = self.db_manager.query(weight_query, recent_ids)
            else:
                weight_query = """
                SELECT id, content, type, role, weight, group_id, 
                       summary, timestamp, last_accessed, 'important' as source
                FROM memories 
                WHERE weight >= 6.0
                ORDER BY weight DESC, timestamp DESC 
                LIMIT 5
                """
                weight_rows = self.db_manager.query(weight_query)
            
            # 合并结果
            all_rows = (recent_rows or []) + (weight_rows or [])
            
            for row in all_rows:
                memory = self._row_to_memory(row, include_source=True)
                memories.append(memory)
            
            self.logger.info(f"启动记忆: 最近{len(recent_rows or [])}条 + 重要{len(weight_rows or [])}条 = 总计{len(memories)}条")
            return memories
            
        except Exception as e:
            self.logger.error(f"获取启动记忆失败: {e}")
            return []
    
    def get_recent_memories(self, limit: int = 8) -> List[Dict[str, Any]]:
        """
        获取最近的记忆
        
        参数:
            limit: 限制数量
            
        返回:
            记忆列表
        """
        try:
            query = """
            SELECT id, content, type, role, weight, group_id, 
                   summary, timestamp, last_accessed
            FROM memories 
            ORDER BY timestamp DESC 
            LIMIT ?
            """
            
            rows = self.db_manager.query(query, [limit])
            
            if rows:
                memories = []
                for row in rows:
                    memory = self._row_to_memory(row)
                    memory['similarity'] = 0.7  # 默认相似度
                    memories.append(memory)
                
                self.logger.info(f"获取最近记忆: {len(memories)} 条")
                return memories
            
            return []
            
        except Exception as e:
            self.logger.error(f"获取最近记忆失败: {e}")
            return []
    
    def keyword_search(self, user_input: str) -> List[Dict[str, Any]]:
        """
        关键词搜索
        
        参数:
            user_input: 用户输入
            
        返回:
            记忆列表
        """
        try:
            keywords = [w for w in user_input.lower().split() if len(w) > 1]
            
            if not keywords:
                return self.get_recent_memories(limit=5)
            
            # 构建搜索查询
            search_conditions = []
            params = []
            
            for keyword in keywords[:3]:  # 限制关键词数量
                search_conditions.append("(LOWER(content) LIKE ? OR LOWER(summary) LIKE ?)")
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            query = f"""
            SELECT id, content, type, role, weight, group_id, 
                   summary, timestamp, last_accessed
            FROM memories 
            WHERE {' OR '.join(search_conditions)}
            ORDER BY weight DESC, timestamp DESC 
            LIMIT 10
            """
            
            rows = self.db_manager.query(query, params)
            
            if rows:
                memories = []
                for row in rows:
                    memory = self._row_to_memory(row)
                    memory['similarity'] = 0.6  # 关键词匹配相似度
                    memories.append(memory)
                
                self.logger.info(f"关键词搜索找到: {len(memories)} 条记忆")
                return memories
            else:
                self.logger.info("关键词搜索无结果，返回最近记忆")
                return self.get_recent_memories(limit=5)
            
        except Exception as e:
            self.logger.error(f"关键词搜索失败: {e}")
            return []
    
    def smart_search(self, user_input: str) -> List[Dict[str, Any]]:
        """
        智能搜索记忆
        
        参数:
            user_input: 用户输入
            
        返回:
            记忆列表
        """
        try:
            # 检测查询类型
            if self.is_history_query(user_input):
                self.logger.info("检测到历史回顾查询")
                return self.get_recent_memories(limit=8)
            elif self.has_meaningful_keywords(user_input):
                self.logger.info("执行关键词搜索")
                return self.keyword_search(user_input)
            else:
                self.logger.info("通用查询，返回相关记忆")
                return self.get_recent_memories(limit=5)
                
        except Exception as e:
            self.logger.error(f"智能搜索失败: {e}")
            return []
    
    def is_history_query(self, user_input: str) -> bool:
        """
        检测是否为历史查询
        
        参数:
            user_input: 用户输入
            
        返回:
            是否为历史查询
        """
        history_keywords = [
            "还记得", "之前", "刚才", "刚刚", "前面", "上次", "历史", 
            "说过", "聊过", "提到", "讨论过", "记得吗", "回忆"
        ]
        user_lower = user_input.lower()
        return any(keyword in user_lower for keyword in history_keywords)
    
    def has_meaningful_keywords(self, user_input: str) -> bool:
        """
        检测是否包含有意义的关键词
        
        参数:
            user_input: 用户输入
            
        返回:
            是否包含有意义关键词
        """
        # 排除常见的无意义词汇
        stop_words = {"的", "了", "在", "是", "我", "你", "他", "她", "它", "们", 
                     "这", "那", "有", "和", "与", "或", "但", "如果", "因为", "所以",
                     "什么", "怎么", "为什么", "哪里", "谁", "吗", "呢", "吧", "啊"}
        
        words = user_input.split()
        meaningful_words = [w for w in words if len(w) > 1 and w not in stop_words]
        
        return len(meaningful_words) > 0
    
    def _row_to_memory(self, row: tuple, include_source: bool = False) -> Dict[str, Any]:
        """
        将数据库行转换为记忆字典
        
        参数:
            row: 数据库行
            include_source: 是否包含来源信息
            
        返回:
            记忆字典
        """
        # 从group_id推导super_group
        group_id = row[5] or ""
        super_group = "其他"
        if group_id:
            parts = group_id.split("_")
            if len(parts) >= 1:
                super_group = parts[0]
        
        memory = {
            "id": row[0],
            "content": row[1],
            "type": row[2],
            "role": row[3],
            "weight": row[4] or 5.0,
            "group_id": group_id,
            "super_group": super_group,
            "summary": row[6],
            "timestamp": row[7],
            "last_accessed": row[8]
        }
        
        # 如果包含来源信息
        if include_source and len(row) > 9:
            memory["source"] = row[9]
            memory["similarity"] = 0.9 if row[9] == 'recent' else 0.8
        
        return memory 