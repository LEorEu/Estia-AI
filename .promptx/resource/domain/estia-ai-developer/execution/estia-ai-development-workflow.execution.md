<execution>
  <constraint>
    ## Estia-AI开发限制
    - **硬件资源**：本地GPU内存限制，需要优化模型大小
    - **实时性要求**：语音交互需要低延迟响应
    - **内存效率**：长期记忆系统的内存管理
    - **模型兼容性**：不同模型格式的统一接口
    - **数据隐私**：用户对话数据的本地化存储
  </constraint>

  <rule>
    ## 强制性开发规则
    - **模块化设计**：每个功能独立模块，便于维护和扩展
    - **异步优先**：所有IO操作必须异步处理
    - **错误处理**：完整的异常处理和降级机制
    - **性能监控**：关键路径必须有性能指标
    - **代码质量**：遵循PEP8，使用类型注解
    - **版本控制**：模型和代码版本同步管理
    - **测试覆盖**：核心功能必须有单元测试
  </rule>

  <guideline>
    ## 开发指导原则
    - **用户体验优先**：响应速度和交互流畅度
    - **渐进式开发**：从简单到复杂逐步实现
    - **可配置性**：参数和行为可配置化
    - **可观测性**：系统运行状态可监控
    - **可扩展性**：架构支持功能扩展
    - **代码复用**：通用功能抽象为公共库
  </guideline>

  <process>
    ## Estia-AI开发流程
    
    ### 第一阶段：基础架构 (1-2周)
    ```mermaid
    graph TD
        A[项目初始化] --> B[核心模块设计]
        B --> C[数据库设计]
        C --> D[API接口设计]
        D --> E[基础测试]
        
        B --> B1[audio_input.py]
        B --> B2[audio_output.py]
        B --> B3[dialogue_engine.py]
        B --> B4[memory_manager.py]
        
        C --> C1[SQLite数据库]
        C --> C2[记忆表结构]
        C --> C3[索引优化]
    ```
    
    **实现任务**：
    1. 搭建项目基础架构
    2. 实现音频输入输出模块
    3. 设计记忆系统数据结构
    4. 建立LLM推理接口
    
    ### 第二阶段：记忆系统 (2-3周)
    ```mermaid
    graph TD
        A[向量化模块] --> B[FAISS索引]
        B --> C[记忆检索]
        C --> D[关联网络]
        D --> E[记忆压缩]
        
        A --> A1[文本向量化]
        A --> A2[向量缓存]
        
        C --> C1[相似度检索]
        C --> C2[时间过滤]
        C --> C3[权重排序]
        
        D --> D1[语义关联]
        D --> D2[主题聚类]
        D --> D3[关联强度]
    ```
    
    **关键代码结构**：
    ```python
    class MemoryManager:
        def __init__(self):
            self.db = SQLiteDB()
            self.faiss_index = FAISSIndex()
            self.embedding_model = EmbeddingModel()
            self.cache = MemoryCache()
            
        async def store_memory(self, content, memory_type, metadata):
            # 存储记忆到数据库和向量索引
            pass
            
        async def retrieve_memories(self, query, top_k=10):
            # 检索相关记忆
            pass
            
        async def update_associations(self, memory_id, related_ids):
            # 更新记忆关联
            pass
    ```
    
    ### 第三阶段：情感系统 (1-2周)
    ```mermaid
    graph TD
        A[情感分析] --> B[情感识别]
        B --> C[情感响应]
        C --> D[人格管理]
        
        A --> A1[文本情感]
        A --> A2[语音情感]
        A --> A3[上下文情感]
        
        C --> C1[情感匹配]
        C --> C2[语气调整]
        C --> C3[共情回应]
        
        D --> D1[人格特征]
        D --> D2[一致性维护]
        D --> D3[个性化调整]
    ```
    
    **情感系统实现**：
    ```python
    class EmotionSystem:
        def __init__(self):
            self.emotion_analyzer = EmotionAnalyzer()
            self.emotion_responder = EmotionResponder()
            self.personality_manager = PersonalityManager()
            
        async def analyze_emotion(self, text, audio=None):
            # 多模态情感分析
            pass
            
        async def generate_empathetic_response(self, emotion, context):
            # 生成共情回应
            pass
    ```
    
    ### 第四阶段：高级功能 (3-4周)
    ```mermaid
    graph TD
        A[视觉能力] --> B[工具使用]
        B --> C[声音定制]
        C --> D[GUI界面]
        
        A --> A1[屏幕识别]
        A --> A2[OCR处理]
        A --> A3[图像理解]
        
        B --> B1[文件操作]
        B --> B2[联网搜索]
        B --> B3[程序调用]
        
        C --> C1[GPT-SoVITS]
        C --> C2[语音合成]
        C --> C3[音质优化]
        
        D --> D1[桌面应用]
        D --> D2[系统托盘]
        D --> D3[快捷操作]
    ```
    
    ### 开发最佳实践
    
    #### 1. 异步编程模式
    ```python
    import asyncio
    from typing import Optional, List
    
    class EstiaAI:
        def __init__(self):
            self.is_running = False
            self.conversation_loop = None
            
        async def start(self):
            self.is_running = True
            self.conversation_loop = asyncio.create_task(self.main_loop())
            
        async def main_loop(self):
            while self.is_running:
                try:
                    # 监听用户输入
                    user_input = await self.listen_for_input()
                    if user_input:
                        # 异步处理
                        response = await self.process_input(user_input)
                        await self.speak_response(response)
                except Exception as e:
                    logger.error(f"Main loop error: {e}")
                    await asyncio.sleep(1)
    ```
    
    #### 2. 配置管理
    ```python
    # config/settings.py
    class EstiaConfig:
        # LLM配置
        LLM_API_URL = "http://localhost:8080/v1/chat/completions"
        LLM_MODEL = "Qwen3-14B-Instruct"
        
        # 记忆配置
        MEMORY_DB_PATH = "data/memory.db"
        FAISS_INDEX_PATH = "data/faiss_index"
        EMBEDDING_MODEL = "text-embedding-3-small"
        
        # 音频配置
        SAMPLE_RATE = 16000
        CHUNK_SIZE = 1024
        TTS_VOICE = "zh-CN-XiaoxiaoNeural"
        
        # 情感配置
        EMOTION_THRESHOLD = 0.5
        PERSONALITY_TRAITS = {
            "warmth": 0.8,
            "patience": 0.9,
            "humor": 0.6
        }
    ```
    
    #### 3. 错误处理机制
    ```python
    class EstiaError(Exception):
        pass
    
    class MemoryError(EstiaError):
        pass
    
    class LLMError(EstiaError):
        pass
    
    # 装饰器用于错误处理
    def error_handler(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                return await handle_error(e)
        return wrapper
    ```
    
    #### 4. 性能监控
    ```python
    import time
    from functools import wraps
    
    def performance_monitor(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            
            # 记录性能指标
            metrics.record_execution_time(
                func.__name__, 
                end_time - start_time
            )
            return result
        return wrapper
    ```
  </process>

  <criteria>
    ## 开发质量标准
    
    ### 性能指标
    - **响应延迟**：语音输入到开始回复 < 2秒
    - **记忆检索**：相关记忆检索 < 500ms
    - **并发处理**：支持多用户同时交互
    - **资源利用率**：内存使用 < 8GB，CPU < 80%
    
    ### 功能完整性
    - **基础对话**：流畅的语音交互
    - **记忆系统**：准确的记忆存储和检索
    - **情感理解**：基本的情感识别和回应
    - **个性化**：根据用户特点调整行为
    
    ### 代码质量
    - **测试覆盖率**：核心功能 > 80%
    - **代码规范**：遵循PEP8和类型注解
    - **文档完整性**：关键模块有详细文档
    - **可维护性**：模块化设计，低耦合
    
    ### 用户体验
    - **交互自然度**：对话流畅，回应恰当
    - **系统稳定性**：长时间运行无崩溃
    - **功能易用性**：简单配置，快速上手
    - **错误恢复**：异常情况自动恢复
  </criteria>
</execution>