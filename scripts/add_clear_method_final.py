#!/usr/bin/env python3
"""
为UnifiedCacheManager类添加clear方法的最终修复脚本
"""

import os
import sys

def add_clear_method_to_unified_cache_manager():
    """为UnifiedCacheManager类添加clear方法"""
    file_path = "core/memory/shared/caching/cache_manager.py"
    
    print("🔧 为UnifiedCacheManager类添加clear方法...")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经有clear方法在UnifiedCacheManager类中
        if 'def clear(self):' in content and 'class UnifiedCacheManager' in content:
            print("✅ UnifiedCacheManager类中已有clear方法")
            return True
        
        # 找到UnifiedCacheManager类的位置
        lines = content.split('\n')
        insert_pos = -1
        in_unified_cache_manager = False
        
        for i, line in enumerate(lines):
            if 'class UnifiedCacheManager' in line:
                in_unified_cache_manager = True
                continue
            
            if in_unified_cache_manager:
                # 找到类的结束位置或者找到一个合适的位置插入方法
                if line.strip() and not line.startswith('    ') and not line.startswith('#'):
                    # 找到类的结束位置
                    insert_pos = i
                    break
                elif 'def clear_all(self)' in line:
                    # 在clear_all方法后面添加clear方法
                    # 找到clear_all方法的结束位置
                    j = i + 1
                    while j < len(lines) and (lines[j].startswith('    ') or lines[j].strip() == ''):
                        j += 1
                    insert_pos = j
                    break
        
        if insert_pos == -1:
            print("❌ 无法找到合适的位置插入clear方法")
            return False
        
        # 添加clear方法
        clear_method = '''    def clear(self):
        """
        清空所有缓存（clear_all的别名方法）
        
        为了保持API一致性，提供clear方法作为clear_all的别名
        """
        return self.clear_all()
'''
        
        # 在指定位置插入clear方法
        lines.insert(insert_pos, clear_method)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("✅ clear方法添加成功")
        return True
        
    except Exception as e:
        print(f"❌ 添加clear方法失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主修复流程"""
    print("🚀 UnifiedCacheManager类clear方法最终修复")
    print("=" * 60)
    
    if add_clear_method_to_unified_cache_manager():
        print("=" * 60)
        print("✅ clear方法修复成功！")
        print("🚀 下一步: 运行 python test_cache_fix_verification.py 验证修复效果")
        print("📊 预期结果: 成功率从66.67%提升到100%")
        return True
    else:
        print("=" * 60)
        print("❌ clear方法修复失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)