# core/dialogue_engine.py

"""
本模块是 AI 的“思考”核心。（V2.0 - OpenAI API 兼容版）
它负责接收用户的文本输入，将其打包成 OpenAI 兼容的格式，
发送给本地运行的、轻量级的 llama.cpp 服务器，并解析返回的回复。
"""

# -----------------------------------------------------------------------------
# 导入必要的库
# -----------------------------------------------------------------------------

import requests                 # 导入 requests 库，用于发送 HTTP API 请求。
import json                     # 导入 json 库，用于处理 JSON 数据格式。
from config import settings     # 从我们的配置文件中导入 settings。


# -----------------------------------------------------------------------------
# 功能函数定义
# -----------------------------------------------------------------------------

def get_llm_response(user_prompt: str, chat_history: list, retrieved_memories: list, personality: str) -> str:

    # 格式化检索到的长期记忆，作为“背景资料”提供给LLM
    context_header = "--- 以下是你可能会用到的、从你的长期记忆中提取的相关信息，请参考这些信息来更好地回答当前问题 ---"
    formatted_memories = "\n".join([f"- [历史对话于 {mem['timestamp']}] {mem['role']}: {mem['content']}" for mem in retrieved_memories])

    # 只有在找到了相关记忆时，才构建这段背景资料
    if retrieved_memories:
        memory_context = f"{context_header}\n{formatted_memories}\n--- 背景资料结束 ---"
    else:
        memory_context = ""

    # 构建最终的消息列表
    messages = [{"role": "system", "content": personality}]

    # 如果有背景资料，就作为一条额外的系统信息插入
    if memory_context:
        messages.append({"role": "system", "name": "memory", "content": memory_context})

    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_prompt})
    
    """
    向本地的 llama.cpp 服务器 (OpenAI 兼容 API) 发送请求并获取回复。

    参数:
        user_prompt (str): 从语音识别模块传来的、用户的提问文本。
        personality (str): AI 的系统级人格设定，可以动态传入。

    返回:
        str: LLM 生成的回复文本。如果出错则返回一条错误信息。
    """
    # 打印提示，表示“大脑”正在思考
    print("🧠 LLM 正在思考中...")

    # --- API 请求的头部信息 ---
    # 指定我们发送的数据是 JSON 格式
    headers = {
        "Content-Type": "application/json"
    }

    # 先构建一个包含系统人格设定的基础消息列表
    messages = [
        {"role": "system", "content": personality}
    ]
    # 使用 .extend() 方法，把“记忆笔记本”（chat_history）里的所有历史对话都加进来
    messages.extend(chat_history)

    # 最后，再把用户这一轮的新问题加到末尾
    messages.append({"role": "user", "content": user_prompt})

    # 构建符合 OpenAI API 格式的“载荷”(payload)
    payload = {
        "model": "Mistral-Small-3.1-24B-Instruct-2503-Q4_K_M.gguf",  # 这里的模型名可以随便写，因为服务器只加载了一个模型。
        "messages": messages, # <- 使用我们构建的、包含历史的完整消息列表
        "temperature": settings.LLM_TEMPERATURE,    # 从配置文件读取“温度”参数
        "max_tokens": settings.LLM_MAX_NEW_TOKENS   # 从配置文件读取“最大生成长度”参数
    }

    try:
        # 使用 requests.post() 方法向我们新的 API URL 发送请求
        # 注意：URL 是从 settings 文件中读取的，请确保你已经把它改成了 http://127.0.0.1:8080/v1/chat/completions
        response = requests.post(settings.LLM_API_URL, headers=headers, json=payload)

        # 检查服务器的返回状态码，200 代表成功
        if response.status_code == 200:
            # 解析返回的 JSON 数据
            result = response.json()
            
            # --- 解析 OpenAI 格式的回复 ---
            # 提取出我们需要的、由AI生成的文本
            # 新的格式下，回复文本在 'choices' 列表的第一个元素的 'message' 字典的 'content' 键中
            ai_response = result['choices'][0]['message']['content']

            # 打印 AI 的原始回复，方便调试
            print(f"🤖 AI 原始回复: {ai_response}")
            
            # 返回最终的回复文本
            return ai_response
        else:
            # 如果服务器返回了错误状态码，打印详细错误信息
            print(f"❌ LLM API 返回错误，状态码: {response.status_code}, 内容: {response.text}")
            return "抱歉，我的大脑好像出了一点小问题。"

    except requests.exceptions.RequestException as e:
        # 如果在发送请求时发生了网络错误（例如 llama.cpp 服务器没打开）
        print(f"❌ 无法连接到 LLM API: {e}")
        return "抱歉，我暂时无法连接到我的大脑，请检查服务是否已启动。"