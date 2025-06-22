import sys
import os

# 添加上级目录到路径，方便导入 core 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.audio_input import record_audio, transcribe_audio

if __name__ == "__main__":
    audio_file = record_audio(duration=5)
    text = transcribe_audio(audio_file)