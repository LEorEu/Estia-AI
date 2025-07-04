import numpy as np
import pytest

# 跳过测试如果缺少关键依赖
pytest.importorskip("numpy")

from core.memory.embedding.cache import EnhancedMemoryCache
from core.memory.memory_cache.cache_manager import CacheManager
from core.memory.caching.cache_manager import UnifiedCacheManager
from core.memory.caching.cache_adapters import (
    EnhancedMemoryCacheAdapter,
    DbCacheAdapter,
)


class DummyDBManager:
    """极简 stub，用于让旧 CacheManager 正常工作而无需真实数据库。"""

    def query(self, sql: str, params=None):
        sql_lower = sql.lower()
        # 返回默认权重
        if "from memories" in sql_lower and "weight" in sql_lower:
            return [(5.0,)]
        # memory_cache 表
        return []

    def execute_query(self, sql: str, params=None):
        # 不做任何持久化
        return True


def reset_ucm_singleton():
    """测试隔离：重置 UnifiedCacheManager 单例。"""
    UnifiedCacheManager._instance = None  # type: ignore


def test_unified_cache_put_get():
    """验证适配器注册 & 统一缓存读写。"""
    reset_ucm_singleton()
    ucm = UnifiedCacheManager.get_instance()

    # 注册嵌入向量缓存
    emb_cache = EnhancedMemoryCache(persist=False)
    EnhancedMemoryCacheAdapter(emb_cache)

    # 注册数据库缓存（使用 DummyDBManager ）
    db_cache = CacheManager(db_manager=DummyDBManager())
    DbCacheAdapter(db_cache)

    assert len(ucm.caches) == 2  # 两个缓存已注册

    # 写入一条记录
    text = "hello unified cache"
    vector = np.random.rand(32)
    ucm.put(text, vector)

    # 读取并验证
    retrieved = ucm.get(text)
    assert retrieved is not None
    assert np.allclose(retrieved, vector)

    # 命中率统计应>0
    mgr_stats = ucm.get_stats()["manager"]
    assert mgr_stats["total_hits"] >= 1
    assert mgr_stats["total_misses"] == 0 