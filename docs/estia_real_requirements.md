# 📋 Estia AI助手真实需求分析文档

> **基于代码分析和设计文档整理的核心需求**

## 🎯 项目愿景

创建一个具有**长期记忆能力**的AI助手，能够：
- 记住用户的个人信息、偏好和对话历史
- 基于历史记忆提供个性化、连贯的对话体验
- 像人类朋友一样理解用户的情感状态和需求变化
- 随着交互增多，越来越了解用户，提供更贴心的服务

## 🧠 核心需求分析

### 1. **长期记忆与个性化**

**需求背景**：
```
用户：我今天没有摸鱼而是一直工作
AI应该回复：我记得你之前提到工作压力很大，今天这么专注工作，是不是有什么特别的项目要完成？
而不是：好的，我了解了
```

**技术要求**：
- ✅ 记住用户的工作状态、生活习惯、兴趣爱好
- ✅ 基于历史对话理解当前语境
- ✅ 区分重要信息（姓名、职业）和临时信息（天气、心情）
- ✅ 支持跨时间跨话题的记忆关联

### 2. **🆕 动态权重与记忆演进**

**需求场景**：
```
第一次对话：用户说"我是程序员" → 权重 6.0
第5次对话：用户又提到"我是程序员，主要写Python" → 权重 7.5
第20次对话：用户说"我现在不做程序员了，转行做产品经理" → 原记忆权重降低，新记忆权重升高
```

**技术要求**：
- ✅ **时间衰减机制**：核心记忆衰减慢（每天0.5%），短期记忆衰减快（每天5%）
- ✅ **访问强化机制**：24小时内访问过的记忆权重增强10%
- ✅ **上下文相关性**：与当前话题相关的记忆权重临时提升20%
- ✅ **情感关联强化**：情感强烈的记忆权重增强15%
- ✅ **近期活跃度**：30分钟内被访问的记忆临时增强30%

### 3. **🆕 智能记忆归档（非删除）**

**需求场景**：
```
传统方案：直接删除30天前的短期记忆
新方案：将记忆标记为"归档"，降低权重30%，不参与主动检索，但可以恢复
```

**技术要求**：
- ✅ **软删除机制**：添加`archived`字段，标记而不删除
- ✅ **权重降级**：归档时降低权重30%，保留原始内容
- ✅ **按需恢复**：被再次访问时可以恢复并提升权重50%
- ✅ **分层存储**：核心记忆（9.0+）永不归档，短期记忆（<4.0）定期归档

### 4. **🆕 LLM主动记忆访问与思考**

**需求场景**：
```
用户：我最近工作压力好大
AI思考过程：
1. 先获取相关记忆 → 发现用户之前提到过工作压力、加班、想换工作
2. 再查询用户基本信息 → 程序员，在某公司工作
3. 查询近期对话 → 上周提到项目deadline临近
4. 综合分析后给出个性化回复
```

**技术要求**：
- ✅ **4种记忆搜索工具**：
  - `search_memories_by_keyword` - 关键词搜索
  - `search_memories_by_timeframe` - 时间范围搜索
  - `search_core_memories` - 核心记忆搜索
  - `get_related_memories` - 关联记忆搜索
- ✅ **工具调用接口**：LLM可以在对话中主动调用记忆搜索
- ✅ **多轮思考**：LLM可以基于检索到的记忆进一步查询
- ✅ **渐进式推理**：从基础信息到深层理解的逐步推理

### 5. **🆕 增强评估上下文**

**需求场景**：
```
传统评估：只看当前对话 → "我今天很开心" → 权重 3.0
增强评估：
- 用户画像：用户平时比较内向，很少表达情感
- 对话历史：前几天一直在抱怨工作压力
- 话题上下文：最近在讨论工作转换
- 情感上下文：从负面情绪转为正面情绪
结果：权重调整为 6.5（情感转折很重要）
```

**技术要求**：
- ✅ **用户画像构建**：基本信息、偏好、目标、性格特征
- ✅ **对话历史分析**：最近3轮对话的配对分析
- ✅ **话题上下文追踪**：当前关键词、活跃话题、话题演进轨迹
- ✅ **情感上下文分析**：当前情感、历史情感、情感模式识别
- ✅ **五维度评估**：时间衰减、访问频率、上下文相关性、情感强度、近期活跃度

