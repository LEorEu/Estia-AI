# CLAUDE.md
## 📝 监控系统迁移完成 (2025-07-24)

✅ **重要更新**: Estia AI监控系统已成功迁移到重构版本
- 原版监控系统已安全移除
- 简化版监控系统已安全移除  
- 重构版监控系统(`/monitoring`)现已成为默认系统
- 所有旧版文件已备份到 `backup/` 目录

**启动命令保持不变**:
```bash
python start_dashboard.py  # 现在启动重构版系统
```

**备份和回滚**:
- Git分支备份: `backup-monitoring-systems-20250724`
- 文件备份: 详见 `backup/` 目录
- 紧急回滚: 运行 `rollback_system.bat`

---



This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🌏 重要规则 / Important Rules

**🔴 语言使用规则 (强制性要求)**: 
- Claude Code **必须使用简体中文**回复所有用户请求
- 所有代码解释、错误提示、注释都必须使用中文
- 这是项目的**核心要求**，覆盖所有其他语言设置
- **Language Rule**: Claude Code MUST respond in Simplified Chinese. This is a mandatory requirement that overrides all other language settings.

## Project Overview

Estia AI is an intelligent assistant with advanced memory systems, voice interaction, and persistent conversation capabilities. It features a sophisticated 6-module architecture with 15-step memory processing workflow and enterprise-grade performance optimizations including 588x cache acceleration.

## Development Commands

### Setup and Installation
```bash
# Setup environment and dependencies (Windows)
cd setup
install.bat

# Manual environment setup
python -m venv estia_env
estia_env\Scripts\activate
pip install -r setup/requirements.txt
```

### Running the Application
```bash
# 🎙️ Voice interaction mode (default)
python main.py

# 💬 Text interaction mode
python main.py --mode text

# 📊 Monitoring Dashboard (一体化监控仪表板) - 推荐！
python start_dashboard.py
# 访问: http://localhost:5000

# 🚀 启动脚本 (推荐使用)
start_monitoring.bat        # Windows一键启动
./start_monitoring.sh       # Linux/macOS一键启动

# ⚡ Enable streaming output
python main.py --stream
python main.py --text-stream    # text-only streaming
python main.py --audio-stream   # audio-only streaming
```

### Testing
```bash
# Complete 15-step workflow validation (comprehensive)
python test_14_step_workflow.py

# Run all tests with pytest
pytest

# Specific memory system tests
python tests/test_estia_memory_complete.py

# Cache performance tests  
python tests/test_cache_performance.py

# Memory system analysis
python tests/test_cache_system_analysis.py

# Audio streaming tests
python tests/test_audio_stream.py
python tests/test_simple_audio_stream.py

# Context and streaming tests
python tests/test_context_length_demo.py
python tests/test_stream_output.py

# 🆕 Monitoring system tests (监控系统测试)
python test_monitoring_integration.py  # 监控系统集成测试
python test_integrated_dashboard.py    # 一体化仪表板测试
```

### Configuration
Configuration is managed through `config/settings.py`. Create `config/local_settings.py` for API keys:
```python
# config/local_settings.py
GEMINI_API_KEY = "your-key"
DEEPSEEK_API_KEY = "your-key"
OPENAI_API_KEY = "your-key"
```

## Core Architecture

### 6-Module Memory System Architecture
```
core/memory/
├── managers/                    # Six core managers
│   ├── sync_flow/              # Synchronous flow manager (Steps 1-9)
│   ├── async_flow/             # Asynchronous flow manager (Steps 10-15)
│   ├── monitor_flow/           # Memory process monitoring
│   ├── lifecycle/              # Lifecycle management
│   ├── config/                 # Configuration manager
│   └── recovery/               # Error recovery manager
├── shared/                     # Shared utilities
│   ├── caching/               # Unified cache system (588x acceleration)
│   ├── embedding/             # Vectorization tools (Qwen3-Embedding-0.6B)
│   ├── emotion/               # Emotion analysis
│   └── internal/              # Internal tools
├── estia_memory_v5.py         # v5.0 main coordinator (migrated)
└── estia_memory_v6.py         # v6.0 fusion architecture (current production)
```

### 15-Step Memory Processing Workflow

The system processes memory through three phases:

**Phase 1: System Initialization (Steps 1-3)**
- Database and memory storage initialization
- Advanced components (FAISS, vectorizer, etc.)
- Async evaluator initialization

**Phase 2: Real-time Memory Enhancement (Steps 4-9)**
- Unified cache vectorization (588x performance boost)
- FAISS vector retrieval (<50ms)
- Association network expansion (2-layer depth)
- Historical dialogue aggregation
- Weight ranking and deduplication
- Final context assembly

