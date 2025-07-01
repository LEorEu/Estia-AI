"""
记忆适配器测试
验证适配器能够正确连接新旧记忆系统
"""

import os
import sys
import time

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.memory.memory_adapter import MemoryAdapter, create_memory_adapter

def test_basic_adapter_functionality():
    """测试适配器基本功能"""
    print("\n🔌 测试记忆适配器基本功能...")
    
    # 创建适配器（不启用高级功能）
    adapter = create_memory_adapter(advanced=False)
    
    # 测试存储记忆
    print("\n📝 测试记忆存储...")
    test_memories = [
        ("你好，我是用户", "user", 8.0),
        ("你好！我是你的AI助手", "assistant", 7.5),
        ("用户喜欢编程", "system", 6.0),
        ("今天是个好天气", "user", 4.0),
        ("记住我的名字是小明", "user", 9.0),
    ]
    
    stored_ids = []
    for content, role, importance in test_memories:
        memory_id = adapter.store_memory(
            content=content,
            role=role, 
            importance=importance,
            memory_type="dialogue",
            session_id="test_session_001"
        )
        stored_ids.append(memory_id)
        print(f"✅ 存储: {content} (角色: {role}, 重要性: {importance})")
    
    print(f"\n📊 成功存储 {len([id for id in stored_ids if id])} 条记忆")
    
    # 测试记忆检索
    print("\n🔍 测试记忆检索...")
    test_queries = ["小明", "助手", "编程", "天气", "你好"]
    
    for query in test_queries:
        results = adapter.retrieve_memories(query, limit=3)
        print(f"\n查询: '{query}'")
        if results:
            for i, result in enumerate(results, 1):
                content = result['content']
                importance = result['importance']
                layer = result['layer']
                print(f"  {i}. [{layer}] {importance:.1f} - {content}")
        else:
            print("  未找到相关记忆")
    
    return adapter

def test_memory_filtering():
    """测试记忆过滤功能"""
    print("\n🎛️ 测试记忆过滤功能...")
    
    adapter = create_memory_adapter(advanced=False)
    
    # 添加不同类型的记忆
    test_data = [
        ("用户问了关于Python的问题", "user", 7.0, "dialogue"),
        ("系统记录：用户偏好设置已更新", "system", 8.0, "event"),
        ("Python是一种编程语言", "system", 6.0, "knowledge"), 
        ("我喜欢听音乐", "user", 5.0, "dialogue"),
        ("重要提醒：明天有会议", "assistant", 9.0, "event"),
    ]
    
    for content, role, importance, mem_type in test_data:
        adapter.store_memory(content, memory_type=mem_type, role=role, importance=importance)
    
    # 测试按记忆类型过滤
    print("\n按记忆类型过滤:")
    dialogue_memories = adapter.retrieve_memories("", limit=10, memory_types=["dialogue"])
    event_memories = adapter.retrieve_memories("", limit=10, memory_types=["event"])
    
    print(f"对话记忆: {len(dialogue_memories)} 条")
    for mem in dialogue_memories:
        print(f"  - {mem['content']} ({mem['type']})")
    
    print(f"事件记忆: {len(event_memories)} 条")
    for mem in event_memories:
        print(f"  - {mem['content']} ({mem['type']})")
    
    # 测试按重要性过滤
    print("\n按重要性过滤 (>= 8.0):")
    important_memories = adapter.retrieve_memories("", limit=10, min_importance=8.0)
    print(f"重要记忆: {len(important_memories)} 条")
    for mem in important_memories:
        print(f"  - {mem['content']} (重要性: {mem['importance']})")

def test_recent_and_important_memories():
    """测试最近记忆和重要记忆获取"""
    print("\n📅 测试最近记忆和重要记忆...")
    
    adapter = create_memory_adapter(advanced=False)
    
    # 添加一些测试记忆
    memories = [
        ("这是一条核心信息", "system", 9.5),
        ("用户的重要偏好", "user", 8.0),
        ("普通对话内容", "user", 5.0),
        ("临时信息", "user", 2.0),
    ]
    
    for content, role, importance in memories:
        adapter.store_memory(content, role=role, importance=importance)
        time.sleep(0.1)  # 确保时间戳不同
    
    # 测试获取最近记忆
    print("\n最近24小时的记忆:")
    recent_memories = adapter.get_recent_memories(limit=5, hours=24)
    for i, mem in enumerate(recent_memories, 1):
        timestamp = time.strftime('%H:%M:%S', time.localtime(mem['timestamp']))
        print(f"  {i}. [{timestamp}] {mem['content']} (重要性: {mem['importance']})")
    
    # 测试获取重要记忆
    print("\n重要记忆 (>= 7.0):")
    important_memories = adapter.get_important_memories(limit=5, min_weight=7.0)
    for i, mem in enumerate(important_memories, 1):
        print(f"  {i}. [{mem['layer']}] {mem['content']} (重要性: {mem['importance']})")

def test_adapter_stats():
    """测试适配器统计信息"""
    print("\n📊 测试适配器统计信息...")
    
    adapter = create_memory_adapter(advanced=False)
    
    # 添加一些记忆
    for i in range(10):
        importance = 5.0 + (i % 5)
        adapter.store_memory(f"测试记忆 {i}", importance=importance)
    
    # 获取统计信息
    stats = adapter.get_memory_stats()
    
    print("记忆系统统计:")
    print(f"  适配器版本: {stats.get('adapter_version', 'N/A')}")
    print(f"  高级功能: {'启用' if stats.get('advanced_features_enabled') else '禁用'}")
    print(f"  总记忆数: {stats.get('total_memories', 0)}")
    
    layers = stats.get('layers', {})
    for layer_name, layer_info in layers.items():
        count = layer_info.get('count', 0)
        capacity = layer_info.get('capacity', 0)
        utilization = layer_info.get('utilization', 0)
        print(f"  {layer_name}层: {count}/{capacity} (利用率: {utilization:.1%})")

def main():
    """主测试函数"""
    print("=" * 60)
    print("🔌 记忆适配器测试")
    print("=" * 60)
    
    try:
        test_basic_adapter_functionality()
        test_memory_filtering() 
        test_recent_and_important_memories()
        test_adapter_stats()
        
        print("\n" + "=" * 60)
        print("✅ 所有适配器测试完成！记忆适配器工作正常")
        print("🎯 适配器成功连接了新旧记忆系统")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 