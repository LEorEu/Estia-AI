"""
记忆层级模块 - 实现多层记忆系统
包括核心记忆、归档记忆、长期记忆和短期记忆
"""

import json
import os
import time
import hashlib
from collections import deque
from config import settings

# 配置参数，应从settings中读取或设置合理默认值
CORE_MEMORY_PATH = os.path.join(settings.LOG_DIR, "memory/core_memory.json")
ARCHIVAL_MEMORY_PATH = os.path.join(settings.LOG_DIR, "memory/archival_memory.json")
SHORT_TERM_MEMORY_SIZE = 50  # 短期记忆容量

class BaseMemory:
    """记忆基类，提供通用方法"""
    
    def _get_key(self, content):
        """生成记忆唯一键值"""
        text = content.get("content", "")
        role = content.get("role", "unknown")
        timestamp = content.get("timestamp", str(time.time()))
        return hashlib.md5(f"{role}:{text}:{timestamp}".encode()).hexdigest()
    
    def _similar_to(self, query, text, threshold=0.5):
        """简单的文本相似度检查，可替换为向量相似度"""
        # 这里仅作示例，实际应该使用向量相似度
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        if not query_words or not text_words:
            return False
        intersection = query_words.intersection(text_words)
        return len(intersection) / max(len(query_words), 1) >= threshold

