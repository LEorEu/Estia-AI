#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Estia AI助手启动入口

使用方法：
    python main.py  # 默认启动语音交互模式
    或
    python main.py --mode text  # 文本交互模式
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# 配置日志
from config import settings

def setup_logging():
    """设置日志记录"""
    # 创建日志目录
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    # 生成日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(settings.LOG_DIR, f"estia_{timestamp}.log")
    
    # 配置日志格式和级别
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # 创建控制台处理器（使用默认编码）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # 创建文件处理器（指定UTF-8编码）
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # 添加处理器到根记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logging.getLogger("estia.main")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Estia AI助手")
    
    parser.add_argument(
        "--mode",
        choices=["voice", "text", "api"],
        default="voice",
        help="交互模式: voice (语音), text (文本), api (API服务)"
    )
    
    # 添加流式输出相关参数
    parser.add_argument(
        "--stream",
        action="store_true",
        help="启用流式输出（文本和语音）"
    )
    
    parser.add_argument(
        "--text-stream",
        action="store_true",
        help="仅启用文本流式输出"
    )
    
    parser.add_argument(
        "--audio-stream",
        action="store_true",
        help="仅启用语音流式输出"
    )
    
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="禁用所有流式输出"
    )
    
    return parser.parse_args()

def main():
    """程序入口"""
    # 设置日志
    logger = setup_logging()
    logger.info("Estia AI助手启动中...")
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 根据交互模式和命令行参数更新流式输出配置
    if args.mode == "text":
        # 文本模式下默认禁用音频流
        if not (args.stream or args.audio_stream):
            settings.ENABLE_AUDIO_STREAM = False
    
    # 根据命令行参数更新流式输出配置
    if args.no_stream:
        settings.ENABLE_STREAM_OUTPUT = False
        settings.ENABLE_TEXT_STREAM = False
        settings.ENABLE_AUDIO_STREAM = False
    elif args.stream:
        settings.ENABLE_STREAM_OUTPUT = True
        settings.ENABLE_TEXT_STREAM = True
        settings.ENABLE_AUDIO_STREAM = True
    elif args.text_stream:
        settings.ENABLE_STREAM_OUTPUT = True
        settings.ENABLE_TEXT_STREAM = True
        settings.ENABLE_AUDIO_STREAM = False
    elif args.audio_stream:
        settings.ENABLE_STREAM_OUTPUT = True
        settings.ENABLE_TEXT_STREAM = False
        settings.ENABLE_AUDIO_STREAM = True
    
    # 显示流式输出配置
    if settings.ENABLE_STREAM_OUTPUT:
        logger.info("流式输出配置:")
        logger.info(f"  文本流式输出: {'启用' if settings.ENABLE_TEXT_STREAM else '禁用'}")
        logger.info(f"  语音流式输出: {'启用' if settings.ENABLE_AUDIO_STREAM else '禁用'}")
        logger.info(f"  流式模式: {settings.STREAM_MODE}")
        logger.info(f"  优先级: {settings.STREAM_PRIORITY}")
    
    try:
        # 导入并运行应用
        from core.app import run_app
        run_app(interaction_mode=args.mode)
    except KeyboardInterrupt:
        logger.info("用户中断，程序退出")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print("\n程序遇到错误，详情请查看日志。")
        sys.exit(1)

if __name__ == "__main__":
    main()