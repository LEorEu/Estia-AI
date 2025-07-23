@echo off
chcp 65001 >nul
echo.
echo ================================================
echo      Estia AI Web监控系统 - Vue版本安装
echo ================================================
echo.

REM 检查Node.js是否安装
echo 🔍 检查Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未检测到Node.js
    echo 请先安装Node.js (https://nodejs.org/)
    echo 推荐版本: 18.0.0 或更高
    pause
    exit /b 1
)

REM 获取Node.js版本
for /f "delims=" %%i in ('node --version 2^>nul') do set NODE_VERSION=%%i
if "%NODE_VERSION%"=="" (
    echo ❌ 错误: 无法获取Node.js版本
    pause
    exit /b 1
)

echo ✅ Node.js版本: %NODE_VERSION%

REM 检查Node.js版本是否符合要求 (v18.0.0+)
set NODE_MAJOR=%NODE_VERSION:~1,2%
if %NODE_MAJOR% LSS 18 (
    echo ⚠️  警告: Node.js版本较低 (%NODE_VERSION%)
    echo 推荐版本: 18.0.0 或更高
    echo 是否继续安装? (某些功能可能无法正常工作)
    pause
)
echo.

REM 检查npm是否可用
echo 🔍 检查npm...
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: npm不可用
    echo npm通常与Node.js一起安装，请重新安装Node.js
    pause
    exit /b 1
)

REM 获取npm版本
for /f "delims=" %%i in ('npm --version 2^>nul') do set NPM_VERSION=%%i
if "%NPM_VERSION%"=="" (
    echo ❌ 错误: 无法获取npm版本
    pause
    exit /b 1
)

echo ✅ npm版本: %NPM_VERSION%
echo.

REM 检查是否在正确的目录
if not exist "package.json" (
    echo ❌ 错误: 未找到package.json文件
    echo 请确保在web-vue目录下运行此脚本
    pause
    exit /b 1
)

echo 🚀 开始安装依赖包...
echo.

REM 清理可能存在的node_modules
if exist "node_modules" (
    echo 🧹 清理旧的node_modules...
    rmdir /s /q node_modules
)

if exist "package-lock.json" (
    echo 🧹 清理package-lock.json...
    del package-lock.json
)

echo.
echo 📦 安装依赖包 (这可能需要几分钟)...
npm install

if %errorlevel% neq 0 (
    echo.
    echo ❌ 依赖包安装失败!
    echo.
    echo 🔧 尝试解决方案:
    echo 1. 检查网络连接
    echo 2. 尝试使用淘宝镜像: npm config set registry https://registry.npmmirror.com/
    echo 3. 清理npm缓存: npm cache clean --force
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ 依赖包安装完成!
echo.

REM 创建环境配置文件
if not exist ".env.local" (
    echo 📝 创建本地环境配置文件...
    echo # Estia AI Web监控系统 - 本地环境配置 > .env.local
    echo. >> .env.local
    echo # API基础URL (可选，默认使用代理) >> .env.local
    echo # VITE_API_BASE_URL=http://localhost:5000 >> .env.local
    echo. >> .env.local
    echo # 是否启用调试模式 >> .env.local
    echo VITE_DEBUG=true >> .env.local
    echo. >> .env.local
    echo # 应用标题 >> .env.local
    echo VITE_APP_TITLE=Estia AI 监控仪表板 >> .env.local
    echo. >> .env.local
    echo # 构建时间戳 >> .env.local
    echo VITE_BUILD_TIME=%date% %time% >> .env.local
    echo.
    echo ✅ 环境配置文件已创建: .env.local
)

echo.
echo 🎉 安装完成!
echo.
echo 📋 接下来的步骤:
echo.
echo 1. 启动开发服务器:
echo    npm run dev
echo.
echo 2. 构建生产版本:
echo    npm run build
echo.
echo 3. 预览生产构建:
echo    npm run preview
echo.
echo 🌐 开发服务器地址: http://localhost:3000
echo 🔧 API代理地址: http://localhost:5000
echo.
echo 📚 更多信息请查看 README.md 文件
echo.

REM 询问是否立即启动开发服务器
set /p choice="是否立即启动开发服务器? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo 🚀 启动开发服务器...
    npm run dev
) else (
    echo.
    echo 💡 提示: 运行 'npm run dev' 启动开发服务器
)

echo.
pause