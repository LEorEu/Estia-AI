#!/usr/bin/env python3
"""
事务性双写修复验证测试
验证修复后的事务性双写机制是否正常工作
"""

import os
import sys
import time
import shutil
import unittest

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.memory.storage.memory_store import MemoryStore
from core.memory.init.db_manager import DatabaseManager
from core.memory.init.vector_index import VectorIndexManager

class TransactionFixVerificationTest(unittest.TestCase):
    """事务性双写修复验证测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = "temp/test_transaction_fix"
        os.makedirs(self.test_dir, exist_ok=True)
        
        self.db_path = os.path.join(self.test_dir, "test_memory.db")
        self.index_path = os.path.join(self.test_dir, "test_index.faiss")
        
        # 清理旧文件
        for file_path in [self.db_path, self.index_path, self.index_path + ".meta"]:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # 创建内存存储
        self.memory_store = MemoryStore(
            db_path=self.db_path,
            index_path=self.index_path,
            vector_dim=384
        )
        
        print(f"✅ 测试环境初始化完成")
        print(f"数据库路径: {self.db_path}")
        print(f"索引路径: {self.index_path}")
    
    def tearDown(self):
        """清理测试环境"""
        try:
            if hasattr(self, 'memory_store'):
                self.memory_store.close()
            
            # 清理测试文件
            if os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
        except Exception as e:
            print(f"清理测试环境失败: {e}")
    
    def get_counts(self):
        """获取当前各种计数"""
        try:
            # 获取数据库记录数
            memories_result = self.memory_store.db_manager.query("SELECT COUNT(*) FROM memories")
            memories_count = memories_result[0][0] if memories_result else 0
            
            vectors_result = self.memory_store.db_manager.query("SELECT COUNT(*) FROM memory_vectors")
            vectors_count = vectors_result[0][0] if vectors_result else 0
            
            # 获取FAISS索引计数
            faiss_count = 0
            if self.memory_store.vector_index and self.memory_store.vector_index.available:
                faiss_count = self.memory_store.vector_index.get_total_count()
            
            return {
                "memories": memories_count,
                "vectors": vectors_count,
                "faiss": faiss_count
            }
        except Exception as e:
            print(f"获取计数失败: {e}")
            return {"memories": -1, "vectors": -1, "faiss": -1}
    
    def test_normal_transaction_success(self):
        """测试正常情况下的事务性双写"""
        print("\n🔍 测试1: 正常事务性双写")
        
        # 获取初始计数
        initial_counts = self.get_counts()
        print(f"初始计数: {initial_counts}")
        
        # 添加记忆
        test_content = "这是一个测试记忆内容，用于验证事务性双写机制"
        memory_id = self.memory_store.add_interaction_memory(
            content=test_content,
            memory_type="test",
            role="user",
            session_id="test_session_1",
            timestamp=time.time(),
            weight=5.0
        )
        
        print(f"添加记忆结果: {memory_id}")
        
        # 获取最终计数
        final_counts = self.get_counts()
        print(f"最终计数: {final_counts}")
        
        # 验证结果
        if memory_id:
            self.assertEqual(final_counts["memories"], initial_counts["memories"] + 1)
            self.assertEqual(final_counts["vectors"], initial_counts["vectors"] + 1)
            self.assertEqual(final_counts["faiss"], initial_counts["faiss"] + 1)
            print("✅ 正常事务性双写测试通过")
        else:
            self.fail("❌ 记忆添加失败")
    
    def test_faiss_failure_rollback(self):
        """测试FAISS失败时的回滚机制"""
        print("\n🔍 测试2: FAISS失败回滚机制")
        
        # 获取初始计数
        initial_counts = self.get_counts()
        print(f"初始计数: {initial_counts}")
        
        # 模拟FAISS失败 - 通过破坏向量索引
        original_add_vectors = None
        if self.memory_store.vector_index:
            original_add_vectors = self.memory_store.vector_index.add_vectors
            # 模拟FAISS添加失败
            self.memory_store.vector_index.add_vectors = lambda vectors, ids: False
        
        try:
            # 尝试添加记忆
            test_content = "这是一个用于测试FAISS失败回滚的记忆内容"
            memory_id = self.memory_store.add_interaction_memory(
                content=test_content,
                memory_type="test_rollback",
                role="user",
                session_id="test_session_2",
                timestamp=time.time(),
                weight=5.0
            )
            
            print(f"添加记忆结果: {memory_id}")
            
            # 获取最终计数
            final_counts = self.get_counts()
            print(f"最终计数: {final_counts}")
            
            # 验证回滚是否成功
            if memory_id is None:
                # 确保所有计数都没有变化
                self.assertEqual(final_counts["memories"], initial_counts["memories"])
                self.assertEqual(final_counts["vectors"], initial_counts["vectors"])
                self.assertEqual(final_counts["faiss"], initial_counts["faiss"])
                print("✅ FAISS失败回滚测试通过")
            else:
                self.fail("❌ FAISS失败时应该回滚，但记忆仍然被添加了")
        
        finally:
            # 恢复原始方法
            if original_add_vectors and self.memory_store.vector_index:
                self.memory_store.vector_index.add_vectors = original_add_vectors
    
    def test_database_failure_rollback(self):
        """测试数据库失败时的回滚机制"""
        print("\n🔍 测试3: 数据库失败回滚机制")
        
        # 获取初始计数
        initial_counts = self.get_counts()
        print(f"初始计数: {initial_counts}")
        
        # 模拟数据库失败 - 通过破坏数据库连接
        original_execute_in_transaction = self.memory_store.db_manager.execute_in_transaction
        
        def mock_execute_in_transaction(query, params=None):
            if "memory_vectors" in query:
                # 模拟在插入memory_vectors时失败
                return None
            return original_execute_in_transaction(query, params)
        
        self.memory_store.db_manager.execute_in_transaction = mock_execute_in_transaction
        
        try:
            # 尝试添加记忆
            test_content = "这是一个用于测试数据库失败回滚的记忆内容"
            memory_id = self.memory_store.add_interaction_memory(
                content=test_content,
                memory_type="test_db_rollback",
                role="user",
                session_id="test_session_3",
                timestamp=time.time(),
                weight=5.0
            )
            
            print(f"添加记忆结果: {memory_id}")
            
            # 获取最终计数
            final_counts = self.get_counts()
            print(f"最终计数: {final_counts}")
            
            # 验证回滚是否成功
            if memory_id is None:
                # 确保所有计数都没有变化
                self.assertEqual(final_counts["memories"], initial_counts["memories"])
                self.assertEqual(final_counts["vectors"], initial_counts["vectors"])
                self.assertEqual(final_counts["faiss"], initial_counts["faiss"])
                print("✅ 数据库失败回滚测试通过")
            else:
                self.fail("❌ 数据库失败时应该回滚，但记忆仍然被添加了")
        
        finally:
            # 恢复原始方法
            self.memory_store.db_manager.execute_in_transaction = original_execute_in_transaction
    
    def test_data_consistency_check(self):
        """测试数据一致性检查功能"""
        print("\n🔍 测试4: 数据一致性检查")
        
        # 添加一些正常记忆
        for i in range(3):
            self.memory_store.add_interaction_memory(
                content=f"测试记忆内容 {i+1}",
                memory_type="test",
                role="user",
                session_id="test_session_consistency",
                timestamp=time.time(),
                weight=5.0
            )
        
        # 运行一致性检查
        report = self.memory_store.check_data_consistency()
        print(f"一致性检查报告: {report}")
        
        # 验证报告结构
        self.assertIn("status", report)
        self.assertIn("total_memories", report)
        self.assertIn("total_vectors", report)
        self.assertIn("total_faiss_vectors", report)
        self.assertIn("missing_vectors", report)
        self.assertIn("orphaned_vectors", report)
        self.assertIn("faiss_sync_issues", report)
        
        # 验证数据一致性
        if report["status"] == "healthy":
            self.assertEqual(report["total_memories"], report["total_vectors"])
            self.assertEqual(report["total_vectors"], report["total_faiss_vectors"])
            self.assertEqual(len(report["missing_vectors"]), 0)
            self.assertEqual(len(report["orphaned_vectors"]), 0)
            self.assertEqual(len(report["faiss_sync_issues"]), 0)
            print("✅ 数据一致性检查测试通过")
        else:
            self.fail(f"❌ 数据一致性检查失败，状态: {report['status']}")
    
    def test_batch_operations_consistency(self):
        """测试批量操作的一致性"""
        print("\n🔍 测试5: 批量操作一致性")
        
        # 获取初始计数
        initial_counts = self.get_counts()
        print(f"初始计数: {initial_counts}")
        
        # 批量添加记忆
        batch_size = 5
        successful_adds = 0
        
        for i in range(batch_size):
            memory_id = self.memory_store.add_interaction_memory(
                content=f"批量测试记忆内容 {i+1}",
                memory_type="batch_test",
                role="user",
                session_id="test_session_batch",
                timestamp=time.time() + i,
                weight=5.0
            )
            
            if memory_id:
                successful_adds += 1
                print(f"成功添加记忆 {i+1}: {memory_id}")
        
        # 获取最终计数
        final_counts = self.get_counts()
        print(f"最终计数: {final_counts}")
        
        # 验证一致性
        expected_memories = initial_counts["memories"] + successful_adds
        expected_vectors = initial_counts["vectors"] + successful_adds
        expected_faiss = initial_counts["faiss"] + successful_adds
        
        self.assertEqual(final_counts["memories"], expected_memories)
        self.assertEqual(final_counts["vectors"], expected_vectors)
        self.assertEqual(final_counts["faiss"], expected_faiss)
        
        print(f"✅ 批量操作一致性测试通过 (成功添加 {successful_adds}/{batch_size} 条记忆)")

def main():
    """运行所有测试"""
    print("🚀 开始事务性双写修复验证测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    test_suite.addTest(TransactionFixVerificationTest('test_normal_transaction_success'))
    test_suite.addTest(TransactionFixVerificationTest('test_faiss_failure_rollback'))
    test_suite.addTest(TransactionFixVerificationTest('test_database_failure_rollback'))
    test_suite.addTest(TransactionFixVerificationTest('test_data_consistency_check'))
    test_suite.addTest(TransactionFixVerificationTest('test_batch_operations_consistency'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 所有测试通过！事务性双写修复成功！")
    else:
        print("❌ 有测试失败，需要进一步修复")
        print(f"失败数量: {len(result.failures)}")
        print(f"错误数量: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 