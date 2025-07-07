#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步记忆评估器 (Step 11-13)
负责异步处理对话评估、存储和关联
"""

import asyncio
import json
import time
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.dialogue.engine import DialogueEngine
from core.prompts.memory_evaluation import MemoryEvaluationPrompts

logger = logging.getLogger(__name__)

class AsyncMemoryEvaluator:
    """异步记忆评估器类"""
    
    def __init__(self, db_manager=None):
        """
        初始化异步评估器
        
        参数:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager
        self.dialogue_engine = None
        self.evaluation_queue = None
        self.worker_task = None
        self.is_running = False
        self.logger = logger
    
    async def start(self):
        """启动异步评估器"""
        try:
            self.evaluation_queue = asyncio.Queue()
            self.dialogue_engine = DialogueEngine()
            self.is_running = True
            
            # 启动工作线程
            self.worker_task = asyncio.create_task(self._evaluation_worker())
            
            self.logger.info("异步记忆评估器启动成功")
            
        except Exception as e:
            self.logger.error(f"异步评估器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止异步评估器"""
        try:
            self.is_running = False
            
            if self.worker_task:
                self.worker_task.cancel()
                try:
                    await self.worker_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("异步记忆评估器已停止")
            
        except Exception as e:
            self.logger.error(f"停止异步评估器失败: {e}")
    
    async def queue_dialogue_for_evaluation(self, user_input: str, ai_response: str, 
                                          session_id: str = None, 
                                          context_memories: list = None):
        """
        将对话加入评估队列
        
        参数:
            user_input: 用户输入
            ai_response: AI响应
            session_id: 会话ID
            context_memories: 上下文记忆
        """
        try:
            dialogue_data = {
                "user_input": user_input,
                "ai_response": ai_response,
                "session_id": session_id or f"session_{int(time.time())}",
                "timestamp": time.time(),
                "context_memories": context_memories or []
            }
            
            if self.evaluation_queue:
                await self.evaluation_queue.put(dialogue_data)
                self.logger.debug("对话已加入评估队列")
            else:
                self.logger.warning("评估队列未初始化")
                
        except Exception as e:
            self.logger.error(f"加入评估队列失败: {e}")
    
    async def _evaluation_worker(self):
        """评估工作线程"""
        self.logger.info("异步评估工作线程启动")
        
        try:
            while self.is_running:
                try:
                    # 等待队列中的对话数据
                    dialogue_data = await asyncio.wait_for(
                        self.evaluation_queue.get(), 
                        timeout=1.0
                    )
                    
                    # Step 11: 评估对话
                    evaluation = await self._evaluate_dialogue(dialogue_data)
                    
                    if evaluation:
                        # Step 12: 保存评估结果
                        await self._save_evaluation_result(dialogue_data, evaluation)
                        
                        # Step 13: 创建自动关联
                        await self._create_auto_associations(dialogue_data, evaluation)
                        
                        self.logger.info(f"对话评估完成: {evaluation['super_group']} - {evaluation['weight']}分")
                    
                    # 标记任务完成
                    self.evaluation_queue.task_done()
                    
                except asyncio.TimeoutError:
                    # 队列为空，继续等待
                    continue
                except Exception as e:
                    self.logger.error(f"评估工作线程处理失败: {e}")
                    
        except Exception as e:
            self.logger.error(f"评估工作线程异常: {e}")
        finally:
            self.logger.info("异步评估工作线程结束")
    
    async def _evaluate_dialogue(self, dialogue_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Step 11: 评估对话
        
        参数:
            dialogue_data: 对话数据
            
        返回:
            评估结果字典或None
        """
        try:
            if not self.dialogue_engine:
                self.logger.warning("对话引擎未初始化")
                return None
            
            # 生成当前日期的group_id
            current_date = datetime.now().strftime("%Y_%m_%d")
            
            # 收集增强的上下文信息
            enhanced_context = await self._collect_enhanced_context(dialogue_data)
            
            # 使用提示词管理器生成评估提示词
            evaluation_prompt = MemoryEvaluationPrompts.get_dialogue_evaluation_prompt(
                user_input=dialogue_data['user_input'],
                ai_response=dialogue_data['ai_response'],
                context_info=enhanced_context
            )

            start_time = time.time()
            response = self.dialogue_engine._get_llm_response(evaluation_prompt)
            evaluation_time = time.time() - start_time
            
            self.logger.info(f"LLM评估耗时: {evaluation_time*1000:.2f}ms")
            
            # 解析JSON响应
            result = self._parse_evaluation_response(response)
            if not result:
                return None
            
            # 自动生成group_id和其他字段
            super_group = result['super_group']
            result['group_id'] = f"{super_group}_{current_date}"
            result['session_id'] = dialogue_data['session_id']
            result['timestamp'] = dialogue_data['timestamp']
            result['evaluation_time'] = evaluation_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"对话评估失败: {e}")
            return None
    
    async def _collect_enhanced_context(self, dialogue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        收集增强的上下文信息
        
        参数:
            dialogue_data: 对话数据
            
        返回:
            增强的上下文信息字典
        """
        try:
            enhanced_context = {
                'context_memories': dialogue_data.get('context_memories', [])
            }
            
            # 分析行为模式
            behavior_patterns = await self._analyze_behavior_patterns(dialogue_data)
            if behavior_patterns:
                enhanced_context['behavior_patterns'] = behavior_patterns
            
            # 分析情感趋势
            emotional_trends = await self._analyze_emotional_trends(dialogue_data)
            if emotional_trends:
                enhanced_context['emotional_trends'] = emotional_trends
            
            return enhanced_context
            
        except Exception as e:
            self.logger.error(f"收集增强上下文失败: {e}")
            return {'context_memories': dialogue_data.get('context_memories', [])}
    
    async def _analyze_behavior_patterns(self, dialogue_data: Dict[str, Any]) -> List[str]:
        """分析用户行为模式"""
        try:
            patterns = []
            context_memories = dialogue_data.get('context_memories', [])
            
            # 分析工作模式
            work_related = [m for m in context_memories if 'work' in m.get('content', '').lower()]
            if work_related:
                patterns.append("工作相关讨论频繁")
            
            # 分析时间模式
            recent_memories = [m for m in context_memories if m.get('timestamp', 0) > time.time() - 7*24*3600]
            if len(recent_memories) > 5:
                patterns.append("近期对话活跃")
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"分析行为模式失败: {e}")
            return []
    
    async def _analyze_emotional_trends(self, dialogue_data: Dict[str, Any]) -> List[str]:
        """分析情感趋势"""
        try:
            trends = []
            context_memories = dialogue_data.get('context_memories', [])
            
            # 分析情感关键词
            positive_words = ['开心', '满意', '成功', '进步', '好']
            negative_words = ['压力', '焦虑', '困难', '问题', '累']
            
            positive_count = 0
            negative_count = 0
            
            for memory in context_memories:
                content = memory.get('content', '').lower()
                for word in positive_words:
                    if word in content:
                        positive_count += 1
                for word in negative_words:
                    if word in content:
                        negative_count += 1
            
            if positive_count > negative_count:
                trends.append("整体情感倾向积极")
            elif negative_count > positive_count:
                trends.append("整体情感倾向消极")
            else:
                trends.append("情感状态相对平衡")
            
            return trends
            
        except Exception as e:
            self.logger.error(f"分析情感趋势失败: {e}")
            return []
    
    def _parse_evaluation_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        解析LLM评估响应
        
        参数:
            response: LLM原始响应
            
        返回:
            解析后的字典或None
        """
        try:
            # 提取JSON部分
            if '```json' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    return None
            elif response.strip().startswith('{'):
                result = json.loads(response.strip())
            else:
                self.logger.warning(f"无法解析的响应格式: {response[:100]}...")
                return None
            
            # 验证必需字段
            required_fields = ['summary', 'weight', 'super_group']
            for field in required_fields:
                if field not in result:
                    self.logger.warning(f"缺少必需字段: {field}")
                    return None
            
            # 验证权重范围
            if not isinstance(result['weight'], (int, float)) or not (1 <= result['weight'] <= 10):
                self.logger.warning(f"权重超出范围: {result['weight']}")
                result['weight'] = max(1, min(10, float(result['weight'])))
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"响应解析失败: {e}")
            return None
    
    async def _save_evaluation_result(self, dialogue_data: Dict[str, Any], 
                                    evaluation: Dict[str, Any]):
        """
        Step 12: 保存评估结果到数据库
        
        参数:
            dialogue_data: 对话数据
            evaluation: 评估结果
        """
        try:
            self.logger.debug("保存评估结果到数据库")
            
            # 保存用户输入记忆
            user_memory_id = await self._save_single_memory(
                content=dialogue_data['user_input'],
                role="user",
                evaluation=evaluation
            )
            
            # 保存AI回复记忆
            ai_memory_id = await self._save_single_memory(
                content=dialogue_data['ai_response'],
                role="assistant", 
                evaluation=evaluation
            )
            
            # 🆕 更新现有记忆的group_id（如果session中有相关记忆）
            await self._update_existing_memories_group_id(dialogue_data, evaluation)
            
            # 创建或更新memory_group表
            await self._create_or_update_memory_group(evaluation)
            
            # 更新分组统计
            await self._update_group_statistics(evaluation['group_id'])
            
            self.logger.info(f"✅ 评估结果保存完成 - 分组: {evaluation['group_id']}")
            
        except Exception as e:
            self.logger.error(f"保存评估结果失败: {e}")
    
    async def _save_single_memory(self, content: str, role: str, 
                                evaluation: Dict[str, Any]) -> str:
        """
        保存单条记忆到数据库
        
        参数:
            content: 记忆内容
            role: 角色 (user/assistant)
            evaluation: 评估结果
            
        返回:
            记忆ID
        """
        memory_id = str(uuid.uuid4())
        
        # 构建元数据
        metadata = {
            "super_group": evaluation['super_group'],
            "evaluation_time": evaluation.get('evaluation_time', 0),
            "auto_generated": True
        }
        
        # 插入数据库
        self.db_manager.execute_query(
            """
            INSERT INTO memories 
            (id, content, type, role, session_id, timestamp, weight, 
             group_id, summary, last_accessed, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory_id,
                content,
                "dialogue",
                role,
                evaluation['session_id'],
                evaluation['timestamp'],
                evaluation['weight'],
                evaluation['group_id'],
                evaluation['summary'],
                evaluation['timestamp'],
                json.dumps(metadata)
            )
        )
        
        # 提交事务
        if self.db_manager.conn:
            self.db_manager.conn.commit()
        
        return memory_id
    
    async def _update_existing_memories_group_id(self, dialogue_data: Dict[str, Any], 
                                               evaluation: Dict[str, Any]):
        """
        更新现有记忆的group_id字段
        
        参数:
            dialogue_data: 对话数据
            evaluation: 评估结果
        """
        try:
            if not self.db_manager:
                return
            
            session_id = dialogue_data.get('session_id')
            group_id = evaluation['group_id']
            super_group = evaluation['super_group']
            
            # 查找同一session中的相关记忆（最近24小时内，相同主题）
            recent_memories = self.db_manager.query(
                """
                SELECT id FROM memories 
                WHERE session_id = ? 
                  AND timestamp > ? 
                  AND (group_id IS NULL OR group_id = '')
                  AND (
                    content LIKE ? OR 
                    metadata LIKE ? OR
                    type = 'user_input' OR type = 'assistant_reply'
                  )
                ORDER BY timestamp DESC
                LIMIT 10
                """,
                (
                    session_id,
                    evaluation['timestamp'] - 24*3600,  # 24小时内
                    f'%{super_group}%',
                    f'%{super_group}%'
                )
            )
            
            if recent_memories:
                # 批量更新这些记忆的group_id
                memory_ids = [memory[0] for memory in recent_memories]
                placeholders = ','.join(['?' for _ in memory_ids])
                
                self.db_manager.execute_query(
                    f"""
                    UPDATE memories 
                    SET group_id = ? 
                    WHERE id IN ({placeholders})
                    """,
                    [group_id] + memory_ids
                )
                
                # 提交事务
                if self.db_manager.conn:
                    self.db_manager.conn.commit()
                
                self.logger.info(f"✅ 更新了 {len(memory_ids)} 条现有记忆的group_id为 {group_id}")
            
        except Exception as e:
            self.logger.error(f"更新现有记忆group_id失败: {e}")
    
    async def _create_or_update_memory_group(self, evaluation: Dict[str, Any]):
        """
        创建或更新memory_group记录
        
        参数:
            evaluation: 评估结果，包含group_id, super_group, summary等
        """
        try:
            if not self.db_manager:
                return
            
            group_id = evaluation['group_id']
            
            # 检查分组是否已存在
            existing_group = self.db_manager.query(
                "SELECT group_id, time_start, time_end, summary FROM memory_group WHERE group_id = ?",
                (group_id,)
            )
            
            if existing_group:
                # 更新现有分组
                await self._update_existing_group(group_id, evaluation)
                self.logger.debug(f"更新现有分组: {group_id}")
            else:
                # 创建新分组
                await self._create_new_group(evaluation)
                self.logger.debug(f"创建新分组: {group_id}")
                
        except Exception as e:
            self.logger.error(f"创建/更新分组失败: {e}")
    
    async def _create_new_group(self, evaluation: Dict[str, Any]):
        """
        创建新的memory_group记录
        
        参数:
            evaluation: 评估结果
        """
        try:
            # 生成话题描述
            topic = await self._generate_topic_description(evaluation)
            
            # 插入新分组记录
            self.db_manager.execute_query(
                """
                INSERT INTO memory_group 
                (group_id, super_group, topic, time_start, time_end, summary, score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evaluation['group_id'],
                    evaluation['super_group'],
                    topic,
                    evaluation['timestamp'],  # 设置开始时间为当前对话时间
                    evaluation['timestamp'],  # 暂时设置结束时间也为当前时间
                    evaluation['summary'],
                    evaluation['weight']
                )
            )
            
            # 提交事务
            if self.db_manager.conn:
                self.db_manager.conn.commit()
            
            self.logger.info(f"✅ 创建新话题分组: {evaluation['group_id']} - {topic}")
            
        except Exception as e:
            self.logger.error(f"创建新分组失败: {e}")
    
    async def _update_existing_group(self, group_id: str, evaluation: Dict[str, Any]):
        """
        更新现有的memory_group记录
        
        参数:
            group_id: 分组ID
            evaluation: 新的评估结果
        """
        try:
            # 更新时间范围和摘要
            self.db_manager.execute_query(
                """
                UPDATE memory_group 
                SET time_end = ?, 
                    summary = CASE 
                        WHEN LENGTH(summary) < LENGTH(?) THEN ?
                        ELSE summary 
                    END,
                    score = (score + ?) / 2.0
                WHERE group_id = ?
                """,
                (
                    evaluation['timestamp'],  # 更新结束时间
                    evaluation['summary'],    # 比较摘要长度
                    evaluation['summary'],    # 如果新摘要更长，则使用新摘要
                    evaluation['weight'],     # 平均分数
                    group_id
                )
            )
            
            # 提交事务
            if self.db_manager.conn:
                self.db_manager.conn.commit()
            
            self.logger.debug(f"更新分组时间范围: {group_id}")
            
        except Exception as e:
            self.logger.error(f"更新现有分组失败: {e}")
    
    async def _generate_topic_description(self, evaluation: Dict[str, Any]) -> str:
        """
        生成话题描述
        
        参数:
            evaluation: 评估结果
            
        返回:
            话题描述字符串
        """
        try:
            # 基于super_group和summary生成描述
            super_group = evaluation.get('super_group', '未分类')
            summary = evaluation.get('summary', '')
            
            # 简单的话题描述生成逻辑
            if summary:
                # 提取摘要的前50个字符作为话题
                topic = summary[:50].strip()
                if len(summary) > 50:
                    topic += "..."
            else:
                # 如果没有摘要，使用super_group
                topic = f"{super_group}相关讨论"
            
            return topic
            
        except Exception as e:
            self.logger.error(f"生成话题描述失败: {e}")
            return evaluation.get('super_group', '未知话题')
    
    async def _update_group_statistics(self, group_id: str):
        """
        更新分组统计信息
        
        参数:
            group_id: 分组ID
        """
        try:
            if not self.db_manager:
                return
            
            # 获取该分组下的所有记忆统计
            stats = self.db_manager.query(
                """
                SELECT COUNT(*) as memory_count,
                       AVG(weight) as avg_weight,
                       MIN(timestamp) as earliest_time,
                       MAX(timestamp) as latest_time
                FROM memories 
                WHERE group_id = ?
                """,
                (group_id,)
            )
            
            if stats and stats[0]:
                memory_count, avg_weight, earliest_time, latest_time = stats[0]
                
                # 更新分组的统计信息
                self.db_manager.execute_query(
                    """
                    UPDATE memory_group 
                    SET time_start = ?,
                        time_end = ?,
                        score = ?
                    WHERE group_id = ?
                    """,
                    (earliest_time, latest_time, avg_weight or 1.0, group_id)
                )
                
                # 提交事务
                if self.db_manager.conn:
                    self.db_manager.conn.commit()
                
                self.logger.debug(f"更新分组统计: {group_id}, 记忆数: {memory_count}, 平均权重: {avg_weight:.2f}")
            
        except Exception as e:
            self.logger.error(f"更新分组统计失败: {e}")
    
    async def _create_auto_associations(self, dialogue_data: Dict[str, Any], 
                                      evaluation: Dict[str, Any]):
        """
        Step 13: 创建自动关联
        
        参数:
            dialogue_data: 对话数据
            evaluation: 评估结果
        """
        try:
            if not self.db_manager:
                return
            
            # 查找相同super_group的最近记忆
            recent_memories = self.db_manager.query(
                """
                SELECT id, content, timestamp, weight, group_id
                FROM memories 
                WHERE metadata LIKE ? 
                  AND timestamp > ?
                  AND group_id != ?
                ORDER BY timestamp DESC
                LIMIT 5
                """,
                (
                    f'%"super_group": "{evaluation["super_group"]}"%',
                    evaluation['timestamp'] - 7*24*3600,  # 7天内
                    evaluation['group_id']
                )
            )
            
            if recent_memories:
                self.logger.info(f"为 {evaluation['group_id']} 找到 {len(recent_memories)} 个潜在关联")
                # 这里可以进一步实现关联逻辑
                
        except Exception as e:
            self.logger.error(f"创建自动关联失败: {e}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        获取队列状态
        
        返回:
            状态信息字典
        """
        try:
            return {
                "is_running": self.is_running,
                "queue_size": self.evaluation_queue.qsize() if self.evaluation_queue else 0,
                "worker_active": self.worker_task is not None and not self.worker_task.done()
            }
        except Exception as e:
            self.logger.error(f"获取队列状态失败: {e}")
            return {"error": str(e)} 