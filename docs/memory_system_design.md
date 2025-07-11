# 📆 Estia 记忆系统工作流程规范（增强版）

本规范文档详细描述 Estia 的记忆模块核心流程，结合数据表字段定义、对话运行场景与语义检索过程，支持模拟人类联想、主题聚合与长期记忆。

---

## 数据表概览

### `memories`（记忆主表）
| 字段 | 含义 |
|--------|------|
| `id` | 唯一记忆 ID，如 mem_001 |
| `content` | 实际内容（用户输入 / 助手回复 / 综合分析等） |
| `type` | user_input / assistant_reply / summary / emotion / intent |
| `role` | user / assistant / system |
| `session_id` | 对话块 ID，用于表示纯时序连续性 |
| `timestamp` | 时间戳 |
| `weight` | 记忆重要程度（LLM 评估结果，0-10） |
| `group_id` | 所属话题分组（时间 + 主题分组） |
| `summary` | 该记忆单独摘要，用于加速检索 / 省token |
| `last_accessed` | 最后访问时间戳，用于缓存管理 |

**索引：**
- `CREATE INDEX idx_memories_session ON memories(session_id);`
- `CREATE INDEX idx_memories_group ON memories(group_id);`
- `CREATE INDEX idx_memories_timestamp ON memories(timestamp);`
- `CREATE INDEX idx_memories_type ON memories(type);`
- `CREATE INDEX idx_memories_last_accessed ON memories(last_accessed);`

---

### `memory_vectors`（向量存储表）
| 字段 | 含义 |
|--------|------|
| `id` | 唯一向量 ID |
| `memory_id` | 对应记忆 ID（memories.id） |
| `vector` | 二进制向量数据（BLOB） |
| `model_name` | 使用的嵌入模型名称 |
| `timestamp` | 创建时间戳 |

**索引：**
- `CREATE INDEX idx_memory_vectors_memory_id ON memory_vectors(memory_id);`

---

### `memory_association`（记忆关联表）
| 字段 | 含义 |
|--------|------|
| `id` | 唯一关联 ID，如 mem001_mem002_summarizes |
| `source_key` | 起点记忆 ID（memories.id） |
| `target_key` | 终点记忆 ID（memories.id） |
| `association_type` | is_related_to / summarizes / contradicts / causes / precedes / elaborates / same_topic |
| `strength` | 0~1程度，用于控制联情综合排序或强弱 |
| `created_at` | 创建时间戳 |
| `last_activated` | 最后激活时间戳，用于消耗时间统计 |
| `group_id` | 所属分组 ID |
| `super_group` | 主题分组（如 work_stress） |

**索引：**
- `CREATE INDEX idx_memory_association_source ON memory_association(source_key);`
- `CREATE INDEX idx_memory_association_target ON memory_association(target_key);`
- `CREATE INDEX idx_memory_association_group ON memory_association(group_id);`

---

### `memory_group`（话题分组表）
| 字段 | 含义 |
|--------|------|
| `group_id` | 唯一分组 ID（如 work_stress_2025_06_27） |
| `super_group` | 所属主题（如 work_stress） |
| `topic` | 手写或模型生成的简要话题描述 |
| `time_start` / `time_end` | 记录这个话题的时间范围 |
| `summary` | 为这组记忆手写的摘要，通常由 LLM 后端生成 |
| `score` | 这组记忆在全年体记忆中的重要程度 |

**索引：**
- `CREATE INDEX idx_memory_group_super ON memory_group(super_group);`

---

### `memory_cache`（记忆缓存表）
| 字段 | 含义 |
|--------|------|
| `id` | 唯一缓存 ID |
| `memory_id` | 对应记忆 ID（memories.id） |
| `cache_level` | 缓存级别（hot/warm） |
| `priority` | 缓存优先级（0-10） |
| `access_count` | 访问计数 |
| `last_accessed` | 最后访问时间戳 |

**索引：**
- `CREATE INDEX idx_memory_cache_level ON memory_cache(cache_level);`
- `CREATE INDEX idx_memory_cache_priority ON memory_cache(priority);`

---

## 🌐 运行流程示意：以用户提出"你怎么看待我今天没有摸鱼而是一直工作？"为例

### Step 1：初始化向量索引和数据库
- 启动时加载 FAISS 索引
- 连接 SQLite 数据库
- 初始化缓存系统

### Step 2：用户语音输入转文本
- 通过 Whisper 模型将语音转换为文本

