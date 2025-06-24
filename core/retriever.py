# core/retriever.py

"""
本模块负责从长期记忆中检索与当前查询最相关的信息。
它使用FAISS索引进行高效的语义搜索。
"""

import faiss
import json
import os
import numpy as np

# 导入我们自己的核心模块
from .database import MemoryDatabase
from .knowledge import text_to_vector

# --- 定义常量 ---
INDEX_PATH = os.path.join("assets", "memory.faiss")
ID_MAP_PATH = os.path.join("assets", "index_to_id_map.json")

class MemoryRetriever:
    def __init__(self):
        """
        初始化检索器，加载FAISS索引、ID映射表，并连接数据库。
        """
        print("🔍 正在初始化记忆检索器...")
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(f"错误：找不到记忆索引文件 {INDEX_PATH}。请先运行 scripts/build_index.py 来创建索引。")

        # 加载FAISS索引
        self.index = faiss.read_index(INDEX_PATH)
        print(f"✅ FAISS索引加载成功，共 {self.index.ntotal} 条记忆。")

        # 加载索引到数据库ID的映射表
        with open(ID_MAP_PATH, 'r', encoding='utf-8') as f:
            # json加载后key会变成字符串，我们需要把它转换回整数
            self.index_to_id_map = {int(k): v for k, v in json.load(f).items()}
        print("✅ ID映射表加载成功。")

        # 连接到记忆数据库，以便根据ID取回原文
        self.db = MemoryDatabase()

    def search(self, query_text: str, k: int = 3) -> list:
        if self.index.ntotal == 0:
            return []

        query_vector = text_to_vector(query_text)
        query_vector_np = np.array([query_vector]).astype('float32')

        # FAISS搜索返回的是最接近的向量，我们可能需要多找一些作为候选
        # 比如我们最终想要3条，可以先找出10条来重新排序
        num_candidates = max(k * 3, 10)
        distances, indices = self.index.search(query_vector_np, min(num_candidates, self.index.ntotal))

        retrieved_memories = []
        for i, faiss_index in enumerate(indices[0]):
            if faiss_index != -1:
                db_id = self.index_to_id_map.get(faiss_index)
                if db_id:
                    entry = self.db.get_entry_by_id(db_id)
                    if entry:
                        memory_dict = {
                            'id': entry[0],
                            'timestamp': entry[1],
                            'role': entry[2],
                            'content': entry[3],
                            'weight': entry[4],
                            'similarity': 1 - distances[0][i] # 距离转换为相似度
                        }
                        retrieved_memories.append(memory_dict)
                        self.db.update_memory_usage(db_id)

        # --- 核心改动：根据相似度和权重进行综合排序 ---
        # 我们使用一个元组 (tuple) 作为排序的key
        # Python会先按元组的第一个元素（权重）排序，如果权重相同，再按第二个元素（相似度）排序
        # reverse=True 表示我们希望权重和相似度都是越高越好
        sorted_memories = sorted(retrieved_memories, key=lambda x: (x['weight'], x['similarity']), reverse=True)
        
        # 返回排序后、最靠前的k条记忆
        return sorted_memories[:k]

    def close(self):
        self.db.close()

# 模块独立测试区
if __name__ == '__main__':
    print("\n--- 正在独立测试 retriever 模块 ---")
    retriever = MemoryRetriever()

    query = "你还记得我们聊过的天气吗？"
    print(f"\n正在搜索关于 '{query}' 的记忆...")
    results = retriever.search(query)

    if results:
        print("\n找到的相关记忆如下：")
        for mem in results:
            print(f"  - (相似度: {mem['similarity']:.4f}) [ID: {mem['id']}] {mem['role']}: {mem['content']}")
    else:
        print("没有找到相关的长期记忆。")

    retriever.close()
    print("\n--- 测试完成 ---")