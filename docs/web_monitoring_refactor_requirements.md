# Estia AI Web监控模块重构需求文档

## 📋 项目概述

**项目名称**: Estia AI Web监控模块增强重构  
**项目目标**: 增强web监控模块功能，提供更深入的系统运行状态可视化，帮助开发者更好地理解15步记忆处理流程和上下文构建过程  
**创建时间**: 2025-01-23  
**负责人**: 开发团队  

## 🎯 核心需求背景

### 当前痛点
1. **缺少上下文透明度**: 无法查看系统如何构建发送给LLM的完整上下文
2. **异步评估黑盒**: 无法了解异步评估的具体内容和结果
3. **流程可视化不足**: 15步记忆处理流程缺乏直观的实时监控
4. **系统健康状态模糊**: 缺少关键系统资源和性能指标的可视化

### 用户需求
- **开发者**: 需要深入了解系统内部工作机制，调试和优化性能
- **系统管理员**: 需要监控系统健康状态，预防潜在问题
- **研究人员**: 需要分析记忆系统的行为模式和效果

## 🏗️ 系统架构概述

### 现有系统基础
- **监控系统**: `core/memory/managers/monitor_flow/` - 完整的15步流程监控
- **Web框架**: `web/web_dashboard.py` - 基于Flask+SocketIO的实时仪表板
- **前端技术栈**: Chart.js + WebSocket + HTML5/CSS3
- **数据采集**: PipelineMonitor提供完整的步骤监控数据

### 15步记忆处理流程
```
Phase 1: 系统初始化 (Steps 1-3)
├── Step 1: 数据库初始化
├── Step 2: 组件初始化  
└── Step 3: 异步评估器初始化

Phase 2: 实时记忆增强 (Steps 4-9)
├── Step 4: 统一缓存向量化 (588x加速)
├── Step 5: FAISS向量检索 (<50ms)
├── Step 6: 关联网络拓展
├── Step 7: 历史对话聚合
├── Step 8: 权重排序去重
└── Step 9: 最终上下文构建

Phase 3: 对话存储与异步评估 (Steps 10-15)
├── Step 10: LLM响应生成
├── Step 11: 即时对话存储
├── Step 12: 异步LLM评估
├── Step 13: 保存评估结果
├── Step 14: 自动关联创建
└── Step 15: 过程监控清理
```

## 🎯 功能需求详述

### 🥇 优先级1: 本轮对话上下文查看器

#### 功能描述
提供完整的本轮对话上下文透明化展示，让用户清楚地看到系统如何构建发送给LLM的prompt。

#### 具体功能
1. **用户输入预处理展示**
   - 原始用户输入
   - 预处理后的查询文本
   - 提取的关键词和实体

2. **记忆检索结果详情** (Steps 4-6)
   - **统一缓存向量化**: 显示查询向量化结果
   - **FAISS检索结果**: 展示检索到的相关记忆列表
     - 记忆内容摘要
     - 相似度分数
     - 创建时间
     - 权重信息
   - **关联网络拓展**: 显示通过关联拓展获得的额外记忆
     - 一级关联记忆
     - 二级关联记忆
     - 关联强度指标

3. **历史对话聚合展示** (Step 7)
   - 相关历史对话片段
   - 对话时间和会话ID
   - 相关性评分

4. **最终上下文构建** (Step 9)
   - **完整上下文结构**:
     ```
     System Prompt: [系统提示词]
     
     Retrieved Memories: [检索到的记忆]
     - Memory 1: [内容] (相似度: 0.85)
     - Memory 2: [内容] (相似度: 0.78)
     
     Historical Context: [历史上下文]
     - Previous Exchange 1: [内容]
     - Previous Exchange 2: [内容]
     
     Current User Input: [当前用户输入]
     ```
   - 上下文长度统计
   - Token数量估算
   - 各部分内容占比

#### 技术实现
```python
# 新增API端点
@app.route('/api/session/<session_id>/context')
def get_session_context(session_id):
    """获取指定会话的完整上下文构建过程"""
    pass

@app.route('/api/current_context')  
def get_current_context():
    """获取当前正在构建的上下文"""
    pass
```

#### 界面设计
- **标签页布局**: 预处理 | 记忆检索 | 历史聚合 | 最终上下文
- **树形结构**: 显示上下文的层次结构
- **语法高亮**: 对prompt内容进行语法高亮
- **可折叠展开**: 长内容支持折叠/展开

### 🥈 优先级2: 异步评估上下文展示

#### 功能描述
透明化异步评估过程，显示评估使用的完整上下文和生成的结果。

#### 具体功能
1. **异步评估触发条件**
   - 评估触发的时机和条件
   - 评估队列状态
   - 评估优先级

