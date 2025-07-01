#!/usr/bin/env python3
"""
简化数据库架构 - 只保留实际使用的字段和表
"""

import os
import sqlite3
import logging
import time
from pathlib import Path

def create_simplified_database(db_path="assets/memory_simplified.db"):
    """创建简化的数据库架构"""
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"🗄️ 创建简化数据库: {db_path}")
    
    try:
        # 1. 简化的记忆主表 - 只保留必要字段
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'memory',
                role TEXT NOT NULL DEFAULT 'user',
                timestamp REAL NOT NULL,
                weight REAL DEFAULT 1.0,
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
        # 为主表创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_weight ON memories(weight)')
        
        print("✅ 创建memories表（简化版）")
        
        # 2. 向量存储表 - 保持不变，这个是必需的
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_vectors (
                id TEXT PRIMARY KEY,
                memory_id TEXT NOT NULL,
                vector BLOB NOT NULL,
                model_name TEXT NOT NULL,
                timestamp REAL NOT NULL,
                FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_vectors_memory_id ON memory_vectors(memory_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_vectors_model ON memory_vectors(model_name)')
        
        print("✅ 创建memory_vectors表")
        
        # 3. 简化的关联表 - 移除冗余字段
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_associations (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                association_type TEXT NOT NULL DEFAULT 'related',
                strength REAL NOT NULL DEFAULT 0.5,
                created_at REAL NOT NULL,
                FOREIGN KEY (source_id) REFERENCES memories(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES memories(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_associations_source ON memory_associations(source_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_associations_target ON memory_associations(target_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_associations_strength ON memory_associations(strength)')
        
        print("✅ 创建memory_associations表（简化版）")
        
        # 提交更改
        conn.commit()
        
        # 显示表信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📊 数据库架构总结:")
        print(f"   • 数据库文件: {db_path}")
        print(f"   • 表数量: {len(tables)}")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"   • {table_name}: {len(columns)}个字段")
            for col in columns:
                print(f"     - {col[1]} ({col[2]})")
        
        print(f"\n🎯 简化对比:")
        print(f"   • 原架构: 5个表，40+字段")
        print(f"   • 简化版: 3个表，18个字段")
        print(f"   • 减少: ~55%的复杂度")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def migrate_from_old_db(old_db_path="assets/memory.db", new_db_path="assets/memory_simplified.db"):
    """从旧数据库迁移数据到新的简化数据库"""
    
    if not os.path.exists(old_db_path):
        print(f"⚠️ 旧数据库不存在: {old_db_path}")
        return False
    
    print(f"🔄 开始数据迁移...")
    print(f"   源数据库: {old_db_path}")
    print(f"   目标数据库: {new_db_path}")
    
    try:
        # 连接两个数据库
        old_conn = sqlite3.connect(old_db_path)
        old_cursor = old_conn.cursor()
        
        new_conn = sqlite3.connect(new_db_path)
        new_cursor = new_conn.cursor()
        
        # 迁移memories表
        old_cursor.execute("""
            SELECT id, content, type, role, timestamp, weight, metadata
            FROM memories
        """)
        
        memories = old_cursor.fetchall()
        
        for memory in memories:
            new_cursor.execute("""
                INSERT OR REPLACE INTO memories 
                (id, content, type, role, timestamp, weight, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, memory)
        
        print(f"✅ 迁移 {len(memories)} 条记忆")
        
        # 迁移向量表
        try:
            old_cursor.execute("SELECT id, memory_id, vector, model_name, timestamp FROM memory_vectors")
            vectors = old_cursor.fetchall()
            
            for vector in vectors:
                new_cursor.execute("""
                    INSERT OR REPLACE INTO memory_vectors 
                    (id, memory_id, vector, model_name, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, vector)
            
            print(f"✅ 迁移 {len(vectors)} 个向量")
        except:
            print("⚠️ 向量表迁移跳过（可能不存在）")
        
        # 迁移关联表（简化字段）
        try:
            old_cursor.execute("""
                SELECT id, source_key, target_key, association_type, strength, created_at
                FROM memory_association
            """)
            associations = old_cursor.fetchall()
            
            for assoc in associations:
                new_cursor.execute("""
                    INSERT OR REPLACE INTO memory_associations 
                    (id, source_id, target_id, association_type, strength, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, assoc)
            
            print(f"✅ 迁移 {len(associations)} 个关联")
        except:
            print("⚠️ 关联表迁移跳过（可能不存在）")
        
        # 提交更改
        new_conn.commit()
        
        # 关闭连接
        old_conn.close()
        new_conn.close()
        
        print(f"✅ 数据迁移完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据迁移失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Estia记忆系统 - 数据库简化工具")
    print("=" * 50)
    
    # 创建简化数据库
    if create_simplified_database():
        print("\n✅ 简化数据库创建成功")
        
        # 询问是否迁移数据
        if os.path.exists("assets/memory.db"):
            response = input("\n❓ 发现旧数据库，是否迁移数据？(y/n): ")
            if response.lower() == 'y':
                if migrate_from_old_db():
                    print("\n🎉 数据库简化和迁移完成！")
                    print("\n📝 下一步:")
                    print("   1. 备份旧数据库: assets/memory.db")
                    print("   2. 重命名新数据库: memory_simplified.db -> memory.db")
                    print("   3. 更新代码以使用简化架构")
                else:
                    print("\n❌ 数据迁移失败")
            else:
                print("\n✅ 跳过数据迁移")
        else:
            print("\n✅ 无需迁移数据")
    else:
        print("\n❌ 数据库简化失败")