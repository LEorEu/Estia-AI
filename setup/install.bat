@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================================
echo 🚀 Estia AI助手 - 完整安装脚本
echo    从零开始，包含conda安装
echo ==========================================

:: 设置项目目录（上级目录）
set PROJECT_DIR=%~dp0..
cd /D %PROJECT_DIR%

:: 询问镜像源选择
echo 💡 选择下载源（影响下载速度）:
echo    1. 官方源 (国外快)
echo    2. 清华源 (国内快)
echo.
set /p MIRROR_CHOICE="请选择 (1 或 2，默认为1): "
if not defined MIRROR_CHOICE set MIRROR_CHOICE=1

if "%MIRROR_CHOICE%"=="2" (
    set USE_MIRROR=1
    echo ✅ 将使用清华镜像源加速
) else (
    set USE_MIRROR=0
    echo ✅ 将使用官方源
)

:: 询问HF镜像配置
echo.
echo 💡 Hugging Face模型下载源:
echo    1. 官方源 (需要良好网络)
echo    2. HF镜像源 (国内推荐)
echo.
set /p HF_CHOICE="请选择 (1 或 2，默认为2): "
if not defined HF_CHOICE set HF_CHOICE=2

if "%HF_CHOICE%"=="2" (
    set USE_HF_MIRROR=1
    echo ✅ 将配置HF镜像源
) else (
    set USE_HF_MIRROR=0
    echo ✅ 将使用HF官方源
)

:: 检查conda是否已安装
echo.
echo 🔍 检查conda环境...
conda --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('conda --version 2^>^&1') do set CONDA_VERSION=%%i
    echo ✅ conda已安装，版本: !CONDA_VERSION!
    goto conda_ready
)

echo ❌ 未找到conda，开始安装Miniconda...

:: 下载并安装Miniconda
echo 📥 下载Miniconda3 (Windows x64)...
if "%USE_MIRROR%"=="1" (
    set CONDA_URL=https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Windows-x86_64.exe
) else (
    set CONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
)

powershell -Command "Invoke-WebRequest -Uri '%CONDA_URL%' -OutFile 'Miniconda3-Installer.exe'"
if not exist "Miniconda3-Installer.exe" (
    echo ❌ Miniconda下载失败，请检查网络连接
    goto end
)

echo 🔧 安装Miniconda...
echo    安装位置: %PROJECT_DIR%miniconda3
start /wait Miniconda3-Installer.exe /InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=%PROJECT_DIR%miniconda3

:: 清理安装包
del Miniconda3-Installer.exe

:: 初始化conda
echo 🔄 初始化conda环境...
call %PROJECT_DIR%miniconda3\Scripts\activate.bat
call conda init cmd.exe

echo ✅ Miniconda安装完成！

:conda_ready

:: 配置conda镜像源
if "%USE_MIRROR%"=="1" (
    echo 🔧 配置conda清华镜像源...
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
    conda config --set show_channel_urls yes
)

:: 检查GPU
echo.
echo 🔍 检测GPU环境...
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 检测到NVIDIA GPU
    for /f "tokens=9" %%i in ('nvidia-smi ^| findstr "CUDA Version"') do set CUDA_VERSION=%%i
    echo    CUDA版本: !CUDA_VERSION!
    set HAS_GPU=1
) else (
    echo ⚠️  未检测到NVIDIA GPU
    echo 💡 强烈建议使用GPU设备以获得最佳性能
    echo.
    set /p CONTINUE="是否继续安装？(y/N): "
    if /i not "!CONTINUE!"=="y" goto end
    set HAS_GPU=0
)

:: 创建项目本地环境
echo.
echo 📦 创建项目本地环境 (Python 3.11)...
if exist "%PROJECT_DIR%env" (
    echo ⚠️  环境已存在，是否重新创建？
    set /p RECREATE="重新创建环境？(y/N): "
    if /i "!RECREATE!"=="y" (
        conda remove --prefix %PROJECT_DIR%env --all -y
        rmdir /s /q env
    ) else (
        echo ✅ 使用现有环境
        goto activate_env
    )
)

