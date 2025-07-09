## Python LLM 开发专业知识

### 核心技术栈

#### LLM 推理框架
- **llama.cpp**：高性能C++推理引擎，支持GGUF格式
- **transformers**：Hugging Face生态，支持多种模型
- **vLLM**：高吞吐量推理服务，适合生产环境
- **Ollama**：本地LLM部署工具，用户友好
- **OpenAI API**：标准化API接口，便于切换模型

#### 向量数据库
- **FAISS**：Facebook开源，高性能相似度搜索
- **ChromaDB**：Python原生，易于集成
- **Pinecone**：云端向量数据库，可扩展性强
- **Weaviate**：图数据库，支持多模态

#### 异步编程
- **asyncio**：Python原生异步库
- **aiohttp**：异步HTTP客户端
- **asyncpg**：异步PostgreSQL驱动
- **aiomultiprocess**：异步多进程处理

### 关键开发模式

#### 1. 流式生成模式
```python
async def stream_generate(prompt: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8080/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "stream": True
            }
        ) as response:
            async for line in response.content:
                if line.startswith(b"data: "):
                    data = json.loads(line[6:])
                    if "choices" in data:
                        yield data["choices"][0]["delta"]["content"]
```

#### 2. 批处理优化
```python
class BatchProcessor:
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        self.queue = asyncio.Queue()
        
    async def process_batch(self, items: List[str]) -> List[str]:
        # 批量处理提高效率
        embeddings = await self.embedding_model.encode_batch(items)
        return embeddings
```

#### 3. 缓存策略
```python
from functools import lru_cache
import redis

class LLMCache:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.memory_cache = {}
        
    @lru_cache(maxsize=1000)
    def get_cached_response(self, prompt_hash: str) -> Optional[str]:
        return self.redis_client.get(f"llm_response:{prompt_hash}")
```

### 性能优化技巧

#### 1. 内存管理
- 使用生成器避免大量数据一次性加载
- 定期清理不用的模型和缓存
- 使用内存映射文件处理大型数据

#### 2. 并发控制
- 使用信号量控制并发数量
- 连接池管理数据库连接
- 异步队列处理任务

#### 3. 模型优化
- 量化模型减少内存占用
- 使用LoRA等技术进行参数高效微调
- 动态加载模型权重

### 常见问题解决方案

#### 1. CUDA内存溢出
```python
import torch
import gc

def clear_gpu_memory():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    gc.collect()
```

#### 2. 死锁避免
```python
import asyncio
from asyncio import Semaphore

class RateLimiter:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = Semaphore(max_concurrent)
        
    async def acquire(self):
        await self.semaphore.acquire()
        
    def release(self):
        self.semaphore.release()
```

#### 3. 错误重试机制
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def resilient_llm_call(prompt: str) -> str:
    # 带重试的LLM调用
    try:
        response = await llm_client.generate(prompt)
        return response
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise
```

### 测试策略

#### 1. 单元测试
```python
import pytest
import asyncio

class TestLLMService:
    @pytest.mark.asyncio
    async def test_generate_response(self):
        service = LLMService()
        response = await service.generate("Hello")
        assert len(response) > 0
        assert isinstance(response, str)
```

#### 2. 集成测试
```python
@pytest.mark.asyncio
async def test_end_to_end_conversation():
    app = EstiaAI()
    await app.initialize()
    
    response = await app.process_input("你好")
    assert response is not None
    assert "你好" in response or "hello" in response.lower()
```

### 部署最佳实践

#### 1. 容器化部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

#### 2. 健康检查
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/health")
async def health_check():
    try:
        # 检查关键服务状态
        await check_llm_service()
        await check_database_connection()
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
```

#### 3. 监控指标
```python
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge

# 定义监控指标
REQUEST_COUNT = Counter('llm_requests_total', 'Total LLM requests')
REQUEST_DURATION = Histogram('llm_request_duration_seconds', 'LLM request duration')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')

def monitor_system_metrics():
    MEMORY_USAGE.set(psutil.Process().memory_info().rss)
```