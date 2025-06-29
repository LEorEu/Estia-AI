#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库ID列迁移脚本
将memories表的id列从INTEGER类型迁移到TEXT类型
"""

import os
import sys
import sqlite3
import time
import json
import uuid
from datetime import datetime

def migrate_id_column(db_path):
    """迁移ID列从INTEGER到TEXT"""
    print(f"🔄 开始迁移ID列: {db_path}")
    
    # 备份数据库
    backup_path = f"{db_path}.id_migration_backup_{int(time.time())}"
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ 数据库已备份到: {backup_path}")
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查当前表结构
        cursor.execute("PRAGMA table_info(memories)")
        columns = cursor.fetchall()
        
        # 检查id列的类型
        id_column_type = None
        for col in columns:
            if col[1] == 'id':  # col[1]是列名
                id_column_type = col[2]  # col[2]是列类型
                break
        
        print(f"📋 当前ID列类型: {id_column_type}")
        
        if id_column_type == 'TEXT':
            print("✅ ID列已经是TEXT类型，无需迁移")
            conn.close()
            return True
        
        print("🔄 开始迁移过程...")
        
        # Step 1: 创建新表结构
        cursor.execute('''
            CREATE TABLE memories_new (
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
        ''')
        print("✅ 创建新表结构完成")
        
        # Step 2: 获取旧数据
        cursor.execute("SELECT * FROM memories")
        old_data = cursor.fetchall()
        print(f"📊 找到 {len(old_data)} 条记录需要迁移")
        
        # Step 3: 迁移数据
        migrated_count = 0
        id_mapping = {}  # 旧ID到新ID的映射
        
        for row in old_data:
            try:
                # 生成新的UUID作为TEXT类型的ID
                new_id = str(uuid.uuid4())
                old_id = row[0]  # 假设第一列是id
                id_mapping[old_id] = new_id
                
                # 处理其他字段
                # 根据当前表结构重新组织数据
                if len(row) == 6:  # 旧结构：id, timestamp, role, content, weight, last_used_timestamp
                    new_row = (
                        new_id,                    # id (TEXT)
                        row[3],                    # content
                        "memory",                  # type (默认值)
                        row[2],                    # role
                        "",                        # session_id (空)
                        time.time() if isinstance(row[1], str) else row[1],  # timestamp
                        row[4] if row[4] else 1.0, # weight
                        "",                        # group_id (空)
                        "",                        # summary (空)
                        row[5] if row[5] else time.time(),  # last_accessed
                        "{}"                       # metadata (空JSON)
                    )
                else:  # 新结构，但ID是INTEGER
                    new_row = (
                        new_id,                    # 新的TEXT ID
                        row[1] if len(row) > 1 else "",     # content
                        row[2] if len(row) > 2 else "memory",  # type
                        row[3] if len(row) > 3 else "user",    # role
                        row[4] if len(row) > 4 else "",        # session_id
                        row[5] if len(row) > 5 else time.time(),  # timestamp
                        row[6] if len(row) > 6 else 1.0,       # weight
                        row[7] if len(row) > 7 else "",        # group_id
                        row[8] if len(row) > 8 else "",        # summary
                        row[9] if len(row) > 9 else time.time(),  # last_accessed
                        row[10] if len(row) > 10 else "{}"     # metadata
                    )
                
                # 插入新记录
                cursor.execute('''
                    INSERT INTO memories_new 
                    (id, content, type, role, session_id, timestamp, weight, group_id, summary, last_accessed, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', new_row)
                
                migrated_count += 1
                
            except Exception as e:
                print(f"⚠️ 迁移记录失败: {e}, 跳过记录: {row[0]}")
        
        print(f"✅ 成功迁移 {migrated_count} 条记录")
        
        # Step 4: 更新memory_vectors表中的memory_id引用
        if migrated_count > 0:
            print("🔄 更新向量表中的ID引用...")
            
            # 检查memory_vectors表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_vectors'")
            if cursor.fetchone():
                cursor.execute("SELECT id, memory_id FROM memory_vectors")
                vector_data = cursor.fetchall()
                
                updated_vectors = 0
                for vector_id, old_memory_id in vector_data:
                    if old_memory_id in id_mapping:
                        new_memory_id = id_mapping[old_memory_id]
                        cursor.execute(
                            "UPDATE memory_vectors SET memory_id = ? WHERE id = ?",
                            (new_memory_id, vector_id)
                        )
                        updated_vectors += 1
                
                print(f"✅ 更新了 {updated_vectors} 个向量引用")
        
        # Step 5: 更新关联表中的ID引用
        if migrated_count > 0:
            print("🔄 更新关联表中的ID引用...")
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_association'")
            if cursor.fetchone():
                cursor.execute("SELECT id, source_key, target_key FROM memory_association")
                assoc_data = cursor.fetchall()
                
                updated_assocs = 0
                for assoc_id, source_key, target_key in assoc_data:
                    new_source = id_mapping.get(source_key, source_key)
                    new_target = id_mapping.get(target_key, target_key)
                    
                    if new_source != source_key or new_target != target_key:
                        cursor.execute(
                            "UPDATE memory_association SET source_key = ?, target_key = ? WHERE id = ?",
                            (new_source, new_target, assoc_id)
                        )
                        updated_assocs += 1
                
                print(f"✅ 更新了 {updated_assocs} 个关联引用")
        
        # Step 6: 替换表
        cursor.execute("DROP TABLE memories")
        cursor.execute("ALTER TABLE memories_new RENAME TO memories")
        
        # Step 7: 重新创建索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_memories_session ON memories(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_memories_group ON memories(group_id)",
            "CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)",
            "CREATE INDEX IF NOT EXISTS idx_memories_last_accessed ON memories(last_accessed)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print("✅ 重新创建索引完成")
        
        # 提交所有更改
        conn.commit()
        conn.close()
        
        print("🎉 ID列迁移完成！")
        print(f"📊 迁移统计:")
        print(f"   • 迁移记录数: {migrated_count}")
        print(f"   • ID映射数: {len(id_mapping)}")
        print(f"   • 备份文件: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 尝试恢复备份
        try:
            conn.close()
        except:
            pass
        
        return False

def main():
    """主函数"""
    print("🔄 Estia数据库ID列迁移工具")
    print("="*50)
    
    db_path = os.path.join("assets", "memory.db")
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"📍 数据库路径: {db_path}")
    
    success = migrate_id_column(db_path)
    
    if success:
        print("\n✅ 迁移成功完成！")
        print("💡 现在可以正常使用新的记忆系统了")
    else:
        print("\n❌ 迁移失败")
        print("💡 请检查错误信息，必要时可以从备份恢复")

if __name__ == "__main__":
    main() 