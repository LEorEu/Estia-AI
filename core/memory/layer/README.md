# 分层记忆系统 (Layered Memory System)

## 概述

分层记忆系统是 Estia 记忆管理的增强模块，提供智能的记忆分层与优先级管理功能。该系统与现有记忆系统完全兼容，采用零破坏性设计，可以无缝集成到现有架构中。

## 核心特性

### 🎯 四层记忆架构
- **核心记忆 (Core)**: 权重 9.0-10.0，永久保留的重要信息
- **归档记忆 (Archive)**: 权重 7.0-8.9，长期保留的历史精华
- **长期记忆 (Long-term)**: 权重 4.0-6.9，定期清理的一般信息
- **短期记忆 (Short-term)**: 权重 1.0-3.9，快速过期的临时信息

### 🔄 双向同步机制
- 权重变化自动更新分层
- 分层调整自动同步权重
- 批量同步现有记忆
- 一致性验证与修复

### 🤖 智能生命周期管理
- 自动清理过期记忆
- 智能提升高价值记忆
- 动态平衡各层级容量
- 可配置的保留策略

### 🚀 检索性能优化
- 分层优先级检索
- 智能层级选择
- 上下文感知过滤
- 访问模式学习

### 📊 全面监控统计
- 实时系统指标
- 层级健康状态
- 容量告警机制
- 性能分析报告

## 快速开始

### 1. 基本集成

```python
from estia.core.memory.layer import initialize_layered_memory_system

# 初始化分层系统
integration = await initialize_layered_memory_system(
    db_manager=your_db_manager,
    vectorizer=your_vectorizer  # 可选
)

if integration:
    print("分层记忆系统初始化成功")
else:
    print("初始化失败")
```

### 2. 增强现有记忆操作

```python
# 存储记忆时自动分层
memory_data = {
    'id': 'memory_123',
    'content': '用户喜欢喝咖啡',
    'weight': 8.5,
    'type': 'preference'
}

# 系统会自动将其分配到归档层级
enhanced_data = integration.enhance_memory_storage(memory_data)
print(f"分配到层级: {enhanced_data['layer_info']['layer']}")

# 检索时使用分层优化
memory_ids = ['memory_123', 'memory_456', 'memory_789']
enhanced_memories = integration.enhance_memory_retrieval(
    memory_ids=memory_ids,
    query_context={'user_input': '我喜欢什么饮料？'}
)

# 构建层级感知的上下文
layered_context = integration.enhance_context_building(
    user_input="告诉我关于咖啡的信息",
    context_memories=enhanced_memories
)
```

### 3. 系统监控

```python
# 获取系统状态
status = integration.get_system_status()
print(f"总记忆数: {status['system_metrics'].total_memories}")
print(f"同步状态: {status['system_metrics'].sync_status}")

# 检查层级健康状态
for layer, health in status['health_status'].items():
    print(f"{layer}: {health}")

# 查看容量告警
for alert in status['capacity_alerts']:
    print(f"{alert['level']}: {alert['message']}")
```

### 4. 手动维护

```python
# 运行系统维护
maintenance_result = await integration.run_maintenance()
if maintenance_result['success']:
    print("维护完成")
    print(f"清理记忆: {maintenance_result['maintenance']['cleaned_count']}")
    print(f"提升记忆: {maintenance_result['maintenance']['promoted_count']}")
```

## 高级配置

### 自定义层级配置

```python
from estia.core.memory.layer import LayerConfigManager, LayerSystemConfig, LayerConfig, MemoryLayer

# 创建自定义配置
custom_config = LayerSystemConfig(
    auto_sync_enabled=True,
    sync_interval_hours=12,
    auto_maintenance_enabled=True,
    maintenance_interval_hours=3,
    default_max_per_layer=100
)

# 自定义层级配置
custom_config.layer_configs[MemoryLayer.CORE] = LayerConfig(
    max_memories=2000,  # 增加核心记忆容量
    cleanup_interval_hours=336,  # 14天清理一次
    retention_days=730,  # 保留2年
    weight_threshold=9.5  # 提高权重阈值
)

# 使用自定义配置
config_manager = LayerConfigManager(custom_config)
integration = LayeredMemoryIntegration(
    db_manager=your_db_manager,
    config_manager=config_manager
)
```

### 配置导入导出

```python
# 导出配置
config_dict = config_manager.export_config()
with open('layer_config.json', 'w') as f:
    json.dump(config_dict, f, indent=2)

# 导入配置
with open('layer_config.json', 'r') as f:
    config_dict = json.load(f)
config_manager.import_config(config_dict)
```

## 独立使用组件

### 分层管理器

```python
from estia.core.memory.layer import LayeredMemoryManager

layer_manager = LayeredMemoryManager(db_manager)

# 手动分配层级
layer_info = layer_manager.assign_layer('memory_123', weight=8.5)
print(f"分配到: {layer_info.layer.value}")

# 获取层级信息
info = layer_manager.get_layer_info('memory_123')
print(f"当前层级: {info.layer.value}, 权重: {info.weight}")

# 获取指定层级的记忆
core_memories = layer_manager.get_memories_by_layer(MemoryLayer.CORE, limit=50)
```

