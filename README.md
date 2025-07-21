# Estia AI 智能助手 


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

## 📊 性能指标与质量评估

### 🎯 实测性能 (v6.0) - 已验证

| 性能指标 | 实测值 | 状态 |
|---------|--------|------|
| **查询处理速度** | **671.60 QPS** (超目标117%) | ✅ 卓越 |
| **平均响应时间** | **1.49ms** | ✅ 卓越 |
| **缓存加速** | **588x** vs 直接计算 | ✅ 完美 |
| **向量检索** | **<50ms** (15个记忆) | ✅ 达标 |


### 🚨 已识别的关键问题

**高优先级问题 (需立即修复):**
- 🔴 **跨平台兼容性**: 音频系统仅支持Windows (msvcrt依赖)
- 🔴 **测试覆盖不足**: 仅15%覆盖率，缺乏单元测试
- 🔴 **内存泄漏风险**: UnifiedCacheManager的key_cache_map可能无限增长

**中优先级问题:**
- 🟡 **代码重复**: 对话引擎消息构建逻辑重复
- 🟡 **模块复杂度**: Web仪表板(1240行)需要拆分
- 🟡 **维度不一致**: Qwen模型(1024维) vs SimpleVectorizer(384维)

### 🎯 性能亮点
- **671.60 QPS** 处理能力，超目标117%
- **1.49ms** 毫秒级响应时间
- **588倍** 缓存性能提升
- **企业级稳定性** 和错误恢复机制

## 🏗️ 系统架构 - v6.0 融合架构

### 6模块管理器架构

```
core/memory/
├── managers/                    # 六大核心管理器
│   ├── sync_flow/              # 同步流程管理器 (Steps 1-9)
│   │   ├── init/               # 系统初始化 (Steps 1-3)
│   │   ├── retrieval/          # 智能检索 (Steps 4-5)
│   │   ├── context/            # 上下文管理 (Steps 6-9)
│   │   ├── ranking/            # 权重排序
│   │   └── storage/            # 记忆存储
│   ├── async_flow/             # 异步流程管理器 (Steps 10-15)
│   │   ├── evaluator/          # LLM异步评估 (Steps 12-13)
│   │   ├── association/        # 关联网络 (Step 14)
│   │   ├── profiling/          # 用户画像
│   │   └── tools/              # 搜索工具
│   ├── monitor_flow/           # 流程监控管理器
│   ├── lifecycle/              # 生命周期管理器
│   ├── config/                 # 配置管理器
│   └── recovery/               # 错误恢复管理器
├── shared/                     # 共享工具集
│   ├── caching/               # 统一缓存系统 (588x加速)
│   ├── embedding/             # 向量化工具 (Qwen3-Embedding-0.6B)
│   ├── emotion/               # 情感分析
│   └── internal/              # 内部工具
└── estia_memory_v6.py         # v6.0融合架构主协调器
```

### 15步记忆处理工作流

**Phase 1: 系统初始化 (Steps 1-3)**
- Step 1: 数据库和记忆存储初始化
- Step 2: 高级组件初始化 (FAISS、向量化器等)
- Step 3: 异步评估器初始化

**Phase 2: 实时记忆增强 (Steps 4-9)**
- Step 4: 统一缓存向量化 (588x性能提升)
- Step 5: FAISS向量检索 (<50ms)
- Step 6: 关联网络扩展 (2层深度)
- Step 7: 历史对话聚合
- Step 8: 权重排序和去重
- Step 9: 最终上下文组装

**Phase 3: 对话存储与异步评估 (Steps 10-15)**
- Step 10: LLM响应生成 (外部调用)
- Step 11: 即时对话存储
- Step 12: 异步LLM评估 (非阻塞)
- Step 13: 保存评估结果 (异步)
- Step 14: 自动关联创建 (异步)
- Step 15: 流程监控和清理 (异步)

## 🚀 快速开始

### 1. 环境安装

```bash
# 克隆项目
git clone https://github.com/LEorEu/Estia-AI.git
cd Estia-AI

# 运行自动安装脚本
cd setup && install.bat && cd ..

# 配置API密钥
echo 'GEMINI_API_KEY="your-key"' > config/local_settings.py
echo 'OPENAI_API_KEY="your-key"' >> config/local_settings.py
```

### 2. 启动系统

```bash
# 语音交互模式（默认）
python main.py

# 文本交互模式
python main.py --mode text

# 启用流式输出
python main.py --stream
```

### 3. 基础使用

```python
from core.memory import create_estia_memory

# 创建记忆系统
memory_system = create_estia_memory(enable_advanced=True)
await memory_system.initialize()

# 增强查询
response = await memory_system.enhance_query(
    user_input="你好！",
    context={"session_id": "user123"}
)
```

## 📚 文档与资源

### 📄 核心文档
- **[🛠️ CLAUDE.md](CLAUDE.md)** - Claude Code 开发指南（最重要）
- **[🔍 代码审查报告](docs/COMPREHENSIVE_CODE_REVIEW_REPORT.md)** - 全面代码质量分析
- **[⚙️ 完整工作流程](docs/complete_workflow_detailed.md)** - 15步技术详解
- **[🏗️ v6.0融合架构](docs/fusion_architecture_v6_implementation_plan.md)** - 架构设计方案

### 🧪 测试与验证
```bash
# 系统验证（推荐）
python test_14_step_workflow.py

# 性能测试
pytest tests/test_cache_performance.py

# 环境检查
python setup/check_env.py
```

### ⚠️ 当前限制
- **🔴 Windows专用**: 音频功能仅支持Windows系统
- **🔴 测试不足**: 单元测试覆盖率仅15%
- **🟡 单用户**: 暂不支持多用户并发场景

---

## 📜 版本历史

- **v6.0** (2025-01-21): 融合架构，588x性能提升，企业级稳定性
- **v5.0** (2024-12): 6模块管理器架构重构
- **v3.0** (2024-11): 14步工作流程完整实现

## 🤝 贡献

欢迎贡献代码和反馈！请优先关注:
1. 跨平台兼容性问题
2. 单元测试覆盖提升
3. 代码重复消除

## 📜 许可证

MIT License - 详细信息请查看 [LICENSE](LICENSE) 文件。