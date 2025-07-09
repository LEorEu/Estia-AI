<execution>
  <constraint>
    ## 记忆系统技术限制
    - **向量维度**：embedding模型的固定维度限制
    - **检索速度**：FAISS索引的查询性能上限
    - **存储容量**：SQLite数据库的扩展性限制
    - **实时性**：记忆检索必须在500ms内完成
    - **一致性**：向量索引与数据库的同步一致性
  </constraint>

  <rule>
    ## 记忆系统强制规则
    - **原子性操作**：记忆存储和索引更新必须原子化
    - **数据完整性**：每条记忆必须有完整的元数据
    - **版本控制**：记忆数据格式支持版本迁移
    - **并发安全**：多线程访问的线程安全保证
    - **备份恢复**：定期备份和故障恢复机制
  </rule>

  <guideline>
    ## 记忆系统实现指南
    - **分层缓存**：热点记忆缓存，冷记忆磁盘存储
    - **渐进式加载**：按需加载记忆数据
    - **智能压缩**：定期压缩和清理无用记忆
    - **权重衰减**：实现时间衰减和访问频率权重
    - **关联学习**：自动发现和建立记忆关联
  </guideline>

  <process>
    ## 记忆系统实现流程
    
    ### 第一步：数据库设计
    ```sql
    -- 核心记忆表
    CREATE TABLE memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        content_type TEXT NOT NULL,  -- user_input, assistant_reply, summary
        session_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        embedding_vector BLOB,
        metadata JSON,
        weight REAL DEFAULT 1.0,
        access_count INTEGER DEFAULT 0,
        last_accessed DATETIME
    );
    
    -- 记忆关联表
    CREATE TABLE memory_associations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_id_1 INTEGER,
        memory_id_2 INTEGER,
        association_type TEXT,  -- semantic, temporal, causal
        strength REAL DEFAULT 1.0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (memory_id_1) REFERENCES memories(id),
        FOREIGN KEY (memory_id_2) REFERENCES memories(id)
    );
    
    -- 记忆摘要表
    CREATE TABLE memory_summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        summary_content TEXT,
        original_memory_ids TEXT,  -- JSON array of memory IDs
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        embedding_vector BLOB
    );
    ```
    
    ### 第二步：向量索引管理
    ```python
    import faiss
    import numpy as np
    from typing import List, Tuple
    
    class FAISSMemoryIndex:
        def __init__(self, dimension: int = 1536):
            self.dimension = dimension
            self.index = faiss.IndexFlatIP(dimension)  # 内积索引
            self.id_mapping = {}  # FAISS索引ID到记忆ID的映射
            self.reverse_mapping = {}  # 记忆ID到FAISS索引ID的映射
            
        def add_memory(self, memory_id: int, embedding: np.ndarray):
            """添加记忆到向量索引"""
            faiss_id = self.index.ntotal
            self.index.add(embedding.reshape(1, -1))
            self.id_mapping[faiss_id] = memory_id
            self.reverse_mapping[memory_id] = faiss_id
            
        def search_similar(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[int, float]]:
            """搜索相似记忆"""
            scores, indices = self.index.search(query_embedding.reshape(1, -1), k)
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx in self.id_mapping:
                    memory_id = self.id_mapping[idx]
                    results.append((memory_id, score))
            return results
            
        def remove_memory(self, memory_id: int):
            """从索引中移除记忆"""
            if memory_id in self.reverse_mapping:
                # FAISS不支持直接删除，需要重建索引
                self._rebuild_index_without(memory_id)
                
        def save_index(self, path: str):
            """保存索引到磁盘"""
            faiss.write_index(self.index, path)
            
        def load_index(self, path: str):
            """从磁盘加载索引"""
            self.index = faiss.read_index(path)
    ```
    
    ### 第三步：记忆管理器
    ```python
    class MemoryManager:
        def __init__(self):
            self.db = SQLiteDB()
            self.faiss_index = FAISSMemoryIndex()
            self.embedding_model = EmbeddingModel()
            self.cache = MemoryCache()
            
        async def store_memory(self, content: str, content_type: str, 
                             session_id: str, metadata: dict = None) -> int:
            """存储记忆"""
            try:
                # 1. 生成embedding
                embedding = await self.embedding_model.encode(content)
                
                # 2. 存储到数据库
                memory_id = await self.db.insert_memory(
                    content=content,
                    content_type=content_type,
                    session_id=session_id,
                    embedding_vector=embedding.tobytes(),
                    metadata=json.dumps(metadata or {})
                )
                
                # 3. 添加到向量索引
                self.faiss_index.add_memory(memory_id, embedding)
                
                # 4. 更新缓存
                self.cache.set(f"memory:{memory_id}", {
                    'content': content,
                    'embedding': embedding,
                    'metadata': metadata
                })
                
                # 5. 异步建立关联
                asyncio.create_task(self._build_associations(memory_id, embedding))
                
                return memory_id
                
            except Exception as e:
                logger.error(f"Failed to store memory: {e}")
                raise MemoryError(f"Storage failed: {e}")
                
        async def retrieve_memories(self, query: str, top_k: int = 10, 
                                  session_filter: str = None) -> List[dict]:
            """检索记忆"""
            try:
                # 1. 生成查询embedding
                query_embedding = await self.embedding_model.encode(query)
                
                # 2. 向量搜索
                similar_memories = self.faiss_index.search_similar(
                    query_embedding, top_k * 2  # 获取更多候选
                )
                
                # 3. 从数据库获取详细信息
                memory_details = []
                for memory_id, similarity in similar_memories:
                    # 优先从缓存获取
                    cached = self.cache.get(f"memory:{memory_id}")
                    if cached:
                        memory_details.append({
                            'id': memory_id,
                            'similarity': similarity,
                            **cached
                        })
                    else:
                        # 从数据库获取
                        memory = await self.db.get_memory(memory_id)
                        if memory:
                            memory_details.append({
                                'id': memory_id,
                                'similarity': similarity,
                                **memory
                            })
                
                # 4. 应用过滤器
                if session_filter:
                    memory_details = [m for m in memory_details 
                                    if m.get('session_id') == session_filter]
                
                # 5. 扩展关联记忆
                expanded_memories = await self._expand_associations(memory_details)
                
                # 6. 重新排序和截断
                final_memories = self._rank_and_limit(expanded_memories, top_k)
                
                # 7. 更新访问统计
                for memory in final_memories:
                    asyncio.create_task(self._update_access_stats(memory['id']))
                
                return final_memories
                
            except Exception as e:
                logger.error(f"Failed to retrieve memories: {e}")
                return []
                
        async def _build_associations(self, memory_id: int, embedding: np.ndarray):
            """建立记忆关联"""
            # 查找语义相似的记忆
            similar_memories = self.faiss_index.search_similar(embedding, k=20)
            
            for similar_id, similarity in similar_memories:
                if similar_id != memory_id and similarity > 0.8:
                    await self.db.insert_association(
                        memory_id_1=memory_id,
                        memory_id_2=similar_id,
                        association_type="semantic",
                        strength=similarity
                    )
                    
        async def _expand_associations(self, memories: List[dict]) -> List[dict]:
            """扩展关联记忆"""
            expanded = memories.copy()
            
            for memory in memories:
                # 获取关联记忆
                associations = await self.db.get_associations(memory['id'])
                for assoc in associations:
                    related_memory = await self.db.get_memory(assoc['related_id'])
                    if related_memory:
                        # 调整相似度分数
                        adjusted_score = memory['similarity'] * assoc['strength'] * 0.5
                        related_memory['similarity'] = adjusted_score
                        expanded.append(related_memory)
                        
            return expanded
            
        def _rank_and_limit(self, memories: List[dict], limit: int) -> List[dict]:
            """排序和限制结果"""
            # 计算综合得分
            for memory in memories:
                time_decay = self._calculate_time_decay(memory['timestamp'])
                access_boost = min(memory.get('access_count', 0) * 0.1, 1.0)
                
                memory['final_score'] = (
                    memory['similarity'] * 0.6 +
                    time_decay * 0.2 +
                    access_boost * 0.2
                )
                
            # 排序和去重
            sorted_memories = sorted(memories, key=lambda x: x['final_score'], reverse=True)
            unique_memories = []
            seen_ids = set()
            
            for memory in sorted_memories:
                if memory['id'] not in seen_ids:
                    unique_memories.append(memory)
                    seen_ids.add(memory['id'])
                    
            return unique_memories[:limit]
            
        def _calculate_time_decay(self, timestamp: str) -> float:
            """计算时间衰减"""
            from datetime import datetime, timedelta
            
            memory_time = datetime.fromisoformat(timestamp)
            now = datetime.now()
            time_diff = now - memory_time
            
            # 指数衰减
            decay_rate = 0.1  # 每天衰减10%
            days_passed = time_diff.days
            decay_factor = np.exp(-decay_rate * days_passed)
            
            return max(decay_factor, 0.1)  # 最小保留10%
    ```
    
    ### 第四步：记忆压缩和清理
    ```python
    class MemoryCompressor:
        def __init__(self, memory_manager: MemoryManager):
            self.memory_manager = memory_manager
            
        async def compress_old_memories(self, days_threshold: int = 30):
            """压缩旧记忆"""
            # 1. 找到需要压缩的记忆
            old_memories = await self.memory_manager.db.get_old_memories(days_threshold)
            
            # 2. 按session分组
            sessions = {}
            for memory in old_memories:
                session_id = memory['session_id']
                if session_id not in sessions:
                    sessions[session_id] = []
                sessions[session_id].append(memory)
                
            # 3. 为每个session生成摘要
            for session_id, memories in sessions.items():
                if len(memories) > 5:  # 只有足够多的记忆才压缩
                    summary = await self._generate_summary(memories)
                    await self._store_summary(session_id, summary, memories)
                    
        async def _generate_summary(self, memories: List[dict]) -> str:
            """生成记忆摘要"""
            # 构建摘要prompt
            context = "请为以下对话记忆生成简洁的摘要：\n"
            for memory in memories:
                context += f"- {memory['content']}\n"
                
            # 调用LLM生成摘要
            summary = await self.llm_service.generate_summary(context)
            return summary
            
        async def _store_summary(self, session_id: str, summary: str, original_memories: List[dict]):
            """存储摘要并删除原始记忆"""
            # 存储摘要
            summary_embedding = await self.memory_manager.embedding_model.encode(summary)
            await self.memory_manager.db.insert_summary(
                session_id=session_id,
                summary_content=summary,
                original_memory_ids=json.dumps([m['id'] for m in original_memories]),
                embedding_vector=summary_embedding.tobytes()
            )
            
            # 删除原始记忆
            for memory in original_memories:
                await self.memory_manager.remove_memory(memory['id'])
    ```
  </process>

  <criteria>
    ## 记忆系统质量标准
    
    ### 性能指标
    - **检索延迟**：平均检索时间 < 500ms
    - **准确率**：相关记忆召回率 > 85%
    - **并发处理**：支持10个并发检索请求
    - **存储效率**：压缩后存储空间减少50%
    
    ### 功能完整性
    - **记忆存储**：支持多种类型记忆存储
    - **相似度检索**：准确的语义相似度搜索
    - **关联网络**：自动建立记忆间关联
    - **时间衰减**：合理的时间权重衰减
    
    ### 可靠性
    - **数据一致性**：向量索引与数据库同步
    - **故障恢复**：系统崩溃后能恢复记忆
    - **备份机制**：定期备份重要记忆
    - **版本兼容**：支持记忆数据格式升级
  </criteria>
</execution>