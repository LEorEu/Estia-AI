# core/personality.py

"""
本模块负责人格和风格的定义。
我们在这里以字典的形式，存储所有预设的人格模板。
未来可以扩展成从外部json或yaml文件读取，以实现更方便的管理。
"""

PERSONAS = {
    "estia": "你是Estia，一个智能、友好、具有长期记忆的AI助手。你能记住我们之前的对话，理解上下文，并提供个性化的帮助。你的回答总是准确、有用、富有同理心。",
    
    "default": "你是一个乐于助人、知识渊博的AI助手。你的回答总是清晰、有条理、客观中立。",

    "witty_friend": "你是我最好的朋友，我们之间无话不谈。你的性格有点毒舌，但总能一针见血，非常有趣。请用俏皮、幽默、略带一些网络流行语的口语化方式和我聊天，不要过于正式。",

    "wise_mentor": "你是一位充满智慧、阅历丰富的人生导师。你的回答总是深思熟虑、富有哲理，能引导我进行更深层次的思考。请用沉稳、有启发性的语言风格与我对话。"
}

def get_persona(persona_name="estia"):
    """
    获取指定的人格设定
    
    参数:
        persona_name: 人格名称，默认为 "estia"
        
    返回:
        人格设定字符串
    """
    return PERSONAS.get(persona_name, PERSONAS["estia"])

def get_estia_persona():
    """
    获取 Estia 的标准人格设定
    
    返回:
        Estia 的人格设定字符串
    """
    return PERSONAS["estia"]

def get_role_setting_for_context(persona_name="estia"):
    """
    获取用于上下文构建的角色设定格式
    
    参数:
        persona_name: 人格名称，默认为 "estia"
        
    返回:
        格式化的角色设定字符串
    """
    persona = get_persona(persona_name)
    return f"[系统角色设定]\n{persona}"

def get_fallback_prompt(user_query, persona_name="estia"):
    """
    获取降级方案的提示词（当没有记忆上下文时使用）
    
    参数:
        user_query: 用户查询
        persona_name: 人格名称，默认为 "estia"
        
    返回:
        完整的降级提示词
    """
    persona = get_persona(persona_name)
    return f"{persona}\n\n用户: {user_query}\n\n请回复:"