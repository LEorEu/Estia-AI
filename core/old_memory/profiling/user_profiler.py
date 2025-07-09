#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户画像器
使用LLM构建用户画像，替代关键词匹配方式
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class UserProfiler:
    """LLM驱动的用户画像器"""
    
    def __init__(self, db_manager, llm_client=None):
        """
        初始化用户画像器
        
        Args:
            db_manager: 数据库管理器
            llm_client: LLM客户端（可选，用于生成画像）
        """
        self.db_manager = db_manager
        self.llm_client = llm_client
        self.logger = logger
        
        # 画像配置
        self.profile_config = {
            'min_memories_for_profile': 10,  # 构建画像需要的最少记忆数
            'profile_update_interval': 86400,  # 画像更新间隔（秒）
            'max_memories_for_analysis': 50,  # 分析用的最大记忆数
            'profile_categories': [
                'basic_info',      # 基本信息
                'preferences',     # 偏好兴趣
                'personality',     # 性格特点
                'goals',           # 目标计划
                'relationships',   # 人际关系
                'habits',          # 生活习惯
                'skills',          # 技能特长
                'values'           # 价值观念
            ]
        }
    
    def build_user_profile(self, user_id: str = "default", force_rebuild: bool = False) -> Dict[str, Any]:
        """
        构建用户画像
        
        Args:
            user_id: 用户ID
            force_rebuild: 是否强制重建
            
        Returns:
            Dict: 用户画像
        """
        try:
            # 检查是否需要更新画像
            existing_profile = self.get_existing_profile(user_id)
            if existing_profile and not force_rebuild:
                last_update = existing_profile.get('last_updated', 0)
                if time.time() - last_update < self.profile_config['profile_update_interval']:
                    self.logger.debug(f"用户 {user_id} 的画像还未到更新时间")
                    return existing_profile
            
            # 获取用户记忆数据
            memories = self.get_user_memories(user_id)
            
            if len(memories) < self.profile_config['min_memories_for_profile']:
                return {
                    'user_id': user_id,
                    'status': 'insufficient_data',
                    'message': f'记忆数量不足，需要至少 {self.profile_config["min_memories_for_profile"]} 条',
                    'memory_count': len(memories),
                    'last_updated': time.time()
                }
            
            # 使用LLM分析构建画像
            if self.llm_client:
                profile = self.llm_generate_profile(memories, user_id)
            else:
                # 降级方案：基于规则的画像生成
                profile = self.rule_based_profile(memories, user_id)
            
            # 保存画像
            self.save_user_profile(user_id, profile)
            
            self.logger.info(f"用户 {user_id} 的画像构建完成")
            return profile
            
        except Exception as e:
            self.logger.error(f"构建用户画像失败: {e}")
            return {
                'user_id': user_id,
                'status': 'error',
                'message': str(e),
                'last_updated': time.time()
            }
    
    def get_user_memories(self, user_id: str, max_count: int = None) -> List[Dict]:
        """
        获取用户记忆数据
        
        Args:
            user_id: 用户ID
            max_count: 最大记忆数量
            
        Returns:
            List: 记忆列表
        """
        try:
            max_count = max_count or self.profile_config['max_memories_for_analysis']
            
            # 获取高权重和最近的记忆
            query = """
                SELECT content, type, weight, timestamp, session_id
                FROM memories 
                WHERE (archived IS NULL OR archived = 0)
                AND (deleted IS NULL OR deleted = 0)
                ORDER BY weight DESC, timestamp DESC
                LIMIT ?
            """
            
            results = self.db_manager.execute_query(query, (max_count,))
            
            memories = []
            if results:
                for row in results:
                    memories.append({
                        'content': row[0],
                        'type': row[1],
                        'weight': row[2],
                        'timestamp': row[3],
                        'session_id': row[4]
                    })
            
            return memories
            
        except Exception as e:
            self.logger.error(f"获取用户记忆失败: {e}")
            return []
    
    def llm_generate_profile(self, memories: List[Dict], user_id: str) -> Dict[str, Any]:
        """
        使用LLM生成用户画像
        
        Args:
            memories: 记忆列表
            user_id: 用户ID
            
        Returns:
            Dict: 用户画像
        """
        try:
            # 构建分析提示词
            analysis_prompt = self.build_analysis_prompt(memories)
            
            # 调用LLM进行分析
            # 这里需要根据实际的LLM客户端进行调整
            if hasattr(self.llm_client, 'generate'):
                response = self.llm_client.generate(analysis_prompt)
                profile_data = self.parse_llm_response(response)
            else:
                # 模拟LLM响应
                profile_data = self.simulate_llm_analysis(memories)
            
            # 构建完整画像
            profile = {
                'user_id': user_id,
                'status': 'success',
                'method': 'llm_generated',
                'profile_data': profile_data,
                'memory_count': len(memories),
                'last_updated': time.time(),
                'confidence_score': self.calculate_confidence_score(profile_data, memories)
            }
            
            return profile
            
        except Exception as e:
            self.logger.error(f"LLM生成画像失败: {e}")
            # 降级到规则方案
            return self.rule_based_profile(memories, user_id)
    
    def build_analysis_prompt(self, memories: List[Dict]) -> str:
        """
        构建LLM分析提示词
        
        Args:
            memories: 记忆列表
            
        Returns:
            str: 分析提示词
        """
        memory_texts = []
        for i, memory in enumerate(memories[:20]):  # 限制记忆数量避免提示词过长
            memory_texts.append(f"{i+1}. [{memory['type']}] {memory['content']}")
        
        memories_text = "\n".join(memory_texts)
        
        prompt = f"""请分析以下用户记忆，构建用户画像。请从以下维度进行分析：

1. 基本信息 (basic_info): 姓名、年龄、职业、居住地等
2. 偏好兴趣 (preferences): 兴趣爱好、喜欢的事物、消费偏好等
3. 性格特点 (personality): 性格特征、行为模式、沟通风格等
4. 目标计划 (goals): 短期和长期目标、计划、愿望等
5. 人际关系 (relationships): 家庭、朋友、同事关系等
6. 生活习惯 (habits): 作息、饮食、运动等生活习惯
7. 技能特长 (skills): 专业技能、才艺、擅长领域等
8. 价值观念 (values): 价值观、信念、态度等

用户记忆数据：
{memories_text}

请以JSON格式返回分析结果，每个维度包含具体的描述和置信度（0-1）：
{{
    "basic_info": {{"description": "具体描述", "confidence": 0.8}},
    "preferences": {{"description": "具体描述", "confidence": 0.7}},
    ...
}}
"""
        
        return prompt
    
    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM响应
        
        Args:
            response: LLM响应文本
            
        Returns:
            Dict: 解析后的画像数据
        """
        try:
            # 尝试解析JSON
            import re
            
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                profile_data = json.loads(json_str)
                return profile_data
            else:
                # 如果没找到JSON，使用文本解析
                return self.parse_text_response(response)
                
        except Exception as e:
            self.logger.error(f"解析LLM响应失败: {e}")
            return self.get_empty_profile_data()
    
    def simulate_llm_analysis(self, memories: List[Dict]) -> Dict[str, Any]:
        """
        模拟LLM分析（当没有LLM客户端时）
        
        Args:
            memories: 记忆列表
            
        Returns:
            Dict: 模拟的画像数据
        """
        # 这是一个简化的模拟分析
        profile_data = {}
        
        for category in self.profile_config['profile_categories']:
            description = f"基于 {len(memories)} 条记忆的{category}分析"
            confidence = min(0.5 + len(memories) * 0.01, 0.9)  # 基于记忆数量的置信度
            
            profile_data[category] = {
                'description': description,
                'confidence': confidence
            }
        
        return profile_data
    
    def rule_based_profile(self, memories: List[Dict], user_id: str) -> Dict[str, Any]:
        """
        基于规则的画像生成（降级方案）
        
        Args:
            memories: 记忆列表
            user_id: 用户ID
            
        Returns:
            Dict: 用户画像
        """
        try:
            profile_data = {}
            
            # 简单的关键词分析
            all_content = " ".join([mem['content'] for mem in memories])
            
            for category in self.profile_config['profile_categories']:
                keywords = self.get_category_keywords(category)
                matches = sum(1 for keyword in keywords if keyword in all_content.lower())
                
                if matches > 0:
                    description = f"检测到 {matches} 个相关关键词"
                    confidence = min(matches * 0.1, 0.8)
                else:
                    description = "暂无相关信息"
                    confidence = 0.1
                
                profile_data[category] = {
                    'description': description,
                    'confidence': confidence
                }
            
            return {
                'user_id': user_id,
                'status': 'success',
                'method': 'rule_based',
                'profile_data': profile_data,
                'memory_count': len(memories),
                'last_updated': time.time(),
                'confidence_score': 0.5  # 规则方案置信度较低
            }
            
        except Exception as e:
            self.logger.error(f"规则画像生成失败: {e}")
            return self.get_empty_profile(user_id)
    
    def get_category_keywords(self, category: str) -> List[str]:
        """
        获取类别关键词
        
        Args:
            category: 类别名称
            
        Returns:
            List: 关键词列表
        """
        keywords_map = {
            'basic_info': ['我叫', '我是', '姓名', '名字', '年龄', '职业', '工作'],
            'preferences': ['喜欢', '爱好', '兴趣', '偏好', '喜爱', '热爱'],
            'personality': ['性格', '特点', '习惯', '风格', '个性', '脾气'],
            'goals': ['目标', '计划', '想要', '希望', '打算', '梦想'],
            'relationships': ['家人', '朋友', '同事', '家庭', '关系', '父母'],
            'habits': ['习惯', '作息', '饮食', '运动', '睡觉', '起床'],
            'skills': ['技能', '能力', '擅长', '专业', '会', '学过'],
            'values': ['价值观', '信念', '认为', '觉得', '重要', '意义']
        }
        
        return keywords_map.get(category, [])
    
    def calculate_confidence_score(self, profile_data: Dict[str, Any], memories: List[Dict]) -> float:
        """
        计算画像置信度
        
        Args:
            profile_data: 画像数据
            memories: 记忆列表
            
        Returns:
            float: 置信度分数
        """
        try:
            confidences = []
            for category_data in profile_data.values():
                if isinstance(category_data, dict) and 'confidence' in category_data:
                    confidences.append(category_data['confidence'])
            
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                # 根据记忆数量调整置信度
                memory_factor = min(len(memories) / 50, 1.0)
                return avg_confidence * memory_factor
            else:
                return 0.1
                
        except Exception as e:
            self.logger.error(f"计算置信度失败: {e}")
            return 0.1
    
    def get_existing_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取现有用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[Dict]: 现有画像或None
        """
        try:
            query = """
                SELECT content, timestamp 
                FROM memories 
                WHERE type = 'user_profile' 
                AND content LIKE ?
                ORDER BY timestamp DESC 
                LIMIT 1
            """
            
            result = self.db_manager.execute_query(query, (f'%"user_id": "{user_id}"%',))
            
            if result:
                profile_json = result[0][0]
                return json.loads(profile_json)
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取现有画像失败: {e}")
            return None
    
    def save_user_profile(self, user_id: str, profile: Dict[str, Any]):
        """
        保存用户画像
        
        Args:
            user_id: 用户ID
            profile: 用户画像
        """
        try:
            profile_json = json.dumps(profile, ensure_ascii=False, indent=2)
            
            # 保存为特殊类型的记忆
            insert_query = """
                INSERT INTO memories (id, content, type, weight, timestamp, session_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            memory_id = f"profile_{user_id}_{int(time.time())}"
            current_time = time.time()
            
            metadata = json.dumps({
                'profile_version': '2.0',
                'generation_method': profile.get('method', 'unknown'),
                'confidence_score': profile.get('confidence_score', 0.0)
            })
            
            self.db_manager.execute_query(
                insert_query,
                (memory_id, profile_json, 'user_profile', 8.0, current_time, None, metadata)
            )
            
            self.logger.info(f"用户 {user_id} 的画像已保存")
            
        except Exception as e:
            self.logger.error(f"保存用户画像失败: {e}")
    
    def get_empty_profile_data(self) -> Dict[str, Any]:
        """获取空的画像数据结构"""
        profile_data = {}
        for category in self.profile_config['profile_categories']:
            profile_data[category] = {
                'description': '暂无信息',
                'confidence': 0.0
            }
        return profile_data
    
    def get_empty_profile(self, user_id: str) -> Dict[str, Any]:
        """获取空的画像结构"""
        return {
            'user_id': user_id,
            'status': 'empty',
            'method': 'fallback',
            'profile_data': self.get_empty_profile_data(),
            'memory_count': 0,
            'last_updated': time.time(),
            'confidence_score': 0.0
        }
    
    def parse_text_response(self, response: str) -> Dict[str, Any]:
        """
        解析文本响应（当JSON解析失败时）
        
        Args:
            response: 响应文本
            
        Returns:
            Dict: 解析后的画像数据
        """
        profile_data = self.get_empty_profile_data()
        
        try:
            # 简单的文本解析逻辑
            lines = response.split('\n')
            current_category = None
            
            for line in lines:
                line = line.strip()
                if any(cat in line.lower() for cat in self.profile_config['profile_categories']):
                    # 找到类别
                    for cat in self.profile_config['profile_categories']:
                        if cat in line.lower():
                            current_category = cat
                            break
                elif current_category and line:
                    # 更新类别描述
                    profile_data[current_category]['description'] = line
                    profile_data[current_category]['confidence'] = 0.6
            
        except Exception as e:
            self.logger.error(f"文本解析失败: {e}")
        
        return profile_data 