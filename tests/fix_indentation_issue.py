#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复缩进问题 - 解决estia_memory_v5.py中的IndentationError
"""

import os
import re

def fix_indentation_in_estia_memory():
    """修复estia_memory_v5.py中的缩进问题"""
    
    file_path = "core/memory/estia_memory_v5.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建修复后的内容
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # 修复第161行开始的缩进问题
            if line_num >= 158 and line_num <= 177:
                # 检查是否是我们添加的组件初始化代码
                if any(keyword in line for keyword in [
                    '# === 文档标准的核心组件初始化 ===',
                    '# 关联网络 (Step 6 核心组件)',
                    'from ..old_memory.association.network import AssociationNetwork',
                    'association_network = AssociationNetwork(db_manager)',
                    "components['association_network'] = association_network",
                    'self.logger.info("✅ 关联网络初始化成功 (文档Step 6)")',
                    '# 历史检索器 (Step 7 核心组件)',
                    'from .managers.sync_flow.context.history import HistoryRetriever',
                    'history_retriever = HistoryRetriever(db_manager)',
                    "components['history_retriever'] = history_retriever",
                    'self.logger.info("✅ 历史检索器初始化成功 (文档Step 7)")',
                    '# 记忆评分器 (Step 8 核心组件)',
                    'from .managers.sync_flow.ranking.scorer import MemoryScorer',
                    'scorer = MemoryScorer()',
                    "components['scorer'] = scorer",
                    'self.logger.info("✅ 记忆评分器初始化成功 (文档Step 8)")',
                    'from .managers.sync_flow.retrieval.faiss_search import FAISSSearchEngine'
                ]):
                    # 修正缩进为正确的20个空格（5级缩进）
                    stripped_line = line.lstrip()
                    if stripped_line:  # 非空行
                        fixed_lines.append('                    ' + stripped_line)
                    else:  # 空行
                        fixed_lines.append('')
                else:
                    # 保持原有行不变
                    fixed_lines.append(line)
            else:
                # 其他行保持不变
                fixed_lines.append(line)
        
        # 重新组装内容
        fixed_content = '\n'.join(fixed_lines)
        
        # 写入修复后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ 缩进问题修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def main():
    """主修复流程"""
    
    print("🔧 开始修复缩进问题...")
    
    if fix_indentation_in_estia_memory():
        print("✅ 缩进修复完成")
        print("\n📋 下一步操作:")
        print("   运行测试脚本: python test_14_step_workflow.py")
        return True
    else:
        print("❌ 缩进修复失败")
        return False

if __name__ == "__main__":
    main()