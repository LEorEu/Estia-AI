# scripts/build_index.py

"""
这是一个用于构建或重建FAISS向量索引的工具脚本。
它会读取SQLite数据库中的所有记忆，
使用embedding模型将它们向量化，
然后创建一个FAISS索引文件和一个ID映射文件。
"""
import sys
import os
import json
import numpy as np
import faiss

# 添加项目根目录到搜索路径，以确保可以导入core模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 从我们的核心模块中，导入需要的工具
from core.database import MemoryDatabase
from core.knowledge import text_to_vector

# --- 定义常量 ---
# FAISS索引文件的保存路径
INDEX_PATH = os.path.join("assets", "memory.faiss")
# ID映射文件的保存路径
ID_MAP_PATH = os.path.join("assets", "index_to_id_map.json")

def build_index():
    print("--- 开始构建记忆索引 ---")

    # 1. 连接数据库并获取所有记忆
    print("🗄️ 正在从数据库读取所有记忆...")
    db = MemoryDatabase()
    all_memories = db.get_all_entries_for_indexing()
    db.close()

    if not all_memories:
        print("⚠️ 数据库中没有记忆，无需构建索引。")
        return

    print(f"共找到 {len(all_memories)} 条记忆需要处理。")

    # 2. 将所有记忆文本转换为向量
    print("🧠 正在将记忆文本向量化 (这个过程可能需要一些时间)...")
    # 将数据库ID和文本内容分开存储
    db_ids = [entry[0] for entry in all_memories]
    texts_to_encode = [entry[1] for entry in all_memories]

    # 批量进行编码，效率更高
    all_vectors = np.array([text_to_vector(text) for text in texts_to_encode])
    print("✅ 文本向量化完成。")

    # 3. 创建并构建FAISS索引
    print("🛠️ 正在构建FAISS索引...")
    # 获取向量的维度
    dimension = all_vectors.shape[1]
    # 创建一个基础的、精确的索引 (IndexFlatL2)，它计算的是欧氏距离的平方
    index = faiss.IndexFlatL2(dimension)
    # 将我们所有的向量添加到索引中
    index.add(all_vectors)
    print(f"✅ FAISS索引构建完成，共包含 {index.ntotal} 个向量。")

    # 4. 保存索引文件和ID映射文件
    print(f"💾 正在保存索引文件到: {INDEX_PATH}")
    faiss.write_index(index, INDEX_PATH)

    # 创建一个从FAISS索引号(0, 1, 2...)到数据库主键ID的映射
    # 这至关重要，因为FAISS搜索返回的是索引号，我们需要通过它找到数据库里的原文
    index_to_id_map = {i: db_id for i, db_id in enumerate(db_ids)}

    print(f"💾 正在保存ID映射文件到: {ID_MAP_PATH}")
    with open(ID_MAP_PATH, 'w', encoding='utf-8') as f:
        json.dump(index_to_id_map, f, ensure_ascii=False, indent=4)

    print("\n--- 所有任务完成！记忆索引已更新。 ---")


if __name__ == '__main__':
    build_index()