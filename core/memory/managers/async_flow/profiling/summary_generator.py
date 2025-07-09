#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
摘要生成器
提供定期摘要生成功能（每日/周摘要）
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SummaryGenerator:
    """定期摘要生成器"""
    
    def __init__(self, db_manager, llm_client=None, user_profiler=None):
        """
        初始化摘要生成器
        
        Args:
            db_manager: 数据库管理器
            llm_client: LLM客户端（可选）
            user_profiler: 用户画像器（可选）
        """
        self.db_manager = db_manager
        self.llm_client = llm_client
        self.user_profiler = user_profiler
        self.logger = logger
        
        # 摘要配置
        self.summary_config = {
            'daily_summary_interval': 86400,  # 每日摘要间隔（秒）
            'weekly_summary_interval': 604800,  # 每周摘要间隔（秒）
            'min_memories_for_daily': 5,  # 每日摘要最少记忆数
            'min_memories_for_weekly': 20,  # 每周摘要最少记忆数
            'max_memories_per_summary': 100,  # 每个摘要最大记忆数
            'summary_weight': 7.5,  # 摘要记忆权重
        }
    
    def generate_daily_summary(self, date: str = None, force: bool = False) -> Dict[str, Any]:
        """
        生成每日摘要
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)，默认为今天
            force: 是否强制生成
            
        Returns:
            Dict: 摘要结果
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            # 检查是否已有摘要
            if not force:
                existing_summary = self.get_existing_summary('daily', date)
                if existing_summary:
                    self.logger.debug(f"日期 {date} 已有每日摘要")
                    return existing_summary
            
            # 获取当日记忆
            memories = self.get_memories_by_date(date)
            
            if len(memories) < self.summary_config['min_memories_for_daily']:
                return {
                    'type': 'daily',
                    'date': date,
                    'status': 'insufficient_data',
                    'message': f'记忆数量不足，需要至少 {self.summary_config["min_memories_for_daily"]} 条',
                    'memory_count': len(memories),
                    'timestamp': time.time()
                }
            
            # 生成摘要
            summary_content = self.generate_summary_content(memories, 'daily', date)
            
            # 保存摘要
            summary_id = self.save_summary('daily', date, summary_content, memories)
            
            # 更新用户画像（如果有用户画像器）
            if self.user_profiler:
                try:
                    self.user_profiler.build_user_profile(force_rebuild=False)
                except Exception as e:
                    self.logger.warning(f"更新用户画像失败: {e}")
            
            self.logger.info(f"每日摘要生成完成: {date}")
            
            return {
                'type': 'daily',
                'date': date,
                'status': 'success',
                'summary_id': summary_id,
                'summary_content': summary_content,
                'memory_count': len(memories),
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"生成每日摘要失败: {e}")
            return {
                'type': 'daily',
                'date': date,
                'status': 'error',
                'message': str(e),
                'timestamp': time.time()
            }
    
    def generate_weekly_summary(self, week_start: str = None, force: bool = False) -> Dict[str, Any]:
        """
        生成每周摘要
        
        Args:
            week_start: 周开始日期字符串 (YYYY-MM-DD)，默认为本周一
            force: 是否强制生成
            
        Returns:
            Dict: 摘要结果
        """
        try:
            if not week_start:
                today = datetime.now()
                monday = today - timedelta(days=today.weekday())
                week_start = monday.strftime('%Y-%m-%d')
            
            # 检查是否已有摘要
            if not force:
                existing_summary = self.get_existing_summary('weekly', week_start)
                if existing_summary:
                    self.logger.debug(f"周 {week_start} 已有每周摘要")
                    return existing_summary
            
            # 获取本周记忆
            memories = self.get_memories_by_week(week_start)
            
            if len(memories) < self.summary_config['min_memories_for_weekly']:
                return {
                    'type': 'weekly',
                    'week_start': week_start,
                    'status': 'insufficient_data',
                    'message': f'记忆数量不足，需要至少 {self.summary_config["min_memories_for_weekly"]} 条',
                    'memory_count': len(memories),
                    'timestamp': time.time()
                }
            
            # 生成摘要
            summary_content = self.generate_summary_content(memories, 'weekly', week_start)
            
            # 保存摘要
            summary_id = self.save_summary('weekly', week_start, summary_content, memories)
            
            self.logger.info(f"每周摘要生成完成: {week_start}")
            
            return {
                'type': 'weekly',
                'week_start': week_start,
                'status': 'success',
                'summary_id': summary_id,
                'summary_content': summary_content,
                'memory_count': len(memories),
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"生成每周摘要失败: {e}")
            return {
                'type': 'weekly',
                'week_start': week_start,
                'status': 'error',
                'message': str(e),
                'timestamp': time.time()
            }
    
    def get_memories_by_date(self, date: str) -> List[Dict]:
        """
        获取指定日期的记忆
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            List: 记忆列表
        """
        try:
            # 转换日期为时间戳范围
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            start_timestamp = date_obj.timestamp()
            end_timestamp = start_timestamp + 86400  # +24小时
            
            query = """
                SELECT id, content, type, weight, timestamp, session_id
                FROM memories 
                WHERE timestamp >= ? AND timestamp < ?
                AND (archived IS NULL OR archived = 0)
                AND (deleted IS NULL OR deleted = 0)
                AND type NOT IN ('daily_summary', 'weekly_summary', 'user_profile')
                ORDER BY weight DESC, timestamp DESC
                LIMIT ?
            """
            
            max_memories = self.summary_config['max_memories_per_summary']
            results = self.db_manager.execute_query(
                query, 
                (start_timestamp, end_timestamp, max_memories)
            )
            
            memories = []
            if results:
                for row in results:
                    memories.append({
                        'id': row[0],
                        'content': row[1],
                        'type': row[2],
                        'weight': row[3],
                        'timestamp': row[4],
                        'session_id': row[5]
                    })
            
            return memories
            
        except Exception as e:
            self.logger.error(f"获取日期记忆失败: {e}")
            return []
    
    def get_memories_by_week(self, week_start: str) -> List[Dict]:
        """
        获取指定周的记忆
        
        Args:
            week_start: 周开始日期字符串 (YYYY-MM-DD)
            
        Returns:
            List: 记忆列表
        """
        try:
            # 转换日期为时间戳范围
            start_date = datetime.strptime(week_start, '%Y-%m-%d')
            start_timestamp = start_date.timestamp()
            end_timestamp = start_timestamp + 604800  # +7天
            
            query = """
                SELECT id, content, type, weight, timestamp, session_id
                FROM memories 
                WHERE timestamp >= ? AND timestamp < ?
                AND (archived IS NULL OR archived = 0)
                AND (deleted IS NULL OR deleted = 0)
                AND type NOT IN ('daily_summary', 'weekly_summary', 'user_profile')
                ORDER BY weight DESC, timestamp DESC
                LIMIT ?
            """
            
            max_memories = self.summary_config['max_memories_per_summary']
            results = self.db_manager.execute_query(
                query, 
                (start_timestamp, end_timestamp, max_memories)
            )
            
            memories = []
            if results:
                for row in results:
                    memories.append({
                        'id': row[0],
                        'content': row[1],
                        'type': row[2],
                        'weight': row[3],
                        'timestamp': row[4],
                        'session_id': row[5]
                    })
            
            return memories
            
        except Exception as e:
            self.logger.error(f"获取周记忆失败: {e}")
            return []
    
    def generate_summary_content(self, memories: List[Dict], summary_type: str, date_key: str) -> Dict[str, Any]:
        """
        生成摘要内容
        
        Args:
            memories: 记忆列表
            summary_type: 摘要类型 ('daily' 或 'weekly')
            date_key: 日期标识
            
        Returns:
            Dict: 摘要内容
        """
        try:
            if self.llm_client:
                return self.llm_generate_summary(memories, summary_type, date_key)
            else:
                return self.rule_based_summary(memories, summary_type, date_key)
                
        except Exception as e:
            self.logger.error(f"生成摘要内容失败: {e}")
            return self.fallback_summary(memories, summary_type, date_key)
    
    def llm_generate_summary(self, memories: List[Dict], summary_type: str, date_key: str) -> Dict[str, Any]:
        """
        使用LLM生成摘要
        
        Args:
            memories: 记忆列表
            summary_type: 摘要类型
            date_key: 日期标识
            
        Returns:
            Dict: 摘要内容
        """
        try:
            # 构建摘要提示词
            prompt = self.build_summary_prompt(memories, summary_type, date_key)
            
            # 调用LLM生成摘要
            if hasattr(self.llm_client, 'generate'):
                response = self.llm_client.generate(prompt)
                summary_data = self.parse_summary_response(response)
            else:
                summary_data = self.simulate_llm_summary(memories, summary_type, date_key)
            
            return {
                'method': 'llm_generated',
                'summary_data': summary_data,
                'confidence': 0.8
            }
            
        except Exception as e:
            self.logger.error(f"LLM摘要生成失败: {e}")
            return self.rule_based_summary(memories, summary_type, date_key)
    
    def build_summary_prompt(self, memories: List[Dict], summary_type: str, date_key: str) -> str:
        """
        构建摘要生成提示词
        
        Args:
            memories: 记忆列表
            summary_type: 摘要类型
            date_key: 日期标识
            
        Returns:
            str: 提示词
        """
        memory_texts = []
        for i, memory in enumerate(memories[:30]):  # 限制记忆数量
            memory_texts.append(f"{i+1}. [{memory['type']}] {memory['content']}")
        
        memories_text = "\n".join(memory_texts)
        
        time_period = "当日" if summary_type == 'daily' else "本周"
        
        prompt = f"""请为以下{time_period}的用户记忆生成摘要。

