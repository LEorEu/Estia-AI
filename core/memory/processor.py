"""
记忆处理模块 - 负责处理和存储对话记忆
"""

import asyncio
import time
from datetime import datetime
from ..intent_parser import evaluate_conversation_weight, determine_memory_layer, evaluate_memory_layer_with_llm

async def process_and_store_memory(user_text, ai_text, chat_history, memory_manager):
    """异步处理并存储对话记忆到分层记忆系统"""
    # 评估对话重要性权重
    weight = evaluate_conversation_weight(user_text, ai_text, chat_history)
    
    # 根据权重和内容确定应该存储在哪个记忆层级
    memory_layer = determine_memory_layer(user_text, ai_text, weight)
    
    # 也可以选择使用LLM判断记忆层级（可选，取消注释启用）
    # memory_layer = evaluate_memory_layer_with_llm(user_text, ai_text, chat_history)
    
    # 准备用户对话记忆
    user_memory = {
        "role": "user",
        "content": user_text,
        "timestamp": time.time(),
        "weight": weight
    }
    
    # 准备AI回复记忆
    ai_memory = {
        "role": "assistant",
        "content": ai_text,
        "timestamp": time.time(),
        "weight": weight
    }
    
    # 存储到相应的记忆层级
    memory_manager.add_memory(user_memory, level=memory_layer)
    memory_manager.add_memory(ai_memory, level=memory_layer)
    
    print(f"✅ 对话已存储到{memory_layer}记忆层，权重为{weight}")
    
    # 如果是一个新的对话日，可以触发记忆巩固和清理
    current_day = datetime.now().day
    last_memory_day = getattr(process_and_store_memory, "last_day", None)
    if last_memory_day is None or current_day != last_memory_day:
        process_and_store_memory.last_day = current_day
        # 执行记忆巩固（短期→长期）和清理任务
        memory_manager.consolidate_memories()
        print("✨ 已执行每日记忆巩固和清理") 