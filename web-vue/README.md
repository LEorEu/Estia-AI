# Estia AI 监控仪表板 - Vue 3 版本

基于Vue 3 + TypeScript + Vite构建的现代化监控仪表板，提供实时系统监控、上下文查看、异步评估展示等功能。

## ✨ 特性

### 🎯 核心功能
- **实时系统监控** - WebSocket实时数据更新
- **性能指标可视化** - Chart.js图表展示
- **关键词分析** - 智能关键词提取和词云
- **会话管理** - 完整的会话历史记录

### 🚀 新增功能
- **上下文查看器** - 完整的对话上下文构建过程透明化
- **异步评估展示** - 监控异步评估过程和结果
- **15步流程可视化** - 实时监控记忆处理流程
- **系统健康监控** - 资源使用和性能趋势

### 🛠️ 技术特性
- **Vue 3 Composition API** - 现代化的组件开发
- **TypeScript** - 完整的类型安全
- **Tailwind CSS** - 快速响应式样式
- **Pinia** - 轻量级状态管理
- **Vite** - 快速构建和热重载

## 📦 技术栈

- **框架**: Vue 3.4+ 
- **构建工具**: Vite 5.0+
- **语言**: TypeScript 5.3+
- **状态管理**: Pinia 2.1+
- **路由**: Vue Router 4.2+
- **样式**: Tailwind CSS 3.4+
- **图表**: Chart.js 4.4+
- **实时通信**: Socket.IO Client 4.7+
- **HTTP客户端**: Axios 1.6+
- **日期处理**: date-fns 3.2+

## 🚀 快速开始

### 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0 或 yarn >= 1.22.0
- 现代浏览器支持 ES2020+

### 安装依赖

```bash
# 进入Vue项目目录
cd web-vue

# 安装依赖
npm install

# 或使用yarn
yarn install
```

### 开发环境

```bash
# 启动开发服务器
npm run dev

# 或使用yarn  
yarn dev
```

开发服务器将在 `http://localhost:3000` 启动。

### 生产构建

```bash
# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 🔧 配置说明

### 代理配置

项目已配置开发环境代理，自动将API请求转发到Flask后端：

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': 'http://localhost:5000',
    '/socket.io': {
      target: 'http://localhost:5000',
      ws: true
    }
  }
}
```

### 环境变量

创建 `.env.local` 文件配置环境变量：

```env
# API基础URL（可选，默认使用代理）
VITE_API_BASE_URL=http://localhost:5000

# 是否启用调试模式
VITE_DEBUG=true

# 应用标题
VITE_APP_TITLE=Estia AI 监控仪表板
```

## 📁 项目结构

```
web-vue/
├── public/                 # 静态资源
├── src/
│   ├── components/         # Vue组件
│   │   ├── cards/         # 卡片组件
│   │   ├── charts/        # 图表组件
│   │   ├── common/        # 通用组件
│   │   ├── data/          # 数据展示组件
│   │   └── layout/        # 布局组件
│   ├── stores/            # Pinia状态管理
│   ├── services/          # API服务
│   ├── utils/             # 工具函数
│   ├── types/             # TypeScript类型定义
│   ├── views/             # 页面视图
│   ├── router/            # 路由配置
│   └── style.css          # 全局样式
├── index.html             # HTML入口
├── vite.config.ts         # Vite配置
├── tailwind.config.js     # Tailwind配置
└── package.json           # 项目配置
```

## 🔌 API集成

### 数据获取策略

1. **实时数据优先**: 首先尝试获取实时数据
2. **仪表板数据降级**: 实时数据失败时使用仪表板数据
3. **测试数据兜底**: 最后使用测试数据保证系统可用

### WebSocket连接

- **自动重连**: 连接断开时自动重连（最多5次）
- **降级策略**: WebSocket失败时降级到HTTP轮询
- **错误处理**: 完善的错误通知和状态提示

## 🎨 UI组件

### 卡片组件
- `SystemStatusCard` - 系统状态卡片
- `PerformanceMetricsCard` - 性能指标卡片
- `ConnectionStatusCard` - 连接状态卡片
- `QuickActionsCard` - 快速操作卡片

