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
from ..memory_cache.cache_manager import CacheManager

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
        self.cache_manager = CacheManager(db_manager)
        self.logger = logger
        
        # 初始化缓存系统
        try:
            self.cache_manager.initialize_cache()
            self.logger.info("智能缓存系统已初始化")
        except Exception as e:
            self.logger.error(f"缓存系统初始化失败: {e}")
            self.cache_manager = None
    
    def get_startup_memories(self) -> List[Dict[str, Any]]:
        """
        获取启动时的记忆（缓存优先 + 最近记忆 + 高权重记忆）
        
        返回:
            记忆列表
        """
        try:
            memories = []
            memory_ids = set()
            
            # 0. 优先获取热缓存记忆
            if self.cache_manager:
                try:
                    hot_cached_ids = self.cache_manager.get_cached_memories('hot', limit=3)
                    if hot_cached_ids:
                        cached_memories = self._get_memories_by_ids(hot_cached_ids)
                        for memory in cached_memories:
                            memory['source'] = 'hot_cache'
                            memories.append(memory)
                            memory_ids.add(memory['id'])
                        self.logger.info(f"热缓存记忆: {len(cached_memories)} 条")
                except Exception as e:
                    self.logger.warning(f"获取缓存记忆失败: {e}")
            
            # 1. 获取最近5条记忆（排除已缓存的）
            if memory_ids:
                placeholders = ','.join(['?' for _ in memory_ids])
                recent_query = f"""
                SELECT id, content, type, role, weight, group_id, 
                       summary, timestamp, last_accessed, 'recent' as source
                FROM memories 
                WHERE id NOT IN ({placeholders})
                ORDER BY timestamp DESC 
                LIMIT 5
                """
                recent_rows = self.db_manager.query(recent_query, list(memory_ids))
            else:
                recent_query = """
                SELECT id, content, type, role, weight, group_id, 
                       summary, timestamp, last_accessed, 'recent' as source
                FROM memories 
                ORDER BY timestamp DESC 
                LIMIT 5
                """
                recent_rows = self.db_manager.query(recent_query)
            
            # 2. 获取权重最高的记忆（排除已获取的）
            all_existing_ids = memory_ids.copy()
            if recent_rows:
                all_existing_ids.update([row[0] for row in recent_rows])
            
            if all_existing_ids:
                placeholders = ','.join(['?' for _ in all_existing_ids])
                weight_query = f"""
                SELECT id, content, type, role, weight, group_id, 
                       summary, timestamp, last_accessed, 'important' as source
                FROM memories 
                WHERE id NOT IN ({placeholders}) AND weight >= 6.0
                ORDER BY weight DESC, timestamp DESC 
                LIMIT 3
                """
                weight_rows = self.db_manager.query(weight_query, list(all_existing_ids))
            else:
                weight_query = """
                SELECT id, content, type, role, weight, group_id, 
                       summary, timestamp, last_accessed, 'important' as source
                FROM memories 
                WHERE weight >= 6.0
                ORDER BY weight DESC, timestamp DESC 
                LIMIT 3
                """
                weight_rows = self.db_manager.query(weight_query)
            
            # 合并所有结果
            all_rows = (recent_rows or []) + (weight_rows or [])
            
            for row in all_rows:
                memory = self._row_to_memory(row, include_source=True)
                memories.append(memory)
                # 记录访问以更新缓存
                self._record_memory_access(memory['id'], 0.8)
            
            self.logger.info(f"启动记忆: 缓存{len([m for m in memories if m.get('source') == 'hot_cache'])}条 + 最近{len(recent_rows or [])}条 + 重要{len(weight_rows or [])}条 = 总计{len(memories)}条")
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
                    # 记录访问
                    self._record_memory_access(memory['id'], 0.5)
                
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
                    # 记录访问，关键词搜索权重更高
                    self._record_memory_access(memory['id'], 1.0)
                
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
    
    def _get_memories_by_ids(self, memory_ids: List[str]) -> List[Dict[str, Any]]:
        """
        根据记忆ID列表获取记忆详情
        
        参数:
            memory_ids: 记忆ID列表
            
        返回:
            记忆详情列表
        """
        if not memory_ids:
            return []
        
        try:
            placeholders = ','.join(['?' for _ in memory_ids])
            query = f"""
            SELECT id, content, type, role, weight, group_id, 
                   summary, timestamp, last_accessed
            FROM memories 
            WHERE id IN ({placeholders})
            ORDER BY weight DESC, timestamp DESC
            """
            
            rows = self.db_manager.query(query, memory_ids)
            
            memories = []
            for row in rows:
                memory = self._row_to_memory(row)
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            self.logger.error(f"根据ID获取记忆失败: {e}")
            return []
    
    def _record_memory_access(self, memory_id: str, access_weight: float = 1.0):
        """
        记录记忆访问，更新缓存
        
        参数:
            memory_id: 记忆ID
            access_weight: 访问权重
        """
        if self.cache_manager:
            try:
                self.cache_manager.record_memory_access(memory_id, access_weight)
            except Exception as e:
                self.logger.debug(f"记录访问失败: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if self.cache_manager:
            return self.cache_manager.get_cache_stats()
        return {"cache_manager": "not_initialized"} 