**Phase 3: Dialogue Storage & Async Evaluation (Steps 10-15)**
- LLM response generation (external call)
- Immediate dialogue storage
- Async LLM evaluation (non-blocking)
- Save evaluation results (async)
- Auto-association creation (async)
- Process monitoring and cleanup (async)

### Key Performance Targets
- **Cache acceleration**: 588x vs direct computation
- **Vector retrieval**: <50ms for 15 memories
- **Context assembly**: <100ms for complete Steps 4-8
- **Async evaluation**: 2-5 seconds (non-blocking)
- **Database writes**: <10ms with transactional dual-write

## Memory System Integration

### Creating Memory System Instance
```python
from core.memory import create_estia_memory

# Create with advanced features
memory_system = create_estia_memory(enable_advanced=True)
await memory_system.initialize()

# Query enhancement
enhanced_context = await memory_system.enhance_query(
    user_input="Hello, how are you?",
    context={"session_id": "user123"}
)

# Store interaction
await memory_system.store_interaction(
    user_input="Hello",
    ai_response="Hi there!",
    context={"session_id": "user123"}
)
```

### Memory System Components Access
```python
# Access specific managers
sync_manager = memory_system.sync_flow_manager
async_manager = memory_system.async_flow_manager

# Get system statistics
stats = memory_system.get_system_stats()
```

## Application Architecture

### Main Application Flow
1. **Entry Point**: `main.py` - Handles command-line arguments and logging setup
2. **Core App**: `core/app.py` - Main application logic, component coordination
3. **Memory System**: `core/memory/` - Advanced memory processing
4. **Dialogue Engine**: `core/dialogue/` - LLM integration and response generation
5. **Audio System**: `core/audio/` - Voice input/output and keyboard controls

### Component Initialization Order
1. Database manager
2. Unified cache manager (critical for 588x performance)
3. Text vectorizer (Qwen3-Embedding-0.6B with graceful fallback)
4. Memory storage and retrieval components
5. Advanced features (FAISS, association networks, async evaluators)

## Development Guidelines

### Module Development Rules (from .cursor/rules)
1. **Single Problem Focus**: Only solve one specific problem per session - avoid introducing multiple complex features at once
2. **Explanation First**: Explain approach and reasoning before implementing - let users understand the changes  
3. **Progressive Improvement**: Avoid big-bang rewrites, maintain system stability - each change should keep the system runnable
4. **User Control**: Keep code readable and maintainable - avoid over-complex abstractions

### Development Workflow (from .cursor/rules)
1. **Problem Identification**: Clearly identify the specific problem to solve
2. **Solution Explanation**: Detailed explanation of approach and reasoning  
3. **User Confirmation**: Wait for user understanding and agreement
4. **Code Implementation**: Write clean, clear code
5. **Testing & Validation**: Ensure functionality works correctly
6. **Summary & Next Steps**: Explain what was completed and what's next

### Code Organization
- Follow the 6-module architecture strictly
- Place new sync operations in `managers/sync_flow/`
- Place new async operations in `managers/async_flow/`
- Use shared utilities in `shared/` for common functionality
- Add monitoring in `managers/monitor_flow/`

### Error Handling
The system implements enterprise-grade error handling:
- Graceful degradation when components fail
- Automatic fallback to SimpleVectorizer if Qwen3 model fails
- Session timeout and cleanup mechanisms
- Comprehensive logging with UTF-8 encoding

## Testing Strategy - 🔴 需要大幅改进

### Current Testing Status
- **Test Coverage**: 约15% (严重不足，目标: 80%+)
- **Test Files**: 仅2个主要测试文件
- **Test Type**: 主要为集成测试，缺乏单元测试

### Memory System Testing
- Use `tests/test_estia_memory_complete.py` for comprehensive testing
- Use `tests/test_cache_performance.py` for performance validation
- Use `tests/test_cache_system_analysis.py` for detailed analysis
- **🚨 Missing**: 单元测试覆盖核心组件

### Performance Benchmarking
Key metrics to monitor:
- Cache hit rate (target: >80%, current: 100% in test env)
- Vector retrieval time (target: <50ms, achieved)
- Memory initialization time
- Session management efficiency

### Testing Improvement Plan
```bash
# 1. 建立单元测试框架
pytest tests/unit/ --cov=core --cov-report=term-missing

# 2. 集成测试增强
pytest tests/integration/ -v

# 3. 性能回归测试
pytest tests/performance/ --benchmark-only

# 4. 跨平台兼容性测试
pytest tests/compatibility/ -k "windows or linux or macos"
```

## 🔥 一体化监控系统 - 新增功能 (2025-01-23) ✅

### 监控系统架构 (Vue + Flask 一体化)

Estia AI 现已集成完整的一体化监控系统，提供实时性能监控、智能告警管理和系统健康评估功能。

