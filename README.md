# Estia AI 智能助手

> 🤖 一个具有先进记忆系统的本地AI助手，支持语音交互、智能对话和持久化记忆

## ✨ 项目亮点

- **🧠 先进记忆系统**：13步记忆处理工作流，智能记忆管理和上下文构建
- **🎙️ 语音交互**：基于Whisper的语音识别和TTS语音合成
- **🔄 智能对话**：支持多种LLM提供商（本地/OpenAI/DeepSeek/Gemini）
- **⚡ 异步处理**：后台异步记忆评估，不影响对话流畅性
- **🎯 个性化**：可配置的AI人格和交互模式
- **🔧 模块化设计**：清晰的架构分层，易于扩展和维护

## 🚀 快速开始

### 1. 环境安装

```bash
# 克隆项目
git clone https://github.com/your-username/estia-ai.git
cd estia-ai

# 运行安装脚本
cd setup
install.bat

# 返回项目根目录
cd ..
```

### 2. 配置设置

编辑 `config/settings.py` 配置你的API密钥：

```python
# 选择模型提供商
MODEL_PROVIDER = "deepseek"  # 可选: "local", "openai", "deepseek", "gemini"

# 配置对应的API密钥
DEEPSEEK_API_KEY = "your-api-key-here"
```

### 3. 启动应用

```bash
# 使用启动脚本（推荐）
start.bat

# 或者手动启动
python main.py --mode voice    # 语音模式
python main.py --mode text     # 文本模式
```

## 🏗️ 系统架构

### 核心模块

```
estia/
├── core/                    # 核心功能模块
│   ├── app.py              # 应用主控制器
│   ├── memory/             # 记忆系统
│   │   ├── pipeline.py     # 记忆处理主管道
│   │   ├── init/           # 数据库和向量索引初始化
│   │   ├── retrieval/      # 智能检索系统
│   │   ├── evaluator/      # 异步记忆评估
│   │   ├── context/        # 上下文构建
│   │   ├── storage/        # 记忆存储管理
│   │   ├── embedding/      # 向量嵌入和缓存
│   │   └── association/    # 记忆关联网络
│   ├── dialogue/           # 对话系统
│   │   ├── engine.py       # 对话引擎
│   │   ├── personality.py  # AI人格设定
│   │   └── processing.py   # 对话处理逻辑
│   ├── audio/              # 音频处理
│   │   ├── system.py       # 音频系统管理
│   │   ├── input.py        # 语音输入（Whisper）
│   │   ├── output.py       # 语音输出（TTS）
│   │   └── keyboard_control.py # 键盘控制
│   ├── prompts/            # 提示词管理
│   │   ├── memory_evaluation.py # 记忆评估提示词
│   │   └── dialogue_generation.py # 对话生成提示词
│   ├── utils/              # 工具函数
│   └── vision/             # 视觉处理（游戏画面识别）
├── config/                 # 配置文件
├── data/                   # 数据存储
├── logs/                   # 日志文件
├── tests/                  # 测试用例
└── setup/                  # 安装脚本
```

### 记忆系统工作流程

Estia的记忆系统采用13步处理流程：

1. **Step 1-2**：数据库初始化和向量化
2. **Step 3**：记忆存储到数据库
3. **Step 4**：FAISS向量相似度检索
4. **Step 5**：关联网络扩展相关记忆
5. **Step 6**：历史记忆检索
6. **Step 7**：记忆排序和去重
7. **Step 8**：智能上下文构建
8. **Step 9-10**：LLM对话生成
9. **Step 11**：LLM异步评估记忆重要性
10. **Step 12**：异步存储评估结果
11. **Step 13**：自动建立记忆关联

## 🧠 记忆系统特性

### 智能检索策略

- **启动记忆**：首次对话主动提供最近5条+高权重5条记忆
- **历史查询**：检测"还记得"等关键词，返回相关历史记忆
- **关键词搜索**：基于用户输入的关键词进行精确匹配
- **语义检索**：使用FAISS向量检索找到语义相似的记忆

