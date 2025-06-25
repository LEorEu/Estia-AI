# core/intent_parser.py

"""
本模块负责解析用户意图和评估对话的重要性。
它会返回一个权重值，并确定适合的记忆层级，用于指导记忆系统。
"""

# 导入我们需要的对话引擎，因为它需要调用LLM来进行判断
from .dialogue_engine import get_llm_response
from config import settings

# 我们为LLM创建一个专门用于评估的"人格"
EVALUATOR_PERSONALITY = """
你是一个记忆权重分析师。你的任务是根据下面这段对话，以及它在最近聊天历史中的位置，为**最后一轮对话**的重要性打分。
请严格按照以下标准，只返回一个1到10之间的整数或浮点数，不要有任何其他文字解释。
评分标准：
- 10分：包含极其关键的个人信息（如姓名、生日、家庭、联系方式、重要约定）、用户的明确指令（"记住这句话"）。
- 8分：涉及生活事件、兴趣、爱好或未来计划，还有用户第一次引入一个全新的、重要的个人话题或爱好（例如"我最近开始学画画了"）。
- 6分：对一个已有话题的有意义的、深入的探讨。
- 4分：普通的、承上启下的闲聊或问答。
- 2分：重复性的、无太多信息量的日常问候（例如"你好"、"晚安"、"你吃饭了吗"）。
""".strip()

# 分层评估人格，判断内容应该被存储在哪个记忆层级
LAYER_EVALUATOR_PERSONALITY = """
你是一个记忆分层专家。你的任务是判断下面这段对话应该被存储在哪个记忆层级。
请根据以下标准，返回一个记忆层级名称（core/archival/long_term/short_term），不要有任何其他文字解释：

- core: 包含用户的核心个人信息（姓名、生日、家庭成员、重要联系方式等）、明确要求记住的内容、用户的重要偏好和习惯。
- archival: 包含重要生活事件、用户的背景故事、重要约定、长期计划等历史性信息。
- long_term: 包含兴趣爱好、一般性偏好、日常活动、有信息价值的讨论、可能在未来有用的知识。
- short_term: 日常问候、无明显信息价值的闲聊、当前任务相关的临时讨论、一次性问答。
""".strip()

# 🔍 关键词触发列表（可扩展）
IMPORTANT_KEYWORDS = ["我的名字", "出生", "生日", "联系方式", "住在", "家庭", "电话号码", "我家", "计划", "记住", "喜欢", "讨厌", "梦想"]

# 扩展核心记忆关键词
CORE_KEYWORDS = [
    "我的名字", "出生", "生日", "身份证", "联系方式", "住址", "家人", "记住这句话", 
    "我叫", "我住在", "我的电话", "我的邮箱", "我的密码", "我的地址", "紧急联系人",
    "我的家庭", "我的父母", "我的孩子", "我的配偶", "永远记住", "一定要记住"
]

# 扩展归档记忆关键词
ARCHIVAL_KEYWORDS = [
    "重要事件", "历史", "过去", "毕业", "结婚", "工作经历", "约定", "承诺", 
    "曾经", "那一次", "第一次", "最后一次", "重要的日子", "纪念日", "转折点",
    "工作", "职业", "学校", "大学", "旅行", "搬家", "重大决定", "成就"
]

# 长期记忆关键词
LONG_TERM_KEYWORDS = [
    "喜欢", "爱好", "兴趣", "习惯", "偏好", "讨厌", "害怕", "梦想", "目标",
    "计划", "未来", "项目", "学习", "技能", "愿望", "期待", "想要"
]

# 情感相关关键词 (情感相关内容通常更容易被记住)
EMOTIONAL_KEYWORDS = [
    "开心", "难过", "伤心", "生气", "兴奋", "失望", "惊讶", "害怕", "焦虑", 
    "紧张", "感动", "感激", "感谢", "后悔", "遗憾", "自豪", "骄傲", "委屈"
]

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

