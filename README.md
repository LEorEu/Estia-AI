# Estia AI 智能助手

> 🤖 一个具有先进记忆系统的本地AI助手，支持语音交互、智能对话和持久化记忆

## ✨ 项目亮点

- **🧠 先进记忆系统**：基于13步工作流的智能记忆管理、上下文构建和异步评估。
- **🎙️ 全功能语音交互**：支持语音唤醒、热键触发、自动静音检测，集成Whisper实时识别和多种TTS引擎。
- **🔄 灵活的对话引擎**：支持多种LLM提供商（本地/OpenAI/DeepSeek/Gemini），可随时切换。
- **⚡ 高性能异步架构**：核心记忆处理流程采用异步设计，确保对话的流畅响应。
- **🎯 高度个性化**：可自由配置AI人格、交互模式和提示词模板。
- **🔧 统一缓存管理**：引入多级缓存系统（热缓存/温缓存），智能管理嵌入向量和记忆数据，提升性能。
- **🚀 快速启动与离线运行**：采用单例模式加载模型，优化启动时间，支持完全离线运行。

## 🚀 快速开始

### 1. 环境安装

```bash
# 克隆项目
git clone https://github.com/your-username/Estia-AI.git
cd Estia-AI

# 运行安装脚本 (会自动创建虚拟环境并安装依赖)
cd setup
install.bat

# 返回项目根目录
cd ..
```

### 2. 配置API密钥

为了保护你的密钥安全，**不推荐**直接修改 `config/settings.py`。请使用以下方法之一：

**方法一：创建 `local_settings.py` (推荐)**

1.  在 `config/` 目录下创建一个新文件 `local_settings.py`。
2.  在该文件中添加你的API密钥，例如：

    ```python
    # config/local_settings.py
    GEMINI_API_KEY = "your-gemini-api-key"
    DEEPSEEK_API_KEY = "your-deepseek-api-key"
    OPENAI_API_KEY = "your-openai-api-key"
    ```

**方法二：使用环境变量**

设置与上述变量同名的环境变量即可。

### 3. 配置模型和功能

打开 `config/settings.py` 文件，根据你的需求调整以下常用配置：

```python
# --- 选择模型提供商 ---
MODEL_PROVIDER = "gemini"  # 可选: "local", "openai", "deepseek", "gemini"

# --- AI人格设定 ---
ACTIVE_PERSONA = "witty_friend" # 在 core/prompts/dialogue_generation.py 中查看可用人格

# --- 音频控制 ---
RECORD_HOTKEY = "t"              # 录音热键
BACKGROUND_LISTENING = False     # 是否启用后台语音唤醒
WAKE_WORD = "你好Estia"        # 语音唤醒词 (仅在上一项启用时有效)
```

### 4. 启动应用

```bash
# 激活虚拟环境
activate.bat

# 使用启动脚本 (推荐)
start.bat

# 或者手动启动
python main.py --mode voice    # 语音模式 (默认)
python main.py --mode text     # 文本模式
python main.py --mode api      # API服务模式
```

**注意**：首次启动会下载必要的模型文件到本地缓存目录，后续启动将更快并支持离线运行。

## 🏗️ 系统架构

### 核心模块

```
core/
├── app.py              # 应用主控制器
├── memory/             # 记忆系统 (13步工作流)
│   ├── estia_memory.py # 记忆系统主控制器
│   ├── caching/        # 统一缓存管理
│   ├── retrieval/      # 智能检索系统
│   ├── evaluator/      # 异步记忆评估
│   ├── storage/        # 记忆存储 (数据库)
│   ├── embedding/      # 文本向量化与嵌入缓存
│   ├── ranking/        # 记忆排序与评分
│   ├── context/        # 上下文构建
│   ├── association/    # 记忆关联网络
│   └── init/           # 数据库与向量索引初始化
├── dialogue/           # 对话系统
│   ├── engine.py       # 对话引擎 (与LLM交互)
│   ├── personality.py  # AI人格设定
│   └── processing.py   # 对话处理逻辑
├── audio/              # 音频处理系统
│   ├── system.py       # 音频系统管理
│   ├── input.py        # 语音输入/唤醒/VAD
│   ├── output.py       # 语音输出 (TTS)
│   └── keyboard_control.py # 键盘热键控制
├── prompts/            # 提示词模板管理
│   ├── dialogue_generation.py # 对话生成提示词
│   └── memory_evaluation.py   # 记忆评估提示词
├── utils/              # 工具函数
│   ├── config_loader.py # 配置文件加载器
│   └── logger.py        # 日志系统
└── vision/             # 视觉处理 (开发中)
    └── game_vision.py
```

