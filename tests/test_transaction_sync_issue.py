#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试数据库与向量索引事务性同步失效问题

这个测试专门验证问题9：数据库与向量索引事务性同步失效
通过模拟各种失败场景来检查数据一致性问题
"""

import os
import sys
import time
import json
import uuid
import sqlite3
import traceback
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_transaction_sync_issues():
    """测试数据库与向量索引的事务性同步问题"""
    print("🔬 测试数据库与向量索引事务性同步问题")
    print("="*60)
    
    # 创建测试数据库
    test_db_path = "assets/test_transaction_sync.db"
    test_index_path = "data/vectors/test_transaction_index.bin"
    
    # 清理旧的测试文件
    for path in [test_db_path, test_index_path, test_index_path + ".meta"]:
        if os.path.exists(path):
            os.remove(path)
    
    try:
        from core.memory.storage.memory_store import MemoryStore
        from core.memory.init.db_manager import DatabaseManager
        
        # 1. 测试正常情况 - 建立基线
        print("\n📋 测试1: 正常情况 - 建立基线")
        memory_store = MemoryStore(
            db_path=test_db_path,
            index_path=test_index_path,
            vector_dim=1024
        )
        
        # 正常添加记忆
        memory_id = memory_store.add_interaction_memory(
            content="测试记忆内容",
            memory_type="user_input", 
            role="user",
            session_id="test_session_1",
            timestamp=time.time(),
            weight=5.0
        )
        
        if memory_id:
            # 检查数据库记录
            db_record = memory_store.db_manager.query(
                "SELECT id FROM memories WHERE id = ?", [memory_id]
            )
            
            # 检查向量记录
            vector_record = memory_store.db_manager.query(
                "SELECT memory_id FROM memory_vectors WHERE memory_id = ?", [memory_id]
            )
            
            print(f"   ✅ 正常情况: 数据库记录={len(db_record)}, 向量记录={len(vector_record)}")
            assert len(db_record) == 1, "数据库记录应该存在"
            assert len(vector_record) == 1, "向量记录应该存在"
        else:
            print("   ❌ 正常情况失败：无法添加记忆")
            
    except Exception as e:
        print(f"   ❌ 正常情况测试失败: {e}")
    
    # 2. 测试向量索引写入失败的情况
    print("\n🚨 测试2: 模拟向量索引写入失败")
    
    try:
        # 重新创建memory_store以避免状态污染
        memory_store = MemoryStore(
            db_path=test_db_path,
            index_path=test_index_path,
            vector_dim=1024
        )
        
        # 备份原始的向量索引方法
        original_add_vectors = None
        if memory_store.vector_index:
            original_add_vectors = memory_store.vector_index.add_vectors
        
        # Mock向量索引的add_vectors方法使其失败
        def mock_add_vectors_fail(*args, **kwargs):
            raise Exception("模拟向量索引写入失败")
        
        if memory_store.vector_index:
            memory_store.vector_index.add_vectors = mock_add_vectors_fail
        
        # 获取添加前的数据库记录数
        db_count_before = memory_store.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
        vector_count_before = memory_store.db_manager.query("SELECT COUNT(*) FROM memory_vectors")[0][0]
        
        print(f"   📊 添加前: 数据库记录={db_count_before}, 向量记录={vector_count_before}")
        
        # 尝试添加记忆（应该失败）
        memory_id = None
        try:
            memory_id = memory_store.add_interaction_memory(
                content="测试向量索引失败",
                memory_type="user_input",
                role="user", 
                session_id="test_session_2",
                timestamp=time.time(),
                weight=5.0
            )
        except Exception as e:
            print(f"   ⚠️ 预期的失败: {e}")
        
        # 检查数据库状态
        db_count_after = memory_store.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
        vector_count_after = memory_store.db_manager.query("SELECT COUNT(*) FROM memory_vectors")[0][0]
        
        print(f"   📊 添加后: 数据库记录={db_count_after}, 向量记录={vector_count_after}")
        
        # 分析结果
        db_increased = db_count_after > db_count_before
        vector_increased = vector_count_after > vector_count_before
        
        if db_increased and not vector_increased:
            print("   🚨 发现事务性问题！数据库记录增加了，但向量记录没有增加")
            print("   💡 这证明了缺少事务性保证的问题")
        elif not db_increased and not vector_increased:
            print("   ✅ 良好：两边都没有增加记录")
        else:
            print(f"   ❓ 意外情况: 数据库增加={db_increased}, 向量增加={vector_increased}")
        
        # 恢复原始方法
        if memory_store.vector_index and original_add_vectors:
            memory_store.vector_index.add_vectors = original_add_vectors
            
    except Exception as e:
        print(f"   ❌ 向量索引失败测试出错: {e}")
        traceback.print_exc()
    
    # 3. 测试数据库写入失败的情况
    print("\n🚨 测试3: 模拟数据库写入失败")
    
    try:
        memory_store = MemoryStore(
            db_path=test_db_path,
            index_path=test_index_path,
            vector_dim=1024
        )
        
        # 备份原始的execute_query方法
        original_execute_query = memory_store.db_manager.execute_query
        
        # Mock数据库的execute_query方法使其在INSERT时失败
        def mock_execute_query_fail(query, params=None):
            if query and "INSERT INTO memories" in query:
                raise Exception("模拟数据库写入失败")
            return original_execute_query(query, params)
        
        memory_store.db_manager.execute_query = mock_execute_query_fail
        
        # 获取添加前的记录数
        db_count_before = original_execute_query("SELECT COUNT(*) FROM memories")[0][0]
        vector_count_before = original_execute_query("SELECT COUNT(*) FROM memory_vectors")[0][0]
        
        print(f"   📊 添加前: 数据库记录={db_count_before}, 向量记录={vector_count_before}")
        
        # 尝试添加记忆（应该失败）
        memory_id = None
        try:
            memory_id = memory_store.add_interaction_memory(
                content="测试数据库写入失败",
                memory_type="user_input",
                role="user",
                session_id="test_session_3", 
                timestamp=time.time(),
                weight=5.0
            )
        except Exception as e:
            print(f"   ⚠️ 预期的失败: {e}")
        
        # 恢复原始方法检查状态
        memory_store.db_manager.execute_query = original_execute_query
        
        db_count_after = memory_store.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
        vector_count_after = memory_store.db_manager.query("SELECT COUNT(*) FROM memory_vectors")[0][0]
        
        print(f"   📊 添加后: 数据库记录={db_count_after}, 向量记录={vector_count_after}")
        
        if db_count_after == db_count_before and vector_count_after == vector_count_before:
            print("   ✅ 良好：数据库失败时，向量索引也没有增加")
        else:
            print("   🚨 潜在问题：数据库失败但向量索引可能有变化")
            
    except Exception as e:
        print(f"   ❌ 数据库失败测试出错: {e}")
        traceback.print_exc()
    
    # 4. 检查当前实现的事务性
    print("\n🔍 测试4: 分析当前实现的事务性机制")
    
    try:
        # 读取memory_store.py的源码来分析事务性
        memory_store_path = "core/memory/storage/memory_store.py"
        if os.path.exists(memory_store_path):
            with open(memory_store_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键事务性特征
            has_transaction = "begin_transaction" in content or "BEGIN TRANSACTION" in content
            has_commit = "commit" in content or "COMMIT" in content  
            has_rollback = "rollback" in content or "ROLLBACK" in content
            has_try_except = "try:" in content and "except" in content
            
            print(f"   📋 事务性特征分析:")
            print(f"      - 包含事务开始: {has_transaction}")
            print(f"      - 包含提交机制: {has_commit}")
            print(f"      - 包含回滚机制: {has_rollback}")
            print(f"      - 包含异常处理: {has_try_except}")
            
            if not (has_transaction and has_commit and has_rollback):
                print("   🚨 缺少完整的事务性机制！")
            else:
                print("   ✅ 具备基本的事务性机制")
                
        else:
            print(f"   ❌ 找不到源文件: {memory_store_path}")
            
    except Exception as e:
        print(f"   ❌ 事务性分析失败: {e}")
    
    # 5. 数据一致性检查
    print("\n🔍 测试5: 数据一致性检查")
    
    try:
        memory_store = MemoryStore(
            db_path=test_db_path,
            index_path=test_index_path,
            vector_dim=1024
        )
        
        # 检查memories表和memory_vectors表的一致性
        memories_count = memory_store.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
        vectors_count = memory_store.db_manager.query("SELECT COUNT(*) FROM memory_vectors")[0][0]
        
        print(f"   📊 数据一致性检查:")
        print(f"      - memories表记录数: {memories_count}")
        print(f"      - memory_vectors表记录数: {vectors_count}")
        
        if memories_count == vectors_count:
            print("   ✅ 数据库表之间保持一致")
        else:
            print(f"   🚨 数据不一致！差异: {abs(memories_count - vectors_count)} 条记录")
        
        # 检查FAISS索引
        if memory_store.vector_index and hasattr(memory_store.vector_index, 'index'):
            faiss_count = memory_store.vector_index.index.ntotal
            print(f"      - FAISS索引记录数: {faiss_count}")
            
            if faiss_count == memories_count:
                print("   ✅ FAISS索引与数据库保持一致")
            else:
                print(f"   🚨 FAISS索引不一致！差异: {abs(faiss_count - memories_count)} 条记录")
        else:
            print("   ⚠️ FAISS索引未初始化或不可用")
        
        # 查找孤儿记录
        orphan_vectors = memory_store.db_manager.query("""
            SELECT memory_id FROM memory_vectors 
            WHERE memory_id NOT IN (SELECT id FROM memories)
        """)
        
        orphan_memories = memory_store.db_manager.query("""
            SELECT id FROM memories 
            WHERE id NOT IN (SELECT memory_id FROM memory_vectors)
        """)
        
        if orphan_vectors:
            print(f"   🚨 发现{len(orphan_vectors)}个孤儿向量记录（有向量但无记忆）")
        
        if orphan_memories:
            print(f"   🚨 发现{len(orphan_memories)}个孤儿记忆记录（有记忆但无向量）")
        
        if not orphan_vectors and not orphan_memories:
            print("   ✅ 未发现孤儿记录")
            
    except Exception as e:
        print(f"   ❌ 数据一致性检查失败: {e}")
        traceback.print_exc()
    
    # 6. 并发写入测试
    print("\n🔄 测试6: 并发写入场景")
    
    try:
        import threading
        import concurrent.futures
        
        memory_store = MemoryStore(
            db_path=test_db_path,
            index_path=test_index_path,
            vector_dim=1024
        )
        
        def add_memory_worker(worker_id):
            """工作线程：添加记忆"""
            try:
                memory_id = memory_store.add_interaction_memory(
                    content=f"并发测试记忆 {worker_id}",
                    memory_type="user_input",
                    role="user",
                    session_id=f"concurrent_session_{worker_id}",
                    timestamp=time.time(),
                    weight=5.0
                )
                return f"Worker {worker_id}: {'成功' if memory_id else '失败'}"
            except Exception as e:
                return f"Worker {worker_id}: 异常 - {e}"
        
        # 获取并发前的记录数
        before_count = memory_store.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
        
        # 启动5个并发线程
        workers = 5
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(add_memory_worker, i) for i in range(workers)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # 检查并发后的记录数
        after_count = memory_store.db_manager.query("SELECT COUNT(*) FROM memories")[0][0]
        
        print(f"   📊 并发写入结果:")
        print(f"      - 写入前记录数: {before_count}")
        print(f"      - 写入后记录数: {after_count}")
        print(f"      - 预期增加: {workers}, 实际增加: {after_count - before_count}")
        
        for result in results:
            print(f"      - {result}")
        
        if after_count - before_count == workers:
            print("   ✅ 并发写入成功，无数据丢失")
        else:
            print("   🚨 并发写入存在问题，可能有数据丢失或冲突")
            
    except Exception as e:
        print(f"   ❌ 并发写入测试失败: {e}")
        traceback.print_exc()
    
    # 清理测试文件
    print("\n🧹 清理测试文件")
    try:
        for path in [test_db_path, test_index_path, test_index_path + ".meta"]:
            if os.path.exists(path):
                os.remove(path)
                print(f"   ✅ 删除: {path}")
    except Exception as e:
        print(f"   ⚠️ 清理失败: {e}")
    
    print("\n" + "="*60)
    print("🎯 测试总结:")
    print("1. 如果发现'数据库记录增加了，但向量记录没有增加'，说明存在事务性问题")
    print("2. 如果发现孤儿记录，说明数据一致性有问题") 
    print("3. 如果并发写入有数据丢失，说明缺少适当的锁机制")
    print("4. 建议实现事务性双写和失败回滚机制")

def test_proposed_solution():
    """测试建议的事务性解决方案"""
    print("\n🔧 测试建议的事务性解决方案")
    print("="*60)
    
    # 这里可以测试修复后的实现
    print("💡 建议的解决方案特征:")
    print("1. 使用数据库事务包装整个写入过程")
    print("2. 在向量索引失败时回滚数据库操作")
    print("3. 添加数据一致性验证")
    print("4. 实现失败重试机制")
    print("5. 添加并发写入的锁保护")

if __name__ == "__main__":
    test_transaction_sync_issues()
    test_proposed_solution() 