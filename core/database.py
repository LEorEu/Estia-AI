# core/database.py (V2.0 - 高级管理版)

"""
本模块负责处理记忆的持久化存储。
此版本加入了'weight'和'last_used'字段，为未来的高级记忆管理（如遗忘、加权排序）打下基础。
"""

import sqlite3
import time # 我们将使用 time.time() 来获取Unix时间戳
import os
from config import settings

DB_PATH = os.path.join("assets", "memory.db")

class MemoryDatabase:
    def __init__(self, db_path=DB_PATH):
        """初始化数据库连接，如果表不存在则创建。"""
        print(f"🗄️ 正在连接到高级记忆数据库: {db_path}")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()
        print("✅ 数据库连接成功。")

    def create_table(self):
        """
        创建一个用于存储记忆的表。
        新增了 weight 和 last_used_timestamp 两个关键字段。
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                weight REAL NOT NULL DEFAULT 1.0,
                last_used_timestamp REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def add_entry(self, role: str, content: str, initial_weight: float = 1.0) -> int:
        """
        向数据库中添加一条新的记忆，并记录初始权重和时间。
        """
        current_timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        current_timestamp_unix = time.time() # 使用Unix时间戳，便于计算

        self.cursor.execute(
            "INSERT INTO memories (timestamp, role, content, weight, last_used_timestamp) VALUES (?, ?, ?, ?, ?)",
            (current_timestamp_str, role, content, initial_weight, current_timestamp_unix)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_entry_by_id(self, entry_id: int):
        """根据ID获取一条记忆。"""
        self.cursor.execute("SELECT * FROM memories WHERE id=?", (entry_id,))
        return self.cursor.fetchone()

    def get_all_entries_for_indexing(self):
        """获取数据库中所有的记忆条目，用于建立向量索引。"""
        # 我们只需要ID和内容来建立索引
        self.cursor.execute("SELECT id, content FROM memories")
        return self.cursor.fetchall()

    def update_memory_usage(self, entry_id: int):
        """当一条记忆被成功检索和使用时，更新它的'last_used_timestamp'。"""
        current_timestamp_unix = time.time()
        self.cursor.execute(
            "UPDATE memories SET last_used_timestamp = ? WHERE id = ?",
            (current_timestamp_unix, entry_id)
        )
        self.conn.commit()

    def adjust_weight(self, entry_id: int, delta: float):
        """调整特定记忆的权重。"""
        self.cursor.execute(
            "UPDATE memories SET weight = weight + ? WHERE id = ?",
            (delta, entry_id)
        )
        self.conn.commit()

    def close(self):
        """关闭数据库连接。"""
        self.conn.close()

# 模块独立测试区
if __name__ == '__main__':
    print("\n--- 正在独立测试 database 模块 (V2.0 高级版) ---")
    test_db_path = os.path.join("assets", "test_memory_v2.db")
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = MemoryDatabase(db_path=test_db_path)
    
    print("\n正在添加两条普通记忆...")
    id1 = db.add_entry("user", "今天天气真不错。")
    id2 = db.add_entry("assistant", "是啊，万里无云呢。")
    
    print("\n正在添加一条高权重的核心记忆...")
    id3 = db.add_entry("user", "请记住，我的生日是10月1日。", initial_weight=10.0)

    print(f"\n记忆添加成功，ID分别为: {id1}, {id2}, {id3}")
    
    print("\n模拟一次ID为2的记忆被成功检索...")
    db.update_memory_usage(id2)
    print("更新了ID为2的记忆的 last_used_timestamp。")

    print("\n模拟一次将ID为1的记忆标记为重要...")
    db.adjust_weight(id1, 5.0) # 权重增加5.0
    print("ID为1的记忆权重已增加。")

    print("\n获取所有记忆用于索引：")
    all_memories = db.get_all_entries_for_indexing()
    print(all_memories)

    db.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    print("\n--- 测试完成 ---")