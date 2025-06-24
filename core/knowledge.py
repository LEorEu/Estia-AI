# core/knowledge.py

"""
本模块负责处理所有与知识、记忆向量化相关的功能。
它包含加载嵌入模型、将文本转换为向量等核心功能。
"""

# 导入 sentence-transformers 库，我们的“汽车”
from sentence_transformers import SentenceTransformer
import numpy as np

# 打印提示信息，表示正在加载模型
print("🧠 正在加载中文嵌入模型 (Qwen/Qwen3-Embedding-0.6B)... 这个过程只需要在程序启动时执行一次。")

# --- 模型加载核心 ---
# 我们在这里加载选定的中文嵌入模型。
# sentence-transformers 会自动处理模型的下载和缓存。
# 'cpu'表示我们让这个（不大的）模型在CPU上运行，把宝贵的显存留给14B的大模型。
embedding_model = SentenceTransformer('Qwen/Qwen3-Embedding-0.6B', device='cpu')

print("✅ 中文嵌入模型加载完成！")


def text_to_vector(text: str) -> np.ndarray:
    """
    将单句文本转换为一个语义向量。

    参数:
        text (str): 需要转换的文本。

    返回:
        numpy.ndarray: 代表该文本语义的向量（一个一维的数字数组）。
    """
    # 调用模型的 .encode() 方法进行编码。
    # normalize_embeddings=True 会对向量进行归一化，这在进行相似度计算时能得到更准确的结果。
    vector = embedding_model.encode(text, normalize_embeddings=True)
    return vector

# -----------------------------------------------------------------------------
# 模块独立测试区域
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    print("\n--- 正在独立测试 knowledge 模块 ---")

    # 定义两个测试句子
    text1 = "我喜欢吃苹果"
    text2 = "我偏爱食用水果"
    text3 = "今天天气真好"

    # 将句子转换为向量
    vector1 = text_to_vector(text1)
    vector2 = text_to_vector(text2)
    vector3 = text_to_vector(text3)

    print(f"\n句子1: '{text1}'")
    # print(f"向量1 (部分): {vector1[:5]}...") # 向量太长，我们只打印前5个维度看看
    print(f"向量维度: {vector1.shape}") # 向量的维度

    # --- 计算语义相似度 ---
    # 向量的点积（dot product）可以用来衡量语义相似度。因为向量已经归一化，点积结果在-1到1之间。越接近1，意思越相近。
    similarity_12 = np.dot(vector1, vector2)
    similarity_13 = np.dot(vector1, vector3)

    print(f"\n'我喜欢吃苹果' 和 '我偏爱食用水果' 的语义相似度: {similarity_12:.4f}")
    print(f"'我喜欢吃苹果' 和 '今天天气真好' 的语义相似度: {similarity_13:.4f}")

    print("\n--- 测试完成 ---")
    print("如果相似度12远大于相似度13，说明嵌入模型工作正常！")