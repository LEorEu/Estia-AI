#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试数据库初始化和基本操作
"""

import os
import sys
import time
import uuid
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入数据库管理器
from core.memory.init.db_manager import DatabaseManager

def test_db_initialization():
    """测试数据库初始化"""
    print("\n===== 测试数据库初始化 =====")
    
    # 使用临时数据库
    test_db_path = os.path.join("assets", "test_memory.db")
    
    # 如果测试数据库已存在，则删除
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"已删除旧的测试数据库: {test_db_path}")
    
    # 创建数据库管理器
    db_manager = DatabaseManager(test_db_path)
    print(f"创建数据库管理器: {test_db_path}")
    
    # 初始化数据库
    success = db_manager.initialize_database()
    print(f"数据库初始化: {'成功' if success else '失败'}")
    
    if not success:
        print("数据库初始化失败，测试终止")
        return False
    
    # 获取表信息
    tables = ["memories", "memory_vectors", "memory_association", "memory_group", "memory_cache"]
    for table in tables:
        info = db_manager.get_table_info(table)
        if info:
            print(f"\n表 {info['table_name']} 结构:")
            for col in info['columns']:
                print(f"  - {col['name']} ({col['type']})")
            print(f"  记录数: {info['record_count']}")
        else:
            print(f"无法获取表 {table} 的信息")
            return False
    
    # 关闭连接
    db_manager.close()
    print("\n数据库初始化测试完成")
    return True

def test_basic_operations():
    """测试基本数据库操作"""
    print("\n===== 测试基本数据库操作 =====")
    
    # 使用临时数据库
    test_db_path = os.path.join("assets", "test_memory.db")
    
    # 创建数据库管理器
    db_manager = DatabaseManager(test_db_path)
    print(f"连接到数据库: {test_db_path}")
    
    # 测试插入记忆
    memory_id = str(uuid.uuid4())
    current_time = time.time()
    
    insert_query = """
    INSERT INTO memories (id, content, type, role, session_id, timestamp, weight, last_accessed, metadata)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    metadata = {
        "source": "test",
        "tags": ["test", "memory"]
    }
    
    params = (
        memory_id,
        "这是一条测试记忆",
        "user_input",
        "user",
        "test_session_001",
        current_time,
        5.0,
        current_time,
        json.dumps(metadata)
    )
    
    success = db_manager.execute_transaction([(insert_query, params)])
    print(f"插入记忆: {'成功' if success else '失败'}")
    
    if not success:
        print("插入记忆失败，测试终止")
        return False
    
    # 测试查询记忆
    select_query = "SELECT * FROM memories WHERE id = ?"
    result = db_manager.execute_query(select_query, (memory_id,))
    
    if result and len(result) > 0:
        memory = dict(result[0])
        print("\n查询到记忆:")
        print(f"  ID: {memory['id']}")
        print(f"  内容: {memory['content']}")
        print(f"  类型: {memory['type']}")
        print(f"  角色: {memory['role']}")
        print(f"  会话ID: {memory['session_id']}")
    else:
        print("查询记忆失败")
        return False
    
    # 测试插入向量
    vector_id = str(uuid.uuid4())
    vector_data = b'\x00\x01\x02\x03' * 32  # 模拟向量数据
    
    insert_vector_query = """
    INSERT INTO memory_vectors (id, memory_id, vector, model_name, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """
    
    vector_params = (
        vector_id,
        memory_id,
        vector_data,
        "test_model",
        current_time
    )
    
    success = db_manager.execute_transaction([(insert_vector_query, vector_params)])
    print(f"插入向量: {'成功' if success else '失败'}")
    
    if not success:
        print("插入向量失败，测试终止")
        return False
    
    # 测试查询向量
    select_vector_query = "SELECT * FROM memory_vectors WHERE memory_id = ?"
    vector_result = db_manager.execute_query(select_vector_query, (memory_id,))
    
    if vector_result and len(vector_result) > 0:
        vector = dict(vector_result[0])
        print("\n查询到向量:")
        print(f"  ID: {vector['id']}")
        print(f"  记忆ID: {vector['memory_id']}")
        print(f"  模型名称: {vector['model_name']}")
        print(f"  向量长度: {len(vector['vector'])} 字节")
    else:
        print("查询向量失败")
        return False
    
    # 获取表记录数
    count_query = "SELECT COUNT(*) FROM memories"
    count_result = db_manager.execute_query(count_query)
    if count_result:
        print(f"\n当前记忆表记录数: {count_result[0][0]}")
    
    # 关闭连接
    db_manager.close()
    print("\n基本数据库操作测试完成")
    return True

def main():
    """主函数"""
    print("开始测试数据库管理器...")
    
    # 测试数据库初始化
    if not test_db_initialization():
        print("数据库初始化测试失败")
        return
    
    # 测试基本操作
    if not test_basic_operations():
        print("基本数据库操作测试失败")
        return
    
    print("\n所有测试完成，数据库管理器工作正常！")

if __name__ == "__main__":
    main() 