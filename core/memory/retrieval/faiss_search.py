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
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.memory_keys = []
        self.vector_count = 0
    
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

# 向后兼容别名
FAISSRetriever = FAISSSearchEngine
