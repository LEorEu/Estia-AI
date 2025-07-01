#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一记忆检索引擎 - Estia记忆系统重构 v2.0
整合FAISS、关联、历史检索功能，支持批处理和并发优化
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """检索结果数据类"""
    memory_id: str
    content: str
    importance: float
    relevance_score: float
    memory_type: str
    layer: str
    timestamp: float
    metadata: Dict[str, Any]

class BatchProcessingEngine:
    """批处理引擎 - 并发优化处理"""
    
    def __init__(self, max_workers: int = 4, batch_size: int = 10):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        logger.info(f"批处理引擎初始化: {max_workers}个工作线程, 批处理大小: {batch_size}")
    
    async def batch_retrieve(self, queries: List[str], retriever_func, **kwargs) -> Dict[str, List[RetrievalResult]]:
        """批量检索 - 并发处理多个查询"""
        try:
            start_time = time.time()
            
            # 智能批处理大小调整
            effective_batch_size = min(self.batch_size, len(queries))
            batches = [queries[i:i + effective_batch_size] for i in range(0, len(queries), effective_batch_size)]
            
            # 并发执行批处理
            loop = asyncio.get_event_loop()
            tasks = []
            
            for batch in batches:
                task = loop.run_in_executor(
                    self.executor, 
                    self._process_batch, 
                    batch, retriever_func, kwargs
                )
                tasks.append(task)
            
            batch_results = await asyncio.gather(*tasks)
            
            # 合并结果
            final_results = {}
            for batch_result in batch_results:
                final_results.update(batch_result)
            
            processing_time = time.time() - start_time
            logger.info(f"批量检索完成: {len(queries)}个查询, 耗时: {processing_time*1000:.2f}ms")
            
            return final_results
            
        except Exception as e:
            logger.error(f"批量检索失败: {e}")
            return {}
    
    def _process_batch(self, batch_queries: List[str], retriever_func, kwargs: Dict) -> Dict[str, List[RetrievalResult]]:
        """处理单个批次"""
        results = {}
        for query in batch_queries:
            try:
                query_results = retriever_func(query, **kwargs)
                results[query] = query_results
            except Exception as e:
                logger.warning(f"查询处理失败 '{query}': {e}")
                results[query] = []
        return results
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)