### 6. **语义关联与联想网络**

**需求场景**：
```
历史对话：用户提到"在做机器学习项目"
当前对话：用户说"遇到过拟合问题"
AI应该：联想到之前的ML项目，而不是其他类型的"问题"
```

**技术要求**：
- ✅ 基于语义相似度的记忆检索（不仅仅是关键词匹配）
- ✅ 多层关联网络（记忆A → 相关记忆B → 更相关记忆C）
- ✅ 关联类型识别：
  - `is_related_to` - 相关记忆
  - `same_topic` - 同话题
  - `causes` - 因果关系
  - `contradicts` - 矛盾冲突
  - `summarizes` - 总结关系

### 7. **主题聚合与会话连贯性**

**需求场景**：
```
工作压力话题：
- 第1天：我工作压力好大
- 第3天：今天又加班到很晚  
- 第7天：我想换工作了
- 第10天：你怎么看待我今天没摸鱼？

AI应该：理解这是一个持续的工作压力话题演进
```

**技术要求**：
- ✅ 自动话题分组（`work_stress_2025_06_27`）
- ✅ 话题演进追踪（从压力 → 抱怨 → 想换工作 → 状态改善）
- ✅ 会话连贯性（记住上下文，避免重复询问）
- ✅ 智能摘要生成（浓缩长期对话的精华）

### 8. **情感状态与个性理解**

**需求场景**：
```
用户A（技术型）：问题都很具体，喜欢详细解释
用户B（情感型）：经常聊心情，需要情感支持
AI应该：针对不同用户采用不同的回复风格
```

**技术要求**：
- ✅ 用户画像构建（技术偏好、情感特征、交流风格）
- ✅ 情感状态追踪（开心、沮丧、兴奋、焦虑）
- ✅ 个性化回复风格（正式/随意、详细/简洁、理性/感性）
- ✅ 长期关系建立（从陌生到熟悉的渐进过程）

## 🏗️ 架构设计需求

### 1. **数据架构需求**

**6张核心数据表**（增强版）：
```sql
-- 记忆主表（增强版）
CREATE TABLE memories (
    id TEXT PRIMARY KEY,           -- mem_001
    content TEXT NOT NULL,         -- 实际内容
    type TEXT NOT NULL,            -- user_input/assistant_reply/summary
    role TEXT NOT NULL,            -- user/assistant/system
    session_id TEXT,               -- 对话块ID
    timestamp REAL NOT NULL,       -- 时间戳
    weight REAL DEFAULT 1.0,       -- 动态权重(LLM评估,0-10)
    group_id TEXT,                 -- 话题分组
    summary TEXT,                  -- 摘要
    last_accessed REAL NOT NULL,   -- 最后访问时间
    archived INTEGER DEFAULT 0,    -- 🆕 归档标记
    metadata TEXT                  -- 🆕 元数据（JSON格式）
);

-- 向量存储表
CREATE TABLE memory_vectors (
    id TEXT PRIMARY KEY,
    memory_id TEXT NOT NULL,       -- 对应记忆ID
    vector BLOB NOT NULL,          -- 二进制向量数据
    model_name TEXT NOT NULL,      -- 嵌入模型名称
    timestamp REAL NOT NULL
);

-- 记忆关联表
CREATE TABLE memory_association (
    id TEXT PRIMARY KEY,
    source_key TEXT NOT NULL,      -- 起点记忆ID
    target_key TEXT NOT NULL,      -- 终点记忆ID
    association_type TEXT NOT NULL, -- 关联类型
    strength REAL NOT NULL,        -- 关联强度(0-1)
    created_at REAL NOT NULL,
    last_activated REAL NOT NULL
);

-- 话题分组表
CREATE TABLE memory_group (
    group_id TEXT PRIMARY KEY,     -- work_stress_2025_06_27
    super_group TEXT,              -- work_stress  
    topic TEXT,                    -- 话题描述
    time_start REAL,               -- 开始时间
    time_end REAL,                 -- 结束时间
    summary TEXT,                  -- 话题摘要
    score REAL DEFAULT 1.0         -- 重要程度
);

-- 记忆缓存表
CREATE TABLE memory_cache (
    id TEXT PRIMARY KEY,
    memory_id TEXT NOT NULL,
    cache_level TEXT NOT NULL,     -- hot/warm
    priority REAL NOT NULL,        -- 缓存优先级(0-10)
    access_count INTEGER,          -- 访问计数
    last_accessed REAL NOT NULL
);
```

