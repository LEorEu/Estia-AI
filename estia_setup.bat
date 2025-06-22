@echo off
setlocal enabledelayedexpansion

:: 设置项目目录
set PROJECT_DIR=%~dp0
cd /D %PROJECT_DIR%

:: Conda 环境名
set ENV_NAME=estia

:: 创建 Conda 环境（使用 TUNA 清华源）
echo Creating conda environment "%ENV_NAME%" with Python 3.11...
conda create -y -n %ENV_NAME% python=3.11 -c https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main

if %errorlevel% neq 0 (
    echo ❌ 环境创建失败，可能是网络问题或源未配置好。
    goto end
)

:: 激活环境
echo Activating conda environment...
call conda activate %ENV_NAME%

:: 设置临时代理（可选）
:: set HTTPS_PROXY=http://127.0.0.1:7890
:: set HTTP_PROXY=http://127.0.0.1:7890

:: 安装核心依赖
echo Installing estia dependencies...
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    numpy soundfile \
    edge-tts \
    pygame \
    openai-whisper \
    llama-cpp-python

if %errorlevel% neq 0 (
    echo ❌ pip 安装失败，请检查网络代理或 PyPI 镜像。
    goto end
)

echo ✅ 环境安装完成，可运行你的主程序：main.py
goto end

:end
pause
