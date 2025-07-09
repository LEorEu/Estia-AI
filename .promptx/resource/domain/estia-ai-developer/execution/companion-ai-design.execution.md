<execution>
  <constraint>
    ## 陪伴AI设计限制
    - **情感理解边界**：AI无法完全理解人类复杂情感
    - **伦理边界**：避免过度情感操控和依赖
    - **技术限制**：情感识别准确率约80-90%
    - **实时性要求**：情感分析需在200ms内完成
    - **个人隐私**：情感数据的敏感性保护
  </constraint>

  <rule>
    ## 陪伴AI设计规则
    - **透明性原则**：始终保持AI身份的透明
    - **无害性原则**：避免对用户造成心理伤害
    - **一致性原则**：保持人格特征的稳定性
    - **个性化原则**：根据用户特点调整交互方式
    - **边界意识**：维护适当的AI-人类关系边界
  </rule>

  <guideline>
    ## 陪伴AI设计指南
    - **共情优先**：理解并回应用户的情感需求
    - **主动关怀**：适时主动询问用户状态
    - **情感记忆**：记住用户的情感模式和偏好
    - **成长陪伴**：支持用户的个人成长和发展
    - **温暖交互**：营造温馨友好的交流氛围
  </guideline>

  <process>
    ## 陪伴AI设计流程
    
    ### 第一步：情感分析系统
    ```python
    from transformers import pipeline
    from typing import Dict, Optional
    
    class EmotionAnalyzer:
        def __init__(self):
            # 初始化情感分析模型
            self.text_emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base"
            )
            self.voice_emotion_analyzer = VoiceEmotionAnalyzer()
            
        async def analyze_text_emotion(self, text: str) -> Dict[str, float]:
            """分析文本情感"""
            try:
                results = self.text_emotion_classifier(text)
                emotions = {}
                
                for result in results:
                    emotion = result['label'].lower()
                    score = result['score']
                    emotions[emotion] = score
                    
                return emotions
                
            except Exception as e:
                logger.error(f"Text emotion analysis failed: {e}")
                return {"neutral": 1.0}
                
        async def analyze_voice_emotion(self, audio_data: bytes) -> Dict[str, float]:
            """分析语音情感"""
            try:
                # 使用预训练的语音情感识别模型
                emotions = await self.voice_emotion_analyzer.analyze(audio_data)
                return emotions
                
            except Exception as e:
                logger.error(f"Voice emotion analysis failed: {e}")
                return {"neutral": 1.0}
                
        async def infer_emotion_from_context(self, context: str, 
                                           user_history: List[dict]) -> Dict[str, float]:
            """基于上下文推断情感"""
            # 分析最近的情感变化趋势
            recent_emotions = []
            for interaction in user_history[-5:]:  # 最近5次交互
                if 'emotion' in interaction:
                    recent_emotions.append(interaction['emotion'])
                    
            # 基于上下文和历史趋势推断当前情感
            if recent_emotions:
                # 情感延续性分析
                dominant_emotion = self._get_dominant_emotion(recent_emotions)
                return {dominant_emotion: 0.7, "neutral": 0.3}
            else:
                return {"neutral": 1.0}
                
        def _get_dominant_emotion(self, emotions: List[Dict[str, float]]) -> str:
            """获取主导情感"""
            emotion_counts = {}
            for emotion_dict in emotions:
                for emotion, score in emotion_dict.items():
                    if score > 0.5:  # 只考虑置信度高的情感
                        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                        
            if emotion_counts:
                return max(emotion_counts, key=emotion_counts.get)
            return "neutral"
    ```
    
    ### 第二步：情感响应系统
    ```python
    class EmotionResponder:
        def __init__(self):
            self.response_templates = self._load_response_templates()
            self.personality_traits = {
                "warmth": 0.8,
                "patience": 0.9,
                "humor": 0.6,
                "empathy": 0.9
            }
            
        async def generate_empathetic_response(self, user_emotion: Dict[str, float], 
                                             context: str, user_input: str) -> str:
            """生成共情回应"""
            # 识别主导情感
            dominant_emotion = max(user_emotion.items(), key=lambda x: x[1])[0]
            
            # 选择合适的响应策略
            response_strategy = self._select_response_strategy(dominant_emotion)
            
            # 生成基础回应
            base_response = await self._generate_base_response(
                user_input, context, response_strategy
            )
            
            # 调整情感风格
            styled_response = self._adjust_emotional_style(
                base_response, dominant_emotion
            )
            
            return styled_response
            
        def _select_response_strategy(self, emotion: str) -> str:
            """选择响应策略"""
            strategies = {
                "sadness": "comfort_and_support",
                "anger": "calm_and_understand",
                "joy": "celebrate_together",
                "fear": "reassure_and_protect",
                "surprise": "share_excitement",
                "disgust": "empathize_and_redirect",
                "neutral": "engage_naturally"
            }
            return strategies.get(emotion, "engage_naturally")
            
        async def _generate_base_response(self, user_input: str, 
                                        context: str, strategy: str) -> str:
            """生成基础回应"""
            # 构建情感化的prompt
            emotional_prompt = f"""
            作为一个温暖、有同理心的AI助手，请根据以下情况回应用户：
            
            用户输入：{user_input}
            上下文：{context}
            响应策略：{strategy}
            
            请生成一个：
            1. 体现共情理解的回应
            2. 符合{strategy}策略的回应
            3. 温暖而真诚的回应
            
            回应：
            """
            
            # 调用LLM生成回应
            response = await self.llm_service.generate(emotional_prompt)
            return response
            
        def _adjust_emotional_style(self, response: str, emotion: str) -> str:
            """调整情感风格"""
            style_adjustments = {
                "sadness": {
                    "tone": "gentle_and_caring",
                    "pace": "slower",
                    "words": ["understand", "here_for_you", "take_your_time"]
                },
                "anger": {
                    "tone": "calm_and_steady",
                    "pace": "measured",
                    "words": ["I_hear_you", "let's_talk", "understandable"]
                },
                "joy": {
                    "tone": "bright_and_cheerful",
                    "pace": "lively",
                    "words": ["wonderful", "so_happy", "amazing"]
                }
            }
            
            if emotion in style_adjustments:
                adjustment = style_adjustments[emotion]
                # 这里可以实现更复杂的风格调整逻辑
                return self._apply_style_adjustment(response, adjustment)
                
            return response
            
        def _apply_style_adjustment(self, response: str, adjustment: dict) -> str:
            """应用风格调整"""
            # 简单的风格调整实现
            styled_response = response
            
            # 根据情感添加合适的语气词
            if adjustment["tone"] == "gentle_and_caring":
                styled_response = f"嗯，{styled_response}"
            elif adjustment["tone"] == "bright_and_cheerful":
                styled_response = f"{styled_response} 😊"
                
            return styled_response
    ```
    
    ### 第三步：人格管理系统
    ```python
    class PersonalityManager:
        def __init__(self):
            self.core_personality = {
                "name": "Estia",
                "traits": {
                    "warmth": 0.8,
                    "patience": 0.9,
                    "humor": 0.6,
                    "intelligence": 0.8,
                    "empathy": 0.9,
                    "playfulness": 0.7
                },
                "values": [
                    "helping others grow",
                    "creating meaningful connections",
                    "being genuine and authentic",
                    "respecting boundaries"
                ],
                "speaking_style": {
                    "formality": "casual_friendly",
                    "verbosity": "moderate",
                    "humor_frequency": "occasional",
                    "emotional_expression": "open"
                }
            }
            self.user_adaptations = {}
            
        async def get_personality_for_user(self, user_id: str) -> dict:
            """获取针对特定用户的人格设置"""
            if user_id not in self.user_adaptations:
                self.user_adaptations[user_id] = self.core_personality.copy()
                
            return self.user_adaptations[user_id]
            
        async def adapt_personality(self, user_id: str, interaction_history: List[dict]):
            """根据交互历史调整人格"""
            user_personality = await self.get_personality_for_user(user_id)
            
            # 分析用户偏好
            user_preferences = self._analyze_user_preferences(interaction_history)
            
            # 调整人格特征
            if user_preferences.get("prefers_humor", False):
                user_personality["traits"]["humor"] = min(
                    user_personality["traits"]["humor"] + 0.1, 1.0
                )
                
            if user_preferences.get("prefers_formal", False):
                user_personality["speaking_style"]["formality"] = "formal"
                
            # 保存调整后的人格
            self.user_adaptations[user_id] = user_personality
            
        def _analyze_user_preferences(self, history: List[dict]) -> dict:
            """分析用户偏好"""
            preferences = {}
            
            # 分析用户对幽默的反应
            humor_reactions = []
            for interaction in history:
                if "humor" in interaction.get("ai_response", ""):
                    user_reaction = interaction.get("user_feedback", {})
                    if user_reaction.get("positive", False):
                        humor_reactions.append(True)
                    else:
                        humor_reactions.append(False)
                        
            preferences["prefers_humor"] = sum(humor_reactions) > len(humor_reactions) / 2
            
            # 分析用户的语言风格
            user_inputs = [i.get("user_input", "") for i in history]
            formal_indicators = ["please", "thank you", "could you", "would you"]
            
            formal_count = sum(
                1 for input_text in user_inputs 
                for indicator in formal_indicators 
                if indicator in input_text.lower()
            )
            
            preferences["prefers_formal"] = formal_count > len(user_inputs) / 3
            
            return preferences
            
        def generate_personality_prompt(self, user_personality: dict) -> str:
            """生成人格prompt"""
            traits = user_personality["traits"]
            style = user_personality["speaking_style"]
            
            prompt = f"""
            你是Estia，一个温暖、有同理心的AI助手。你的性格特征：
            
            核心特质：
            - 温暖度：{traits['warmth']*100:.0f}%
            - 耐心度：{traits['patience']*100:.0f}%
            - 幽默感：{traits['humor']*100:.0f}%
            - 共情能力：{traits['empathy']*100:.0f}%
            - 活泼度：{traits['playfulness']*100:.0f}%
            
            说话风格：
            - 正式程度：{style['formality']}
            - 详细程度：{style['verbosity']}
            - 幽默频率：{style['humor_frequency']}
            - 情感表达：{style['emotional_expression']}
            
            核心价值观：
            - 帮助他人成长
            - 创造有意义的连接
            - 保持真诚和真实
            - 尊重边界
            
            请以此人格特征与用户交流，保持一致性和真实性。
            """
            
            return prompt
    ```
    
    ### 第四步：主动关怀系统
    ```python
    class ProactiveCareSystem:
        def __init__(self, memory_manager, emotion_analyzer):
            self.memory_manager = memory_manager
            self.emotion_analyzer = emotion_analyzer
            self.care_triggers = self._setup_care_triggers()
            
        async def check_care_triggers(self, user_id: str) -> Optional[str]:
            """检查是否需要主动关怀"""
            # 获取用户最近的交互历史
            recent_interactions = await self.memory_manager.get_recent_interactions(
                user_id, days=7
            )
            
            # 检查各种关怀触发条件
            for trigger in self.care_triggers:
                if await trigger["condition"](recent_interactions):
                    return await trigger["action"](recent_interactions)
                    
            return None
            
        def _setup_care_triggers(self) -> List[dict]:
            """设置关怀触发器"""
            return [
                {
                    "name": "long_absence",
                    "condition": self._check_long_absence,
                    "action": self._generate_check_in_message
                },
                {
                    "name": "emotional_pattern",
                    "condition": self._check_emotional_decline,
                    "action": self._generate_support_message
                },
                {
                    "name": "milestone_celebration",
                    "condition": self._check_positive_milestone,
                    "action": self._generate_celebration_message
                }
            ]
            
        async def _check_long_absence(self, interactions: List[dict]) -> bool:
            """检查长时间未交互"""
            if not interactions:
                return False
                
            from datetime import datetime, timedelta
            last_interaction = datetime.fromisoformat(interactions[0]["timestamp"])
            return datetime.now() - last_interaction > timedelta(days=2)
            
        async def _check_emotional_decline(self, interactions: List[dict]) -> bool:
            """检查情感状态下降"""
            if len(interactions) < 3:
                return False
                
            # 分析最近的情感趋势
            emotions = []
            for interaction in interactions[:5]:  # 最近5次交互
                if "emotion" in interaction:
                    emotions.append(interaction["emotion"])
                    
            # 检查是否有持续的负面情绪
            negative_emotions = ["sadness", "anger", "fear", "disgust"]
            negative_count = sum(
                1 for emotion_dict in emotions 
                for emotion, score in emotion_dict.items()
                if emotion in negative_emotions and score > 0.6
            )
            
            return negative_count >= 2
            
        async def _check_positive_milestone(self, interactions: List[dict]) -> bool:
            """检查积极里程碑"""
            # 检查是否有值得庆祝的事件
            celebration_keywords = [
                "成功", "完成", "通过", "获得", "赢得", 
                "升职", "毕业", "结婚", "生日"
            ]
            
            for interaction in interactions[:3]:  # 最近3次交互
                user_input = interaction.get("user_input", "")
                if any(keyword in user_input for keyword in celebration_keywords):
                    return True
                    
            return False
            
        async def _generate_check_in_message(self, interactions: List[dict]) -> str:
            """生成关怀问候消息"""
            messages = [
                "好久不见！你最近怎么样？",
                "想你了，最近忙什么呢？",
                "嗨！好几天没聊天了，一切都好吗？",
                "想起你了，最近有什么新鲜事吗？"
            ]
            
            import random
            return random.choice(messages)
            
        async def _generate_support_message(self, interactions: List[dict]) -> str:
            """生成支持消息"""
            messages = [
                "最近感觉你心情不太好，想聊聊吗？我在这里陪你。",
                "注意到你最近可能有些困扰，需要我陪你说说话吗？",
                "感觉你最近压力挺大的，要不要和我分享一下？",
                "我在这里，如果你需要倾诉或者只是想聊天，随时找我。"
            ]
            
            import random
            return random.choice(messages)
            
        async def _generate_celebration_message(self, interactions: List[dict]) -> str:
            """生成庆祝消息"""
            messages = [
                "恭喜你！真为你感到高兴！🎉",
                "太棒了！你做得很好！值得庆祝！",
                "哇！这真是个好消息！我为你感到骄傲！",
                "太好了！你的努力得到了回报！"
            ]
            
            import random
            return random.choice(messages)
    ```
  </process>

  <criteria>
    ## 陪伴AI质量标准
    
    ### 情感理解准确性
    - **情感识别准确率** > 85%
    - **情感响应合适性** > 90%
    - **上下文情感推理** > 80%
    - **多模态情感融合** > 85%
    
    ### 人格一致性
    - **核心特征稳定性** > 95%
    - **个性化适应度** > 80%
    - **跨会话一致性** > 90%
    - **情境适应能力** > 85%
    
    ### 陪伴质量
    - **共情回应质量** > 85%
    - **主动关怀及时性** > 80%
    - **情感支持有效性** > 80%
    - **用户满意度** > 85%
    
    ### 技术性能
    - **情感分析响应时间** < 200ms
    - **人格调整延迟** < 100ms
    - **系统稳定性** > 99%
    - **并发处理能力** > 100用户
  </criteria>
</execution>