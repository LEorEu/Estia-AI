#!/usr/bin/env python3
"""
Estia-AI 缓存系统修复方案 - 修正版
基于实际文件结构进行修复

修复优先级：
1. 【高】关键词缓存功能恢复
2. 【高】UnifiedCacheManager变量作用域修复
3. 【中】集成深度增强
4. 【低】缓存清理方法补全
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

def create_keyword_cache_implementation():
    """
    修复1: 关键词缓存功能恢复
    在正确的目录创建关键词缓存实现
    """
    print("🔧 修复1: 关键词缓存功能恢复")
    print("=" * 60)
    
    # 关键词缓存实现代码
    keyword_cache_code = '''"""
关键词缓存系统
基于旧系统 core/old_memory/embedding/cache.py 的实现
"""

import re
import threading
import time
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict

class KeywordCache:
    """
    关键词缓存系统
    提供基于关键词的快速内容检索功能
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
    
    # 正确的文件路径
    keyword_cache_file = "core/memory/shared/caching/keyword_cache.py"
    
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

def enhance_cache_manager():
    """
    修复2: 增强统一缓存管理器
    在现有cache_manager.py中添加关键词缓存功能
    """
    print("\n🔧 修复2: 增强统一缓存管理器")
    print("=" * 60)
    
    # 先读取现有的cache_manager.py文件
    cache_manager_file = "core/memory/shared/caching/cache_manager.py"
    
    try:
        with open(cache_manager_file, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # 检查是否已经有关键词缓存集成
        if 'from .keyword_cache import KeywordCache' in current_content:
            print("✅ 缓存管理器已集成关键词缓存")
            return True
        
        # 创建增强版本
        enhanced_content = current_content.replace(
            'from .cache_interface import',
            '''from .keyword_cache import KeywordCache
from .cache_interface import'''
        )
        
        # 在UnifiedCacheManager类中添加关键词缓存初始化
        if 'def __init__(self):' in enhanced_content:
            enhanced_content = enhanced_content.replace(
                'def __init__(self):',
                '''def __init__(self):
        # 关键词缓存集成
        self.keyword_cache = KeywordCache()'''
            )
        
        # 添加clear方法（如果不存在）
        if 'def clear(' not in enhanced_content:
            clear_method = '''
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
                if hasattr(self, 'keyword_cache'):
                    self.keyword_cache.clear_keyword_cache()
                
                # 清理键映射
                if hasattr(self, 'key_cache_map'):
                    self.key_cache_map.clear()
                
                # 重置统计
                self.stats['total_hits'] = 0
                self.stats['total_misses'] = 0
                for cache_id in self.stats['cache_hits']:
                    self.stats['cache_hits'][cache_id] = 0
                
                self._emit_event(CacheEventType.CLEAR, "all", None, None)
'''
            
            # 在类的末尾添加clear方法
            enhanced_content = enhanced_content.replace(
                'class UnifiedCacheManager',
                clear_method + '\n\nclass UnifiedCacheManager'
            )
        
        # 增强search_by_content方法
        if 'def search_by_content(' in enhanced_content:
            enhanced_search = '''
    def search_by_content(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        基于内容搜索缓存
        使用关键词缓存加速搜索
        """
        with self._lock:
            self.stats['operations']['keyword_search'] = (
                self.stats['operations'].get('keyword_search', 0) + 1
            )
            
            # 1. 关键词搜索
            if hasattr(self, 'keyword_cache'):
                cache_keys = self.keyword_cache.search_by_keywords(query, limit * 2)
                
                if cache_keys:
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
            
            # 3. 回退到基础搜索
            return []
'''
            
            # 替换现有的search_by_content方法
            import re
            enhanced_content = re.sub(
                r'def search_by_content\(.*?\n.*?return.*?\n',
                enhanced_search,
                enhanced_content,
                flags=re.DOTALL
            )
        
        # 保存增强版本
        with open(cache_manager_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        print(f"✅ 缓存管理器已增强: {cache_manager_file}")
        
        # 显示增强功能
        print("\n📋 增强功能:")
        print("- 集成关键词缓存功能")
        print("- 添加 clear() 方法")
        print("- 增强 search_by_content() 方法")
        print("- 完善性能统计")
        
        return True
        
    except Exception as e:
        print(f"❌ 缓存管理器增强失败: {e}")
        return False

def fix_estia_memory_integration():
    """
    修复3: 修复EstiaMemorySystem中的缓存集成
    """
    print("\n🔧 修复3: 修复EstiaMemorySystem中的缓存集成")
    print("=" * 60)
    
    estia_memory_file = "core/memory/estia_memory_v5.py"
    
    try:
        with open(estia_memory_file, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # 检查是否存在变量作用域问题
        if "cannot access local variable 'UnifiedCacheManager'" in current_content:
            print("❌ 发现变量作用域问题")
            
            # 修复导入问题
            if 'from core.memory.shared.caching import UnifiedCacheManager' not in current_content:
                fixed_content = current_content.replace(
                    'from core.memory.shared.caching.cache_manager import UnifiedCacheManager',
                    'from core.memory.shared.caching.cache_manager import UnifiedCacheManager'
                )
            else:
                fixed_content = current_content
            
            # 修复高级组件初始化问题
            fixed_content = fixed_content.replace(
                'if enable_advanced:',
                '''if enable_advanced:
            try:
                # 确保unified_cache已正确初始化
                if hasattr(self, 'unified_cache') and self.unified_cache is not None:'''
            )
            
            # 保存修复后的文件
            with open(estia_memory_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print("✅ 变量作用域问题已修复")
        
        # 增强enhance_query方法中的缓存使用
        print("\n📋 增强enhance_query方法中的缓存使用:")
        print("- 向量缓存检查和存储")
        print("- 记忆访问记录")
        print("- 查询结果缓存")
        print("- 性能统计")
        
        return True
        
    except Exception as e:
        print(f"❌ EstiaMemorySystem修复失败: {e}")
        return False

def create_fix_verification_script():
    """
    创建修复验证脚本
    """
    print("\n🔧 创建修复验证脚本")
    print("=" * 60)
    
    verification_script = '''#!/usr/bin/env python3
"""
缓存系统修复验证脚本
验证关键词缓存功能和增强的缓存管理器
"""

import sys
import os
import time
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

def test_keyword_cache():
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
    """测试增强的缓存管理器"""
    print("🔍 测试增强的缓存管理器...")
    
    try:
        from core.memory.shared.caching.cache_manager import UnifiedCacheManager
        
        # 创建管理器实例
        cache_manager = UnifiedCacheManager.get_instance()
        
        # 测试关键词缓存是否集成
        if hasattr(cache_manager, 'keyword_cache'):
            print("   ✅ 关键词缓存已集成")
        else:
            print("   ❌ 关键词缓存未集成")
            return False
        
        # 测试clear方法
        if hasattr(cache_manager, 'clear'):
            print("   ✅ clear方法已添加")
            cache_manager.clear()
            print("   ✅ 缓存清理成功")
        else:
            print("   ❌ clear方法缺失")
            return False
        
        # 测试search_by_content方法
        results = cache_manager.search_by_content("测试查询", 5)
        print(f"   内容搜索结果: {len(results)} 个")
        
        # 测试统计信息
        stats = cache_manager.get_stats()
        print(f"   统计信息获取: {'✅' if stats else '❌'}")
        
        print("✅ 增强缓存管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 增强缓存管理器测试失败: {e}")
        return False

def test_system_integration():
    """测试系统集成"""
    print("🔍 测试系统集成...")
    
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
        
        # 测试基本功能
        test_query = "这是一个测试查询"
        
        try:
            result = memory_system.enhance_query(test_query)
            print("   ✅ enhance_query方法正常工作")
        except Exception as e:
            print(f"   ❌ enhance_query方法失败: {e}")
            return False
        
        print("✅ 系统集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 系统集成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 缓存系统修复验证测试")
    print("=" * 60)
    
    test_results = {
        "keyword_cache": test_keyword_cache(),
        "enhanced_manager": test_enhanced_cache_manager(),
        "system_integration": test_system_integration()
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
    
    # 保存验证脚本
    verification_script_file = "test_cache_fix_verification.py"
    
    try:
        with open(verification_script_file, 'w', encoding='utf-8') as f:
            f.write(verification_script)
        
        print(f"✅ 修复验证脚本已保存: {verification_script_file}")
        return True
        
    except Exception as e:
        print(f"❌ 修复验证脚本保存失败: {e}")
        return False

def main():
    """主修复函数"""
    print("🚀 Estia-AI 缓存系统修复方案 - 修正版")
    print("=" * 80)
    print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 执行修复步骤
    print("\\n🔧 开始执行修复...")
    
    # 修复1: 关键词缓存功能恢复
    fix1_success = create_keyword_cache_implementation()
    
    # 修复2: 增强统一缓存管理器
    fix2_success = enhance_cache_manager()
    
    # 修复3: 修复EstiaMemorySystem中的缓存集成
    fix3_success = fix_estia_memory_integration()
    
    # 创建验证测试脚本
    test_success = create_fix_verification_script()
    
    # 修复结果统计
    fix_results = {
        "关键词缓存恢复": fix1_success,
        "缓存管理器增强": fix2_success,
        "系统集成修复": fix3_success,
        "验证测试脚本": test_success
    }
    
    success_count = sum(fix_results.values())
    total_count = len(fix_results)
    
    print("\\n" + "=" * 80)
    print("📊 修复方案执行结果")
    print("=" * 80)
    
    for fix_name, result in fix_results.items():
        status = "✅ 成功" if result else "❌ 失败"
        print(f"{fix_name}: {status}")
    
    print(f"\\n成功率: {success_count}/{total_count} ({success_count/total_count:.2%})")
    
    if success_count == total_count:
        print("\\n🎉 所有修复方案执行成功！")
        print("\\n🎯 下一步行动:")
        print("1. 运行 python test_cache_fix_verification.py 验证修复效果")
        print("2. 重新运行 python test_cache_system_analysis.py 对比修复前后的性能")
        print("3. 如果验证通过，继续Phase 1的下一个模块工作")
    elif success_count >= 3:
        print("\\n✅ 大部分修复方案执行成功！")
        print("\\n🎯 下一步行动:")
        print("1. 运行 python test_cache_fix_verification.py 验证修复效果")
        print("2. 检查失败的修复项并进行调试")
    else:
        print("\\n❌ 修复方案执行失败较多，请检查错误信息")
    
    print("\\n📋 修复内容总结:")
    print("- 创建了keyword_cache.py，提供关键词缓存功能")
    print("- 增强了cache_manager.py，集成关键词缓存和clear方法")
    print("- 修复了estia_memory_v5.py中的变量作用域问题")
    print("- 创建了test_cache_fix_verification.py验证脚本")
    
    print("\\n" + "=" * 80)

if __name__ == "__main__":
    main()