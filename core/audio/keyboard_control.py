"""
键盘控制音频交互模块 - 提供热键触发录音和语音交互功能
"""

import os
import time
import logging
import msvcrt  # Windows下的键盘输入模块

from config import settings
from core.audio.system import AudioSystem

# 设置日志
logger = logging.getLogger("estia.audio.keyboard")

class KeyboardAudioController:
    """键盘控制音频交互类，提供热键控制录音和响应功能"""
    
    def __init__(self, audio_system=None, llm_callback=None):
        """
        初始化键盘音频控制器
        
        参数:
            audio_system: AudioSystem实例，如果为None则自动创建
            llm_callback: 处理语音转文本后的回调函数，接收文本参数并返回响应文本
        """
        self.logger = logger
        self.audio_system = audio_system or AudioSystem()
        
        # 检查回调函数
        if llm_callback is None:
            self.logger.warning("未提供LLM回调函数，将使用简单的回显功能")
            # 简单的回显回调，实际应用中应替换为真实的LLM处理
            self.llm_callback = lambda text: f"收到: '{text}'"
        else:
            self.llm_callback = llm_callback
    
    def start_hotkey_listener(self, record_key='1', quit_key='q'):
        """
        启动热键监听，并根据按键进行相应处理
        
        参数:
            record_key: 触发录音的按键
            quit_key: 退出程序的按键
        """
        print("\n=== 键盘命令模式 ===")
        print(f"按下 '{record_key}' 开始录音")
        print(f"按下 '空格键' 可以提前结束录音")
        print(f"按下 '{quit_key}' 退出程序")
        print("等待按键输入...")
        
        while True:
            if msvcrt.kbhit():  # 检查是否有按键输入
                key = msvcrt.getch().decode('utf-8', errors='ignore')
                
                if key.lower() == quit_key.lower():
                    print("\n退出监听...")
                    break
                    
                elif key == record_key:
                    self._handle_recording()
                
            time.sleep(0.1)  # 短暂休眠以降低CPU使用率
    
    def _handle_recording(self):
        """处理录音并获取AI响应"""
        print("\n[开始录音] 请说话...")
        print("说完后按空格键结束录音")
        
        # 开始录音
        audio_file = self.audio_system.record_audio(
            duration=settings.RECORD_MAX_DURATION
        )
        
        if not audio_file:
            print("录音失败")
            return
        
        # 转录音频
        print("转录音频中...")
        text = self.audio_system.transcribe_audio(audio_file)
        
        if not text:
            print("转录失败")
            return
            
        print(f"识别结果: {text}")
        
        # 处理LLM响应
        response = self.llm_callback(text)
        
        # 语音回复
        print(f"AI响应: {response}")
        self.audio_system.speak(response)
        
        print("\n按下按键继续...")


def start_keyboard_controller(llm_callback=None):
    """
    启动键盘控制器的便捷函数
    
    参数:
        llm_callback: 处理语音转文本后的回调函数
    """
    print("初始化音频系统...")
    
    # 初始化音频系统和控制器
    audio_system = AudioSystem()
    controller = KeyboardAudioController(audio_system, llm_callback)
    
    # 测试简单的语音合成
    print("测试语音合成...")
    audio_system.speak("音频系统测试开始！")
    
    # 启动热键监听
    controller.start_hotkey_listener(
        record_key=settings.RECORD_HOTKEY or '1', 
        quit_key='q'
    )
    
    print("音频系统已关闭")
    return controller 