2. **评估上下文构建** (Step 12)
   - **评估使用的完整上下文**:
     ```
     Evaluation Context:
     User Input: [用户输入]
     Assistant Response: [AI回复]
     Retrieved Memories: [相关记忆]
     Session Context: [会话上下文]
     
     Evaluation Prompt: [评估提示词]
     ```
   - 评估模型信息
   - 评估参数配置

3. **评估结果详情** (Step 13)
   - **记忆重要性评分**: 1-10分评分及理由
   - **情感分析结果**: 用户情感状态识别
   - **主题标签**: 自动生成的主题标签
   - **关联建议**: 系统建议的潜在关联
   - **知识提取**: 从对话中提取的关键信息

4. **自动关联创建** (Step 14)
   - 新创建的关联关系
   - 关联强度评分
   - 关联类型分类
   - 关联创建时间

#### 技术实现
```python
# 新增API端点
@app.route('/api/session/<session_id>/evaluation')
def get_session_evaluation(session_id):
    """获取指定会话的异步评估结果"""
    pass

@app.route('/api/evaluations/pending')
def get_pending_evaluations():
    """获取待处理的评估队列"""
    pass
```

#### 界面设计
- **评估timeline**: 时间轴显示评估过程
- **评分仪表盘**: 直观显示各项评分
- **关联图谱**: 可视化显示新创建的关联关系
- **对比视图**: 评估前后的状态对比

### 🥉 优先级3: 15步流程可视化MVP

#### 功能描述
提供直观的15步记忆处理流程实时监控，以简洁清晰的方式展示系统运行状态。

#### 具体功能
1. **流程状态总览**
   - **三阶段进度环形图**:
     ```
     ┌─────────────────┬──────────────────┬─────────────────┐
     │   初始化阶段      │    实时增强阶段     │   存储评估阶段    │
     │   (Steps 1-3)   │   (Steps 4-9)    │  (Steps 10-15)  │
     │      ●○○         │      ●●●○○○       │     ○○○○○○      │
     └─────────────────┴──────────────────┴─────────────────┘
     ```
   - **步骤状态指示器**: 每个步骤的实时状态（等待/执行中/完成/失败）
   - **当前执行步骤**: 高亮显示正在执行的步骤

2. **关键性能指标实时监控**
   - **系统性能卡片**:
     - QPS: 671.60 (超目标117%)
     - 平均响应时间: 1.49ms
     - 缓存加速倍数: 588x
     - 缓存命中率: 100%
   - **步骤耗时统计**: 每个步骤的平均耗时和当前耗时
   - **瓶颈识别**: 自动识别耗时最长的步骤

3. **实时状态更新**
   - WebSocket实时推送
   - 1秒更新频率
   - 状态变化动画效果

#### 技术实现
```javascript
// 流程可视化组件
class MemoryPipelineVisualizer {
    constructor(container) {
        this.container = container;
        this.stepStates = {};
        this.socket = io();
        this.initializeSocket();
    }
    
    initializeSocket() {
        this.socket.on('pipeline_status_update', (data) => {
            this.updatePipelineView(data);
        });
    }
    
    renderPipeline(stepData) {
        // 渲染15步流程图
    }
    
    updateStepStatus(stepId, status) {
        // 更新步骤状态
    }
}
```

#### 界面设计
- **横向流水线布局**: 15个步骤按顺序排列
- **颜色编码**: 不同状态使用不同颜色（灰色-等待，蓝色-执行中，绿色-完成，红色-失败）
- **进度动画**: 执行中的步骤显示进度条动画
- **悬停详情**: 鼠标悬停显示步骤详细信息

### 🏅 优先级4: 系统健康监控(可选)

#### 功能描述
提供系统资源使用和性能趋势的长期监控，帮助识别潜在问题。

#### 具体功能
1. **资源使用监控**
   - 内存使用率趋势图
   - CPU使用率监控
   - 数据库连接池状态
   - 缓存内存占用

2. **性能趋势分析**
   - 历史QPS趋势
   - 响应时间分布
   - 缓存命中率变化
   - 会话成功率统计

3. **告警和通知**
   - 性能异常自动检测
   - 资源使用率告警
   - 错误率超阈值提醒

## 🛠️ 技术实现方案

### 后端API扩展
在`web/web_dashboard.py`中新增以下API端点:

```python
# 上下文查看相关
@app.route('/api/session/<session_id>/context')
@app.route('/api/session/<session_id>/context/step/<step_id>')
@app.route('/api/current_context')

# 异步评估相关  
@app.route('/api/session/<session_id>/evaluation')
@app.route('/api/evaluations/pending')
@app.route('/api/evaluations/history')

# 流程监控相关
@app.route('/api/pipeline/status')
@app.route('/api/pipeline/metrics')
@app.route('/api/pipeline/step/<step_id>/details')

# 系统健康相关
@app.route('/api/system/health')
@app.route('/api/system/metrics/trend')
@app.route('/api/system/alerts')
```

