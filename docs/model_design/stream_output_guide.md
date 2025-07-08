# 流式输出功能使用指南

## 🎯 功能概述

Estia AI助手现在支持流式输出功能，提供更自然的对话体验：

- **文本流式输出**：逐字显示AI回复
- **语音流式输出**：边生成边播放语音
- **混合流式输出**：同时进行文本和语音流式输出

## 🚀 快速开始

### 1. 命令行启动

```bash
# 启用所有流式输出
python main.py --stream

# 仅启用文本流式输出
python main.py --text-stream

# 仅启用语音流式输出
python main.py --audio-stream

# 禁用所有流式输出
python main.py --no-stream
```

### 2. 配置文件设置

在 `config/settings.py` 中配置流式输出：

```python
# 流式输出功能开关
ENABLE_STREAM_OUTPUT = True          # 是否启用流式输出
ENABLE_TEXT_STREAM = True            # 是否启用文本流式输出
ENABLE_AUDIO_STREAM = True           # 是否启用语音流式输出

# 流式输出参数
STREAM_CHUNK_SIZE = 50               # 文本分段大小（字符数）
STREAM_DELAY = 0.1                  # 流式输出延迟（秒）
STREAM_AUDIO_SEGMENT_SIZE = 50      # 音频分段大小（字符数）

# 流式输出模式
STREAM_MODE = "both"                # 可选: "text_only", "audio_only", "both"
STREAM_PRIORITY = "text_first"      # 可选: "text_first", "audio_first", "parallel"
```

## 📝 编程接口

### 1. 文本流式输出

```python
from core.dialogue.engine import DialogueEngine

engine = DialogueEngine()

# 流式生成回复
for chunk in engine.generate_response_stream("你好"):
    print(chunk, end="", flush=True)
```

### 2. 语音流式输出

```python
from core.audio.output import speak_stream

def text_generator():
    yield "你好！"
    yield "我是Estia。"
    yield "很高兴认识你！"

# 流式语音输出
speak_stream(text_generator())
```

### 3. 完整流式体验

```python
from core.app import EstiaApp

app = EstiaApp()

# 流式处理查询
for chunk in app.process_query_stream("请介绍一下你自己"):
    print(chunk, end="", flush=True)
```

## ⚙️ 配置选项详解

### 流式输出模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `text_only` | 仅文本流式输出 | 快速响应，节省资源 |
| `audio_only` | 仅语音流式输出 | 语音交互场景 |
| `both` | 文本+语音流式输出 | 完整体验，需要更多资源 |

### 优先级设置

| 优先级 | 说明 | 特点 |
|--------|------|------|
| `text_first` | 文本优先 | 文本显示更快 |
| `audio_first` | 语音优先 | 语音播放更快 |
| `parallel` | 并行处理 | 最佳体验，资源消耗大 |

### 分段参数

- **STREAM_CHUNK_SIZE**: 文本分段大小，影响流式显示的粒度
- **STREAM_AUDIO_SEGMENT_SIZE**: 音频分段大小，影响语音播放的连续性
- **STREAM_DELAY**: 流式输出延迟，控制显示速度

## 🎯 使用场景

### 1. 快速响应场景
```bash
python main.py --text-stream --mode text
```
适合需要快速看到AI回复开始的场景。

### 2. 语音交互场景
```bash
python main.py --audio-stream --mode voice
```
适合语音对话，边听边生成。

### 3. 完整体验场景
```bash
python main.py --stream --mode voice
```
适合需要最佳用户体验的场景。

## 🔧 性能优化

### 1. 资源消耗对比

| 模式 | CPU使用 | 内存使用 | 网络使用 | 延迟 |
|------|---------|----------|----------|------|
| 普通输出 | 低 | 低 | 低 | 高 |
| 文本流式 | 中 | 中 | 中 | 低 |
| 语音流式 | 高 | 高 | 高 | 低 |
| 混合流式 | 高 | 高 | 高 | 最低 |

### 2. 优化建议

- **低配置设备**：使用 `--text-stream` 或 `--no-stream`
- **高配置设备**：使用 `--stream` 获得最佳体验
- **网络环境差**：使用 `--no-stream` 减少网络依赖

## 🐛 故障排除

### 1. 流式输出不工作

**问题**：流式输出没有效果
**解决**：
```bash
# 检查配置
python -c "from config import settings; print(settings.ENABLE_STREAM_OUTPUT)"

# 重新启动
python main.py --stream
```

### 2. 语音流式输出失败

**问题**：语音流式输出报错
**解决**：
```bash
# 检查音频依赖
pip install edge-tts pygame

# 测试音频功能
python tests/test_simple_audio_stream.py
```

### 3. 性能问题

**问题**：流式输出卡顿
**解决**：
```python
# 调整配置参数
STREAM_CHUNK_SIZE = 100  # 增加分段大小
STREAM_DELAY = 0.05      # 减少延迟
```

## 📊 效果对比

### 普通输出
```
用户: 你好
[等待完整回复...]
AI: 你好！很高兴见到你，我是Estia，有什么可以帮助你的吗？
```

### 流式输出
```
用户: 你好
AI: 你 → 你好 → 你好！ → 你好！很 → 你好！很高兴 → ...
```

## 🎉 总结

流式输出功能大大提升了Estia AI助手的用户体验：

- ✅ **低延迟**：立即开始响应
- ✅ **自然体验**：更像真人对话
- ✅ **灵活配置**：支持多种模式
- ✅ **性能优化**：根据设备配置调整

选择合适的流式输出模式，享受更自然的AI对话体验！ 