"""
通用日志工具，提供一致的UTF-8日志配置
"""

import os
import logging
from config import settings

def setup_logger(name, log_file=None, level=None):
    """
    设置并获取logger
    
    参数:
        name: 日志记录器名称
        log_file: 日志文件名（如果不提供，将使用'{name}.log'）
        level: 日志级别（如果不提供，将使用settings.LOG_LEVEL）
        
    返回:
        配置好的logger
    """
    # 确保日志目录存在
    log_dir = getattr(settings, 'LOG_DIR', './logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 确定日志级别
    if level is None:
        level = getattr(settings, 'LOG_LEVEL', 'INFO')
    
    # 确定日志文件
    if log_file is None:
        log_file = os.path.join(log_dir, f'{name}.log')
    else:
        log_file = os.path.join(log_dir, log_file)
    
    # 获取logger
    logger = logging.getLogger(name)
    
    # 防止重复添加处理器
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(getattr(logging, level) if isinstance(level, str) else level)
    
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, level) if isinstance(level, str) else level)
    
    # 添加处理器
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name):
    """
    获取一个已配置的logger
    
    参数:
        name: 日志记录器名称
        
    返回:
        配置好的logger
    """
    # 先检查logger是否已存在
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    # 如果不存在，创建一个新的
    return setup_logger(name)
