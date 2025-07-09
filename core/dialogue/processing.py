"""
对话异步处理模块 - 负责对话的异步评分、总结和存储
"""

import threading
import time
import logging
from typing import List, Dict, Any, Optional

# 设置日志
logger = logging.getLogger("estia.dialogue.processing")

class AsyncProcessor:
    """
    对话异步处理器
    负责在后台处理对话评分、总结和存储等任务
    """
    
    def __init__(self, memory_system=None, database=None):
        """
        初始化异步处理器
        
        参数:
            memory_system: 记忆系统实例
            database: 数据库实例
        """
        self.memory_system = memory_system
        self.database = database
        self.logger = logger
        
        # 线程池
        self.active_threads = []
        self.max_threads = 3
    
    def process_async(self, user_input: str, ai_response: str, chat_history: List[Dict[str, Any]]):
        """
        异步处理对话
        
        参数:
            user_input: 用户输入
            ai_response: AI回复
            chat_history: 对话历史
        """
        # 清理已完成的线程
        self._clean_threads()
        
        # 如果线程数已达上限，则同步处理
        if len(self.active_threads) >= self.max_threads:
            self.logger.info("线程池已满，同步处理对话")
            self._process_dialogue(user_input, ai_response, chat_history)
            return
        
        # 创建新线程进行异步处理
        thread = threading.Thread(
            target=self._process_dialogue,
            args=(user_input, ai_response, chat_history),
            daemon=True
        )
        thread.start()
        self.active_threads.append(thread)
        self.logger.info(f"启动异步处理线程，当前活跃线程数: {len(self.active_threads)}")
    
    def _clean_threads(self):
        """清理已完成的线程"""
        self.active_threads = [t for t in self.active_threads if t.is_alive()]
    
    def _process_dialogue(self, user_input: str, ai_response: str, chat_history: List[Dict[str, Any]]):
        """
        处理对话的核心逻辑
        
        参数:
            user_input: 用户输入
            ai_response: AI回复
            chat_history: 对话历史
        """
        try:
            # 1. 评估对话重要性
            weight = self._evaluate_importance(user_input, ai_response, chat_history)
            
            # 2. 生成对话总结
            summary = self._generate_summary(user_input, ai_response, chat_history)
            
            # 3. 存储到数据库
            self._store_to_database(user_input, ai_response, weight, summary)
            
            # 4. 更新记忆系统中的权重
            self._update_memory_weights(user_input, ai_response, weight)
            
            self.logger.info("对话异步处理完成")
            
        except Exception as e:
            self.logger.error(f"对话处理失败: {e}")
    
    def _evaluate_importance(self, user_input: str, ai_response: str, chat_history: List[Dict[str, Any]]) -> float:
        """评估对话重要性，返回权重分数"""
        try:
            # 这里可以使用LLM或规则系统评估重要性
            # 简单实现：基于关键词和长度的启发式评分
            
            # 重要性基础分
            base_score = 5.0
            
            # 长度因子
            length_factor = min(len(user_input) / 100, 2.0)
            
            # 关键词检查
            important_keywords = ["记住", "重要", "不要忘记", "牢记", "请记住"]
            keyword_score = 0.0
            for keyword in important_keywords:
                if keyword in user_input.lower():
                    keyword_score += 1.0
            
            # 计算最终权重
            weight = base_score + length_factor + keyword_score
            weight = max(1.0, min(10.0, weight))  # 限制在1-10范围内
            
            self.logger.info(f"对话重要性评分: {weight}")
            return weight
            
        except Exception as e:
            self.logger.error(f"评估重要性失败: {e}")
            return 5.0  # 默认中等重要性
    
    def _generate_summary(self, user_input: str, ai_response: str, chat_history: List[Dict[str, Any]]) -> str:
        """生成对话总结"""
        try:
            # 这里应该使用LLM生成总结
            # 简单实现：截取用户输入的前部分作为总结
            max_length = 100
            if len(user_input) > max_length:
                summary = user_input[:max_length] + "..."
            else:
                summary = user_input
                
            return f"对话摘要: {summary}"
            
        except Exception as e:
            self.logger.error(f"生成总结失败: {e}")
            return "对话摘要生成失败"
    
    def _store_to_database(self, user_input: str, ai_response: str, weight: float, summary: str):
        """存储对话到数据库"""
        if not self.database:
            self.logger.warning("数据库未连接，跳过存储")
            return
            
        try:
            # 存储用户输入
            user_id = self.database.add_memory(
                content=user_input,
                role="user",
                weight=weight,
                timestamp=time.time()
            )
            
            # 存储AI回复
            ai_id = self.database.add_memory(
                content=ai_response,
                role="assistant",
                weight=weight,
                timestamp=time.time()
            )
            
            # 存储总结
            summary_id = self.database.add_memory(
                content=summary,
                role="summary",
                weight=weight + 1,  # 总结略微提高权重
                timestamp=time.time()
            )
            
            # 关联这三条记录
            if hasattr(self.database, 'create_association'):
                self.database.create_association(user_id, ai_id, "dialogue_pair")
                self.database.create_association(user_id, summary_id, "summarized_by")
                self.database.create_association(ai_id, summary_id, "summarized_by")
            
            self.logger.info(f"对话已存储到数据库，ID: {user_id}, {ai_id}, {summary_id}")
            
        except Exception as e:
            self.logger.error(f"存储到数据库失败: {e}")
    
    def _update_memory_weights(self, user_input: str, ai_response: str, weight: float):
        """更新记忆系统中的权重"""
        if not self.memory_system:
            self.logger.warning("记忆系统未连接，跳过更新权重")
            return
            
        try:
            # 这里需要实现记忆系统中的权重更新逻辑
            # 由于我们没有直接的引用，这部分可能需要后续完善
            pass
            
        except Exception as e:
            self.logger.error(f"更新记忆权重失败: {e}")