### 2. **🆕 动态权重算法**

**权重调整公式**：
```python
def calculate_dynamic_weight(current_weight, factors):
    # 5个权重因子
    time_decay = 0.995 ** age_days        # 时间衰减
    access_frequency = 1.1 if recent_access else 0.98  # 访问频率
    contextual_relevance = 1.2 if topic_related else 1.0  # 上下文相关性
    emotional_intensity = 1.15 if emotional_content else 1.0  # 情感强度
    recency_boost = 1.3 if just_accessed else 1.0  # 近期活跃度
    
    # 综合计算
    new_weight = current_weight * time_decay * access_frequency * contextual_relevance * emotional_intensity * recency_boost
    return min(10.0, max(0.1, new_weight))
```

### 3. **🆕 工作流程需求（增强版）**

**完整的15步记忆处理流程**：
1. **Step 1-2**: 系统初始化（数据库+向量索引）
2. **Step 3**: 用户输入向量化
3. **Step 4**: FAISS向量相似度检索 
4. **Step 5**: 关联网络扩展（depth=2多跳检索）
5. **Step 6**: 历史对话内容聚合（session_id + group_id）
6. **Step 7**: 记忆排序去重（权重+相似度+时效性）
7. **Step 8**: 🆕 LLM主动记忆访问（工具调用）
8. **Step 9**: 智能上下文构建
9. **Step 10**: LLM对话生成
10. **Step 11**: 🆕 增强评估上下文构建
11. **Step 12**: 🆕 异步LLM评估（包含用户画像、对话历史、话题上下文、情感上下文）
12. **Step 13**: 异步存储评估结果
13. **Step 14**: 🆕 动态权重更新
14. **Step 15**: 自动建立记忆关联

### 4. **🆕 性能需求**

**响应速度要求**：
- ✅ 查询增强：< 100ms（Step 3-9）
- ✅ 完整对话：< 500ms（Step 1-10）
- ✅ 动态权重更新：< 50ms（Step 14）
- ✅ 异步处理：不阻塞用户交互（Step 11-15）

**存储容量需求**：
- ✅ 核心记忆：永久保留（权重9.0+）
- ✅ 归档记忆：降权保留（权重7.0-8.9）
- ✅ 长期记忆：2000条（权重4.0-6.9）
- ✅ 短期记忆：500条（权重1.0-3.9，定期归档）

## 🛠️ 技术实现需求

### 1. **🆕 LLM记忆访问工具**

```python
# LLM可调用的记忆搜索工具
tools = [
    {
        "name": "search_memories_by_keyword",
        "description": "根据关键词搜索相关记忆",
        "parameters": {
            "keywords": str,  # 搜索关键词
            "weight_threshold": float,  # 权重阈值
            "max_results": int  # 最大结果数
        }
    },
    {
        "name": "search_core_memories", 
        "description": "搜索核心记忆（权重9.0+）",
        "parameters": {
            "category": str  # 记忆类别
        }
    },
    # ... 其他工具
]
```

### 2. **🆕 增强评估上下文**

```python
class EvaluationContext:
    def __init__(self):
        self.user_profile = {
            'basic_info': [],      # 基本信息
            'preferences': [],     # 偏好习惯
            'goals': [],          # 目标计划
            'personality_traits': [] # 性格特征
        }
        self.conversation_history = []  # 近期对话历史
        self.topic_context = {
            'current_keywords': [],   # 当前关键词
            'active_topics': [],      # 活跃话题
            'topic_evolution': []     # 话题演进轨迹
        }
        self.emotional_context = {
            'current_emotion': 'neutral',  # 当前情感
            'historical_emotions': [],     # 历史情感
            'emotion_pattern': 'stable'    # 情感模式
        }
```

### 3. **🆕 接口设计需求**

