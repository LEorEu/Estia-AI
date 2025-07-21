# core/dialogue_engine.py

"""
本模块是 AI 的"思考"核心。（V3.0 - 多模型兼容版）
它负责接收用户的文本输入，根据配置决定调用本地或云端大模型API，
并解析返回的回复。支持多种模型提供商：本地模型、OpenAI、DeepSeek。
"""

# -----------------------------------------------------------------------------
# 导入必要的库
# -----------------------------------------------------------------------------

import os
# 预先设置环境变量来使用镜像站点
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import requests                 # 导入 requests 库，用于发送 HTTP API 请求。
import json                     # 导入 json 库，用于处理 JSON 数据格式。
from config import settings     # 从我们的配置文件中导入 settings。
import time                     # 导入 time 库，用于格式化时间戳。
import logging
from core.dialogue.personality import get_fallback_prompt, get_estia_persona

# 设置日志
log_dir = getattr(settings, 'LOG_DIR', './logs')
os.makedirs(log_dir, exist_ok=True)

# 获取logger
logger = logging.getLogger('dialogue_engine')

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 创建文件处理器
file_handler = logging.FileHandler(
    os.path.join(log_dir, 'dialogue_engine.log'),
    encoding='utf-8'  # 指定UTF-8编码
)
file_handler.setFormatter(formatter)
file_handler.setLevel(getattr(settings, 'LOG_LEVEL', 'INFO'))

# 添加处理器
logger.addHandler(file_handler)
logger.setLevel(getattr(settings, 'LOG_LEVEL', 'INFO'))

# 根据配置决定是否导入OpenAI库
if settings.MODEL_PROVIDER.lower() in ["openai", "deepseek"]:
    try:
        import openai
        logger.info(f"已加载OpenAI库，使用{settings.MODEL_PROVIDER}提供商")
    except ImportError:
        logger.error("未找到OpenAI库。请使用 'pip install openai' 安装")
        # 使用基本的requests库作为后备

try:
    import google.generativeai as genai
    from google.api_core import client_options
    logger.info("已加载 Google Generative AI SDK。")
except ImportError:
    logger.warning("未找到 Google Generative AI SDK。如果需要使用Gemini，请运行 'pip install google-generativeai'")

# -----------------------------------------------------------------------------
# 对话引擎类定义
# -----------------------------------------------------------------------------

