"""
向量索引管理器 - 负责FAISS向量索引的初始化、管理和搜索
"""

import os
import numpy as np
import pickle
import time
import logging
from typing import List, Dict, Any, Optional, Tuple, Union

# 尝试导入FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS库未安装，向量搜索功能将不可用。请安装FAISS: pip install faiss-cpu 或 pip install faiss-gpu")

# 导入日志工具
try:
    from core.utils.logger import get_logger
    logger = get_logger("estia.memory.vector")
except ImportError:
    # 如果还没有日志工具，使用标准日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("estia.memory.vector")

class VectorIndexManager:
    """向量索引管理器类，负责FAISS向量索引的初始化、管理和搜索"""
    
    def __init__(self, index_path=None, vector_dim=768, index_type="flat"):
        """
        初始化向量索引管理器
        
        参数:
            index_path: 索引文件路径，如果为None则使用默认路径
            vector_dim: 向量维度，默认为768（适用于大多数Transformer模型）
            index_type: 索引类型，可选值为"flat"（精确搜索）、"ivf"（近似搜索）、"hnsw"（图索引）
        """
        if not FAISS_AVAILABLE:
            logger.error("FAISS库未安装，向量索引管理器无法正常工作")
            self.available = False
            return
            
        self.available = True
        self.vector_dim = vector_dim
        self.index_type = index_type
        
        if index_path is None:
            # 默认路径为data/vectors/faiss_index.bin
            index_path = os.path.join("data", "vectors", "faiss_index.bin")
            
        # 确保目录存
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
            
        self.index_path = index_path
        self.index = None
        self.id_map = {}  # 映射内部索引ID到外部记忆ID
        self.next_id = 0  # 下一个可用的内部索引ID
        
        # 元数据
        self.metadata = {
            "created_at": time.time(),
            "last_modified": time.time(),
            "vector_dim": vector_dim,
            "index_type": index_type,
            "vector_count": 0
        }
        
        logger.info(f"向量索引管理器初始化，使用索引: {index_path}")
        
    def create_index(self):
        """
        创建新的FAISS索引
        
        返回:
            bool: 是否成功创建
        """
        if not self.available:
            logger.error("FAISS库未安装，无法创建索引")
            return False
            
        try:
            # 根据索引类型创建不同的索引
            if self.index_type == "flat":
                # 创建精确搜索索引（L2距离）
                self.index = faiss.IndexFlatL2(self.vector_dim)
                logger.info(f"创建FAISS Flat索引，维度: {self.vector_dim}")
            elif self.index_type == "ivf":
                # 创建IVF索引（近似搜索，需要训练）
                quantizer = faiss.IndexFlatL2(self.vector_dim)
                nlist = 100  # 聚类中心数量
                self.index = faiss.IndexIVFFlat(quantizer, self.vector_dim, nlist, faiss.METRIC_L2)
                logger.info(f"创建FAISS IVF索引，维度: {self.vector_dim}，聚类中心: {nlist}")
            elif self.index_type == "hnsw":
                # 创建HNSW索引（图索引，高效近似搜索）
                self.index = faiss.IndexHNSWFlat(self.vector_dim, 32)  # 32是每个节点的连接数
                logger.info(f"创建FAISS HNSW索引，维度: {self.vector_dim}")
            else:
                # 默认使用Flat索引
                self.index = faiss.IndexFlatL2(self.vector_dim)
                logger.info(f"创建默认FAISS Flat索引，维度: {self.vector_dim}")
                
            # 重置ID映射
            self.id_map = {}
            self.next_id = 0
            
            # 更新元数据
            self.metadata["created_at"] = time.time()
            self.metadata["last_modified"] = time.time()
            self.metadata["vector_count"] = 0
            
            return True
        except Exception as e:
            logger.error(f"创建FAISS索引失败: {e}")
            return False
    
    def load_index(self):
        """
        加载已有的FAISS索引
        
        返回:
            bool: 是否成功加载
        """
        if not self.available:
            logger.error("FAISS库未安装，无法加载索引")
            return False
            
        if not os.path.exists(self.index_path):
            logger.warning(f"索引文件不存在: {self.index_path}，将创建新索引")
            return self.create_index()
            
        try:
            # 加载索引
            self.index = faiss.read_index(self.index_path)
            
            # 加载ID映射和元数据
            metadata_path = self.index_path + ".meta"
            if os.path.exists(metadata_path):
                with open(metadata_path, "rb") as f:
                    data = pickle.load(f)
                    self.id_map = data.get("id_map", {})
                    self.next_id = data.get("next_id", 0)
                    self.metadata = data.get("metadata", self.metadata)
                    
                    # 更新维度信息
                    self.vector_dim = self.metadata.get("vector_dim", self.vector_dim)
                    
                    logger.info(f"加载索引元数据成功，包含 {self.metadata['vector_count']} 个向量")
            else:
                logger.warning(f"索引元数据文件不存在: {metadata_path}")
                
            logger.info(f"加载FAISS索引成功，维度: {self.index.d}")
            return True
        except Exception as e:
            logger.error(f"加载FAISS索引失败: {e}")
            return False
    
    def save_index(self):
        """
        保存FAISS索引到文件
        
        返回:
            bool: 是否成功保存
        """
        if not self.available or self.index is None:
            logger.error("FAISS索引未初始化，无法保存")
            return False
            
        try:
            # 更新元数据
            self.metadata["last_modified"] = time.time()
            self.metadata["vector_count"] = self.index.ntotal
            
            # 保存索引
            faiss.write_index(self.index, self.index_path)
            
            # 保存ID映射和元数据
            metadata_path = self.index_path + ".meta"
            with open(metadata_path, "wb") as f:
                pickle.dump({
                    "id_map": self.id_map,
                    "next_id": self.next_id,
                    "metadata": self.metadata
                }, f)
                
            logger.info(f"保存FAISS索引成功: {self.index_path}")
            return True
        except Exception as e:
            logger.error(f"保存FAISS索引失败: {e}")
            return False
    
    def add_vectors(self, vectors: np.ndarray, ids: List[str]) -> bool:
        """
        添加向量到索引
        
        参数:
            vectors: 向量数组，形状为 (n, vector_dim)
            ids: 与向量对应的外部ID列表
            
        返回:
            bool: 是否成功添加
        """
        if not self.available or self.index is None:
            logger.error("FAISS索引未初始化，无法添加向量")
            return False
            
        if len(vectors) != len(ids):
            logger.error(f"向量数量 ({len(vectors)}) 与ID数量 ({len(ids)}) 不匹配")
            return False
            
        if len(vectors) == 0:
            logger.warning("没有要添加的向量")
            return True
            
        try:
            # 确保向量是float32类型，FAISS要求
            vectors = vectors.astype('float32')
            
            # 检查向量维度
            if vectors.shape[1] != self.vector_dim:
                logger.error(f"向量维度不匹配: 预期 {self.vector_dim}，实际 {vectors.shape[1]}")
                return False
                
            # 创建内部索引ID
            internal_ids = np.array([self.next_id + i for i in range(len(vectors))], dtype=np.int64)
            
            # 更新ID映射
            for i, external_id in enumerate(ids):
                self.id_map[internal_ids[i]] = external_id
                
            # 添加向量到索引
            # 注意：不是所有索引类型都支持add_with_ids，例如IndexFlatL2只支持add
            # 我们需要根据索引类型选择正确的添加方法
            index_type_name = type(self.index).__name__
            logger.debug(f"索引类型: {index_type_name}")
            
            # 检查索引类型是否支持add_with_ids
            supports_add_with_ids = False
            try:
                # 尝试获取add_with_ids方法
                if hasattr(self.index, 'add_with_ids'):
                    # 对于某些索引类型，虽然有add_with_ids方法但实际不支持
                    # 我们需要进一步检查索引类型
                    if not (index_type_name == "IndexFlatL2" or 
                            index_type_name == "IndexFlat" or
                            index_type_name == "IndexHNSWFlat"):
                        supports_add_with_ids = True
            except:
                supports_add_with_ids = False
            
            # 根据索引类型选择添加方法
            if supports_add_with_ids:
                logger.debug(f"使用add_with_ids添加向量，数量: {len(vectors)}")
                self.index.add_with_ids(vectors, internal_ids)
            else:
                logger.debug(f"使用add添加向量，数量: {len(vectors)}")
                self.index.add(vectors)
                
            # 更新下一个可用ID
            self.next_id += len(vectors)
            
            # 更新元数据
            self.metadata["last_modified"] = time.time()
            self.metadata["vector_count"] = self.index.ntotal
            
            logger.info(f"成功添加 {len(vectors)} 个向量到索引")
            return True
        except Exception as e:
            logger.error(f"添加向量到索引失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> Tuple[List[str], List[float]]:
        """
        搜索最相似的向量
        
        参数:
            query_vector: 查询向量，形状为 (vector_dim,) 或 (1, vector_dim)
            k: 返回的最相似向量数量
            
        返回:
            Tuple[List[str], List[float]]: 外部ID列表和对应的相似度分数
        """
        if not self.available or self.index is None:
            logger.error("FAISS索引未初始化，无法搜索")
            return [], []
            
        try:
            # 确保查询向量是二维的
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
                
            # 检查向量维度
            if query_vector.shape[1] != self.vector_dim:
                logger.error(f"查询向量维度不匹配: 预期 {self.vector_dim}，实际 {query_vector.shape[1]}")
                return [], []
                
            # 执行搜索
            distances, indices = self.index.search(query_vector, k)
            
            # 转换内部索引ID为外部ID
            external_ids = []
            scores = []
            
            for i, idx in enumerate(indices[0]):
                if idx != -1 and idx in self.id_map:  # -1表示无效结果
                    external_ids.append(self.id_map[idx])
                    # 将距离转换为相似度分数（1 - 归一化距离）
                    distance = distances[0][i]
                    if distance > 0:
                        score = 1.0 / (1.0 + distance)  # 将距离转换为0-1之间的相似度
                    else:
                        score = 1.0  # 完全匹配
                    scores.append(score)
            
            logger.debug(f"搜索完成，找到 {len(external_ids)} 个结果")
            return external_ids, scores
        except Exception as e:
            logger.error(f"搜索向量失败: {e}")
            return [], []
    
    def batch_search(self, query_vectors: np.ndarray, k: int = 5) -> List[Tuple[List[str], List[float]]]:
        """
        批量搜索最相似的向量
        
        参数:
            query_vectors: 查询向量数组，形状为 (n, vector_dim)
            k: 每个查询返回的最相似向量数量
            
        返回:
            List[Tuple[List[str], List[float]]]: 每个查询的结果，包含外部ID列表和对应的相似度分数
        """
        if not self.available or self.index is None:
            logger.error("FAISS索引未初始化，无法搜索")
            return []
            
        try:
            # 检查向量维度
            if query_vectors.shape[1] != self.vector_dim:
                logger.error(f"查询向量维度不匹配: 预期 {self.vector_dim}，实际 {query_vectors.shape[1]}")
                return []
                
            # 执行搜索
            distances, indices = self.index.search(query_vectors, k)
            
            results = []
            for i in range(len(query_vectors)):
                external_ids = []
                scores = []
                
                for j, idx in enumerate(indices[i]):
                    if idx != -1 and idx in self.id_map:
                        external_ids.append(self.id_map[idx])
                        distance = distances[i][j]
                        if distance > 0:
                            score = 1.0 / (1.0 + distance)
                        else:
                            score = 1.0
                        scores.append(score)
                
                results.append((external_ids, scores))
            
            logger.debug(f"批量搜索完成，处理了 {len(query_vectors)} 个查询")
            return results
        except Exception as e:
            logger.error(f"批量搜索向量失败: {e}")
            return []
    
    def delete_vectors(self, ids: List[str]) -> bool:
        """
        从索引中删除向量
        
        参数:
            ids: 要删除的外部ID列表
            
        返回:
            bool: 是否成功删除
        """
        if not self.available or self.index is None:
            logger.error("FAISS索引未初始化，无法删除向量")
            return False
            
        try:
            # 查找内部索引ID
            internal_ids = []
            for internal_id, external_id in self.id_map.items():
                if external_id in ids:
                    internal_ids.append(internal_id)
            
            if not internal_ids:
                logger.warning(f"未找到要删除的向量ID: {ids}")
                return False
                
            # 检查索引是否支持删除
            if hasattr(self.index, 'remove_ids'):
                # 转换为numpy数组
                internal_ids_np = np.array(internal_ids, dtype=np.int64)
                self.index.remove_ids(internal_ids_np)
                
                # 更新ID映射
                for internal_id in internal_ids:
                    if internal_id in self.id_map:
                        del self.id_map[internal_id]
                
                # 更新元数据
                self.metadata["last_modified"] = time.time()
                self.metadata["vector_count"] = self.index.ntotal
                
                logger.info(f"成功删除 {len(internal_ids)} 个向量")
                return True
            else:
                logger.error("当前索引类型不支持删除操作")
                return False
        except Exception as e:
            logger.error(f"删除向量失败: {e}")
            return False
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        获取索引信息
        
        返回:
            Dict[str, Any]: 索引信息字典
        """
        if not self.available or self.index is None:
            logger.error("FAISS索引未初始化，无法获取信息")
            return {}
            
        info = {
            "index_type": self.index_type,
            "vector_dim": self.vector_dim,
            "vector_count": self.index.ntotal,
            "id_map_size": len(self.id_map),
            "created_at": self.metadata.get("created_at", 0),
            "last_modified": self.metadata.get("last_modified", 0),
            "index_path": self.index_path
        }
        
        return info
    
    def train_index(self, training_vectors: np.ndarray) -> bool:
        """
        训练索引（仅对需要训练的索引类型有效，如IVF）
        
        参数:
            training_vectors: 训练用的向量数组
            
        返回:
            bool: 是否成功训练
        """
        if not self.available or self.index is None:
            logger.error("FAISS索引未初始化，无法训练")
            return False
            
        # 检查索引是否需要训练
        if not hasattr(self.index, 'train'):
            logger.info("当前索引类型不需要训练")
            return True
            
        try:
            # 检查向量维度
            if training_vectors.shape[1] != self.vector_dim:
                logger.error(f"训练向量维度不匹配: 预期 {self.vector_dim}，实际 {training_vectors.shape[1]}")
                return False
                
            # 训练索引
            self.index.train(training_vectors)
            
            # 更新元数据
            self.metadata["last_modified"] = time.time()
            
            logger.info(f"成功使用 {len(training_vectors)} 个向量训练索引")
            return True
        except Exception as e:
            logger.error(f"训练索引失败: {e}")
            return False
    
    def get_total_count(self) -> int:
        """
        获取索引中的向量总数
        
        返回:
            int: 向量总数，如果索引未初始化则返回0
        """
        if not self.available or self.index is None:
            return 0
        
        try:
            return self.index.ntotal
        except Exception as e:
            logger.error(f"获取向量总数失败: {e}")
            return 0
    
    def clear(self) -> bool:
        """
        清空索引中的所有向量
        
        返回:
            bool: 是否成功清空
        """
        if not self.available:
            logger.error("FAISS库未安装，无法清空索引")
            return False
            
        try:
            # 重新创建索引
            success = self.create_index()
            if success:
                logger.info("成功清空向量索引")
                return True
            else:
                logger.error("清空向量索引失败")
                return False
        except Exception as e:
            logger.error(f"清空向量索引失败: {e}")
            return False
    
    def close(self):
        """
        关闭索引管理器
        """
        try:
            if self.available and self.index is not None:
                # 保存索引
                self.save_index()
                
            # 清理资源
            self.index = None
            self.id_map = {}
            self.available = False
            
            logger.info("向量索引管理器已关闭")
        except Exception as e:
            logger.error(f"关闭向量索引管理器失败: {e}")

# 模块测试代码
if __name__ == "__main__":
    import numpy as np
    
    print("测试向量索引管理器...")
    
    # 使用临时索引路径
    test_index_path = os.path.join("data", "vectors", "test_index.bin")
    
    # 创建向量索引管理器
    vector_manager = VectorIndexManager(test_index_path, vector_dim=128)
    
    if not vector_manager.available:
        print("FAISS库未安装，测试终止")
        exit(1)
    
    # 创建索引
    success = vector_manager.create_index()
    print(f"创建索引: {'成功' if success else '失败'}")
    
    # 生成测试向量
    num_vectors = 100
    test_vectors = np.random.random((num_vectors, 128)).astype('float32')
    test_ids = [f"test_id_{i}" for i in range(num_vectors)]
    
    # 添加向量
    success = vector_manager.add_vectors(test_vectors, test_ids)
    print(f"添加向量: {'成功' if success else '失败'}")
    
    # 保存索引
    success = vector_manager.save_index()
    print(f"保存索引: {'成功' if success else '失败'}")
    
    # 搜索向量
    query_vector = np.random.random((1, 128)).astype('float32')
    ids, scores = vector_manager.search(query_vector, k=5)
    print(f"搜索结果: {len(ids)} 个匹配项")
    for i, (id, score) in enumerate(zip(ids, scores)):
        print(f"  {i+1}. ID: {id}, 相似度: {score:.4f}")
    
    # 获取索引信息
    info = vector_manager.get_index_info()
    print("\n索引信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n测试完成")
