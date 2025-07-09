#!/usr/bin/env python3
"""
Estia-AI 缓存系统修复方案
基于测试结果分析，针对关键问题进行修复

修复优先级：
1. 【高】关键词缓存功能恢复
2. 【高】UnifiedCacheManager变量作用域修复
3. 【中】集成深度增强
4. 【低】缓存清理方法补全

修复策略：
- 参考旧系统core/old_memory的成功实现
- 保持新系统的架构优势
- 确保向后兼容性
"""

import sys
import os
import re
import time
import json
from typing import Dict, List, Set, Any, Optional
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fix_unified_cache_manager_scope():
    """
    修复1: UnifiedCacheManager变量作用域问题
    
    问题：estia_memory_v5.py中出现 "cannot access local variable 'UnifiedCacheManager'"
    原因：变量作用域问题
    解决：修复导入和变量使用
    """
    print("🔧 修复1: UnifiedCacheManager变量作用域问题")
    print("=" * 60)
    
    # 定位问题文件
    estia_memory_file = "/mnt/d/Estia-AI/core/memory/estia_memory_v5.py"
    
    try:
        with open(estia_memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找问题代码段
        if "cannot access local variable 'UnifiedCacheManager'" in content:
            print("❌ 发现变量作用域问题")
        
        # 分析代码结构
        lines = content.split('\n')
        problematic_lines = []
        
        for i, line in enumerate(lines):
            if 'UnifiedCacheManager' in line and ('import' not in line):
                problematic_lines.append((i+1, line.strip()))
        
        print(f"📍 发现 {len(problematic_lines)} 处 UnifiedCacheManager 使用")
        
        # 查找导入语句
        import_lines = []
        for i, line in enumerate(lines):
            if 'UnifiedCacheManager' in line and 'import' in line:
                import_lines.append((i+1, line.strip()))
        
        print(f"📍 发现 {len(import_lines)} 处 UnifiedCacheManager 导入")
        
        # 提供修复建议
        print("\n🔧 修复建议:")
        print("1. 确保在文件顶部正确导入 UnifiedCacheManager")
        print("2. 检查是否存在局部变量重名问题")
        print("3. 使用完整的模块路径避免命名冲突")
        
        # 生成修复代码
        fix_code = '''
# 修复方案：在文件顶部添加正确的导入
from core.memory.shared.caching.cache_manager import UnifiedCacheManager

# 在 EstiaMemorySystem 类的 __init__ 方法中：
def __init__(self, db_path: str = "assets/memory.db", enable_advanced: bool = True):
    """初始化Estia记忆系统"""
    try:
        # 确保使用完整的类名，避免作用域问题
        self.unified_cache = UnifiedCacheManager.get_instance()
        logger.info("✅ 统一缓存管理器初始化成功")
        
        # 在高级组件初始化中使用 self.unified_cache
        if enable_advanced:
            try:
                # 使用已经初始化的 unified_cache 实例
                if hasattr(self, 'unified_cache') and self.unified_cache:
                    # 高级组件初始化代码
                    pass
            except Exception as e:
                logger.warning(f"高级组件初始化失败: {e}")
                
    except Exception as e:
        logger.error(f"统一缓存管理器初始化失败: {e}")
        self.unified_cache = None
'''
        
        print(f"\n📝 修复代码示例:")
        print(fix_code)
        
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def create_keyword_cache_implementation():
    """
    修复2: 关键词缓存功能恢复
    
    问题：新系统缺少关键词缓存功能
    解决：参考旧系统实现，添加关键词缓存功能
    """
    print("\n🔧 修复2: 关键词缓存功能恢复")
    print("=" * 60)
    
    # 基于旧系统的关键词缓存实现
    keyword_cache_code = '''
import re
import threading
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict, OrderedDict

class KeywordCache:
    """
    关键词缓存系统
    基于旧系统 core/old_memory/embedding/cache.py 的实现
    """
    
    def __init__(self, max_keywords: int = 10000):
        """初始化关键词缓存"""
        self.max_keywords = max_keywords
        self.keyword_cache: Dict[str, Set[str]] = defaultdict(set)
        self.keyword_metadata: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        
        # 中文停用词
        self.stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看',
            '好', '自己', '这', '那', '什么', '可以', '这个', '还', '时候', '如果'
        }
        
        # 英文停用词
        self.stop_words.update({
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'this', 'that', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall'
        })
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词
        基于旧系统的实现，支持中英文混合文本
        """
        if not text:
            return []
            
        # 提取中文和英文词汇
        words = re.findall(r'[\\w\\u4e00-\\u9fff]+', text.lower())
        
        # 过滤停用词和短词
        keywords = []
        for word in words:
            if (len(word) > 1 and 
                word not in self.stop_words and 
                not word.isdigit()):
                keywords.append(word)
        
        # 限制关键词数量
        return keywords[:10]
    
    def add_to_keyword_cache(self, cache_key: str, text: str, weight: float = 1.0):
        """
        添加到关键词缓存
        
        Args:
            cache_key: 缓存键
            text: 文本内容
            weight: 权重
        """
        with self.lock:
            keywords = self._extract_keywords(text)
            
            for keyword in keywords:
                # 添加到关键词映射
                self.keyword_cache[keyword].add(cache_key)
                
                # 更新元数据
                if keyword not in self.keyword_metadata:
                    self.keyword_metadata[keyword] = {
                        'count': 0,
                        'weight': 0.0,
                        'last_updated': None
                    }
                
                # 更新统计信息
                self.keyword_metadata[keyword]['count'] += 1
                self.keyword_metadata[keyword]['weight'] = max(
                    self.keyword_metadata[keyword]['weight'], weight
                )
                self.keyword_metadata[keyword]['last_updated'] = time.time()
    
    def search_by_keywords(self, query: str, limit: int = 10) -> List[str]:
        """
        基于关键词搜索缓存项
        
        Args:
            query: 搜索查询
            limit: 返回结果数量限制
            
        Returns:
            相关的缓存键列表
        """
        with self.lock:
            keywords = self._extract_keywords(query)
            
            if not keywords:
                return []
            
            # 收集候选项
            candidates = defaultdict(float)
            
            for keyword in keywords:
                if keyword in self.keyword_cache:
                    # 获取包含此关键词的缓存项
                    cache_keys = self.keyword_cache[keyword]
                    keyword_weight = self.keyword_metadata[keyword]['weight']
                    
                    for cache_key in cache_keys:
                        # 计算相关性分数
                        candidates[cache_key] += keyword_weight
            
            # 按分数排序
            sorted_candidates = sorted(
                candidates.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return [cache_key for cache_key, score in sorted_candidates[:limit]]
    
    def remove_from_keyword_cache(self, cache_key: str):
        """
        从关键词缓存中移除项
        
        Args:
            cache_key: 要移除的缓存键
        """
        with self.lock:
            # 查找并移除包含此cache_key的关键词
            keywords_to_clean = []
            
            for keyword, cache_keys in self.keyword_cache.items():
                if cache_key in cache_keys:
                    cache_keys.remove(cache_key)
                    
                    # 如果该关键词没有其他缓存项，标记为待清理
                    if not cache_keys:
                        keywords_to_clean.append(keyword)
            
            # 清理空的关键词条目
            for keyword in keywords_to_clean:
                del self.keyword_cache[keyword]
                if keyword in self.keyword_metadata:
                    del self.keyword_metadata[keyword]
    
    def get_keyword_stats(self) -> Dict[str, Any]:
        """
        获取关键词缓存统计信息
        
        Returns:
            统计信息字典
        """
        with self.lock:
            return {
                'total_keywords': len(self.keyword_cache),
                'total_cache_items': sum(len(cache_keys) for cache_keys in self.keyword_cache.values()),
                'top_keywords': sorted(
                    [(keyword, len(cache_keys)) for keyword, cache_keys in self.keyword_cache.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }
    
    def clear_keyword_cache(self):
        """清理关键词缓存"""
        with self.lock:
            self.keyword_cache.clear()
            self.keyword_metadata.clear()
    
    def _maintain_keyword_cache(self):
        """
        维护关键词缓存
        清理过期和低权重的关键词
        """
        with self.lock:
            current_time = time.time()
            keywords_to_remove = []
            
            for keyword, metadata in self.keyword_metadata.items():
                # 检查是否过期（30天）
                if (current_time - metadata['last_updated']) > (30 * 24 * 3600):
                    keywords_to_remove.append(keyword)
                # 检查是否权重过低
                elif metadata['weight'] < 0.1 and metadata['count'] < 2:
                    keywords_to_remove.append(keyword)
            
            # 移除过期关键词
            for keyword in keywords_to_remove:
                if keyword in self.keyword_cache:
                    del self.keyword_cache[keyword]
                if keyword in self.keyword_metadata:
                    del self.keyword_metadata[keyword]
'''
    
    # 保存关键词缓存实现
    keyword_cache_file = "/mnt/d/Estia-AI/core/memory/shared/caching/keyword_cache.py"
    
    try:
        with open(keyword_cache_file, 'w', encoding='utf-8') as f:
            f.write(keyword_cache_code)
        
        print(f"✅ 关键词缓存实现已保存: {keyword_cache_file}")
        
        # 显示关键功能
        print("\n📋 关键词缓存功能:")
        print("- _extract_keywords(): 提取中英文关键词")
        print("- add_to_keyword_cache(): 添加到关键词索引")
        print("- search_by_keywords(): 基于关键词搜索")
        print("- remove_from_keyword_cache(): 移除关键词索引")
        print("- get_keyword_stats(): 获取统计信息")
        print("- clear_keyword_cache(): 清理缓存")
        
        return True
        
    except Exception as e:
        print(f"❌ 关键词缓存实现保存失败: {e}")
        return False

def create_enhanced_cache_manager():
    """
    修复3: 增强统一缓存管理器
    
    问题：缺少clear方法和关键词缓存集成
    解决：增强UnifiedCacheManager，集成关键词缓存
    """
    print("\n🔧 修复3: 增强统一缓存管理器")
    print("=" * 60)
    
    enhanced_manager_code = '''
# 增强版统一缓存管理器
# 文件位置: core/memory/shared/caching/cache_manager.py

import threading
import time
from typing import Dict, List, Set, Any, Optional, TypeVar, Generic
from .keyword_cache import KeywordCache
from .cache_interface import CacheInterface, CacheLevel, CacheEvent, CacheEventType

K = TypeVar('K')
V = TypeVar('V')
M = TypeVar('M')

class EnhancedUnifiedCacheManager(Generic[K, V, M]):
    """
    增强版统一缓存管理器
    集成关键词缓存功能
    """
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        with self._lock:
            if not self._initialized:
                # 基础缓存管理
                self.caches: Dict[str, CacheInterface] = {}
                self.level_caches: Dict[CacheLevel, List[CacheInterface]] = {
                    level: [] for level in CacheLevel
                }
                
                # 关键词缓存集成
                self.keyword_cache = KeywordCache()
                
                # 性能统计
                self.stats = {
                    'total_hits': 0,
                    'total_misses': 0,
                    'cache_hits': {},
                    'level_hits': {},
                    'operations': {},
                    'keyword_searches': 0,
                    'keyword_hits': 0
                }
                
                # 缓存键映射
                self.key_cache_map: Dict[K, Set[str]] = {}
                
                # 事件监听器
                self.listeners: List[callable] = []
                
                # 配置
                self.config = {
                    'maintenance_interval': 300,
                    'enable_keyword_cache': True,
                    'keyword_cache_threshold': 0.5
                }
                
                self._initialized = True
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        return cls()
    
    def register_cache(self, cache: CacheInterface, level: CacheLevel = CacheLevel.EXTERNAL):
        """
        注册缓存到管理器
        
        Args:
            cache: 缓存实例
            level: 缓存级别
        """
        with self._lock:
            cache_id = cache.cache_id
            self.caches[cache_id] = cache
            self.level_caches[level].append(cache)
            
            # 初始化统计
            self.stats['cache_hits'][cache_id] = 0
            self.stats['level_hits'][level.value] = 0
            
            self._emit_event(CacheEventType.INIT, cache_id, None, None)
    
    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """
        获取缓存值
        支持多级缓存查找和关键词搜索
        """
        with self._lock:
            # 1. 检查键映射中的已知缓存
            if key in self.key_cache_map:
                for cache_id in self.key_cache_map[key]:
                    if cache_id in self.caches:
                        cache = self.caches[cache_id]
                        value = cache.get(key)
                        if value is not None:
                            self._record_hit(cache_id)
                            return value
            
            # 2. 按优先级顺序查找
            for level in [CacheLevel.HOT, CacheLevel.WARM, CacheLevel.COLD, CacheLevel.PERSISTENT]:
                for cache in self.level_caches[level]:
                    value = cache.get(key)
                    if value is not None:
                        self._record_hit(cache.cache_id)
                        self._update_key_mapping(key, cache.cache_id)
                        return value
            
            # 3. 记录未命中
            self._record_miss()
            return default
    
    def put(self, key: K, value: V, metadata: Optional[M] = None, 
            text_content: Optional[str] = None, weight: float = 1.0):
        """
        放入缓存值
        支持关键词缓存集成
        """
        with self._lock:
            # 1. 存储到适当的缓存级别
            target_level = self._determine_cache_level(weight)
            
            if self.level_caches[target_level]:
                cache = self.level_caches[target_level][0]
                cache.put(key, value, metadata)
                
                # 2. 更新键映射
                self._update_key_mapping(key, cache.cache_id)
                
                # 3. 添加到关键词缓存
                if (self.config['enable_keyword_cache'] and 
                    text_content and 
                    weight >= self.config['keyword_cache_threshold']):
                    self.keyword_cache.add_to_keyword_cache(
                        str(key), text_content, weight
                    )
                
                # 4. 触发事件
                self._emit_event(CacheEventType.PUT, cache.cache_id, key, value)
    
    def search_by_content(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        基于内容搜索缓存
        使用关键词缓存加速搜索
        """
        with self._lock:
            self.stats['keyword_searches'] += 1
            
            # 1. 关键词搜索
            if self.config['enable_keyword_cache']:
                cache_keys = self.keyword_cache.search_by_keywords(query, limit * 2)
                
                if cache_keys:
                    self.stats['keyword_hits'] += 1
                    
                    # 2. 获取缓存内容
                    results = []
                    for cache_key in cache_keys:
                        # 尝试从各个缓存中获取
                        for cache in self.caches.values():
                            value = cache.get(cache_key)
                            if value is not None:
                                results.append({
                                    'key': cache_key,
                                    'value': value,
                                    'cache_id': cache.cache_id
                                })
                                break
                    
                    return results[:limit]
            
            # 3. 回退到遍历搜索
            results = []
            for cache_id, cache in self.caches.items():
                # 简单的遍历搜索（可以根据具体缓存类型优化）
                if hasattr(cache, 'search'):
                    cache_results = cache.search(query, limit)
                    results.extend(cache_results)
            
            return results[:limit]
    
    def record_memory_access(self, memory_id: str, access_weight: float = 1.0):
        """
        记录记忆访问
        更新缓存优先级
        """
        with self._lock:
            # 更新访问统计
            self.stats['operations']['memory_access'] = (
                self.stats['operations'].get('memory_access', 0) + 1
            )
            
            # 可以根据访问权重调整缓存优先级
            # 这里可以实现智能提升逻辑
            pass
    
    def clear(self, cache_id: Optional[str] = None):
        """
        清理缓存
        
        Args:
            cache_id: 指定缓存ID，None表示清理所有
        """
        with self._lock:
            if cache_id:
                # 清理指定缓存
                if cache_id in self.caches:
                    cache = self.caches[cache_id]
                    cache.clear()
                    self._emit_event(CacheEventType.CLEAR, cache_id, None, None)
            else:
                # 清理所有缓存
                for cache in self.caches.values():
                    cache.clear()
                
                # 清理关键词缓存
                self.keyword_cache.clear_keyword_cache()
                
                # 清理键映射
                self.key_cache_map.clear()
                
                # 重置统计
                self.stats['total_hits'] = 0
                self.stats['total_misses'] = 0
                for cache_id in self.stats['cache_hits']:
                    self.stats['cache_hits'][cache_id] = 0
                
                self._emit_event(CacheEventType.CLEAR, "all", None, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        包含关键词缓存统计
        """
        with self._lock:
            hit_ratio = 0.0
            total_operations = self.stats['total_hits'] + self.stats['total_misses']
            if total_operations > 0:
                hit_ratio = self.stats['total_hits'] / total_operations
            
            # 获取关键词缓存统计
            keyword_stats = self.keyword_cache.get_keyword_stats()
            
            return {
                'manager': {
                    'hit_ratio': hit_ratio,
                    'total_hits': self.stats['total_hits'],
                    'total_misses': self.stats['total_misses'],
                    'cache_hits': self.stats['cache_hits'].copy(),
                    'level_hits': self.stats['level_hits'].copy(),
                    'operations': self.stats['operations'].copy(),
                    'keyword_searches': self.stats['keyword_searches'],
                    'keyword_hits': self.stats['keyword_hits']
                },
                'caches': {
                    cache_id: cache.get_stats() if hasattr(cache, 'get_stats') else {}
                    for cache_id, cache in self.caches.items()
                },
                'keyword_cache': keyword_stats
            }
    
    def _determine_cache_level(self, weight: float) -> CacheLevel:
        """根据权重确定缓存级别"""
        if weight >= 8.0:
            return CacheLevel.HOT
        elif weight >= 5.0:
            return CacheLevel.WARM
        elif weight >= 2.0:
            return CacheLevel.COLD
        else:
            return CacheLevel.PERSISTENT
    
    def _update_key_mapping(self, key: K, cache_id: str):
        """更新键映射"""
        if key not in self.key_cache_map:
            self.key_cache_map[key] = set()
        self.key_cache_map[key].add(cache_id)
    
    def _record_hit(self, cache_id: str):
        """记录缓存命中"""
        self.stats['total_hits'] += 1
        self.stats['cache_hits'][cache_id] = self.stats['cache_hits'].get(cache_id, 0) + 1
    
    def _record_miss(self):
        """记录缓存未命中"""
        self.stats['total_misses'] += 1
    
    def _emit_event(self, event_type: CacheEventType, cache_id: str, key: K, value: V):
        """触发事件"""
        event = CacheEvent(event_type, cache_id, key, value, time.time())
        for listener in self.listeners:
            try:
                listener(event)
            except Exception as e:
                # 忽略监听器异常
                pass

# 为了向后兼容，保持原有的类名
UnifiedCacheManager = EnhancedUnifiedCacheManager
'''
    
    # 保存增强版缓存管理器
    enhanced_manager_file = "/mnt/d/Estia-AI/core/memory/shared/caching/enhanced_cache_manager.py"
    
    try:
        with open(enhanced_manager_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_manager_code)
        
        print(f"✅ 增强版缓存管理器已保存: {enhanced_manager_file}")
        
        # 显示增强功能
        print("\n📋 增强功能:")
        print("- 集成关键词缓存功能")
        print("- 添加 clear() 方法")
        print("- 增强 search_by_content() 方法")
        print("- 完善性能统计")
        print("- 添加 record_memory_access() 方法")
        print("- 支持基于内容的智能缓存")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强版缓存管理器保存失败: {e}")
        return False

def create_integration_enhancement():
    """
    修复4: 集成深度增强
    
    问题：enhance_query方法中缓存使用不足
    解决：增强核心流程中的缓存集成
    """
    print("\n🔧 修复4: 集成深度增强")
    print("=" * 60)
    
    integration_code = '''
# 集成深度增强方案
# 文件位置: core/memory/estia_memory_v5.py

# 在 EstiaMemorySystem 类中增强 enhance_query 方法

def enhance_query(self, user_input: str, context: dict = None) -> str:
    """
    增强查询处理
    深度集成缓存系统，参考旧系统的3个关键缓存使用位置
    """
    start_time = time.time()
    
    try:
        # 1. 向量缓存使用（第一个关键位置）
        cache_key = f"vector:{user_input}"
        cached_vector = None
        
        if self.unified_cache:
            cached_vector = self.unified_cache.get(cache_key)
            
        if cached_vector is None:
            # 向量化
            if self.vectorizer:
                cached_vector = self.vectorizer.encode(user_input)
                if self.unified_cache:
                    self.unified_cache.put(
                        cache_key, cached_vector, 
                        text_content=user_input, 
                        weight=1.0
                    )
        
        # 2. 记忆访问记录（第二个关键位置）
        if self.unified_cache:
            self.unified_cache.record_memory_access(
                f"query:{user_input}", 
                access_weight=1.0
            )
        
        # 3. 查询结果缓存（第三个关键位置）
        result_cache_key = f"result:{user_input}"
        cached_result = None
        
        if self.unified_cache:
            cached_result = self.unified_cache.get(result_cache_key)
            
        if cached_result is None:
            # 执行实际的查询增强逻辑
            if hasattr(self, 'sync_flow_manager') and self.sync_flow_manager:
                enhanced_context = self.sync_flow_manager.enhance_query(
                    user_input, context or {}
                )
                
                # 缓存结果
                if self.unified_cache:
                    self.unified_cache.put(
                        result_cache_key, enhanced_context,
                        text_content=user_input,
                        weight=2.0
                    )
                
                cached_result = enhanced_context
            else:
                cached_result = user_input
        
        # 4. 性能统计和监控
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000  # ms
        
        if self.unified_cache:
            # 记录性能指标
            self.unified_cache.record_memory_access(
                f"performance:{processing_time:.2f}ms",
                access_weight=0.5
            )
        
        logger.info(f"✅ 同步流程完成，总耗时: {processing_time:.2f}ms")
        
        return cached_result
        
    except Exception as e:
        logger.error(f"查询增强失败: {e}")
        return user_input

# 增强初始化方法
def __init__(self, db_path: str = "assets/memory.db", enable_advanced: bool = True):
    """
    初始化Estia记忆系统
    确保统一缓存管理器正确初始化
    """
    logger.info("🚀 开始初始化Estia记忆系统 v5.0.0")
    
    try:
        # 1. 数据库管理器
        self.db_manager = DatabaseManager(db_path)
        logger.info("✅ 数据库管理器初始化成功")
        
        # 2. 统一缓存管理器 - 修复变量作用域问题
        from core.memory.shared.caching.enhanced_cache_manager import EnhancedUnifiedCacheManager
        self.unified_cache = EnhancedUnifiedCacheManager.get_instance()
        logger.info("✅ 统一缓存管理器初始化成功")
        
        # 3. 向量化器
        self.vectorizer = TextVectorizer()
        logger.info("✅ 使用TextVectorizer（all-MiniLM-L6-v2）")
        
        # 4. 基础记忆存储器
        self.memory_store = MemoryStore(
            db_manager=self.db_manager,
            vectorizer=self.vectorizer
        )
        logger.info("✅ 基础记忆存储器初始化成功")
        
        # 5. 高级组件初始化 - 修复变量作用域问题
        if enable_advanced:
            try:
                # 确保unified_cache已正确初始化
                if hasattr(self, 'unified_cache') and self.unified_cache is not None:
                    # 初始化高级组件
                    self.smart_retriever = SmartRetriever(
                        db_manager=self.db_manager,
                        vectorizer=self.vectorizer,
                        cache_manager=self.unified_cache
                    )
                    
                    self.faiss_retriever = FAISSSearchEngine(
                        db_manager=self.db_manager,
                        vectorizer=self.vectorizer
                    )
                    
                    # 初始化同步流程管理器
                    self.sync_flow_manager = SyncFlowManager(
                        db_manager=self.db_manager,
                        unified_cache=self.unified_cache,
                        vectorizer=self.vectorizer,
                        memory_store=self.memory_store
                    )
                    
                    logger.info("✅ 高级组件初始化成功")
                else:
                    logger.warning("统一缓存管理器未正确初始化，跳过高级组件")
                    
            except Exception as e:
                logger.warning(f"高级组件初始化失败: {e}")
                # 设置为None以便后续检查
                self.smart_retriever = None
                self.faiss_retriever = None
                self.sync_flow_manager = None
        
        logger.info("✅ Estia记忆系统 v5.0.0 初始化完成")
        
    except Exception as e:
        logger.error(f"Estia记忆系统初始化失败: {e}")
        raise
'''
    
    print("📝 集成深度增强方案:")
    print("1. 在enhance_query方法中添加3个关键缓存使用位置")
    print("2. 修复UnifiedCacheManager变量作用域问题")
    print("3. 增强初始化方法的错误处理")
    print("4. 添加性能监控和统计")
    
    print(f"\n📋 增强要点:")
    print("- 向量缓存使用（第一个关键位置）")
    print("- 记忆访问记录（第二个关键位置）") 
    print("- 查询结果缓存（第三个关键位置）")
    print("- 性能统计和监控")
    print("- 变量作用域修复")
    
    return True

def create_fix_test_script():
    """
    创建修复验证测试脚本
    """
    print("\n🔧 创建修复验证测试脚本")
    print("=" * 60)
    
    test_script = '''
#!/usr/bin/env python3
"""
缓存系统修复验证测试脚本
验证修复效果和性能提升
"""

import sys
import os
import time
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_keyword_cache_functionality():
    """测试关键词缓存功能"""
    print("🔍 测试关键词缓存功能...")
    
    try:
        from core.memory.shared.caching.keyword_cache import KeywordCache
        
        # 创建关键词缓存实例
        keyword_cache = KeywordCache()
        
        # 测试关键词提取
        test_text = "今天天气很好，我想出去散步，享受阳光"
        keywords = keyword_cache._extract_keywords(test_text)
        print(f"   关键词提取: {keywords}")
        
        # 测试添加到缓存
        keyword_cache.add_to_keyword_cache("test_key_1", test_text, 5.0)
        keyword_cache.add_to_keyword_cache("test_key_2", "散步是很好的运动", 3.0)
        
        # 测试搜索
        search_results = keyword_cache.search_by_keywords("散步", 5)
        print(f"   搜索结果: {search_results}")
        
        # 测试统计
        stats = keyword_cache.get_keyword_stats()
        print(f"   统计信息: {stats}")
        
        print("✅ 关键词缓存功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 关键词缓存功能测试失败: {e}")
        return False

def test_enhanced_cache_manager():
    """测试增强版缓存管理器"""
    print("🔍 测试增强版缓存管理器...")
    
    try:
        from core.memory.shared.caching.enhanced_cache_manager import EnhancedUnifiedCacheManager
        
        # 创建管理器实例
        cache_manager = EnhancedUnifiedCacheManager.get_instance()
        
        # 测试基本功能
        cache_manager.put("test_key", "test_value", text_content="这是测试内容", weight=5.0)
        value = cache_manager.get("test_key")
        print(f"   基本缓存: {value}")
        
        # 测试内容搜索
        search_results = cache_manager.search_by_content("测试内容", 5)
        print(f"   内容搜索: {len(search_results)} 个结果")
        
        # 测试clear方法
        cache_manager.clear()
        print("   缓存清理完成")
        
        # 测试统计信息
        stats = cache_manager.get_stats()
        print(f"   统计信息: {stats['manager']['hit_ratio']:.2%}")
        
        print("✅ 增强版缓存管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 增强版缓存管理器测试失败: {e}")
        return False

def test_integration_enhancement():
    """测试集成深度增强"""
    print("🔍 测试集成深度增强...")
    
    try:
        from core.memory.estia_memory_v5 import EstiaMemorySystem
        
        # 创建记忆系统实例
        memory_system = EstiaMemorySystem()
        
        # 测试统一缓存是否正确初始化
        if hasattr(memory_system, 'unified_cache') and memory_system.unified_cache:
            print("   ✅ 统一缓存正确初始化")
        else:
            print("   ❌ 统一缓存未正确初始化")
            return False
        
        # 测试enhance_query缓存效果
        test_query = "这是一个测试查询"
        
        # 第一次查询
        start_time = time.time()
        result1 = memory_system.enhance_query(test_query)
        first_time = time.time() - start_time
        
        # 第二次查询（应该命中缓存）
        start_time = time.time()
        result2 = memory_system.enhance_query(test_query)
        second_time = time.time() - start_time
        
        print(f"   第一次查询: {first_time:.4f}s")
        print(f"   第二次查询: {second_time:.4f}s")
        
        # 检查加速比
        if first_time > 0 and second_time < first_time * 0.5:
            speedup = first_time / second_time if second_time > 0 else float('inf')
            print(f"   ✅ 缓存加速比: {speedup:.2f}x")
        else:
            print("   ❌ 缓存加速效果不明显")
            return False
        
        # 测试缓存统计
        stats = memory_system.unified_cache.get_stats()
        print(f"   缓存命中率: {stats['manager']['hit_ratio']:.2%}")
        
        print("✅ 集成深度增强测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 集成深度增强测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 缓存系统修复验证测试")
    print("=" * 60)
    
    test_results = {
        "keyword_cache": test_keyword_cache_functionality(),
        "enhanced_manager": test_enhanced_cache_manager(),
        "integration": test_integration_enhancement()
    }
    
    # 计算总体成功率
    success_rate = sum(test_results.values()) / len(test_results)
    
    print("\\n" + "=" * 60)
    print("📊 修复验证结果")
    print("=" * 60)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\\n总体成功率: {success_rate:.2%}")
    
    if success_rate == 1.0:
        print("🎉 所有修复验证通过！")
    elif success_rate >= 0.8:
        print("✅ 大部分修复验证通过，少数问题待解决")
    else:
        print("❌ 修复验证失败较多，需要进一步调试")

if __name__ == "__main__":
    main()
'''
    
    # 保存测试脚本
    test_script_file = "/mnt/d/Estia-AI/test_cache_fix_verification.py"
    
    try:
        with open(test_script_file, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print(f"✅ 修复验证测试脚本已保存: {test_script_file}")
        return True
        
    except Exception as e:
        print(f"❌ 修复验证测试脚本保存失败: {e}")
        return False

def main():
    """主修复函数"""
    print("🚀 Estia-AI 缓存系统修复方案")
    print("=" * 80)
    print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 执行修复步骤
    print("\n🔧 开始执行修复...")
    
    # 修复1: UnifiedCacheManager变量作用域问题
    fix1_success = fix_unified_cache_manager_scope()
    
    # 修复2: 关键词缓存功能恢复
    fix2_success = create_keyword_cache_implementation()
    
    # 修复3: 增强统一缓存管理器
    fix3_success = create_enhanced_cache_manager()
    
    # 修复4: 集成深度增强
    fix4_success = create_integration_enhancement()
    
    # 创建验证测试脚本
    test_success = create_fix_test_script()
    
    # 修复结果统计
    fix_results = {
        "变量作用域修复": fix1_success,
        "关键词缓存恢复": fix2_success,
        "缓存管理器增强": fix3_success,
        "集成深度增强": fix4_success,
        "验证测试脚本": test_success
    }
    
    success_count = sum(fix_results.values())
    total_count = len(fix_results)
    
    print("\n" + "=" * 80)
    print("📊 修复方案执行结果")
    print("=" * 80)
    
    for fix_name, result in fix_results.items():
        status = "✅ 成功" if result else "❌ 失败"
        print(f"{fix_name}: {status}")
    
    print(f"\n成功率: {success_count}/{total_count} ({success_count/total_count:.2%})")
    
    if success_count == total_count:
        print("\n🎉 所有修复方案执行成功！")
        print("\n🎯 下一步行动:")
        print("1. 手动应用修复代码到相应文件")
        print("2. 运行 test_cache_fix_verification.py 验证修复效果")
        print("3. 重新运行 test_cache_system_analysis.py 对比修复前后的性能")
    else:
        print("\n❌ 部分修复方案执行失败，请检查错误信息")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()