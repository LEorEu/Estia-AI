"""
记忆总结模块 - 将多条相关记忆合并为概括性记忆
"""

import time
import json
import os
from config import settings
from ..dialogue_engine import get_llm_response

# 记忆总结LLM提示
MEMORY_SUMMARIZATION_PROMPT = """
你是一个记忆整合专家。请对以下相关记忆进行整合和总结。
你的任务是创建一个简洁但全面的概括，捕捉这些记忆的核心信息。

记忆列表:
{memories}

请生成一个总结，应包含这些记忆中最重要的信息，尤其是用户的偏好、习惯、背景信息等。
总结应该是一个完整的段落，长度适中，易于理解。
请确保总结忠实于原始记忆内容，不要添加不存在的信息。

总结:
"""

# 主题识别LLM提示
TOPIC_IDENTIFICATION_PROMPT = """
你是一个主题识别专家。请从以下记忆中识别主要主题。
主题应该是一个简短的短语，描述这些记忆的共同点。

记忆列表:
{memories}

请仅返回一个主题短语，不超过5个字，不要有任何其他说明。
"""

class MemorySummarizer:
    """记忆总结器 - 将相关记忆整合为概括性记忆"""
    
    def __init__(self, memory_manager=None, association_network=None):
        """初始化记忆总结器"""
        self.memory_manager = memory_manager  # 记忆管理器
        self.association_network = association_network  # 关联网络
        self.summaries = {}  # 存储已生成的摘要
        self.summary_path = os.path.join(settings.LOG_DIR, "memory/summaries.json")
        os.makedirs(os.path.dirname(self.summary_path), exist_ok=True)
        self._load_summaries()
        
        # 总结配置
        self.min_cluster_size = 3  # 最小需要总结的记忆簇大小
        self.similarity_threshold = 0.6  # 相似度阈值
        self.summarization_interval = 7 * 24 * 3600  # 总结间隔，默认一周
        self.last_summarization = time.time()
    
    def _load_summaries(self):
        """加载已有的摘要"""
        try:
            with open(self.summary_path, "r", encoding="utf-8") as f:
                self.summaries = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.summaries = {}
    
    def _save_summaries(self):
        """保存摘要"""
        with open(self.summary_path, "w", encoding="utf-8") as f:
            json.dump(self.summaries, f, ensure_ascii=False, indent=2)
    
    def generate_memory_summary(self, memory_group):
        """
        使用LLM对一组相关记忆生成概括
        
        参数:
            memory_group: 相关记忆列表
            
        返回:
            概括记忆对象
        """
        if not memory_group or len(memory_group) < 2:
            return None
        
        # 准备记忆文本
        memory_texts = []
        for mem in memory_group:
            role = "用户" if mem.get("role") == "user" else "AI"
            timestamp = mem.get("timestamp", "")
            if isinstance(timestamp, (int, float)):
                import datetime
                timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
            
            memory_texts.append(f"[{timestamp}] {role}: {mem.get('content', '')}")
        
        memories_text = "\n".join(memory_texts)
        
        # 识别记忆主题
        topic = self._identify_topic(memories_text)
        
        # 生成摘要
        prompt = MEMORY_SUMMARIZATION_PROMPT.format(memories=memories_text)
        try:
            summary_text = get_llm_response(prompt, [], personality="你是一个擅长总结的助手")
            
            # 创建摘要记忆
            import hashlib
            # 使用记忆内容和当前时间创建唯一键
            summary_key = hashlib.md5(f"summary_{summary_text}_{time.time()}".encode()).hexdigest()
            
            # 计算综合权重 (使用最高权重)
            max_weight = max([mem.get("weight", 0) for mem in memory_group])
            
            summary_memory = {
                "key": summary_key,
                "content": summary_text,
                "role": "system",
                "type": "summary",
                "topic": topic,
                "source_keys": [mem.get("key") for mem in memory_group if "key" in mem],
                "timestamp": time.time(),
                "weight": max_weight,
                "level": "archival"  # 摘要存储在归档记忆层
            }
            
            # 存储摘要
            self.summaries[summary_key] = summary_memory
            self._save_summaries()
            
            # 添加到记忆系统
            if self.memory_manager:
                self.memory_manager.add_memory(summary_memory, "archival")
            
            # 创建关联
            if self.association_network:
                for mem in memory_group:
                    if "key" in mem:
                        self.association_network.create_association(
                            summary_key,
                            mem["key"],
                            "summarizes",
                            0.9
                        )
            
            return summary_memory
            
        except Exception as e:
            print(f"生成记忆摘要失败: {e}")
            return None
    
    def _identify_topic(self, memories_text):
        """识别记忆组的主题"""
        prompt = TOPIC_IDENTIFICATION_PROMPT.format(memories=memories_text)
        try:
            topic = get_llm_response(prompt, [], personality="你是一个擅长识别主题的助手")
            # 清理主题文本，确保简洁
            topic = topic.strip()
            if len(topic) > 20:  # 如果太长，可能是LLM返回了额外解释
                topic = topic[:20]
            return topic
        except Exception as e:
            print(f"识别主题失败: {e}")
            return "未分类"
    
    def cluster_memories(self, memories, method="topic_based"):
        """
        将记忆聚类为相关组
        
        参数:
            memories: 记忆列表
            method: 聚类方法，可以是 'topic_based', 'time_based', 或 'association_based'
            
        返回:
            记忆簇列表
        """
        if not memories:
            return []
        
        if method == "topic_based":
            return self._cluster_by_topic(memories)
        elif method == "time_based":
            return self._cluster_by_time(memories)
        elif method == "association_based":
            return self._cluster_by_association(memories)
        else:
            # 默认使用主题聚类
            return self._cluster_by_topic(memories)
    
    def _cluster_by_topic(self, memories):
        """按主题聚类记忆"""
        # 提取所有可能的主题
        topics = {}
        for mem in memories:
            content = mem.get("content", "")
            # 简单方法：使用LLM为每条记忆生成主题
            topic = self._get_memory_topic(mem)
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(mem)
        
        # 返回足够大的簇
        clusters = [cluster for topic, cluster in topics.items() if len(cluster) >= self.min_cluster_size]
        return clusters
    
    def _get_memory_topic(self, memory):
        """获取单条记忆的主题"""
        # 如果记忆已有主题，直接使用
        if "topic" in memory:
            return memory["topic"]
        
        # 否则，使用LLM生成主题
        content = memory.get("content", "")
        try:
            topic = get_llm_response(
                f"请用一个简短的短语（不超过5个字）概括以下内容的主题:\n\n{content}\n\n仅返回主题，不要有额外解释。",
                [],
                personality="你是一个擅长识别主题的助手"
            )
            # 清理返回的主题
            topic = topic.strip()
            if len(topic) > 20:
                topic = topic[:20]
            return topic
        except:
            # 如果失败，使用默认主题
            return "未分类"
    
    def _cluster_by_time(self, memories):
        """按时间聚类记忆"""
        # 按天对记忆进行分组
        time_clusters = {}
        for mem in memories:
            timestamp = mem.get("timestamp", 0)
            if isinstance(timestamp, (int, float)):
                import datetime
                # 获取日期部分
                day = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                if day not in time_clusters:
                    time_clusters[day] = []
                time_clusters[day].append(mem)
        
        # 返回足够大的簇
        clusters = [cluster for day, cluster in time_clusters.items() if len(cluster) >= self.min_cluster_size]
        return clusters
    
    def _cluster_by_association(self, memories):
        """按关联网络聚类记忆"""
        if not self.association_network:
            return []
        
        clusters = []
        processed = set()  # 跟踪已处理的记忆
        
        for mem in memories:
            if "key" not in mem or mem["key"] in processed:
                continue
            
            # 获取与此记忆相关的所有记忆
            related_keys = self.association_network.get_related_memories(mem["key"], depth=1)
            if not related_keys:
                continue
            
            # 创建簇
            cluster = [mem]
            for key in related_keys:
                for m in memories:
                    if m.get("key") == key and m not in cluster:
                        cluster.append(m)
            
            # 如果簇足够大，添加到结果
            if len(cluster) >= self.min_cluster_size:
                clusters.append(cluster)
                # 标记所有记忆为已处理
                for m in cluster:
                    if "key" in m:
                        processed.add(m["key"])
        
        return clusters
    
    def schedule_summarization(self, force=False):
        """
        定期执行记忆总结
        
        参数:
            force: 是否强制执行总结，忽略时间间隔
        
        返回:
            生成的摘要数量
        """
        now = time.time()
        if not force and now - self.last_summarization < self.summarization_interval:
            print(f"距离上次记忆总结时间不足，跳过总结")
            return 0
        
        print("开始执行记忆总结...")
        self.last_summarization = now
        
        # 获取所有长期记忆
        memories = self._get_all_memories()
        if not memories:
            print("没有找到需要总结的记忆")
            return 0
        
        # 将记忆聚类
        clusters = self.cluster_memories(memories)
        
        # 为每个簇生成摘要
        summary_count = 0
        for cluster in clusters:
            # 检查是否已经有这个簇的摘要
            cluster_keys = set(mem.get("key", "") for mem in cluster if "key" in mem)
            skip = False
            
            for summary in self.summaries.values():
                source_keys = set(summary.get("source_keys", []))
                # 如果有超过50%的重叠，跳过这个簇
                overlap = len(cluster_keys.intersection(source_keys))
                if overlap > 0 and overlap / len(cluster_keys) > 0.5:
                    skip = True
                    break
            
            if not skip:
                summary = self.generate_memory_summary(cluster)
                if summary:
                    summary_count += 1
        
        print(f"记忆总结完成，生成了{summary_count}条摘要记忆")
        return summary_count
    
    def _get_all_memories(self):
        """获取所有需要总结的记忆"""
        if not self.memory_manager:
            return []
        
        all_memories = []
        
        # 从长期记忆层获取记忆
        if hasattr(self.memory_manager, 'long_term') and hasattr(self.memory_manager.long_term, 'memory'):
            for key, mem in self.memory_manager.long_term.memory.items():
                # 跳过已经是摘要的记忆
                if mem.get("type") != "summary":
                    all_memories.append(mem)
        
        # 从短期记忆层获取记忆
        if hasattr(self.memory_manager, 'short_term') and hasattr(self.memory_manager.short_term, 'memory'):
            all_memories.extend(list(self.memory_manager.short_term.memory))
        
        return all_memories
    
    def get_summary_for_entity(self, entity, limit=1):
        """
        获取与特定实体相关的摘要
        
        参数:
            entity: 实体名称或关键词
            limit: 返回的最大摘要数量
            
        返回:
            相关摘要列表
        """
        relevant_summaries = []
        
        for key, summary in self.summaries.items():
            content = summary.get("content", "")
            topic = summary.get("topic", "")
            
            # 检查实体是否在内容或主题中
            if entity.lower() in content.lower() or entity.lower() in topic.lower():
                relevant_summaries.append(summary)
        
        # 按权重排序
        relevant_summaries.sort(key=lambda x: x.get("weight", 0), reverse=True)
        
        return relevant_summaries[:limit] 