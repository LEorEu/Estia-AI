#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试文件更新脚本 - 更新到新记忆系统
"""

import os
import re
import glob

def update_test_file(file_path):
    """更新测试文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        original = content
        
        # 替换导入
        content = re.sub(r"from core\.memory\.enhanced_pipeline import create_enhanced_pipeline", 
                        "from core.memory import create_simple_pipeline", content)
        content = re.sub(r"create_enhanced_pipeline", "create_simple_pipeline", content)
        
        content = re.sub(r"from core\.memory\.memory_adapter import.*", 
                        "from core.memory import create_memory_manager", content)
        content = re.sub(r"create_memory_adapter", "create_memory_manager", content)
        
        content = re.sub(r"from core\.memory\.unified_manager import UnifiedMemoryManager", 
                        "from core.memory import EstiaMemoryManager", content)
        content = re.sub(r"UnifiedMemoryManager", "EstiaMemoryManager", content)
        
        # 替换方法调用
        content = re.sub(r"\.memory_adapter\.", ".", content)
        content = re.sub(r"adapter\.", "manager.", content)
        content = re.sub(r"adapter = ", "manager = ", content)
        
        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 已更新: {file_path}")
        else:
            print(f"⏭️  无需更新: {file_path}")
            
    except Exception as e:
        print(f"❌ 更新失败 {file_path}: {e}")

def main():
    test_files = glob.glob("tests/test_*.py") 
    for file in test_files:
        update_test_file(file)

if __name__ == "__main__":
    main()

