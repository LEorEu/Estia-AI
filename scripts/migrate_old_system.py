#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
旧系统迁移脚本
将 core/old_memory 中的成熟模块迁移到新的六大模块架构中
"""

import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemMigrator:
    """系统迁移器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.old_memory_dir = self.project_root / "core" / "old_memory"
        self.new_memory_dir = self.project_root / "core" / "memory"
        
        # 迁移映射配置
        self.migration_map = {
            # LLM搜索工具 → 异步流程管理器
            "memory_search.py": "managers/async_flow/tools/memory_search_tools.py",
            
            # 异步评估器 → 异步流程管理器
            "evaluator/async_evaluator.py": "managers/async_flow/evaluator/async_evaluator.py",
            "evaluator/async_startup_manager.py": "managers/async_flow/evaluator/async_startup_manager.py",
            
            # 系统统计 → 监控流程管理器
            "system_stats.py": "managers/monitor_flow/monitoring/system_stats.py",
            
            # 生命周期管理 → 生命周期管理器
            "lifecycle_management.py": "managers/lifecycle/lifecycle_management.py",
            
            # 旧系统的检索组件 → 同步流程管理器
            "retrieval/smart_retriever.py": "managers/sync_flow/retrieval/smart_retriever.py",
            "retrieval/faiss_search.py": "managers/sync_flow/retrieval/faiss_search.py",
            
            # 关联网络 → 同步流程管理器  
            "association/": "managers/sync_flow/association/",
            
            # 上下文管理 → 同步流程管理器
            "context/": "managers/sync_flow/context/",
            
            # 排序评分 → 同步流程管理器
            "ranking/": "managers/sync_flow/ranking/",
            
            # 存储组件 → 同步流程管理器
            "storage/": "managers/sync_flow/storage/",
            
            # 嵌入组件 → 共享模块
            "embedding/": "shared/embedding/",
            
            # 情感分析 → 共享模块
            "emotion/": "shared/emotion/",
            
            # 用户画像 → 异步流程管理器
            "profiling/": "managers/async_flow/profiling/",
            
            # 初始化组件 → 同步流程管理器
            "init/": "managers/sync_flow/init/",
        }
        
    def migrate_all(self):
        """执行完整迁移"""
        logger.info("🚀 开始迁移旧系统模块到新架构")
        
        # 1. 检查旧系统是否存在
        if not self.old_memory_dir.exists():
            logger.error(f"旧系统目录不存在: {self.old_memory_dir}")
            return False
        
        # 2. 创建必要的目录结构
        self._create_directory_structure()
        
        # 3. 执行模块迁移
        success_count = 0
        total_count = len(self.migration_map)
        
        for old_path, new_path in self.migration_map.items():
            if self._migrate_single_module(old_path, new_path):
                success_count += 1
        
        logger.info(f"✅ 迁移完成: {success_count}/{total_count} 个模块迁移成功")
        
        # 4. 修复导入路径
        self._fix_import_paths()
        
        return success_count == total_count
    
    def _create_directory_structure(self):
        """创建新系统的目录结构"""
        directories = [
            "managers/async_flow/tools",
            "managers/async_flow/evaluator", 
            "managers/async_flow/profiling",
            "managers/monitor_flow/monitoring",
            "managers/sync_flow/association",
            "managers/sync_flow/context",
            "managers/sync_flow/ranking",
            "managers/sync_flow/storage",
            "shared/embedding",
            "shared/emotion"
        ]
        
        for dir_path in directories:
            full_path = self.new_memory_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            # 创建 __init__.py 文件
            init_file = full_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text('# -*- coding: utf-8 -*-\n')
    
    def _migrate_single_module(self, old_path: str, new_path: str) -> bool:
        """迁移单个模块"""
        try:
            old_full_path = self.old_memory_dir / old_path
            new_full_path = self.new_memory_dir / new_path
            
            if not old_full_path.exists():
                logger.warning(f"源文件不存在: {old_full_path}")
                return False
            
            # 确保目标目录存在
            new_full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if old_full_path.is_file():
                # 复制文件
                shutil.copy2(old_full_path, new_full_path)
                logger.info(f"📁 文件迁移: {old_path} → {new_path}")
            else:
                # 复制目录
                if new_full_path.exists():
                    shutil.rmtree(new_full_path)
                shutil.copytree(old_full_path, new_full_path)
                logger.info(f"📂 目录迁移: {old_path} → {new_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"迁移失败 {old_path} → {new_path}: {e}")
            return False
    
    def _fix_import_paths(self):
        """修复迁移后的导入路径"""
        logger.info("🔧 开始修复导入路径")
        
        # 需要修复的文件模式
        import_fixes = [
            # 修复旧系统导入
            ("from ..init.db_manager", "from ...managers.sync_flow.init.db_manager"),
            ("from ..memory_cache", "from ...shared.caching"),
            ("from ..caching", "from ...shared.caching"),
            ("from ..embedding", "from ...shared.embedding"),
            ("from ..emotion", "from ...shared.emotion"),
            ("from core.dialogue.engine", "from ....dialogue.engine"),
            ("from core.prompts.memory_evaluation", "from ....prompts.memory_evaluation"),
        ]
        
        # 遍历新系统目录，修复导入
        for root, dirs, files in os.walk(self.new_memory_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    self._fix_file_imports(file_path, import_fixes)
    
    def _fix_file_imports(self, file_path: Path, import_fixes: list):
        """修复单个文件的导入路径"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            for old_import, new_import in import_fixes:
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    logger.debug(f"修复导入: {file_path.name} - {old_import} → {new_import}")
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"✅ 导入路径修复完成: {file_path.relative_to(self.project_root)}")
                
        except Exception as e:
            logger.error(f"修复导入路径失败 {file_path}: {e}")

def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    migrator = SystemMigrator()
    
    if migrator.migrate_all():
        print("✅ 迁移成功完成")
        print("🔄 建议接下来运行测试，确保迁移的模块正常工作")
    else:
        print("❌ 迁移过程中出现错误，请检查日志")

if __name__ == "__main__":
    main() 