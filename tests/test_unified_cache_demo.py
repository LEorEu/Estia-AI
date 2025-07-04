"""统一缓存系统演示测试
与 pytest 单元测试互补，直观展示多级缓存统一后的运行效果。
运行方式：
    python tests/test_unified_cache_demo.py
"""

import numpy as np
import time
from core.memory.embedding.cache import EnhancedMemoryCache
from core.memory.memory_cache.cache_manager import CacheManager
from core.memory.caching.cache_manager import UnifiedCacheManager
from core.memory.caching.cache_adapters import (
    EnhancedMemoryCacheAdapter,
    DbCacheAdapter,
)


def banner(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    banner("🧪 统一缓存系统演示测试")

    # 1️⃣ 初始化管理器 & 适配器
    print("\n[1] 初始化缓存管理器与适配器…")
    UnifiedCacheManager._instance = None  # 测试隔离
    ucm = UnifiedCacheManager.get_instance()

    emb_cache = EnhancedMemoryCache(persist=False)
    EnhancedMemoryCacheAdapter(emb_cache)
    print("   • 已注册增强嵌入缓存 (HOT)")

    db_cache = CacheManager()
    DbCacheAdapter(db_cache)
    print("   • 已注册数据库缓存 (WARM)")

    print(f"   • 当前已注册缓存: {list(ucm.caches.keys())}")

    # 2️⃣ 写入并读取
    print("\n[2] 写入 / 读取缓存项…")
    text = "统一缓存系统真方便"
    vector = np.random.rand(32)
    ucm.put(text, vector)
    print("   • 已写入一条记录 -> HOT")

    retrieved = ucm.get(text)
    status = "命中" if retrieved is not None else "未命中"
    print(f"   • 读取同一键: {status}")

    # 3️⃣ 查看统计
    mgr_stats = ucm.get_stats()["manager"]
    hit_ratio = mgr_stats.get("hit_ratio", 0) * 100
    print("\n[3] 统计信息…")
    print(f"   • total_hits    : {mgr_stats.get('total_hits', 0)}")
    print(f"   • total_misses  : {mgr_stats.get('total_misses', 0)}")
    print(f"   • hit_ratio     : {hit_ratio:.1f}%")

    # 4️⃣ 删除 / 清空
    print("\n[4] 删除 / 清空演示…")
    ucm.delete(text)
    print("   • 已删除该键 (同步至各缓存)")
    assert ucm.get(text) is None
    ucm.clear_all()
    print("   • 已清空全部缓存")

    banner("✅ 演示完成，统一缓存系统工作正常！")


if __name__ == "__main__":
    main() 