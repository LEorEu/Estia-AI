"""
Estia AI 主程序入口
"""

import time
import logging
import os
import threading

from config import settings
from core.app import EstiaApp

def setup_logger():
    """设置日志记录器"""
    log_dir = settings.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger("estia")
    logger.setLevel(logging.INFO)
    
    # 文件处理器
    file_handler = logging.FileHandler(os.path.join(log_dir, "estia.log"), encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 格式化器
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def main():
    """主程序入口"""
    # 初始化日志
    logger = setup_logger()
    logger.info("🚀 Estia AI 启动中...")
    
    try:
        # 创建应用实例
        app = EstiaApp(logger)
        
        # 初始化应用
        app.initialize()
        
        # 启动记忆维护线程
        def memory_maintenance_task():
            while True:
                try:
                    app.perform_memory_maintenance()
                except Exception as e:
                    logger.error(f"记忆维护出错: {e}")
                
                # 休眠6小时后再次执行
                time.sleep(6 * 3600)
        
        maintenance_thread = threading.Thread(target=memory_maintenance_task, daemon=True)
        maintenance_thread.start()
        logger.info("✅ 记忆维护任务已启动")
        
        # 运行主循环
        app.run()
        
    except Exception as e:
        logger.error(f"❌ 程序初始化失败: {e}", exc_info=True)
        
if __name__ == "__main__":
    main()