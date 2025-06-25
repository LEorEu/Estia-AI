# core/dialogue_engine.py

"""
本模块是 AI 的"思考"核心。（V2.0 - OpenAI API 兼容版）
它负责接收用户的文本输入，将其打包成 OpenAI 兼容的格式，
发送给本地运行的、轻量级的 llama.cpp 服务器，并解析返回的回复。
"""

# -----------------------------------------------------------------------------
# 导入必要的库
# -----------------------------------------------------------------------------

import requests                 # 导入 requests 库，用于发送 HTTP API 请求。
import json                     # 导入 json 库，用于处理 JSON 数据格式。
from config import settings     # 从我们的配置文件中导入 settings。
import time                     # 导入 time 库，用于格式化时间戳。
import os
import openai


# -----------------------------------------------------------------------------
# 功能函数定义
# -----------------------------------------------------------------------------

def get_llm_response(prompt, history=None, personality=""):
    """
    使用大语言模型生成回复
    
    参数:
        prompt: 提示文本
        history: 历史对话 (可选)
        personality: 人格设定 (可选)
    
    返回:
        模型生成的回复
    """
    if history is None:
        history = []
    
    # 构建消息数组
    messages = []
    
    # 添加人格设定 (如果有)
    if personality:
        messages.append({
            "role": "system",
            "content": personality
        })
    
    # 添加历史对话
    for entry in history:
        messages.append({
            "role": entry.get("role", "user"),
            "content": entry.get("content", "")
        })
    
    # 添加当前提示
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    # 请求LLM
    try:
        # 加载API设置
        openai.api_key = settings.OPENAI_API_KEY
        
        # 配置超时
        timeout = 60  # 60秒超时
        
        # 调用API
        if settings.MODEL_PROVIDER.lower() == "azure":
            openai.api_type = "azure"
            openai.api_base = settings.AZURE_ENDPOINT
            openai.api_version = settings.AZURE_API_VERSION
            
            response = openai.ChatCompletion.create(
                engine=settings.LLM_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                timeout=timeout
            )
        else:
            # 使用OpenAI API
            response = openai.ChatCompletion.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                timeout=timeout
            )
        
        # 提取回复文本
        reply = response.choices[0].message.content.strip()
        return reply
        
    except Exception as e:
        print(f"LLM调用失败: {e}")
        return "抱歉，我现在无法完成这个请求。"

def generate_response(user_query, memory_context, personality=""):
    """
    生成回复，考虑记忆上下文和人格
    
    参数:
        user_query: 用户查询
        memory_context: 相关记忆上下文
        personality: 人格设定
    
    返回:
        生成的回复
    """
    # 构建完整提示
    full_prompt = f"""请基于以下信息回答用户的问题或请求。

{memory_context if memory_context else "没有找到相关记忆。"}

用户请求: {user_query}

请注意:
1. 如果记忆中包含矛盾信息，请优先考虑标记为最新的信息
2. 回答时考虑关联记忆提供的额外上下文
3. 如果看到记忆摘要，可以利用其提供的整合信息
4. 保持简洁自然的对话风格

请基于上述信息给出回复:"""

    # 调用LLM生成回复
    response = get_llm_response(full_prompt, [], personality)
    return response

def retrieve_memories(query, limit=5, memory_manager=None):
    """
    从记忆管理器中检索相关记忆
    
    参数:
        query: 查询文本
        limit: 最大返回数量
        memory_manager: 记忆管理器实例
    
    返回:
        格式化的记忆文本
    """
    if not memory_manager:
        return "没有可用的记忆。"
    
    try:
        # 从记忆管理器检索记忆
        results = memory_manager.retrieve_memory(
            query, 
            limit=limit,
            parallel=True,
            include_associations=True,
            check_conflicts=True
        )
        
        if not results:
            return "没有找到相关记忆。"
        
        # 格式化记忆
        formatted_memories = []
        
        for memory in results:
            role = memory.get("role", "system")
            content = memory.get("content", "")
            timestamp = memory.get("timestamp", "")
            
            # 格式化时间
            if isinstance(timestamp, (int, float)):
                import datetime
                timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
            
            # 处理特殊标记
            prefix = ""
            if memory.get("is_associated", False):
                prefix = "[关联记忆] "
            elif memory.get("is_summary", False):
                prefix = "[记忆摘要] "
            elif memory.get("status") == "superseded":
                prefix = "[已更新的信息] "
            
            # 添加上下文信息
            context = ""
            if "context" in memory:
                context = f" (备注: {memory['context']})"
            
            formatted_memories.append(f"{prefix}[{timestamp}] {role}: {content}{context}")
        
        # 添加一个简短的介绍
        header = "系统记忆:"
        formatted_text = header + "\n" + "\n".join(formatted_memories)
        
        return formatted_text
        
    except Exception as e:
        print(f"记忆检索失败: {e}")
        return "记忆检索过程中出现错误。"