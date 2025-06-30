# 配置文件说明

## 📁 文件结构

```
config/
├── settings.py           # 主配置文件（安全，可提交）
├── settings_template.py  # 配置模板（可提交）
├── local_settings.py     # 本地配置（包含API密钥，不提交）
└── README.md            # 本说明文件
```

## 🔧 配置方法

### 方法1：使用本地配置文件（推荐）

1. 复制模板文件：
```bash
cp config/settings_template.py config/local_settings.py
```

2. 编辑 `config/local_settings.py`，填入你的API密钥：
```python
# DeepSeek API 配置
DEEPSEEK_API_KEY = "your-deepseek-api-key"

# Gemini API 配置  
GEMINI_API_KEY = "your-gemini-api-key"

# OpenAI API 配置
OPENAI_API_KEY = "your-openai-api-key"
```

### 方法2：使用环境变量

设置环境变量：
```bash
# Windows
set DEEPSEEK_API_KEY=your-deepseek-api-key
set GEMINI_API_KEY=your-gemini-api-key

# Linux/Mac
export DEEPSEEK_API_KEY=your-deepseek-api-key
export GEMINI_API_KEY=your-gemini-api-key
```

## 🔒 安全说明

- `settings.py` - 主配置文件，不包含敏感信息，可以安全提交到Git
- `local_settings.py` - 包含真实API密钥，已在.gitignore中，不会被提交
- `settings_template.py` - 配置模板，供新用户参考

## 🚀 优先级

配置加载优先级：**环境变量** > **local_settings.py** > **默认空值**

这样既保证了安全性，又提供了灵活性！ 