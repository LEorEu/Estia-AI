# config/settings.py

import os

# --- 语音识别模型配置 ---
# 在这里定义你想使用的 Whisper 模型在 Hugging Face 上的ID
WHISPER_MODEL_ID = "openai/whisper-large-v3-turbo"

# LLM 对话引擎配置
# 模型提供商选择: "local", "openai", "deepseek", "gemini"
MODEL_PROVIDER = "deepseek"

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
ACTIVE_PERSONA = "estia" 

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

# --- 记忆系统上下文长度配置 ---
# 总上下文长度限制（字符数）
MEMORY_CONTEXT_MAX_LENGTH = 16000

# 各部分的长度分配（字符数）
MEMORY_CONTEXT_LIMITS = {
    # 当前会话对话（最高优先级）
    "current_session": {
        "max_dialogues": 5,        # 增加到5轮对话
        "max_chars_per_dialogue": 300,  # 增加到300字符
        "priority": 1
    },
    
    # 核心记忆（高权重记忆）
    "core_memories": {
        "max_count": 5,            # 增加到5条核心记忆
        "max_chars_per_memory": 250,   # 增加到250字符
        "min_weight": 8.0,         # 最小权重阈值
        "priority": 2
    },
    
    # 相关历史对话（语义相关）
    "historical_dialogues": {
        "max_sessions": 3,         # 增加到3个历史会话
        "max_dialogues_per_session": 3,  # 增加到3轮对话
        "max_chars_per_dialogue": 250,   # 增加到250字符
        "priority": 3
    },
    
    # 相关记忆（中等权重）
    "relevant_memories": {
        "max_count": 8,            # 增加到8条相关记忆
        "max_chars_per_memory": 200,    # 增加到200字符
        "min_weight": 5.0,         # 最小权重阈值
        "priority": 4
    },
    
    # 重要总结
    "summaries": {
        "max_count": 5,            # 增加到5条总结
        "max_chars_per_summary": 150,   # 增加到150字符
        "priority": 5
    },
    
    # 系统角色设定（固定）
    "role_setting": {
        "max_chars": 300,          # 增加到300字符
        "priority": 0              # 最高优先级，总是包含
    }
}

# 上下文长度自适应配置
MEMORY_CONTEXT_ADAPTIVE = {
    "enabled": True,               # 是否启用自适应长度
    "min_length": 2000,           # 最小长度
    "max_length": 8000,           # 最大长度（以balanced模式为准）
    "target_length": 6000,        # 目标长度
    "compression_ratio": 0.8      # 压缩比例（当超出长度时）
}

# 不同场景的预设配置
MEMORY_CONTEXT_PRESETS = {
    "compact": {                   # 紧凑模式（快速响应）
        "max_length": 4000,
        "current_session": {"max_dialogues": 3, "max_chars_per_dialogue": 200},
        "core_memories": {"max_count": 3, "max_chars_per_memory": 150},
        "historical_dialogues": {"max_sessions": 2, "max_dialogues_per_session": 2, "max_chars_per_dialogue": 180},
        "relevant_memories": {"max_count": 5, "max_chars_per_memory": 120},
        "summaries": {"max_count": 3, "max_chars_per_summary": 100}
    },
    
    "balanced": {                  # 平衡模式（默认）
        "max_length": 8000,
        "current_session": {"max_dialogues": 5, "max_chars_per_dialogue": 300},
        "core_memories": {"max_count": 5, "max_chars_per_memory": 250},
        "historical_dialogues": {"max_sessions": 3, "max_dialogues_per_session": 3, "max_chars_per_dialogue": 250},
        "relevant_memories": {"max_count": 8, "max_chars_per_memory": 200},
        "summaries": {"max_count": 5, "max_chars_per_summary": 150}
    },
    
    "detailed": {                  # 详细模式（深度对话）
        "max_length": 16000,
        "current_session": {"max_dialogues": 8, "max_chars_per_dialogue": 400},
        "core_memories": {"max_count": 8, "max_chars_per_memory": 300},
        "historical_dialogues": {"max_sessions": 4, "max_dialogues_per_session": 4, "max_chars_per_dialogue": 300},
        "relevant_memories": {"max_count": 12, "max_chars_per_memory": 250},
        "summaries": {"max_count": 8, "max_chars_per_summary": 200}
    }
}

# 当前使用的预设
MEMORY_CONTEXT_PRESET = "balanced"  # 可选: "compact", "balanced", "detailed" 

# --- 流式输出配置 ---
# 流式输出功能开关
ENABLE_STREAM_OUTPUT = True          # 是否启用流式输出
ENABLE_TEXT_STREAM = True            # 是否启用文本流式输出
ENABLE_AUDIO_STREAM = True           # 是否启用语音流式输出

# 流式输出参数
STREAM_CHUNK_SIZE = 50               # 文本分段大小（字符数）
STREAM_DELAY = 0.1                  # 流式输出延迟（秒）
STREAM_AUDIO_SEGMENT_SIZE = 50      # 音频分段大小（字符数）

# 流式输出触发条件
STREAM_AUDIO_TRIGGERS = [           # 触发音频生成的标点符号
    '。', '！', '？', '.', '!', '?'
]

# 流式输出模式
STREAM_MODE = "both"                # 可选: "text_only", "audio_only", "both"
STREAM_PRIORITY = "text_first"      # 可选: "text_first", "audio_first", "parallel"

# --- 上下文管理器默认配置 ---
# 当配置文件中没有对应值时使用的默认值
MEMORY_CONTEXT_DEFAULT_LIMITS = {
    "current_session": {
        "max_dialogues": 3,
        "max_chars_per_dialogue": 200
    },
    "core_memories": {
        "max_count": 3,
        "max_chars_per_memory": 150,
        "min_weight": 7.0
    },
    "historical_dialogues": {
        "max_sessions": 2,
        "max_dialogues_per_session": 2,
        "max_chars_per_dialogue": 180
    },
    "relevant_memories": {
        "max_count": 5,
        "max_chars_per_memory": 120,
        "min_weight": 4.0
    },
    "summaries": {
        "max_count": 3,
        "max_chars_per_summary": 100
    },
    "role_setting": {
        "max_chars": 200
    }
}

# 自适应调整默认配置
MEMORY_CONTEXT_DEFAULT_ADAPTIVE = {
    "max_length": 3000,
    "target_length": 2500,
    "compression_ratio": 0.8
}