#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
关联网络模块
实现记忆之间的语义关联和多层检索功能
"""

import time
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Set, Tuple
from sklearn.metrics.pairwise import cosine_similarity

# 设置日志
logger = logging.getLogger(__name__)

class AssociationNetwork:
    """
    记忆关联网络类
    负责建立、维护和查询记忆之间的关联关系
    """
    
    def __init__(self, db_manager=None):
        """
        初始化关联网络
        
        参数:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager
        self.association_cache = {}  # 缓存关联关系
        self.strength_threshold = 0.2  # 最小关联强度阈值
        self.max_associations_per_memory = 10  # 每个记忆的最大关联数
        
        # 关联类型权重
        self.association_weights = {
            "same_topic": 1.2,
            "temporal_sequence": 1.1,
            "is_related_to": 1.0,
            "cause_effect": 1.15,
            "contradiction": 0.8
        }
        
        logger.info("关联网络初始化完成")
    
    def calculate_association_strength(self, memory1: Dict[str, Any], 
                                     memory2: Dict[str, Any]) -> float:
        """
        计算两个记忆之间的关联强度
        
        参数:
            memory1: 第一个记忆
            memory2: 第二个记忆
            
        返回:
            float: 关联强度 (0-1)
        """
        try:
            # 基础语义相似度（需要向量化器支持）
            base_strength = 0.0
            
            # 简化版：基于内容的文本相似度
            content1 = memory1.get("content", "").lower()
            content2 = memory2.get("content", "").lower()
            
            # 关键词重叠度
            words1 = set(content1.split())
            words2 = set(content2.split())
            
            if len(words1) > 0 and len(words2) > 0:
                overlap = len(words1.intersection(words2))
                union = len(words1.union(words2))
                base_strength = overlap / union if union > 0 else 0
            
            # 时间接近度加成
            time_bonus = self._calculate_time_bonus(memory1, memory2)
            
            # 主题一致性加成  
            topic_bonus = self._calculate_topic_bonus(memory1, memory2)
            
            # 重要性影响
            importance_factor = (memory1.get("importance", 0.5) + 
                               memory2.get("importance", 0.5)) / 2
            
            # 综合计算
            final_strength = min(1.0, base_strength + time_bonus + topic_bonus)
            final_strength *= (0.5 + importance_factor * 0.5)  # 重要性调节
            
            return max(0.0, final_strength)
            
        except Exception as e:
            logger.error(f"计算关联强度失败: {e}")
            return 0.0
    
    def _calculate_time_bonus(self, memory1: Dict[str, Any], 
                            memory2: Dict[str, Any]) -> float:
        """计算时间接近度加成"""
        try:
            timestamp1 = memory1.get("created_at", 0)
            timestamp2 = memory2.get("created_at", 0)
            
            if timestamp1 == 0 or timestamp2 == 0:
                return 0.0
            
            time_diff = abs(timestamp1 - timestamp2)
            days_diff = time_diff / (24 * 3600)
            
            if days_diff <= 1:
                return 0.2      # 同一天
            elif days_diff <= 7:
                return 0.1      # 同一周
            elif days_diff <= 30:
                return 0.05     # 同一月
            else:
                return 0.0      # 时间太远
                
        except Exception:
            return 0.0
    
    def _calculate_topic_bonus(self, memory1: Dict[str, Any], 
                             memory2: Dict[str, Any]) -> float:
        """计算主题一致性加成"""
        try:
            # 检查元数据中的分类
            meta1 = memory1.get("metadata", {})
            meta2 = memory2.get("metadata", {})
            
            category1 = meta1.get("category", "")
            category2 = meta2.get("category", "")
            
            if category1 and category2 and category1 == category2:
                return 0.15  # 同类别加成
            
            # 检查内容中的关键概念
            content1 = memory1.get("content", "").lower()
            content2 = memory2.get("content", "").lower()
            
            # 简单的关键词检查
            tech_keywords = ["python", "编程", "ai", "机器学习", "深度学习", "算法"]
            life_keywords = ["天气", "散步", "电影", "朋友", "周末"]
            work_keywords = ["项目", "团队", "公司", "会议", "工作"]
            
            for keywords in [tech_keywords, life_keywords, work_keywords]:
                count1 = sum(1 for kw in keywords if kw in content1)
                count2 = sum(1 for kw in keywords if kw in content2)
                
                if count1 > 0 and count2 > 0:
                    return 0.1  # 同主题关键词加成
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def auto_create_associations(self, memory_id: str, memory_content: Dict[str, Any],
                               existing_memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        为新记忆自动创建关联
        
        参数:
            memory_id: 新记忆的ID
            memory_content: 新记忆的内容
            existing_memories: 现有记忆列表
            
        返回:
            List[Dict[str, Any]]: 创建的关联列表
        """
        try:
            associations = []
            
            for existing_memory in existing_memories:
                # 跳过自己
                if existing_memory.get("memory_id") == memory_id:
                    continue
                
                # 计算关联强度
                strength = self.calculate_association_strength(memory_content, existing_memory)
                
                # 只为高强度关联创建关联关系
                if strength >= self.strength_threshold:
                    
                    # 确定关联类型
                    association_type = self._determine_association_type(
                        memory_content, existing_memory, strength
                    )
                    
                    # 应用关联类型权重
                    final_strength = min(1.0, strength * self.association_weights.get(association_type, 1.0))
                    
                    association = {
                        "source_id": memory_id,
                        "target_id": existing_memory.get("memory_id"),
                        "association_type": association_type,
                        "strength": final_strength,
                        "created_at": time.time()
                    }
                    
                    associations.append(association)
            
            # 限制关联数量，保留强度最高的
            associations.sort(key=lambda x: x["strength"], reverse=True)
            associations = associations[:self.max_associations_per_memory]
            
            # 保存到数据库
            for assoc in associations:
                self._save_association_to_db(assoc)
            
            logger.info(f"为记忆 {memory_id} 创建了 {len(associations)} 个关联")
            return associations
            
        except Exception as e:
            logger.error(f"自动创建关联失败: {e}")
            return []
    
    def _determine_association_type(self, memory1: Dict[str, Any], 
                                  memory2: Dict[str, Any], 
                                  strength: float) -> str:
        """确定关联类型"""
        try:
            content1 = memory1.get("content", "").lower()
            content2 = memory2.get("content", "").lower()
            
            # 检查时间序列关系
            time1 = memory1.get("created_at", 0)
            time2 = memory2.get("created_at", 0)
            time_diff = abs(time1 - time2) / (24 * 3600) if time1 and time2 else 999
            
            if time_diff <= 2:  # 2天内
                if any(word in content1 and word in content2 for word in ["然后", "接着", "后来", "之后"]):
                    return "temporal_sequence"
            
            # 检查主题一致性
            if strength > 0.8:
                # 检查是否同主题
                meta1 = memory1.get("metadata", {})
                meta2 = memory2.get("metadata", {})
                
                if meta1.get("category") == meta2.get("category") and meta1.get("category"):
                    return "same_topic"
            
            # 检查因果关系
            cause_words = ["因为", "由于", "导致", "造成", "结果"]
            if any(word in content1 or word in content2 for word in cause_words):
                return "cause_effect"
            
            # 检查矛盾关系
            contradiction_words = ["但是", "然而", "不过", "相反", "矛盾"]
            if any(word in content1 or word in content2 for word in contradiction_words):
                return "contradiction"
            
            # 默认为一般相关
            return "is_related_to"
            
        except Exception:
            return "is_related_to"
    
    def _save_association_to_db(self, association: Dict[str, Any]) -> bool:
        """保存关联到数据库"""
        try:
            if not self.db_manager:
                return False
            
            # 检查关联是否已存在
            existing = self.db_manager.query(
                """
                SELECT id FROM memory_association 
                WHERE (source_key = ? AND target_key = ?) 
                   OR (source_key = ? AND target_key = ?)
                """,
                (association["source_id"], association["target_id"],
                 association["target_id"], association["source_id"])
            )
            
            if existing:
                # 更新现有关联
                self.db_manager.execute_query(
                    """
                    UPDATE memory_association 
                    SET strength = ?, association_type = ?, last_activated = ?
                    WHERE id = ?
                    """,
                    (association["strength"], association["association_type"], 
                     time.time(), existing[0][0])
                )
            else:
                # 创建新关联
                assoc_id = f"assoc_{int(time.time() * 1000000)}"
                self.db_manager.execute_query(
                    """
                    INSERT INTO memory_association 
                    (id, source_key, target_key, association_type, 
                     strength, created_at, last_activated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (assoc_id, association["source_id"], association["target_id"],
                     association["association_type"], association["strength"],
                     association["created_at"], association["created_at"])
                )
            
            # 提交事务
            if self.db_manager.conn:
                self.db_manager.conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"保存关联到数据库失败: {e}")
            return False
    
    def get_related_memories(self, memory_id: str, depth: int = 1, 
                           min_strength: float = 0.5) -> List[Dict[str, Any]]:
        """
        获取关联记忆（支持多层检索）
        
        参数:
            memory_id: 源记忆ID
            depth: 检索深度 (1 或 2)
            min_strength: 最小关联强度
            
        返回:
            List[Dict[str, Any]]: 关联记忆列表
        """
        try:
            if depth == 1:
                return self._get_direct_associations(memory_id, min_strength)
            elif depth == 2:
                return self._get_two_hop_associations(memory_id, min_strength)
            else:
                logger.warning(f"不支持的检索深度: {depth}")
                return []
                
        except Exception as e:
            logger.error(f"获取关联记忆失败: {e}")
            return []
    
    def _get_direct_associations(self, memory_id: str, min_strength: float) -> List[Dict[str, Any]]:
        """获取直接关联的记忆"""
        try:
            if not self.db_manager:
                return []
            
            # 查询关联关系
            associations = self.db_manager.query(
                """
                SELECT ma.target_key, ma.association_type, ma.strength,
                       m.content, m.role, m.timestamp, m.weight, m.metadata
                FROM memory_association ma
                JOIN memories m ON ma.target_key = m.id
                WHERE ma.source_key = ? AND ma.strength >= ?
                
                UNION
                
                SELECT ma.source_key, ma.association_type, ma.strength,
                       m.content, m.role, m.timestamp, m.weight, m.metadata
                FROM memory_association ma
                JOIN memories m ON ma.source_key = m.id
                WHERE ma.target_key = ? AND ma.strength >= ?
                
                ORDER BY strength DESC
                """,
                (memory_id, min_strength, memory_id, min_strength)
            )
            
            # 更新访问统计
            self._update_association_access(memory_id)
            
            # 构建结果
            related_memories = []
            for row in associations:
                try:
                    metadata = json.loads(row[7]) if row[7] else {}
                except:
                    metadata = {}
                
                related_memories.append({
                    "memory_id": row[0],
                    "association_type": row[1],
                    "strength": row[2],
                    "content": row[3],
                    "source": row[4],
                    "created_at": row[5],
                    "importance": row[6],
                    "metadata": metadata,
                    "association_path": [memory_id, row[0]]  # 记录关联路径
                })
            
            return related_memories
            
        except Exception as e:
            logger.error(f"获取直接关联失败: {e}")
            return []
    
    def _get_two_hop_associations(self, memory_id: str, min_strength: float) -> List[Dict[str, Any]]:
        """获取二度关联的记忆"""
        try:
            # 先获取直接关联
            direct_associations = self._get_direct_associations(memory_id, min_strength)
            
            # 获取二度关联
            visited_ids = {memory_id}  # 避免循环
            two_hop_memories = []
            
            for direct_memory in direct_associations:
                direct_id = direct_memory["memory_id"]
                visited_ids.add(direct_id)
                
                # 获取这个记忆的关联
                indirect_associations = self._get_direct_associations(direct_id, min_strength * 0.8)
                
                for indirect_memory in indirect_associations:
                    indirect_id = indirect_memory["memory_id"]
                    
                    # 避免重复和循环
                    if indirect_id not in visited_ids:
                        # 计算综合强度
                        combined_strength = (direct_memory["strength"] * 
                                           indirect_memory["strength"])
                        
                        if combined_strength >= min_strength * 0.6:  # 二度关联阈值稍低
                            indirect_memory["strength"] = combined_strength
                            indirect_memory["association_path"] = [
                                memory_id, direct_id, indirect_id
                            ]
                            indirect_memory["is_two_hop"] = True
                            
                            two_hop_memories.append(indirect_memory)
                            visited_ids.add(indirect_id)
            
            # 合并直接和间接关联，按强度排序
            all_associations = direct_associations + two_hop_memories
            all_associations.sort(key=lambda x: x["strength"], reverse=True)
            
            return all_associations
            
        except Exception as e:
            logger.error(f"获取二度关联失败: {e}")
            return []
    
    def _update_association_access(self, memory_id: str):
        """更新关联访问统计"""
        try:
            if not self.db_manager:
                return
            
            current_time = time.time()
            
            # 更新所有涉及此记忆的关联
            self.db_manager.execute_query(
                """
                UPDATE memory_association 
                SET last_activated = ?
                WHERE source_key = ? OR target_key = ?
                """,
                (current_time, memory_id, memory_id)
            )
            
            if self.db_manager.conn:
                self.db_manager.conn.commit()
                
        except Exception as e:
            logger.error(f"更新关联访问统计失败: {e}")
    
    def update_association_strength(self, source_id: str, target_id: str, 
                                  strength_delta: float = 0.01):
        """
        更新关联强度（基于使用频率）
        
        参数:
            source_id: 源记忆ID
            target_id: 目标记忆ID
            strength_delta: 强度增量
        """
        try:
            if not self.db_manager:
                return
            
            self.db_manager.execute_query(
                """
                UPDATE memory_association 
                SET strength = MIN(1.0, strength + ?)
                WHERE (source_key = ? AND target_key = ?)
                   OR (source_key = ? AND target_key = ?)
                """,
                (strength_delta, source_id, target_id, target_id, source_id)
            )
            
            if self.db_manager.conn:
                self.db_manager.conn.commit()
                
        except Exception as e:
            logger.error(f"更新关联强度失败: {e}")
    
    def decay_unused_associations(self, days_threshold: int = 30, 
                                decay_factor: float = 0.95):
        """
        衰减长时间未使用的关联
        
        参数:
            days_threshold: 天数阈值
            decay_factor: 衰减因子
        """
        try:
            if not self.db_manager:
                return
            
            threshold_time = time.time() - (days_threshold * 24 * 3600)
            
            # 衰减旧关联
            self.db_manager.execute_query(
                """
                UPDATE memory_association 
                SET strength = MAX(0.1, strength * ?)
                WHERE last_activated < ?
                """,
                (decay_factor, threshold_time)
            )
            
            # 删除强度过低的关联
            self.db_manager.execute_query(
                """
                DELETE FROM memory_association 
                WHERE strength < 0.1
                """,
                ()
            )
            
            if self.db_manager.conn:
                self.db_manager.conn.commit()
            
            logger.info("关联衰减完成")
            
        except Exception as e:
            logger.error(f"关联衰减失败: {e}")
    
    def get_association_stats(self) -> Dict[str, Any]:
        """获取关联网络统计信息"""
        try:
            if not self.db_manager:
                return {}
            
            # 总关联数
            total_result = self.db_manager.query(
                "SELECT COUNT(*) FROM memory_association", ()
            )
            total_count = total_result[0][0] if total_result else 0
            
            # 各类型关联数
            type_stats = self.db_manager.query(
                """
                SELECT association_type, COUNT(*) 
                FROM memory_association 
                GROUP BY association_type
                """, ()
            )
            
            # 强度分布
            strength_result = self.db_manager.query(
                """
                SELECT 
                    COUNT(CASE WHEN strength >= 0.8 THEN 1 END) as strong,
                    COUNT(CASE WHEN strength >= 0.6 AND strength < 0.8 THEN 1 END) as medium,
                    COUNT(CASE WHEN strength < 0.6 THEN 1 END) as weak
                FROM memory_association
                """, ()
            )
            
            strength_stats = strength_result[0] if strength_result else (0, 0, 0)
            
            return {
                "total_associations": total_count,
                "type_distribution": dict(type_stats) if type_stats else {},
                "strength_distribution": {
                    "strong": strength_stats[0],
                    "medium": strength_stats[1], 
                    "weak": strength_stats[2]
                }
            }
            
        except Exception as e:
            logger.error(f"获取关联统计失败: {e}")
            return {}

    def create_association(self, source_id: str, target_id: str, strength: float = 0.5) -> bool:
        """
        创建两个记忆之间的关联
        
        参数:
            source_id: 源记忆ID
            target_id: 目标记忆ID
            strength: 关联强度
            
        返回:
            bool: 是否创建成功
        """
        try:
            if not self.db_manager:
                logger.error("数据库管理器未初始化")
                return False
            
            # 检查关联是否已存在（只检查单向）
            existing = self.db_manager.query(
                """
                SELECT id FROM memory_association 
                WHERE source_key = ? AND target_key = ?
                """,
                (source_id, target_id)
            )
            
            if existing:
                logger.debug(f"关联已存在: {source_id} -> {target_id}")
                return True
            
            # 创建新关联
            association_id = f"assoc_{int(time.time() * 1000)}"
            result = self.db_manager.execute_query(
                """
                INSERT INTO memory_association 
                (id, source_key, target_key, association_type, strength, created_at, last_activated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (association_id, source_id, target_id, "is_related_to", strength, time.time(), time.time())
            )
            
            if result:
                logger.debug(f"✅ 关联创建成功: {source_id} -> {target_id} ({strength:.2f})")
                return True
            else:
                logger.error(f"❌ 关联创建失败: {source_id} -> {target_id}")
                return False
                
        except Exception as e:
            logger.error(f"创建关联失败: {e}")
            return False
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """
        获取关联网络统计信息
        
        返回:
            Dict[str, Any]: 网络统计信息
        """
        try:
            if not self.db_manager:
                return {"error": "数据库管理器未初始化"}
            
            # 获取基本统计
            stats = self.db_manager.query(
                """
                SELECT 
                    COUNT(*) as total_associations,
                    COUNT(DISTINCT source_key) as unique_sources,
                    COUNT(DISTINCT target_key) as unique_targets,
                    AVG(strength) as avg_strength,
                    MAX(strength) as max_strength,
                    MIN(strength) as min_strength
                FROM memory_association
                """
            )
            
            if stats:
                result = dict(stats[0])
                result['status'] = 'success'
                return result
            else:
                return {"status": "no_data", "total_associations": 0}
                
        except Exception as e:
            logger.error(f"获取网络统计失败: {e}")
            return {"error": str(e)}
    
    def delete_association(self, source_id: str, target_id: str) -> bool:
        """
        删除两个记忆之间的关联
        
        参数:
            source_id: 源记忆ID
            target_id: 目标记忆ID
            
        返回:
            bool: 是否删除成功
        """
        try:
            if not self.db_manager:
                logger.error("数据库管理器未初始化")
                return False
            
            result = self.db_manager.execute_query(
                """
                DELETE FROM memory_association 
                WHERE (source_key = ? AND target_key = ?) OR (source_key = ? AND target_key = ?)
                """,
                (source_id, target_id, target_id, source_id)
            )
            
            if result:
                logger.debug(f"✅ 关联删除成功: {source_id} <-> {target_id}")
                return True
            else:
                logger.warning(f"⚠️ 关联删除失败或不存在: {source_id} <-> {target_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除关联失败: {e}")
            return False
