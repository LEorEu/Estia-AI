# Estia AI 智能助手

> 🤖 一个具有先进记忆系统的本地AI助手，支持语音交互、智能对话和持久化记忆

## ✨ 项目亮点

### 🏗️ 企业级架构设计
- **六大模块架构**：采用现代化模块化设计，职责清晰分离
- **15步工作流程**：完整的记忆处理生命周期，从输入到存储
- **588倍缓存加速**：统一缓存管理器，毫秒级响应
- **异步评估机制**：后台智能评估，不阻塞主流程

### 🧠 先进记忆系统
- **4层记忆分级**：核心记忆、归档记忆、长期记忆、短期记忆
- **6种关联类型**：语义、时间、因果、矛盾、相关、总结关联
- **动态权重算法**：基于5个因子的智能权重调整
- **2层深度联想**：智能关联网络，模拟人类记忆

### 🎙️ 全功能语音交互
- **实时语音识别**：集成Whisper，支持多种触发模式
- **多种TTS引擎**：支持多种语音合成方案
- **智能静音检测**：自动检测语音活动
- **热键快速触发**：便捷的交互方式

### 🔄 灵活的对话引擎
- **多LLM支持**：本地/OpenAI/DeepSeek/Gemini，随时切换
- **个性化配置**：可自由配置AI人格和交互模式
- **上下文管理**：智能上下文构建和长度控制
- **异步响应**：高性能异步架构

### 🛡️ 企业级稳定性
- **错误恢复机制**：断路器、重试、降级策略
- **健康监控**：实时监控系统性能和健康状况
- **配置管理**：统一配置管理和动态更新
- **生命周期管理**：自动归档、清理、维护

## 🏗️ 系统架构

### 六大模块架构

```
core/memory/
├── managers/                    # 六大核心管理器
│   ├── sync_flow/              # 同步流程管理器 (Step 1-9)
│   ├── async_flow/             # 异步流程管理器 (Step 10-15)
│   ├── monitor_flow/           # 记忆流程监控器
│   ├── lifecycle/              # 生命周期管理器
│   ├── config/                 # 配置管理器
│   └── recovery/               # 错误恢复管理器
├── shared/                     # 共享工具模块
│   ├── internal/              # 内部工具
│   ├── caching/               # 缓存系统
│   ├── embedding/             # 向量化工具
│   └── emotion/               # 情感分析
└── estia_memory_v5.py         # v5主协调器
```

### 15步工作流程

#### 阶段一：系统初始化 (Step 1-3)
- **Step 1**: 数据库与记忆存储初始化
- **Step 2**: 高级组件初始化 (FAISS、向量化器等)
- **Step 3**: 异步评估器初始化

#### 阶段二：实时记忆增强 (Step 4-9)
- **Step 4**: 统一缓存向量化 (588倍性能提升)
- **Step 5**: FAISS向量检索 (<50ms)
- **Step 6**: 关联网络拓展 (2层深度)
- **Step 7**: 历史对话聚合
- **Step 8**: 权重排序与去重
- **Step 9**: 组装最终上下文

#### 阶段三：对话存储与异步评估 (Step 10-15)
- **Step 10**: LLM生成回复 (外部调用)
- **Step 11**: 立即存储对话
- **Step 12**: 异步LLM评估 (不阻塞)
- **Step 13**: 保存评估结果 (异步)
- **Step 14**: 自动关联创建 (异步)
- **Step 15**: 流程监控和清理 (异步)

## 📊 性能指标

| 性能指标 | 目标值 | 说明 |
|----------|--------|------|
| **缓存加速比** | 588倍 | 统一缓存vs直接计算 |
| **向量检索时间** | <50ms | FAISS检索15条记忆 |
| **上下文组装** | <100ms | 完整Step 4-8流程 |
| **异步评估** | 2-5秒 | LLM评估(不阻塞) |
| **数据库写入** | <10ms | 事务性双写机制 |
| **关联网络查询** | <20ms | 2层深度检索 |

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

1. 在 `config/` 目录下创建一个新文件 `local_settings.py`。
2. 在该文件中添加你的API密钥，例如：

```python
# config/local_settings.py
GEMINI_API_KEY = "your-gemini-api-key"
DEEPSEEK_API_KEY = "your-deepseek-api-key"
OPENAI_API_KEY = "your-openai-api-key"
```

**方法二：使用环境变量**

设置与上述变量同名的环境变量即可。

### 3. 启动系统

```bash
# 启动主程序
python main.py

# 或者使用快捷脚本
start.bat
```

## 🔧 配置管理

### 记忆系统配置

```python
# 获取配置管理器
from core.memory.managers.config import get_config_manager

config_manager = get_config_manager()

# 获取配置
config = config_manager.get_config()

# 更新配置
config_manager.update_config(
    cache_size=2000,
    retrieval_top_k=20,
    similarity_threshold=0.4
)
```

