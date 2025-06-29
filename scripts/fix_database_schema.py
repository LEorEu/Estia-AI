#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库Schema修复脚本
修复数据库表结构不匹配的问题
"""

import os
import sys
import sqlite3
import time
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_table_structure(db_path):
    """检查数据库表结构"""
    print(f"🔍 检查数据库表结构: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📋 找到 {len(tables)} 个表:")
        
        for table in tables:
            table_name = table[0]
            print(f"\n📊 表: {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"   • {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")
        return False

def backup_database(db_path):
    """备份数据库"""
    if not os.path.exists(db_path):
        return True
        
    backup_path = f"{db_path}.backup_{int(time.time())}"
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ 数据库已备份到: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ 备份数据库失败: {e}")
        return False

def migrate_memories_table(conn, cursor):
    """迁移memories表"""
    print("🔄 迁移memories表...")
    
    try:
        # 检查当前表结构
        cursor.execute("PRAGMA table_info(memories)")
        current_columns = {col[1]: col[2] for col in cursor.fetchall()}
        
        # 期望的表结构
        expected_columns = {
            'id': 'TEXT',
            'content': 'TEXT',
            'type': 'TEXT',
            'role': 'TEXT',
            'session_id': 'TEXT',
            'timestamp': 'REAL',
            'weight': 'REAL',
            'group_id': 'TEXT',
            'summary': 'TEXT',
            'last_accessed': 'REAL',
            'metadata': 'TEXT'
        }
        
        # 找出缺失的列
        missing_columns = []
        for col, col_type in expected_columns.items():
            if col not in current_columns:
                missing_columns.append((col, col_type))
        
        if not missing_columns:
            print("   ✅ memories表结构已是最新")
            return True
        
        print(f"   📝 需要添加 {len(missing_columns)} 个列:")
        for col, col_type in missing_columns:
            print(f"      • {col} ({col_type})")
        
        # 添加缺失的列
        for col, col_type in missing_columns:
            try:
                # 设置默认值
                default_value = ""
                if col_type == "REAL":
                    if col in ["timestamp", "last_accessed"]:
                        default_value = str(time.time())
                    else:
                        default_value = "0.0"
                elif col_type == "TEXT":
                    if col == "type":
                        default_value = "'memory'"
                    elif col == "role":
                        default_value = "'user'"
                    elif col == "session_id":
                        default_value = "''"
                    else:
                        default_value = "''"
                
                alter_sql = f"ALTER TABLE memories ADD COLUMN {col} {col_type} DEFAULT {default_value}"
                cursor.execute(alter_sql)
                print(f"      ✅ 添加列: {col}")
                
            except Exception as e:
                print(f"      ❌ 添加列失败 {col}: {e}")
        
        # 更新现有记录的默认值
        try:
            current_time = time.time()
            update_queries = []
            
            # 更新timestamp和last_accessed
            if "timestamp" in [col for col, _ in missing_columns]:
                update_queries.append(f"UPDATE memories SET timestamp = {current_time} WHERE timestamp IS NULL OR timestamp = 0")
            
            if "last_accessed" in [col for col, _ in missing_columns]:
                update_queries.append(f"UPDATE memories SET last_accessed = {current_time} WHERE last_accessed IS NULL OR last_accessed = 0")
            
            # 更新type
            if "type" in [col for col, _ in missing_columns]:
                update_queries.append("UPDATE memories SET type = 'memory' WHERE type IS NULL OR type = ''")
            
            # 更新role
            if "role" in [col for col, _ in missing_columns]:
                update_queries.append("UPDATE memories SET role = 'user' WHERE role IS NULL OR role = ''")
            
            # 更新weight
            if "weight" in [col for col, _ in missing_columns]:
                update_queries.append("UPDATE memories SET weight = 1.0 WHERE weight IS NULL OR weight = 0")
            
            for query in update_queries:
                cursor.execute(query)
                print(f"      ✅ 更新默认值")
                
        except Exception as e:
            print(f"      ⚠️ 更新默认值失败: {e}")
        
        print("   ✅ memories表迁移完成")
        return True
        
    except Exception as e:
        print(f"   ❌ memories表迁移失败: {e}")
        return False

def create_missing_tables(conn, cursor):
    """创建缺失的表"""
    print("🔄 创建缺失的表...")
    
    # 检查现有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {table[0] for table in cursor.fetchall()}
    
    # 需要的表
    required_tables = {
        'memories': '''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                type TEXT NOT NULL,
                role TEXT NOT NULL,
                session_id TEXT,
                timestamp REAL NOT NULL,
                weight REAL DEFAULT 1.0,
                group_id TEXT,
                summary TEXT,
                last_accessed REAL NOT NULL,
                metadata TEXT
            )
        ''',
        'memory_vectors': '''
            CREATE TABLE IF NOT EXISTS memory_vectors (
                id TEXT PRIMARY KEY,
                memory_id TEXT NOT NULL,
                vector BLOB NOT NULL,
                model_name TEXT NOT NULL,
                timestamp REAL NOT NULL,
                FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
            )
        ''',
        'memory_association': '''
            CREATE TABLE IF NOT EXISTS memory_association (
                id TEXT PRIMARY KEY,
                source_key TEXT NOT NULL,
                target_key TEXT NOT NULL,
                association_type TEXT NOT NULL,
                strength REAL NOT NULL,
                created_at REAL NOT NULL,
                last_activated REAL NOT NULL,
                group_id TEXT,
                super_group TEXT,
                FOREIGN KEY (source_key) REFERENCES memories(id) ON DELETE CASCADE,
                FOREIGN KEY (target_key) REFERENCES memories(id) ON DELETE CASCADE
            )
        ''',
        'memory_group': '''
            CREATE TABLE IF NOT EXISTS memory_group (
                group_id TEXT PRIMARY KEY,
                super_group TEXT,
                topic TEXT,
                time_start REAL,
                time_end REAL,
                summary TEXT,
                score REAL DEFAULT 1.0
            )
        ''',
        'memory_cache': '''
            CREATE TABLE IF NOT EXISTS memory_cache (
                id TEXT PRIMARY KEY,
                memory_id TEXT NOT NULL,
                cache_level TEXT NOT NULL,
                priority REAL DEFAULT 5.0,
                access_count INTEGER DEFAULT 1,
                last_accessed REAL NOT NULL,
                FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
            )
        '''
    }
    
    created_count = 0
    
    for table_name, create_sql in required_tables.items():
        if table_name not in existing_tables:
            try:
                cursor.execute(create_sql)
                print(f"   ✅ 创建表: {table_name}")
                created_count += 1
            except Exception as e:
                print(f"   ❌ 创建表失败 {table_name}: {e}")
        else:
            print(f"   ✅ 表已存在: {table_name}")
    
    # 创建索引
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_memories_session ON memories(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_memories_group ON memories(group_id)",
        "CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)",
        "CREATE INDEX IF NOT EXISTS idx_memories_last_accessed ON memories(last_accessed)",
        "CREATE INDEX IF NOT EXISTS idx_memory_vectors_memory_id ON memory_vectors(memory_id)",
        "CREATE INDEX IF NOT EXISTS idx_memory_association_source ON memory_association(source_key)",
        "CREATE INDEX IF NOT EXISTS idx_memory_association_target ON memory_association(target_key)",
        "CREATE INDEX IF NOT EXISTS idx_memory_association_group ON memory_association(group_id)",
        "CREATE INDEX IF NOT EXISTS idx_memory_group_super ON memory_group(super_group)",
        "CREATE INDEX IF NOT EXISTS idx_memory_cache_level ON memory_cache(cache_level)",
        "CREATE INDEX IF NOT EXISTS idx_memory_cache_priority ON memory_cache(priority)"
    ]
    
    print("🔄 创建索引...")
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
        except Exception as e:
            print(f"   ⚠️ 创建索引失败: {e}")
    
    print(f"   ✅ 创建了 {created_count} 个新表和相关索引")
    return True

def fix_database_schema(db_path):
    """修复数据库schema"""
    print(f"🔧 开始修复数据库schema: {db_path}")
    
    try:
        # 备份数据库
        if not backup_database(db_path):
            return False
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 设置行工厂，方便访问列名
        conn.row_factory = sqlite3.Row
        
        # 迁移memories表
        if not migrate_memories_table(conn, cursor):
            conn.close()
            return False
        
        # 创建缺失的表
        if not create_missing_tables(conn, cursor):
            conn.close()
            return False
        
        # 提交更改
        conn.commit()
        conn.close()
        
        print("✅ 数据库schema修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复数据库schema失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Estia数据库Schema修复工具")
    print("="*50)
    
    # 数据库路径
    db_path = os.path.join("assets", "memory.db")
    
    print(f"📍 数据库路径: {db_path}")
    
    # 检查当前表结构
    print("\n📋 修复前的表结构:")
    check_table_structure(db_path)
    
    # 修复schema
    print(f"\n🔧 开始修复...")
    success = fix_database_schema(db_path)
    
    if success:
        print("\n📋 修复后的表结构:")
        check_table_structure(db_path)
        
        print("\n🎉 数据库schema修复成功！")
        print("💡 现在可以重新启动Estia系统了")
    else:
        print("\n❌ 数据库schema修复失败")
        print("💡 请检查错误信息并手动修复")

if __name__ == "__main__":
    main() 