### 生命周期管理

```python
from estia.core.memory.layer import MemoryLifecycleManager

lifecycle_manager = MemoryLifecycleManager(layer_manager, config_manager)

# 清理过期记忆
cleanup_result = await lifecycle_manager.cleanup_expired_memories()
print(f"清理了 {cleanup_result['cleaned_count']} 条记忆")

# 提升高价值记忆
promotion_result = await lifecycle_manager.promote_memories()
print(f"提升了 {promotion_result['promoted_count']} 条记忆")
```

### 权重同步

```python
from estia.core.memory.layer import WeightLayerSynchronizer

synchronizer = WeightLayerSynchronizer(layer_manager)

# 同步所有记忆
sync_result = await synchronizer.sync_all_memories()
print(f"同步了 {sync_result['synced_count']} 条记忆")

# 验证同步一致性
consistency_result = await synchronizer.verify_consistency()
if consistency_result['inconsistent_count'] > 0:
    print(f"发现 {consistency_result['inconsistent_count']} 条不一致记忆")
    # 修复不一致
    fix_result = await synchronizer.fix_inconsistencies()
    print(f"修复了 {fix_result['fixed_count']} 条记忆")
```

### 检索增强

```python
from estia.core.memory.layer import LayeredRetrievalEnhancer

retrieval_enhancer = LayeredRetrievalEnhancer(layer_manager)

# 智能层级选择
layers = retrieval_enhancer.smart_layer_selection('personal_info')
print(f"推荐层级: {[layer.value for layer in layers]}")

# 按层级过滤
filtered_ids = retrieval_enhancer.filter_by_layer(
    memory_ids=['mem1', 'mem2', 'mem3'],
    allowed_layers=[MemoryLayer.CORE, MemoryLayer.ARCHIVE]
)
```

### 系统监控

```python
from estia.core.memory.layer import LayerMonitor

monitor = LayerMonitor(layer_manager, config_manager)

# 获取详细性能报告
report = monitor.get_performance_report()
print(f"系统健康分数: {report['overall_health_score']}")
print(f"建议: {report['recommendations']}")

# 获取容量告警
alerts = monitor.get_capacity_alerts()
for alert in alerts:
    print(f"{alert['level']}: {alert['message']}")
```

## 最佳实践

### 1. 渐进式集成
```python
# 第一步：初始化系统但不启用自动功能
config = LayerSystemConfig(
    auto_sync_enabled=False,
    auto_maintenance_enabled=False
)

# 第二步：手动测试各项功能
# 第三步：逐步启用自动功能
```

### 2. 监控驱动优化
```python
# 定期检查系统状态
async def health_check():
    status = integration.get_system_status()
    
    # 检查容量使用率
    for layer, metrics in status['system_metrics'].layer_metrics.items():
        if metrics.capacity_usage > 0.8:
            print(f"警告: {layer.value} 层级容量使用率过高")
    
    # 检查同步状态
    if status['system_metrics'].sync_status != 'synced':
        print("需要执行同步操作")
        await integration.run_maintenance()
```

### 3. 配置调优
```python
# 根据实际使用情况调整配置
config_manager = get_config_manager()

# 如果核心记忆增长过快，提高权重阈值
core_config = config_manager.get_layer_config(MemoryLayer.CORE)
if core_config.max_memories < current_core_count:
    core_config.weight_threshold = 9.5  # 提高阈值
    config_manager.update_layer_config(MemoryLayer.CORE, core_config)
```

## 故障排除

### 常见问题

1. **初始化失败**
   - 检查数据库连接
   - 确认权限设置
   - 查看日志错误信息

2. **同步不一致**
   ```python
   # 强制重新同步
   sync_result = await synchronizer.sync_all_memories(force=True)
   ```

3. **性能问题**
   ```python
   # 检查系统指标
   metrics = monitor.get_system_metrics()
   if metrics.performance_stats['db_query_time_ms'] > 100:
       print("数据库查询性能较慢")
   ```

4. **容量告警**
   ```python
   # 手动清理
   cleanup_result = await lifecycle_manager.cleanup_expired_memories()
   
   # 或调整容量限制
   config = config_manager.get_layer_config(MemoryLayer.SHORT_TERM)
   config.max_memories *= 2
   config_manager.update_layer_config(MemoryLayer.SHORT_TERM, config)
   ```

## 架构说明

```
分层记忆系统架构
├── types.py           # 核心类型定义
├── manager.py         # 分层管理器
├── lifecycle.py       # 生命周期管理
├── sync.py           # 权重同步器
├── retrieval.py      # 检索增强器
├── config.py         # 配置管理
├── monitoring.py     # 监控系统
└── integration.py    # 集成模块
```

## 版本信息

- **版本**: 1.0.0
- **作者**: Estia Memory Team
- **描述**: Intelligent Memory Layering and Priority Management System

## 许可证

本模块遵循 Estia 项目的许可证协议。