**用户API**（增强版）：
```python
class EstiaMemorySystem:
    def enhance_query(self, user_input: str) -> str:
        """查询增强：返回包含相关记忆的上下文"""
        
    def store_interaction(self, user_input: str, ai_response: str):
        """存储对话：异步处理评估和权重更新"""
        
    def get_memory_search_tools(self) -> List[Dict]:
        """获取LLM可用的记忆搜索工具定义"""
        
    def execute_memory_search_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """执行记忆搜索工具（供LLM调用）"""
        
    def update_memory_weight_dynamically(self, memory_id: str, context: Dict) -> Dict:
        """动态更新记忆权重"""
        
    def archive_old_memories(self, days_threshold: int = 30) -> Dict:
        """归档过期记忆（软删除）"""
        
    def restore_archived_memories(self, memory_ids: List[str]) -> Dict:
        """恢复归档记忆"""
```

## 🎯 质量标准

### 1. **🆕 功能质量**
- ✅ **记忆持久性**：核心记忆永不丢失，重要记忆可恢复
- ✅ **权重准确性**：动态权重能准确反映记忆重要性变化
- ✅ **思考连贯性**：LLM能通过工具调用进行深入思考
- ✅ **评估精准性**：基于丰富上下文的准确重要性评估

### 2. **🆕 技术质量**  
- ✅ **响应速度**：动态权重更新 < 50ms
- ✅ **存储效率**：归档机制节省80%存储空间
- ✅ **工具可用性**：LLM工具调用成功率 > 95%
- ✅ **上下文准确性**：评估上下文构建准确率 > 90%

### 3. **🆕 用户体验**
- ✅ **记忆演进感**：用户感受到AI记忆的动态变化
- ✅ **思考深度感**：AI回复体现深入思考过程
- ✅ **个性化程度**：基于丰富上下文的个性化回复
- ✅ **长期价值感**：记忆系统随使用时间增长而更智能

## 🚀 实施优先级

### 第一阶段：基础记忆系统（MVP）
- [x] 数据库初始化（6张表）
- [x] 基础存储和检索  
- [x] 简单的重要性评估
- [x] 基本的上下文构建

### 第二阶段：智能检索优化
- [x] FAISS向量检索
- [x] 记忆排序和去重
- [x] 缓存系统优化
- [x] 性能监控和调优

### 第三阶段：高级关联网络
- [x] 多跳关联检索
- [x] 主题自动分组
- [x] 异步LLM评估
- [x] 智能摘要生成

### 🆕 第四阶段：动态记忆管理
- [x] 动态权重机制
- [x] 软删除归档系统
- [x] 记忆恢复机制
- [x] 分层存储优化

### 🆕 第五阶段：LLM主动思考
- [x] 记忆搜索工具集
- [x] 工具调用接口
- [x] 多轮思考支持
- [x] 渐进式推理

### 🆕 第六阶段：增强评估系统
- [x] 用户画像构建
- [x] 对话历史分析
- [x] 话题上下文追踪
- [x] 情感上下文分析

### 第七阶段：深度个性化
- [ ] 用户画像完善
- [ ] 情感状态追踪  
- [ ] 个性化回复风格
- [ ] 长期关系管理

## 📊 成功指标

### 🆕 定量指标
- **记忆准确率**：检索到的记忆与当前话题相关性 > 85%
- **权重动态性**：24小时内权重变化的记忆占比 > 30%
- **工具调用率**：LLM主动调用记忆工具的频率 > 50%
- **评估准确率**：基于增强上下文的评估准确性 > 90%
- **归档效率**：归档机制节省的存储空间 > 70%

### 🆕 定性指标
- **记忆演进感**：用户感受到AI记忆的动态变化和成长
- **思考深度感**：AI回复体现深入思考，而非简单检索
- **个性化精准度**：基于丰富上下文的精准个性化回复
- **长期伴侣感**：AI成为真正理解用户的智能伙伴

---

## 📝 总结

Estia记忆系统的真实需求已经从简单的存储检索系统进化为**智能记忆伙伴系统**，核心价值在于：

1. **🧠 动态记忆演进**：像人类一样，记忆的重要性会随时间和情境动态变化
2. **🔍 主动思考能力**：LLM能够主动查询需要的记忆，进行深入思考
3. **📊 丰富评估上下文**：基于用户画像、对话历史、话题演进的准确评估
4. **💾 智能归档管理**：软删除机制保留所有记忆，按需恢复
5. **🎯 深度个性化**：真正理解用户的个性、情感和需求变化

这不仅是一个记忆系统，更是一个能够**学习、思考、成长**的智能记忆伙伴。 