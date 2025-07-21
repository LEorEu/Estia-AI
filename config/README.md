# 配置文件说明

## ⚠️ 安全警告：Token泄露修复

**重要：由于之前的token泄露，请立即按照以下步骤操作：**

1. **立即撤销被泄露的token**: `sk-ant-oat01-e108b9b0d69a97f...`
2. **生成新的API token**
3. **按照下方配置说明设置新token**

## 📁 文件结构

```
config/
├── settings.py           # 主配置文件（安全，可提交）
├── env_template.ps1      # PowerShell环境配置模板
├── env_local.ps1         # 本地环境配置（包含API密钥，不提交）
├── local_settings.py     # 本地配置（包含API密钥，不提交）
└── README.md            # 本说明文件
```

## 🔧 配置方法

### 方法1：PowerShell环境配置（推荐用于run_claude.ps1）

1. 复制模板文件：
```powershell
cp config\env_template.ps1 config\env_local.ps1
```

2. 编辑 `config\env_local.ps1`，填入你的API密钥：
```powershell
# Anthropic API配置
$env:ANTHROPIC_API_KEY = "sk-ant-oat01-your-new-token-here"
$env:ANTHROPIC_BASE_URL = "https://relay01.gaccode.com/claudecode"
```

### 方法2：Python本地配置文件

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

### 方法3：使用环境变量

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
- `env_local.ps1` - PowerShell环境配置，包含真实API密钥，已在.gitignore中，不会被提交
- `local_settings.py` - Python配置文件，包含真实API密钥，已在.gitignore中，不会被提交
- `env_template.ps1` - PowerShell配置模板，供新用户参考
- `settings_template.py` - Python配置模板，供新用户参考

## 🚨 立即行动清单

- [ ] **立即撤销泄露的token**: `sk-ant-oat01-e108b9b0d69a97f...`
- [ ] **生成新的API token**
- [ ] **创建 `config\env_local.ps1` 配置新token**
- [ ] **测试新配置是否工作正常**
- [ ] **确认敏感文件已被.gitignore忽略**

## 🚀 优先级

配置加载优先级：**环境变量** > **local_settings.py** > **默认空值**

这样既保证了安全性，又提供了灵活性！ 