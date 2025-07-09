## AI 记忆系统专业知识

### 记忆系统分类

#### 1. 短期记忆 (Short-term Memory)
- **定义**：当前会话中的上下文信息
- **存储**：内存中的对话历史列表
- **特点**：快速访问，会话结束后清除
- **实现**：Python列表或队列结构

#### 2. 工作记忆 (Working Memory)
- **定义**：正在处理的活跃信息
- **存储**：内存缓存系统
- **特点**：临时性，用于推理和决策
- **实现**：Redis或内存字典

#### 3. 长期记忆 (Long-term Memory)
- **定义**：持久化的重要信息
- **存储**：数据库 + 向量索引
- **特点**：大容量，语义检索
- **实现**：SQLite + FAISS

### 记忆编码策略

#### 1. 向量编码
```python
from sentence_transformers import SentenceTransformer

class MemoryEncoder:
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model = SentenceTransformer(model_name)
        
    def encode_memory(self, text: str) -> np.ndarray:
        """将文本编码为向量"""
        return self.model.encode(text, normalize_embeddings=True)
        
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """批量编码提高效率"""
        return self.model.encode(texts, normalize_embeddings=True)
```

#### 2. 分层编码
- **句子级别**：单个句子的语义向量
- **段落级别**：段落的综合语义
- **对话级别**：整个对话的主题向量
- **情感级别**：情感状态的向量表示

#### 3. 多模态编码
- **文本**：transformer模型编码
- **音频**：音频特征提取
- **图像**：视觉特征编码
- **时间**：时间序列特征

### 记忆存储架构

#### 1. 数据库设计
```sql
-- 核心记忆表
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    content_type TEXT NOT NULL,
    session_id TEXT,
    user_id TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    embedding_vector BLOB,
    metadata JSON,
    importance_score REAL DEFAULT 1.0,
    access_count INTEGER DEFAULT 0,
    last_accessed DATETIME,
    emotional_tag TEXT,
    topic_cluster INTEGER
);

-- 记忆关联表
CREATE TABLE memory_associations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id_1 INTEGER,
    memory_id_2 INTEGER,
    association_type TEXT,
    strength REAL DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id_1) REFERENCES memories(id),
    FOREIGN KEY (memory_id_2) REFERENCES memories(id)
);

-- 记忆标签表
CREATE TABLE memory_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER,
    tag_name TEXT,
    tag_value TEXT,
    confidence REAL DEFAULT 1.0,
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);
```

#### 2. 向量索引结构
```python
class HierarchicalIndex:
    def __init__(self):
        self.sentence_index = faiss.IndexFlatIP(768)    # 句子级别
        self.paragraph_index = faiss.IndexFlatIP(768)   # 段落级别
        self.conversation_index = faiss.IndexFlatIP(768) # 对话级别
        
    def add_hierarchical_memory(self, memory: dict):
        """添加分层记忆"""
        sentence_emb = memory['sentence_embedding']
        paragraph_emb = memory['paragraph_embedding']
        conversation_emb = memory['conversation_embedding']
        
        self.sentence_index.add(sentence_emb)
        self.paragraph_index.add(paragraph_emb)
        self.conversation_index.add(conversation_emb)
```

### 记忆检索算法

#### 1. 多阶段检索
```python
class MultiStageRetrieval:
    def __init__(self):
        self.semantic_retriever = SemanticRetriever()
        self.temporal_retriever = TemporalRetriever()
        self.association_retriever = AssociationRetriever()
        
    async def retrieve_memories(self, query: str, context: dict) -> List[dict]:
        # 第一阶段：语义检索
        semantic_results = await self.semantic_retriever.search(query, top_k=50)
        
        # 第二阶段：时间过滤
        temporal_results = await self.temporal_retriever.filter(
            semantic_results, time_window=context.get('time_window')
        )
        
        # 第三阶段：关联扩展
        expanded_results = await self.association_retriever.expand(
            temporal_results, depth=2
        )
        
        # 第四阶段：重排序
        final_results = self.rerank(expanded_results, query, context)
        
        return final_results[:10]  # 返回前10个结果
```