### 记忆评估机制

- **权重评分**：1-10分评价记忆重要性
- **智能摘要**：根据内容类型生成不同详细程度的摘要
- **话题分组**：自动识别和分类对话话题
- **异步处理**：后台处理不影响对话流畅性

### 上下文构建

- **分层结构**：角色设定→核心记忆→相关记忆→话题摘要→用户输入
- **智能截断**：根据重要性和相关性优化上下文长度
- **个性化增强**：结合用户偏好和历史交互模式

## 🎙️ 语音交互

### 语音识别
- 基于OpenAI Whisper模型
- 支持实时语音转文本
- 可配置识别语言和模型精度

### 语音合成
- 支持多种TTS引擎
- 可配置语音、语速和音量
- 自然流畅的中文语音输出

### 键盘控制
- 热键触发录音（默认T键）
- 自动静音检测
- 可配置录音参数

## 🤖 对话引擎

### 多模型支持
- **本地模型**：基于llama.cpp的本地部署
- **OpenAI**：GPT-3.5/GPT-4系列
- **DeepSeek**：DeepSeek-Chat等模型
- **Gemini**：Google Gemini系列

### 个性化设定
- 可配置AI人格（友好、专业、幽默等）
- 支持自定义提示词模板
- 个性化回复风格

## 📊 性能特性

### 缓存优化
- 多级记忆缓存机制
- 向量嵌入缓存
- 智能缓存失效策略

### 异步处理
- 后台异步记忆评估
- 非阻塞记忆存储
- 并发处理提升响应速度

### 数据库优化
- SQLite高效存储
- 索引优化查询性能
- 事务处理保证数据一致性

## 🔧 配置选项

### 基础配置
```python
# 模型提供商
MODEL_PROVIDER = "deepseek"

# 语音设置
WHISPER_MODEL_ID = "openai/whisper-large-v3-turbo"
TTS_VOICE = "zh-CN-XiaoyiNeural"

# 记忆设置
MEMORY_CACHE_SIZE = 1000
CONTEXT_WINDOW_SIZE = 10

# 热键设置
RECORD_HOTKEY = "t"
RECORD_MAX_DURATION = 60
```

### 高级配置
- API端点自定义
- 记忆评估参数调整
- 缓存策略配置
- 日志级别设置

## 🧪 测试和开发

### 运行测试
```bash
# 记忆系统测试
python tests/test_memory_pipeline.py

# 异步评估测试
python tests/test_async_evaluator.py

# 完整工作流测试
python tests/test_complete_workflow.py
```

### 开发工具
```bash
# 环境检查
python setup/check_env.py

# 数据库初始化
python scripts/fix_database_schema.py

# 向量索引构建
python scripts/build_index.py
```

## 📈 项目状态

### 已完成功能
- ✅ 完整的13步记忆处理流程
- ✅ 智能检索和上下文构建
- ✅ 异步记忆评估系统
- ✅ 多模型对话引擎支持
- ✅ 语音输入输出功能
- ✅ 模块化架构设计

### 开发中功能
- 🔄 记忆系统优化，记忆归档、记忆遗忘、记忆冲突
- 🔄 更多个性化设定选项，模拟情绪、用户人格画像、情感声线
- 🔄 多模态感知，游戏画面识别（vision模块）
- 🔄 Web API接口

### 计划功能
- 📋 云端同步
- 📋 Q群聊天
- 📋 移动端支持
- 📋 多语言支持
- 📋 插件系统

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置
1. Fork项目
2. 创建开发分支
3. 安装开发依赖
4. 运行测试确保功能正常
5. 提交代码并创建PR

### 代码规范
- 使用中文注释
- 遵循PEP 8代码风格
- 添加适当的类型提示
- 编写测试用例

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- OpenAI Whisper - 语音识别
- Hugging Face - 模型和工具
- FAISS - 向量检索
- 所有贡献者和用户的支持

---

**Estia AI** - 让AI助手真正理解和记住你 🌟