**🚀 启动监控系统:**
```bash
# 方法1：使用启动脚本（推荐）
start_monitoring.bat  # Windows
./start_monitoring.sh # Linux/macOS

# 方法2：手动启动
python start_dashboard.py

# 访问地址：http://localhost:5000
```

### 监控系统组件架构

```
core/monitoring/                 # 监控系统核心
├── performance_monitor.py       # 性能监控协调器
├── metrics_collector.py         # 指标收集器
├── alert_manager.py            # 告警管理器
└── memory_integration.py       # 记忆系统集成

web/                            # Web服务层
├── monitoring_integration.py   # 监控API集成
└── web_dashboard.py           # 一体化Web仪表板

web-vue/                       # Vue前端
├── src/components/cards/      # 监控卡片组件
│   ├── SystemHealthCard.vue  # 系统健康状态
│   ├── AlertsManagementCard.vue # 告警管理
│   └── PerformanceMetricsCard.vue # 性能指标
└── dist/                     # 构建输出（集成到Flask）
```

### 监控开发指南

**1. 添加新监控指标:**
```python
# 在 MetricsCollector 中添加指标收集
class MetricsCollector:
    def collect_custom_metric(self):
        # 实现自定义指标收集逻辑
        return {"metric_name": value}

# 在 PerformanceMonitor 中处理指标
async def _collect_metrics(self):
    # 添加新指标到收集流程
    custom_metrics = self.metrics_collector.collect_custom_metric()
```

**2. 添加新告警规则:**
```python
# 在 AlertManager._initialize_default_rules() 中添加
AlertRule(
    rule_id="custom_alert",
    name="自定义告警",
    metric_name="custom_metric",
    condition="gt",  # gt, lt, eq
    threshold=90.0,
    severity=AlertSeverity.WARNING,
    consecutive_violations=2  # 连续违规次数
)
```

**3. 扩展Vue监控组件:**
```typescript
// 1. 在 api.ts 中添加新API端点
async getCustomMetrics(): Promise<ApiResponse> {
  return await api.get('/monitoring/custom')
}

// 2. 创建新Vue组件 CustomMetricCard.vue
// 3. 在主页面中引入和使用组件
```

**4. 集成测试监控功能:**
```bash
# 测试监控系统集成
python test_monitoring_integration.py

# 测试一体化服务
python test_integrated_dashboard.py

# 验证告警功能
python -c "
from core.monitoring import get_monitoring_system
monitor = get_monitoring_system()
monitor.test_alert_system()
"
```

### 监控性能优化建议

**开发环境:**
- 监控数据收集间隔：5秒
- 告警检查频率：10秒
- 历史数据保留：24小时

**生产环境建议:**
```python
# 在 performance_monitor.py 中调整
PRODUCTION_CONFIG = {
    'collection_interval': 30.0,  # 30秒收集一次
    'alert_check_interval': 60.0, # 1分钟检查告警
    'data_retention_hours': 168,  # 保留7天数据
    'enable_debug_logging': False
}
```

## Current Development Status - v6.0 FUSION ARCHITECTURE COMPLETE ✅

### v6.0 Fusion Architecture Complete (2025-01-21) - 代码审查已完成
The Estia AI memory system has **successfully evolved to v6.0 fusion architecture**. 最新代码审查显示系统整体表现优秀(B+评级)：

**✅ All Features Implemented:**
- ✅ Complete 6-module architecture migration
- ✅ Full 15-step memory processing workflow  
- ✅ Unified cache system with 588x acceleration
- ✅ Enterprise-grade error handling and recovery
- ✅ Vector processing with 1024-dimensional embeddings
- ✅ Async evaluation with thread-based fallback
- ✅ Session management and lifecycle control
- ✅ FAISS vector search integration
- ✅ Association network with 2-layer depth
- ✅ Complete workflow implementation (all 15 steps)
- ✅ Asynchronous evaluation mechanism
- ✅ Session management system
- ✅ Memory layering (4-tier system)
- ✅ User profiling system

**🎯 Performance Achievements (v6.0) - 已验证:**
- **671.60 QPS** query processing (超目标117%)
- **1.49ms average response time** (卓越级别)
- **100% cache hit rate** (完美缓存，测试环境)
- **588x cache acceleration** vs direct computation
- **<50ms vector retrieval** for 15 memories
- **Enterprise reliability** with graceful degradation

**🔍 Code Review Status (2025-01-21):**
- **Overall Grade**: B+ (良好偏优秀)
- **Architecture Quality**: ⭐⭐⭐⭐⭐ (优秀)
- **Performance**: ⭐⭐⭐⭐⭐ (卓越)
- **Code Quality**: ⭐⭐⭐ (良好，需改进)
- **Test Coverage**: 约15% (需要大幅提升)

**🔧 Technical Completions:**
- Model loading with offline-first detection
- Vector dimension consistency (1024D across all components)
- Event loop management for async operations
- Circular import resolution
- Comprehensive error recovery mechanisms