#### 2. 相关性评分
```python
class RelevanceScorer:
    def __init__(self):
        self.weights = {
            'semantic_similarity': 0.4,
            'temporal_relevance': 0.2,
            'emotional_match': 0.2,
            'access_frequency': 0.1,
            'importance_score': 0.1
        }
        
    def calculate_relevance(self, memory: dict, query: str, context: dict) -> float:
        """计算记忆相关性得分"""
        score = 0.0
        
        # 语义相似度
        semantic_score = self.calculate_semantic_similarity(memory, query)
        score += semantic_score * self.weights['semantic_similarity']
        
        # 时间相关性
        temporal_score = self.calculate_temporal_relevance(memory, context)
        score += temporal_score * self.weights['temporal_relevance']
        
        # 情感匹配
        emotional_score = self.calculate_emotional_match(memory, context)
        score += emotional_score * self.weights['emotional_match']
        
        # 访问频率
        access_score = min(memory.get('access_count', 0) / 10.0, 1.0)
        score += access_score * self.weights['access_frequency']
        
        # 重要性得分
        importance_score = memory.get('importance_score', 1.0)
        score += importance_score * self.weights['importance_score']
        
        return score
```

### 记忆关联网络

#### 1. 关联类型
- **语义关联**：基于内容相似性
- **时间关联**：基于时间邻近性
- **因果关联**：基于逻辑因果关系
- **情感关联**：基于情感状态相似
- **主题关联**：基于话题聚类

#### 2. 关联强度计算
```python
class AssociationCalculator:
    def calculate_semantic_association(self, memory1: dict, memory2: dict) -> float:
        """计算语义关联强度"""
        emb1 = memory1['embedding']
        emb2 = memory2['embedding']
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
    def calculate_temporal_association(self, memory1: dict, memory2: dict) -> float:
        """计算时间关联强度"""
        time1 = datetime.fromisoformat(memory1['timestamp'])
        time2 = datetime.fromisoformat(memory2['timestamp'])
        time_diff = abs((time1 - time2).total_seconds())
        
        # 时间越近，关联越强
        return np.exp(-time_diff / (24 * 3600))  # 24小时衰减
        
    def calculate_causal_association(self, memory1: dict, memory2: dict) -> float:
        """计算因果关联强度"""
        # 使用NLP技术识别因果关系
        causal_indicators = ["因为", "所以", "导致", "由于", "因此"]
        
        text1 = memory1['content']
        text2 = memory2['content']
        
        causal_score = 0.0
        for indicator in causal_indicators:
            if indicator in text1 and indicator in text2:
                causal_score += 0.2
                
        return min(causal_score, 1.0)
```

### 记忆压缩与总结

#### 1. 分层总结
```python
class MemoryCompressor:
    def __init__(self, llm_service):
        self.llm_service = llm_service
        
    async def compress_conversation(self, memories: List[dict]) -> dict:
        """压缩对话记忆"""
        # 构建总结prompt
        context = "以下是一段对话记忆，请生成简洁的总结：\n"
        for memory in memories:
            context += f"- {memory['content']}\n"
            
        # 生成总结
        summary = await self.llm_service.generate_summary(context)
        
        # 创建总结记忆
        summary_memory = {
            'content': summary,
            'content_type': 'summary',
            'original_memory_ids': [m['id'] for m in memories],
            'compression_ratio': len(summary) / sum(len(m['content']) for m in memories)
        }
        
        return summary_memory
```

#### 2. 重要性评估
```python
class ImportanceEvaluator:
    def evaluate_memory_importance(self, memory: dict, context: dict) -> float:
        """评估记忆重要性"""
        importance = 0.0
        
        # 情感强度
        emotional_intensity = self.calculate_emotional_intensity(memory)
        importance += emotional_intensity * 0.3
        
        # 信息密度
        information_density = self.calculate_information_density(memory)
        importance += information_density * 0.2
        
        # 用户参与度
        user_engagement = self.calculate_user_engagement(memory)
        importance += user_engagement * 0.3
        
        # 话题重要性
        topic_importance = self.calculate_topic_importance(memory)
        importance += topic_importance * 0.2
        
        return min(importance, 1.0)
```

### 记忆系统性能优化

#### 1. 缓存策略
- **LRU缓存**：最近最少使用的记忆优先淘汰
- **LFU缓存**：最不频繁使用的记忆优先淘汰
- **TTL缓存**：基于时间的缓存过期
- **多级缓存**：内存-SSD-磁盘的分层缓存

#### 2. 索引优化
- **倒排索引**：关键词快速检索
- **LSH索引**：近似最近邻搜索
- **PQ索引**：乘积量化压缩
- **图索引**：基于图结构的检索

#### 3. 并发控制
- **读写分离**：查询和写入分离
- **分片存储**：数据水平分片
- **异步处理**：非阻塞的记忆操作
- **批处理**：批量操作提高效率