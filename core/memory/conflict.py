"""
记忆冲突检测与解决模块 - 识别和处理矛盾的记忆
"""

import time
import re
from ..dialogue_engine import get_llm_response

# 冲突类型定义
CONFLICT_TYPES = [
    "factual",       # 事实性冲突 (如"我住在北京" vs "我住在上海")
    "preference",    # 偏好冲突 (如"我喜欢咖啡" vs "我不喜欢咖啡")
    "temporal",      # 时间性冲突 (可能是正常变化，如"我明天有会议" vs "我明天没安排")
    "uncertain"      # 不确定冲突
]

# 实体类型定义
ENTITY_TYPES = [
    "person",        # 人物
    "location",      # 地点
    "organization",  # 组织
    "time",          # 时间
    "preference",    # 偏好
    "activity",      # 活动
    "object",        # 物品
    "attribute"      # 属性
]

# 实体提取的LLM提示
ENTITY_EXTRACTION_PROMPT = """
你是一个实体提取专家。请从以下文本中提取关键实体和信息。
注意提取用户的个人信息、偏好、活动、地点、时间等。
输出格式应为JSON，包含实体类型和值。例如:
{
  "entities": [
    {"type": "person", "value": "张三"},
    {"type": "location", "value": "北京"},
    {"type": "preference", "value": "喜欢咖啡"},
    {"type": "time", "value": "明天下午"}
  ]
}

文本: {text}

仅返回JSON格式的结果，不要有任何其他说明。
"""

# 冲突检测的LLM提示
CONFLICT_DETECTION_PROMPT = """
你是一个矛盾检测专家。请分析以下两段文本，判断它们是否存在矛盾或不一致。
如果存在矛盾，请确定矛盾类型和具体矛盾内容。

文本1 ({time1}): {text1}
文本2 ({time2}): {text2}

矛盾类型可以是:
- factual: 事实性矛盾，如地点、身份等客观事实的冲突
- preference: 偏好矛盾，如喜好、兴趣等主观偏好的变化
- temporal: 时间性变化，如计划、安排等随时间正常变化的内容
- uncertain: 不确定是否矛盾

请按以下JSON格式返回结果:
{
  "is_conflict": true/false,
  "conflict_type": "factual/preference/temporal/uncertain",
  "conflict_description": "简要描述矛盾内容",
  "entity": "矛盾涉及的实体或主题"
}

仅返回JSON格式的结果，不要有任何其他说明。
"""

