"""
配置加载器 - 用于加载和处理配置文件
"""

import os
import logging
import importlib.util

def load_config(config_path=None):
    """
    加载配置文件
    
    参数:
        config_path: 配置文件路径，如果为None，则使用默认的配置
        
    返回:
        配置对象
    """
    try:
        # 如果没有提供路径，使用默认配置
        if config_path is None:
            from config import settings
            return settings
            
        # 如果提供了路径，从文件加载
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件未找到: {config_path}")
            
        # 从文件路径加载模块
        spec = importlib.util.spec_from_file_location("settings", config_path)
        if spec is None:
            raise ImportError(f"无法加载配置文件: {config_path}")
            
        settings = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            raise ImportError(f"无法加载配置文件的加载器: {config_path}")
            
        spec.loader.exec_module(settings)
        
        return settings
        
    except Exception as e:
        logging.error(f"加载配置失败: {e}")
        # 返回一个空对象作为后备
        class EmptySettings:
            LOG_LEVEL = "INFO"
            LOG_DIR = "./logs"
        return EmptySettings()
