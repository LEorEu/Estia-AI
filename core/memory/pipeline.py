#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆处理管道
协调各个记忆模块的工作流程，集成Step 7-10
"""

import time
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# 导入核心模块
from .init.db_manager import DatabaseManager
from .evaluator.async_evaluator import AsyncMemoryEvaluator
from .context.builder import ContextBuilder
from .retrieval.smart_retriever import SmartRetriever

# 设置日志
logger = logging.getLogger(__name__)

class MemoryPipeline:
    """
    记忆处理管道类
    协调完整的记忆处理流程 (Step 1-13)
    """
    
    def __init__(self):
        """初始化记忆管道"""
        self.db_manager = None
        self.async_evaluator = None
        self.context_builder = None
        self.smart_retriever = None
        self.is_initialized = False
        self._async_init_task = None
        self._initialization_lock = asyncio.Lock() if hasattr(asyncio, 'Lock') else None
        self._is_first_query = True  # 标记是否为第一次查询
        
        logger.info("记忆管道初始化开始")
        self._initialize_sync()
        
    def _initialize_sync(self):
        """同步初始化核心组件"""
        try:
            # 初始化数据库
            db_path = "data/memory.db"
            self.db_manager = DatabaseManager(db_path)
            
            if not self.db_manager.initialize_database():
                raise Exception("数据库初始化失败")
            
            # 初始化智能检索器
            self.smart_retriever = SmartRetriever(self.db_manager)
            
            # 初始化上下文构建器
            self.context_builder = ContextBuilder(
                max_context_length=2000,
                max_memories=15
            )
            
            self.is_initialized = True
            logger.info("记忆管道核心组件初始化完成")
            
        except Exception as e:
            logger.error(f"记忆管道初始化失败: {e}")
            raise
    
    async def ensure_async_initialized(self):
        """确保异步组件已初始化"""
        if not self.async_evaluator:
            await self._initialize_async_components()
    
    async def _initialize_async_components(self):
        """异步初始化组件"""
        try:
            if not self.async_evaluator:
                logger.info("正在初始化异步评估器...")
                self.async_evaluator = AsyncMemoryEvaluator(self.db_manager)
                await self.async_evaluator.start()
                logger.info("异步评估器启动完成")
        except Exception as e:
            logger.error(f"异步组件初始化失败: {e}")
        finally:
            self._async_init_task = None
    
    def enhance_query(self, user_input: str, context: Optional[Dict] = None) -> str:
        """
        增强用户查询 - Step 1-8的完整流程
        
        参数:
            user_input: 用户输入
            context: 可选上下文
            
        返回:
            增强后的上下文字符串
        """
        try:
            start_time = time.time()
            logger.info(f"开始记忆增强查询: {user_input[:30]}...")
            
            if not self.is_initialized:
                logger.warning("记忆管道未初始化，返回原始输入")
                return user_input
            
            # Step 1-6: 记忆检索和处理
            retrieved_memories = self._retrieve_memories(user_input)
            logger.info(f"Step 1-6 记忆检索: 找到 {len(retrieved_memories)} 条记忆")
            
            # Step 7: 记忆排序和去重
            ranked_memories = self._simple_rank_memories(retrieved_memories)
            logger.info(f"Step 7 记忆排序: 保留 {len(ranked_memories)} 条记忆")
            
            # Step 8: 上下文构建
            enhanced_context = self._simple_build_context(ranked_memories, user_input)
            
            processing_time = time.time() - start_time
            logger.info(f"Step 8 上下文构建完成: {len(enhanced_context)} 字符，耗时: {processing_time*1000:.2f}ms")
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"查询增强失败: {e}")
            return f"基于用户输入: {user_input}"
    
    def _retrieve_memories(self, user_input: str) -> List[Dict[str, Any]]:
        """
        Step 1-6: 检索相关记忆
        """
        try:
            if not self.smart_retriever:
                return []
            
            # 第一次查询：主动提供最近+高权重记忆
            if self._is_first_query:
                logger.info("第一次查询，提供最近记忆+高权重记忆作为上下文")
                self._is_first_query = False
                return self.smart_retriever.get_startup_memories()
            
            # 后续查询：根据内容进行智能检索
            return self.smart_retriever.smart_search(user_input)
            
        except Exception as e:
            logger.error(f"记忆检索失败: {e}")
            return []
    
    def _simple_rank_memories(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Step 7: 记忆排序和去重
        """
        try:
            if not memories:
                return []
            
            # 计算综合评分
            for memory in memories:
                score = 0.0
                
                # 基础权重
                base_weight = float(memory.get('weight', 5.0))
                score += base_weight
                
                # 类型加成
                memory_type = memory.get('type', '')
                if memory_type == 'summary':
                    score += 2.0
                elif memory_type == 'user_input':
                    score += 1.0
                
                # 时间加成
                timestamp = memory.get('timestamp')
                if timestamp:
                    try:
                        if isinstance(timestamp, str):
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            timestamp = dt.timestamp()
                        
                        time_diff_hours = (time.time() - timestamp) / 3600
                        if time_diff_hours < 24:  # 24小时内
                            score += 1.0
                    except:
                        pass
                
                memory['computed_score'] = score
            
            # 按评分排序
            sorted_memories = sorted(memories, 
                                   key=lambda x: x.get('computed_score', 0), 
                                   reverse=True)
            
            # 简单去重
            deduplicated = []
            seen_content = set()
            
            for memory in sorted_memories:
                content = memory.get('content', '').strip()
                if content and content not in seen_content:
                    deduplicated.append(memory)
                    seen_content.add(content)
                    
                if len(deduplicated) >= 10:  # 限制数量
                    break
            
            logger.debug(f"记忆排序完成: {len(memories)} -> {len(deduplicated)} 条")
            return deduplicated
            
        except Exception as e:
            logger.error(f"记忆排序失败: {e}")
            return memories[:10]
    
    def _simple_build_context(self, memories: List[Dict[str, Any]], user_input: str) -> str:
        """
        Step 8: 使用专门的上下文构建器构建上下文
        """
        try:
            if not self.context_builder:
                # 降级到简单模式
                return self._fallback_build_context(memories, user_input)
            
            # 使用专门的上下文构建器
            enhanced_context = self.context_builder.build_enhanced_context(
                user_input=user_input,
                ranked_memories=memories,
                personality_info=None  # 暂时不使用个性化信息
            )
            
            logger.debug(f"专业上下文构建完成，长度: {len(enhanced_context)} 字符")
            return enhanced_context
            
        except Exception as e:
            logger.error(f"专业上下文构建失败: {e}")
            return self._fallback_build_context(memories, user_input)
    
    def _fallback_build_context(self, memories: List[Dict[str, Any]], user_input: str) -> str:
        """
        降级版上下文构建（原简化版）
        """
        try:
            if not memories:
                return f"用户输入: {user_input}"
            
            context_parts = []
            
            # 添加高分记忆
            high_score_memories = [m for m in memories if m.get('computed_score', 0) >= 8.0]
            if high_score_memories:
                context_parts.append("[重要记忆]")
                for memory in high_score_memories[:3]:
                    content = memory.get('content', '')
                    if len(content) > 100:
                        content = content[:100] + "..."
                    context_parts.append(f"• {content}")
                context_parts.append("")
            
            # 添加其他相关记忆
            other_memories = [m for m in memories if m.get('computed_score', 0) < 8.0]
            if other_memories:
                context_parts.append("[相关记忆]")
                for memory in other_memories[:5]:
                    content = memory.get('content', '')
                    if len(content) > 80:
                        content = content[:80] + "..."
                    context_parts.append(f"• {content}")
                context_parts.append("")
            
            # 添加用户输入
            context_parts.append(f"[用户当前输入]\n{user_input}")
            
            final_context = "\n".join(context_parts)
            logger.debug(f"降级上下文构建完成，长度: {len(final_context)} 字符")
            
            return final_context
            
        except Exception as e:
            logger.error(f"降级上下文构建失败: {e}")
            return f"用户输入: {user_input}"
    
    def store_interaction(self, user_input: str, ai_response: str, context: Optional[Dict] = None):
        """
        存储交互记录 - Step 11-13异步处理
        
        参数:
            user_input: 用户输入
            ai_response: AI响应
            context: 可选上下文
        """
        try:
            if self.async_evaluator:
                # 异步队列处理，不阻塞主线程
                session_id = f"session_{int(time.time())}"
                
                # 检查是否在异步环境中
                try:
                    loop = asyncio.get_running_loop()
                    # 在异步环境中，创建任务
                    asyncio.create_task(
                        self.async_evaluator.queue_dialogue_for_evaluation(
                            user_input=user_input,
                            ai_response=ai_response,
                            session_id=session_id,
                            context_memories=[]
                        )
                    )
                except RuntimeError:
                    # 不在异步环境中，使用线程池处理
                    import threading
                    def async_worker():
                        asyncio.run(self.async_evaluator.queue_dialogue_for_evaluation(
                            user_input=user_input,
                            ai_response=ai_response,
                            session_id=session_id,
                            context_memories=[]
                        ))
                    
                    thread = threading.Thread(target=async_worker, daemon=True)
                    thread.start()
                
                logger.debug("对话已加入异步评估队列")
            else:
                logger.warning("异步评估器未初始化，跳过存储")
                
        except Exception as e:
            logger.error(f"存储交互记录失败: {e}")
            # 存储失败不影响用户体验
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆系统统计信息"""
        try:
            stats = {
                "initialized": self.is_initialized,
                "database_connected": self.db_manager is not None,
                "async_evaluator_running": False,
                "total_memories": 0,
                "recent_memories": 0
            }
            
            if self.async_evaluator:
                queue_status = self.async_evaluator.get_queue_status()
                stats["async_evaluator_running"] = queue_status.get("is_running", False)
                stats["queue_size"] = queue_status.get("queue_size", 0)
            
            if self.db_manager:
                # 总记忆数
                total_result = self.db_manager.query("SELECT COUNT(*) FROM memories")
                if total_result:
                    stats["total_memories"] = total_result[0][0]
                
                # 最近24小时的记忆数
                recent_result = self.db_manager.query("""
                    SELECT COUNT(*) FROM memories 
                    WHERE datetime(timestamp) > datetime('now', '-1 day')
                """)
                if recent_result:
                    stats["recent_memories"] = recent_result[0][0]
            
            return stats
            
        except Exception as e:
            logger.error(f"获取记忆统计失败: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """关闭管道"""
        try:
            if self.async_evaluator:
                await self.async_evaluator.stop()
            
            if self.db_manager:
                self.db_manager.close()
            
            logger.info("记忆管道已关闭")
        except Exception as e:
            logger.error(f"关闭管道失败: {e}")
