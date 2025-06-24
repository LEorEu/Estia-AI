# core/intent_parser.py

"""
本模块负责解析用户意图和评估对话的重要性。
它会返回一个权重值，用于指导记忆系统。
"""

# 导入我们需要的对话引擎，因为它需要调用LLM来进行判断
from .dialogue_engine import get_llm_response
from config import settings

# 我们为LLM创建一个专门用于评估的“人格”
EVALUATOR_PERSONALITY = """
你是一个记忆权重分析师。你的任务是根据下面这段对话，以及它在最近聊天历史中的位置，为**最后一轮对话**的重要性打分。
请严格按照以下标准，只返回一个1到10之间的整数或浮点数，不要有任何其他文字解释。
评分标准：
- 10分：包含极其关键的个人信息（如姓名、生日、家庭、联系方式、重要约定）、用户的明确指令（“记住这句话”）。
- 8分：涉及生活事件、兴趣、爱好或未来计划，还有用户第一次引入一个全新的、重要的个人话题或爱好（例如“我最近开始学画画了”）。
- 6分：对一个已有话题的有意义的、深入的探讨。
- 4分：普通的、承上启下的闲聊或问答。
- 2分：重复性的、无太多信息量的日常问候（例如“你好”、“晚安”、“你吃饭了吗”）。
""".strip()

# 🔍 关键词触发列表（可扩展）
IMPORTANT_KEYWORDS = ["我的名字", "出生", "生日", "联系方式", "住在", "家庭", "电话号码", "我家", "计划", "记住", "喜欢", "讨厌", "梦想"]

def evaluate_conversation_weight(user_text: str, assistant_text: str, chat_history: list) -> float:
    """
    对最后一轮对话（user + assistant）进行重要性打分。返回权重值 1~10。
    优先使用规则，无法判断再调用 LLM。
    """

    # 规则1：最高优先级 - 用户的强制记忆指令
    IMPORTANT_KEYWORD = "记住这句话："
    if user_text.startswith(IMPORTANT_KEYWORD):
        print("💡 检测到强制记忆指令，权重设定为最高。")
        return 10.0
    
    # 规则触发：关键词
    if any(keyword in user_text for keyword in IMPORTANT_KEYWORDS):
        print("📌 命中重要关键词，权重 = 8.0")
        return 8.0
    
    # 规则触发：字数较长（信息量可能较大）
    if len(user_text.strip()) > 50:
        print("📌 对话较长，可能信息量大，权重 = 6.0")
        return 6.0

    # 未触发规则，交给LLM判断（兜底）
    print("🤖 正在调用 LLM 评估权重...")
    return _evaluate_with_llm(user_text, assistant_text, chat_history)

def _evaluate_with_llm(user_text: str, assistant_text: str, chat_history: list) -> float:
    """
    调用 LLM 进行打分。要求只返回纯数字字符串。
    """

    # 可选：截取最近 3 轮对话作为上下文参考（防止 LLM 打分脱离语境）
    recent_history = "\n".join([
        f"{msg['role']}: {msg['content']}" for msg in chat_history[-6:]
    ]) if chat_history else ""

    # 构建用于评分的 Prompt
    prompt_for_evaluation = f"""
    [历史对话片段]
    {recent_history}

    [当前对话]
    user: {user_text}
    assistant: {assistant_text}

    [你的任务]
    请根据上述内容为“当前对话”打一个 1~10 的分数（可含小数），只返回数字：
    """.strip()

    try:
        response_text = get_llm_response(
            prompt_for_evaluation,
            chat_history=[],  # 不附带主对话历史，防止人格污染
            personality=EVALUATOR_PERSONALITY
        )

        score = float(response_text.strip())
        score = max(1.0, min(10.0, score))  # 限定范围
        print(f"💡 LLM 打分结果为: {score}")
        return score

    except ValueError:
        print(f"⚠️ LLM 返回内容无法解析为数字: '{response_text}'，使用默认权重 3.0")
        return 3.0
    except Exception as e:
        print(f"❌ LLM 打分出错: {e}，使用默认权重 3.0")
        return 3.0