### 图表组件
- `PerformanceChart` - 性能趋势图表
- `KeywordCloud` - 关键词云
- `PipelineVisualizer` - 流程可视化

### 数据组件
- `SessionList` - 会话列表
- `MemoryAnalysis` - 记忆分析
- `ContextViewer` - 上下文查看器

## 🔍 新功能详述

### 上下文查看器 (`/context`)

查看完整的对话上下文构建过程：
- 用户输入预处理
- 记忆检索结果
- 关联网络拓展
- 最终上下文结构

### 异步评估展示 (`/evaluation`)

监控异步评估过程：
- 评估触发条件
- 评估使用的上下文
- 评估结果详情
- 自动关联创建

### 15步流程可视化 (`/pipeline`)

实时监控记忆处理流程：
- 三阶段进度显示
- 步骤状态实时更新
- 性能指标监控
- 瓶颈识别

## 🧪 测试

```bash
# 运行单元测试
npm run test

# 运行测试并生成覆盖率报告
npm run test:coverage

# 运行端到端测试
npm run test:e2e
```

## 📝 开发指南

### 添加新组件

1. 在 `src/components/` 对应目录创建组件
2. 使用TypeScript和Composition API
3. 遵循命名约定：`PascalCase.vue`
4. 添加必要的类型定义

### 状态管理

使用Pinia进行状态管理：

```typescript
// 创建store
export const useMyStore = defineStore('myStore', () => {
  const state = ref(initialValue)
  
  const action = () => {
    // 业务逻辑
  }
  
  return { state, action }
})

// 在组件中使用
const myStore = useMyStore()
```

### API调用

使用统一的API服务：

```typescript
import { apiService } from '@/services/api'

// 调用API
const data = await apiService.getDashboardData()
```

## 🐛 故障排查

### 常见问题

**1. 依赖安装失败**
```bash
# 清除缓存重新安装
rm -rf node_modules package-lock.json
npm install
```

**2. 开发服务器启动失败**
```bash
# 检查端口占用
netstat -ano | findstr :3000

# 使用不同端口
npm run dev -- --port 3001
```

**3. API连接失败**
- 确保Flask后端服务运行在 `http://localhost:5000`
- 检查代理配置是否正确
- 查看浏览器控制台错误信息

**4. WebSocket连接失败**
- 检查防火墙设置
- 确认Socket.IO版本兼容性
- 查看网络标签页的WebSocket连接状态

### 调试模式

```bash
# 启用调试模式
VITE_DEBUG=true npm run dev
```

## 🚀 部署

### 构建优化

```bash
# 分析构建包大小
npm run build -- --mode analyze

# 构建时预渲染
npm run build -- --mode prerender
```

### 静态部署

构建完成后，`dist/` 目录包含所有静态文件，可以部署到：
- Nginx
- Apache
- Vercel
- Netlify
- GitHub Pages

### 服务端集成

将构建后的文件集成到Flask应用：

```python
# 在Flask应用中添加静态文件路由
@app.route('/')
@app.route('/<path:path>')
def serve_vue_app(path=''):
    return send_from_directory('dist', 'index.html')
```

## 📊 性能优化

- **代码分割**: 路由懒加载，减少初始包大小
- **缓存策略**: API响应缓存，减少重复请求  
- **虚拟滚动**: 大列表虚拟滚动，提升渲染性能
- **防抖节流**: 搜索、窗口调整等事件防抖节流

## 🔄 版本历史

- **v1.0.0** - Vue 3重构版本
  - 完整的TypeScript重写
  - 新增上下文查看器
  - 新增异步评估展示
  - 新增15步流程可视化

## 🤝 贡献指南

1. Fork项目到你的GitHub
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

如遇问题或需要帮助：

1. 查看[故障排查](#-故障排查)部分
2. 搜索[GitHub Issues](https://github.com/your-repo/issues)
3. 创建新的Issue描述问题

---

**开发团队**: Estia AI  
**最后更新**: 2025-01-23