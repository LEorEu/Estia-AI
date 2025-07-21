import os
import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

class FAISSSearchEngine:
    def __init__(self, index_path: str, dimension: int, cache_dir: Optional[str] = None, index_type: str = "Flat"):
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS库未安装")
        
        self.index_path = index_path
        self.dimension = dimension
        self.cache_dir = cache_dir
        self.index_type = index_type
        
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
        
        # 尝试加载现有索引，如果不存在则创建新索引
        self.memory_keys = []
        self.vector_count = 0
        
        if os.path.exists(index_path):
            self._load_index()
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            logger.info(f"创建新的FAISS索引，维度: {self.dimension}")
    
    def add_vector(self, memory_key: str, vector: np.ndarray) -> bool:
        try:
            if vector.ndim == 1:
                vector = vector.reshape(1, -1)
            
            if vector.shape[1] != self.dimension:
                return False
            
            self.index.add(vector.astype(np.float32))
            self.memory_keys.append(memory_key)
            self.vector_count += 1
            
            return True
        except Exception as e:
            return False
    
    def search(self, query_vector: np.ndarray, k: int = 5, threshold: float = 0.0) -> List[Tuple[str, float]]:
        try:
            if self.index is None or self.vector_count == 0:
                return []
            
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            
            if query_vector.shape[1] != self.dimension:
                return []
            
            distances, indices = self.index.search(query_vector.astype(np.float32), k)
            
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx == -1:
                    break
                
                similarity = np.exp(-distance)
                memory_key = self.memory_keys[idx] if idx < len(self.memory_keys) else f"unknown_{idx}"
                results.append((memory_key, similarity))
            
            return results
        except Exception as e:
            return []
    
    def _load_index(self):
        """加载现有的FAISS索引文件"""
        try:
            import pickle
            
            # 加载FAISS索引
            self.index = faiss.read_index(self.index_path)
            logger.info(f"成功加载FAISS索引: {self.index_path}")
            
            # 加载元数据（记忆键和向量数量）
            meta_path = self.index_path + ".meta"
            if os.path.exists(meta_path):
                with open(meta_path, "rb") as f:
                    meta_data = pickle.load(f)
                    
                    # 处理新格式的元数据
                    if "id_map" in meta_data:
                        id_map = meta_data["id_map"]
                        self.vector_count = len(id_map)
                        # 将id_map转换为memory_keys列表
                        self.memory_keys = [""] * self.vector_count
                        for idx, memory_id in id_map.items():
                            if isinstance(idx, (int, np.integer)) and 0 <= idx < self.vector_count:
                                self.memory_keys[int(idx)] = memory_id
                        logger.info(f"加载新格式元数据: {self.vector_count}个向量，{len(self.memory_keys)}个键")
                    
                    # 处理旧格式的元数据
                    elif "memory_keys" in meta_data:
                        self.memory_keys = meta_data.get("memory_keys", [])
                        self.vector_count = meta_data.get("vector_count", 0)
                        logger.info(f"加载旧格式元数据: {self.vector_count}个向量，{len(self.memory_keys)}个键")
                    
                    else:
                        # 没有识别的格式，从索引推断
                        self.vector_count = self.index.ntotal
                        self.memory_keys = [f"unknown_{i}" for i in range(self.vector_count)]
                        logger.warning(f"元数据格式未知，从索引推断: {self.vector_count}个向量")
            else:
                # 如果没有元数据文件，从索引推断
                self.vector_count = self.index.ntotal
                self.memory_keys = [f"unknown_{i}" for i in range(self.vector_count)]
                logger.warning(f"元数据文件不存在，推断向量数量: {self.vector_count}")
                
        except Exception as e:
            logger.error(f"加载FAISS索引失败: {e}")
            # 创建新索引作为备用
            self.index = faiss.IndexFlatL2(self.dimension)
            self.memory_keys = []
            self.vector_count = 0
    
    def save_index(self):
        """保存FAISS索引和元数据"""
        try:
            import pickle
            
            # 保存FAISS索引
            faiss.write_index(self.index, self.index_path)
            
            # 保存元数据
            meta_path = self.index_path + ".meta"
            meta_data = {
                "memory_keys": self.memory_keys,
                "vector_count": self.vector_count,
                "dimension": self.dimension,
                "index_type": self.index_type
            }
            with open(meta_path, "wb") as f:
                pickle.dump(meta_data, f)
                
            logger.info(f"保存FAISS索引成功: {self.index_path}")
            return True
        except Exception as e:
            logger.error(f"保存FAISS索引失败: {e}")
            return False