摘要应包含以下内容：
1. 主要活动：{time_period}的主要活动和事件
2. 重要话题：讨论的主要话题和关注点
3. 情感状态：{time_period}的整体情感倾向
4. 学习成长：新的学习、认知或成长点
5. 人际互动：与他人的交流和互动情况
6. 未来计划：提到的计划或目标

请以JSON格式返回摘要：
{{
    "main_activities": "主要活动描述",
    "key_topics": ["话题1", "话题2", "话题3"],
    "emotional_state": "情感状态描述",
    "learning_growth": "学习成长描述",
    "social_interactions": "人际互动描述",
    "future_plans": "未来计划描述",
    "highlights": ["重点1", "重点2", "重点3"]
}}

{time_period}记忆数据（共{len(memories)}条）：
{memories_text}
"""
        
        return prompt
    
    def parse_summary_response(self, response: str) -> Dict[str, Any]:
        """
        解析摘要响应
        
        Args:
            response: LLM响应
            
        Returns:
            Dict: 解析后的摘要数据
        """
        try:
            import re
            
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                summary_data = json.loads(json_str)
                return summary_data
            else:
                return self.parse_text_summary(response)
                
        except Exception as e:
            self.logger.error(f"解析摘要响应失败: {e}")
            return {
                "main_activities": "无法解析的摘要内容",
                "key_topics": [],
                "emotional_state": "中性",
                "learning_growth": "暂无",
                "social_interactions": "暂无",
                "future_plans": "暂无",
                "highlights": []
            }
    
    def simulate_llm_summary(self, memories: List[Dict], summary_type: str, date_key: str) -> Dict[str, Any]:
        """
        模拟LLM摘要生成
        
        Args:
            memories: 记忆列表
            summary_type: 摘要类型
            date_key: 日期标识
            
        Returns:
            Dict: 模拟摘要数据
        """
        # 提取关键词作为话题
        all_text = " ".join([mem['content'] for mem in memories])
        topics = self.extract_keywords(all_text)
        
        return {
            "main_activities": f"基于{len(memories)}条记忆的{summary_type}活动总结",
            "key_topics": topics[:5],  # 前5个话题
            "emotional_state": "积极向上",  # 简化的情感状态
            "learning_growth": f"在{date_key}期间有新的认知和学习",
            "social_interactions": "与他人有良好的交流互动",
            "future_plans": "制定了新的计划和目标",
            "highlights": [f"重要事件{i+1}" for i in range(min(3, len(memories)//3))]
        }
    
    def rule_based_summary(self, memories: List[Dict], summary_type: str, date_key: str) -> Dict[str, Any]:
        """
        基于规则的摘要生成
        
        Args:
            memories: 记忆列表
            summary_type: 摘要类型
            date_key: 日期标识
            
        Returns:
            Dict: 摘要内容
        """
        try:
            # 基本统计
            user_memories = [m for m in memories if m['type'] == 'user_input']
            ai_memories = [m for m in memories if m['type'] == 'assistant_reply']
            
            # 提取关键信息
            all_text = " ".join([mem['content'] for mem in memories])
            keywords = self.extract_keywords(all_text)
            
            return {
                'method': 'rule_based',
                'summary_data': {
                    "main_activities": f"共进行了{len(user_memories)}次交流，{len(ai_memories)}次回应",
                    "key_topics": keywords[:5],
                    "emotional_state": "正常交流状态",
                    "learning_growth": f"处理了{len(memories)}条记忆信息",
                    "social_interactions": f"与AI助手进行了{len(user_memories)}次对话",
                    "future_plans": "继续保持对话和学习",
                    "highlights": [f"高权重记忆: {mem['content'][:50]}..." 
                                 for mem in sorted(memories, key=lambda x: x['weight'], reverse=True)[:3]]
                },
                'confidence': 0.5
            }
            
        except Exception as e:
            self.logger.error(f"规则摘要生成失败: {e}")
            return self.fallback_summary(memories, summary_type, date_key)
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        简单的关键词提取
        
        Args:
            text: 文本内容
            
        Returns:
            List: 关键词列表
        """
        try:
            # 简单的分词和筛选
            import re
            
            # 去除标点符号，分词
            words = re.findall(r'\b\w+\b', text.lower())
            
            # 简单的停用词
            stop_words = {'的', '了', '是', '在', '我', '你', '他', '她', '我们', '你们', '他们', '这', '那', '有', '要', '不', '会', '可以', '能', '去', '来', '到'}
            
            # 过滤停用词和短词
            keywords = [word for word in words if len(word) > 1 and word not in stop_words]
            
            # 计算词频，返回频率最高的词
            from collections import Counter
            word_counts = Counter(keywords)
            
            return [word for word, count in word_counts.most_common(10)]
            
        except Exception as e:
            self.logger.error(f"关键词提取失败: {e}")
            return []
    
    def fallback_summary(self, memories: List[Dict], summary_type: str, date_key: str) -> Dict[str, Any]:
        """
        降级摘要生成
        
        Args:
            memories: 记忆列表
            summary_type: 摘要类型
            date_key: 日期标识
            
        Returns:
            Dict: 降级摘要
        """
        return {
            'method': 'fallback',
            'summary_data': {
                "main_activities": f"{summary_type}摘要生成失败，共有{len(memories)}条记忆",
                "key_topics": ["摘要生成失败"],
                "emotional_state": "未知",
                "learning_growth": "数据处理中",
                "social_interactions": "记录中",
                "future_plans": "待分析",
                "highlights": ["摘要生成失败，请检查系统状态"]
            },
            'confidence': 0.1
        }
    
    def save_summary(self, summary_type: str, date_key: str, summary_content: Dict[str, Any], memories: List[Dict]) -> str:
        """
        保存摘要到数据库
        
        Args:
            summary_type: 摘要类型
            date_key: 日期标识
            summary_content: 摘要内容
            memories: 相关记忆
            
        Returns:
            str: 摘要ID
        """
        try:
            # 构建完整摘要数据
            full_summary = {
                'type': summary_type,
                'date_key': date_key,
                'summary_content': summary_content,
                'memory_count': len(memories),
                'memory_ids': [mem['id'] for mem in memories],
                'generated_at': time.time()
            }
            
            summary_json = json.dumps(full_summary, ensure_ascii=False, indent=2)
            
            # 保存到数据库
            summary_id = f"{summary_type}_{date_key}_{int(time.time())}"
            
            insert_query = """
                INSERT INTO memories (id, content, type, weight, timestamp, session_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            metadata = json.dumps({
                'summary_version': '1.0',
                'generation_method': summary_content.get('method', 'unknown'),
                'confidence': summary_content.get('confidence', 0.0)
            })
            
            self.db_manager.execute_query(
                insert_query,
                (summary_id, summary_json, f'{summary_type}_summary', 
                 self.summary_config['summary_weight'], time.time(), None, metadata)
            )
            
            self.logger.info(f"{summary_type}摘要已保存: {summary_id}")
            return summary_id
            
        except Exception as e:
            self.logger.error(f"保存摘要失败: {e}")
            return ""
    
    def get_existing_summary(self, summary_type: str, date_key: str) -> Optional[Dict[str, Any]]:
        """
        获取现有摘要
        
        Args:
            summary_type: 摘要类型
            date_key: 日期标识
            
        Returns:
            Optional[Dict]: 现有摘要或None
        """
        try:
            query = """
                SELECT content, timestamp 
                FROM memories 
                WHERE type = ?
                AND content LIKE ?
                ORDER BY timestamp DESC 
                LIMIT 1
            """
            
            result = self.db_manager.execute_query(
                query, 
                (f'{summary_type}_summary', f'%"date_key": "{date_key}"%')
            )
            
            if result:
                summary_json = result[0][0]
                return json.loads(summary_json)
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取现有摘要失败: {e}")
            return None
    
    def parse_text_summary(self, response: str) -> Dict[str, Any]:
        """
        解析文本格式的摘要响应
        
        Args:
            response: 文本响应
            
        Returns:
            Dict: 解析后的摘要数据
        """
        # 简单的文本解析逻辑
        return {
            "main_activities": response[:200] if len(response) > 200 else response,
            "key_topics": ["文本解析"],
            "emotional_state": "中性",
            "learning_growth": "基于文本分析",
            "social_interactions": "正常",
            "future_plans": "继续分析",
            "highlights": ["文本摘要生成"]
        }
    
    def schedule_summaries(self) -> Dict[str, Any]:
        """
        执行定期摘要生成
        
        Returns:
            Dict: 执行结果
        """
        try:
            results = {
                'daily_summary': None,
                'weekly_summary': None,
                'execution_time': time.time()
            }
            
            # 生成每日摘要
            try:
                daily_result = self.generate_daily_summary()
                results['daily_summary'] = daily_result
            except Exception as e:
                results['daily_summary'] = {'status': 'error', 'message': str(e)}
            
            # 检查是否需要生成每周摘要（仅周一生成）
            today = datetime.now()
            if today.weekday() == 0:  # 周一
                try:
                    weekly_result = self.generate_weekly_summary()
                    results['weekly_summary'] = weekly_result
                except Exception as e:
                    results['weekly_summary'] = {'status': 'error', 'message': str(e)}
            
            return {
                'success': True,
                'results': results,
                'message': '定期摘要生成完成'
            }
            
        except Exception as e:
            self.logger.error(f"定期摘要执行失败: {e}")
            return {
                'success': False,
                'message': f'执行失败: {str(e)}',
                'execution_time': time.time()
            } 