class CoreMemory(BaseMemory):
    """核心记忆 - 存储最重要的信息，永不遗忘"""
    
    def __init__(self):
        self.memory = {}
        self._ensure_dir()
        self._load()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(CORE_MEMORY_PATH), exist_ok=True)
    
    def _load(self):
        """加载记忆"""
        try:
            with open(CORE_MEMORY_PATH, "r", encoding="utf-8") as f:
                self.memory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.memory = {}
    
    def _save(self):
        """保存记忆"""
        with open(CORE_MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def add(self, content):
        """添加核心记忆"""
        key = self._get_key(content)
        self.memory[key] = {
            **content,
            "level": "core",
            "weight": 10.0,  # 核心记忆权重固定为最高
            "last_accessed": time.time()
        }
        self._save()
        return key
    
    def retrieve(self, query, limit=5):
        """检索核心记忆"""
        results = []
        for key, item in self.memory.items():
            content = item.get("content", "")
            if query.lower() in content.lower() or self._similar_to(query, content):
                results.append(item)
                # 更新访问时间
                self.memory[key]["last_accessed"] = time.time()
        
        # 按权重排序并限制结果数量
        results = sorted(results, key=lambda x: x.get("weight", 0), reverse=True)[:limit]
        if results:
            self._save()  # 保存更新的访问时间
        return results

class ArchivalMemory(BaseMemory):
    """归档记忆 - 存储重要事件和背景信息"""
    
    def __init__(self):
        self.memory = {}
        self._ensure_dir()
        self._load()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(ARCHIVAL_MEMORY_PATH), exist_ok=True)
    
    def _load(self):
        """加载记忆"""
        try:
            with open(ARCHIVAL_MEMORY_PATH, "r", encoding="utf-8") as f:
                self.memory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.memory = {}
    
    def _save(self):
        """保存记忆"""
        with open(ARCHIVAL_MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def add(self, content):
        """添加归档记忆"""
        key = self._get_key(content)
        self.memory[key] = {
            **content,
            "level": "archival",
            "weight": 8.0,  # 归档记忆初始权重较高
            "last_accessed": time.time()
        }
        self._save()
        return key
    
    def retrieve(self, query, limit=5):
        """检索归档记忆"""
        results = []
        for key, item in self.memory.items():
            content = item.get("content", "")
            if query.lower() in content.lower() or self._similar_to(query, content):
                results.append(item)
                # 更新访问时间
                self.memory[key]["last_accessed"] = time.time()
        
        # 按权重排序并限制结果数量
        results = sorted(results, key=lambda x: x.get("weight", 0), reverse=True)[:limit]
        if results:
            self._save()  # 保存更新的访问时间
        return results

class LongTermMemory(BaseMemory):
    """长期记忆 - 使用向量数据库存储"""
    
    def __init__(self, vector_store=None):
        self.vector_store = vector_store  # 这里应该传入实际的向量存储对象
        self.memory = {}  # 本地缓存，用于存储元数据
        self._load_metadata()
    
    def _load_metadata(self):
        """加载记忆元数据"""
        import os
        from config import settings
        
        metadata_path = os.path.join(settings.LOG_DIR, "memory/long_term_metadata.json")
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                import json
                self.memory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.memory = {}
    
    def _save_metadata(self):
        """保存记忆元数据"""
        import os
        import json
        from config import settings
        
        metadata_path = os.path.join(settings.LOG_DIR, "memory/long_term_metadata.json")
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def add(self, content):
        """添加到长期记忆"""
        key = self._get_key(content)
        
        # 更新元数据
        self.memory[key] = {
            **content,
            "level": "long_term",
            "last_accessed": time.time(),
            "access_count": 0
        }
        self._save_metadata()
        
        # 添加到向量存储
        if self.vector_store and "content" in content:
            try:
                # 如果向量存储支持add_texts方法
                if hasattr(self.vector_store, 'add_texts'):
                    metadata = {
                        "role": content.get("role", "unknown"),
                        "timestamp": content.get("timestamp", str(time.time())),
                        "key": key,
                        "level": "long_term",
                        "weight": content.get("weight", 5.0)
                    }
                    self.vector_store.add_texts(
                        [content["content"]], 
                        metadatas=[metadata]
                    )
                # 如果向量存储支持自定义的add方法
                elif hasattr(self.vector_store, 'add'):
                    self.vector_store.add(content["content"], key)
            except Exception as e:
                print(f"⚠️ 向量存储添加失败: {e}")
        
        return key
    
    def retrieve(self, query, limit=5):
        """从长期记忆检索"""
        results = []
        
        # 从向量存储中检索
        if self.vector_store:
            try:
                # 如果向量存储支持similarity_search方法
                if hasattr(self.vector_store, 'similarity_search'):
                    docs = self.vector_store.similarity_search(query, k=limit)
                    for doc in docs:
                        content = doc.page_content
                        metadata = doc.metadata
                        key = metadata.get("key", self._get_key({"content": content}))
                        
                        # 更新元数据
                        if key in self.memory:
                            self.memory[key]["last_accessed"] = time.time()
                            self.memory[key]["access_count"] = self.memory[key].get("access_count", 0) + 1
                        
                        results.append({
                            "content": content,
                            "role": metadata.get("role", "unknown"),
                            "timestamp": metadata.get("timestamp", ""),
                            "level": "long_term",
                            "weight": metadata.get("weight", 5.0),
                            "key": key,
                            "last_accessed": time.time()
                        })
                
                # 如果向量存储支持自定义的search方法
                elif hasattr(self.vector_store, 'search'):
                    items = self.vector_store.search(query, limit)
                    for item in items:
                        # 假设item是(content, key, score)形式的元组
                        if isinstance(item, tuple) and len(item) >= 2:
                            content, key = item[0], item[1]
                            
                            # 更新元数据
                            if key in self.memory:
                                self.memory[key]["last_accessed"] = time.time()
                                self.memory[key]["access_count"] = self.memory[key].get("access_count", 0) + 1
                                
                                results.append(self.memory[key])
            
            except Exception as e:
                print(f"⚠️ 向量存储检索失败: {e}")
        
        # 保存更新的元数据
        if results:
            self._save_metadata()
        
        return results

class ShortTermMemory(BaseMemory):
    """短期记忆 - 基于队列的临时存储"""
    
    def __init__(self):
        self.memory = deque(maxlen=SHORT_TERM_MEMORY_SIZE)
    
    def add(self, content):
        """添加到短期记忆"""
        key = self._get_key(content)
        item = {
            **content,
            "key": key,
            "level": "short_term",
            "weight": 3.0,  # 短期记忆初始权重较低
            "timestamp": content.get("timestamp", time.time())
        }
        self.memory.append(item)
        return key
    
    def retrieve(self, query, limit=5):
        """从短期记忆检索"""
        results = []
        for item in self.memory:
            content = item.get("content", "")
            if query.lower() in content.lower() or self._similar_to(query, content):
                results.append(item)
        
        # 按权重和时间排序
        results = sorted(
            results, 
            key=lambda x: (x.get("weight", 0), x.get("timestamp", 0)), 
            reverse=True
        )[:limit]
        
        return results

class MemoryManager:
    """记忆管理器 - 统一管理所有记忆层"""
    
    def __init__(self, vector_store=None):
        # 初始化记忆层
        self.core = CoreMemory()
        self.archival = ArchivalMemory()
        self.long_term = LongTermMemory(vector_store)
        self.short_term = ShortTermMemory()
        self.last_consolidation = time.time()
        self.last_decay = time.time()
        
        # 记忆管理配置
        self.consolidation_interval = 3600 * 24  # 默认每24小时巩固一次
        self.decay_interval = 3600 * 24 * 7      # 默认每7天衰减一次
        self.similarity_threshold = 0.75         # 相似度阈值，用于去重
        
        # 高级记忆功能
        from .memory_association import MemoryAssociationNetwork
        from .memory_conflict import MemoryConflictDetector
        from .memory_summarizer import MemorySummarizer
        
        # 初始化高级功能模块
        self.association_network = MemoryAssociationNetwork()
        self.conflict_detector = MemoryConflictDetector(self, self.association_network)
        self.summarizer = MemorySummarizer(self, self.association_network)
    
    def add_memory(self, content, level=None):
        """添加记忆到指定层或自动分层"""
        # 检查新记忆是否与现有记忆冲突
        conflicts = self.conflict_detector.detect_conflicts_for_new_memory(content)
        if conflicts:
            print(f"📢 检测到 {len(conflicts)} 个记忆冲突并自动解决")
        
        # 1. 添加记忆到相应层级
        if level == "core":
            memory_key = self.core.add(content)
        elif level == "archival":
            memory_key = self.archival.add(content)
        elif level == "long_term":
            memory_key = self.long_term.add(content)
        elif level == "short_term":
            memory_key = self.short_term.add(content)
        else:
            # 自动分层逻辑
            weight = content.get("weight", 0)
            if weight >= 9.0:
                memory_key = self.core.add(content)
                level = "core"
            elif weight >= 7.0:
                memory_key = self.archival.add(content)
                level = "archival"
            elif weight >= 5.0:
                memory_key = self.long_term.add(content)
                level = "long_term"
            else:
                memory_key = self.short_term.add(content)
                level = "short_term"
        
        # 2. 自动建立关联
        if memory_key and hasattr(content, 'get') and content.get('content'):
            memory_with_key = dict(content)
            memory_with_key['key'] = memory_key
            self.association_network.auto_associate_memory(memory_with_key, self, self.long_term.vector_store)
        
        # 3. 如果是重要记忆，提前尝试总结
        if level in ["core", "archival"] or (level == "long_term" and content.get("weight", 0) >= 6.0):
            # 只对重要记忆触发即时总结，提高系统响应性
            if hasattr(content, 'get') and content.get('content'):
                # 查找相关记忆
                related_keys = self.association_network.get_related_memories(memory_key, depth=1)
                if len(related_keys) >= 2:  # 至少需要3条记忆才总结(新记忆+至少2条相关)
                    related_memories = []
                    for key in related_keys:
                        mem = self._get_memory_by_key(key)
                        if mem:
                            related_memories.append(mem)
                    
                    # 如果有足够的相关记忆，生成总结
                    if len(related_memories) >= 2:
                        all_memories = [memory_with_key] + related_memories
                        self.summarizer.generate_memory_summary(all_memories)
        
        return memory_key
    
    def _get_memory_by_key(self, key):
        """根据键获取记忆，在所有层级中查找"""
        # 检查核心记忆
        if hasattr(self.core, 'memory') and key in self.core.memory:
            return self.core.memory[key]
            
        # 检查归档记忆
        if hasattr(self.archival, 'memory') and key in self.archival.memory:
            return self.archival.memory[key]
            
        # 检查长期记忆
        if hasattr(self.long_term, 'memory') and key in self.long_term.memory:
            return self.long_term.memory[key]
            
        # 检查短期记忆
        if hasattr(self.short_term, 'memory'):
            for mem in self.short_term.memory:
                if mem.get("key") == key:
                    return mem
        
        return None
    
    def retrieve_memory(self, query, limit=5, parallel=True, include_associations=True, check_conflicts=True):
        """从所有记忆层检索并合并结果，支持关联和冲突检测"""
        # 1. 基本检索
        if parallel:
            raw_results = self._retrieve_memory_parallel(query, limit)
        else:
            raw_results = self._retrieve_memory_sequential(query, limit)
        
        # 2. 应用冲突检测
        if check_conflicts:
            results = self.conflict_detector.get_conflict_aware_memories(raw_results)
        else:
            results = raw_results
        
        # 3. 添加关联记忆
        if include_associations and results:
            # 从检索结果中找出权重最高的记忆
            primary_result = max(results, key=lambda x: x.get("weight", 0))
            if "key" in primary_result:
                # 获取关联记忆
                related_keys = self.association_network.get_related_memories(
                    primary_result["key"], 
                    depth=1, 
                    min_strength=0.5
                )
                
                # 检索关联记忆内容
                related_memories = []
                for key in related_keys:
                    memory = self._get_memory_by_key(key)
                    if memory and memory not in results:
                        # 标记为关联记忆
                        memory["is_associated"] = True
                        memory["association_source"] = primary_result.get("key", "")
                        related_memories.append(memory)
                
                # 按权重排序关联记忆
                related_memories.sort(key=lambda x: x.get("weight", 0), reverse=True)
                
                # 添加最相关的记忆（最多limit/2个）
                addition_limit = max(1, limit // 2)
                results.extend(related_memories[:addition_limit])
                
                # 4. 检查是否有相关摘要
                if hasattr(self.summarizer, 'get_summary_for_entity'):
                    # 尝试从主要结果内容中提取实体
                    entities = self.conflict_detector.extract_entities(primary_result.get("content", ""))
                    for entity in entities:
                        entity_value = entity.get("value", "")
                        if entity_value:
                            summaries = self.summarizer.get_summary_for_entity(entity_value, limit=1)
                            for summary in summaries:
                                if summary not in results:
                                    summary["is_summary"] = True
                                    results.append(summary)
                                    break  # 只添加一个最相关的摘要
        
        # 最终排序和限制结果数
        final_results = sorted(results, key=lambda x: x.get("weight", 0), reverse=True)
        return final_results[:limit]
    
    def _retrieve_memory_parallel(self, query, limit=5):
        """并行从所有记忆层检索"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        # 定义线程函数
        def retrieve_from_layer(layer_name, retriever, query, limit):
            try:
                results = retriever.retrieve(query, limit)
                # 给结果添加来源标记
                for item in results:
                    if "level" not in item:
                        item["level"] = layer_name
                results_queue.put(results)
            except Exception as e:
                print(f"⚠️ 从{layer_name}检索时出错: {e}")
                results_queue.put([])
        
        # 创建并启动所有检索线程
        threads = []
        layers = [
            ("core", self.core),
            ("archival", self.archival), 
            ("long_term", self.long_term),
            ("short_term", self.short_term)
        ]
        
        for layer_name, layer in layers:
            thread = threading.Thread(
                target=retrieve_from_layer,
                args=(layer_name, layer, query, limit)
            )
            thread.start()
            threads.append(thread)
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 收集所有结果
        all_results = []
        while not results_queue.empty():
            layer_results = results_queue.get()
            all_results.extend(layer_results)
        
        # 去重、排序并限制结果数量
        return self._process_retrieved_results(all_results, query, limit)
    
    def _retrieve_memory_sequential(self, query, limit=5):
        """按顺序从所有记忆层检索"""
        # 从各层获取结果
        core_results = self.core.retrieve(query, limit)
        archival_results = self.archival.retrieve(query, limit)
        long_term_results = self.long_term.retrieve(query, limit)
        short_term_results = self.short_term.retrieve(query, limit)
        
        # 合并所有结果
        all_results = core_results + archival_results + long_term_results + short_term_results
        
        # 去重、排序并限制结果数量
        return self._process_retrieved_results(all_results, query, limit)
    
    def _process_retrieved_results(self, all_results, query, limit=5):
        """处理检索结果：去重、排序和筛选"""
        # 1. 去重（基于内容）
        unique_results = {}
        for item in all_results:
            content = item.get("content", "")
            # 如果内容已存在且新的权重更高，替换
            if content not in unique_results or item.get("weight", 0) > unique_results[content].get("weight", 0):
                unique_results[content] = item
                
                # 记录访问次数
                item["access_count"] = item.get("access_count", 0) + 1
                
                # 更新最后访问时间
                item["last_accessed"] = time.time()
        
        results_list = list(unique_results.values())
        
        # 2. 基于多种因素为结果评分
        scored_results = []
        for item in results_list:
            # 初始分数就是记忆权重
            score = item.get("weight", 1.0)
            
            # 内容相关性加分
            content = item.get("content", "").lower()
            query_terms = query.lower().split()
            
            # 计算查询词在内容中出现的次数
            term_matches = sum(1 for term in query_terms if term in content)
            relevance_score = term_matches / max(1, len(query_terms))
            score += relevance_score * 2  # 相关性权重
            
            # 长度适中的内容加分
            content_length = len(content)
            if 20 <= content_length <= 200:
                score += 0.5  # 适中长度加分
            
            # 记忆层级加权
            level_weights = {
                "core": 3.0,
                "archival": 2.0,
                "long_term": 1.0,
                "short_term": 0.5
            }
            level = item.get("level", "short_term")
            score += level_weights.get(level, 0)
            
            # 最近访问加分（时间衰减）
            last_accessed = item.get("last_accessed", 0)
            days_since_access = (time.time() - last_accessed) / (3600 * 24)
            recency_score = 1.0 / (1 + days_since_access)
            score += recency_score
            
            # 添加到评分结果
            scored_results.append((score, item))
        
        # 3. 按最终评分排序
        sorted_results = [item for _, item in sorted(scored_results, key=lambda x: x[0], reverse=True)]
        
        # 4. 限制返回结果数量
        return sorted_results[:limit]
    
    def consolidate_memories(self):
        """执行多种记忆维护任务：巩固、衰减、关联维护和总结"""
        print("🧠 开始全面记忆维护...")
        
        # 1. 执行基础的短期→长期记忆巩固
        print("🧠 开始记忆巩固流程...")
        
        # 检查间隔时间
        now = time.time()
        if now - self.last_consolidation < self.consolidation_interval:
            print(f"⏱️ 距离上次巩固间隔不足，跳过本次巩固")
            return
            
        self.last_consolidation = now
        consolidated_count = 0
        
        # 提取短期记忆中需要巩固的项目
        to_consolidate = []
        for item in list(self.short_term.memory):
            # 权重高的短期记忆转为长期记忆
            if item.get("weight", 0) >= 5.0:
                to_consolidate.append(item)
                consolidated_count += 1
            
            # 频繁访问的短期记忆也转为长期记忆
            elif item.get("access_count", 0) >= 3:
                item["weight"] = max(item.get("weight", 0), 5.0)  # 提升权重
                to_consolidate.append(item)
                consolidated_count += 1
        
        # 将需要巩固的记忆转移到长期记忆
        for item in to_consolidate:
            self.long_term.add(item)
            print(f"📝 巩固记忆: {item.get('content', '')[:30]}...")
        
        print(f"✅ 记忆巩固完成，共处理 {consolidated_count} 条记忆")
        
        # 2. 触发记忆衰减流程
        if now - self.last_decay >= self.decay_interval:
            self.decay_memories()
        
        # 3. 维护关联网络
        if hasattr(self.association_network, 'decay_associations'):
            print("🔄 维护记忆关联网络...")
            decay_count, deleted_count = self.association_network.decay_associations()
            print(f"✅ 关联网络维护完成: {decay_count}条关联衰减, {deleted_count}条关联删除")
        
        # 4. 执行记忆总结
        if hasattr(self.summarizer, 'schedule_summarization'):
            print("📋 执行记忆总结...")
            summary_count = self.summarizer.schedule_summarization()
            print(f"✅ 记忆总结完成: 生成了{summary_count}条摘要记忆")
        
        print("🧠 全面记忆维护完成!")
    
    def decay_memories(self):
        """记忆衰减：随时间降低记忆权重，可能导致遗忘"""
        print("🧠 开始记忆衰减流程...")
        self.last_decay = time.time()
        
        # 1. 长期记忆衰减
        decayed_count = 0
        forgotten_count = 0
        
        # 这里假设长期记忆有一个字典结构
        if hasattr(self.long_term, 'memory') and isinstance(self.long_term.memory, dict):
            for key, item in list(self.long_term.memory.items()):
                # 计算衰减因子：上次访问越久远，衰减越明显
                last_accessed = item.get("last_accessed", 0)
                days_since_access = (time.time() - last_accessed) / (3600 * 24)
                decay_factor = 0.05 * days_since_access  # 每天衰减5%
                
                # 核心记忆和标记为重要的记忆不衰减
                if item.get("level") == "core" or item.get("important", False):
                    continue
                    
                # 应用权重衰减
                original_weight = item.get("weight", 5.0)
                new_weight = max(1.0, original_weight - decay_factor)
                
                if new_weight < 3.0:  # 权重低于阈值，考虑遗忘
                    # 检查是否有频繁访问，频繁访问的不遗忘
                    if item.get("access_count", 0) < 2:
                        del self.long_term.memory[key]
                        forgotten_count += 1
                        continue
                
                # 更新权重
                if new_weight != original_weight:
                    self.long_term.memory[key]["weight"] = new_weight
                    decayed_count += 1
        
        print(f"✅ 记忆衰减完成，衰减 {decayed_count} 条记忆，遗忘 {forgotten_count} 条记忆")
    
    def deduplicate_memories(self):
        """去除冗余记忆：合并相似的记忆项"""
        print("🧠 开始记忆去重流程...")
        
        # 这里需要依赖向量存储实现，简单示例
        if not hasattr(self.long_term, 'vector_store') or not self.long_term.vector_store:
            print("⚠️ 缺少向量存储，无法执行去重")
            return
        
        # 实际去重逻辑需要根据您的向量存储实现方式调整
        print("✅ 记忆去重完成")
    
    def mark_important(self, memory_key, level="long_term"):
        """将特定记忆标记为重要，防止遗忘"""
        if level == "long_term" and hasattr(self.long_term, 'memory'):
            if memory_key in self.long_term.memory:
                self.long_term.memory[memory_key]["important"] = True
                self.long_term.memory[memory_key]["weight"] = 9.0  # 提升权重
                print(f"🔒 已将记忆标记为重要: {memory_key}")
                return True
        
        elif level == "archival":
            if memory_key in self.archival.memory:
                self.archival.memory[memory_key]["important"] = True
                print(f"🔒 已将归档记忆标记为重要: {memory_key}")
                return True
        
        return False 