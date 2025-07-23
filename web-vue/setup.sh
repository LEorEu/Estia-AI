#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "================================================"
echo "      Estia AI Web监控系统 - Vue版本安装"
echo "================================================"
echo -e "${NC}"

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 错误: 未检测到Node.js${NC}"
    echo "请先安装Node.js (https://nodejs.org/)"
    echo "推荐版本: 18.0.0 或更高"
    exit 1
fi

echo -e "${GREEN}✅ Node.js版本:${NC}"
node --version
echo

# 检查npm是否可用
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ 错误: npm不可用${NC}"
    exit 1
fi

echo -e "${GREEN}✅ npm版本:${NC}"
npm --version
echo

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ 错误: 未找到package.json文件${NC}"
    echo "请确保在web-vue目录下运行此脚本"
    exit 1
fi

echo -e "${BLUE}🚀 开始安装依赖包...${NC}"
echo

# 清理可能存在的node_modules
if [ -d "node_modules" ]; then
    echo -e "${YELLOW}🧹 清理旧的node_modules...${NC}"
    rm -rf node_modules
fi

if [ -f "package-lock.json" ]; then
    echo -e "${YELLOW}🧹 清理package-lock.json...${NC}"
    rm -f package-lock.json
fi

echo
echo -e "${BLUE}📦 安装依赖包 (这可能需要几分钟)...${NC}"
npm install

if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}❌ 依赖包安装失败!${NC}"
    echo
    echo -e "${YELLOW}🔧 尝试解决方案:${NC}"
    echo "1. 检查网络连接"
    echo "2. 尝试使用淘宝镜像: npm config set registry https://registry.npmmirror.com/"
    echo "3. 清理npm缓存: npm cache clean --force"
    echo
    exit 1
fi

echo
echo -e "${GREEN}✅ 依赖包安装完成!${NC}"
echo

# 创建环境配置文件
if [ ! -f ".env.local" ]; then
    echo -e "${BLUE}📝 创建本地环境配置文件...${NC}"
    cat > .env.local << EOL
# Estia AI Web监控系统 - 本地环境配置

# API基础URL (可选，默认使用代理)
# VITE_API_BASE_URL=http://localhost:5000

# 是否启用调试模式
VITE_DEBUG=true

# 应用标题
VITE_APP_TITLE=Estia AI 监控仪表板

# 构建时间戳
VITE_BUILD_TIME=$(date)
EOL
    echo
    echo -e "${GREEN}✅ 环境配置文件已创建: .env.local${NC}"
fi

echo
echo -e "${GREEN}🎉 安装完成!${NC}"
echo
echo -e "${BLUE}📋 接下来的步骤:${NC}"
echo
echo "1. 启动开发服务器:"
echo "   npm run dev"
echo
echo "2. 构建生产版本:"
echo "   npm run build"
echo
echo "3. 预览生产构建:"
echo "   npm run preview"
echo
echo -e "${YELLOW}🌐 开发服务器地址: http://localhost:3000${NC}"
echo -e "${YELLOW}🔧 API代理地址: http://localhost:5000${NC}"
echo
echo -e "${BLUE}📚 更多信息请查看 README.md 文件${NC}"
echo

# 询问是否立即启动开发服务器
read -p "是否立即启动开发服务器? (y/n): " choice
case "$choice" in 
  y|Y ) 
    echo
    echo -e "${BLUE}🚀 启动开发服务器...${NC}"
    npm run dev
    ;;
  * ) 
    echo
    echo -e "${YELLOW}💡 提示: 运行 'npm run dev' 启动开发服务器${NC}"
    ;;
esac

echo