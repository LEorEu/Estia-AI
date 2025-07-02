"""
记忆存储管理器 - 负责记忆的存储、检索和管理
整合数据库管理器、向量索引管理器和文本向量化器
"""

import os
import time
import json
import uuid
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime

# 导入记忆系统组件
try:
    from core.memory.init import DatabaseManager, VectorIndexManager
    from core.memory.embedding import TextVectorizer, EmbeddingCache
    from core.utils.logger import get_logger
    logger = get_logger("estia.memory.storage")
except ImportError:
    # 如果还没有日志工具，使用标准日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("estia.memory.storage")
    
    # 尝试导入必要组件
    try:
        from core.memory.init import DatabaseManager, VectorIndexManager
    except ImportError:
        logger.error("无法导入DatabaseManager或VectorIndexManager")
        DatabaseManager = None
        VectorIndexManager = None
    
    try:
        from core.memory.embedding import TextVectorizer, EmbeddingCache
    except ImportError:
        logger.error("无法导入TextVectorizer或EmbeddingCache")
        TextVectorizer = None
        EmbeddingCache = None

class MemoryStore:
    """
    记忆存储管理器类
    负责记忆的存储、检索和管理
    整合数据库、向量索引和向量化功能
    """
    
    def __init__(self, db_path: Optional[str] = None, 
                 index_path: Optional[str] = None,
                 cache_dir: Optional[str] = None,
                 vector_dim: int = 1024,
                 model_type: str = "sentence-transformers",
                 model_name: str = "Qwen/Qwen3-Embedding-0.6B"):
        """
        初始化记忆存储管理器
        
        参数:
            db_path: 数据库路径，如果为None则使用默认路径
            index_path: 向量索引路径，如果为None则使用默认路径
            cache_dir: 缓存目录，如果为None则使用默认路径
            vector_dim: 向量维度，默认为1024（适用于Qwen模型）
            model_type: 向量化模型类型
            model_name: 向量化模型名称
        """
        # 设置默认路径
        if db_path is None:
            db_path = os.path.join("assets", "memory.db")
            
        if index_path is None:
            index_path = os.path.join("data", "vectors", "memory_index.bin")
            
        if cache_dir is None:
            cache_dir = os.path.join("data", "memory", "cache")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        os.makedirs(cache_dir, exist_ok=True)
        
        self.db_path = db_path
        self.index_path = index_path
        self.cache_dir = cache_dir
        self.vector_dim = vector_dim
        
        # 初始化组件
        self.db_manager: Optional["DatabaseManager"] = None
        self.vector_index: Optional["VectorIndexManager"] = None
        self.vectorizer: Optional["TextVectorizer"] = None
        
        # 初始化数据库管理器
        self._init_db_manager()
        
        # 初始化向量索引管理器
        self._init_vector_index()
        
        # 初始化文本向量化器
        self._init_vectorizer(model_type, model_name)
        
        logger.info(f"记忆存储管理器初始化完成，数据库: {db_path}, 向量索引: {index_path}")
    
    def _init_db_manager(self):
        """初始化数据库管理器"""
        try:
            if DatabaseManager is None:
                logger.error("DatabaseManager类未导入")
                return
                
            self.db_manager = DatabaseManager(self.db_path)
            if self.db_manager and self.db_manager.connect():
                self.db_manager.initialize_database()
                logger.info(f"数据库管理器初始化成功: {self.db_path}")
            else:
                logger.error("数据库连接失败")
                self.db_manager = None
        except Exception as e:
            logger.error(f"初始化数据库管理器失败: {e}")
            self.db_manager = None
    
    def _init_vector_index(self):
        """初始化向量索引管理器"""
        try:
            if VectorIndexManager is None:
                logger.error("VectorIndexManager类未导入")
                return
                
            self.vector_index = VectorIndexManager(
                index_path=self.index_path,
                vector_dim=self.vector_dim
            )
            
            if self.vector_index and not self.vector_index.available:
                logger.warning("FAISS不可用，向量索引功能将被禁用")
                return
            
            # 加载或创建索引
            if self.vector_index and os.path.exists(self.index_path):
                success = self.vector_index.load_index()
                if success:
                    logger.info(f"加载向量索引成功: {self.index_path}")
                else:
                    logger.warning(f"加载向量索引失败，创建新索引")
                    self.vector_index.create_index()
            elif self.vector_index:
                self.vector_index.create_index()
                logger.info(f"创建新向量索引: {self.index_path}")
        except Exception as e:
            logger.error(f"初始化向量索引管理器失败: {e}")
            self.vector_index = None
    
    def _init_vectorizer(self, model_type, model_name):
        """初始化文本向量化器"""
        try:
            if TextVectorizer is None:
                logger.error("TextVectorizer类未导入")
                return
                
            self.vectorizer = TextVectorizer(
                model_type=model_type,
                model_name=model_name,
                cache_dir=self.cache_dir,
                use_cache=True
            )
            logger.info(f"文本向量化器初始化成功，模型: {model_type}/{model_name}")
        except Exception as e:
            logger.error(f"初始化文本向量化器失败: {e}")
            self.vectorizer = None
    
    def add_memory(self, content: str, source: str = "user", 
                  importance: float = 0.5, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        添加新记忆
        
        参数:
            content: 记忆内容
            source: 记忆来源，如"user"、"system"等
            importance: 重要性分数，0-1之间
            metadata: 其他元数据
            
        返回:
            Optional[str]: 记忆ID，失败时返回None
        """
        if not content.strip():
            logger.warning("记忆内容为空，不添加")
            return None
            
        if self.db_manager is None:
            logger.error("数据库管理器未初始化，无法添加记忆")
            return None
            
        try:
            # 生成记忆ID
            memory_id = str(uuid.uuid4())
            
            # 获取当前时间戳
            timestamp = int(time.time())
            
            # 准备元数据
            if metadata is None:
                metadata = {}
                
            metadata_json = json.dumps(metadata, ensure_ascii=False)
            
            # 步骤1：将记忆存入数据库
            self.db_manager.execute_query(
                """
                INSERT INTO memories 
                (id, content, type, role, session_id, timestamp, weight, last_accessed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (memory_id, content, "memory", source, "", timestamp, importance, timestamp, metadata_json)
            )
            
            # 提交数据库事务
            if self.db_manager.conn:
                self.db_manager.conn.commit()
            
            # 步骤2：对内容进行向量化
            vector = self._vectorize_text(content)
            
            if vector is not None:
                # 步骤3：将向量存入向量表
                vector_id = f"vec_{memory_id}"
                
                # 将向量转换为二进制格式存储
                vector_blob = vector.tobytes()
                
                self.db_manager.execute_query(
                    """
                    INSERT INTO memory_vectors
                    (id, memory_id, vector, model_name, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (vector_id, memory_id, vector_blob, f"{self.vectorizer.model_type}/{self.vectorizer.model_name}", timestamp)
                )
                
                # 提交向量数据
                if self.db_manager.conn:
                    self.db_manager.conn.commit()
                
                # 步骤4：将向量添加到向量索引
                if self.vector_index and self.vector_index.available:
                    success = self.vector_index.add_vectors(
                        vectors=vector.reshape(1, -1),
                        ids=[memory_id]
                    )
                    
                    if success:
                        # 保存索引
                        self.vector_index.save_index()
                    else:
                        logger.warning("添加向量到索引失败，但记忆已保存到数据库")
                else:
                    logger.warning("向量索引不可用，仅保存到数据库")
                
            logger.info(f"成功添加记忆: {memory_id}, 内容: {content[:30]}...")
            return memory_id
            
        except Exception as e:
            logger.error(f"添加记忆失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def add_interaction_memory(self, content: str, memory_type: str, role: str,
                              session_id: str, timestamp: float, weight: float = 5.0) -> Optional[str]:
        """
        添加交互记忆（兼容EstiaMemorySystem接口）
        
        参数:
            content: 记忆内容
            memory_type: 记忆类型（user_input, assistant_reply等）
            role: 角色（user, assistant, system）
            session_id: 会话ID
            timestamp: 时间戳
            weight: 权重
            
        返回:
            Optional[str]: 记忆ID，失败时返回None
        """
        if not content.strip():
            logger.warning("记忆内容为空，不添加")
            return None
            
        if self.db_manager is None:
            logger.error("数据库管理器未初始化，无法添加记忆")
            return None
            
        try:
            # 生成记忆ID
            memory_id = f"mem_{uuid.uuid4().hex[:12]}"
            
            # 准备元数据
            metadata = {
                "session_id": session_id,
                "memory_type": memory_type,
                "role": role
            }
            metadata_json = json.dumps(metadata, ensure_ascii=False)
            
            # 存储到数据库
            self.db_manager.execute_query(
                """
                INSERT INTO memories 
                (id, content, type, role, session_id, timestamp, weight, last_accessed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (memory_id, content, memory_type, role, session_id, timestamp, weight, timestamp, metadata_json)
            )
            
            # 提交事务
            if self.db_manager.conn:
                self.db_manager.conn.commit()
            
            # 向量化和索引（异步进行，避免阻塞）
            try:
                vector = self._vectorize_text(content)
                if vector is not None:
                    # 存储向量到数据库
                    vector_id = f"vec_{memory_id}"
                    vector_blob = vector.tobytes()
                    
                    self.db_manager.execute_query(
                        """
                        INSERT INTO memory_vectors
                        (id, memory_id, vector, model_name, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (vector_id, memory_id, vector_blob, 
                         f"{self.vectorizer.model_type}/{self.vectorizer.model_name}" if self.vectorizer else "unknown", 
                         timestamp)
                    )
                    
                    # 添加到FAISS索引
                    if self.vector_index and self.vector_index.available:
                        success = self.vector_index.add_vectors(
                            vectors=vector.reshape(1, -1),
                            ids=[memory_id]
                        )
                        if success:
                            self.vector_index.save_index()
            except Exception as e:
                logger.warning(f"向量化处理失败，但记忆已保存: {e}")
            
            logger.debug(f"✅ 交互记忆存储成功: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"交互记忆存储失败: {e}")
            return None
    
    def _vectorize_text(self, text: str) -> np.ndarray:
        """
        将文本向量化
        
        参数:
            text: 输入文本
            
        返回:
            np.ndarray: 向量表示
        """
        try:
            # 使用向量化器将文本转换为向量
            vector = self.vectorizer.encode(text)
            return vector
        except Exception as e:
            logger.error(f"文本向量化失败: {e}")
            return None
    
    def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索与查询文本相似的记忆
        
        参数:
            query: 查询文本
            limit: 返回结果数量
            
        返回:
            List[Dict[str, Any]]: 相似记忆列表
        """
        try:
            # 对查询文本进行向量化
            query_vector = self._vectorize_text(query)
            
            if query_vector is None:
                logger.error("查询向量化失败")
                return []
            
            # 在向量索引中搜索相似向量
            memory_ids, scores = self.vector_index.search(
                query_vector.reshape(1, -1), 
                k=limit
            )
            
            if not memory_ids:
                logger.info(f"未找到与查询相似的记忆: {query[:30]}...")
                return []
            
            # 从数据库中获取记忆详情
            placeholders = ','.join(['?'] * len(memory_ids))
            results = self.db_manager.query(
                f"""
                SELECT m.id as memory_id, m.content, m.role as source, m.timestamp as created_at, 
                       m.weight as importance, m.metadata
                FROM memories m
                WHERE m.id IN ({placeholders})
                ORDER BY m.timestamp DESC
                """,
                memory_ids
            )
            
            # 构建结果列表
            memories = []
            for i, row in enumerate(results):
                # 查找对应的相似度分数
                score = 0.0
                for j, mid in enumerate(memory_ids):
                    if mid == row[0]:  # memory_id
                        score = scores[j]
                        break
                
                # 解析元数据
                try:
                    metadata = json.loads(row[5]) if row[5] else {}
                except:
                    metadata = {}
                
                # 添加到结果列表
                memories.append({
                    "memory_id": row[0],
                    "content": row[1],
                    "source": row[2],
                    "created_at": row[3],
                    "timestamp": datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M:%S'),
                    "importance": row[4],
                    "similarity": score,
                    "metadata": metadata
                })
            
            # 按相似度排序
            memories.sort(key=lambda x: x["similarity"], reverse=True)
            
            logger.info(f"找到 {len(memories)} 条与查询相似的记忆")
            return memories
            
        except Exception as e:
            logger.error(f"搜索相似记忆失败: {e}")
            return []
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定ID的记忆
        
        参数:
            memory_id: 记忆ID
            
        返回:
            Optional[Dict[str, Any]]: 记忆详情，如果不存在则返回None
        """
        try:
            result = self.db_manager.query(
                """
                SELECT id as memory_id, content, role as source, timestamp as created_at, 
                       weight as importance, metadata
                FROM memories
                WHERE id = ?
                """,
                (memory_id,)
            )
            
            if not result:
                logger.warning(f"未找到记忆: {memory_id}")
                return None
            
            row = result[0]
            
            # 解析元数据
            try:
                metadata = json.loads(row[5]) if row[5] else {}
            except:
                metadata = {}
            
            # 构建记忆详情
            memory = {
                "memory_id": row[0],
                "content": row[1],
                "source": row[2],
                "created_at": row[3],
                "timestamp": datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M:%S'),
                "importance": row[4],
                "metadata": metadata
            }
            
            return memory
            
        except Exception as e:
            logger.error(f"获取记忆失败: {e}")
            return None
    
    def update_memory_importance(self, memory_id: str, importance: float) -> bool:
        """
        更新记忆的重要性分数
        
        参数:
            memory_id: 记忆ID
            importance: 新的重要性分数，0-1之间
            
        返回:
            bool: 是否更新成功
        """
        if self.db_manager is None:
            logger.error("数据库管理器未初始化，无法更新记忆")
            return False
            
        try:
            # 限制重要性分数范围
            importance = max(0.0, min(1.0, importance))
            
            # 更新数据库
            self.db_manager.execute_query(
                """
                UPDATE memories
                SET weight = ?
                WHERE id = ?
                """,
                (importance, memory_id)
            )
            
            # 提交事务
            if self.db_manager.conn:
                self.db_manager.conn.commit()
            
            logger.info(f"更新记忆重要性成功: {memory_id}, 新重要性: {importance}")
            return True
            
        except Exception as e:
            logger.error(f"更新记忆重要性失败: {e}")
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        删除指定ID的记忆
        
        参数:
            memory_id: 记忆ID
            
        返回:
            bool: 是否删除成功
        """
        if self.db_manager is None:
            logger.error("数据库管理器未初始化，无法删除记忆")
            return False
            
        try:
            # 从数据库中删除记忆
            self.db_manager.execute_query(
                "DELETE FROM memories WHERE id = ?",
                (memory_id,)
            )
            
            # 删除对应的向量
            self.db_manager.execute_query(
                "DELETE FROM memory_vectors WHERE memory_id = ?",
                (memory_id,)
            )
            
            # 提交事务
            if self.db_manager.conn:
                self.db_manager.conn.commit()
            
            # 从向量索引中删除（如果可用）
            if self.vector_index and self.vector_index.available:
                success = self.vector_index.delete_vectors([memory_id])
                if success:
                    self.vector_index.save_index()
            
            logger.info(f"删除记忆成功: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除记忆失败: {e}")
            return False
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的记忆
        
        参数:
            limit: 返回结果数量
            
        返回:
            List[Dict[str, Any]]: 记忆列表
        """
        try:
            results = self.db_manager.query(
                """
                SELECT id as memory_id, content, role as source, timestamp as created_at, 
                       weight as importance, metadata
                FROM memories
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,)
            )
            
            memories = []
            for row in results:
                # 解析元数据
                try:
                    metadata = json.loads(row[5]) if row[5] else {}
                except:
                    metadata = {}
                
                # 添加到结果列表
                memories.append({
                    "memory_id": row[0],
                    "content": row[1],
                    "source": row[2],
                    "created_at": row[3],
                    "timestamp": datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M:%S'),
                    "importance": row[4],
                    "metadata": metadata
                })
            
            logger.info(f"获取最近 {len(memories)} 条记忆")
            return memories
            
        except Exception as e:
            logger.error(f"获取最近记忆失败: {e}")
            return []
    
    def get_memories_by_ids(self, memory_ids: List[str]) -> List[Dict[str, Any]]:
        """
        根据ID列表批量获取记忆（兼容EstiaMemorySystem接口）
        
        参数:
            memory_ids: 记忆ID列表
            
        返回:
            List[Dict[str, Any]]: 记忆列表
        """
        if not memory_ids or not self.db_manager:
            return []
        
        try:
            placeholders = ','.join(['?' for _ in memory_ids])
            results = self.db_manager.query(f"""
                SELECT id, content, type, role, session_id, timestamp, weight, group_id, summary, metadata
                FROM memories WHERE id IN ({placeholders})
                ORDER BY timestamp DESC
            """, memory_ids)
            
            memories = []
            for row in results:
                # 解析元数据
                try:
                    metadata = json.loads(row[9]) if row[9] else {}
                except:
                    metadata = {}
                
                memories.append({
                    'memory_id': row[0],
                    'content': row[1], 
                    'type': row[2],
                    'role': row[3],
                    'session_id': row[4] or "",
                    'timestamp': row[5],
                    'weight': row[6] or 5.0,
                    'group_id': row[7] or "",
                    'summary': row[8] or "",
                    'metadata': metadata
                })
            
            logger.debug(f"批量获取 {len(memories)} 条记忆")
            return memories
            
        except Exception as e:
            logger.error(f"批量获取记忆失败: {e}")
            return []
    
    def add_association(self, source_id: str, target_id: str, 
                       association_type: str = "related", 
                       strength: float = 0.5) -> bool:
        """
        添加记忆之间的关联
        
        参数:
            source_id: 源记忆ID
            target_id: 目标记忆ID
            association_type: 关联类型，如"related"、"cause_effect"等
            strength: 关联强度，0-1之间
            
        返回:
            bool: 是否添加成功
        """
        if self.db_manager is None:
            logger.error("数据库管理器未初始化，无法添加关联")
            return False
            
        try:
            # 生成关联ID
            association_id = str(uuid.uuid4())
            
            # 获取当前时间戳
            timestamp = int(time.time())
            
            # 添加关联
            self.db_manager.execute_query(
                """
                INSERT INTO memory_association
                (id, source_key, target_key, association_type, strength, created_at, last_activated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (association_id, source_id, target_id, association_type, strength, timestamp, timestamp)
            )
            
            # 提交事务
            if self.db_manager.conn:
                self.db_manager.conn.commit()
            
            logger.info(f"添加记忆关联成功: {source_id} -> {target_id}, 类型: {association_type}")
            return True
            
        except Exception as e:
            logger.error(f"添加记忆关联失败: {e}")
            return False
    
    def get_associated_memories(self, memory_id: str, 
                              association_type: str = None) -> List[Dict[str, Any]]:
        """
        获取与指定记忆相关联的记忆
        
        参数:
            memory_id: 记忆ID
            association_type: 关联类型，如果为None则获取所有类型
            
        返回:
            List[Dict[str, Any]]: 关联记忆列表
        """
        try:
            query = """
                SELECT a.id as association_id, a.source_key, a.target_key, 
                       a.association_type, a.strength, a.created_at,
                       m.content, m.role as source, m.weight as importance, m.metadata
                FROM memory_association a
                JOIN memories m ON a.target_key = m.id
                WHERE a.source_key = ?
            """
            
            params = [memory_id]
            
            if association_type:
                query += " AND a.association_type = ?"
                params.append(association_type)
                
            query += " ORDER BY a.strength DESC"
            
            results = self.db_manager.query(query, params)
            
            associations = []
            for row in results:
                # 解析元数据
                try:
                    metadata = json.loads(row[9]) if row[9] else {}
                except:
                    metadata = {}
                
                # 添加到结果列表
                associations.append({
                    "association_id": row[0],
                    "source_id": row[1],
                    "target_id": row[2],
                    "association_type": row[3],
                    "strength": row[4],
                    "created_at": row[5],
                    "content": row[6],
                    "source": row[7],
                    "importance": row[8],
                    "metadata": metadata
                })
            
            logger.info(f"获取记忆关联成功: {memory_id}, 找到 {len(associations)} 条关联")
            return associations
            
        except Exception as e:
            logger.error(f"获取记忆关联失败: {e}")
            return []
    
    def close(self):
        """关闭记忆存储管理器，保存所有数据"""
        try:
            # 保存向量索引
            if self.vector_index:
                self.vector_index.save_index()
                
            # 关闭数据库连接
            if self.db_manager:
                self.db_manager.close()
                
            logger.info("记忆存储管理器已关闭")
        except Exception as e:
            logger.error(f"关闭记忆存储管理器失败: {e}")

# 模块测试代码
if __name__ == "__main__":
    print("测试记忆存储管理器...")
    
    # 使用测试数据库和索引
    test_db_path = os.path.join("assets", "test_memory.db")
    test_index_path = os.path.join("data", "vectors", "test_memory_index.bin")
    
    # 初始化记忆存储管理器
    memory_store = MemoryStore(
        db_path=test_db_path,
        index_path=test_index_path
    )
    
    # 测试添加记忆
    print("\n1. 测试添加记忆")
    test_memories = [
        "今天天气真好，阳光明媚",
        "我喜欢编程，尤其是Python和人工智能",
        "记忆系统是AI助手的重要组成部分",
        "向量数据库可以高效地进行相似性搜索"
    ]
    
    memory_ids = []
    for i, content in enumerate(test_memories):
        memory_id = memory_store.add_memory(
            content=content,
            source="test",
            importance=0.5 + i * 0.1,
            metadata={"test_index": i}
        )
        if memory_id:
            memory_ids.append(memory_id)
            print(f"添加记忆成功: {memory_id}, 内容: {content}")
    
    # 测试获取记忆
    print("\n2. 测试获取记忆")
    if memory_ids:
        memory = memory_store.get_memory(memory_ids[0])
        if memory:
            print(f"获取记忆成功:")
            print(f"  ID: {memory['memory_id']}")
            print(f"  内容: {memory['content']}")
            print(f"  时间: {memory['timestamp']}")
            print(f"  重要性: {memory['importance']}")
            print(f"  元数据: {memory['metadata']}")
    
    # 测试搜索相似记忆
    print("\n3. 测试搜索相似记忆")
    query = "AI系统中的记忆功能"
    similar_memories = memory_store.search_similar(query, limit=3)
    
    print(f"查询: {query}")
    print(f"找到 {len(similar_memories)} 条相似记忆:")
    
    for i, memory in enumerate(similar_memories):
        print(f"\n结果 {i+1}:")
        print(f"  ID: {memory['memory_id']}")
        print(f"  内容: {memory['content']}")
        print(f"  相似度: {memory['similarity']:.4f}")
        print(f"  重要性: {memory['importance']}")
    
    # 测试添加关联
    print("\n4. 测试添加关联")
    if len(memory_ids) >= 2:
        success = memory_store.add_association(
            source_id=memory_ids[0],
            target_id=memory_ids[1],
            association_type="related",
            strength=0.8
        )
        print(f"添加关联: {'成功' if success else '失败'}")
        
        # 获取关联记忆
        associations = memory_store.get_associated_memories(memory_ids[0])
        print(f"获取关联记忆: {len(associations)} 条")
        
        for i, assoc in enumerate(associations):
            print(f"\n关联 {i+1}:")
            print(f"  关联ID: {assoc['association_id']}")
            print(f"  目标ID: {assoc['target_id']}")
            print(f"  内容: {assoc['content']}")
            print(f"  关联类型: {assoc['association_type']}")
            print(f"  强度: {assoc['strength']}")
    
    # 测试获取最近记忆
    print("\n5. 测试获取最近记忆")
    recent_memories = memory_store.get_recent_memories(limit=5)
    print(f"获取最近 {len(recent_memories)} 条记忆:")
    
    for i, memory in enumerate(recent_memories):
        print(f"\n记忆 {i+1}:")
        print(f"  ID: {memory['memory_id']}")
        print(f"  内容: {memory['content']}")
        print(f"  时间: {memory['timestamp']}")
    
    # 关闭记忆存储管理器
    memory_store.close()
    print("\n测试完成，记忆存储管理器已关闭")
