# Estia AI助手 - 分步安装指南

> 如果批处理脚本有问题，可以按照这个指南手动安装

### 步骤1: 创建conda环境
```bash
# 创建Python 3.11环境并安装基础科学计算包
conda create -n estia python=3.11 numpy scipy pip -y

# 激活环境
conda activate estia
```

### 步骤2: 验证环境
```bash
# 检查Python版本
python --version

# 检查GPU
nvidia-smi
```

### 步骤3: 安装GPU版PyTorch
```bash
# RTX 3060适用（CUDA 12.1兼容CUDA 12.5）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 步骤4: 验证PyTorch GPU支持
```bash
# 验证安装
python -c "import torch; print('PyTorch版本:', torch.__version__); print('CUDA可用:', torch.cuda.is_available())"
```

### 步骤5: 安装项目依赖
```bash
# 安装AI和机器学习包
pip install openai openai-whisper transformers sentence-transformers

# 安装音频处理包
pip install sounddevice soundfile edge-tts pygame

# 安装向量检索（CPU版本，更稳定）
pip install faiss-cpu

# 安装系统工具
pip install keyboard
```

### 步骤6: 验证所有安装
```bash
# 验证各个组件
python -c "import openai-whisper; print('✅ openai-whisper已安装')"
python -c "import faiss; print('✅ FAISS已安装')"
python -c "from sentence_transformers import SentenceTransformer; print('✅ sentence-transformers已安装')"
python -c "import sounddevice; print('✅ 音频设备支持已安装')"
```

### 步骤7: 配置API密钥
```bash
# 编辑配置文件
notepad config/settings.py

# 或者用VS Code
code config/settings.py
```

在配置文件中设置：
```python
DEEPSEEK_API_KEY = "your-deepseek-api-key-here"
MODEL_PROVIDER = "deepseek"
```

### 步骤8: 测试运行
```bash
# 文本模式测试
python main.py --mode text

# 语音模式测试（如果文本模式正常）
python main.py
```

---

## 🛠️ 其他安装方式

### 方式A: 使用environment.yml（推荐）
```bash
# 1. 下载基础环境
conda env create -f environment.yml

# 2. 激活环境
conda activate estia

# 3. 安装GPU版PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 方式B: 项目本地环境（venv）
```bash
# 1. 创建本地虚拟环境
python -m venv env

# 2. 激活环境（Windows）
env\Scripts\activate.bat

# 3. 升级pip
python -m pip install --upgrade pip

# 4. 安装PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 5. 安装项目依赖
pip install -r requirements.txt
```

### 方式C: 使用清华源加速（网络慢时）
```bash
# 1. 创建环境
conda create -n estia python=3.11 numpy scipy pip -y
conda activate estia

# 2. 配置pip清华源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 安装PyTorch（这个必须用官方源）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 4. 安装其他依赖（使用清华源）
pip install openai openai-whisper sounddevice scipy numpy edge-tts keyboard pygame transformers soundfile sentence-transformers faiss-cpu
```

---

## 🗑️ 环境清理命令

### 删除conda环境
```bash
# 删除全局环境
conda remove -n estia --all -y

# 删除本地环境（如果用的--prefix方式）
conda remove --prefix .\env --all -y
rmdir /s /q env
```

### 删除venv环境
```bash
# 停用环境
deactivate

# 删除文件夹
rmdir /s /q env
```

---

## 🔧 常见问题解决

### Q: PyTorch安装失败
```bash
# 清理pip缓存
pip cache purge

# 重新安装
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --no-cache-dir
```

### Q: CUDA版本不匹配
```bash
# 检查CUDA版本
nvidia-smi

# 根据CUDA版本选择对应的PyTorch：
# CUDA 11.8: --index-url https://download.pytorch.org/whl/cu118
# CUDA 12.1: --index-url https://download.pytorch.org/whl/cu121
```

### Q: 网络下载速度慢
```bash
# 使用国内镜像（仅限非PyTorch包）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name
```

### Q: 权限问题
```bash
# 以管理员身份运行CMD或PowerShell
# 或者使用用户级安装
pip install --user package_name
``` 