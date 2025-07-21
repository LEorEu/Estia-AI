#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步流程管理器 (AsyncFlowManager)
负责Step 10-15: 异步评估、权重更新、关联建立
职责：后台评估，不影响用户体验的异步操作
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from ...shared.internal import handle_memory_errors, ErrorHandlerMixin

# 导入迁移的核心模块
from .tools.memory_search_tools import MemorySearchManager
from .evaluator.async_evaluator import AsyncMemoryEvaluator
from .weight_management import WeightManager

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
        self.db_manager = components.get('db_manager')
        self.association_network = components.get('association_network')
        
        # 🔥 初始化迁移的核心模块
        self.memory_search_manager = None
        self.async_evaluator = None
        self.weight_manager = None
        
        if self.db_manager:
            # 初始化LLM搜索工具管理器
            self.memory_search_manager = MemorySearchManager(
                self.db_manager, 
                self.association_network
            )
            
            # 初始化异步评估器
            self.async_evaluator = AsyncMemoryEvaluator(self.db_manager)
            
            # 初始化权重管理器
            self.weight_manager = WeightManager(self.db_manager)
            
            # 🔥 启动异步评估器
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环已经运行，直接启动
                    asyncio.create_task(self.async_evaluator.start())
                else:
                    # 如果事件循环还没运行，标记为需要启动
                    self._need_start_evaluator = True
            except RuntimeError:
                # 没有事件循环，标记为需要启动
                self._need_start_evaluator = True
                
        else:
            self._need_start_evaluator = False
        
        # 传统组件（保持兼容性）
        self.layer_manager = components.get('layer_manager')
        self.summary_generator = components.get('summary_generator')
        
        self.evaluation_queue = asyncio.Queue()
        self.is_running = False
        self.logger = logger
    
    async def start_async_processing(self):
        """启动异步处理循环"""
        self.is_running = True
        self.logger.info("🔄 启动异步流程管理器")
        
        # 🔥 启动异步评估器（如果还没启动）
        if self.async_evaluator and getattr(self, '_need_start_evaluator', False):
            await self.async_evaluator.start()
            self._need_start_evaluator = False
            self.logger.info("✅ 异步评估器已启动")
        
        # 启动异步处理任务
        asyncio.create_task(self._process_evaluation_queue())
    
    async def stop_async_processing(self):
        """停止异步处理"""
        self.is_running = False
        self.logger.info("⏹️ 停止异步流程管理器")
        
        # 🔥 停止异步评估器
        if self.async_evaluator:
            await self.async_evaluator.stop()
            self.logger.info("✅ 异步评估器已停止")
    
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
            # 🔥 使用异步评估器的完整评估功能
            dialogue_data = {
                'user_input': task['user_input'],
                'ai_response': task['ai_response'],
                'session_id': task.get('context', {}).get('session_id'),
                'context_memories': task.get('context', {}).get('context_memories', []),
                'timestamp': task.get('timestamp', time.time())
            }
            
            # 直接调用内部评估方法
            evaluation_result = await self.async_evaluator._evaluate_dialogue(dialogue_data)
            
            if evaluation_result:
                self.logger.debug(f"💭 LLM评估完成: 权重={evaluation_result.get('weight', 1.0)}")
                return evaluation_result
            else:
                # 如果LLM评估失败，使用估算方法
                estimated_weight = self._estimate_dialogue_weight(task)
                result = {
                    'weight': estimated_weight,
                    'emotion': 'neutral',
                    'topic': 'general',
                    'super_group': 'dialogue'
                }
                self.logger.debug(f"💭 使用估算权重: {estimated_weight}")
                return result
            
        except Exception as e:
            self.logger.error(f"LLM评估失败: {e}")
            # 回退到估算方法
            estimated_weight = self._estimate_dialogue_weight(task)
            return {
                'weight': estimated_weight,
                'emotion': 'neutral',
                'topic': 'general',
                'super_group': 'dialogue'
            }
    
    async def _update_memory_weights(self, task: Dict[str, Any], evaluation: Dict[str, Any]):
        """
        更新记忆权重 (Step 12)
        
        Args:
            task: 评估任务
            evaluation: 评估结果
        """
        try:
            if not self.weight_manager:
                self.logger.warning("权重管理器未初始化")
                return
                
            memory_ids = task['memory_ids']
            new_weight = evaluation.get('weight', 1.0)
            
            # 🔥 使用正确的权重管理器方法
            context = {
                'change_reason': 'async_evaluation',
                'evaluation_result': evaluation
            }
            
            # 更新用户输入记忆权重
            if memory_ids.get('user_memory_id'):
                result = self.weight_manager.update_memory_weight_dynamically(
                    memory_ids['user_memory_id'], context
                )
                if result.get('success'):
                    self.logger.debug(f"用户记忆权重更新: {result.get('message')}")
            
            # 更新AI回复记忆权重
            if memory_ids.get('ai_memory_id'):
                result = self.weight_manager.update_memory_weight_dynamically(
                    memory_ids['ai_memory_id'], context
                )
                if result.get('success'):
                    self.logger.debug(f"AI记忆权重更新: {result.get('message')}")
                
            self.logger.debug(f"⚖️ 权重更新完成: {new_weight}")
            
        except Exception as e:
            self.logger.error(f"权重更新失败: {e}")
    
    def _estimate_dialogue_weight(self, task: Dict[str, Any]) -> float:
        """
        估算对话权重（简化版本）
        
        Args:
            task: 评估任务
            
        Returns:
            float: 估算的权重值
        """
        try:
            user_input = task.get('user_input', '')
            ai_response = task.get('ai_response', '')
            
            base_weight = 1.0
            
            # 基于长度的权重调整
            total_length = len(user_input) + len(ai_response)
            if total_length > 200:
                base_weight += 0.5
            if total_length > 500:
                base_weight += 0.5
                
            # 基于关键词的权重调整
            important_keywords = ['重要', '记住', '提醒', '喜欢', '不喜欢', '偏好']
            for keyword in important_keywords:
                if keyword in user_input or keyword in ai_response:
                    base_weight += 0.3
                    break
            
            # 基于问号数量（表示交互性）
            question_count = user_input.count('?') + user_input.count('？')
            if question_count > 0:
                base_weight += min(question_count * 0.2, 0.6)
            
            # 确保权重在合理范围内
            return max(0.5, min(base_weight, 5.0))
            
        except Exception as e:
            self.logger.error(f"权重估算失败: {e}")
            return 1.0
    
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
                    # 使用同步方法，因为旧系统的关联网络是同步的
                    self.association_network.create_association(
                        memory_ids['user_memory_id'],
                        memory_ids['ai_memory_id'],
                        strength=0.9
                    )
                
                # 建立主题关联（基于同样的内容创建关联）
                user_memory_id = memory_ids.get('user_memory_id')
                ai_memory_id = memory_ids.get('ai_memory_id')
                
                if user_memory_id and ai_memory_id:
                    # 获取记忆内容，用于自动关联
                    memory_content = {
                        'user_input': task['user_input'],
                        'ai_response': task['ai_response'],
                        'topic': topic,
                        'emotion': evaluation.get('emotion', 'neutral')
                    }
                    
                    # 为用户记忆创建自动关联
                    self.association_network.auto_create_associations(
                        user_memory_id, memory_content, max_associations=5
                    )
                    
                    # 为AI记忆创建自动关联
                    self.association_network.auto_create_associations(
                        ai_memory_id, memory_content, max_associations=5
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
    
    # 🔥 LLM搜索工具集成
    def get_memory_search_tools(self) -> List[Dict[str, Any]]:
        """
        获取LLM可用的记忆搜索工具定义
        供LLM主动查询记忆使用
        
        Returns:
            List: 工具定义列表
        """
        if not self.memory_search_manager:
            return []
        
        return self.memory_search_manager.get_memory_search_tools()
    
    def execute_memory_search_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行记忆搜索工具（供LLM调用）
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            Dict: 搜索结果
        """
        if not self.memory_search_manager:
            return {
                'success': False,
                'message': '记忆搜索管理器未初始化',
                'memories': []
            }
        
        try:
            result = self.memory_search_manager.execute_memory_search_tool(tool_name, parameters)
            self.logger.debug(f"🔍 LLM搜索工具执行: {tool_name} - 找到 {len(result.get('memories', []))} 条记忆")
            return result
            
        except Exception as e:
            self.logger.error(f"LLM搜索工具执行失败: {e}")
            return {
                'success': False,
                'message': f'工具执行失败: {str(e)}',
                'memories': []
            }