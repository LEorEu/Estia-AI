# Estia AI助手 - 安装使用说明

## 🚀 快速开始

### 1. 安装环境
```bash
# 进入setup目录
cd setup

# 运行安装脚本
install.bat

# 或者双击运行 setup/install.bat
```

### 2. 启动程序
```bash
# 回到项目根目录
cd ..

# 使用友好启动器（推荐）
start.bat

# 或者手动激活环境
activate.bat
```

## 📁 目录结构

```
estia/
├── setup/                  # 安装相关文件
│   ├── install.bat        # 主安装脚本
│   ├── activate.bat       # 环境激活脚本
│   ├── check_env.py       # 环境检查工具
│   ├── requirements.txt   # 依赖列表
│   └── INSTALL_STEPS.md   # 详细安装步骤
├── miniconda3/            # Miniconda安装目录（自动创建）
├── env/                   # Python环境（自动创建）
├── start.bat              # 友好启动器
├── activate.bat           # 环境激活脚本（自动创建）
├── main.py               # 主程序
└── config/               # 配置文件
    └── settings.py       # 设置文件
```

## 💡 使用方法

### 启动选项
1. **`start.bat`** - 友好启动器（推荐）
   - 自动检查环境
   - 提供菜单选择
   - 支持多种运行模式

2. **`activate.bat`** - 手动激活环境
   - 激活后可以运行任何Python命令
   - 适合开发和调试

3. **`setup\activate.bat`** - 从setup目录激活
   - 从setup目录启动的激活脚本

### 环境检查
```bash
# 在激活的环境中运行
python setup\check_env.py

# 检查所有组件状态
```

## 🔧 配置设置

### DeepSeek API配置
编辑 `config/settings.py`:
```python
DEEPSEEK_API_KEY = "你的API密钥"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
```

### 镜像源设置
安装时可选择：
- 清华源（国内推荐）
- HF镜像源（模型下载加速）

## 🛠️ 故障排除

### 常见问题
1. **环境未安装**: 运行 `setup\install.bat`
2. **GPU未检测**: 检查NVIDIA驱动
3. **网络问题**: 重新安装时选择镜像源
4. **环境损坏**: 删除env和miniconda3目录重新安装

### 完全卸载
```bash
# 删除所有安装内容
rmdir /s /q env
rmdir /s /q miniconda3
del activate.bat
```

## 📋 系统要求

- **推荐**: RTX 3060 6GB或更高
- **内存**: 8GB RAM+
- **存储**: 5GB可用空间
- **网络**: 稳定互联网连接（首次安装）

---

💡 **提示**: 使用 `start.bat` 获得最佳用户体验！ 