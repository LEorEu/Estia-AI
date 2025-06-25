"""
记忆关联网络 - 建立记忆之间的连接关系
"""

import time
import json
import os
from config import settings

# 关联类型定义
ASSOCIATION_TYPES = [
    "is_related_to",  # 一般关联
    "contradicts",    # 矛盾关系
    "elaborates",     # 详细说明
    "summarizes",     # 概括总结
    "precedes",       # 时间先后
    "causes",         # 因果关系
    "same_topic"      # 同主题
]

class MemoryAssociationNetwork:
    """记忆关联网络 - 管理记忆之间的连接关系"""
    
    def __init__(self):
        """初始化记忆关联网络"""
        self.associations = {}  # 存储所有关联关系
        self.memory_to_associations = {}  # 记忆到关联的映射，用于快速查找
        self.association_path = os.path.join(settings.LOG_DIR, "memory/associations.json")
        os.makedirs(os.path.dirname(self.association_path), exist_ok=True)
        self._load_associations()
        
        # 关联配置
        self.similarity_threshold = 0.65  # 自动建立关联的相似度阈值
        self.decay_rate = 0.05  # 关联强度衰减率
        self.min_strength = 0.2  # 最小关联强度，低于此值的关联会被删除
    
    def _load_associations(self):
        """加载已有关联"""
        try:
            with open(self.association_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.associations = data.get("associations", {})
                self.memory_to_associations = data.get("memory_to_associations", {})
        except (FileNotFoundError, json.JSONDecodeError):
            self.associations = {}
            self.memory_to_associations = {}
    
    def _save_associations(self):
        """保存关联数据"""
        with open(self.association_path, "w", encoding="utf-8") as f:
            json.dump({
                "associations": self.associations,
                "memory_to_associations": self.memory_to_associations
            }, f, ensure_ascii=False, indent=2)
    
    def create_association(self, source_key, target_key, association_type="is_related_to", strength=0.5):
        """
        创建两个记忆之间的关联
        
        参数:
            source_key: 源记忆的键
            target_key: 目标记忆的键
            association_type: 关联类型，必须是ASSOCIATION_TYPES中的一种
            strength: 关联强度，范围0-1
        
        返回:
            关联ID
        """
        if source_key == target_key:
            return None  # 不能与自己建立关联
        
        if association_type not in ASSOCIATION_TYPES:
            raise ValueError(f"关联类型 '{association_type}' 无效，必须是以下之一: {ASSOCIATION_TYPES}")
        
        # 创建唯一的关联ID
        association_id = f"{source_key}_{target_key}_{association_type}"
        
        # 创建关联对象
        association = {
            "id": association_id,
            "source_key": source_key,
            "target_key": target_key,
            "association_type": association_type,
            "strength": max(0.0, min(1.0, strength)),  # 限制在0-1范围内
            "created_at": time.time(),
            "last_activated": time.time()
        }
        
        # 存储关联
        self.associations[association_id] = association
        
        # 更新内存映射
        if source_key not in self.memory_to_associations:
            self.memory_to_associations[source_key] = []
        if target_key not in self.memory_to_associations:
            self.memory_to_associations[target_key] = []
        
        self.memory_to_associations[source_key].append(association_id)
        self.memory_to_associations[target_key].append(association_id)
        
        # 保存更新
        self._save_associations()
        
        return association_id
    
    def get_associations(self, memory_key, association_type=None, direction=None, min_strength=0.0):
        """
        获取与指定记忆相关的所有关联
        
        参数:
            memory_key: 记忆的键
            association_type: 可选，筛选特定类型的关联
            direction: 可选，'outgoing'表示从该记忆出发的关联，'incoming'表示指向该记忆的关联，默认两者都返回
            min_strength: 最小关联强度，低于此值的关联不返回
        
        返回:
            关联列表
        """
        if memory_key not in self.memory_to_associations:
            return []
        
        associations = []
        for assoc_id in self.memory_to_associations[memory_key]:
            if assoc_id in self.associations:
                assoc = self.associations[assoc_id]
                
                # 检查方向
                if direction == "outgoing" and assoc["source_key"] != memory_key:
                    continue
                if direction == "incoming" and assoc["target_key"] != memory_key:
                    continue
                
                # 检查类型
                if association_type and assoc["association_type"] != association_type:
                    continue
                
                # 检查强度
                if assoc["strength"] < min_strength:
                    continue
                
                associations.append(assoc)
        
        return associations
    
    def strengthen_association(self, association_id, increment=0.1):
        """增强关联强度"""
        if association_id in self.associations:
            self.associations[association_id]["strength"] = min(
                1.0, 
                self.associations[association_id]["strength"] + increment
            )
            self.associations[association_id]["last_activated"] = time.time()
            self._save_associations()
            return True
        return False
    
    def weaken_association(self, association_id, decrement=0.1):
        """减弱关联强度"""
        if association_id in self.associations:
            self.associations[association_id]["strength"] = max(
                0.0, 
                self.associations[association_id]["strength"] - decrement
            )
            self._save_associations()
            
            # 如果强度低于阈值，删除关联
            if self.associations[association_id]["strength"] < self.min_strength:
                self.delete_association(association_id)
            
            return True
        return False
    
    def delete_association(self, association_id):
        """删除关联"""
        if association_id in self.associations:
            assoc = self.associations[association_id]
            source_key = assoc["source_key"]
            target_key = assoc["target_key"]
            
            # 从内存映射中移除
            if source_key in self.memory_to_associations and association_id in self.memory_to_associations[source_key]:
                self.memory_to_associations[source_key].remove(association_id)
            
            if target_key in self.memory_to_associations and association_id in self.memory_to_associations[target_key]:
                self.memory_to_associations[target_key].remove(association_id)
            
            # 删除关联
            del self.associations[association_id]
            self._save_associations()
            return True
        return False
    
    def get_related_memories(self, memory_key, depth=1, min_strength=0.3, max_results=10):
        """
        获取与指定记忆相关的记忆，可以递归获取多层关联
        
        参数:
            memory_key: 起始记忆的键
            depth: 递归深度，1表示直接相关，2表示相关的相关，以此类推
            min_strength: 最小关联强度
            max_results: 最大返回结果数
        
        返回:
            相关记忆键的集合
        """
        if depth <= 0:
            return set()
        
        # 获取直接关联的记忆
        direct_assocs = self.get_associations(memory_key, min_strength=min_strength)
        related_keys = set()
        
        for assoc in direct_assocs:
            if assoc["source_key"] == memory_key:
                related_keys.add(assoc["target_key"])
            else:
                related_keys.add(assoc["source_key"])
            
            # 标记关联为最近激活
            assoc["last_activated"] = time.time()
        
        # 如果需要更深层次的关联，递归查找
        if depth > 1:
            indirect_keys = set()
            for key in related_keys:
                # 递归查找下一层关联，深度减1
                next_level = self.get_related_memories(
                    key, 
                    depth=depth-1, 
                    min_strength=min_strength,
                    max_results=max_results
                )
                indirect_keys.update(next_level)
            
            # 合并结果，但排除原始记忆
            related_keys.update(indirect_keys)
            if memory_key in related_keys:
                related_keys.remove(memory_key)
        
        # 限制结果数量
        if len(related_keys) > max_results:
            # 这里可以实现更智能的选择算法，例如按关联强度排序
            # 简单起见，我们直接截断
            related_keys = set(list(related_keys)[:max_results])
        
        self._save_associations()  # 保存激活时间更新
        return related_keys
    
    def auto_associate_memory(self, memory, memory_store, vector_store=None):
        """
        自动为新记忆建立关联
        
        参数:
            memory: 新的记忆对象
            memory_store: 记忆存储对象，用于获取记忆内容
            vector_store: 可选，向量存储对象，用于计算语义相似度
        
        返回:
            创建的关联数量
        """
        if "key" not in memory or "content" not in memory:
            return 0
        
        memory_key = memory["key"]
        content = memory["content"]
        associations_created = 0
        
        # 方法1: 使用向量存储计算语义相似度
        if vector_store:
            try:
                similar_memories = vector_store.similarity_search(content, k=5)
                for sim_mem in similar_memories:
                    sim_key = sim_mem.metadata.get("key")
                    if sim_key and sim_key != memory_key:
                        # 创建关联，强度基于相似度分数
                        sim_score = sim_mem.metadata.get("score", 0.5)
                        if sim_score >= self.similarity_threshold:
                            self.create_association(
                                memory_key, 
                                sim_key, 
                                "is_related_to", 
                                sim_score
                            )
                            associations_created += 1
            except Exception as e:
                print(f"自动关联计算出错: {e}")
        
        # 方法2: 使用简单的关键词匹配
        # 这里可以添加更多的关联判断逻辑
        
        return associations_created
    
    def decay_associations(self, days_threshold=30):
        """
        关联强度随时间衰减
        
        参数:
            days_threshold: 超过多少天未激活的关联会开始衰减
        """
        now = time.time()
        decay_count = 0
        deleted_count = 0
        
        for assoc_id, assoc in list(self.associations.items()):
            last_activated = assoc.get("last_activated", assoc.get("created_at", 0))
            days_inactive = (now - last_activated) / (3600 * 24)
            
            # 超过阈值的关联开始衰减
            if days_inactive > days_threshold:
                # 计算衰减量，时间越长衰减越多
                decay_amount = self.decay_rate * (days_inactive - days_threshold) / 30
                decay_amount = min(decay_amount, 0.5)  # 限制最大衰减量
                
                # 应用衰减
                new_strength = max(0.0, assoc["strength"] - decay_amount)
                if new_strength < self.min_strength:
                    # 强度太低，删除关联
                    self.delete_association(assoc_id)
                    deleted_count += 1
                else:
                    # 更新衰减后的强度
                    assoc["strength"] = new_strength
                    decay_count += 1
        
        if decay_count > 0 or deleted_count > 0:
            self._save_associations()
            print(f"关联衰减完成: {decay_count}条关联强度降低, {deleted_count}条关联被删除")
        
        return decay_count, deleted_count
    
    def get_association_network(self, central_memory_key, depth=2, min_strength=0.3):
        """
        获取以特定记忆为中心的关联网络
        
        参数:
            central_memory_key: 中心记忆的键
            depth: 网络深度
            min_strength: 最小关联强度
        
        返回:
            包含节点和边的网络结构
        """
        # 获取相关记忆
        related_keys = self.get_related_memories(
            central_memory_key, 
            depth=depth, 
            min_strength=min_strength
        )
        related_keys.add(central_memory_key)  # 添加中心记忆
        
        # 构建网络
        network = {
            "nodes": [],
            "edges": []
        }
        
        # 添加节点
        for key in related_keys:
            network["nodes"].append({
                "id": key,
                "type": "memory"
            })
        
        # 添加边
        for source_key in related_keys:
            assocs = self.get_associations(source_key, min_strength=min_strength)
            for assoc in assocs:
                # 只添加网络内的关联
                if assoc["source_key"] in related_keys and assoc["target_key"] in related_keys:
                    network["edges"].append({
                        "source": assoc["source_key"],
                        "target": assoc["target_key"],
                        "type": assoc["association_type"],
                        "strength": assoc["strength"]
                    })
        
        return network 