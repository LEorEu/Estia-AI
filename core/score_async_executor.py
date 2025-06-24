# core/score_async_executor.py
"""
评分异步执行器：score_async_executor.py
负责在后台异步评估对话权重（规则优先，LLM兜底）并写入数据库。
"""

import threading
from core.intent_parser import evaluate_conversation_weight
from core.database import MemoryDatabase

# ✅ 创建一个线程池（最大并发任务数，可自调）
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=2)

def score_and_store(user_text: str, ai_text: str, chat_history: list, db: MemoryDatabase):
    """
    在后台异步执行的评分和入库逻辑（由主程序调用）
    """
    def task():
        try:
            print("📊 正在后台评分...")
            weight = evaluate_conversation_weight(user_text, ai_text, chat_history)
            db.add_entry("user", user_text, initial_weight=weight)
            db.add_entry("assistant", ai_text, initial_weight=weight)
            print(f"✅ 评分完成，权重为 {weight:.2f}，已保存入记忆数据库。")
        except Exception as e:
            print(f"❌ 后台评分失败: {e}")

    # 提交任务给线程池执行，不阻塞主线程
    executor.submit(task)


# ✅ 示例使用（放在主循环中调用）：
# from core.score_async_executor import score_and_store
# score_and_store(user_text, ai_text, chat_history, db)

# ✅ 推荐在程序退出时关闭线程池：
# executor.shutdown(wait=False)  # 可放在主程序 exit 逻辑中
