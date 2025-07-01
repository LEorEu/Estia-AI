# config/settings.py

import os

# --- 语音识别模型配置 ---
# 在这里定义你想使用的 Whisper 模型在 Hugging Face 上的ID
WHISPER_MODEL_ID = "openai/whisper-large-v3-turbo"

# LLM 对话引擎配置
# 模型提供商选择: "local", "openai", "deepseek", "gemini"
MODEL_PROVIDER = "gemini"

# 本地模型配置
LLM_API_URL = "http://127.0.0.1:8080/v1/chat/completions" 
LLM_MODEL = "local-model"  # 本地模型标识符，用于log
LLM_MAX_NEW_TOKENS = 4096   # 给予AI足够的发挥空间，确保回答完整
LLM_TEMPERATURE = 0.8       # 保证逻辑性的同时，带有一点自然的创造力

# API密钥配置 - 从本地配置文件或环境变量加载
def load_api_keys():
    """加载API密钥，优先级：环境变量 > 本地配置文件 > 默认空值"""
    keys = {
        'OPENAI_API_KEY': '',
        'DEEPSEEK_API_KEY': '',
        'GEMINI_API_KEY': ''
    }
    
    # 1. 尝试从环境变量加载
    for key in keys:
        env_value = os.getenv(key)
        if env_value:
            keys[key] = env_value
    
    # 2. 尝试从本地配置文件加载
    try:
        from . import local_settings
        for key in keys:
            if hasattr(local_settings, key) and getattr(local_settings, key):
                keys[key] = getattr(local_settings, key)
    except ImportError:
        # local_settings.py不存在，跳过
        pass
    
    return keys

# 加载API密钥
_api_keys = load_api_keys()

# OpenAI API 配置
OPENAI_API_KEY = _api_keys['OPENAI_API_KEY']
OPENAI_API_BASE = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-3.5-turbo"  # 可选: gpt-3.5-turbo, gpt-4, 等

# DeepSeek API 配置
DEEPSEEK_API_KEY = _api_keys['DEEPSEEK_API_KEY']
DEEPSEEK_API_BASE = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"  # 可根据实际可用模型调整

# Gemini API 配置
GEMINI_API_KEY = _api_keys['GEMINI_API_KEY']
GEMINI_API_BASE = "https://gemini.estia.moe"
GEMINI_MODEL = "gemini-2.5-pro"  # 使用官方支持的模型名称

# 日志配置
LOG_DIR = "./logs"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 人格设定 ---
# 在这里选择你想让AI扮演的角色，只需要修改这里的名字即可
ACTIVE_PERSONA = "witty_friend" 

# --- 音频控制设置 ---
# 录音热键设置 (使用键码名称，如F1-F12, a-z, 0-9等)
RECORD_HOTKEY = "t"         # 按下开始录音的热键
RECORD_MAX_DURATION = 60     # 最大录音时长(秒)
RECORD_AUTO_STOP_SILENCE = 2 # 检测到静音多少秒后自动停止录音 (0表示禁用此功能)

# 后台监听设置
WAKE_WORD = "你好Estia"   # 唤醒词
BACKGROUND_LISTENING = False # 是否启用后台监听
VOICE_ACTIVITY_THRESHOLD = 0.3 # 语音活动检测阈值 (0-1), 越低越敏感

# 音频输出设置
TTS_VOICE = "zh-CN-XiaoyiNeural"  # 语音合成声音
AUDIO_OUTPUT_VOLUME = 1.0   # 音量 (0-1) 