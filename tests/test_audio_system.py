"""
测试音频系统 - 热键触发录音和语音交互
"""

import os
import sys
import logging

# 确保能够导入core模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from core.audio.keyboard_control import start_keyboard_controller

# 设置日志
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("test_audio")

def test_llm_response(text):
    """测试用的LLM回复处理函数"""
    logger.info(f"用户说: {text}")
    responses = {
        "你好": "你好！我是艾丝缇娅，很高兴为你服务！",
        "你是谁": "我是艾丝缇娅，你的AI助手。",
        "今天天气怎么样": "我没有实时天气信息，但希望你今天过得愉快！",
        "再见": "再见！有需要随时叫我！"
    }
    
    # 简单关键词匹配
    for key, response in responses.items():
        if key in text:
            return response
    
    # 默认回复
    return "我听到你说了，但我还在学习如何回应这种对话。"

def main():
    """主函数"""
    print("开始音频系统测试...")
    
    # 启动键盘控制器，并传入我们自己的LLM处理函数
    start_keyboard_controller(llm_callback=test_llm_response)
    
    print("测试结束")

if __name__ == "__main__":
    main() 