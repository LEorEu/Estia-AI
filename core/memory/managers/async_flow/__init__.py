#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步流程管理器 (AsyncFlowManager)
负责Step 10-15: 异步评估、权重更新、关联建立
职责：后台评估，不影响用户体验的异步操作
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from ...internal import handle_memory_errors, ErrorHandlerMixin

logger = logging.getLogger(__name__)

class AsyncFlowManager(ErrorHandlerMixin):
    """异步流程管理器 - 处理Step 10-15的后台流程"""
    
    def __init__(self, components: Dict[str, Any]):
        """
        初始化异步流程管理器
        
        Args:
            components: 所需的组件字典
        """
        super().__init__()
        self.async_evaluator = components.get('async_evaluator')
        self.weight_manager = components.get('weight_manager')
        self.layer_manager = components.get('layer_manager')
        self.association_network = components.get('association_network')
        self.summary_generator = components.get('summary_generator')
        
        self.evaluation_queue = asyncio.Queue()
        self.is_running = False
        self.logger = logger
    
    async def start_async_processing(self):
        """启动异步处理循环"""
        self.is_running = True
        self.logger.info("🔄 启动异步流程管理器")
        
        # 启动异步处理任务
        asyncio.create_task(self._process_evaluation_queue())
    
    async def stop_async_processing(self):
        """停止异步处理"""
        self.is_running = False
        self.logger.info("⏹️ 停止异步流程管理器")
    
    @handle_memory_errors("异步流程触发失败")
    async def trigger_async_evaluation(self, user_input: str, ai_response: str, 
                                     memory_ids: Dict[str, Any], context: Optional[Dict] = None):
        """
        触发异步评估 (Step 10)
        
        Args:
            user_input: 用户输入
            ai_response: AI回复
            memory_ids: 存储的记忆ID
            context: 上下文信息
        """
        evaluation_task = {
            'user_input': user_input,
            'ai_response': ai_response,
            'memory_ids': memory_ids,
            'context': context,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        await self.evaluation_queue.put(evaluation_task)
        self.logger.debug("📋 异步评估任务已加入队列")
    
    async def _process_evaluation_queue(self):
        """处理异步评估队列"""
        while self.is_running:
            try:
                # Step 10: 获取评估任务
                task = await asyncio.wait_for(
                    self.evaluation_queue.get(), timeout=1.0
                )
                
                # Step 11: LLM评估对话重要性
                evaluation_result = await self._llm_evaluate_dialogue(task)
                
                # Step 12: 更新记忆权重
                await self._update_memory_weights(task, evaluation_result)
                
                # Step 13: 权重分层调整
                await self._adjust_memory_layers(task['memory_ids'])
                
                # Step 14: 生成摘要和标签
                await self._generate_summaries_and_tags(task, evaluation_result)
                
                # Step 15: 建立记忆关联
                await self._establish_memory_associations(task, evaluation_result)
                
                self.logger.debug("✅ 异步评估流程完成")
                
            except asyncio.TimeoutError:
                # 队列空闲，继续等待
                continue
            except Exception as e:
                self.logger.error(f"异步评估流程错误: {e}")
    
    async def _llm_evaluate_dialogue(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        LLM评估对话重要性 (Step 11)
        
        Args:
            task: 评估任务
            
        Returns:
            Dict: 评估结果（权重、情感、主题等）
        """
        if not self.async_evaluator:
            return {'weight': 1.0, 'emotion': 'neutral', 'topic': 'general'}
        
        try:
            evaluation_context = {
                'user_input': task['user_input'],
                'ai_response': task['ai_response'],
                'context': task.get('context', {})
            }
            
            result = await self.async_evaluator.evaluate_dialogue_importance(evaluation_context)
            self.logger.debug(f"💭 LLM评估完成: 权重={result.get('weight', 1.0)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"LLM评估失败: {e}")
            return {'weight': 1.0, 'emotion': 'neutral', 'topic': 'general'}
    
    async def _update_memory_weights(self, task: Dict[str, Any], evaluation: Dict[str, Any]):
        """
        更新记忆权重 (Step 12)
        
        Args:
            task: 评估任务
            evaluation: 评估结果
        """
        try:
            memory_ids = task['memory_ids']
            new_weight = evaluation.get('weight', 1.0)
            
            # 更新用户输入记忆权重
            if memory_ids.get('user_memory_id'):
                await self.weight_manager.update_weight_async(
                    memory_ids['user_memory_id'], new_weight
                )
            
            # 更新AI回复记忆权重
            if memory_ids.get('ai_memory_id'):
                await self.weight_manager.update_weight_async(
                    memory_ids['ai_memory_id'], new_weight
                )
                
            self.logger.debug(f"⚖️ 权重更新完成: {new_weight}")
            
        except Exception as e:
            self.logger.error(f"权重更新失败: {e}")
    
    async def _adjust_memory_layers(self, memory_ids: Dict[str, Any]):
        """
        权重分层调整 (Step 13)
        
        Args:
            memory_ids: 记忆ID字典
        """
        try:
            if self.layer_manager:
                await self.layer_manager.adjust_layers_async(memory_ids)
                self.logger.debug("🏗️ 分层调整完成")
                
        except Exception as e:
            self.logger.error(f"分层调整失败: {e}")
    
    async def _generate_summaries_and_tags(self, task: Dict[str, Any], evaluation: Dict[str, Any]):
        """
        生成摘要和标签 (Step 14)
        
        Args:
            task: 评估任务
            evaluation: 评估结果
        """
        try:
            if self.summary_generator:
                summary_data = {
                    'content': f"{task['user_input']} -> {task['ai_response']}",
                    'topic': evaluation.get('topic', 'general'),
                    'emotion': evaluation.get('emotion', 'neutral')
                }
                
                await self.summary_generator.generate_async_summary(summary_data)
                self.logger.debug("📝 摘要生成完成")
                
        except Exception as e:
            self.logger.error(f"摘要生成失败: {e}")
    
    async def _establish_memory_associations(self, task: Dict[str, Any], evaluation: Dict[str, Any]):
        """
        建立记忆关联 (Step 15)
        
        Args:
            task: 评估任务
            evaluation: 评估结果
        """
        try:
            if self.association_network:
                memory_ids = task['memory_ids']
                topic = evaluation.get('topic', 'general')
                
                # 建立用户输入和AI回复之间的关联
                if memory_ids.get('user_memory_id') and memory_ids.get('ai_memory_id'):
                    await self.association_network.create_association_async(
                        memory_ids['user_memory_id'],
                        memory_ids['ai_memory_id'],
                        'dialogue_pair',
                        strength=0.9
                    )
                
                # 建立主题关联
                await self.association_network.establish_topic_associations(
                    list(memory_ids.values()), topic
                )
                
                self.logger.debug("🕸️ 关联建立完成")
                
        except Exception as e:
            self.logger.error(f"关联建立失败: {e}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            'is_running': self.is_running,
            'queue_size': self.evaluation_queue.qsize(),
            'status': 'active' if self.is_running else 'stopped'
        }