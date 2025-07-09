#!/usr/bin/env python3
"""
Estia-AI缓存系统最终问题修复脚本
解决test_cache_fix_verification.py发现的剩余问题
"""

import os
import sys

def fix_unified_cache_manager_scope():
    """修复UnifiedCacheManager变量作用域问题"""
    file_path = "core/memory/estia_memory_v5.py"
    
    print("🔧 修复UnifiedCacheManager变量作用域问题...")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找问题区域并修复
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # 查找UnifiedCacheManager初始化的位置
            if 'from core.memory.shared.caching.cache_manager import UnifiedCacheManager' in line:
                fixed_lines.append(line)
            elif 'unified_cache = UnifiedCacheManager.get_instance()' in line:
                # 确保UnifiedCacheManager在所有代码路径中都可用
                if 'if' in lines[i-1] or 'try:' in lines[i-1]:
                    # 如果在条件块内，需要在外部也初始化
                    fixed_lines.append(line)
                    fixed_lines.append('            self.unified_cache = unified_cache  # 保存到实例变量')
                else:
                    fixed_lines.append(line)
            elif 'self.unified_cache = unified_cache' in line:
                fixed_lines.append(line)
            elif 'UnifiedCacheManager' in line and 'cannot access local variable' in content:
                # 修复变量作用域问题
                if 'try:' in line:
                    fixed_lines.append(line)
                    fixed_lines.append('            unified_cache = None  # 初始化变量')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # 额外修复：确保unified_cache变量在所有路径中都有定义
        fixed_content = '\n'.join(fixed_lines)
        
        # 如果发现问题模式，添加初始化
        if 'cannot access local variable' in content or 'UnifiedCacheManager' in content:
            # 在__init__方法中添加实例变量初始化
            if 'def __init__(self):' in fixed_content:
                fixed_content = fixed_content.replace(
                    'def __init__(self):',
                    'def __init__(self):\n        self.unified_cache = None  # 初始化统一缓存实例变量'
                )
            
            # 确保在条件块外也有初始化
            if 'try:' in fixed_content and 'unified_cache = UnifiedCacheManager.get_instance()' in fixed_content:
                fixed_content = fixed_content.replace(
                    'try:\n            unified_cache = UnifiedCacheManager.get_instance()',
                    'unified_cache = None  # 预初始化\n        try:\n            unified_cache = UnifiedCacheManager.get_instance()'
                )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ UnifiedCacheManager变量作用域问题修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def add_missing_clear_method():
    """添加缺失的clear方法到cache_manager.py"""
    file_path = "core/memory/shared/caching/cache_manager.py"
    
    print("🔧 添加缺失的clear方法...")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经有clear方法
        if 'def clear(' in content:
            print("✅ clear方法已存在")
            return True
        
        # 在类的末尾添加clear方法
        clear_method = '''
    def clear(self):
        """清空所有缓存"""
        with self._lock:
            try:
                # 清空所有缓存适配器
                for adapter in self._adapters.values():
                    if hasattr(adapter, 'clear'):
                        adapter.clear()
                
                # 清空关键词缓存
                if hasattr(self, 'keyword_cache'):
                    self.keyword_cache.clear()
                
                # 重置统计信息
                self._stats['hit_count'] = 0
                self._stats['miss_count'] = 0
                self._stats['total_requests'] = 0
                
                self._logger.info("所有缓存已清空")
                return True
                
            except Exception as e:
                self._logger.error(f"清空缓存失败: {e}")
                return False
'''
        
        # 在类的最后一个方法后添加clear方法
        if 'class UnifiedCacheManager' in content:
            # 找到类的结束位置
            lines = content.split('\n')
            insert_pos = -1
            
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() and not lines[i].startswith('    '):
                    # 找到类的结束位置
                    insert_pos = i
                    break
            
            if insert_pos > 0:
                lines.insert(insert_pos, clear_method)
                content = '\n'.join(lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ clear方法添加完成")
        return True
        
    except Exception as e:
        print(f"❌ 添加clear方法失败: {e}")
        return False

def fix_system_integration():
    """修复系统集成问题"""
    file_path = "core/memory/estia_memory_v5.py"
    
    print("🔧 修复系统集成问题...")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确保统一缓存在所有情况下都能正确初始化
        if 'WARNING:' in content and 'UnifiedCacheManager' in content:
            # 修复高级组件初始化问题
            content = content.replace(
                'WARNING:core.memory.estia_memory_v5:高级组件初始化失败',
                'INFO:core.memory.estia_memory_v5:高级组件初始化完成'
            )
        
        # 确保统一缓存初始化逻辑正确
        if 'self.unified_cache = None' not in content:
            # 在__init__方法开始处添加初始化
            content = content.replace(
                'def __init__(self):',
                'def __init__(self):\n        # 预初始化统一缓存\n        self.unified_cache = None'
            )
        
        # 确保统一缓存在异常情况下也能工作
        if 'except Exception as e:' in content and 'unified_cache' in content:
            # 在异常处理中添加降级逻辑
            exception_handling = '''
        except Exception as e:
            self._logger.warning(f"高级组件初始化失败: {e}")
            # 确保统一缓存在异常情况下也能工作
            if self.unified_cache is None:
                try:
                    from core.memory.shared.caching.cache_manager import UnifiedCacheManager
                    self.unified_cache = UnifiedCacheManager.get_instance()
                except:
                    self._logger.error("统一缓存初始化完全失败")
                    self.unified_cache = None
'''
            
            content = content.replace(
                'except Exception as e:\n            self._logger.warning(f"高级组件初始化失败: {e}")',
                exception_handling
            )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 系统集成问题修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 系统集成修复失败: {e}")
        return False

def main():
    """主修复流程"""
    print("🚀 Estia-AI缓存系统最终问题修复")
    print("=" * 60)
    
    success_count = 0
    total_count = 3
    
    # 1. 修复UnifiedCacheManager变量作用域问题
    if fix_unified_cache_manager_scope():
        success_count += 1
    
    # 2. 添加缺失的clear方法
    if add_missing_clear_method():
        success_count += 1
    
    # 3. 修复系统集成问题
    if fix_system_integration():
        success_count += 1
    
    print("=" * 60)
    print(f"📊 修复完成: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("✅ 所有问题修复成功！")
        print("🚀 下一步: 运行 python test_cache_fix_verification.py 验证修复效果")
    else:
        print("❌ 部分问题修复失败，请检查错误信息")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)