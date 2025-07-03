#!/usr/bin/env python3
"""
数据一致性监控脚本
定期检查记忆存储系统的数据一致性，并在发现问题时自动修复
"""

import os
import sys
import time
import json
import schedule
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.memory.storage.memory_store import MemoryStore
    from core.utils.logger import get_logger
    logger = get_logger("estia.monitor.consistency")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("estia.monitor.consistency")

class DataConsistencyMonitor:
    """数据一致性监控器"""
    
    def __init__(self, 
                 db_path: str = None,
                 index_path: str = None,
                 report_dir: str = "logs/consistency_reports",
                 auto_repair: bool = True,
                 alert_threshold: str = "warning"):
        """
        初始化监控器
        
        参数:
            db_path: 数据库路径
            index_path: 向量索引路径  
            report_dir: 报告存储目录
            auto_repair: 是否自动修复问题
            alert_threshold: 告警阈值 ("healthy", "warning", "critical")
        """
        self.db_path = db_path or os.path.join("assets", "memory.db")
        self.index_path = index_path or os.path.join("data", "vectors", "memory_index.bin")
        self.report_dir = report_dir
        self.auto_repair = auto_repair
        self.alert_threshold = alert_threshold
        
        # 确保报告目录存在
        os.makedirs(self.report_dir, exist_ok=True)
        
        self.memory_store = None
        
    def initialize_memory_store(self):
        """初始化内存存储"""
        try:
            if self.memory_store is None:
                self.memory_store = MemoryStore(
                    db_path=self.db_path,
                    index_path=self.index_path
                )
                logger.info("内存存储初始化成功")
            return True
        except Exception as e:
            logger.error(f"初始化内存存储失败: {e}")
            return False
    
    def check_consistency(self) -> dict:
        """执行一致性检查"""
        try:
            if not self.initialize_memory_store():
                return {"status": "error", "error": "无法初始化内存存储"}
            
            logger.info("开始数据一致性检查...")
            report = self.memory_store.check_data_consistency()
            
            # 保存报告
            self.save_report(report)
            
            # 记录检查结果
            status = report.get("status", "unknown")
            logger.info(f"一致性检查完成，状态: {status}")
            
            if status != "healthy":
                logger.warning(f"发现数据一致性问题: {report.get('recommendations', [])}")
                
                # 如果启用自动修复且状态不是错误
                if self.auto_repair and status != "error":
                    self.auto_repair_issues(report)
            else:
                logger.info("数据一致性正常")
            
            return report
            
        except Exception as e:
            logger.error(f"一致性检查失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def auto_repair_issues(self, consistency_report: dict):
        """自动修复数据一致性问题"""
        try:
            logger.info("开始自动修复数据一致性问题...")
            
            # 确定修复选项
            repair_options = {
                "fix_missing_vectors": len(consistency_report.get("missing_vectors", [])) > 0,
                "remove_orphaned_vectors": len(consistency_report.get("orphaned_vectors", [])) > 0,
                "rebuild_faiss": len(consistency_report.get("faiss_sync_issues", [])) > 0
            }
            
            if any(repair_options.values()):
                repair_result = self.memory_store.repair_data_consistency(repair_options)
                
                # 保存修复报告
                self.save_repair_report(repair_result)
                
                repair_status = repair_result.get("status", "unknown")
                logger.info(f"自动修复完成，状态: {repair_status}")
                
                if repair_status == "success":
                    logger.info("✅ 所有问题已成功修复")
                elif repair_status == "partial_success":
                    logger.warning("⚠️ 部分问题已修复，仍有错误")
                else:
                    logger.error("❌ 自动修复失败")
            else:
                logger.info("没有需要修复的问题")
                
        except Exception as e:
            logger.error(f"自动修复失败: {e}")
    
    def save_report(self, report: dict):
        """保存一致性检查报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(self.report_dir, f"consistency_report_{timestamp}.json")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"一致性报告已保存: {report_file}")
            
        except Exception as e:
            logger.error(f"保存一致性报告失败: {e}")
    
    def save_repair_report(self, repair_result: dict):
        """保存修复报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            repair_file = os.path.join(self.report_dir, f"repair_report_{timestamp}.json")
            
            with open(repair_file, 'w', encoding='utf-8') as f:
                json.dump(repair_result, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"修复报告已保存: {repair_file}")
            
        except Exception as e:
            logger.error(f"保存修复报告失败: {e}")
    
    def get_summary_stats(self) -> dict:
        """获取汇总统计信息"""
        try:
            if not self.initialize_memory_store():
                return {"error": "无法初始化内存存储"}
            
            # 获取基本统计
            stats = self.memory_store.check_data_consistency()
            
            # 添加额外的统计信息
            extra_stats = {
                "last_check_time": datetime.now().isoformat(),
                "db_file_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0,
                "index_file_size": os.path.getsize(self.index_path) if os.path.exists(self.index_path) else 0,
                "auto_repair_enabled": self.auto_repair
            }
            
            stats.update(extra_stats)
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"error": str(e)}
    
    def cleanup_old_reports(self, days_to_keep: int = 30):
        """清理旧的报告文件"""
        try:
            current_time = time.time()
            cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
            
            report_files = os.listdir(self.report_dir)
            deleted_count = 0
            
            for file_name in report_files:
                if file_name.endswith('.json'):
                    file_path = os.path.join(self.report_dir, file_name)
                    file_time = os.path.getmtime(file_path)
                    
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"清理了 {deleted_count} 个旧报告文件")
            
        except Exception as e:
            logger.error(f"清理旧报告失败: {e}")