def determine_memory_layer(user_text: str, assistant_text: str, weight: float) -> str:
    """
    根据对话内容和权重确定应该存储在哪个记忆层级
    使用更复杂的规则和启发式方法进行判断
    返回: 'core', 'archival', 'long_term', 或 'short_term'
    """
    # 1. 优先考虑用户明确指示
    if "记住这句话" in user_text.lower():
        print("📌 用户明确要求记住，判定为核心记忆")
        return "core"
    
    # 2. 检查核心记忆关键词
    if any(keyword in user_text.lower() for keyword in CORE_KEYWORDS):
        print("📌 命中核心记忆关键词，判定为核心记忆")
        return "core"
    
    # 3. 检查归档记忆关键词
    if any(keyword in user_text.lower() for keyword in ARCHIVAL_KEYWORDS):
        print("📌 命中归档记忆关键词，判定为归档记忆")
        return "archival"
    
    # 4. 检查长期记忆关键词
    if any(keyword in user_text.lower() for keyword in LONG_TERM_KEYWORDS):
        print("📌 命中长期记忆关键词，判定为长期记忆")
        return "long_term"
    
    # 5. 考虑情感因素 (情感内容通常记忆更深刻)
    if any(keyword in user_text.lower() for keyword in EMOTIONAL_KEYWORDS):
        emotion_boost = 1.0  # 情感加成
        adjusted_weight = min(10.0, weight + emotion_boost)
        print(f"📌 检测到情感内容，权重从 {weight} 提升到 {adjusted_weight}")
        weight = adjusted_weight
    
    # 6. 考虑对话长度 (更长的对话通常包含更多信息)
    if len(user_text) > 100:
        length_boost = 0.5  # 长度加成
        adjusted_weight = min(10.0, weight + length_boost)
        print(f"📌 检测到较长对话，权重从 {weight} 提升到 {adjusted_weight}")
        weight = adjusted_weight
    
    # 7. 考虑助手回复长度 (助手回复详细可能表明重要内容)
    if len(assistant_text) > 150:
        response_boost = 0.5  # 回复长度加成
        adjusted_weight = min(10.0, weight + response_boost)
        print(f"📌 助手回复详细，权重从 {weight} 提升到 {adjusted_weight}")
        weight = adjusted_weight
    
    # 8. 根据最终权重决定记忆层级
    if weight >= 9.0:
        print(f"📌 最终权重 {weight}，判定为核心记忆")
        return "core"
    elif weight >= 7.0:
        print(f"📌 最终权重 {weight}，判定为归档记忆")
        return "archival"
    elif weight >= 5.0:
        print(f"📌 最终权重 {weight}，判定为长期记忆")
        return "long_term"
    else:
        print(f"📌 最终权重 {weight}，判定为短期记忆")
        return "short_term"

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
    请根据上述内容为"当前对话"打一个 1~10 的分数（可含小数），只返回数字：
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

def evaluate_memory_layer_with_llm(user_text: str, assistant_text: str, chat_history: list) -> str:
    """
    使用LLM判断对话应该被存储在哪个记忆层级
    返回: 'core', 'archival', 'long_term', 或 'short_term'
    """
    # 截取最近对话作为上下文
    recent_history = "\n".join([
        f"{msg['role']}: {msg['content']}" for msg in chat_history[-6:]
    ]) if chat_history else ""

    # 构建用于评估的 Prompt
    prompt_for_layer = f"""
    [历史对话片段]
    {recent_history}

    [当前对话]
    user: {user_text}
    assistant: {assistant_text}

    [你的任务]
    请判断这段对话应该存储在哪个记忆层级，只返回一个层级名称（core/archival/long_term/short_term）：
    """.strip()

    try:
        response_text = get_llm_response(
            prompt_for_layer,
            chat_history=[],  # 不附带主对话历史，防止人格污染
            personality=LAYER_EVALUATOR_PERSONALITY
        )

        layer = response_text.strip().lower()
        if layer in ["core", "archival", "long_term", "short_term"]:
            print(f"💡 LLM 判定记忆层级为: {layer}")
            return layer
        else:
            print(f"⚠️ LLM 返回的层级名称无法识别: '{layer}'，使用默认层级 short_term")
            return "short_term"

    except Exception as e:
        print(f"❌ LLM 层级判定出错: {e}，使用默认层级 short_term")
        return "short_term"