### 记忆系统工作流程

Estia的记忆系统是项目的核心，采用13步处理流程，以确保AI能够长期、准确地记忆信息。
1.  **会话管理**：自动创建和管理对话会话。
2.  **输入处理**：接收用户输入，并进行向量化（利用缓存加速）。
3.  **多策略检索**：
    *   **FAISS向量检索**：查找语义相似的记忆。
    *   **历史记忆检索**：根据上下文获取近期对话。
    *   **关联网络扩展**：通过记忆关联图谱发现潜在相关信息。
4.  **信息排序与去重**：对检索到的信息进行排序、合并和去重。
5.  **智能上下文构建**：根据信息的重要性和相关性，动态构建最适合当前对话的上下文。
6.  **对话生成**：将构建好的上下文与用户输入一起提交给LLM生成回复。
7.  **记忆存储**：将新的交互（用户输入和AI回复）存入长期记忆库。
8.  **异步记忆评估**：在后台，LLM会异步地对新存入的记忆进行评估，包括：
    *   **重要性评分** (1-10分)
    *   **内容摘要**
    *   **话题归类**
9.  **关联建立**：根据评估结果，自动在相关记忆之间建立新的关联。

## 🔧 主要配置选项

所有配置项均位于 `config/settings.py`。

| 配置项 | 类型 | 描述 |
| :--- | :--- | :--- |
| `MODEL_PROVIDER` | str | 选择使用的LLM提供商: "local", "openai", "deepseek", "gemini" |
| `ACTIVE_PERSONA` | str | 选择AI的人格，对应 `core/prompts` 中的设定 |
| `WHISPER_MODEL_ID` | str | Hugging Face上的Whisper模型ID |
| `TTS_VOICE` | str | 语音合成的音色，如 "zh-CN-XiaoyiNeural" |
| `RECORD_HOTKEY` | str | 开始录音的全局热键，如 "t" |
| `BACKGROUND_LISTENING` | bool | `True` 启用后台监听和语音唤醒, `False` 禁用 |
| `WAKE_WORD` | str | 语音唤醒的关键词 |
| `LOG_LEVEL` | str | 日志级别: "DEBUG", "INFO", "WARNING" |

**高级配置**：
- **LLM Endpoints**: `LLM_API_URL`, `OPENAI_API_BASE`, `DEEPSEEK_API_BASE`, `GEMINI_API_BASE` 等。
- **本地模型参数**: `LLM_MAX_NEW_TOKENS`, `LLM_TEMPERATURE`。
- **音频参数**: `RECORD_MAX_DURATION`, `RECORD_AUTO_STOP_SILENCE` 等。

## 🧪 开发与测试

### 运行测试

项目包含丰富的测试用例，覆盖核心功能模块。
```bash
# 激活环境
activate.bat

# 运行一个测试 (示例)
python tests/test_memory_pipeline.py
python tests/test_async_evaluator.py
python tests/test_complete_workflow.py
```

### 常用开发脚本

`scripts/` 目录下提供了一些有用的开发和维护脚本。
```bash
# 检查环境配置是否正确
python setup/check_env.py

# 修复或初始化数据库表结构
python scripts/fix_database_schema.py

# 从头构建向量索引 (耗时较长)
python scripts/build_index.py
```

## 📈 项目状态

### 已实现功能
- ✅ 完整的13步记忆处理工作流
- ✅ 统一的多级缓存系统
- ✅ 智能检索和动态上下文构建
- ✅ 后台异步记忆评估与关联系统
- ✅ 多LLM提供商支持和运行时切换
- ✅ 支持语音唤醒和热键的语音交互
- ✅ 高度模块化的架构和清晰的代码分层

### 未来计划
- [ ] **视觉能力集成**：接入视觉模型，实现对游戏画面的理解。
- [ ] **Web UI界面**：提供一个Web界面用于更方便的交互和记忆管理。
- [ ] **记忆编辑与管理**：允许用户手动修改、删除或标注记忆。
- [ ] **更强的知识图谱能力**：深化记忆关联网络，构建更复杂的知识结构。

## 协议

本项目采用 MIT 协议。