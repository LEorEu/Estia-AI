@echo off
chcp 65001 >nul

echo ==========================================
echo 🚀 Estia AI助手 - 启动器
echo ==========================================

:: 检查是否已安装环境
if not exist "env\" (
    echo ❌ 环境未安装！
    echo.
    echo 💡 请选择操作:
    echo    1. 安装环境 (推荐)
    echo    2. 退出
    echo.
    set /p CHOICE="请选择 (1 或 2): "
    
    if "!CHOICE!"=="1" (
        echo 🔧 正在启动安装程序...
        cd setup
        call install.bat
        cd ..
        echo.
        echo 📝 安装完成后请重新运行 start.bat
        pause
        exit /b 0
    ) else (
        echo 👋 再见！
        pause
        exit /b 0
    )
)

:: 检查miniconda
if not exist "miniconda3\" (
    echo ❌ Miniconda未安装！请运行 setup\install.bat
    pause
    exit /b 1
)

:: 初始化conda
call miniconda3\Scripts\activate.bat

:: 激活环境
call conda activate .\env

if %errorlevel% neq 0 (
    echo ❌ 环境激活失败！
    echo 💡 请运行 setup\install.bat 重新安装
    pause
    exit /b 1
)

echo ✅ 环境已激活！
echo.

:: 显示菜单
:menu
echo ==========================================
echo 🎯 选择运行模式:
echo    1. 文本模式 (测试对话)
echo    2. 语音模式 (完整体验)
echo    3. 环境检查
echo    4. 配置设置
echo    5. 退出
echo ==========================================
set /p MODE="请选择模式 (1-5): "

if "%MODE%"=="1" (
    echo 🔤 启动文本模式...
    python main.py --mode text
    goto menu
) else if "%MODE%"=="2" (
    echo 🎤 启动语音模式...
    python main.py --mode voice
    goto menu
) else if "%MODE%"=="3" (
    echo 🔍 检查环境...
    python setup\check_env.py
    pause
    goto menu
) else if "%MODE%"=="4" (
    echo ⚙️  打开配置目录...
    explorer config\
    echo 💡 请编辑 settings.py 设置API密钥
    pause
    goto menu
) else if "%MODE%"=="5" (
    echo 👋 再见！
    exit /b 0
) else (
    echo ❌ 无效选择，请重新选择
    goto menu
) 