### 前端组件架构
```
web/static/js/
├── components/
│   ├── ContextViewer.js         # 上下文查看器
│   ├── EvaluationPanel.js       # 异步评估面板
│   ├── PipelineVisualizer.js    # 流程可视化
│   └── HealthMonitor.js         # 健康监控
├── utils/
│   ├── api.js                   # API调用封装
│   ├── websocket.js             # WebSocket管理
│   └── formatters.js            # 数据格式化
└── main.js                      # 主应用入口
```

### 数据库扩展
可能需要在现有数据库中新增以下表结构:

```sql
-- 上下文快照表
CREATE TABLE context_snapshots (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    context_data TEXT NOT NULL,  -- JSON格式存储
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 评估结果详情表  
CREATE TABLE evaluation_details (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    evaluation_context TEXT NOT NULL,  -- JSON格式
    evaluation_results TEXT NOT NULL,  -- JSON格式
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📅 实施计划

### Phase 1: 基础准备 (1-2天)
- [ ] 完善需求文档和技术方案
- [ ] 搭建开发环境和测试数据
- [ ] 设计API接口规范

### Phase 2: 核心功能开发 (5-7天)
- [ ] **Week 1**: 实现上下文查看器 (2-3天)
  - 后端API开发
  - 前端组件实现
  - 数据采集和格式化
- [ ] **Week 1**: 实现异步评估展示 (2-3天)
  - 评估数据采集
  - 评估结果可视化
  - 关联关系图谱
- [ ] **Week 2**: 基础测试和优化 (1天)

### Phase 3: 流程可视化 (3-4天)
- [ ] **Week 2**: 实现15步流程可视化MVP (3-4天)
  - 流程图组件开发
  - 实时状态更新
  - 性能指标面板

### Phase 4: 系统完善 (2-3天)
- [ ] **Week 3**: 系统健康监控(可选) (2天)
- [ ] **Week 3**: 整体测试和文档 (1天)

### 总计开发时间: 11-16天

## 🎯 验收标准

### 功能验收
- [ ] 可以完整查看任意会话的上下文构建过程
- [ ] 可以查看异步评估的完整上下文和结果
- [ ] 实时显示15步流程执行状态
- [ ] 关键性能指标准确显示
- [ ] WebSocket实时更新正常工作

### 性能要求
- [ ] 页面加载时间 < 3秒
- [ ] 实时数据更新延迟 < 1秒  
- [ ] 支持并发10+ 用户访问
- [ ] 内存占用增长 < 50MB

### 用户体验
- [ ] 界面响应流畅，无明显卡顿
- [ ] 数据展示清晰，易于理解
- [ ] 支持主流浏览器(Chrome, Firefox, Safari)
- [ ] 移动端基础适配

## 🚨 风险评估与缓解

### 技术风险
| 风险项 | 影响程度 | 发生概率 | 缓解措施 |
|--------|----------|----------|----------|
| 实时数据量过大导致性能问题 | 高 | 中 | 数据分页、缓存策略、异步加载 |
| WebSocket连接不稳定 | 中 | 低 | 自动重连、降级到HTTP轮询 |
| 前端组件复杂度过高 | 中 | 中 | 模块化设计、渐进式开发 |
| 现有系统集成问题 | 高 | 低 | 详细的集成测试、向后兼容 |

### 项目风险
| 风险项 | 影响程度 | 发生概率 | 缓解措施 |
|--------|----------|----------|----------|
| 开发时间超期 | 中 | 中 | 分阶段交付、MVP优先 |
| 需求变更频繁 | 中 | 中 | 需求冻结、变更控制流程 |
| 测试不充分 | 高 | 中 | 制定详细测试计划、自动化测试 |

## 📖 相关文档

### 现有文档
- [CLAUDE.md](../CLAUDE.md) - 项目总体指南
- [core/memory架构文档](../core/memory/README.md)
- [监控系统文档](../core/memory/managers/monitor_flow/README.md)

### 新增文档(待创建)
- API接口文档
- 前端组件使用说明
- 部署和运维指南
- 故障排查手册

## 🔗 相关资源

### 技术参考
- [Chart.js官方文档](https://www.chartjs.org/docs/)
- [D3.js可视化库](https://d3js.org/)
- [Flask-SocketIO文档](https://flask-socketio.readthedocs.io/)
- [WebSocket最佳实践](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

### 设计参考
- [现有仪表板界面](../templates/dashboard.html)
- [监控系统界面设计模式](https://grafana.com/docs/)
- [实时数据可视化最佳实践](https://observablehq.com/@d3/real-time-data)

---

**文档状态**: 初稿完成  
**最后更新**: 2025-01-23  
**审核状态**: 待审核  
**批准状态**: 待批准  

---

*此文档将随着项目进展持续更新和完善。如有疑问或建议，请联系开发团队。*