# tests/test_stream_output.py

# 假设您已经导入了 DialogueEngine 和其他必要的模块
# from core.dialogue_engine import DialogueEngine
# import sys
# import io

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dialogue.engine import DialogueEngine
from core.utils.logger import setup_logger

def run_test():
    """运行流式输出的测试"""
    print("🎯 流式输出功能测试")
    print("============================================================")
    print("🚀 开始测试流式输出功能")
    print("==================================================")
    
    engine = DialogueEngine() # 创建引擎实例
    
    test_prompts = [
        "你好，请简单介绍一下你自己",
        "今天东京的天气怎么样？", # 修正了问题，让它更具体
        "你能帮我写一首关于夏日夜晚的短诗吗？"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- 测试 {i} ---")
        print(f"用户: {prompt}")
        
        # 准备消息格式
        messages = [{"role": "user", "content": prompt}]
        
        # --- 核心修正点在这里 ---
        
        print("流式输出: ", end="") # 打印提示语，不换行
        
        # 1. 调用流式方法，得到生成器
        response_generator = engine._call_gemini_api_stream(messages)
        
        # 2. 使用 for 循环来“消费”生成器，并实时打印每个文本块
        full_response_text = []
        for text_chunk in response_generator:
            print(text_chunk, end="", flush=True) # 实时打印文本块
            full_response_text.append(text_chunk) # 将文本块收集起来

        print() # 确保在流式输出结束后换行

        # 3. 将收集到的文本块拼接成完整回复
        final_reply = "".join(full_response_text)
        
        print(f"完整回复: {final_reply}")
        print("------------------------------")

if __name__ == "__main__":
    run_test()