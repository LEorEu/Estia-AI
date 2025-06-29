# Estia AI 个人助手

## 🚀 运行

### 方法1: 智能激活脚本（推荐）
```bash
activate_env.bat             # 自动检测并激活任何类型的环境
python main.py              # 语音模式
python main.py --mode text  # 文本模式
```

### 方法2: 手动激活（按环境类型）
```bash
# Python venv环境（简化版安装）：
env\Scripts\activate.bat

# Conda全局环境：
conda activate estia

# Conda本地环境：
conda activate .\env

# 然后运行：
python main.py              # 语音模式
python main.py --mode text  # 文本模式
```

---

## 项目概述

Estia是一个本地运行的个性化AI助手，具有语音交互能力和强大的记忆系统。它使用大语言模型作为核心，通过多层次记忆架构实现智能对话和长期记忆能力。

## 系统架构

### 核心组件

- **AI大脑**: 基于`llama.cpp`的轻量级服务器，负责加载GGUF格式的大语言模型或者启用openai的api
- **AI身体**: Python编写的前端应用，处理语音输入输出和记忆管理
- **记忆系统**: 多层次记忆架构，支持缓存、修正和检索
- **评分系统**: 对话重要性评估机制，决定记忆存储方式

## 记忆系统详解

### 1. 多层次记忆架构

Estia的记忆系统由四个层次组成，按重要性和访问频率划分：

- **核心记忆**: 存储最重要的用户信息（如姓名、生日、联系方式），永不遗忘
- **归档记忆**: 存储重要但不常用的信息（如生活事件、背景故事）
- **长期记忆**: 存储普通的个人信息和知识（如兴趣爱好、一般性偏好）
- **短期记忆**: 存储临时对话内容，有时间衰减机制

每个层次的记忆都有不同的存储方式、权重和检索优先级。

### 2. 记忆存储方式

- **JSON文件存储**: 
  - 核心记忆: `data/memory/core_memory.json`
  - 归档记忆: `data/memory/archival_memory.json`
  - 长期记忆元数据: `data/memory/long_term_metadata.json`

- **数据库存储**: 
  - 使用SQLite数据库存储所有对话历史
  - 支持按ID、内容、时间和权重检索

- **内存缓存**: 
  - 热缓存: 存储最常访问和最重要的记忆(默认200条)
  - 温缓存: 存储次常访问的记忆(默认1000条)

### 3. 高级特性

- **记忆缓存系统**: 
  - 热/温双层缓存机制
  - 关键词索引加速检索
  - 动态缓存提升策略

- **记忆修正机制**: 
  - 支持更新错误记忆
  - 保留修正历史，降低旧记忆权重

- **关联网络**:
  - 建立记忆之间的语义关联
  - 增强相关记忆的检索能力

## 评分系统详解

### 1. 评分原理

评分系统决定对话的重要性，通过三级优先级机制：

- **规则优先**: 基于关键词和模式的硬编码规则
- **人工干预**: 用户可手动标记重要性
- **LLM评估**: 使用大模型智能判断重要性

### 2. 权重机制

每条记忆都有1-10的权重值：
- **10分**: 核心个人信息、用户明确指令
- **8分**: 重要生活事件、兴趣爱好
- **6分**: 有意义的深入探讨
- **4分**: 普通闲聊或问答
- **2分**: 无信息量的日常问候

### 3. 异步评分

系统使用异步线程池处理评分，不影响主对话流程：
- 对话完成后，评分任务提交到后台线程
- 线程完成评分后将结果写入数据库
- 主程序可继续处理用户交互，不受阻塞

## 工作流程

Estia的完整记忆处理流程如下：

1. **输入处理**:
   - 用户语音输入转文本
   - 文本进行向量嵌入

2. **对话处理**:
   - 检索相关记忆（优先从缓存中查找）
   - 将记忆与当前输入一起发送给LLM
   - LLM生成回复

3. **记忆评估**:
   - 对话完成后启动异步评分
   - 根据规则和LLM评估确定权重
   - 根据权重决定记忆层级

4. **记忆存储**:
   - 将用户输入和AI回复存入数据库
   - 根据层级决定是否写入特定记忆文件
   - 更新记忆缓存

5. **记忆优化**:
   - 定期执行记忆衰减
   - 合并重复记忆
   - 汇总长期记忆

## 使用指南

### 测试记忆系统

按以下顺序运行测试脚本：

```bash
# 基础记忆功能测试
python scripts/test_memory_simple.py

# 记忆缓存测试
python scripts/test_memory_cache.py

# 记忆修正测试
python scripts/test_memory_correction.py

# 评分系统测试
python scripts/test_score_system.py

# 完整记忆系统测试
python scripts/test_memory.py
```

