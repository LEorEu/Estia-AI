# core/audio/output.py

"""
本模块负责处理所有的音频输出功能，核心任务是将文字转换为语音并播放出来。
此版本使用 Pygame 作为音频播放引擎，以提高稳定性和兼容性。
"""

# -----------------------------------------------------------------------------
# 导入必要的库
# -----------------------------------------------------------------------------

import asyncio      # 导入 asyncio 库，因为 edge-tts 的核心功能是异步的。
import os           # 导入 os 模块，用于处理文件路径。
from datetime import datetime # 导入 datetime，用于生成唯一文件名。
import time         # 导入 time 模块，用于在等待音频播放时进行短暂休眠。

import edge_tts     # 导入 edge-tts 库。
import pygame       # 导入 pygame 库，用于播放音频。

from config import settings # 导入我们的配置文件。


# -----------------------------------------------------------------------------
# 初始化设置
# -----------------------------------------------------------------------------

# 定义并创建用于存放语音文件的目录
AUDIO_DIR = os.path.join("assets", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# 定义默认的发音人
VOICE = "zh-CN-XiaoyiNeural" 

# --- Pygame Mixer 初始化 ---
# pygame 的音频模块在使用前需要进行初始化。
# 这行代码也只会在程序启动加载本模块时执行一次。
pygame.mixer.init()
print("✅ Pygame Mixer 初始化完成。")


# -----------------------------------------------------------------------------
# 功能函数定义
# -----------------------------------------------------------------------------

def speak(text: str):
    """
    将输入的文本转换为语音并播放出来，这是一个同步包装函数，方便其他模块调用。

    参数:
        text (str): 需要转换成语音的文本字符串。
    """
    asyncio.run(text_to_speech(text))

def speak_stream(text_generator):
    """
    流式语音输出，边接收文本边生成语音并播放
    
    参数:
        text_generator: 文本生成器，yield文本片段
    """
    asyncio.run(text_to_speech_stream(text_generator))

async def text_to_speech_stream(text_generator):
    """
    流式文本转语音，边接收文本边生成语音并播放
    
    参数:
        text_generator: 文本生成器，yield文本片段
    """
    print("🔊 AI 开始流式语音输出...")
    
    # 音频片段队列
    audio_segments = []
    current_text = ""
    
    try:
        for text_chunk in text_generator:
            # 打印文本
            print(text_chunk, end="", flush=True)
            current_text += text_chunk
            
            # 当累积的文本达到一定长度或遇到标点符号时，生成语音
            if _should_generate_audio(current_text):
                audio_file = await _generate_audio_segment(current_text)
                if audio_file:
                    audio_segments.append(audio_file)
                    # 播放音频片段
                    await _play_audio_segment(audio_file)
                current_text = ""
        
        # 处理剩余的文本
        if current_text.strip():
            audio_file = await _generate_audio_segment(current_text)
            if audio_file:
                audio_segments.append(audio_file)
                await _play_audio_segment(audio_file)
        
        print()  # 换行
        
    except Exception as e:
        print(f"\n❌ 流式语音输出过程中发生错误: {e}")
    finally:
        # 清理临时文件
        await _cleanup_audio_segments(audio_segments)

def _should_generate_audio(text: str) -> bool:
    """
    判断是否应该生成音频片段
    
    参数:
        text: 当前累积的文本
        
    返回:
        是否应该生成音频
    """
    # 遇到句号、问号、感叹号时生成音频
    sentence_endings = ['。', '！', '？', '.', '!', '?']
    if any(ending in text for ending in sentence_endings):
        return True
    
    # 文本长度超过50个字符时生成音频
    if len(text) >= 50:
        return True
    
    return False

async def _generate_audio_segment(text: str) -> str | None:
    """
    生成音频片段
    
    参数:
        text: 要转换的文本
        
    返回:
        音频文件路径
    """
    if not text.strip():
        return None
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        audio_file = os.path.join(AUDIO_DIR, f"segment_{timestamp}.mp3")
        
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(audio_file)
        
        return audio_file
    except Exception as e:
        print(f"❌ 生成音频片段失败: {e}")
        return None

async def _play_audio_segment(audio_file: str):
    """
    播放音频片段
    
    参数:
        audio_file: 音频文件路径
    """
    try:
        # 加载音频文件
        pygame.mixer.music.load(audio_file)
        
        # 开始播放
        pygame.mixer.music.play()
        
        # 等待播放完成
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        
        # 停止并卸载
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        
    except Exception as e:
        print(f"❌ 播放音频片段失败: {e}")

async def _cleanup_audio_segments(audio_segments: list):
    """
    清理音频片段文件
    
    参数:
        audio_segments: 音频文件路径列表
    """
    for audio_file in audio_segments:
        try:
            if os.path.exists(audio_file):
                await asyncio.sleep(0.1)  # 确保文件句柄已释放
                os.remove(audio_file)
        except Exception as e:
            print(f"❌ 清理音频文件失败: {e}")

async def text_to_speech(text_to_speak: str):
    """
    将输入的文本转换为语音，并使用 Pygame 播放出来。

    参数:
        text_to_speak (str): 需要转换成语音的文本字符串。
    """
    print(f"🔊 AI 准备说: {text_to_speak}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_audio_file = os.path.join(AUDIO_DIR, f"response_{timestamp}.mp3")

    try:
        communicate = edge_tts.Communicate(text_to_speak, VOICE)
        await communicate.save(temp_audio_file)
        print(f"🎵 音频文件已生成: {temp_audio_file}")

        # --- 使用 Pygame 播放音频的核心代码 ---
        
        # 1. 加载刚刚生成的音频文件
        pygame.mixer.music.load(temp_audio_file)
        
        # 2. 开始播放音频。这个函数是"非阻塞"的，意味着代码会立刻继续往下执行，而音乐在后台播放。
        pygame.mixer.music.play()

        # 3. 创建一个循环来等待音频播放结束。
        #    pygame.mixer.music.get_busy() 会在音乐播放时返回 True，播放结束时返回 False。
        while pygame.mixer.music.get_busy():
            # 在等待时，让程序短暂休眠一下（例如0.1秒），避免这个 while 循环一直空转，过度消耗CPU资源。
            await asyncio.sleep(0.1)

    except Exception as e:
        print(f"❌ 在文本转语音或播放过程中发生错误: {e}")
        
    finally:
        # 清理工作：无论成功与否，都尝试删除临时文件。
        # 在删除前，先确保 pygame.mixer.music 已经停止，以释放对文件的占用。
        pygame.mixer.music.stop()
        # 卸载文件，进一步确保文件句柄被释放
        pygame.mixer.music.unload() 
        if os.path.exists(temp_audio_file):
            # 加一个小小的延迟，确保操作系统有时间释放文件锁
            await asyncio.sleep(0.1) 
            os.remove(temp_audio_file)
            # print(f"🗑️ 已删除临时文件: {temp_audio_file}")


# -----------------------------------------------------------------------------
# 模块独立测试区域
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    print("\n--- 正在独立测试 audio_output 模块 (使用 Pygame) ---")
    test_text = "你好，我是 Estia，很高兴认识你～"
    # 测试同步方法
    speak(test_text)
    print("\n--- 测试完成 ---")