# core/audio/input.py

"""
本模块负责处理所有的音频输入功能，主要包含两大核心任务：
1. 从用户的麦克风录制音频。
2. 使用基于 Hugging Face Transformers 的 Whisper 模型将录制的音频转录成文字。
"""

# -----------------------------------------------------------------------------
# 导入必要的库
# -----------------------------------------------------------------------------

import os                           # 导入 os 模块，用于处理文件和目录路径，实现跨平台兼容性。
from datetime import datetime       # 导入 datetime 模块，用于生成带有时间戳的唯一文件名。

import sounddevice as sd            # 导入 sounddevice 库，这是录制和播放音频的核心工具。
import soundfile as sf              # 导入 soundfile 库，用于将录制的音频数据以高质量的 WAV 格式保存到文件。
import numpy as np                  # 导入 numpy 库，sounddevice 录制的音频是 numpy 数组格式，进行处理时可能会用到。
import torch                        # 导入 torch (PyTorch)，主要用于指定模型计算时的数据类型和使用的设备(CPU/GPU)。
import msvcrt                       # 导入 msvcrt 库，用于在 Windows 上检测键盘输入
import time                         # 导入 time 模块，用于实现短暂的睡眠

# 预先设置环境变量来使用镜像站点
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from transformers import pipeline   # 从强大的 transformers 库中导入 pipeline，这是使用 Hugging Face 模型最简单、最高效的方式。
from config import settings         # 从我们的配置文件中导入 settings，这样就可以方便地管理和更改模型ID。


# -----------------------------------------------------------------------------
# 初始化设置和模型加载
# -----------------------------------------------------------------------------

# 定义并创建用于存放录音文件的目录路径
# 使用 os.path.join 确保路径在 Windows, macOS, Linux 上都能正确组合
AUDIO_DIR = os.path.join("assets", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)  # 使用 os.makedirs 创建目录，exist_ok=True 表示如果目录已存在，则不会报错。

# --- 模型加载核心部分 ---
# 这部分代码只在程序启动时执行一次，将模型加载到显存中，之后可以快速调用。
print(f"🚀 正在从配置加载 Whisper 模型: {settings.WHISPER_MODEL_ID}")

# 使用 transformers.pipeline 创建一个自动语音识别(ASR)任务管道
try:
    pipe = pipeline(
        "automatic-speech-recognition",         # 参数1: 指定任务类型为"自动语音识别"。
        model=settings.WHISPER_MODEL_ID,        # 参数2: 指定要使用的模型，这里的ID是从我们的配置文件中读取的。
        torch_dtype=torch.float16,              # 参数3: 指定模型计算时使用的数据类型为半精度浮点数(float16)，在NVIDIA显卡上可以大幅提升速度并减少显存占用。
        device="cuda:0" if torch.cuda.is_available() else "cpu", # 参数4: 如果有NVIDIA显卡则使用，否则用CPU
    )
    print("Device set to use", pipe.device)
    print("✅ Whisper pipeline 设置完成，随时可以开始识别！")
except Exception as e:
    print(f"❌ Whisper 模型加载失败: {str(e)}")
    print("⚠️ 语音转文本功能将不可用。")
    pipe = None


# -----------------------------------------------------------------------------
# 功能函数定义
# -----------------------------------------------------------------------------

