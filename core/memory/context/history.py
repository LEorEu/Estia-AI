"""
Step 6: 从数据库或缓存中取出对话
根据FAISS检索和关联网络结果，从数据库获取完整记忆内容
支持根据group_id和session_id聚合相关对话，提取summary内容
"""

import time
import json
import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta

# 设置日志
logger = logging.getLogger("estia.memory.context")

class HistoryRetriever:
    """
    历史对话检索器
    负责从数据库中获取记忆内容，聚合相关对话，提取总结
    """
    
    def __init__(self, db_manager=None):
        """
        初始化历史检索器
        
        参数:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
        self.logger = logger
        
    def retrieve_memory_contents(self, memory_ids: List[str], 
                                include_summaries: bool = True,
                                include_sessions: bool = True,
                                max_recent_dialogues: int = 10) -> Dict[str, Any]:
        """
        检索记忆内容的主入口
        
        参数:
            memory_ids: 记忆ID列表（来自FAISS检索和关联网络）
            include_summaries: 是否包含总结内容
            include_sessions: 是否包含会话相关对话
            max_recent_dialogues: 最大返回的最近对话数量
            
        返回:
            Dict: 包含各类记忆内容的字典
        """
        if not self.db_manager or not memory_ids:
            return self._empty_result()
        
        start_time = time.time()
        
        try:
            # Step 1: 获取基础记忆内容
            primary_memories = self._get_memories_by_ids(memory_ids)
            
            # Step 2: 按group_id聚合相关记忆
            grouped_memories = self._group_memories_by_group_id(primary_memories)
            
            # Step 3: 按session_id聚合会话对话
            session_dialogues = {}
            if include_sessions:
                session_dialogues = self._get_session_dialogues(primary_memories, max_recent_dialogues)
            
            # Step 4: 提取和聚合总结内容
            summaries = {}
            if include_summaries:
                summaries = self._extract_summaries(primary_memories, grouped_memories)
            
            # Step 5: 组装最终结果
            result = {
                "primary_memories": primary_memories,
                "grouped_memories": grouped_memories,
                "session_dialogues": session_dialogues,
                "summaries": summaries,
                "stats": {
                    "total_memories": len(primary_memories),
                    "groups_found": len(grouped_memories),
                    "sessions_found": len(session_dialogues),
                    "summaries_found": len(summaries),
                    "retrieval_time": time.time() - start_time
                }
            }
            
            self.logger.info(f"检索记忆内容完成: {len(primary_memories)}条记忆, "
                           f"{len(grouped_memories)}个分组, {len(session_dialogues)}个会话, "
                           f"耗时: {result['stats']['retrieval_time']*1000:.2f}ms")
            
            return result
            
        except Exception as e:
            self.logger.error(f"检索记忆内容失败: {e}")
            return self._empty_result()
    
    def _get_memories_by_ids(self, memory_ids: List[str]) -> List[Dict[str, Any]]:
        """根据ID列表获取记忆内容"""
        if not memory_ids:
            return []
        
        try:
            # 构建查询语句
            placeholders = ','.join(['?' for _ in memory_ids])
            query = f"""
                SELECT id, content, type, role, session_id, timestamp, 
                       weight, group_id, summary, last_accessed, metadata
                FROM memories 
                WHERE id IN ({placeholders})
                ORDER BY timestamp DESC
            """
            
            results = self.db_manager.query(query, memory_ids)
            
            memories = []
            for row in results:
                try:
                    # 解析元数据
                    metadata = json.loads(row[10]) if row[10] else {}
                except:
                    metadata = {}
                
                memory = {
                    "memory_id": row[0],
                    "content": row[1],
                    "type": row[2],
                    "role": row[3],
                    "session_id": row[4] or "",
                    "timestamp": row[5],
                    "weight": row[6],
                    "group_id": row[7] or "",
                    "summary": row[8] or "",
                    "last_accessed": row[9],
                    "metadata": metadata,
                    "formatted_time": datetime.fromtimestamp(row[5]).strftime('%Y-%m-%d %H:%M:%S')
                }
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            self.logger.error(f"根据ID获取记忆失败: {e}")
            return []
    
    def _group_memories_by_group_id(self, memories: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按group_id分组记忆"""
        groups = {}
        
        for memory in memories:
            group_id = memory.get("group_id", "")
            if not group_id:
                continue
                
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(memory)
        
        # 为每个分组添加统计信息
        for group_id, group_memories in groups.items():
            # 按时间排序
            group_memories.sort(key=lambda x: x["timestamp"])
            
            # 添加分组统计
            if group_memories:
                groups[group_id] = {
                    "group_id": group_id,
                    "memories": group_memories,
                    "count": len(group_memories),
                    "time_span": {
                        "start": group_memories[0]["formatted_time"],
                        "end": group_memories[-1]["formatted_time"]
                    },
                    "avg_weight": sum(m["weight"] for m in group_memories) / len(group_memories)
                }
        
        return groups
    
    def _get_session_dialogues(self, memories: List[Dict[str, Any]], 
                              max_dialogues: int = 10) -> Dict[str, Dict[str, Any]]:
        """获取会话相关的对话"""
        sessions = {}
        
        # 收集所有session_id
        session_ids = set()
        for memory in memories:
            session_id = memory.get("session_id", "")
            if session_id:
                session_ids.add(session_id)
        
        if not session_ids:
            return sessions
        
        try:
            # 为每个session获取完整对话
            for session_id in session_ids:
                session_memories = self._get_session_memories(session_id, max_dialogues)
                if session_memories:
                    sessions[session_id] = {
                        "session_id": session_id,
                        "memories": session_memories,
                        "count": len(session_memories),
                        "dialogue_pairs": self._extract_dialogue_pairs(session_memories)
                    }
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"获取会话对话失败: {e}")
            return {}
    
    def _get_session_memories(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取特定会话的记忆"""
        try:
            query = """
                SELECT id, content, type, role, session_id, timestamp, 
                       weight, group_id, summary, last_accessed, metadata
                FROM memories 
                WHERE session_id = ? AND type != 'summary'
                ORDER BY timestamp DESC
                LIMIT ?
            """
            
            results = self.db_manager.query(query, (session_id, limit))
            
            memories = []
            for row in results:
                try:
                    metadata = json.loads(row[10]) if row[10] else {}
                except:
                    metadata = {}
                
                memory = {
                    "memory_id": row[0],
                    "content": row[1],
                    "type": row[2],
                    "role": row[3],
                    "session_id": row[4],
                    "timestamp": row[5],
                    "weight": row[6],
                    "group_id": row[7] or "",
                    "summary": row[8] or "",
                    "last_accessed": row[9],
                    "metadata": metadata,
                    "formatted_time": datetime.fromtimestamp(row[5]).strftime('%Y-%m-%d %H:%M:%S')
                }
                memories.append(memory)
            
            # 按时间正序排列（最早的在前）
            memories.reverse()
            return memories
            
        except Exception as e:
            self.logger.error(f"获取会话记忆失败: {e}")
            return []
    
    def _extract_dialogue_pairs(self, session_memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从会话记忆中提取对话对"""
        dialogue_pairs = []
        
        user_memory = None
        for memory in session_memories:
            role = memory.get("role", "")
            
            if role == "user":
                user_memory = memory
            elif role in ["assistant", "ai"] and user_memory:
                # 形成对话对
                dialogue_pairs.append({
                    "user": user_memory,
                    "assistant": memory,
                    "timestamp": user_memory["timestamp"],
                    "formatted_time": user_memory["formatted_time"]
                })
                user_memory = None
        
        return dialogue_pairs
    
    def _extract_summaries(self, primary_memories: List[Dict[str, Any]], 
                          grouped_memories: Dict[str, Any]) -> Dict[str, Any]:
        """提取和聚合总结内容"""
        summaries = {
            "direct_summaries": [],      # 直接的summary类型记忆
            "memory_summaries": [],      # 记忆中的summary字段
            "group_summaries": {},       # 按组的总结
            "session_summaries": {}      # 按会话的总结
        }
        
        try:
            # 1. 提取直接的summary类型记忆
            for memory in primary_memories:
                if memory.get("type") == "summary":
                    summaries["direct_summaries"].append({
                        "content": memory["content"],
                        "timestamp": memory["timestamp"],
                        "formatted_time": memory["formatted_time"],
                        "weight": memory["weight"],
                        "source": "direct_summary"
                    })
                
                # 2. 提取记忆中的summary字段
                if memory.get("summary"):
                    summaries["memory_summaries"].append({
                        "content": memory["summary"],
                        "related_memory": memory["memory_id"],
                        "timestamp": memory["timestamp"],
                        "formatted_time": memory["formatted_time"],
                        "source": "memory_field"
                    })
            
            # 3. 获取相关的summary记忆
            related_summaries = self._get_related_summaries(primary_memories)
            summaries["direct_summaries"].extend(related_summaries)
            
            # 4. 按组聚合总结
            for group_id, group_data in grouped_memories.items():
                group_summaries = self._get_group_summaries(group_id)
                if group_summaries:
                    summaries["group_summaries"][group_id] = group_summaries
            
            return summaries
            
        except Exception as e:
            self.logger.error(f"提取总结失败: {e}")
            return summaries
    
    def _get_related_summaries(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """获取相关的总结记忆"""
        if not memories:
            return []
        
        try:
            # 获取所有相关的session_id和group_id
            session_ids = set()
            group_ids = set()
            
            for memory in memories:
                if memory.get("session_id"):
                    session_ids.add(memory["session_id"])
                if memory.get("group_id"):
                    group_ids.add(memory["group_id"])
            
            summaries = []
            
            # 按session_id查找总结
            for session_id in session_ids:
                session_summaries = self._get_session_summaries(session_id)
                summaries.extend(session_summaries)
            
            # 按group_id查找总结
            for group_id in group_ids:
                group_summaries = self._get_group_summaries(group_id)
                summaries.extend(group_summaries)
            
            return summaries
            
        except Exception as e:
            self.logger.error(f"获取相关总结失败: {e}")
            return []
    
    def _get_session_summaries(self, session_id: str) -> List[Dict[str, Any]]:
        """获取特定会话的总结"""
        try:
            query = """
                SELECT content, timestamp, weight, metadata
                FROM memories 
                WHERE session_id = ? AND type = 'summary'
                ORDER BY timestamp DESC
                LIMIT 5
            """
            
            results = self.db_manager.query(query, (session_id,))
            
            summaries = []
            for row in results:
                summaries.append({
                    "content": row[0],
                    "timestamp": row[1],
                    "formatted_time": datetime.fromtimestamp(row[1]).strftime('%Y-%m-%d %H:%M:%S'),
                    "weight": row[2],
                    "source": f"session_{session_id}"
                })
            
            return summaries
            
        except Exception as e:
            self.logger.error(f"获取会话总结失败: {e}")
            return []
    
    def _get_group_summaries(self, group_id: str) -> List[Dict[str, Any]]:
        """获取特定分组的总结"""
        try:
            # 从memory_group表获取分组总结
            query = """
                SELECT summary, time_start, time_end, score, topic
                FROM memory_group 
                WHERE group_id = ?
            """
            
            results = self.db_manager.query(query, (group_id,))
            
            summaries = []
            for row in results:
                if row[0]:  # summary不为空
                    summaries.append({
                        "content": row[0],
                        "topic": row[4] or "未分类",
                        "time_span": {
                            "start": datetime.fromtimestamp(row[1]).strftime('%Y-%m-%d %H:%M:%S') if row[1] else "",
                            "end": datetime.fromtimestamp(row[2]).strftime('%Y-%m-%d %H:%M:%S') if row[2] else ""
                        },
                        "score": row[3],
                        "source": f"group_{group_id}"
                    })
            
            return summaries
            
        except Exception as e:
            self.logger.error(f"获取分组总结失败: {e}")
            return []
    
    def _empty_result(self) -> Dict[str, Any]:
        """返回空结果"""
        return {
            "primary_memories": [],
            "grouped_memories": {},
            "session_dialogues": {},
            "summaries": {
                "direct_summaries": [],
                "memory_summaries": [],
                "group_summaries": {},
                "session_summaries": {}
            },
            "stats": {
                "total_memories": 0,
                "groups_found": 0,
                "sessions_found": 0,
                "summaries_found": 0,
                "retrieval_time": 0
            }
        }
    
    def format_for_context(self, retrieval_result: Dict[str, Any], 
                          max_context_length: int = 2000) -> str:
        """将检索结果格式化为上下文字符串"""
        try:
            context_parts = []
            current_length = 0
            
            # 1. 添加总结内容（优先级最高）
            summaries = retrieval_result.get("summaries", {})
            
            # 直接总结
            for summary in summaries.get("direct_summaries", []):
                summary_text = f"[总结] {summary['content']}"
                if current_length + len(summary_text) < max_context_length:
                    context_parts.append(summary_text)
                    current_length += len(summary_text)
            
            # 分组总结
            for group_id, group_summaries in summaries.get("group_summaries", {}).items():
                for summary in group_summaries:
                    summary_text = f"[{summary['topic']}总结] {summary['content']}"
                    if current_length + len(summary_text) < max_context_length:
                        context_parts.append(summary_text)
                        current_length += len(summary_text)
            
            # 2. 添加最近的对话
            session_dialogues = retrieval_result.get("session_dialogues", {})
            for session_id, session_data in session_dialogues.items():
                dialogue_pairs = session_data.get("dialogue_pairs", [])
                for pair in dialogue_pairs[-3:]:  # 最近3轮对话
                    user_text = f"[{pair['formatted_time']}] 用户: {pair['user']['content']}"
                    ai_text = f"[{pair['formatted_time']}] 助手: {pair['assistant']['content']}"
                    
                    if current_length + len(user_text) + len(ai_text) < max_context_length:
                        context_parts.append(user_text)
                        context_parts.append(ai_text)
                        current_length += len(user_text) + len(ai_text)
            
            # 3. 添加其他相关记忆
            primary_memories = retrieval_result.get("primary_memories", [])
            for memory in primary_memories[:5]:  # 最多5条
                if memory.get("type") != "summary":  # 避免重复
                    memory_text = f"[{memory['formatted_time']}] {memory['role']}: {memory['content']}"
                    if current_length + len(memory_text) < max_context_length:
                        context_parts.append(memory_text)
                        current_length += len(memory_text)
            
            # 组装最终上下文
            if context_parts:
                context = "相关记忆:\n" + "\n".join(context_parts)
            else:
                context = "没有找到相关记忆。"
            
            return context
            
        except Exception as e:
            self.logger.error(f"格式化上下文失败: {e}")
            return "上下文格式化失败。"
