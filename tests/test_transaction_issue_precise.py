#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
精确测试数据库与向量索引事务性同步失效问题
验证FAISS索引失败时数据库不回滚的具体问题
"""

import os
import sys
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_precise_transaction_issue():
    """精确测试事务性同步问题"""
    print("🎯 精确测试数据库与FAISS索引事务性问题")
    print("="*60)
    
    # 创建干净的测试环境
    test_db_path = "assets/test_precise_transaction.db"
    test_index_path = "data/vectors/test_precise_index.bin"
    
    # 清理旧文件
    for path in [test_db_path, test_index_path, test_index_path + ".meta"]:
        if os.path.exists(path):
            os.remove(path)
    
    try:
        from core.memory.storage.memory_store import MemoryStore
        
        # 创建MemoryStore实例
        memory_store = MemoryStore(
            db_path=test_db_path,
            index_path=test_index_path,
            vector_dim=1024
        )
        
        print("\n📊 测试1: 验证正常情况")
        
        # 正常添加一条记忆
        memory_id1 = memory_store.add_interaction_memory(
            content="正常测试记忆",
            memory_type="user_input",
            role="user",
            session_id="test_session",
            timestamp=time.time(),
            weight=5.0
        )
        
        # 检查初始状态
        memories_count = memory_store.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
        vectors_count = memory_store.db_manager.query("SELECT COUNT(*) FROM memory_vectors")[0][0]
        faiss_count = memory_store.vector_index.index.ntotal if memory_store.vector_index else 0
        
        print(f"   📋 正常添加后:")
        print(f"      - memories表: {memories_count}")
        print(f"      - memory_vectors表: {vectors_count}")
        print(f"      - FAISS索引: {faiss_count}")
        
        print("\n🚨 测试2: 模拟FAISS save_index失败")
        
        # 备份原始方法
        original_save_index = memory_store.vector_index.save_index if memory_store.vector_index else None
        
        # Mock save_index方法使其失败
        def mock_save_index_fail():
            raise Exception("模拟FAISS保存失败")
        
        if memory_store.vector_index:
            memory_store.vector_index.save_index = mock_save_index_fail
        
        # 尝试添加第二条记忆
        print("   🔄 尝试添加记忆（FAISS保存会失败）...")
        
        memory_id2 = memory_store.add_interaction_memory(
            content="FAISS保存失败测试",
            memory_type="user_input", 
            role="user",
            session_id="test_session_2",
            timestamp=time.time(),
            weight=5.0
        )
        
        # 检查添加后的状态
        memories_count_after = memory_store.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
        vectors_count_after = memory_store.db_manager.query("SELECT COUNT(*) FROM memory_vectors")[0][0]
        faiss_count_after = memory_store.vector_index.index.ntotal if memory_store.vector_index else 0
        
        print(f"   📋 FAISS保存失败后:")
        print(f"      - memories表: {memories_count} → {memories_count_after} (增加{memories_count_after - memories_count})")
        print(f"      - memory_vectors表: {vectors_count} → {vectors_count_after} (增加{vectors_count_after - vectors_count})")
        print(f"      - FAISS索引: {faiss_count} → {faiss_count_after} (增加{faiss_count_after - faiss_count})")
        
        # 分析结果
        db_increased = memories_count_after > memories_count
        vector_db_increased = vectors_count_after > vectors_count
        faiss_increased = faiss_count_after > faiss_count
        
        print(f"\n   🔍 结果分析:")
        print(f"      - 数据库memories增加: {db_increased}")
        print(f"      - 数据库vectors增加: {vector_db_increased}")
        print(f"      - FAISS索引增加: {faiss_increased}")
        print(f"      - 返回的memory_id: {'成功' if memory_id2 else '失败'}")
        
        if db_increased and vector_db_increased and not faiss_increased:
            print("   🚨 发现事务性问题！")
            print("      数据库记录增加了，但FAISS索引没有更新")
            print("      这证明了缺少事务性回滚机制")
        elif not db_increased and not vector_db_increased and not faiss_increased:
            print("   ✅ 良好：所有操作都回滚了")
        else:
            print("   ❓ 意外情况，需要进一步分析")
        
        # 恢复原始方法
        if memory_store.vector_index and original_save_index:
            memory_store.vector_index.save_index = original_save_index
        
        print("\n🚨 测试3: 模拟FAISS add_vectors失败")
        
        # 备份原始方法
        original_add_vectors = memory_store.vector_index.add_vectors if memory_store.vector_index else None
        
        # Mock add_vectors方法使其失败
        def mock_add_vectors_fail(*args, **kwargs):
            raise Exception("模拟FAISS添加向量失败")
        
        if memory_store.vector_index:
            memory_store.vector_index.add_vectors = mock_add_vectors_fail
        
        # 记录添加前的状态
        memories_before = memory_store.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
        vectors_before = memory_store.db_manager.query("SELECT COUNT(*) FROM memory_vectors")[0][0]
        faiss_before = memory_store.vector_index.index.ntotal if memory_store.vector_index else 0
        
        print("   🔄 尝试添加记忆（FAISS添加向量会失败）...")
        
        # 尝试添加第三条记忆
        memory_id3 = memory_store.add_interaction_memory(
            content="FAISS添加向量失败测试",
            memory_type="user_input",
            role="user", 
            session_id="test_session_3",
            timestamp=time.time(),
            weight=5.0
        )
        
        # 检查添加后的状态
        memories_after = memory_store.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
        vectors_after = memory_store.db_manager.query("SELECT COUNT(*) FROM memory_vectors")[0][0]
        faiss_after = memory_store.vector_index.index.ntotal if memory_store.vector_index else 0
        
        print(f"   📋 FAISS添加向量失败后:")
        print(f"      - memories表: {memories_before} → {memories_after} (增加{memories_after - memories_before})")
        print(f"      - memory_vectors表: {vectors_before} → {vectors_after} (增加{vectors_after - vectors_before})")
        print(f"      - FAISS索引: {faiss_before} → {faiss_after} (增加{faiss_after - faiss_before})")
        print(f"      - 返回的memory_id: {'成功' if memory_id3 else '失败'}")
        
        # 关键分析
        if (memories_after > memories_before) and (vectors_after > vectors_before) and (faiss_after == faiss_before):
            print("   🚨 再次发现事务性问题！")
            print("      数据库操作成功，但FAISS索引失败，且没有回滚")
            return True  # 确认问题存在
        
        # 恢复原始方法
        if memory_store.vector_index and original_add_vectors:
            memory_store.vector_index.add_vectors = original_add_vectors
        
        print("\n🔍 测试4: 检查当前数据一致性")
        
        # 最终一致性检查
        final_memories = memory_store.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
        final_vectors = memory_store.db_manager.query("SELECT COUNT(*) FROM memory_vectors")[0][0]
        final_faiss = memory_store.vector_index.index.ntotal if memory_store.vector_index else 0
        
        print(f"   📊 最终状态:")
        print(f"      - memories表: {final_memories}")
        print(f"      - memory_vectors表: {final_vectors}")
        print(f"      - FAISS索引: {final_faiss}")
        
        inconsistency_found = (final_memories != final_faiss) or (final_vectors != final_faiss)
        
        if inconsistency_found:
            print("   🚨 确认数据不一致问题！")
            print(f"      差异: memories与FAISS相差{abs(final_memories - final_faiss)}")
        else:
            print("   ✅ 数据保持一致")
        
        return inconsistency_found
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理测试文件
        print("\n🧹 清理测试文件")
        for path in [test_db_path, test_index_path, test_index_path + ".meta"]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"   ✅ 删除: {path}")
                except:
                    print(f"   ⚠️ 删除失败: {path}")

def main():
    print("🔬 精确测试数据库与向量索引事务性同步问题")
    
    has_issue = test_precise_transaction_issue()
    
    print("\n" + "="*60)
    print("🎯 测试结论:")
    
    if has_issue:
        print("🚨 确认存在事务性同步问题！")
        print("\n💡 问题描述:")
        print("1. 数据库写入成功，但FAISS索引操作失败")
        print("2. 系统没有回滚数据库操作")
        print("3. 导致数据库与索引不一致")
        print("\n🔧 建议解决方案:")
        print("1. 使用数据库事务包装整个操作")
        print("2. FAISS操作失败时回滚数据库事务")
        print("3. 添加数据一致性验证机制")
    else:
        print("✅ 未发现明显的事务性问题")
        print("💡 可能系统已有适当的错误处理机制")

if __name__ == "__main__":
    main() 