### 主要配置项

```python
class MemoryConfig:
    # 数据库配置
    db_path: str = "data/memory.db"
    
    # 向量化配置
    embedding_model: str = "Qwen3-Embedding-0.6B"
    vector_dimension: int = 1024
    
    # 缓存配置
    cache_enabled: bool = True
    cache_size: int = 1000
    cache_ttl: int = 3600
    
    # 权重配置
    weight_decay_rate: float = 0.995
    max_weight: float = 10.0
    min_weight: float = 0.1
    
    # 检索配置
    retrieval_top_k: int = 15
    similarity_threshold: float = 0.3
    association_depth: int = 2
    
    # 异步评估配置
    async_evaluation_enabled: bool = True
    evaluation_batch_size: int = 10
    evaluation_timeout: int = 30
```

## 🛠️ 开发指南

### 核心API使用

```python
from core.memory import create_estia_memory

# 创建记忆系统实例
memory_system = create_estia_memory(enable_advanced=True)

# 初始化系统
await memory_system.initialize()

# 记忆增强查询
enhanced_context = await memory_system.enhance_query(
    user_input="你好，今天天气怎么样？",
    context={"session_id": "user123"}
)

# 存储交互
await memory_system.store_interaction(
    user_input="你好，今天天气怎么样？",
    ai_response="你好！今天天气很好，阳光明媚。",
    context={"session_id": "user123"}
)
```

### 扩展开发

#### 添加新的管理器

```python
# 1. 创建管理器类
class NewManager:
    def __init__(self, config_manager):
        self.config = config_manager.get_config()
        
    async def new_functionality(self):
        # 实现新功能
        pass

# 2. 在managers/__init__.py中导出
from .new_manager import NewManager
__all__ = [..., 'NewManager']
```

#### 添加新的流程步骤

```python
# 1. 确定步骤归属（同步/异步）
# 2. 在相应管理器中实现逻辑
# 3. 在monitor_flow中添加监控
# 4. 更新文档
```

## 📚 文档

- [六大模块架构文档](docs/six_modules_architecture.md) - 详细的架构设计说明
- [完整工作流程文档](docs/complete_workflow_detailed.md) - 15步工作流程详解
- [安装配置指南](setup/INSTALL_STEPS.md) - 环境安装和配置
- [API参考文档](docs/api_reference.md) - 接口使用说明

## 🎯 版本演进

### v3 → v4 → v5 演进历程

- **v3 (单体架构)**: 1720行代码集中在单个文件，难以维护
- **v4 (轻量级协调器)**: 359行主文件，79%代码减少，engines/模块化
- **v5 (六大模块架构)**: 真正的模块化设计，企业级质量，100%向后兼容

### 关键技术突破

1. **统一缓存管理器**: 588倍性能提升
2. **六大模块协调**: 清晰的职责分离
3. **异步评估机制**: 不阻塞主流程
4. **配置驱动**: 高度可配置
5. **错误恢复**: 企业级稳定性

## 🤝 贡献指南

### 开发环境搭建

```bash
# 1. Fork项目
# 2. 克隆到本地
git clone https://github.com/your-username/Estia-AI.git

# 3. 创建开发分支
git checkout -b feature/your-feature

# 4. 安装开发依赖
pip install -r setup/requirements.txt

# 5. 运行测试
python -m pytest tests/
```

### 代码规范

- 遵循PEP 8代码风格
- 使用类型注解
- 完善的文档字符串
- 单元测试覆盖

### 提交规范

```bash
# 提交格式
git commit -m "feat: 添加新功能"
git commit -m "fix: 修复bug"
git commit -m "docs: 更新文档"
git commit -m "refactor: 重构代码"
```

## 🐛 问题反馈

如果你遇到任何问题或有建议，请在 [GitHub Issues](https://github.com/your-username/Estia-AI/issues) 中提交。

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢所有贡献者和开源社区的支持！

---

## 📝 更新日志

### v5.0.0 (2024-07-09)
- 🎉 **六大模块架构重构**: 完全重构为模块化架构
- ⚡ **588倍缓存加速**: 统一缓存管理器性能优化
- 🔧 **配置管理系统**: 新增ConfigManager统一配置管理
- 🛡️ **错误恢复机制**: 新增ErrorRecoveryManager企业级错误处理
- 📊 **完善监控体系**: 15步流程监控和性能分析
- 🚀 **API保持兼容**: 100%向后兼容，无缝升级

### v4.0.0 (2024-06-XX)
- 🏗️ **轻量级协调器**: 主文件代码减少79%
- 📦 **engines模块化**: 功能模块化设计
- 🔧 **改善维护性**: 提高代码可维护性

### v3.0.0 (2024-05-XX)
- 🧠 **13步工作流程**: 完整的记忆处理流程
- 📊 **性能监控**: 基础性能监控功能
- 🎙️ **语音交互**: 语音输入输出支持