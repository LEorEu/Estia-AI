"""
数据库管理器 - 负责初始化SQLite数据库、创建表和索引
"""

import os
import sqlite3
import logging
import json
import time
from pathlib import Path

# 导入日志工具
try:
    from core.utils.logger import get_logger
    logger = get_logger("estia.memory.db")
except ImportError:
    # 如果还没有日志工具，使用标准日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("estia.memory.db")

class DatabaseManager:
    """数据库管理器类，负责初始化和管理SQLite数据库"""
    
    def __init__(self, db_path=None):
        """
        初始化数据库管理器
        
        参数:
            db_path: 数据库文件路径，如果为None则使用默认路径
        """
        if db_path is None:
            # 使用统一的默认路径配置
            try:
                from .. import get_default_db_path
                db_path = get_default_db_path()
            except ImportError:
                # 备用方案
                db_path = os.path.join("assets", "memory.db")
            
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.is_connected = False
        
        logger.info(f"数据库管理器初始化，使用数据库: {db_path}")
    
    def connect(self):
        """连接到数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            self.cursor = self.conn.cursor()
            self.is_connected = True
            logger.info("成功连接到数据库")
            return True
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            self.conn = None
            self.cursor = None
            self.is_connected = False
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            self.is_connected = False
            logger.info("数据库连接已关闭")
    
    def initialize_database(self):
        """初始化数据库，创建所有必要的表和索引"""
        # 确保连接
        if not self.is_connected or not self.conn or not self.cursor:
            if not self.connect():
                logger.error("无法初始化数据库：连接失败")
                return False
        
        try:
            # 创建记忆表
            if not self._create_memories_table():
                return False
            
            # 创建向量表
            if not self._create_vectors_table():
                return False
            
            # 创建关联表
            if not self._create_associations_table():
                return False
            
            # 创建分组表
            if not self._create_groups_table():
                return False
            
            # 创建缓存表
            if not self._create_cache_table():
                return False
            
            logger.info("数据库初始化完成")
            return True
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
            return False
    
    def _ensure_connection(self):
        """确保数据库连接有效"""
        if not self.is_connected or not self.conn or not self.cursor:
            return self.connect()
        return True
    
    def _create_memories_table(self):
        """创建记忆主表及其索引"""
        # 确保连接
        if not self._ensure_connection():
            logger.error("无法创建memories表：数据库未连接")
            return False
        
        try:
            # 创建表
            self.cursor.execute('''
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
            ''')
            
            # 创建索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_session ON memories(session_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_group ON memories(group_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_last_accessed ON memories(last_accessed)')
            
            # 提交更改
            self.conn.commit()
            logger.info("创建memories表及索引完成")
            return True
        except Exception as e:
            logger.error(f"创建memories表失败: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def _create_vectors_table(self):
        """创建向量存储表及其索引"""
        # 确保连接
        if not self._ensure_connection():
            logger.error("无法创建memory_vectors表：数据库未连接")
            return False
        
        try:
            # 创建表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_vectors (
                    id TEXT PRIMARY KEY,
                    memory_id TEXT NOT NULL,
                    vector BLOB NOT NULL,
                    model_name TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
                )
            ''')
            
            # 创建索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_vectors_memory_id ON memory_vectors(memory_id)')
            
            # 提交更改
            self.conn.commit()
            logger.info("创建memory_vectors表及索引完成")
            return True
        except Exception as e:
            logger.error(f"创建memory_vectors表失败: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def _create_associations_table(self):
        """创建记忆关联表及其索引"""
        # 确保连接
        if not self._ensure_connection():
            logger.error("无法创建memory_association表：数据库未连接")
            return False
        
        try:
            # 创建表
            self.cursor.execute('''
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
            ''')
            
            # 创建索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_association_source ON memory_association(source_key)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_association_target ON memory_association(target_key)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_association_group ON memory_association(group_id)')
            
            # 提交更改
            self.conn.commit()
            logger.info("创建memory_association表及索引完成")
            return True
        except Exception as e:
            logger.error(f"创建memory_association表失败: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def _create_groups_table(self):
        """创建话题分组表及其索引"""
        # 确保连接
        if not self._ensure_connection():
            logger.error("无法创建memory_group表：数据库未连接")
            return False
        
        try:
            # 创建表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_group (
                    group_id TEXT PRIMARY KEY,
                    super_group TEXT,
                    topic TEXT,
                    time_start REAL,
                    time_end REAL,
                    summary TEXT,
                    score REAL DEFAULT 1.0
                )
            ''')
            
            # 创建索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_group_super ON memory_group(super_group)')
            
            # 提交更改
            self.conn.commit()
            logger.info("创建memory_group表及索引完成")
            return True
        except Exception as e:
            logger.error(f"创建memory_group表失败: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def _create_cache_table(self):
        """创建记忆缓存表及其索引"""
        # 确保连接
        if not self._ensure_connection():
            logger.error("无法创建memory_cache表：数据库未连接")
            return False
        
        try:
            # 创建表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_cache (
                    id TEXT PRIMARY KEY,
                    memory_id TEXT NOT NULL,
                    cache_level TEXT NOT NULL,
                    priority REAL DEFAULT 5.0,
                    access_count INTEGER DEFAULT 1,
                    last_accessed REAL NOT NULL,
                    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
                )
            ''')
            
            # 创建索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_cache_level ON memory_cache(cache_level)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_cache_priority ON memory_cache(priority)')
            
            # 提交更改
            self.conn.commit()
            logger.info("创建memory_cache表及索引完成")
            return True
        except Exception as e:
            logger.error(f"创建memory_cache表失败: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def execute_query(self, query, params=None):
        """
        执行SQL查询
        
        参数:
            query: SQL查询语句
            params: 查询参数
            
        返回:
            查询结果
        """
        # 确保连接
        if not self._ensure_connection():
            logger.error("无法执行查询：未连接到数据库")
            return None
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            # 🔥 关键修复：如果是写入操作，立即提交事务
            query_upper = query.strip().upper()
            if query_upper.startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER')):
                self.conn.commit()
                logger.debug("数据库写入操作已提交")
                
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            if self.conn and query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.conn.rollback()
                logger.debug("数据库操作已回滚")
            return None
    
    def query(self, query_sql, params=None):
        """
        执行SQL查询（execute_query的别名，为了兼容性）
        
        参数:
            query_sql: SQL查询语句
            params: 查询参数
            
        返回:
            查询结果
        """
        return self.execute_query(query_sql, params)
    
    def execute_transaction(self, queries):
        """
        执行事务（多个SQL语句）
        
        参数:
            queries: 包含SQL语句和参数的列表，每项格式为 (query, params)
            
        返回:
            是否成功
        """
        # 确保连接
        if not self._ensure_connection():
            logger.error("无法执行事务：未连接到数据库")
            return False
        
        try:
            for query, params in queries:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                    
            self.conn.commit()
            return True
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"执行事务失败: {e}")
            return False
    
    def backup_database(self, backup_path=None):
        """
        备份数据库
        
        参数:
            backup_path: 备份文件路径，如果为None则使用时间戳生成
            
        返回:
            备份文件路径或None（如果失败）
        """
        # 确保连接
        if not self._ensure_connection():
            logger.error("无法备份数据库：未连接到数据库")
            return None
        
        try:
            if backup_path is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_dir = os.path.join("assets", "backups")
                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(backup_dir, f"memory_{timestamp}.db")
            
            # 创建备份连接
            backup_conn = sqlite3.connect(backup_path)
            
            # 执行备份
            with backup_conn:
                self.conn.backup(backup_conn)
            
            backup_conn.close()
            logger.info(f"数据库已备份到: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"备份数据库失败: {e}")
            return None
    
    def get_table_info(self, table_name):
        """
        获取表信息
        
        参数:
            table_name: 表名
            
        返回:
            表信息字典
        """
        # 确保连接
        if not self._ensure_connection():
            logger.error("无法获取表信息：未连接到数据库")
            return None
        
        try:
            # 获取表结构
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            
            # 获取记录数
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = self.cursor.fetchone()[0]
            
            return {
                "table_name": table_name,
                "columns": [dict(col) for col in columns],
                "record_count": count
            }
        except Exception as e:
            logger.error(f"获取表信息失败: {e}")
            return None

# 模块测试代码
if __name__ == "__main__":
    # 使用临时数据库进行测试
    test_db_path = os.path.join("assets", "test_memory.db")
    
    # 如果测试数据库已存在，则删除
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # 创建数据库管理器
    db_manager = DatabaseManager(test_db_path)
    
    # 初始化数据库
    success = db_manager.initialize_database()
    print(f"数据库初始化{'成功' if success else '失败'}")
    
    # 获取表信息
    tables = ["memories", "memory_vectors", "memory_association", "memory_group", "memory_cache"]
    for table in tables:
        info = db_manager.get_table_info(table)
        if info:
            print(f"\n表 {info['table_name']} 结构:")
            for col in info['columns']:
                print(f"  - {col['name']} ({col['type']})")
            print(f"  记录数: {info['record_count']}")
    
    # 关闭连接
    db_manager.close()
    
    print("\n测试完成")
