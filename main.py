# main.py (V3.1 - 最终稳定版)

"""
AI 助手的总入口程序。
此版本采用异步非阻塞方式处理记忆的评估和存储，
并修复了数据库连接和线程安全问题，达到了生产就绪状态。
"""

import asyncio
import time
import sys

from core.audio_input import record_audio, transcribe_audio
from core.dialogue_engine import get_llm_response
from core.audio_output import text_to_speech
from core.personality import PERSONAS
from core.retriever import MemoryRetriever
from core.database import MemoryDatabase         # 导入数据库模块
from core.score_async_executor import score_and_store, executor
from config import settings

async def main_loop():
    print("AI 助手已启动！")

    # --- 初始化所有核心组件 ---
    active_persona_prompt = PERSONAS.get(settings.ACTIVE_PERSONA, PERSONAS["default"])
    print(f"✅ AI人格已设定为: {settings.ACTIVE_PERSONA}")

    retriever = MemoryRetriever()
    print("✅ 记忆检索器已就位。")

    # --- 修正 1: 在这里初始化数据库连接 ---
    db = MemoryDatabase()
    print("✅ 记忆数据库已连接。")
    
    chat_history = []
    MAX_HISTORY_TURNS = 5
    is_first_run = True
    
    while True:
        try:
            if is_first_run:
                input("\n准备好了吗？请按回车键开始录音...")
                is_first_run = False
            else:
                input("\n...对话暂停，AI正在待命... 请按回车键开始下一次录音，或按 Ctrl+C 退出...")

            # --- 步骤 1: 聆听 ---
            recorded_file = record_audio(duration=7)
            user_text = transcribe_audio(recorded_file)

            if not user_text or user_text.strip() == "":
                print("⚠️ 未识别到有效语音，请重试。")
                continue

            # --- 步骤 2: 思考前准备（记忆检索） ---
            print("🔍 正在检索相关长期记忆...")
            retrieved_memories = retriever.search(user_text, k=3)
            if retrieved_memories:
                print("💡 已找到相关记忆！")

            # --- 步骤 3: 思考（生成回复） ---
            ai_text = get_llm_response(user_text, chat_history, retrieved_memories, active_persona_prompt)
            
            # --- 步骤 4: 回应 (立刻！) ---
            await text_to_speech(ai_text)
            
            # --- 步骤 5: “事后复盘”（异步执行，不影响用户）---
            print("📤 正在后台评估并存储本轮记忆...")
            # --- 修正 2: 传递 chat_history 的一个副本 (.copy()) 给后台线程 ---
            score_and_store(user_text, ai_text, chat_history.copy(), db)

            # --- 步骤 6: 更新用于下一轮对话的短期记忆 ---
            chat_history.append({"role": "user", "content": user_text})
            chat_history.append({"role": "assistant", "content": ai_text})

            # 控制短期记忆长度 (滑动窗口)
            if len(chat_history) > MAX_HISTORY_TURNS * 2:
                chat_history = chat_history[-(MAX_HISTORY_TURNS*2):]
                print(f"（短期记忆已清理，仅保留最近 {MAX_HISTORY_TURNS} 轮对话。）")

            print("\n" + "="*50) 

        except KeyboardInterrupt:
            print("\n👋 检测到用户中断，AI 助手正在关闭...再会！")
            # --- 修正 3: 在退出时，也关闭数据库连接 ---
            db.close()
            executor.shutdown(wait=False)
            sys.exit(0)
        except Exception as e:
            print(f"🚫 主循环发生未知错误: {e}")
            time.sleep(2)


if __name__ == "__main__":
    asyncio.run(main_loop())