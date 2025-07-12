#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试模型路径问题
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def debug_model_path():
    """调试模型路径配置"""
    print("🔍 调试模型路径配置")
    print("=" * 60)
    
    # 当前工作目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 项目根目录
    project_root = os.path.dirname(__file__)
    print(f"项目根目录: {project_root}")
    
    # 期望的模型缓存目录
    expected_cache_dir = os.path.join(project_root, "cache")
    print(f"期望缓存目录: {expected_cache_dir}")
    print(f"缓存目录是否存在: {os.path.exists(expected_cache_dir)}")
    
    # 检查模型目录
    model_dir = os.path.join(expected_cache_dir, "models--Qwen--Qwen3-Embedding-0.6B")
    print(f"模型目录: {model_dir}")
    print(f"模型目录是否存在: {os.path.exists(model_dir)}")
    
    if os.path.exists(model_dir):
        print("✅ 模型目录存在")
        # 列出模型文件
        for item in os.listdir(model_dir):
            item_path = os.path.join(model_dir, item)
            print(f"  - {item} {'(目录)' if os.path.isdir(item_path) else '(文件)'}")
    else:
        print("❌ 模型目录不存在")
    
    # 检查向量化器中的路径计算
    print("\n🔧 向量化器路径计算")
    print("-" * 40)
    
    # 模拟向量化器的路径计算
    from core.memory.shared.embedding.vectorizer import TextVectorizer
    vectorizer_file = Path(TextVectorizer.__file__)
    print(f"向量化器文件: {vectorizer_file}")
    
    # 计算路径
    calculated_cache = str(vectorizer_file.parent.parent.parent.parent.parent / "cache")
    print(f"计算的缓存路径: {calculated_cache}")
    print(f"计算的缓存路径是否存在: {os.path.exists(calculated_cache)}")
    
    # 检查环境变量
    print("\n🌍 环境变量检查")
    print("-" * 40)
    
    env_vars = [
        'HUGGINGFACE_HUB_CACHE',
        'SENTENCE_TRANSFORMERS_HOME', 
        'HF_HOME',
        'HF_HUB_OFFLINE',
        'TRANSFORMERS_OFFLINE'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, '未设置')
        print(f"{var}: {value}")
    
    # 测试本地模型加载
    print("\n🧪 测试本地模型加载")
    print("-" * 40)
    
    # 设置环境变量
    os.environ['HUGGINGFACE_HUB_CACHE'] = calculated_cache
    os.environ['SENTENCE_TRANSFORMERS_HOME'] = calculated_cache
    os.environ['HF_HOME'] = calculated_cache
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    
    try:
        from sentence_transformers import SentenceTransformer
        
        model_name = "Qwen/Qwen3-Embedding-0.6B"
        print(f"尝试加载模型: {model_name}")
        
        # 检查是否能找到模型
        expected_model_path = os.path.join(calculated_cache, f"models--{model_name.replace('/', '--')}")
        print(f"期望模型路径: {expected_model_path}")
        print(f"模型路径是否存在: {os.path.exists(expected_model_path)}")
        
        if os.path.exists(expected_model_path):
            print("✅ 发现本地模型，尝试加载...")
            model = SentenceTransformer(
                model_name,
                device='cpu',
                cache_folder=calculated_cache,
                trust_remote_code=True
            )
            print("✅ 模型加载成功！")
            print(f"模型维度: {model.get_sentence_embedding_dimension()}")
        else:
            print("❌ 本地模型不存在")
            
    except ImportError:
        print("❌ sentence-transformers 未安装")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
    
    print("\n🏁 调试完成")

if __name__ == "__main__":
    debug_model_path()