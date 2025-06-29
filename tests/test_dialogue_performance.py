#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对话性能测试
模拟实际用户对话的响应时间
"""

import os
import sys
import time
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dialogue_response_time():
    """测试对话响应时间"""
    print("🚀 Estia对话性能测试")
    print("模拟实际用户对话的响应时间")
    print("=" * 60)
    
    try:
        # 假设系统已经初始化完成，现在测试单次对话的响应时间
        print("📋 测试场景：系统已初始化，用户发送新对话")
        
        # Step 1: 模拟语音转文本（这里直接用文本）
        user_input = "我今天学习了深度学习，感觉很有收获"
        print(f"👤 用户输入: {user_input}")
        
        # Step 2: 文本向量化（使用已初始化的向量化器）
        print("\n🔍 Step 1: 文本向量化")
        start_time = time.time()
        
        from core.memory.embedding.vectorizer import TextVectorizer
        vectorizer = TextVectorizer(
            model_type="sentence-transformers",
            model_name="Qwen/Qwen3-Embedding-0.6B",
            cache_dir="data/memory/cache",
            use_cache=True
        )
        
        # 向量化用户输入
        query_vector = vectorizer.encode(user_input)
        vectorization_time = time.time() - start_time
        print(f"   ⏱️ 向量化耗时: {vectorization_time*1000:.2f}ms")
        
        # Step 3: FAISS检索相关记忆
        print("\n🔍 Step 2: FAISS向量检索")
        start_time = time.time()
        
        from core.memory.retrieval.faiss_search import FAISSSearchEngine
        search_engine = FAISSSearchEngine(
            index_path="data/vectors/memory_index.bin",
            dimension=1024,
            cache_dir="data/memory/faiss_cache"
        )
        
        # 检索相关记忆
        faiss_results = search_engine.search(query_vector, k=5)
        faiss_time = time.time() - start_time
        print(f"   ⏱️ FAISS检索耗时: {faiss_time*1000:.2f}ms")
        print(f"   📄 找到 {len(faiss_results)} 个相关记忆")
        
        # Step 4: 关联网络拓展
        print("\n🔍 Step 3: 关联网络拓展")
        start_time = time.time()
        
        from core.memory.storage.memory_store import MemoryStore
        memory_store = MemoryStore(
            db_path="assets/memory.db",
            vector_dim=1024,
            model_name="Qwen/Qwen3-Embedding-0.6B"
        )
        
        from core.memory.association.network import AssociationNetwork
        association_network = AssociationNetwork(db_manager=memory_store.db_manager)
        
        # 获取关联记忆
        associated_memories = set()
        for memory_key, similarity in faiss_results:
            try:
                related = association_network.get_related_memories(
                    memory_key, depth=1, min_strength=0.3
                )
                if related:
                    associated_memories.update([r.get('memory_id', r) for r in related])
            except:
                pass
        
        association_time = time.time() - start_time
        print(f"   ⏱️ 关联拓展耗时: {association_time*1000:.2f}ms")
        print(f"   🔗 找到 {len(associated_memories)} 个关联记忆")
        
        # Step 5: 上下文组装
        print("\n🔍 Step 4: 上下文组装")
        start_time = time.time()
        
        # 模拟从数据库获取记忆内容
        primary_memories = [memory_key for memory_key, _ in faiss_results]
        all_memory_keys = list(set(primary_memories + list(associated_memories)))
        
        # 构建上下文
        context_parts = [
            "[系统] 你是Estia，一个具有记忆能力的AI助手。",
            f"[相关记忆] 找到 {len(all_memory_keys)} 条相关记忆。",
            f"[用户] {user_input}",
            "[指令] 基于相关记忆，给出有用的回复。"
        ]
        
        final_context = "\n".join(context_parts)
        context_time = time.time() - start_time
        print(f"   ⏱️ 上下文组装耗时: {context_time*1000:.2f}ms")
        
        # Step 6: 保存新记忆（异步）
        print("\n🔍 Step 5: 保存用户输入")
        start_time = time.time()
        
        # 模拟保存用户输入为新记忆
        memory_id = memory_store.add_memory(
            content=user_input,
            source="user",
            importance=0.7,
            metadata={
                "type": "user_input",
                "timestamp": time.time(),
                "session_id": "test_session"
            }
        )
        
        save_time = time.time() - start_time
        print(f"   ⏱️ 记忆保存耗时: {save_time*1000:.2f}ms")
        
        # 计算总时间
        total_time = vectorization_time + faiss_time + association_time + context_time + save_time
        
        print("\n" + "=" * 60)
        print("📊 对话响应性能分析")
        print("=" * 60)
        
        print(f"🔤 向量化耗时:     {vectorization_time*1000:>8.2f}ms")
        print(f"🔍 FAISS检索耗时:  {faiss_time*1000:>8.2f}ms") 
        print(f"🕸️ 关联拓展耗时:    {association_time*1000:>8.2f}ms")
        print(f"📝 上下文组装耗时:  {context_time*1000:>8.2f}ms")
        print(f"💾 记忆保存耗时:    {save_time*1000:>8.2f}ms")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"⚡ 总响应时间:     {total_time*1000:>8.2f}ms")
        
        # 性能评估
        print(f"\n🎯 性能评估:")
        if total_time < 0.1:
            print("   ✅ 优秀 (<100ms) - 实时响应")
        elif total_time < 0.5:
            print("   ✅ 良好 (<500ms) - 流畅对话")
        elif total_time < 1.0:
            print("   ⚠️ 一般 (<1s) - 可接受延迟")
        else:
            print("   ❌ 较慢 (>1s) - 需要优化")
        
        # 瓶颈分析
        times = {
            "向量化": vectorization_time,
            "FAISS检索": faiss_time,
            "关联拓展": association_time,
            "上下文组装": context_time,
            "记忆保存": save_time
        }
        
        bottleneck = max(times, key=times.get)
        bottleneck_time = times[bottleneck]
        
        print(f"\n🔍 性能瓶颈分析:")
        print(f"   最慢环节: {bottleneck} ({bottleneck_time*1000:.2f}ms)")
        print(f"   占总时间: {bottleneck_time/total_time*100:.1f}%")
        
        # 优化建议
        print(f"\n💡 优化建议:")
        if vectorization_time > 0.05:
            print("   🔤 向量化: 考虑使用更小的模型或增加缓存")
        if faiss_time > 0.02:
            print("   🔍 FAISS: 考虑减少检索数量或使用更快的索引")
        if association_time > 0.05:
            print("   🕸️ 关联: 考虑限制关联深度或使用缓存")
        if save_time > 0.1:
            print("   💾 保存: 考虑异步保存或批量处理")
        
        return total_time
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_multiple_queries():
    """测试多次查询的平均性能"""
    print("\n" + "=" * 60)
    print("🔄 多次查询性能测试")
    print("=" * 60)
    
    test_queries = [
        "今天天气怎么样？",
        "我想学习Python编程",
        "推荐一些好看的电影",
        "工作压力很大怎么办？",
        "深度学习的基础知识"
    ]
    
    times = []
    
    try:
        # 预热系统
        print("🔥 系统预热中...")
        from core.memory.embedding.vectorizer import TextVectorizer
        vectorizer = TextVectorizer(
            model_type="sentence-transformers",
            model_name="Qwen/Qwen3-Embedding-0.6B",
            cache_dir="data/memory/cache",
            use_cache=True
        )
        vectorizer.encode("预热查询")  # 预热
        
        print("📊 开始性能测试...")
        for i, query in enumerate(test_queries, 1):
            start_time = time.time()
            
            # 模拟完整的查询流程
            query_vector = vectorizer.encode(query)
            
            # 这里可以添加更多步骤...
            
            query_time = time.time() - start_time
            times.append(query_time)
            
            print(f"   查询 {i}: {query_time*1000:>6.2f}ms - {query}")
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📈 多查询统计:")
        print(f"   平均响应时间: {avg_time*1000:.2f}ms")
        print(f"   最快响应时间: {min_time*1000:.2f}ms")
        print(f"   最慢响应时间: {max_time*1000:.2f}ms")
        print(f"   响应时间稳定性: {'✅ 稳定' if max_time/min_time < 2 else '⚠️ 不稳定'}")
        
        return avg_time
        
    except Exception as e:
        print(f"❌ 多查询测试失败: {e}")
        return None

def main():
    """主函数"""
    # 单次对话性能测试
    single_time = test_dialogue_response_time()
    
    # 多次查询性能测试
    avg_time = test_multiple_queries()
    
    # 总结
    print("\n" + "=" * 60)
    print("🎯 性能测试总结")
    print("=" * 60)
    
    if single_time and avg_time:
        print(f"单次对话响应时间: {single_time*1000:.2f}ms")
        print(f"平均查询响应时间: {avg_time*1000:.2f}ms")
        
        if single_time < 0.5:
            print("✅ 系统性能良好，可以支持流畅对话")
        else:
            print("⚠️ 系统性能需要优化，响应较慢")
    
    print("\n💡 实际对话中，初始化只需要一次，后续每次对话的响应会更快！")

if __name__ == "__main__":
    main() 