class DialogueEngine:
    """对话引擎类，封装LLM交互功能"""
    
    def __init__(self):
        """初始化对话引擎"""
        self.logger = logger
        self.logger.info("对话引擎初始化")
        
    def generate_response(self, user_query, memory_context=None):
        """
        生成对话回复
        
        参数:
            user_query: 用户查询
            memory_context: 已构建的完整上下文（由 ContextLengthManager 构建）
        
        返回:
            生成的回复
        """
        # 直接使用已构建的完整上下文
        if memory_context:
            # memory_context 已经是 ContextLengthManager 构建的完整上下文
            # 包含：角色设定、当前会话、核心记忆、历史对话、相关记忆、重要总结、用户输入
            full_prompt = memory_context
        else:
            # 降级方案：没有上下文时使用基础模板
            full_prompt = get_fallback_prompt(user_query)

        # 直接调用LLM，不进行二次包装
        response = self._get_llm_response(full_prompt)
        return response
        
    def generate_response_stream(self, user_query, memory_context=None):
        """
        流式生成对话回复
        
        参数:
            user_query: 用户查询
            memory_context: 已构建的完整上下文（由 ContextLengthManager 构建）
        
        返回:
            生成的完整回复
        """
        # 直接使用已构建的完整上下文
        if memory_context:
            # memory_context 已经是 ContextLengthManager 构建的完整上下文
            # 包含：角色设定、当前会话、核心记忆、历史对话、相关记忆、重要总结、用户输入
            full_prompt = memory_context
        else:
            # 降级方案：没有上下文时使用基础模板
            full_prompt = get_fallback_prompt(user_query)

        # 直接调用LLM流式生成，不进行二次包装
        return self._get_llm_response_stream(full_prompt)
        
    def _get_llm_response(self, prompt, history=None, personality=""):
        """
        使用大语言模型生成回复
        
        参数:
            prompt: 提示文本（可以是完整的上下文或简单提示）
            history: 历史对话 (可选，用于兼容性)
            personality: 人格设定 (可选，用于兼容性)
        
        返回:
            模型生成的回复
        """
        if history is None:
            history = []
        
        # 构建消息数组
        messages = []
        
        # 添加人格设定 (如果有)
        if personality:
            messages.append({
                "role": "system",
                "content": personality
            })
        
        # 添加历史对话
        for entry in history:
            messages.append({
                "role": entry.get("role", "user"),
                "content": entry.get("content", "")
            })
        
        # 添加当前提示
        # 如果 prompt 已经是完整的上下文（包含角色设定等），直接使用
        # 否则作为用户消息处理
        if prompt.strip().startswith(('[系统角色设定]', get_estia_persona()[:10], '[角色设定]')) or len(prompt) > 500:
            # 这是一个完整的上下文，直接作为用户消息发送
            messages.append({
                "role": "user", 
                "content": prompt
            })
        else:
            # 这是一个简单的提示或评估请求
            messages.append({
                "role": "user",
                "content": prompt
            })
        
        # 根据提供商选择适当的API调用方法
        provider = settings.MODEL_PROVIDER.lower()
        
        # 请求LLM
        try:
            self.logger.debug(f"使用{provider}提供商发送请求，消息数: {len(messages)}")
            
            if provider == "local":
                # 使用本地LLM API
                return self._call_local_llm(messages)
            elif provider == "openai":
                # 使用OpenAI API
                return self._call_openai_api(messages)
            elif provider == "deepseek":
                # 使用DeepSeek API
                return self._call_deepseek_api(messages)
            elif provider == "gemini":
                # 使用Gemini API
                return self._call_gemini_api(messages)
            else:
                self.logger.error(f"未知的模型提供商: {provider}")
                return "错误：未知的模型提供商配置。请检查settings.py中的MODEL_PROVIDER设置。"
                
        except Exception as e:
            self.logger.error(f"LLM调用失败: {e}")
            return f"抱歉，无法完成请求。错误: {str(e)}"

    def _get_llm_response_stream(self, prompt, history=None, personality=""):
        """
        使用大语言模型流式生成回复
        
        参数:
            prompt: 提示文本（可以是完整的上下文或简单提示）
            history: 历史对话 (可选，用于兼容性)
            personality: 人格设定 (可选，用于兼容性)
        
        返回:
            模型生成的完整回复
        """
        if history is None:
            history = []
        
        # 构建消息数组
        messages = []
        
        # 添加人格设定 (如果有)
        if personality:
            messages.append({
                "role": "system",
                "content": personality
            })
        
        # 添加历史对话
        for entry in history:
            messages.append({
                "role": entry.get("role", "user"),
                "content": entry.get("content", "")
            })
        
        # 添加当前提示
        # 如果 prompt 已经是完整的上下文（包含角色设定等），直接使用
        # 否则作为用户消息处理
        if prompt.strip().startswith(('[系统角色设定]', get_estia_persona()[:10], '[角色设定]')) or len(prompt) > 500:
            # 这是一个完整的上下文，直接作为用户消息发送
            messages.append({
                "role": "user", 
                "content": prompt
            })
        else:
            # 这是一个简单的提示或评估请求
            messages.append({
                "role": "user",
                "content": prompt
            })
        
        # 根据提供商选择适当的流式API调用方法
        provider = settings.MODEL_PROVIDER.lower()
        
        # 请求LLM流式响应
        try:
            self.logger.debug(f"使用{provider}提供商发送流式请求，消息数: {len(messages)}")
            
            if provider == "local":
                # 使用本地LLM API流式调用
                return self._call_local_llm_stream(messages)
            elif provider == "openai":
                # 使用OpenAI API流式调用
                return self._call_openai_api_stream(messages)
            elif provider == "deepseek":
                # 使用DeepSeek API流式调用
                return self._call_deepseek_api_stream(messages)
            elif provider == "gemini":
                # 使用Gemini API流式调用
                return self._call_gemini_api_stream(messages)
            else:
                self.logger.error(f"未知的模型提供商: {provider}")
                return "错误：未知的模型提供商配置。请检查settings.py中的MODEL_PROVIDER设置。"
                
        except Exception as e:
            self.logger.error(f"LLM流式调用失败: {e}")
            return f"抱歉，无法完成请求。错误: {str(e)}"

    def _call_local_llm(self, messages):
        """调用本地LLM API（兼容 OpenAI 接口）"""
        try:
            request_data = {
                "model": getattr(settings, "LLM_MODEL", "local-model"),
                "messages": messages,
                "temperature": getattr(settings, "LLM_TEMPERATURE", 0.7),
                "max_tokens": getattr(settings, "LLM_MAX_NEW_TOKENS", 1024)
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(
                settings.LLM_API_URL,
                json=request_data,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            choices = result.get("choices")
            if not choices or "message" not in choices[0]:
                self.logger.warning(f"本地LLM响应结构异常: {result}")
                return "抱歉，我无法生成回复。"

            content = choices[0]["message"].get("content", "").strip()
            if not content:
                self.logger.warning("本地LLM返回了空回复")
                return "抱歉，我无法生成回复。"

            self.logger.debug(f"🤖 本地LLM原始回复: {content}")
            return content

        except requests.RequestException as e:
            self.logger.error(f"本地LLM API请求失败: {e}")
            return "抱歉，我暂时无法连接到我的大脑，请检查服务是否已启动。"

    def _call_local_llm_stream(self, messages):
        """调用本地LLM API流式接口"""
        try:
            request_data = {
                "model": getattr(settings, "LLM_MODEL", "local-model"),
                "messages": messages,
                "temperature": getattr(settings, "LLM_TEMPERATURE", 0.7),
                "max_tokens": getattr(settings, "LLM_MAX_NEW_TOKENS", 1024),
                "stream": True  # 启用流式输出
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(
                settings.LLM_API_URL,
                json=request_data,
                headers=headers,
                timeout=60,
                stream=True  # 启用流式响应
            )
            response.raise_for_status()

            full_response = ""
            print("🤖 AI: ", end="", flush=True)
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # 去掉 'data: ' 前缀
                        if data == '[DONE]':
                            break
                        try:
                            json_data = json.loads(data)
                            if 'choices' in json_data and len(json_data['choices']) > 0:
                                choice = json_data['choices'][0]
                                if 'delta' in choice and 'content' in choice['delta']:
                                    content = choice['delta']['content']
                                    if content:
                                        print(content, end="", flush=True)
                                        full_response += content
                        except json.JSONDecodeError:
                            continue
            
            print()  # 换行
            return full_response.strip()

        except requests.RequestException as e:
            self.logger.error(f"本地LLM流式API请求失败: {e}")
            return "抱歉，我暂时无法连接到我的大脑，请检查服务是否已启动。"

    def _call_openai_api(self, messages):
        """调用OpenAI API"""
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            raise ValueError("未配置OpenAI API密钥。请在settings.py中设置OPENAI_API_KEY。")
            
        import openai
        openai.api_key = settings.OPENAI_API_KEY

        # 设置自定义基础URL（如果有）
        if hasattr(settings, 'OPENAI_API_BASE') and settings.OPENAI_API_BASE:
            openai.base_url = settings.OPENAI_API_BASE  # 注意：新版是 base_url，不是 api_base

        # 调用API（新版接口）
        response = openai.chat.completions.create(
            model=getattr(settings, "OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            temperature=getattr(settings, "LLM_TEMPERATURE", 0.7),
            max_tokens=getattr(settings, "LLM_MAX_NEW_TOKENS", 1024)
        )
        
        # 提取回复文本
        content = response.choices[0].message.content
        if content is None:
            self.logger.warning("OpenAI API返回了空回复")
            return "抱歉，我无法生成回复。"
        reply = content.strip()
        return reply


    def _call_openai_api_stream(self, messages):
        """调用OpenAI API流式接口"""
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            raise ValueError("未配置OpenAI API密钥。请在settings.py中设置OPENAI_API_KEY。")
            
        import openai
        openai.api_key = settings.OPENAI_API_KEY

        # 设置自定义基础URL（如果有）
        if hasattr(settings, 'OPENAI_API_BASE') and settings.OPENAI_API_BASE:
            openai.base_url = settings.OPENAI_API_BASE

        # 调用流式API
        response = openai.chat.completions.create(
            model=getattr(settings, "OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            temperature=getattr(settings, "LLM_TEMPERATURE", 0.7),
            max_tokens=getattr(settings, "LLM_MAX_NEW_TOKENS", 1024),
            stream=True  # 启用流式输出
        )
        
        full_response = ""
        print("🤖 AI: ", end="", flush=True)
        
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        
        print()  # 换行
        return full_response.strip()

    def _call_deepseek_api(self, messages):
        """调用DeepSeek API"""
        if not hasattr(settings, 'DEEPSEEK_API_KEY') or not settings.DEEPSEEK_API_KEY:
            raise ValueError("未配置DeepSeek API密钥。请在settings.py中设置DEEPSEEK_API_KEY。")
        
        import openai
        openai.api_key = settings.DEEPSEEK_API_KEY

        if hasattr(settings, 'DEEPSEEK_API_BASE') and settings.DEEPSEEK_API_BASE:
            openai.base_url = settings.DEEPSEEK_API_BASE  # 注意新版是 base_url

        response = openai.chat.completions.create(
            model=getattr(settings, "DEEPSEEK_MODEL", "deepseek-chat"),
            messages=messages,
            temperature=getattr(settings, "LLM_TEMPERATURE", 0.7),
            max_tokens=getattr(settings, "LLM_MAX_NEW_TOKENS", 1024)
        )

        # 提取回复文本
        content = response.choices[0].message.content
        if content is None:
            self.logger.warning("DeepSeek API返回了空回复")
            return "抱歉，我无法生成回复。"
        reply = content.strip()
        return reply

    def _call_deepseek_api_stream(self, messages):
        """调用DeepSeek API流式接口"""
        if not hasattr(settings, 'DEEPSEEK_API_KEY') or not settings.DEEPSEEK_API_KEY:
            raise ValueError("未配置DeepSeek API密钥。请在settings.py中设置DEEPSEEK_API_KEY。")
        
        import openai
        openai.api_key = settings.DEEPSEEK_API_KEY

        if hasattr(settings, 'DEEPSEEK_API_BASE') and settings.DEEPSEEK_API_BASE:
            openai.base_url = settings.DEEPSEEK_API_BASE

        response = openai.chat.completions.create(
            model=getattr(settings, "DEEPSEEK_MODEL", "deepseek-chat"),
            messages=messages,
            temperature=getattr(settings, "LLM_TEMPERATURE", 0.7),
            max_tokens=getattr(settings, "LLM_MAX_NEW_TOKENS", 1024),
            stream=True  # 启用流式输出
        )

        full_response = ""
        print("🤖 AI: ", end="", flush=True)
        
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        
        print()  # 换行
        return full_response.strip()

    # ------------------ 以下是被完全修正的 Gemini 相关方法 ------------------

    def _call_gemini_api(self, messages):
        """调用Gemini API（使用官方SDK，稳定可靠）"""
        if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
            raise ValueError("未配置Gemini API密钥。请在settings.py中设置GEMINI_API_KEY。")

        try:
            # 关键步骤：处理代理配置
            api_endpoint = None
            if hasattr(settings, 'GEMINI_API_BASE') and settings.GEMINI_API_BASE:
                from urllib.parse import urlparse
                # 从完整的URL中提取主机名部分，例如 "gemini-proxy.yourdomain.com"
                api_endpoint = urlparse(settings.GEMINI_API_BASE).netloc
            
            client_opts = client_options.ClientOptions(api_endpoint=api_endpoint) if api_endpoint else None
            
            # 1. 配置API Key和客户端选项（包含代理）
            genai.configure(
                api_key=settings.GEMINI_API_KEY,
                transport="rest", # 明确使用rest传输以应用代理
                client_options=client_opts
            )
            
            # 2. 转换消息格式 (调用下面已修正的辅助函数)
            system_instruction, gemini_contents = self._convert_messages_to_gemini_format(messages)

            # 3. 设置生成参数
            generation_config = genai.types.GenerationConfig(
                temperature=getattr(settings, "LLM_TEMPERATURE", 0.7),
                max_output_tokens=getattr(settings, "LLM_MAX_NEW_TOKENS", 2048),
                top_p=0.8,
                top_k=10
            )
            
            # 4. 设置安全设置
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

            # 5. 初始化模型
            model = genai.GenerativeModel(
                model_name=getattr(settings, "GEMINI_MODEL", "gemini-2.5-pro"),
                generation_config=generation_config,
                system_instruction=system_instruction,
                safety_settings=safety_settings
            )

            self.logger.debug(f"Gemini SDK 请求内容: {gemini_contents}")
            
            # 6. 发送请求
            response = model.generate_content(gemini_contents)
            
            # 添加详细的响应调试信息
            self.logger.debug(f"Gemini API 响应对象类型: {type(response)}")
            self.logger.debug(f"Gemini API 响应属性: {dir(response)}")
            
            # 7. 解析响应 - 改进版本
            # 首先检查是否有候选响应
            candidates = getattr(response, 'candidates', [])
            if not candidates:
                self.logger.warning("Gemini API 没有返回任何候选响应")
                return "抱歉，我无法生成回复。"
            
            # 获取第一个候选响应
            candidate = candidates[0]
            candidate_finish_reason = getattr(candidate, 'finish_reason', None)
            
            # 检查finish_reason
            if candidate_finish_reason:
                self.logger.debug(f"Candidate finish reason: {candidate_finish_reason}")
                
                # 根据finish_reason处理不同情况
                if candidate_finish_reason == 1:  # STOP - 正常完成
                    pass  # 继续处理
                elif candidate_finish_reason == 2:  # MAX_TOKENS
                    self.logger.warning("Gemini API达到最大token限制")
                    return "回复内容过长，已被截断。请尝试更简洁的问题。"
                elif candidate_finish_reason == 3:  # SAFETY
                    self.logger.warning("Gemini API因安全策略阻止")
                    return "抱歉，由于安全策略限制，我无法回复这个问题。请尝试换个话题。"
                elif candidate_finish_reason == 4:  # RECITATION
                    self.logger.warning("Gemini API因版权问题阻止")
                    return "抱歉，这个问题可能涉及版权内容，我无法回复。"
                else:
                    self.logger.warning(f"未知的finish_reason: {candidate_finish_reason}")
                    return f"抱歉，我暂时无法生成回复。(原因码: {candidate_finish_reason})"
            
            # 检查响应内容
            if not response.parts:
                # 检查具体的失败原因
                finish_reason = getattr(response, 'finish_reason', 'UNKNOWN')
                prompt_feedback = getattr(response, 'prompt_feedback', {})
                
                # 添加更多调试信息
                self.logger.warning(f"Gemini API 返回了空内容")
                self.logger.warning(f"Finish Reason: {finish_reason}")
                self.logger.warning(f"Prompt Feedback: {prompt_feedback}")
                self.logger.warning(f"Response candidates: {getattr(response, 'candidates', [])}")
                self.logger.warning(f"Response text: {getattr(response, 'text', 'N/A')}")
                
                # 尝试从candidates中获取信息
                candidates = getattr(response, 'candidates', [])
                if candidates:
                    candidate = candidates[0]
                    self.logger.warning(f"First candidate: {candidate}")
                    candidate_finish_reason = getattr(candidate, 'finish_reason', 'UNKNOWN')
                    self.logger.warning(f"Candidate finish reason: {candidate_finish_reason}")
                
                # 根据具体原因返回不同的错误信息
                if finish_reason == 'SAFETY':
                    return "抱歉，由于安全策略限制，我无法回复这个问题。请尝试换个话题。"
                elif finish_reason == 'MAX_TOKENS':
                    return "回复内容过长，已被截断。请尝试更简洁的问题。"
                elif finish_reason == 'RECITATION':
                    return "抱歉，这个问题可能涉及版权内容，我无法回复。"
                else:
                    return f"抱歉，我暂时无法生成回复。(原因: {finish_reason})"
                
            # 安全地获取响应文本
            try:
                reply = response.text.strip()
                if not reply:
                    self.logger.warning("Gemini API返回了空文本")
                    return "抱歉，我无法生成有效的回复。"
                    
                self.logger.debug(f"🤖 Gemini API 回复: {reply}")
                return reply
            except Exception as text_error:
                self.logger.error(f"获取响应文本时出错: {text_error}")
                return "抱歉，处理回复时出现错误。"

        except Exception as e:
            self.logger.error(f"Gemini SDK 调用异常: {e}")
            return f"抱歉，处理Gemini请求时出现错误: {str(e)}"

    def _call_gemini_api_stream(self, messages):
        """
        调用Gemini API并以流式返回响应（使用官方SDK）。
        这是一个生成器函数，会逐块 yield 响应文本。
        """
        if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
            # 对于生成器，我们可以yield一个错误信息而不是raise异常
            # 这样调用方可以在UI上显示错误
            yield "[ERROR] 未配置Gemini API密钥。请在settings.py中设置GEMINI_API_KEY。"
            return # 必须return来结束生成器

        # 您现有的所有配置和初始化代码都可以复用
        try:
            # 关键步骤：处理代理配置
            api_endpoint = None
            if hasattr(settings, 'GEMINI_API_BASE') and settings.GEMINI_API_BASE:
                from urllib.parse import urlparse
                api_endpoint = urlparse(settings.GEMINI_API_BASE).netloc
            
            client_opts = client_options.ClientOptions(api_endpoint=api_endpoint) if api_endpoint else None
            
            # 1. 配置API Key和客户端选项（包含代理）
            genai.configure(
                api_key=settings.GEMINI_API_KEY,
                transport="rest", # 明确使用rest传输以应用代理
                client_options=client_opts
            )
            
            # 2. 转换消息格式
            system_instruction, gemini_contents = self._convert_messages_to_gemini_format(messages)

            # 3. 设置生成参数
            generation_config = genai.types.GenerationConfig(
                temperature=getattr(settings, "LLM_TEMPERATURE", 0.7),
                max_output_tokens=getattr(settings, "LLM_MAX_NEW_TOKENS", 2048),
                top_p=0.8,
                top_k=10
            )
            
            # 4. 设置安全设置
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

            # 5. 初始化模型
            model = genai.GenerativeModel(
                model_name=getattr(settings, "GEMINI_MODEL", "gemini-1.5-pro-latest"),
                generation_config=generation_config,
                system_instruction=system_instruction,
                safety_settings=safety_settings
            )

            self.logger.debug(f"Gemini SDK [STREAM] 请求内容: {gemini_contents}")
            
            # 6. 发送流式请求 (核心变化)
            response_stream = model.generate_content(
                gemini_contents,
                stream=True  # <--- ✨ 开启流式模式！
            )
            
            # 7. 循环处理数据流并 yield 每一块文本 (核心变化)
            for chunk in response_stream:
                # 安全地获取文本块，防止因奇怪的响应（如只有finish_reason）而报错
                if chunk.text:
                    yield chunk.text # <--- ✨ 使用yield而不是return

        except Exception as e:
            self.logger.error(f"Gemini SDK [STREAM] 调用异常: {e}")
            # 在生成器中，通过yield返回错误信息是更好的方式
            yield f"\n[ERROR] 抱歉，处理Gemini流式请求时出现错误: {str(e)}"
    
    def _convert_messages_to_gemini_format(self, messages):
        """
        [已修正] 将OpenAI格式的消息列表转换为Gemini SDK所需的格式。
        - 提取 system 指令。
        - 确保 user/model 角色交替。
        - 合并连续的同角色消息。
        """
        system_instruction = None
        gemini_contents = []
        
        if not messages:
            return None, []

        # 1. 提取 system 指令 (通常是列表中的第一条)
        if messages[0]['role'] == 'system':
            system_instruction = messages[0]['content']
            messages = messages[1:]

        if not messages:
            return system_instruction, []

        # 2. 合并连续的同角色消息，避免API报错
        merged_messages = []
        current_role = messages[0]['role']
        current_content = [messages[0]['content']]

        for msg in messages[1:]:
            if msg['role'] == current_role:
                current_content.append(msg['content'])
            else:
                merged_messages.append({'role': current_role, 'content': "\n".join(current_content)})
                current_role = msg['role']
                current_content = [msg['content']]
        merged_messages.append({'role': current_role, 'content': "\n".join(current_content)})
        
        # 3. 转换为Gemini格式，并确保角色交替
        for msg in merged_messages:
            # 角色映射: assistant -> model
            role = 'model' if msg['role'] == 'assistant' else 'user'
            
            # 保证历史记录以 user 开头，且 user/model 交替
            if role == 'user' or (role == 'model' and len(gemini_contents) > 0 and gemini_contents[-1]['role'] == 'user'):
                gemini_contents.append({'role': role, 'parts': [msg['content']]})
            else:
                # 如果出现不规范的开头(如model)或连续的model角色，则记录并跳过，以防API报错
                self.logger.warning(f"丢弃了格式不正确的对话历史部分: {msg}")

        return system_instruction, gemini_contents


# -----------------------------------------------------------------------------
# 兼容性导出函数 (用于向后兼容)
# -----------------------------------------------------------------------------

def get_llm_response(prompt, history=None, personality=""):
    """
    使用大语言模型生成回复 (兼容旧版)
    """
    engine = DialogueEngine()
    return engine._get_llm_response(prompt, history, personality)

def generate_response(user_query, memory_context, personality=""):
    """
    生成回复，考虑记忆上下文和人格 (兼容旧版)
    """
    engine = DialogueEngine()
    return engine.generate_response(user_query, memory_context, personality)

def retrieve_memories(query, limit=5, memory_manager=None):
    """
    从记忆管理器中检索相关记忆
    
    参数:
        query: 查询文本
        limit: 最大返回数量
        memory_manager: 记忆管理器实例
    
    返回:
        格式化的记忆文本
    """
    if not memory_manager:
        return "没有可用的记忆。"
    
    try:
        # 从记忆管理器检索记忆
        results = memory_manager.retrieve_memory(
            query, 
            limit=limit,
            parallel=True,
            include_associations=True,
            check_conflicts=True
        )
        
        if not results:
            return "没有找到相关记忆。"
        
        # 格式化记忆
        formatted_memories = []
        
        for memory in results:
            role = memory.get("role", "system")
            content = memory.get("content", "")
            timestamp = memory.get("timestamp", "")
            
            # 格式化时间
            if isinstance(timestamp, (int, float)):
                import datetime
                timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
            
            # 处理特殊标记
            prefix = ""
            if memory.get("is_associated", False):
                prefix = "[关联记忆] "
            elif memory.get("is_summary", False):
                prefix = "[记忆摘要] "
            elif memory.get("status") == "superseded":
                prefix = "[已更新的信息] "
            
            # 添加上下文信息
            context = ""
            if "context" in memory:
                context = f" (备注: {memory['context']})"
            
            formatted_memories.append(f"{prefix}[{timestamp}] {role}: {content}{context}")
        
        # 添加一个简短的介绍
        header = "系统记忆:"
        formatted_text = header + "\n" + "\n".join(formatted_memories)
        
        return formatted_text
        
    except Exception as e:
        logger.error(f"记忆检索失败: {e}")
        return "记忆检索过程中出现错误。"