def run_scheduled_check():
    """运行计划的检查"""
    logger.info("="*50)
    logger.info("开始计划的数据一致性检查")
    
    monitor = DataConsistencyMonitor()
    report = monitor.check_consistency()
    
    # 输出关键信息
    status = report.get("status", "unknown")
    total_memories = report.get("total_memories", 0)
    total_vectors = report.get("total_vectors", 0)
    total_faiss = report.get("total_faiss_vectors", 0)
    
    logger.info(f"检查完成 - 状态: {status}")
    logger.info(f"记忆数: {total_memories}, 向量数: {total_vectors}, FAISS: {total_faiss}")
    
    if status != "healthy":
        issues = len(report.get("missing_vectors", [])) + len(report.get("orphaned_vectors", [])) + len(report.get("faiss_sync_issues", []))
        logger.warning(f"发现 {issues} 个问题")
    
    logger.info("="*50)

def setup_monitoring_schedule():
    """设置监控计划"""
    # 每小时检查一次
    schedule.every().hour.do(run_scheduled_check)
    
    # 每天凌晨3点执行深度检查和清理
    schedule.every().day.at("03:00").do(lambda: DataConsistencyMonitor().cleanup_old_reports())
    
    logger.info("监控计划已设置:")
    logger.info("- 每小时执行一致性检查")
    logger.info("- 每天凌晨3点清理旧报告")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据一致性监控脚本')
    parser.add_argument('--once', action='store_true', help='只执行一次检查')
    parser.add_argument('--no-repair', action='store_true', help='禁用自动修复')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='清理指定天数前的旧报告')
    
    args = parser.parse_args()
    
    # 创建监控器
    monitor = DataConsistencyMonitor(auto_repair=not args.no_repair)
    
    if args.stats:
        # 显示统计信息
        stats = monitor.get_summary_stats()
        print("\n📊 数据一致性统计信息:")
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return
    
    if args.cleanup:
        # 清理旧报告
        monitor.cleanup_old_reports(args.cleanup)
        print(f"✅ 已清理 {args.cleanup} 天前的旧报告")
        return
    
    if args.once:
        # 只执行一次检查
        print("🔍 执行单次数据一致性检查...")
        report = monitor.check_consistency()
        print(f"✅ 检查完成，状态: {report.get('status', 'unknown')}")
        return
    
    # 启动定期监控
    logger.info("🚀 启动数据一致性监控服务")
    setup_monitoring_schedule()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次是否有待执行的任务
    except KeyboardInterrupt:
        logger.info("👋 监控服务已停止")

if __name__ == "__main__":
    main() 