# 🚀 Estia AI 一体化监控仪表板

## 概述

Estia AI 现在包含了完整的一体化监控系统，将Vue.js前端和Flask后端完美集成，提供强大的性能监控和告警管理功能。

## ✨ 主要特性

### 🔍 实时性能监控
- **系统资源监控**: CPU、内存、磁盘使用率
- **应用性能监控**: 查询响应时间、QPS、缓存命中率
- **记忆系统监控**: 活跃会话、记忆数量、向量检索性能

### 🚨 智能告警系统
- **多级告警**: 严重/警告/信息三级告警
- **实时检测**: 基于阈值的自动告警触发
- **告警管理**: 确认、解决、历史记录管理
- **预设规则**: CPU、内存、缓存、错误率等预设告警规则

### 📊 系统健康评分
- **综合评分**: 0-100分的系统健康评分
- **问题诊断**: 自动识别系统问题和瓶颈
- **优化建议**: 基于监控数据的智能优化建议

### 🌐 一体化部署
- **单端口服务**: Vue前端和Flask后端统一在5000端口
- **无需分离部署**: 前端静态文件自动集成到Flask应用
- **开箱即用**: 一个命令启动完整的监控服务

## 🚀 快速启动

### 方法1：使用启动脚本（推荐）
```bash
# Windows
start_monitoring.bat

# Linux/macOS
chmod +x start_monitoring.sh && ./start_monitoring.sh
```

### 方法2：手动启动
```bash
# 1. 确保Vue前端已构建
cd web-vue
npm install
npm run build
cd ..

# 2. 启动一体化服务
python start_dashboard.py
```

### 访问仪表板
启动后访问: **http://localhost:5000**

## 📡 API端点

### 基础API
- `GET /api/status` - 系统状态
- `GET /api/dashboard_data` - 仪表板综合数据
- `GET /api/performance` - 性能统计

### 增强监控API
- `GET /api/monitoring/status` - 监控系统状态
- `GET /api/monitoring/metrics/current` - 当前性能指标
- `GET /api/monitoring/metrics/history` - 历史指标数据
- `GET /api/monitoring/alerts` - 活跃告警列表
- `POST /api/monitoring/alerts/{id}/acknowledge` - 确认告警
- `GET /api/monitoring/health` - 系统健康状态
- `GET /api/monitoring/comprehensive` - 综合监控报告

## 🔧 配置说明

### 告警阈值配置
告警阈值可以在 `core/monitoring/alert_manager.py` 中的 `_initialize_default_rules()` 方法中调整：

```python
# 示例配置
AlertRule(
    rule_id="cpu_high",
    name="CPU使用率过高",
    metric_name="cpu_usage",
    condition="gt",
    threshold=80.0,  # 调整此值
    severity=AlertSeverity.WARNING
)
```

### 监控间隔配置
在 `core/monitoring/performance_monitor.py` 中调整：

```python
# 监控数据收集间隔（秒）
collection_interval = 5.0
```

## 🧪 测试和验证

### 集成测试
```bash
# 测试所有组件是否正常
python test_monitoring_integration.py

# 测试一体化服务（需要先启动服务）
python test_integrated_dashboard.py
```

### 手动测试
1. 启动服务：`python start_dashboard.py`
2. 访问主界面：http://localhost:5000
3. 检查各个监控卡片是否显示数据
4. 测试告警确认功能
5. 查看系统健康评分

## 📊 前端组件说明

### 核心监控组件
- **SystemHealthCard**: 系统健康状态和评分
- **AlertsManagementCard**: 告警管理界面
- **PerformanceMetricsCard**: 增强的性能指标展示
- **SystemStatusCard**: 基础系统状态
- **ConnectionStatusCard**: 连接状态监控

### 页面路由
- `/` - 主仪表板（包含所有监控卡片）
- `/dashboard` - 仪表板别名
- `/context` - 上下文查看器
- `/pipeline` - 流程监控器
- `/evaluation` - 评估查看器

## 🛠️ 开发和扩展

### 添加新的监控指标
1. 在 `MetricsCollector` 中添加指标收集逻辑
2. 在 `PerformanceMonitor` 中添加指标处理
3. 在前端组件中添加指标显示

### 添加新的告警规则
1. 在 `AlertManager._initialize_default_rules()` 中添加规则
2. 可选：在前端添加规则管理界面

### 自定义前端组件
1. 在 `web-vue/src/components/` 中创建新组件
2. 在相应的页面中引入和使用
3. 重新构建：`cd web-vue && npm run build`

## 🐛 故障排除

### 常见问题

**1. 服务启动失败**
- 检查端口5000是否被占用
- 确认Python依赖已安装：`pip install flask flask-socketio psutil`
- 查看详细错误信息

**2. Vue前端不显示**
- 确认Vue前端已构建：`cd web-vue && npm run build`
- 检查 `web-vue/dist/` 目录是否存在且包含文件
- 查看浏览器控制台是否有错误

**3. 监控数据不更新**
- 检查监控系统是否初始化成功
- 查看服务器日志中的错误信息
- 确认 `psutil` 包已安装用于系统监控

**4. 告警不触发**
- 检查告警规则配置是否正确
- 确认指标数据正常收集
- 查看告警管理器的日志输出

### 日志查看
服务运行时会在控制台输出详细日志，包括：
- 监控系统初始化状态
- API请求处理情况
- 告警触发和处理
- 系统性能指标

## 📈 性能优化建议

1. **生产环境部署**：设置 `debug=False` 并使用生产级WSGI服务器
2. **数据库优化**：为监控数据创建适当的索引
3. **缓存策略**：利用Redis等缓存系统优化数据访问
4. **负载均衡**：在高负载环境下使用负载均衡器

## 🤝 贡献指南

欢迎提交问题报告和功能请求！在开发新功能时，请：

1. 遵循现有的代码结构和命名规范
2. 添加适当的错误处理和日志记录
3. 更新相关文档和测试
4. 确保前后端数据格式兼容

---

**🎉 享受强大的Estia AI监控体验！**