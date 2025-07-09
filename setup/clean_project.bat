@echo off
chcp 65001 >nul

echo ==========================================
echo 🧹 Estia AI助手 - 项目清理工具
echo    清理运行时数据和缓存文件
echo ==========================================

:: 设置项目根目录
set PROJECT_DIR=%~dp0..
cd /D %PROJECT_DIR%

echo 📊 分析当前项目状态...
echo.

:: 计算各目录大小
if exist "data\" (
    for /f %%A in ('dir /s "data\" ^| find "个文件"') do set DATA_FILES=%%A
    echo 📁 data/ 目录: 包含运行时数据和缓存
)

if exist "assets\*.db" (
    echo 📁 assets/ 目录: 包含数据库文件
)

if exist "logs\" (
    echo 📁 logs/ 目录: 包含日志文件
)

if exist "temp\" (
    echo 📁 temp/ 目录: 包含临时文件
)

echo.
echo ⚠️  以下数据将被清理:
echo    🗑️  data/ - 所有缓存和向量数据
echo    🗑️  assets/*.db - 数据库文件
echo    🗑️  logs/ - 日志文件
echo    🗑️  temp/ - 临时文件
echo    🗑️  __pycache__/ - Python缓存
echo.
echo 💡 这些数据在程序运行时会重新生成
echo    但第一次运行会需要重新下载模型

set /p CONFIRM="确认清理项目数据？(y/N): "
if /i not "%CONFIRM%"=="y" (
    echo 取消清理
    pause
    exit /b 0
)

echo.
echo 🚀 开始清理项目...

:: 清理运行时数据
if exist "data\" (
    echo 🗑️  清理 data/ 目录...
    rmdir /s /q "data\" 2>nul
    if %errorlevel% equ 0 (
        echo    ✅ data/ 清理完成
    ) else (
        echo    ⚠️  data/ 部分文件可能正在使用
    )
)

:: 清理数据库文件
echo 🗑️  清理数据库文件...
if exist "assets\*.db" (
    del /q "assets\*.db" 2>nul
    echo    ✅ 数据库文件清理完成
)

:: 清理日志
if exist "logs\" (
    echo 🗑️  清理日志文件...
    rmdir /s /q "logs\" 2>nul
    echo    ✅ 日志文件清理完成
)

:: 清理临时文件
if exist "temp\" (
    echo 🗑️  清理临时文件...
    rmdir /s /q "temp\" 2>nul
    echo    ✅ 临时文件清理完成
)

:: 清理Python缓存
echo 🗑️  清理Python缓存...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
del /s /q "*.pyc" 2>nul
del /s /q "*.pyo" 2>nul
echo    ✅ Python缓存清理完成

:: 清理其他缓存文件
echo 🗑️  清理其他缓存...
if exist "*.log" del /q "*.log" 2>nul
if exist "*.tmp" del /q "*.tmp" 2>nul
if exist "*.temp" del /q "*.temp" 2>nul

echo.
echo ==========================================
echo ✅ 项目清理完成！
echo ==========================================
echo 📊 清理结果:
echo    🗑️  运行时数据已清除
echo    🗑️  缓存文件已清除
echo    🗑️  日志文件已清除
echo    🗑️  临时文件已清除
echo.
echo 💡 注意事项:
echo    - 环境和代码文件保持完整
echo    - 首次运行会重新初始化数据
echo    - 模型文件需要重新下载
echo.
echo 🚀 现在可以:
echo    1. 运行 start.bat 启动程序
echo    2. 或运行 python main.py 开始使用
echo ==========================================

pause 