class UnifiedMemoryRetriever:
    """统一检索引擎 - 合并FAISS、关联、历史检索"""
    
    def __init__(self, memory_manager, enable_batch: bool = True):
        self.memory_manager = memory_manager
        self.enable_batch = enable_batch
        
        # 批处理引擎
        if enable_batch:
            self.batch_engine = BatchProcessingEngine()
        
        # 检索组件 - 复用现有组件
        self.faiss_engine = None
        self.vector_index = None
        self.memory_scorer = None
        
        # 尝试加载高级检索组件
        self._try_load_advanced_retrievers()
        
        # 检索统计
        self.retrieval_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'avg_response_time': 0.0,
            'batch_queries': 0
        }
        
        logger.info(f"统一检索引擎初始化完成 (批处理: {'启用' if enable_batch else '禁用'})")
    
    def _try_load_advanced_retrievers(self):
        """尝试加载高级检索组件"""
        try:
            # 尝试加载检索组件
            from .ranking.scorer import MemoryScorer
            
            # 先加载记忆评分器（不需要参数）
            self.memory_scorer = MemoryScorer()
            
            # FAISS组件暂时跳过，需要额外配置
            # TODO: 在热缓存系统中集成FAISS
            logger.info("基础检索组件加载成功")
            logger.info("FAISS组件将在热缓存系统中集成")
            
        except ImportError as e:
            logger.warning(f"高级检索组件不可用: {e}")
            logger.info("将使用基础检索功能")
    
    async def unified_search(self, query: str, limit: int = 10, 
                           min_importance: float = 0.0, 
                           context: Optional[Dict] = None) -> List[RetrievalResult]:
        """统一检索接口 - 50ms内完成"""
        try:
            start_time = time.time()
            self.retrieval_stats['total_queries'] += 1
            
            logger.debug(f"开始统一检索: {query[:30]}...")
            
            # 快速轨道检索 (目标50ms)
            results = await self._fast_track_search(query, limit, min_importance, context)
            
            # 异步关联扩展 (不阻塞响应)
            if results and len(results) < limit:
                asyncio.create_task(self._expand_associations(query, results))
            
            processing_time = time.time() - start_time
            self.retrieval_stats['avg_response_time'] = (
                self.retrieval_stats['avg_response_time'] * (self.retrieval_stats['total_queries'] - 1) + 
                processing_time
            ) / self.retrieval_stats['total_queries']
            
            logger.debug(f"统一检索完成: {len(results)}个结果, 耗时: {processing_time*1000:.2f}ms")
            
            return results
            
        except Exception as e:
            logger.error(f"统一检索失败: {e}")
            return []
    
    async def batch_unified_search(self, queries: List[str], **kwargs) -> Dict[str, List[RetrievalResult]]:
        """批量统一检索"""
        if not self.enable_batch:
            logger.warning("批处理未启用，将逐个处理查询")
            results = {}
            for query in queries:
                results[query] = await self.unified_search(query, **kwargs)
            return results
        
        self.retrieval_stats['batch_queries'] += len(queries)
        return await self.batch_engine.batch_retrieve(
            queries, 
            self._sync_unified_search, 
            **kwargs
        )
    
    async def _fast_track_search(self, query: str, limit: int, 
                               min_importance: float, context: Optional[Dict]) -> List[RetrievalResult]:
        """快速轨道检索 - 核心检索逻辑"""
        results = []
        
        # 1. 基础记忆管理器检索 (20ms目标)
        basic_memories = self.memory_manager.retrieve_memories(
            query=query,
            limit=limit * 2,  # 获取更多候选结果
            min_importance=min_importance
        )
        
        # 2. 转换为统一结果格式
        for memory in basic_memories:
            result = RetrievalResult(
                memory_id=memory.get('id', ''),
                content=memory.get('content', ''),
                importance=memory.get('importance', 0.0),
                relevance_score=self._calculate_relevance(query, memory.get('content', '')),
                memory_type=memory.get('memory_type', 'unknown'),
                layer=memory.get('layer', 'unknown'),
                timestamp=memory.get('timestamp', 0.0),
                metadata=memory.get('metadata', {})
            )
            results.append(result)
        
        # 3. 智能排序去重 (10ms目标)
        results = self._smart_ranking_and_dedup(results, query)
        
        return results[:limit]
    
    def _smart_ranking_and_dedup(self, results: List[RetrievalResult], query: str) -> List[RetrievalResult]:
        """智能排序去重"""
        if not results:
            return []
        
        # 1. 内容去重
        seen_contents = set()
        deduped_results = []
        
        for result in results:
            content_hash = hash(result.content[:100])  # 使用前100字符去重
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                deduped_results.append(result)
        
        # 2. 综合排序
        def calculate_score(result: RetrievalResult) -> float:
            # 综合评分：相关性(40%) + 重要性(30%) + 时效性(20%) + 层级权重(10%)
            relevance_score = result.relevance_score * 0.4
            importance_score = (result.importance / 10.0) * 0.3
            
            # 时效性评分
            time_diff = time.time() - result.timestamp
            time_score = max(0, 1 - (time_diff / (30 * 24 * 3600))) * 0.2  # 30天衰减
            
            # 层级权重
            layer_weights = {'core': 1.0, 'active': 0.8, 'archive': 0.6, 'temp': 0.4, 'faiss': 0.7}
            layer_score = layer_weights.get(result.layer, 0.5) * 0.1
            
            return relevance_score + importance_score + time_score + layer_score
        
        # 排序
        sorted_results = sorted(deduped_results, key=calculate_score, reverse=True)
        
        return sorted_results
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """计算相关性得分"""
        try:
            if not query or not content:
                return 0.0
            
            query_words = set(query.lower().split())
            content_words = set(content.lower().split())
            
            if not query_words or not content_words:
                return 0.0
            
            # 计算Jaccard相似度
            intersection = len(query_words.intersection(content_words))
            union = len(query_words.union(content_words))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.warning(f"计算相关性失败: {e}")
            return 0.0
    
    async def _expand_associations(self, query: str, base_results: List[RetrievalResult]):
        """异步关联扩展 - 深度处理轨道"""
        try:
            logger.debug(f"开始关联扩展: {query[:30]}...")
            
            # 简化的关联计算 (移除复杂逻辑)
            # 基于现有结果寻找相关记忆
            for result in base_results[:3]:  # 只处理前3个结果
                related_memories = self.memory_manager.retrieve_memories(
                    query=result.content[:50],  # 使用记忆内容作为查询
                    limit=2,
                    min_importance=result.importance - 1.0
                )
                
                logger.debug(f"为记忆 {result.memory_id} 找到 {len(related_memories)} 个关联")
            
        except Exception as e:
            logger.warning(f"关联扩展失败: {e}")
    
    def _sync_unified_search(self, query: str, **kwargs) -> List[RetrievalResult]:
        """同步版本的统一检索 - 用于批处理"""
        try:
            # 创建新的事件循环来运行异步方法
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(self.unified_search(query, **kwargs))
                return result
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"同步检索失败: {e}")
            return []
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """获取检索统计信息"""
        return {
            'total_queries': self.retrieval_stats['total_queries'],
            'batch_queries': self.retrieval_stats['batch_queries'],
            'cache_hits': self.retrieval_stats['cache_hits'],
            'cache_hit_rate': (
                self.retrieval_stats['cache_hits'] / max(self.retrieval_stats['total_queries'], 1)
            ),
            'avg_response_time_ms': self.retrieval_stats['avg_response_time'] * 1000,
            'components_available': {
                'faiss_engine': self.faiss_engine is not None,
                'memory_scorer': self.memory_scorer is not None,
                'batch_processing': self.enable_batch
            }
        }

def create_unified_retriever(memory_manager, enable_batch: bool = True) -> UnifiedMemoryRetriever:
    """创建统一检索引擎"""
    return UnifiedMemoryRetriever(memory_manager, enable_batch) 