### 常见问题

1. **记忆检索失败**:
   - 确保向量模型已正确加载
   - 检查数据目录是否存在(data/memory/)
   - 验证数据库连接正常

2. **记忆权重异常**:
   - 检查intent_parser.py中的关键词设置
   - 确保LLM连接正常
   - 查看score_async_executor.py日志

3. **缓存统计异常**:
   - 重置缓存：`manager.cache.clear()`
   - 增加日志级别获取详细信息

## 未来计划

1. **改进中文分词支持**
   - 集成专门的中文分词库

2. **增强记忆压缩**
   - 实现更智能的记忆整合
   - 基于时间的自动记忆压缩

3. **个性化特征**
   - 根据用户交互调整记忆权重
   - 添加兴趣标签和情感分析


## 📁 目录结构概览
- `estia/core/memory/init`
- `estia/core/memory/embedding`
- `estia/core/memory/retrieval`
- `estia/core/memory/association`
- `estia/core/memory/context`
- `estia/core/memory/ranking`
- `estia/core/memory/storage`
- `estia/core/audio`
- `estia/core/dialogue`
- `estia/core/utils`
- `estia/config`
- `estia/scripts`
- `estia/tests/test_memory`
- `estia/tests/test_dialogue`
- `estia/tests/test_integration`
- `estia/data/memory`
- `estia/data/vectors`

## 🌟 模块说明与职责
- `memory/init/`: 初始化数据库与向量索引（FAISS + SQLite）
- `memory/embedding/`: 文本向量化与嵌入缓存
- `memory/retrieval/`: FAISS 检索逻辑封装
- `memory/association/`: 记忆关联网络管理（自动关联、多跳联想）
- `memory/context/`: 根据 session_id 获取历史会话或摘要
- `memory/ranking/`: 记忆评分、排序与去重策略
- `memory/storage/`: 统一记忆存储与管理接口（写入、更新）
- `audio/`: Whisper 转文字 + TTS 合成语音模块
- `dialogue/`: 对话主逻辑（生成、处理、人格等）
- `utils/`: 通用配置与日志工具
- `scripts/`: 索引构建、清理维护等开发工具脚本
- `tests/`: 单元测试与集成测试目录


estia/
├── core/
│   ├── memory/               # 专注于记忆系统
│   │   ├── init/             # 步骤1: 初始化向量索引和数据库
│   │   │   ├── __init__.py
│   │   │   ├── db_manager.py
│   │   │   └── vector_index.py
│   │   │
│   │   ├── embedding/        # 步骤3: 文本向量化
│   │   │   ├── __init__.py
│   │   │   ├── vectorizer.py
│   │   │   └── cache.py      # 嵌入缓存
│   │   │
│   │   ├── retrieval/        # 步骤4: FAISS搜索
│   │   │   ├── __init__.py
│   │   │   └── faiss_search.py
│   │   │
│   │   ├── association/      # 步骤5: 关联网络拓展
│   │   │   ├── __init__.py
│   │   │   └── network.py
│   │   │
│   │   ├── context/          # 步骤6: 获取对话记录
│   │   │   ├── __init__.py
│   │   │   └── history.py
│   │   │
│   │   ├── ranking/          # 步骤7: 权重优先排序
│   │   │   ├── __init__.py
│   │   │   └── scorer.py
│   │   │
│   │   ├── storage/          # 存储相关功能
│   │   │   ├── __init__.py
│   │   │   └── memory_store.py
│   │   │
│   │   └── pipeline.py       # 记忆系统的流程控制
│   │
│   ├── audio/                # 音频处理相关
│   │   ├── input.py          # 步骤2: 语音输入转文本
│   │   └── output.py         # 语音输出
│   │
│   ├── dialogue/             # 对话系统
│   │   ├── engine.py         # 对话引擎核心
│   │   ├── personality.py    # 人格设定
│   │   ├── generation.py     # 步骤9: LLM生成回复
│   │   └── processing.py     # 步骤10-11: 异步处理和评估
│   │
│   ├── utils/                # 通用工具函数
│   │   ├── config_loader.py
│   │   └── logger.py
│   │
│   └── app.py               # 应用主控制器，整合所有功能
│
├── config/                   # 配置文件
│   └── settings.py
│
├── data/                     # 数据存储
│   ├── memory/
│   └── vectors/
│
├── scripts/                  # 实用脚本
│   ├── build_index.py
│   └── maintenance.py
│
└── tests/                    # 测试用例
    ├── test_memory/
    ├── test_dialogue/
    └── test_integration/