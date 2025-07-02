# Estia 情节演化 & 情感一致性 设计草案

> 版本：v0.1  作者：AI 助理  日期：2025-07-02

---

## ✨ 目标
1. 让 AI 具备「故事线（Story Arc）」记忆与引用能力，长期陪伴用户。
2. 让回复在情绪与语调上保持一致，提升陪伴真实感。

---

## 1. 情节演化（Story Arc）

### 1.1 核心概念
| 概念 | 说明 |
|------|------|
| Story Arc | 持续多天/多轮的主题剧情，如「准备海岛旅行」 |
| Story Event | Arc 内的原子事件节点，如「订机票成功」 |
| Timeline | 将各 Arc 的 Event 按时间轴串联，便于回溯与推理 |

### 1.2 数据库设计
```sql
CREATE TABLE story_arc (
  arc_id TEXT PRIMARY KEY,          -- travel_202507
  title  TEXT,                      -- 海岛旅行计划
  status TEXT DEFAULT 'ongoing',    -- ongoing / finished
  summary TEXT,                     -- AI 持续更新
  started_at REAL, ended_at REAL
);

CREATE TABLE story_event (
  event_id TEXT PRIMARY KEY,
  arc_id   TEXT,                    -- 所属 Arc
  content  TEXT,                    -- 事件描述
  timestamp REAL,
  importance REAL DEFAULT 1.0,
  meta     TEXT                     -- JSON 附加信息
);
```

### 1.3 工作流
1. **检测** `StoryDetector.detect_arc(user_input)`  
   - 关键词 / LLM 分类，判断是否触发或创建 Arc。
2. **写入事件** `StoryManager.add_event(arc_id, content)`  
   - 记录原话摘要、时间戳、重要度。
3. **更新摘要** `StoryManager.update_summary(arc_id)`  
   - 每日或每 N 条 Event，用 LLM 生成进展摘要写回 `story_arc.summary`。
4. **检索拼接** `ContextBuilder` 读取最近 7 天内的 Arc summary + 关联 Event（top-k by importance），拼入 Prompt。
5. **归档**  
   - 当 `status`=finished：压缩所有 Event ⇒ 1 条 `memories(type='summary', level='archive')`，删除/降级细节。

### 1.4 最小可行版本 (MVP)
- 新建 `StoryManager`（≈200 LOC）
- 纯关键词检测：旅行 / 健身 / 考研 …
- LLM 每晚定时批量更新 summary（异步任务）
- `ContextBuilder` 追加 `[剧情]{title}:{summary}` 行

---

## 2. 情感 / 语调一致性

### 2.1 三元标签
| 字段 | 示例值 | 作用 |
|------|--------|------|
| emotion | joy / neutral / sad / anger ... | 客观情绪 |
| tone | playful / gentle / formal ... | 语气风格 |
| intensity | 0 – 1 | 强度、口吻浓淡 |

存储位置：`memories.metadata` JSON
```json
{
  "emotion": "joy",
  "tone": "playful",
  "intensity": 0.7
}
```

### 2.2 标签生成
1. **规则关键词**：简单情感词典匹配。  
2. **本地情感模型**：如 `distilbert-sst2` 或中文情感分类模型。  
3. **LLM 分类**：`classify_emotion(text)` 辅助高置信度场景。

### 2.3 一致性推断公式
```
current_emotion = α * latest_user_emotion
                + β * mean(last_5_user_emotions)
                + γ * decay(prev_ai_emotion)
```
默认 α=0.6, β=0.3, γ=0.1

### 2.4 Prompt 注入模板
```
你是一位体贴的朋友，语气 {tone}，情绪 {emotion}，强度 {intensity}。
在回答时使用符合语气的词汇和 Emoji。
```
> 可预置 5-10 套不同 tone 的「措辞模板」实现快速切换。

### 2.5 回复示例
| 场景 | Prompt 片段 | 输出示例 |
|------|-------------|----------|
| 用户抱怨加班 | gentle + empathic | "听起来今天真不容易呢🥺，想试试之前说的分工方案吗？" |
| 用户兴奋拿到 offer | playful + joy | "太棒啦🎉！为你点赞！准备怎么庆祝？" |

---

## 3. 集成步骤一览
1. **DB**：执行两张新表 SQL；`ALTER TABLE memories ADD COLUMN ...`（若需要）。
2. **代码**：
   - `story_manager.py`（逻辑 + LLM 摘要）
   - `emotion_tagger.py`（规则+模型混合）
3. **Pipeline Hook**：
   - `MemoryStore.add_interaction_memory()` → 写 StoryEvent / emotion
   - `ContextBuilder.build_context()` → 拼 Arc summary + tone prompt
4. **任务调度**：
   - 每 D 日 `update_summary`、衰减情绪、归档 finished Arc
5. **监控指标**：
   - Arc 数量、进行中 / 已完成比、情感标签分布

---

## 4. 里程碑 & 预估
| 阶段 | 任务 | 工期 |
|------|------|------|
| MVP | StoryManager ＋ 情感打标（规则） | 5 天 |
| v1  | LLM 摘要自动化、Prompt 语调模板 | 7 天 |
| v1.5 | 本地情感模型替换 / 微调 | 5 天 |
| v2  | 完整情绪衰减算法 + UI 可视化 | 1 周 |

---

## 5. 拟人化增强技巧（可选）
> 小投入、大体验，打造"像真人"细节。

| # | 机制 | 设计要点 | MVP 实现 |
|---|------|----------|----------|
| 1 | 生活节奏提示 | 为 AI 设定本地作息表（睡觉/吃饭） | 在回复前 `if now in sleep_range: prepend("我刚准备休息…")` |
| 2 | 轻微不完美 | 1–3 % 概率出现打字错误后自嘲修正 | `if random()<0.03: typo(text)` + "打错啦😅…" |
| 3 | 兴趣偏好演化 | metadata.hobbies 浮点权重随互动增减 | `MemoryStore.update_hobby_score(hobby, delta)` |
| 4 | 短期忘记 & 追问 | 1–2 % 概率忘记刚提到的小细节 | `if rand<0.02 and not core_info: ask_follow_up()` |
| 5 | 情绪冷却曲线 | intensity 每轮衰减 0.3，2–3 轮回归 neutral | 在 `emotion_manager.postprocess()` 衰减 |
| 6 | 每日反思日记 | 夜间写 `diary` 类型记忆，次日可引用 | 定时任务调用 GPT 生成自省文本 |

> 建议优先落地：①生活节奏、⑤情绪冷却（1–2 天）；随后 ③兴趣演化、⑥反思日记。

---

> 本文档只阐述数据结构与流程，未锁定具体模型／阈值，可根据项目规模灵活调整。 