#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整重新修复14步工作流程 - 从备份开始正确修复
解决缩进问题，确保代码正确性
"""

import os
import re

def restore_and_fix_properly():
    """从备份恢复并正确修复"""
    
    main_file = "core/memory/estia_memory_v5.py"
    backup_file = "core/memory/estia_memory_v5.py.backup"
    
    if not os.path.exists(backup_file):
        print(f"❌ 备份文件不存在: {backup_file}")
        return False
    
    try:
        # 从备份恢复
        with open(backup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ 从备份恢复: {backup_file}")
        
        # 查找正确的插入位置：FAISS初始化之后
        # 寻找这个模式：components['faiss_retriever'] = faiss_retriever
        faiss_pattern = r'(                    components\[\'faiss_retriever\'\] = faiss_retriever\s+                    self\.logger\.info\("✅ 高级检索组件初始化成功"\))'
        
        replacement = r'''\1
                    
                    # === 文档标准的核心组件初始化 ===
                    
                    # 关联网络 (Step 6 核心组件)
                    from ..old_memory.association.network import AssociationNetwork
                    association_network = AssociationNetwork(db_manager)
                    components['association_network'] = association_network
                    self.logger.info("✅ 关联网络初始化成功 (文档Step 6)")
                    
                    # 历史检索器 (Step 7 核心组件)
                    from .managers.sync_flow.context.history import HistoryRetriever
                    history_retriever = HistoryRetriever(db_manager)
                    components['history_retriever'] = history_retriever
                    self.logger.info("✅ 历史检索器初始化成功 (文档Step 7)")
                    
                    # 记忆评分器 (Step 8 核心组件)
                    from .managers.sync_flow.ranking.scorer import MemoryScorer
                    scorer = MemoryScorer()
                    components['scorer'] = scorer
                    self.logger.info("✅ 记忆评分器初始化成功 (文档Step 8)")'''
        
        # 应用修复
        new_content = re.sub(faiss_pattern, replacement, content)
        
        # 验证修改是否成功
        if 'AssociationNetwork' not in new_content:
            print("❌ 第一种方法失败，尝试备用方案...")
            
            # 备用方案：寻找except Exception as e:之前的位置
            except_pattern = r'(\s+)(except Exception as e:\s+self\.logger\.warning\(f"高级组件初始化失败: \{e\}"\))'
            
            replacement2 = r'''                    
                    # === 文档标准的核心组件初始化 ===
                    
                    # 关联网络 (Step 6 核心组件)
                    from ..old_memory.association.network import AssociationNetwork
                    association_network = AssociationNetwork(db_manager)
                    components['association_network'] = association_network
                    self.logger.info("✅ 关联网络初始化成功 (文档Step 6)")
                    
                    # 历史检索器 (Step 7 核心组件) 
                    from .managers.sync_flow.context.history import HistoryRetriever
                    history_retriever = HistoryRetriever(db_manager)
                    components['history_retriever'] = history_retriever
                    self.logger.info("✅ 历史检索器初始化成功 (文档Step 7)")
                    
                    # 记忆评分器 (Step 8 核心组件)
                    from .managers.sync_flow.ranking.scorer import MemoryScorer
                    scorer = MemoryScorer()
                    components['scorer'] = scorer
                    self.logger.info("✅ 记忆评分器初始化成功 (文档Step 8)")
                    
\1\2'''
            
            new_content = re.sub(except_pattern, replacement2, content)
        
        # 最终验证
        if 'AssociationNetwork' in new_content and 'HistoryRetriever' in new_content and 'MemoryScorer' in new_content:
            # 写入修复后的文件
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ estia_memory_v5.py 重新修复完成")
            print("   - AssociationNetwork (Step 6): ✅")
            print("   - HistoryRetriever (Step 7): ✅")
            print("   - MemoryScorer (Step 8): ✅")
            return True
        else:
            print("❌ 自动修复失败，手动创建正确版本...")
            return create_manual_fix()
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def create_manual_fix():
    """手动创建正确的修复版本"""
    
    main_file = "core/memory/estia_memory_v5.py"
    backup_file = "core/memory/estia_memory_v5.py.backup"
    
    try:
        # 读取备份文件
        with open(backup_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 找到插入位置（在FAISS初始化之后）
        insert_index = -1
        for i, line in enumerate(lines):
            if '✅ 高级检索组件初始化成功' in line:
                insert_index = i + 1
                break
        
        if insert_index == -1:
            print("❌ 找不到插入位置")
            return False
        
        # 准备要插入的代码行
        new_lines = [
            "                    \n",
            "                    # === 文档标准的核心组件初始化 ===\n",
            "                    \n",
            "                    # 关联网络 (Step 6 核心组件)\n",
            "                    from ..old_memory.association.network import AssociationNetwork\n",
            "                    association_network = AssociationNetwork(db_manager)\n",
            "                    components['association_network'] = association_network\n",
            "                    self.logger.info(\"✅ 关联网络初始化成功 (文档Step 6)\")\n",
            "                    \n",
            "                    # 历史检索器 (Step 7 核心组件)\n",
            "                    from .managers.sync_flow.context.history import HistoryRetriever\n",
            "                    history_retriever = HistoryRetriever(db_manager)\n",
            "                    components['history_retriever'] = history_retriever\n",
            "                    self.logger.info(\"✅ 历史检索器初始化成功 (文档Step 7)\")\n",
            "                    \n",
            "                    # 记忆评分器 (Step 8 核心组件)\n",
            "                    from .managers.sync_flow.ranking.scorer import MemoryScorer\n",
            "                    scorer = MemoryScorer()\n",
            "                    components['scorer'] = scorer\n",
            "                    self.logger.info(\"✅ 记忆评分器初始化成功 (文档Step 8)\")\n",
            "                    \n"
        ]
        
        # 插入新代码
        fixed_lines = lines[:insert_index] + new_lines + lines[insert_index:]
        
        # 写入修复后的文件
        with open(main_file, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print("✅ 手动修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 手动修复失败: {e}")
        return False

def main():
    """主修复流程"""
    
    print("🔧 开始重新修复14步工作流程...")
    print("="*50)
    
    if restore_and_fix_properly():
        print("\n✅ 修复完成！")
        print("\n📋 下一步操作:")
        print("   运行测试脚本: python test_14_step_workflow.py")
        return True
    else:
        print("\n❌ 修复失败")
        return False

if __name__ == "__main__":
    main()