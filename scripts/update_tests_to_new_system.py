#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试文件更新脚本
将所有使用旧记忆系统的测试文件更新到新系统
"""

import os
import re
import glob

def update_import_statements(content):
    """更新导入语句"""
    # 替换旧的导入
    replacements = [
        # enhanced_pipeline -> simple_pipeline
        (r'from core\.memory\.enhanced_pipeline import create_enhanced_pipeline',
         'from core.memory import create_simple_pipeline'),
        (r'create_enhanced_pipeline\(advanced=([^)]+)\)',
         r'create_simple_pipeline(advanced=\1)'),
        (r'create_enhanced_pipeline\(\)',
         'create_simple_pipeline()'),
        
        # memory_adapter -> 直接使用manager
        (r'from core\.memory\.memory_adapter import MemoryAdapter, create_memory_adapter',
         'from core.memory import create_memory_manager'),
        (r'from core\.memory\.memory_adapter import.*',
         'from core.memory import create_memory_manager'),
        (r'create_memory_adapter\(advanced=([^)]+)\)',
         r'create_memory_manager(advanced=\1)'),
        (r'create_memory_adapter\(\)',
         'create_memory_manager()'),
        
        # unified_manager -> manager
        (r'from core\.memory\.unified_manager import UnifiedMemoryManager',
         'from core.memory import EstiaMemoryManager'),
        (r'UnifiedMemoryManager\(',
         'EstiaMemoryManager('),
        
        # 更新方法调用
        (r'\.memory_adapter\.store_memory\(',
         '.store_memory('),
        (r'\.memory_adapter\.retrieve_memories\(',
         '.retrieve_memories('),
        (r'\.memory_adapter\.get_memory_stats\(\)',
         '.get_statistics()'),
        (r'\.memory_adapter\.memory_manager',
         '.memory_manager'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    return content

def update_variable_names(content):
    """更新变量名"""
    # 更新变量名和对象引用
    replacements = [
        (r'enhanced_system\.memory_adapter', 'memory_system'),
        (r'enhanced_system', 'memory_system'),
        (r'pipeline\.memory_adapter', 'pipeline'),
        (r'adapter = create_memory_adapter', 'manager = create_memory_manager'),
        (r'adapter\.', 'manager.'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    return content

def update_test_file(file_path):
    """更新单个测试文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 应用更新
        content = update_import_statements(content)
        content = update_variable_names(content)
        
        # 如果有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已更新: {file_path}")
            return True
        else:
            print(f"⏭️  无需更新: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 更新失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("🔄 开始更新测试文件到新记忆系统...")
    
    # 查找所有测试文件
    test_files = glob.glob("tests/test_*.py")
    
    updated_count = 0
    total_count = len(test_files)
    
    for test_file in test_files:
        if update_test_file(test_file):
            updated_count += 1
    
    print(f"\n📊 更新完成:")
    print(f"   • 总文件数: {total_count}")
    print(f"   • 已更新: {updated_count}")
    print(f"   • 无需更新: {total_count - updated_count}")
    
    print(f"\n💡 接下来你需要:")
    print(f"   1. 运行测试验证更新结果")
    print(f"   2. 手动检查复杂的测试逻辑")
    print(f"   3. 更新任何特定的测试断言")

if __name__ == "__main__":
    main() 