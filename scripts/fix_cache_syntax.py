#!/usr/bin/env python3
"""
修复cache_manager.py中的语法错误
"""

import sys
import os

def fix_cache_manager_syntax():
    """修复cache_manager.py中的语法错误"""
    print("🔧 修复cache_manager.py中的语法错误")
    print("=" * 60)
    
    cache_manager_file = "core/memory/shared/caching/cache_manager.py"
    
    try:
        # 读取文件内容
        with open(cache_manager_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复search_by_content方法中的语法错误
        # 问题：缺少try语句但有except语句
        fixed_content = content.replace(
            '''def search_by_content(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        基于内容搜索缓存
        使用关键词缓存加速搜索
        """
        with self._lock:''',
            '''def search_by_content(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        基于内容搜索缓存
        使用关键词缓存加速搜索
        """
        try:
            with self._lock:'''
        )
        
        # 保存修复后的文件
        with open(cache_manager_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ 语法错误已修复: {cache_manager_file}")
        print("   - 在search_by_content方法中添加了缺失的try语句")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 修复cache_manager.py语法错误")
    print("=" * 60)
    
    success = fix_cache_manager_syntax()
    
    if success:
        print("\n✅ 语法错误修复成功！")
        print("\n🎯 下一步行动:")
        print("1. 运行 python test_cache_fix_verification.py 重新验证")
        print("2. 如果验证通过，运行 python test_cache_system_analysis.py 测试性能")
    else:
        print("\n❌ 语法错误修复失败，请检查错误信息")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()