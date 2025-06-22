# scripts/test_tts.py

"""
这是一个用于专门测试文本转语音（TTS）功能的脚本。
它可以让你从命令行直接指定希望 AI 说出的句子，而无需修改任何核心代码。
这在开发和调试过程中非常有用。
"""

import sys      # 导入 sys 模块，用于访问命令行参数。
import os       # 导入 os 模块，用于处理文件路径。
import asyncio  # 导入 asyncio，因为我们的 TTS 函数是异步的。

# --- 关键步骤：将项目根目录添加到 Python 的搜索路径中 ---
# 这样做可以确保无论我们在哪个目录下运行此脚本，
# 它都能正确地找到 core, config 等项目模块。
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 从我们的核心模块中导入 text_to_speech 函数
from core.audio_output import text_to_speech

# 脚本的主执行逻辑
if __name__ == "__main__":
    # --- 从命令行获取要说的文本 ---
    # sys.argv 是一个列表，包含了所有命令行参数。
    # sys.argv[0] 是脚本自己的名字 (test_tts.py)
    # sys.argv[1] 是第一个参数，sys.argv[2] 是第二个，以此类推。
    
    # 我们检查用户是否在命令后面提供了要说的文本
    if len(sys.argv) > 1:
        # 如果提供了（列表长度大于1），我们就将第一个参数作为要说的内容。
        text_to_say = sys.argv[1]
    else:
        # 如果用户没有提供任何参数，我们就使用一个默认的句子。
        text_to_say = "你没有告诉我该说什么，所以我就说这句默认的话来测试一下。"

    # 打印将要执行的任务
    print(f"▶️  准备执行TTS测试，内容为：'{text_to_say}'")

    # 使用 asyncio.run() 来执行我们的异步 TTS 函数
    try:
        asyncio.run(text_to_speech(text_to_say))
        print("✅ 测试成功完成。")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")