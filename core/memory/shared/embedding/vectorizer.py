"""
文本向量化模块 - 负责将文本转换为向量表示
"""

import os
import numpy as np
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import time
from pathlib import Path

# 尝试导入日志工具
try:
    from core.utils.logger import get_logger
    logger = get_logger("estia.memory.embedding.vectorizer")
except ImportError:
    # 如果还没有日志工具，使用标准日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("estia.memory.embedding.vectorizer")

# 尝试导入缓存模块
try:
    from .cache import EnhancedMemoryCache
    EmbeddingCache = EnhancedMemoryCache  # 使用新的增强缓存
except ImportError:
    logger.warning("无法导入EnhancedMemoryCache，将不使用缓存功能")
    EmbeddingCache = None

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    计算两个向量的余弦相似度
    
    参数:
        vec1: 第一个向量
        vec2: 第二个向量
        
    返回:
        余弦相似度值 (0-1之间)
    """
    try:
        # 确保向量是numpy数组
        vec1 = np.array(vec1, dtype=np.float32)
        vec2 = np.array(vec2, dtype=np.float32)
        
        # 计算余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
        
    except Exception as e:
        logger.error(f"计算余弦相似度失败: {e}")
        return 0.0

class TextVectorizer:
    """
    文本向量化类，负责将文本转换为向量表示
    
    支持多种Embedding模型:
    - 本地模型 (sentence-transformers)
    - OpenAI API
    - 自定义模型
    """
    
    # 🔥 单例模式：全局唯一实例
    _instance = None
    _initialized = False
    
    # 支持的模型类型
    MODEL_TYPES = ["sentence-transformers", "openai", "custom"]
    
    # 默认模型配置
    DEFAULT_MODEL = "sentence-transformers"
    DEFAULT_MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"  # 使用阿里巴巴的Qwen模型
    
    def __new__(cls, *args, **kwargs):
        """单例模式：确保全局只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, model_type: Optional[str] = None, model_name: Optional[str] = None, 
                 api_key: Optional[str] = None, cache_dir: Optional[str] = None, 
                 use_cache: bool = True, device: str = "cpu"):
        """
        初始化文本向量化器
        
        参数:
            model_type: 模型类型，可选值为 "sentence-transformers", "openai", "custom"
            model_name: 模型名称，对于sentence-transformers是模型ID，对于openai是模型名称
            api_key: API密钥，用于OpenAI API
            cache_dir: 缓存目录，默认使用项目内部cache目录
            use_cache: 是否使用缓存
            device: 设备，可选值为 "cpu", "cuda", "mps"（对于Apple Silicon）
        """
        # 🔥 单例模式：只初始化一次
        if self._initialized:
            logger.debug("TextVectorizer已初始化，跳过重复初始化")
            return
            
        self.model_type = model_type or self.DEFAULT_MODEL
        self.model_name = model_name or self.DEFAULT_MODEL_NAME
        if self.model_name is None:
            self.model_name = self.DEFAULT_MODEL_NAME
            logger.warning("模型名称为None，使用默认模型")
        self.api_key = api_key
        self.device = device
        self.use_cache = use_cache and EmbeddingCache is not None
        
        # 🔥 优化：区分模型缓存和运行时缓存
        if cache_dir is None:
            # 运行时缓存使用data/memory/cache（保持现有数据）
            self.cache_dir = os.path.join("data", "memory", "cache")
        else:
            self.cache_dir = cache_dir
        
        # 模型缓存使用项目根目录的cache（避免网络下载）
        self.model_cache_dir = str(Path(__file__).parent.parent.parent.parent.parent / "cache")
        
        # 初始化模型
        self.model = None
        self.vector_dim = 0
        
        # 初始化增强缓存
        self.cache = None
        if self.use_cache and EmbeddingCache is not None:
            self.cache = EmbeddingCache(cache_dir=self.cache_dir)
            logger.info("已启用增强版记忆缓存")
        
        # 🔥 新增：自动注册缓存适配器到统一缓存管理器
        self._register_cache_adapters()
        
        # 加载模型
        self._load_model()
        
        # 🔥 标记为已初始化
        self._initialized = True
        
        logger.info(f"文本向量化器初始化完成，使用模型: {self.model_type}/{self.model_name}")
        logger.info(f"缓存目录: {self.cache_dir}")
    
    def _register_cache_adapters(self) -> None:
        """自动注册缓存适配器到统一缓存管理器"""
        if not self.use_cache:
            return
            
        try:
            from ...shared.caching.cache_manager import UnifiedCacheManager
            from ...shared.caching.cache_adapters import EnhancedMemoryCacheAdapter
            
            unified_cache = UnifiedCacheManager.get_instance()
            
            # 检查是否已经注册了向量缓存适配器
            registered_caches = list(unified_cache.caches.keys())
            if "embedding_cache" not in registered_caches and self.cache:
                # 创建并注册向量缓存适配器
                vector_adapter = EnhancedMemoryCacheAdapter(
                    source_cache=self.cache,
                    cache_id="embedding_cache",
                    auto_register=False  # 手动注册，避免重复
                )
                unified_cache.register_cache(vector_adapter)
                logger.info("✅ 已自动注册向量缓存适配器到统一缓存管理器")
            else:
                logger.debug("向量缓存适配器已存在或无需注册")
                
        except Exception as e:
            logger.warning(f"注册缓存适配器失败: {e}")
            # 不影响主要功能，继续执行
    
    def _load_model(self) -> None:
        """加载Embedding模型"""
        if self.model_type == "sentence-transformers":
            self._load_sentence_transformers()
        elif self.model_type == "openai":
            self._load_openai()
        elif self.model_type == "custom":
            self._load_custom_model()
        else:
            logger.warning(f"未知的模型类型: {self.model_type}，将使用默认模型")
            self.model_type = self.DEFAULT_MODEL
            self._load_sentence_transformers()
    
    def _load_sentence_transformers(self) -> None:
        """加载sentence-transformers模型，使用项目内部缓存"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # 🔥 设置项目内部缓存环境（用于模型缓存）
            os.environ['HUGGINGFACE_HUB_CACHE'] = self.model_cache_dir
            os.environ['SENTENCE_TRANSFORMERS_HOME'] = self.model_cache_dir
            os.environ['HF_HOME'] = self.model_cache_dir
            
            logger.info(f"🔧 使用项目模型缓存目录: {self.model_cache_dir}")
            
            # 检查model_name是否有效
            if self.model_name is None:
                logger.error("模型名称未设置")
                raise ValueError("模型名称未设置")
            
            # 确保model_name是字符串
            if not isinstance(self.model_name, str):
                logger.error(f"模型名称类型错误: {type(self.model_name)}")
                self.model_name = str(self.model_name)
            
            logger.info(f"🔄 加载模型: {self.model_name}")
            
            # 🔥 首先检查本地模型是否存在
            expected_model_path = os.path.join(self.model_cache_dir, f"models--{self.model_name.replace('/', '--')}")
            
            if os.path.exists(expected_model_path):
                logger.info(f"🎯 发现本地模型: {expected_model_path}")
                # 设置为离线模式，强制使用本地模型
                os.environ['HF_HUB_OFFLINE'] = '1'
                os.environ['TRANSFORMERS_OFFLINE'] = '1'
                
                try:
                    self.model = SentenceTransformer(
                        self.model_name,
                        device=self.device,
                        cache_folder=self.model_cache_dir,
                        trust_remote_code=True
                    )
                    logger.info(f"✅ 成功加载本地模型: {self.model_name}")
                    
                except Exception as local_error:
                    logger.warning(f"本地模型加载失败: {local_error}")
                    # 清除离线设置，尝试在线加载
                    if 'HF_HUB_OFFLINE' in os.environ:
                        del os.environ['HF_HUB_OFFLINE']
                    if 'TRANSFORMERS_OFFLINE' in os.environ:
                        del os.environ['TRANSFORMERS_OFFLINE']
                    raise local_error
            else:
                logger.warning(f"本地模型不存在: {expected_model_path}")
                logger.info("🌐 尝试在线模式...")
                
                # 尝试多个镜像站和模型名称
                model_options = [
                    # 原始模型名称 + 镜像站
                    (self.model_name, 'https://hf-mirror.com'),
                    # 备用模型名称 + 镜像站
                    ('sentence-transformers/all-MiniLM-L6-v2', 'https://hf-mirror.com'),
                    # 原始模型名称 + 官方站点
                    (self.model_name, 'https://huggingface.co'),
                    # 备用模型名称 + 官方站点
                    ('sentence-transformers/all-MiniLM-L6-v2', 'https://huggingface.co'),
                ]
                
                model_loaded = False
                for model_name, endpoint in model_options:
                    try:
                        logger.info(f"🔄 尝试加载 {model_name} 从 {endpoint}")
                        os.environ['HF_ENDPOINT'] = endpoint
                        
                        self.model = SentenceTransformer(
                            model_name,
                            device=self.device,
                            cache_folder=self.model_cache_dir,
                            trust_remote_code=True
                        )
                        self.model_name = model_name  # 更新成功的模型名称
                        logger.info(f"✅ 在线模式加载成功: {model_name}")
                        model_loaded = True
                        break
                        
                    except Exception as online_error:
                        logger.warning(f"尝试 {model_name} 失败: {online_error}")
                        continue
                
                if not model_loaded:
                    logger.error("所有在线模型加载尝试都失败了")
                    raise RuntimeError("无法加载任何 sentence-transformers 模型")
            
            # 获取向量维度
            self.vector_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"✅ 模型初始化完成，向量维度: {self.vector_dim}")
            
        except ImportError:
            logger.error("未找到sentence-transformers库，请安装: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"加载sentence-transformers模型失败: {e}")
            raise
    
    def _load_openai(self) -> None:
        """加载OpenAI API"""
        try:
            import openai
            
            # 设置API密钥
            if self.api_key:
                openai.api_key = self.api_key
            elif "OPENAI_API_KEY" in os.environ:
                openai.api_key = os.environ["OPENAI_API_KEY"]
            else:
                logger.error("未提供OpenAI API密钥")
                raise ValueError("未提供OpenAI API密钥，请通过api_key参数或OPENAI_API_KEY环境变量设置")
            
            # 默认模型名称
            if not self.model_name:
                self.model_name = "text-embedding-ada-002"
            
            # 设置模型（实际上不需要预加载）
            self.model = openai
            
            # 根据模型设置向量维度
            model_dims = {
                "text-embedding-ada-002": 1536,
                "text-embedding-3-small": 1536,
                "text-embedding-3-large": 3072
            }
            self.vector_dim = model_dims.get(self.model_name, 1536)
            
            logger.info(f"OpenAI API配置成功，使用模型: {self.model_name}, 向量维度: {self.vector_dim}")
            
        except ImportError:
            logger.error("未找到openai库，请安装: pip install openai")
            raise
        except Exception as e:
            logger.error(f"配置OpenAI API失败: {e}")
            raise
    
    def _load_custom_model(self) -> None:
        """加载自定义模型"""
        # 这里可以实现加载自定义模型的逻辑
        # 例如基于其他框架的模型或自己训练的模型
        logger.warning("自定义模型加载未实现，请在子类中实现")
        raise NotImplementedError("自定义模型加载未实现")
    
    def encode(self, texts: Union[str, List[str]], 
               batch_size: int = 32, 
               show_progress: bool = False,
               memory_weights: Optional[Union[float, List[float]]] = None) -> np.ndarray:
        """
        将文本编码为向量
        
        参数:
            texts: 单个文本或文本列表
            batch_size: 批处理大小
            show_progress: 是否显示进度条
            memory_weights: 记忆重要性权重，用于智能缓存
            
        返回:
            np.ndarray: 文本向量，形状为 (n, vector_dim) 或 (vector_dim,)
        """
        if self.model is None:
            logger.error("模型未加载，无法编码文本")
            raise ValueError("模型未加载，无法编码文本")
        
        # 确保输入是列表
        is_single_text = isinstance(texts, str)
        if is_single_text:
            texts = [texts]
            if memory_weights is not None and not isinstance(memory_weights, list):
                memory_weights = [memory_weights]
        
        # 处理权重
        if memory_weights is None:
            memory_weights = [1.0] * len(texts)
        elif isinstance(memory_weights, (int, float)):
            # 单个权重值，转换为列表
            memory_weights = [float(memory_weights)] * len(texts)
        elif len(memory_weights) != len(texts):
            logger.warning(f"权重数量({len(memory_weights)})与文本数量({len(texts)})不匹配，使用默认权重")
            memory_weights = [1.0] * len(texts)
        
        # 尝试使用统一缓存管理器
        unified_cache = None
        try:
            from ...shared.caching.cache_manager import UnifiedCacheManager
            unified_cache = UnifiedCacheManager.get_instance()
        except Exception as e:
            logger.debug(f"统一缓存管理器不可用: {e}")
        
        # 检查缓存
        if self.use_cache and (unified_cache or self.cache):
            # 尝试从缓存获取所有向量
            cached_vectors = []
            texts_to_encode = []
            text_indices = []
            weights_to_encode = []
            
            for i, (text, weight) in enumerate(zip(texts, memory_weights)):
                vector = None
                
                # 优先使用统一缓存管理器
                if unified_cache:
                    try:
                        vector = unified_cache.get(text)
                    except Exception as e:
                        logger.debug(f"统一缓存获取失败: {e}")
                
                # 降级到直接缓存
                if vector is None and self.cache:
                    try:
                        vector = self.cache.get(text, memory_weight=weight)
                    except Exception as e:
                        logger.debug(f"直接缓存获取失败: {e}")
                
                if vector is not None:
                    cached_vectors.append((i, vector))
                else:
                    texts_to_encode.append(text)
                    text_indices.append(i)
                    weights_to_encode.append(weight)
            
            # 如果所有向量都在缓存中
            if len(texts_to_encode) == 0:
                logger.debug(f"所有 {len(texts)} 个文本都从缓存中获取")
                # 构建结果数组
                results = np.zeros((len(texts), self.vector_dim), dtype=np.float32)
                for i, vector in cached_vectors:
                    results[i] = vector
                
                return results[0] if is_single_text else results
            
            # 编码未缓存的文本
            if len(texts_to_encode) > 0:
                logger.debug(f"从缓存获取 {len(cached_vectors)} 个向量，需要编码 {len(texts_to_encode)} 个文本")
                new_vectors = self._encode_texts(texts_to_encode, batch_size, show_progress)
                
                # 将新向量添加到缓存
                for text, vector, weight in zip(texts_to_encode, new_vectors, weights_to_encode):
                    # 优先使用统一缓存管理器
                    if unified_cache:
                        try:
                            unified_cache.put(text, vector, {"source": "vectorizer", "weight": weight})
                        except Exception as e:
                            logger.debug(f"统一缓存存储失败: {e}")
                    
                    # 降级到直接缓存
                    if self.cache:
                        try:
                            self.cache.put(text, vector, memory_weight=weight)
                        except Exception as e:
                            logger.debug(f"直接缓存存储失败: {e}")
                
                # 构建完整结果数组
                results = np.zeros((len(texts), self.vector_dim), dtype=np.float32)
                
                # 填入缓存的向量
                for i, vector in cached_vectors:
                    results[i] = vector
                
                # 填入新编码的向量
                for idx, vector in zip(text_indices, new_vectors):
                    results[idx] = vector
                
                return results[0] if is_single_text else results
        
        # 如果不使用缓存，直接编码
        vectors = self._encode_texts(texts, batch_size, show_progress)
        
        # 如果使用缓存，保存新编码的向量
        if self.use_cache:
            for text, vector, weight in zip(texts, vectors, memory_weights):
                # 优先使用统一缓存管理器
                if unified_cache:
                    try:
                        unified_cache.put(text, vector, {"source": "vectorizer", "weight": weight})
                    except Exception as e:
                        logger.debug(f"统一缓存存储失败: {e}")
                
                # 降级到直接缓存
                if self.cache:
                    try:
                        self.cache.put(text, vector, memory_weight=weight)
                    except Exception as e:
                        logger.debug(f"直接缓存存储失败: {e}")
        
        return vectors[0] if is_single_text else vectors
    
    def _encode_texts(self, texts: List[str], batch_size: int = 32, 
                     show_progress: bool = False) -> np.ndarray:
        """实际的文本编码逻辑"""
        if self.model_type == "sentence-transformers":
            return self._encode_with_sentence_transformers(texts, batch_size, show_progress)
        elif self.model_type == "openai":
            return self._encode_with_openai(texts, batch_size)
        elif self.model_type == "custom":
            return self._encode_with_custom_model(texts, batch_size)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
    
    def _encode_with_sentence_transformers(self, texts: List[str], 
                                          batch_size: int = 32, 
                                          show_progress: bool = False) -> np.ndarray:
        """使用sentence-transformers编码文本"""
        try:
            # 使用模型编码
            start_time = time.time()
            embeddings = self.model.encode(
                texts, 
                batch_size=batch_size, 
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            encode_time = time.time() - start_time
            
            logger.debug(f"使用sentence-transformers编码 {len(texts)} 个文本，耗时: {encode_time:.2f}秒")
            return embeddings
            
        except Exception as e:
            logger.error(f"sentence-transformers编码失败: {e}")
            raise
    
    def _encode_with_openai(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """使用OpenAI API编码文本"""
        try:
            all_embeddings = []
            
            # 批量处理
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                
                start_time = time.time()
                response = self.model.Embedding.create(
                    input=batch,
                    model=self.model_name
                )
                batch_time = time.time() - start_time
                
                # 提取嵌入向量
                batch_embeddings = [item["embedding"] for item in response["data"]]
                all_embeddings.extend(batch_embeddings)
                
                logger.debug(f"OpenAI批处理 {len(batch)} 个文本，耗时: {batch_time:.2f}秒")
                
                # API速率限制，避免触发限制
                if i + batch_size < len(texts):
                    time.sleep(0.5)
            
            # 转换为numpy数组
            embeddings = np.array(all_embeddings, dtype=np.float32)
            return embeddings
            
        except Exception as e:
            logger.error(f"OpenAI编码失败: {e}")
            raise
    
    def _encode_with_custom_model(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """使用自定义模型编码文本"""
        # 这里实现自定义模型的编码逻辑
        logger.warning("自定义模型编码未实现")
        raise NotImplementedError("自定义模型编码未实现")
    
    def get_vector_dimension(self) -> int:
        """
        获取向量维度
        
        返回:
            int: 向量维度
        """
        return self.vector_dim
    
    def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算两个向量的相似度（余弦相似度）
        
        参数:
            vec1: 第一个向量
            vec2: 第二个向量
            
        返回:
            float: 相似度分数 (0-1)
        """
        # 确保向量是一维的
        if vec1.ndim > 1:
            vec1 = vec1.flatten()
        if vec2.ndim > 1:
            vec2 = vec2.flatten()
            
        # 计算余弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    def batch_compute_similarity(self, query_vec: np.ndarray, 
                                vectors: np.ndarray) -> np.ndarray:
        """
        批量计算查询向量与多个向量的相似度
        
        参数:
            query_vec: 查询向量，形状为 (vector_dim,)
            vectors: 向量数组，形状为 (n, vector_dim)
            
        返回:
            np.ndarray: 相似度分数数组，形状为 (n,)
        """
        # 确保查询向量是一维的
        if query_vec.ndim > 1:
            query_vec = query_vec.flatten()
            
        # 计算点积
        dot_products = np.dot(vectors, query_vec)
        
        # 计算范数
        query_norm = np.linalg.norm(query_vec)
        vector_norms = np.linalg.norm(vectors, axis=1)
        
        # 避免除零
        mask = vector_norms != 0
        similarities = np.zeros_like(vector_norms)
        similarities[mask] = dot_products[mask] / (vector_norms[mask] * query_norm)
        
        return similarities
    
    def search_cached_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        在缓存中搜索相关记忆，利用关键词缓存加速
        
        参数:
            query: 搜索查询
            limit: 最大返回条数
            
        返回:
            List[Dict]: 匹配的记忆列表
        """
        # 尝试使用统一缓存管理器
        unified_cache = None
        try:
            from ...shared.caching.cache_manager import UnifiedCacheManager
            unified_cache = UnifiedCacheManager.get_instance()
        except Exception as e:
            logger.debug(f"统一缓存管理器不可用: {e}")
        
        if unified_cache:
            try:
                # 统一缓存管理器目前不支持内容搜索，降级到直接缓存
                if self.use_cache and self.cache:
                    return self.cache.search_by_content(query, limit)
            except Exception as e:
                logger.debug(f"统一缓存搜索失败: {e}")
        elif self.use_cache and self.cache:
            return self.cache.search_by_content(query, limit)
        
        logger.warning("缓存未启用或不可用，无法搜索缓存记忆")
        return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        # 尝试使用统一缓存管理器
        unified_cache = None
        try:
            from ...shared.caching.cache_manager import UnifiedCacheManager
            unified_cache = UnifiedCacheManager.get_instance()
        except Exception as e:
            logger.debug(f"统一缓存管理器不可用: {e}")
        
        if unified_cache:
            try:
                stats = unified_cache.get_stats()
                stats["cache_enabled"] = True
                stats["cache_type"] = "unified"
                return stats
            except Exception as e:
                logger.debug(f"统一缓存统计获取失败: {e}")
        
        if self.use_cache and self.cache:
            stats = self.cache.get_stats()
            stats["cache_enabled"] = True
            stats["cache_type"] = "direct"
            return stats
        
        return {"cache_enabled": False, "cache_type": "none"}
    
    def clear_cache(self) -> None:
        """清空缓存"""
        # 尝试使用统一缓存管理器
        unified_cache = None
        try:
            from ...shared.caching.cache_manager import UnifiedCacheManager
            unified_cache = UnifiedCacheManager.get_instance()
        except Exception as e:
            logger.debug(f"统一缓存管理器不可用: {e}")
        
        if unified_cache:
            try:
                unified_cache.clear_all()
                logger.info("统一缓存已清空")
            except Exception as e:
                logger.debug(f"统一缓存清空失败: {e}")
        
        if self.use_cache and self.cache:
            self.cache.clear_all_cache()
            logger.info("直接缓存已清空")

# 模块测试代码
if __name__ == "__main__":
    print("测试文本向量化模块...")
    
    # 尝试加载sentence-transformers模型
    try:
        print("\n1. 测试sentence-transformers模型")
        vectorizer = TextVectorizer(
            model_type="sentence-transformers",
            model_name="paraphrase-multilingual-MiniLM-L12-v2",
            use_cache=True
        )
        
        # 测试文本
        test_texts = [
            "这是一个测试文本，用于验证向量化功能",
            "This is a test text for verifying vectorization functionality",
            "这是另一个相似的测试文本"
        ]
        
        # 编码文本
        print("编码文本...")
        vectors = vectorizer.encode(test_texts, show_progress=True)
        
        print(f"向量形状: {vectors.shape}")
        print(f"向量维度: {vectorizer.get_vector_dimension()}")
        
        # 计算相似度
        print("\n计算相似度:")
        for i in range(len(test_texts)):
            for j in range(i+1, len(test_texts)):
                sim = vectorizer.compute_similarity(vectors[i], vectors[j])
                print(f"文本 {i+1} 和文本 {j+1} 的相似度: {sim:.4f}")
        
        # 测试批量相似度计算
        print("\n批量计算相似度:")
        query_vec = vectors[0]
        similarities = vectorizer.batch_compute_similarity(query_vec, vectors)
        for i, sim in enumerate(similarities):
            print(f"查询与文本 {i+1} 的相似度: {sim:.4f}")
        
        # 测试缓存
        print("\n测试缓存:")
        start_time = time.time()
        cached_vectors = vectorizer.encode(test_texts)
        cache_time = time.time() - start_time
        print(f"从缓存获取向量耗时: {cache_time:.6f}秒")
        
        # 验证向量一致性
        is_equal = np.array_equal(vectors, cached_vectors)
        print(f"向量一致性: {is_equal}")
        
    except ImportError:
        print("未安装sentence-transformers，跳过测试")
    except Exception as e:
        print(f"测试sentence-transformers失败: {e}")
    
    # 如果有OpenAI API密钥，测试OpenAI模型
    if "OPENAI_API_KEY" in os.environ:
        try:
            print("\n2. 测试OpenAI模型")
            openai_vectorizer = TextVectorizer(
                model_type="openai",
                model_name="text-embedding-ada-002",
                use_cache=True
            )
            
            # 测试单个文本
            test_text = "这是一个简短的测试文本"
            
            print("编码文本...")
            vector = openai_vectorizer.encode(test_text)
            
            print(f"向量形状: {vector.shape}")
            print(f"向量维度: {openai_vectorizer.get_vector_dimension()}")
            
        except ImportError:
            print("未安装openai库，跳过测试")
        except Exception as e:
            print(f"测试OpenAI模型失败: {e}")
    else:
        print("\n未设置OPENAI_API_KEY环境变量，跳过OpenAI模型测试")
    
    print("\n测试完成")