class MemoryConflictDetector:
    """记忆冲突检测与解决"""
    
    def __init__(self, memory_manager=None, association_network=None):
        """初始化冲突检测器"""
        self.memory_manager = memory_manager  # 记忆管理器实例
        self.association_network = association_network  # 关联网络实例
        self.conflict_history = []  # 记录已检测的冲突
        
    def extract_entities(self, text):
        """从文本中提取实体"""
        prompt = ENTITY_EXTRACTION_PROMPT.format(text=text)
        try:
            response = get_llm_response(prompt, [], personality="")
            # 尝试解析返回的JSON
            import json
            try:
                # 寻找JSON部分
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                    return data.get("entities", [])
                else:
                    data = json.loads(response)
                    return data.get("entities", [])
            except json.JSONDecodeError:
                print(f"无法解析实体提取结果: {response}")
                return []
        except Exception as e:
            print(f"实体提取失败: {e}")
            return []
    
    def detect_conflict(self, memory1, memory2):
        """检测两条记忆之间是否存在冲突"""
        # 检查输入有效性
        if not memory1 or not memory2 or "content" not in memory1 or "content" not in memory2:
            return None
        
        # 准备时间信息
        time1 = memory1.get("timestamp", "未知时间")
        time2 = memory2.get("timestamp", "未知时间")
        
        # 格式化时间
        if isinstance(time1, (int, float)):
            import datetime
            time1 = datetime.datetime.fromtimestamp(time1).strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(time2, (int, float)):
            import datetime
            time2 = datetime.datetime.fromtimestamp(time2).strftime('%Y-%m-%d %H:%M:%S')
        
        # 构建提示
        prompt = CONFLICT_DETECTION_PROMPT.format(
            text1=memory1["content"],
            text2=memory2["content"],
            time1=time1,
            time2=time2
        )
        
        # 调用LLM进行冲突检测
        try:
            response = get_llm_response(prompt, [], personality="")
            
            # 解析结果
            import json
            try:
                # 寻找JSON部分
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                else:
                    result = json.loads(response)
                
                if result.get("is_conflict", False):
                    # 记录冲突
                    conflict = {
                        "memory1_key": memory1.get("key", ""),
                        "memory2_key": memory2.get("key", ""),
                        "memory1_content": memory1["content"],
                        "memory2_content": memory2["content"],
                        "memory1_time": time1,
                        "memory2_time": time2,
                        "conflict_type": result.get("conflict_type", "uncertain"),
                        "conflict_description": result.get("conflict_description", ""),
                        "entity": result.get("entity", ""),
                        "detected_at": time.time(),
                        "resolved": False
                    }
                    self.conflict_history.append(conflict)
                    return conflict
                
                return None  # 没有冲突
                
            except json.JSONDecodeError:
                print(f"无法解析冲突检测结果: {response}")
                return None
                
        except Exception as e:
            print(f"冲突检测失败: {e}")
            return None
    
    def search_conflicts_by_entity(self, entity_value, entity_type=None):
        """搜索涉及特定实体的冲突"""
        conflicts = []
        for conflict in self.conflict_history:
            if entity_value.lower() in conflict.get("entity", "").lower():
                if entity_type is None or entity_type == conflict.get("entity_type"):
                    conflicts.append(conflict)
        return conflicts
    
    def detect_conflicts_for_new_memory(self, new_memory):
        """检测新记忆与现有记忆之间的潜在冲突"""
        if not new_memory or "content" not in new_memory:
            return []
        
        # 1. 提取实体
        entities = self.extract_entities(new_memory["content"])
        detected_conflicts = []
        
        # 2. 对每个实体，查找相关记忆
        for entity in entities:
            entity_type = entity.get("type")
            entity_value = entity.get("value")
            
            # 只对特定类型的实体进行冲突检测
            if entity_type not in ["location", "preference", "activity"]:
                continue
            
            # 3. 查找包含该实体的记忆
            related_memories = self._find_memories_by_entity(entity_value)
            
            # 4. 与每条相关记忆进行冲突检测
            for related_memory in related_memories:
                # 跳过自身
                if related_memory.get("key") == new_memory.get("key"):
                    continue
                    
                # 检测冲突
                conflict = self.detect_conflict(new_memory, related_memory)
                if conflict:
                    # 如果检测到冲突，尝试解决
                    self.resolve_conflict(conflict)
                    detected_conflicts.append(conflict)
        
        return detected_conflicts
    
    def _find_memories_by_entity(self, entity_value):
        """查找包含特定实体的记忆"""
        if not self.memory_manager:
            return []
            
        # 使用内存管理器的检索功能
        # 这里假设memory_manager有一个search方法
        if hasattr(self.memory_manager, 'retrieve_memory'):
            return self.memory_manager.retrieve_memory(entity_value, limit=10, parallel=True)
        
        return []
    
    def resolve_conflict(self, conflict):
        """解决检测到的冲突"""
        if not conflict or conflict.get("resolved", False):
            return False
            
        # 获取冲突记忆
        memory1_key = conflict.get("memory1_key")
        memory2_key = conflict.get("memory2_key")
        
        # 确定哪个记忆更新
        memory1_time = conflict.get("memory1_time", "")
        memory2_time = conflict.get("memory2_time", "")
        
        # 转换时间为可比较格式
        import datetime
        try:
            if isinstance(memory1_time, str):
                memory1_time = datetime.datetime.strptime(memory1_time, '%Y-%m-%d %H:%M:%S').timestamp()
            if isinstance(memory2_time, str):
                memory2_time = datetime.datetime.strptime(memory2_time, '%Y-%m-%d %H:%M:%S').timestamp()
        except:
            # 如果转换失败，使用字符串比较
            newer_memory_key = memory2_key if str(memory2_time) > str(memory1_time) else memory1_key
            older_memory_key = memory1_key if newer_memory_key == memory2_key else memory2_key
        else:
            # 如果成功转换为时间戳，使用数值比较
            newer_memory_key = memory2_key if float(memory2_time) > float(memory1_time) else memory1_key
            older_memory_key = memory1_key if newer_memory_key == memory2_key else memory2_key
        
        # 获取冲突类型
        conflict_type = conflict.get("conflict_type", "uncertain")
        
        # 根据冲突类型应用不同的解决策略
        if conflict_type == "factual":
            # 对于事实性冲突，优先采信较新的记忆
            self._update_memory_status(older_memory_key, "superseded", 0.5)
            self._update_memory_status(newer_memory_key, "current", 1.5)
            
            # 建立冲突关联
            if self.association_network:
                self.association_network.create_association(
                    newer_memory_key, 
                    older_memory_key, 
                    "contradicts", 
                    1.0
                )
            
        elif conflict_type == "preference":
            # 对于偏好冲突，也优先新信息，但保留旧信息作为历史参考
            self._update_memory_context(
                older_memory_key, 
                f"过去的偏好，在{conflict.get('memory2_time', '未知时间')}发生变化"
            )
            self._update_memory_context(
                newer_memory_key, 
                f"当前偏好，从{conflict.get('memory2_time', '未知时间')}开始"
            )
            
            # 建立关联
            if self.association_network:
                self.association_network.create_association(
                    newer_memory_key,
                    older_memory_key,
                    "precedes",
                    0.8
                )
            
        elif conflict_type == "temporal":
            # 时间性冲突通常是自然变化，记录变化但不降权
            self._update_memory_context(
                older_memory_key,
                f"历史安排，在{conflict.get('memory2_time', '未知时间')}更新"
            )
            
            # 建立时间序列关联
            if self.association_network:
                self.association_network.create_association(
                    newer_memory_key,
                    older_memory_key,
                    "precedes",
                    0.7
                )
        
        # 标记冲突为已解决
        conflict["resolved"] = True
        conflict["resolution_time"] = time.time()
        
        return True
    
    def _update_memory_status(self, memory_key, status, weight_multiplier=1.0):
        """更新记忆状态和权重"""
        if not self.memory_manager or not hasattr(self.memory_manager, 'long_term'):
            return False
            
        # 假设memory_manager的long_term记忆层有memory字典
        memory_store = getattr(self.memory_manager.long_term, 'memory', {})
        if memory_key in memory_store:
            memory_store[memory_key]["status"] = status
            memory_store[memory_key]["weight"] = memory_store[memory_key].get("weight", 1.0) * weight_multiplier
            return True
            
        return False
    
    def _update_memory_context(self, memory_key, context):
        """更新记忆上下文信息"""
        if not self.memory_manager or not hasattr(self.memory_manager, 'long_term'):
            return False
            
        # 假设memory_manager的long_term记忆层有memory字典
        memory_store = getattr(self.memory_manager.long_term, 'memory', {})
        if memory_key in memory_store:
            memory_store[memory_key]["context"] = context
            return True
            
        return False
    
    def get_conflict_aware_memories(self, results):
        """处理检索结果，考虑已解决的冲突"""
        processed_results = []
        
        for result in results:
            result_key = result.get("key", "")
            
            # 检查这条记忆是否参与了冲突
            is_superseded = False
            context_update = None
            
            for conflict in self.conflict_history:
                if conflict.get("resolved", False):
                    if result_key == conflict.get("memory1_key") or result_key == conflict.get("memory2_key"):
                        # 确定此记忆在冲突中的角色
                        if conflict.get("conflict_type") == "factual":
                            # 如果是已被替代的事实，标记为过时
                            memory_store = getattr(self.memory_manager.long_term, 'memory', {})
                            if result_key in memory_store and memory_store[result_key].get("status") == "superseded":
                                is_superseded = True
                                
                                # 找到替代它的记忆
                                other_key = conflict.get("memory2_key") if result_key == conflict.get("memory1_key") else conflict.get("memory1_key")
                                context_update = f"此信息已被更新，请参考更新的信息: {memory_store.get(other_key, {}).get('content', '')}"
                        
                        # 如果有上下文更新，添加到结果中
                        if not context_update:
                            memory_store = getattr(self.memory_manager.long_term, 'memory', {})
                            if result_key in memory_store and "context" in memory_store[result_key]:
                                context_update = memory_store[result_key]["context"]
            
            # 根据冲突状态处理结果
            if is_superseded:
                # 对于被替代的记忆，降低其权重但仍然保留
                result["weight"] = result.get("weight", 1.0) * 0.3
                result["status"] = "superseded"
            
            if context_update:
                result["context"] = context_update
            
            processed_results.append(result)
        
        # 按权重重新排序
        processed_results.sort(key=lambda x: x.get("weight", 0), reverse=True)
        
        return processed_results 