@echo off
chcp 65001 >nul
echo.
echo 🔍 环境检测脚本
echo ================
echo.

echo 检查Node.js...
node --version
echo errorlevel = %errorlevel%
echo.

echo 检查npm...
npm --version  
echo errorlevel = %errorlevel%
echo.

echo 检查where命令...
where node
echo errorlevel = %errorlevel%
echo.

where npm
echo errorlevel = %errorlevel%
echo.

echo 检查package.json...
if exist "package.json" (
    echo ✅ 找到package.json
) else (
    echo ❌ 未找到package.json
)
echo.

echo 当前目录:
echo %CD%
echo.

pause