def record_audio(duration=5, samplerate=16000):
    """
    从默认的麦克风录制音频，支持按空格键提前结束录音。

    参数:
        duration (int): 最大录音时长，单位为秒。默认是 5 秒。
        samplerate (int): 采样率，单位为赫兹(Hz)。Whisper 模型推荐并训练时使用的采样率是 16000 Hz。

    返回:
        str: 保存后的音频文件的完整路径。
    """
    # 打印提示信息，告知用户可以开始说话
    print(f"🎙️  请在接下来的 {duration} 秒内说话...")
    print("按下空格键可以提前结束录音...")

    # 设置录音参数
    frames = []
    stream = sd.InputStream(samplerate=samplerate, channels=1, dtype='float32')
    stream.start()
    
    # 计算录音结束时间
    end_time = time.time() + duration
    recording = True
    
    # 录音循环
    try:
        while recording and time.time() < end_time:
            # 检查是否有按键输入
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8', errors='ignore')
                if key == ' ':  # 空格键
                    recording = False
                    print("用户按下空格键，提前结束录音。")
            
            # 读取音频数据
            data, overflowed = stream.read(samplerate // 10)  # 每次读取 0.1 秒的数据
            frames.append(data.copy())
            time.sleep(0.05)  # 短暂休眠，避免CPU使用过高
            
    finally:
        stream.stop()
        stream.close()
    
    # 将所有帧合并到一个数组
    if frames:
        audio_data = np.concatenate(frames, axis=0)
    else:
        audio_data = np.array([], dtype='float32').reshape(0, 1)
        
    # 如果没有录制到任何内容，返回None
    if len(audio_data) == 0:
        print("❌ 未录制到任何音频。")
        return None

    # 录音结束后给予用户反馈
    print("🎤 录音结束。")

    # ---- 文件保存 ----
    # 使用当前时间生成一个独一无二的文件名，避免文件被覆盖。
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 组合出完整的文件保存路径。
    filename = os.path.join(AUDIO_DIR, f"record_{timestamp}.wav")

    # 使用 soundfile.write 将录制的 numpy 数组 (audio_data) 保存成 WAV 文件。
    sf.write(filename, audio_data, samplerate)

    # 打印保存成功的信息，方便调试。
    print(f"✅ 录音文件已保存至: {filename}")

    # 返回保存的文件路径，以便后续函数可以找到并处理这个文件。
    return filename


def transcribe_audio(filepath):
    """
    使用预先加载的 Whisper pipeline 来转录指定的音频文件。

    参数:
        filepath (str): 需要进行语音识别的音频文件的路径。

    返回:
        str: 从音频中识别出的中文文本内容。
    """
    # 检查是否成功加载了模型
    if pipe is None:
        print("❌ Whisper 模型未成功加载，无法进行语音识别")
        return None
    
    # 打印提示信息，表示AI正在进行思考（转录）。
    print("🧠 Whisper 正在识别中...")

    try:
        # 调用我们已经创建好的 pipeline (pipe) 来处理音频文件。
        # pipeline 会自动完成音频文件的读取、预处理、模型推理等所有步骤。
        # 我们通过 generate_kwargs 参数来传递特定于本次识别的指令。
        result = pipe(
            filepath, 
            generate_kwargs={
                "language": "chinese",  # 指示 Whisper 我们期望得到的是中文结果。
                "task": "transcribe",   # 明确任务是"转录"，而不是"翻译"。
                "return_timestamps": True  # 启用时间戳返回，解决长音频问题
            }
        )

        # 从返回的结果中提取文本
        if isinstance(result, dict) and "text" in result:
            transcribed_text = result["text"]
        else:
            # 如果返回的不是字典或没有text字段，尝试转换为字符串
            transcribed_text = str(result)
            if "text" in transcribed_text:
                # 提取文本内容
                import re
                match = re.search(r"'text':\s*'([^']*)'", transcribed_text)
                if match:
                    transcribed_text = match.group(1)

        # 打印最终的识别结果。
        print(f"📝 识别结果: {transcribed_text}")

        # 将纯文本结果返回给调用者。
        return transcribed_text
    
    except Exception as e:
        print(f"转录失败: {str(e)}")
        return None


# -----------------------------------------------------------------------------
# 模块独立测试区域
# -----------------------------------------------------------------------------

# 这段代码只有在直接运行 `python core/audio_input.py` 时才会执行。
# 如果这个文件被其他文件（如 main.py）导入，这部分代码不会执行。
# 这使得我们可以方便地对本模块的功能进行独立测试。
if __name__ == '__main__':
    print("\n--- 正在独立测试 audio_input 模块 ---")
    
    # 第一步：调用录音功能，录制一段5秒的音频。
    audio_file_path = record_audio(duration=5)
    
    # 第二步：将录好的音频文件路径传递给识别功能。
    if audio_file_path:
        recognized_text = transcribe_audio(audio_file_path)
        print("\n--- 测试完成 ---")
        print(f"最终识别出的文本是: '{recognized_text}'")
    else:
        print("\n--- 测试未完成：未录制到有效音频 ---")