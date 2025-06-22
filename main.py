# main.py (V2.0 - 交互控制版)

"""
AI 助手的总入口程序。
此版本引入了按键触发机制，用户可以控制每一轮对话的开始，交互体验更自然。
"""

import asyncio
import time
import sys # 导入sys，用于退出程序

# 从 core 包中导入我们已经写好的所有功能函数
from core.audio_input import record_audio, transcribe_audio
from core.dialogue_engine import get_llm_response
from core.audio_output import text_to_speech
from core.personality import PERSONAS
from config import settings

async def main_loop():
    """
    程序的主循环，现在由用户通过按键来驱动。
    """
    print("AI 助手已启动！")

    # --- 从配置文件加载选定的人格 ---
    # 使用 .get() 方法安全地获取人格，如果名字写错了，就使用默认的"default"人格
    active_persona_prompt = PERSONAS.get(settings.ACTIVE_PERSONA, PERSONAS["default"])
    print(f"✅ AI人格已设定为: {settings.ACTIVE_PERSONA}")

    # --- 初始化“记忆笔记本” ---
    # 定义一个空列表，用于存储对话历史
    chat_history = []
    # 定义最大记忆轮数，防止上下文无限增长导致溢出。5轮是一个比较合理的初始值。
    MAX_HISTORY_TURNS = 5
    
    # 定义一个变量来控制是否是第一次运行，第一次运行时不需要提示
    is_first_run = True

    while True:
        try:
            # --- 新增的交互控制部分 ---
            if is_first_run:
                # 如果是第一次运行，直接提示开始录音
                input("\n准备好了吗？请按回车键开始录音...")
                is_first_run = False
            else:
                # 在后续的循环中，提示用户进行下一次对话
                input("\n...对话暂停，AI正在待命... 请按回车键开始下一次录音，或按 Ctrl+C 退出...")

            # --- 第一步：聆听 (Ears) ---
            recorded_file = record_audio(duration=7)
            
            user_text = transcribe_audio(recorded_file)

            if not user_text or user_text.strip() == "":
                print("⚠️ 未识别到有效语音，请重试。")
                # 使用 continue 会直接跳到下一次循环的 input() 提示，让用户重新开始
                continue

            # --- 第二步：思考 (核心改动) ---
            # 将用户的文字 和 历史记录 一同发送给对话引擎
            ai_text = get_llm_response(user_text, chat_history, active_persona_prompt)

            # --- 新增：核心改动 2: 将本轮对话记录到“短期记忆”中 ---
            # 将用户的提问添加到历史记录
            chat_history.append({"role": "user", "content": user_text})
            # 将AI的回答也添加到历史记录
            chat_history.append({"role": "assistant", "content": ai_text})

            # --- 新增：核心改动 3: 控制记忆长度（“滑动窗口”技术） ---
            # 如果对话轮数超过了我们设定的上限，就删除最早的一轮对话（一轮包含用户和AI的两条消息）
            if len(chat_history) > MAX_HISTORY_TURNS * 2:
                # 使用列表切片，只保留最后 MAX_HISTORY_TURNS * 2 条记录
                chat_history = chat_history[-MAX_HISTORY_TURNS*2:]
                print(f"（记忆已清理，仅保留最近 {MAX_HISTORY_TURNS} 轮对话。）")

            # --- 第三步：回应 (Mouth) ---
            await text_to_speech(ai_text)
            
            # 打印分割线，让界面更清晰
            print("\n" + "="*50) 

        except KeyboardInterrupt:
            # 允许用户通过按 Ctrl+C 来优雅地退出程序
            print("\n👋 检测到用户中断，AI 助手正在关闭...再会！")
            # 使用 sys.exit() 来干净地终止程序
            sys.exit(0)
        except Exception as e:
            # 捕获其他可能的未知错误，打印后继续等待用户的下一次指令
            print(f"🚫 主循环发生未知错误: {e}")
            time.sleep(2)


if __name__ == "__main__":
    asyncio.run(main_loop())