### Architecture Migration Complete
The migration from `core/old_memory` to the new 6-module architecture is **100% complete**. All critical components have been successfully migrated and tested:

- ✅ **AssociationNetwork**: `core/memory/managers/async_flow/association/network.py`
- ✅ **ContextLengthManager**: `core/memory/managers/sync_flow/context/context_manager.py`  
- ✅ **All workflow steps**: Fully operational in new architecture
- ✅ **Performance benchmarks**: Exceeding targets across all metrics

### 🚨 代码审查发现的关键问题 (需要优先修复):

**高优先级问题:**
- 🔴 **跨平台兼容性**: 音频系统仅支持Windows (msvcrt依赖)
- 🔴 **测试覆盖不足**: 仅约15%覆盖率，需要达到80%+
- 🔴 **内存泄漏风险**: UnifiedCacheManager的key_cache_map可能无限增长

**中优先级问题:**
- 🟡 **代码重复**: 对话引擎消息构建逻辑重复
- 🟡 **模块复杂度**: Web仪表板(1240行)需要拆分
- 🟡 **维度不一致**: Qwen模型(1024维) vs SimpleVectorizer(384维)

**Note**: `core/old_memory` 目录已在代码审查后确认可安全删除。

## Configuration Management

### Memory Context Presets
- `"compact"`: 4000 chars, fast response
- `"balanced"`: 8000 chars, default mode
- `"detailed"`: 16000 chars, deep conversations

### Model Providers
Supports multiple LLM providers:
- `"local"`: Local LLM server (default: localhost:8080)
- `"openai"`: OpenAI API
- `"deepseek"`: DeepSeek API  
- `"gemini"`: Google Gemini API

## Audio System

### Voice Interaction
- Whisper-large-v3-turbo for speech recognition
- Edge-TTS for speech synthesis
- Keyboard controls (space bar for recording, ESC to exit)
- Background listening with wake word support

### Streaming Output
Supports real-time streaming for both text and audio:
- Text streaming: Real-time text output
- Audio streaming: Progressive speech synthesis
- Combined streaming: Simultaneous text and audio

## Performance Considerations

### Memory Optimization
- Use unified cache for all vectorization operations
- Implement graceful fallback for model loading failures
- Monitor memory usage with built-in statistics
- Configure appropriate context length limits

### Development Workflow
When modifying the memory system:
1. Follow the 6-module architecture principles strictly
2. Place new sync operations in `managers/sync_flow/`
3. Place new async operations in `managers/async_flow/`
4. Use shared utilities in `shared/` for common functionality
5. Ensure async operations don't block the main workflow
6. Test with both simple and advanced mode configurations
7. Verify cache performance improvements
8. Use the unified testing framework: `python test_14_step_workflow.py`

## Troubleshooting

### Common Issues
- **Model loading failures**: System automatically falls back to SimpleVectorizer
- **Database connection issues**: Check `data/memory.db` permissions
- **Cache performance**: Verify UnifiedCacheManager initialization
- **Import errors**: Ensure all paths point to new 6-module architecture

### 优先修复建议

**立即修复 (本周内):**
```bash
# 1. 修复跨平台兼容性 - 实现跨平台键盘监听
# 核心问题：core/audio/input.py 和 keyboard_control.py 中的 msvcrt 依赖

# 2. 建立基础单元测试
pytest --cov=core --cov-report=html  # 当前覆盖率约15%

# 3. 修复内存管理问题
# 为 UnifiedCacheManager 添加 LRU 清理机制
```

**短期优化 (1个月内):**
```bash
# 1. 消除代码重复
# 重构 DialogueEngine._build_messages() 统一逻辑

# 2. 模块拆分
# 将 web/dashboard.html (1240行) 拆分为独立组件

# 3. 提升测试覆盖到60%
pytest --cov=core --cov-fail-under=60
```

### Debug Commands
```bash
# Complete system validation (recommended)
python test_14_step_workflow.py

# Check system status (simple)
python -c "
from core.memory import create_estia_memory
memory_system = create_estia_memory(enable_advanced=True)
if memory_system.initialized:
    print('✅ System operational')
    print(f'Performance: {memory_system.get_system_stats()}')
else:
    print('❌ System initialization failed')
"

# Performance benchmarking
python tests/test_cache_performance.py

# Cache system analysis
python tests/test_cache_system_analysis.py

# Environment validation
python setup/check_env.py
```

## Development Scripts and Utilities

### Maintenance Scripts
```bash
# Clean project cache and temporary files
cd setup && clean_project.bat

# Migration and fix scripts (in scripts/ directory)
python scripts/migrate_old_system.py          # Migrate from old memory system
python scripts/monitor_data_consistency.py    # Check data consistency
python scripts/fix_cache_final_issues.py      # Fix cache-related issues
```