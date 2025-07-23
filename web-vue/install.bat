@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Estia AI Web监控系统 - 快速安装
echo ========================================
echo.

REM 检查当前目录
if not exist "package.json" (
    echo ❌ 错误: 请在web-vue目录下运行此脚本
    pause
    exit /b 1
)

echo ✅ 找到package.json文件
echo.

REM 显示Node.js和npm版本
echo 📋 环境信息:
echo Node.js: 
node --version 2>nul || echo "未安装Node.js"
echo npm: 
npm --version 2>nul || echo "未安装npm"
echo.

REM 检查Node.js是否可用
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js不可用，请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

REM 检查npm是否可用  
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm不可用，请重新安装Node.js
    pause
    exit /b 1
)

echo 🚀 开始安装依赖包...
echo.

REM 清理旧的安装
if exist "node_modules" (
    echo 🧹 清理旧的node_modules目录...
    rmdir /s /q node_modules
)

if exist "package-lock.json" (
    echo 🧹 清理package-lock.json...
    del package-lock.json
)

echo.
echo 📦 执行 npm install...
echo (这可能需要几分钟时间，请耐心等待)
echo.

npm install

if %errorlevel% neq 0 (
    echo.
    echo ❌ 安装失败！
    echo.
    echo 🔧 可能的解决方案:
    echo 1. 检查网络连接
    echo 2. 使用国内镜像: npm config set registry https://registry.npmmirror.com/
    echo 3. 清理缓存: npm cache clean --force
    echo 4. 以管理员身份运行
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ 安装成功！
echo.

REM 创建环境配置文件
if not exist ".env.local" (
    echo 📝 创建环境配置文件...
    (
        echo # Estia AI 本地环境配置
        echo VITE_DEBUG=true
        echo VITE_APP_TITLE=Estia AI 监控仪表板
    ) > .env.local
    echo ✅ 已创建 .env.local 文件
    echo.
)

echo 🎉 安装完成！
echo.
echo 📋 使用方法:
echo   启动开发服务器: npm run dev
echo   构建生产版本:   npm run build
echo   预览构建结果:   npm run preview
echo.
echo 🌐 开发服务器将在 http://localhost:3000 启动
echo 🔗 API代理地址: http://localhost:5000
echo.

set /p start="是否立即启动开发服务器? (y/n): "
if /i "%start%"=="y" (
    echo.
    echo 🚀 启动开发服务器...
    echo 按 Ctrl+C 停止服务器
    echo.
    npm run dev
) else (
    echo.
    echo 💡 运行 'npm run dev' 启动开发服务器
)

echo.
pause