conda create --prefix %PROJECT_DIR%env python=3.11 numpy scipy pip -y
if %errorlevel% neq 0 (
    echo ❌ 环境创建失败
    goto end
)

:activate_env
:: 激活环境
echo 🔄 激活环境...
call conda activate %PROJECT_DIR%env

:: 配置pip镜像源
if "%USE_MIRROR%"=="1" (
    echo 🔧 配置pip清华镜像源...
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
)

:: 配置Hugging Face环境变量
if "%USE_HF_MIRROR%"=="1" (
    echo 🔧 配置Hugging Face镜像环境...
    set HF_ENDPOINT=https://hf-mirror.com
    setx HF_ENDPOINT "https://hf-mirror.com"
    echo    已设置 HF_ENDPOINT=https://hf-mirror.com
)

:: 安装PyTorch
echo.
if %HAS_GPU% equ 1 (
    echo 🚀 安装GPU版PyTorch (CUDA 12.1)...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
) else (
    echo 💻 安装CPU版PyTorch...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
)

if %errorlevel% neq 0 (
    echo ❌ PyTorch安装失败
    goto end
)

:: 验证PyTorch
echo 🧪 验证PyTorch安装...
python -c "import torch; print('✅ PyTorch版本:', torch.__version__); print('✅ CUDA可用:', torch.cuda.is_available())"

:: 安装AI和机器学习包
echo.
echo 📚 安装AI组件...
pip install openai openai-whisper transformers sentence-transformers

:: 安装音频处理包
echo 🎵 安装音频处理包...
pip install sounddevice soundfile edge-tts pygame

:: 安装向量检索和工具
echo 🔍 安装向量检索和工具...
pip install faiss-cpu keyboard

:: 验证安装
echo.
echo 🧪 验证组件安装...
python -c "import whisper; print('✅ OpenAI Whisper已安装')"
python -c "import faiss; print('✅ FAISS已安装')"
python -c "from sentence_transformers import SentenceTransformer; print('✅ sentence-transformers已安装')"
python -c "import sounddevice; print('✅ 音频设备支持已安装')"

:: 测试HF环境
if "%USE_HF_MIRROR%"=="1" (
    echo.
    echo 🔧 测试Hugging Face镜像配置...
    python -c "import os; print('HF_ENDPOINT:', os.environ.get('HF_ENDPOINT', '未设置'))"
)

:: 创建.gitignore
echo.
echo 📝 配置项目文件...
if not exist .gitignore echo. > .gitignore
findstr /C:"env/" .gitignore >nul || echo env/ >> .gitignore
findstr /C:"miniconda3/" .gitignore >nul || echo miniconda3/ >> .gitignore
findstr /C:"*.log" .gitignore >nul || echo *.log >> .gitignore
findstr /C:"__pycache__/" .gitignore >nul || echo __pycache__/ >> .gitignore

:: 创建激活脚本
echo @echo off > "%PROJECT_DIR%\activate.bat"
echo call "%PROJECT_DIR%\miniconda3\Scripts\activate.bat" >> "%PROJECT_DIR%\activate.bat"
echo call conda activate "%PROJECT_DIR%\env" >> "%PROJECT_DIR%\activate.bat"
echo echo ✅ Estia环境已激活！ >> "%PROJECT_DIR%\activate.bat"
echo echo 💡 现在可以运行: python main.py >> "%PROJECT_DIR%\activate.bat"
echo cmd /k >> "%PROJECT_DIR%\activate.bat"

echo.
echo ==========================================
echo 🎉 安装完成！
echo ==========================================
echo 📍 conda位置: %PROJECT_DIR%miniconda3
echo 📍 环境位置: %PROJECT_DIR%env
echo.
echo 💡 使用方法:
echo    start.bat            # 友好启动器（推荐）
echo    activate.bat         # 激活环境
echo    setup\activate.bat   # 从setup目录激活
echo.
echo 📝 下一步:
echo    1. 编辑 config/settings.py 设置DeepSeek API密钥
echo    2. 运行 start.bat 使用启动器
echo    3. 或运行 activate.bat 手动激活环境
echo.
echo 🗑️  完全卸载 (如需要):
echo    rmdir /s /q env
echo    rmdir /s /q miniconda3
echo ==========================================

:end
pause 