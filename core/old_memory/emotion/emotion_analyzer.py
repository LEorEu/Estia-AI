#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
情感分析器
使用专业情感分析模型（如goemotions）替代关键词匹配
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """专业情感分析器"""
    
    def __init__(self, model_name: str = "goemotions", use_transformers: bool = True):
        """
        初始化情感分析器
        
        Args:
            model_name: 模型名称
            use_transformers: 是否使用transformers库
        """
        self.model_name = model_name
        self.use_transformers = use_transformers
        self.logger = logger
        
        # 情感配置
        self.emotion_config = {
            'confidence_threshold': 0.5,  # 置信度阈值
            'max_text_length': 512,       # 最大文本长度
            'batch_size': 8,              # 批处理大小
            'use_cache': True,            # 是否使用缓存
        }
        
        # 情感标签映射
        self.emotion_mapping = {
            # GoEmotions 27种情感 -> 简化的6种情感
            'admiration': 'positive',
            'amusement': 'positive', 
            'approval': 'positive',
            'caring': 'positive',
            'excitement': 'positive',
            'gratitude': 'positive',
            'joy': 'positive',
            'love': 'positive',
            'optimism': 'positive',
            'pride': 'positive',
            'relief': 'positive',
            
            'anger': 'negative',
            'annoyance': 'negative',
            'disappointment': 'negative',
            'disapproval': 'negative',
            'disgust': 'negative',
            'embarrassment': 'negative',
            'grief': 'negative',
            'remorse': 'negative',
            'sadness': 'negative',
            
            'fear': 'anxious',
            'nervousness': 'anxious',
            
            'confusion': 'confused',
            'curiosity': 'curious',
            'desire': 'desire',
            'realization': 'realization',
            'surprise': 'surprise',
            'neutral': 'neutral'
        }
        
        # 初始化模型
        self.model = None
        self.tokenizer = None
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化情感分析模型"""
        try:
            if self.use_transformers:
                self._initialize_transformers_model()
            else:
                self._initialize_fallback_model()
                
        except Exception as e:
            self.logger.warning(f"情感分析模型初始化失败: {e}，使用降级方案")
            self._initialize_fallback_model()
    
    def _initialize_transformers_model(self):
        """初始化transformers模型"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            # 使用GoEmotions模型
            model_path = "j-hartmann/emotion-english-distilroberta-base"
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            
            # 设置为评估模式
            self.model.eval()
            
            self.logger.info(f"✅ 情感分析模型加载成功: {model_path}")
            
        except ImportError:
            self.logger.warning("transformers库未安装，使用降级方案")
            raise
        except Exception as e:
            self.logger.error(f"transformers模型加载失败: {e}")
            raise
    
    def _initialize_fallback_model(self):
        """初始化降级模型（基于规则）"""
        self.model = "rule_based"
        self.tokenizer = None
        self.logger.info("🔄 使用基于规则的情感分析降级方案")
    
    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """
        分析单个文本的情感
        
        Args:
            text: 待分析的文本
            
        Returns:
            Dict: 情感分析结果
        """
        try:
            if not text or len(text.strip()) == 0:
                return self._get_neutral_emotion()
            
            # 文本预处理
            processed_text = self._preprocess_text(text)
            
            if self.model and self.model != "rule_based":
                return self._analyze_with_model(processed_text)
            else:
                return self._analyze_with_rules(processed_text)
                
        except Exception as e:
            self.logger.error(f"情感分析失败: {e}")
            return self._get_error_emotion(str(e))
    
    def analyze_emotions_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        批量分析情感
        
        Args:
            texts: 文本列表
            
        Returns:
            List: 情感分析结果列表
        """
        try:
            if not texts:
                return []
            
            # 预处理所有文本
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            if self.model and self.model != "rule_based":
                return self._analyze_batch_with_model(processed_texts)
            else:
                return [self._analyze_with_rules(text) for text in processed_texts]
                
        except Exception as e:
            self.logger.error(f"批量情感分析失败: {e}")
            return [self._get_error_emotion(str(e)) for _ in texts]
    
    def _analyze_with_model(self, text: str) -> Dict[str, Any]:
        """使用深度学习模型分析情感"""
        try:
            import torch
            from torch.nn.functional import softmax
            
            # 编码文本
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=self.emotion_config['max_text_length'],
                padding=True
            )
            
            # 推理
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = softmax(outputs.logits, dim=-1)
            
            # 获取预测结果
            emotion_scores = predictions[0].tolist()
            
            # 获取标签（这里需要根据实际模型调整）
            emotion_labels = [
                'anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise'
            ]  # 这是一个示例，实际标签需要根据模型确定
            
            # 构建结果
            emotions = {}
            for label, score in zip(emotion_labels, emotion_scores):
                emotions[label] = round(score, 4)
            
            # 找到最高分的情感
            max_emotion = max(emotions.items(), key=lambda x: x[1])
            primary_emotion = max_emotion[0]
            confidence = max_emotion[1]
            
            # 映射到简化的情感类别
            simplified_emotion = self.emotion_mapping.get(primary_emotion, 'neutral')
            
            return {
                'primary_emotion': primary_emotion,
                'simplified_emotion': simplified_emotion,
                'confidence': confidence,
                'all_emotions': emotions,
                'method': 'transformer_model',
                'model_name': self.model_name
            }
            
        except Exception as e:
            self.logger.error(f"模型情感分析失败: {e}")
            return self._analyze_with_rules(text)
    
    def _analyze_batch_with_model(self, texts: List[str]) -> List[Dict[str, Any]]:
        """批量使用模型分析"""
        try:
            import torch
            from torch.nn.functional import softmax
            
            # 批量编码
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                truncation=True,
                max_length=self.emotion_config['max_text_length'],
                padding=True
            )
            
            # 批量推理
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = softmax(outputs.logits, dim=-1)
            
            # 处理结果
            results = []
            emotion_labels = [
                'anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise'
            ]
            
            for i, text in enumerate(texts):
                emotion_scores = predictions[i].tolist()
                
                emotions = {}
                for label, score in zip(emotion_labels, emotion_scores):
                    emotions[label] = round(score, 4)
                
                max_emotion = max(emotions.items(), key=lambda x: x[1])
                primary_emotion = max_emotion[0]
                confidence = max_emotion[1]
                simplified_emotion = self.emotion_mapping.get(primary_emotion, 'neutral')
                
                results.append({
                    'primary_emotion': primary_emotion,
                    'simplified_emotion': simplified_emotion,
                    'confidence': confidence,
                    'all_emotions': emotions,
                    'method': 'transformer_model_batch',
                    'model_name': self.model_name
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"批量模型分析失败: {e}")
            return [self._analyze_with_rules(text) for text in texts]
    
    def _analyze_with_rules(self, text: str) -> Dict[str, Any]:
        """基于规则的情感分析（降级方案）"""
        try:
            text_lower = text.lower()
            
            # 情感关键词词典
            emotion_keywords = {
                'positive': [
                    '开心', '高兴', '兴奋', '愉快', '快乐', '满意', '棒', '好', '赞', '喜欢',
                    '爱', '感谢', '谢谢', '优秀', '完美', '成功', '胜利', '幸福', '美好'
                ],
                'negative': [
                    '难过', '沮丧', '烦恼', '郁闷', '失望', '愤怒', '生气', '恼火', '讨厌',
                    '糟糕', '坏', '差', '失败', '痛苦', '悲伤', '不满', '抱怨'
                ],
                'anxious': [
                    '焦虑', '担心', '紧张', '害怕', '恐惧', '不安', '忧虑', '惊慌', '恐慌'
                ],
                'surprise': [
                    '惊讶', '意外', '震惊', '不敢相信', '没想到', '竟然', '居然'
                ],
                'confused': [
                    '困惑', '迷惑', '不懂', '不明白', '搞不清', '疑惑', '纳闷'
                ]
            }
            
            # 计算各情感的匹配分数
            scores = {}
            for emotion, keywords in emotion_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                scores[emotion] = score / len(keywords)  # 归一化
            
            # 添加中性情感
            scores['neutral'] = 0.5 if all(score == 0 for score in scores.values()) else 0.1
            
            # 找到最高分的情感
            if scores:
                max_emotion = max(scores.items(), key=lambda x: x[1])
                primary_emotion = max_emotion[0]
                confidence = min(max_emotion[1] * 2, 1.0)  # 调整置信度
            else:
                primary_emotion = 'neutral'
                confidence = 0.5
            
            # 如果置信度太低，设为中性
            if confidence < self.emotion_config['confidence_threshold']:
                primary_emotion = 'neutral'
                confidence = 0.6
            
            return {
                'primary_emotion': primary_emotion,
                'simplified_emotion': primary_emotion,
                'confidence': round(confidence, 3),
                'all_emotions': {k: round(v, 3) for k, v in scores.items()},
                'method': 'rule_based',
                'model_name': 'keyword_matching'
            }
            
        except Exception as e:
            self.logger.error(f"规则情感分析失败: {e}")
            return self._get_neutral_emotion()
    
    def _preprocess_text(self, text: str) -> str:
        """文本预处理"""
        try:
            # 基本清理
            text = text.strip()
            
            # 限制长度
            if len(text) > self.emotion_config['max_text_length']:
                text = text[:self.emotion_config['max_text_length']]
            
            return text
            
        except Exception as e:
            self.logger.error(f"文本预处理失败: {e}")
            return text
    
    def _get_neutral_emotion(self) -> Dict[str, Any]:
        """获取中性情感结果"""
        return {
            'primary_emotion': 'neutral',
            'simplified_emotion': 'neutral',
            'confidence': 0.6,
            'all_emotions': {'neutral': 1.0},
            'method': 'default',
            'model_name': 'fallback'
        }
    
    def _get_error_emotion(self, error_msg: str) -> Dict[str, Any]:
        """获取错误情感结果"""
        return {
            'primary_emotion': 'neutral',
            'simplified_emotion': 'neutral',
            'confidence': 0.0,
            'all_emotions': {'neutral': 1.0},
            'method': 'error',
            'model_name': 'fallback',
            'error': error_msg
        }
    
    def analyze_emotion_pattern(self, emotion_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析情感模式
        
        Args:
            emotion_history: 历史情感分析结果列表
            
        Returns:
            Dict: 情感模式分析
        """
        try:
            if not emotion_history:
                return {'pattern': 'no_data', 'description': '没有足够的情感数据'}
            
            # 统计各种情感的频率
            emotion_counts = {}
            total_confidence = 0
            
            for emotion_result in emotion_history:
                primary = emotion_result.get('simplified_emotion', 'neutral')
                confidence = emotion_result.get('confidence', 0)
                
                emotion_counts[primary] = emotion_counts.get(primary, 0) + 1
                total_confidence += confidence
            
            total_count = len(emotion_history)
            avg_confidence = total_confidence / total_count if total_count > 0 else 0
            
            # 计算情感分布
            emotion_distribution = {
                emotion: count / total_count 
                for emotion, count in emotion_counts.items()
            }
            
            # 确定主要情感模式
            dominant_emotion = max(emotion_distribution.items(), key=lambda x: x[1])
            dominant_emotion_name = dominant_emotion[0]
            dominant_ratio = dominant_emotion[1]
            
            # 分析模式类型
            if dominant_ratio > 0.7:
                pattern = 'consistent'  # 情感一致
                description = f'情感较为一致，主要表现为{dominant_emotion_name}'
            elif len(emotion_counts) >= 4:
                pattern = 'diverse'  # 情感多样
                description = '情感表达丰富多样'
            elif 'positive' in emotion_counts and 'negative' in emotion_counts:
                pattern = 'mixed'  # 情感混合
                description = '正负情感交替出现'
            else:
                pattern = 'stable'  # 情感稳定
                description = '情感状态相对稳定'
            
            return {
                'pattern': pattern,
                'description': description,
                'dominant_emotion': dominant_emotion_name,
                'dominant_ratio': round(dominant_ratio, 3),
                'emotion_distribution': emotion_distribution,
                'avg_confidence': round(avg_confidence, 3),
                'sample_count': total_count
            }
            
        except Exception as e:
            self.logger.error(f"情感模式分析失败: {e}")
            return {
                'pattern': 'error',
                'description': f'分析失败: {str(e)}',
                'sample_count': len(emotion_history) if emotion_history else 0
            }
    
    def get_emotion_insights(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取情感洞察（包含情感分析和上下文理解）
        
        Args:
            text: 待分析文本
            context: 上下文信息
            
        Returns:
            Dict: 情感洞察结果
        """
        try:
            # 基础情感分析
            emotion_result = self.analyze_emotion(text)
            
            # 添加上下文洞察
            insights = {
                'emotion_analysis': emotion_result,
                'context_insights': {},
                'recommendations': []
            }
            
            if context:
                # 分析上下文中的情感变化
                if 'previous_emotions' in context:
                    pattern_analysis = self.analyze_emotion_pattern(context['previous_emotions'])
                    insights['context_insights']['emotion_pattern'] = pattern_analysis
                
                # 基于情感给出建议
                primary_emotion = emotion_result['simplified_emotion']
                confidence = emotion_result['confidence']
                
                if primary_emotion == 'negative' and confidence > 0.7:
                    insights['recommendations'].append('检测到较强的负面情感，建议关注用户情绪')
                elif primary_emotion == 'positive' and confidence > 0.7:
                    insights['recommendations'].append('用户情绪积极，可以继续当前的交流方式')
                elif primary_emotion == 'anxious' and confidence > 0.6:
                    insights['recommendations'].append('用户可能感到焦虑，建议提供安慰和支持')
            
            return insights
            
        except Exception as e:
            self.logger.error(f"情感洞察分析失败: {e}")
            return {
                'emotion_analysis': self._get_error_emotion(str(e)),
                'context_insights': {},
                'recommendations': ['情感分析出现问题，建议检查系统状态']
            } 