### Step 3：嵌入模型向量化文本
- 对当前输入 `content="你怎么看待我今天没有摸鱼而是一直工作？"` 进行 embedding
- 检查缓存是否已有该句 embedding，若无则生成并缓存（避免重复计算）
- 向量化结果存入 `memory_vectors` 表

### Step 4：FAISS 检索最相关记忆
- 查询 embedding，取出 K 条相似度最高的向量（长文本自动分段索引）
- 如果 `memory_cache` 中已有此向量对应 ID → 直接从 cache 命中内容（避免 DB 查询）
- 根据优先级和访问频率决定缓存策略

### Step 5：关联网络拓展
- 使用 `association_type='is_related_to' or 'same_topic'` 进行自动联想
- 检索路径支持 `depth=2`（当前 → 相关 → 再相关）
- 每条关联通过 `strength` 加权排序 → 综合评分融合

### Step 6：从数据库或缓存中取出对话
- 拿到 top-K memory ID 后：
  - 检查 `group_id` 是否一致
  - 如果一致：根据 `session_id` 聚合出历史连续对话
  - 提取该 session 下的 `type=summary` 内容补入总结

📌 示例数据：
```
id       | content                         | type             | session_id           | timestamp
---------|----------------------------------|------------------|----------------------|---------------------
mem001   | 我今天上班真的好累……              | user_input       | sess_20250627_001    | 2025-06-27 00:50
mem002   | 怎么了？想和我聊聊吗？             | assistant_reply  | sess_20250627_001    | 2025-06-27 00:51
mem003   | 用户因工作压力感到疲惫，情绪低落。   | summary          | sess_20250627_001    | 2025-06-27 00:52
```

### Step 7：权重优先排序 + 去重
- 对所有 memory:
  - score = weight + embedding 相似度 + 是否为 summary（+2） + 是否最近访问（+1）
  - 去重（按内容）后排序，保留最关键的前 N 条

### Step 8：组装最终上下文
- 拼装 prompt：
```text
[角色设定（人格等）]
[核心记忆（如用户长期工作压力）]
[重要历史/group 总结]
[你刚才说的话（如"今天很累"）]
[用户输入：你怎么看待我今天没有摸鱼？]
```

### Step 9：传入本地 LLM 生成回复
- 根据上下文 token 长度调整 `max_tokens`
- 提供角色设定 + 历史摘要 + 当前话题，形成自然连续回复

### Step 10：异步请求 LLM 进行：
- 当前对话段 `summary`
- 当前输入和回复 `weight` 评估（重要程度）
- 自动 topic / super_group 提取

### Step 11：得到总结与评估结果
```json
{
  "summary": "用户今日工作状态专注，表达成就感和疲惫感混合情绪",
  "weight": 7.5,
  "group_id": "work_stress_2025_06_28",
  "super_group": "work_stress"
}
```

### Step 12：保存对话 + 总结到 memories 表
- 使用事务确保数据一致性
- 插入：
  - `type='user_input'`, `type='assistant_reply'`, `type='summary'`
  - 统一绑定 `session_id` + 自动生成 `group_id`
  - 写入 `weight` + `summary` 字段

### Step 13：自动关联
- 将本轮 `mem_input`, `mem_reply`, `mem_summary` 生成 embedding 并加入向量库
- 调用 `MemoryAssociationNetwork.auto_associate_memory()`
  - 如果与旧内容 `sim > 0.65` → 建立 `is_related_to` 边
  - 或通过 prompt 自动判断是否 `summarizes`
  - 写入 `memory_association` 表

---

## 实现优先级

### 第一阶段：基础存储和检索
- 数据库初始化和基本CRUD操作
- 向量化和FAISS索引构建
- 简单的会话管理
- 核心表结构：`memories`, `memory_vectors`

### 第二阶段：记忆增强功能
- 缓存系统实现
- 关联网络构建
- 权重评估和排序
- 核心表结构：`memory_cache`, `memory_association`

### 第三阶段：高级功能
- 多跳推理
- 主题分组和摘要
- 冲突检测和解决
- 核心表结构：`memory_group`

---

## 核心模块实现

1. `embedding/vectorizer.py` - 向量化和缓存层逻辑
2. `association/network.py` - depth=2 多跳检索函数
3. `context/history.py` - session_id ↔️ memory 聚合查询器
4. `storage/memory_store.py` - 事务支持和CRUD操作
5. `init/db_manager.py` - 数据库初始化和索引管理
6. `retrieval/faiss_search.py` - 向量检索和混合搜索
7. `ranking/scorer.py` - 记忆评分和排序系统
