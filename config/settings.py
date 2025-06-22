# config/settings.py

# --- 语音识别模型配置 ---
# 在这里定义你想使用的 Whisper 模型在 Hugging Face 上的ID
WHISPER_MODEL_ID = "openai/whisper-large-v3-turbo"

# LLM 对话引擎配置
LLM_API_URL = "http://127.0.0.1:8080/v1/chat/completions" 
LLM_MAX_NEW_TOKENS = 1024   # 给予AI足够的发挥空间，确保回答完整
LLM_TEMPERATURE = 0.8       # 保证逻辑性的同时，带有一点自然的创造力


# 人格设定 ---
# 在这里选择你想让AI扮演的角色，只需要修改这里的名字即可
ACTIVE_PERSONA = "witty_friend" 