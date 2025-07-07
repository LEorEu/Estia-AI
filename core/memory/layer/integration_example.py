#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层记忆系统集成示例

展示如何将分层系统集成到现有的EstiaMemorySystem中
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

# 假设的现有系统导入
# from estia.core.memory.estia_memory import EstiaMemorySystem

# 分层系统导入
from . import (
    initialize_layered_memory_system,
    LayeredMemoryIntegration,
    get_layered_integration,
    LayerConfigManager,
    LayerSystemConfig
)

logger = logging.getLogger(__name__)


class EnhancedEstiaMemorySystem:
    """
    增强版Estia记忆系统
    
    在原有EstiaMemorySystem基础上集成分层功能
    """
    
    def __init__(self, db_manager, vectorizer, faiss_retriever, 
                 association_network, history_retriever, scorer, 
                 async_evaluator, context_builder):
        """
        初始化增强版记忆系统
        
        Args:
            db_manager: 数据库管理器
            vectorizer: 向量化器
            faiss_retriever: FAISS检索器
            association_network: 关联网络
            history_retriever: 历史检索器
            scorer: 记忆评分器
            async_evaluator: 异步评估器
            context_builder: 上下文构建器
        """
        # 保存原有组件
        self.db_manager = db_manager
        self.vectorizer = vectorizer
        self.faiss_retriever = faiss_retriever
        self.association_network = association_network
        self.history_retriever = history_retriever
        self.scorer = scorer
        self.async_evaluator = async_evaluator
        self.context_builder = context_builder
        
        # 分层系统集成
        self.layered_integration: Optional[LayeredMemoryIntegration] = None
        self._layered_enabled = False
        
        logger.info("增强版Estia记忆系统已创建")
    
    async def initialize_layered_system(self, config: LayerSystemConfig = None) -> bool:
        """
        初始化分层系统
        
        Args:
            config: 分层系统配置
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            logger.info("开始初始化分层记忆系统...")
            
            # 创建配置管理器
            config_manager = LayerConfigManager(config) if config else None
            
            # 初始化分层集成
            self.layered_integration = await initialize_layered_memory_system(
                db_manager=self.db_manager,
                vectorizer=self.vectorizer,
                config_manager=config_manager
            )
            
            if self.layered_integration:
                self._layered_enabled = True
                logger.info("分层记忆系统初始化成功")
                return True
            else:
                logger.error("分层记忆系统初始化失败")
                return False
                
        except Exception as e:
            logger.error(f"初始化分层系统失败: {e}")
            return False
    
    async def enhance_query(self, user_input: str, session_id: str, 
                          context_length: int = 20) -> Dict[str, Any]:
        """
        增强查询处理（集成分层功能的完整13步流程）
        
        Args:
            user_input: 用户输入
            session_id: 会话ID
            context_length: 上下文长度
            
        Returns:
            Dict: 增强的上下文信息
        """
        try:
            logger.debug(f"开始处理查询: {user_input[:50]}...")
            
            # Step 1-2: 接收和预处理（保持原有逻辑）
            processed_input = self._preprocess_input(user_input)
            
            # Step 3: 向量化用户输入
            vectorized_input = self.vectorizer.vectorize(processed_input)
            
            # Step 4: FAISS检索相似记忆
            similar_memories = self.faiss_retriever.search(
                vectorized_input, 
                top_k=context_length * 3  # 获取更多候选
            )
            
            # 🆕 分层增强检索
            if self._layered_enabled:
                query_context = {
                    'user_input': user_input,
                    'session_id': session_id,
                    'processed_input': processed_input
                }
                similar_memories = self.layered_integration.enhance_memory_retrieval(
                    memory_ids=[m.get('id', m.get('memory_id', '')) for m in similar_memories],
                    query_context=query_context
                )
            
            # Step 5: 关联网络拓展
            expanded_memories = self.association_network.expand(similar_memories)
            
            # Step 6: 历史对话聚合
            history_memories = self.history_retriever.get_session_history(session_id)
            
            # 🆕 分层增强历史检索
            if self._layered_enabled and history_memories:
                history_memories = self.layered_integration.enhance_memory_retrieval(
                    memory_ids=[m.get('id', m.get('memory_id', '')) for m in history_memories],
                    query_context=query_context
                )
            
            # Step 7: 记忆排序与去重
            all_memories = expanded_memories + history_memories
            ranked_memories = self.scorer.rank_memories(all_memories)
            
            # 限制上下文长度
            final_memories = ranked_memories[:context_length]
            
            # Step 8: 组装最终上下文
            if self._layered_enabled:
                # 🆕 分层感知的上下文构建
                enhanced_context = self.layered_integration.enhance_context_building(
                    user_input=user_input,
                    context_memories=final_memories
                )
            else:
                # 原有上下文构建
                enhanced_context = self.context_builder.build(
                    user_input=user_input,
                    memories=final_memories
                )
            
            # 🆕 更新访问信息
            if self._layered_enabled:
                for memory in final_memories:
                    memory_id = memory.get('id', memory.get('memory_id', ''))
                    if memory_id:
                        self.layered_integration.update_memory_access(
                            memory_id, 
                            {'query_context': query_context}
                        )
            
            logger.debug(f"查询处理完成，返回 {len(final_memories)} 条记忆")
            return enhanced_context
            
        except Exception as e:
            logger.error(f"查询增强失败: {e}")
            # 降级到原有逻辑
            return self._fallback_query(user_input, session_id, context_length)
    
    async def store_interaction(self, user_input: str, ai_response: str, 
                              session_id: str, metadata: Dict[str, Any] = None) -> bool:
        """
        存储交互记忆（集成分层功能）
        
        Args:
            user_input: 用户输入
            ai_response: AI响应
            session_id: 会话ID
            metadata: 额外元数据
            
        Returns:
            bool: 存储是否成功
        """
        try:
            logger.debug("开始存储交互记忆")
            
            # 创建记忆对象
            user_memory = {
                'id': self._generate_memory_id('user'),
                'content': user_input,
                'type': 'user',
                'role': 'user',
                'session_id': session_id,
                'timestamp': self._get_current_timestamp(),
                'weight': self._calculate_initial_weight(user_input, 'user'),
                'metadata': metadata or {}
            }
            
            ai_memory = {
                'id': self._generate_memory_id('assistant'),
                'content': ai_response,
                'type': 'assistant',
                'role': 'assistant',
                'session_id': session_id,
                'timestamp': self._get_current_timestamp(),
                'weight': self._calculate_initial_weight(ai_response, 'assistant'),
                'metadata': metadata or {}
            }
            
            # 🆕 分层增强存储
            if self._layered_enabled:
                user_memory = self.layered_integration.enhance_memory_storage(user_memory)
                ai_memory = self.layered_integration.enhance_memory_storage(ai_memory)
            
            # Step 12: 存储记忆到数据库
            user_success = self.db_manager.store_memory(user_memory)
            ai_success = self.db_manager.store_memory(ai_memory)
            
            if user_success and ai_success:
                # Step 11: 异步评估记忆重要性
                await self.async_evaluator.evaluate_importance(user_memory['id'])
                await self.async_evaluator.evaluate_importance(ai_memory['id'])
                
                # Step 13: 更新关联和统计
                self._update_associations(user_memory, ai_memory)
                
                logger.debug("交互记忆存储成功")
                return True
            else:
                logger.error("记忆存储失败")
                return False
                
        except Exception as e:
            logger.error(f"存储交互失败: {e}")
            return False
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        获取系统统计信息（包含分层信息）
        
        Returns:
            Dict: 系统统计信息
        """
        try:
            # 原有统计信息
            base_stats = {
                'total_memories': self._get_total_memories(),
                'total_sessions': self._get_total_sessions(),
                'avg_memory_weight': self._get_avg_memory_weight(),
                'last_cleanup': self._get_last_cleanup_time()
            }
            
            # 🆕 分层统计信息
            if self._layered_enabled:
                layered_stats = self.layered_integration.get_system_status()
                base_stats.update({
                    'layered_system': layered_stats,
                    'layer_distribution': layered_stats.get('system_metrics', {}).get('layer_distribution', {}),
                    'sync_status': layered_stats.get('system_metrics', {}).get('sync_status', 'unknown'),
                    'health_status': layered_stats.get('health_status', {})
                })
            
            return base_stats
            
        except Exception as e:
            logger.error(f"获取系统统计失败: {e}")
            return {'error': str(e)}
    
    async def run_maintenance(self) -> Dict[str, Any]:
        """
        运行系统维护（包含分层维护）
        
        Returns:
            Dict: 维护结果
        """
        try:
            logger.info("开始系统维护...")
            
            maintenance_results = {
                'timestamp': self._get_current_timestamp(),
                'base_maintenance': {},
                'layered_maintenance': {}
            }
            
            # 原有维护逻辑
            base_result = await self._run_base_maintenance()
            maintenance_results['base_maintenance'] = base_result
            
            # 🆕 分层系统维护
            if self._layered_enabled:
                layered_result = await self.layered_integration.run_maintenance()
                maintenance_results['layered_maintenance'] = layered_result
            
            logger.info("系统维护完成")
            return maintenance_results
            
        except Exception as e:
            logger.error(f"系统维护失败: {e}")
            return {'error': str(e), 'timestamp': self._get_current_timestamp()}
    
    async def shutdown(self):
        """
        优雅关闭系统
        """
        try:
            logger.info("开始关闭增强版记忆系统...")
            
            # 关闭分层系统
            if self._layered_enabled and self.layered_integration:
                await self.layered_integration.shutdown()
            
            # 关闭原有组件
            if hasattr(self.async_evaluator, 'shutdown'):
                await self.async_evaluator.shutdown()
            
            if hasattr(self.db_manager, 'close'):
                self.db_manager.close()
            
            logger.info("增强版记忆系统已关闭")
            
        except Exception as e:
            logger.error(f"关闭系统失败: {e}")
    
    # 辅助方法
    def _preprocess_input(self, user_input: str) -> str:
        """预处理用户输入"""
        return user_input.strip()
    
    def _generate_memory_id(self, prefix: str) -> str:
        """生成记忆ID"""
        import uuid
        return f"{prefix}_{uuid.uuid4().hex[:8]}"
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _calculate_initial_weight(self, content: str, role: str) -> float:
        """计算初始权重"""
        base_weight = 5.0
        if role == 'assistant':
            base_weight += 1.0
        if len(content) > 100:
            base_weight += 0.5
        return min(base_weight, 10.0)
    
    def _get_total_memories(self) -> int:
        """获取总记忆数"""
        try:
            result = self.db_manager.query("SELECT COUNT(*) FROM memories")
            return result[0][0] if result else 0
        except:
            return 0
    
    def _get_total_sessions(self) -> int:
        """获取总会话数"""
        try:
            result = self.db_manager.query("SELECT COUNT(DISTINCT session_id) FROM memories")
            return result[0][0] if result else 0
        except:
            return 0
    
    def _get_avg_memory_weight(self) -> float:
        """获取平均记忆权重"""
        try:
            result = self.db_manager.query("SELECT AVG(weight) FROM memories")
            return result[0][0] if result and result[0][0] else 0.0
        except:
            return 0.0
    
    def _get_last_cleanup_time(self) -> Optional[str]:
        """获取最后清理时间"""
        # 这里应该从维护日志中获取
        return None
    
    def _update_associations(self, user_memory: Dict, ai_memory: Dict):
        """更新记忆关联"""
        try:
            # 这里实现关联更新逻辑
            pass
        except Exception as e:
            logger.error(f"更新关联失败: {e}")
    
    async def _run_base_maintenance(self) -> Dict[str, Any]:
        """运行基础维护"""
        try:
            # 这里实现原有的维护逻辑
            return {
                'success': True,
                'cleaned_memories': 0,
                'updated_weights': 0
            }
        except Exception as e:
            logger.error(f"基础维护失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _fallback_query(self, user_input: str, session_id: str, 
                       context_length: int) -> Dict[str, Any]:
        """降级查询处理"""
        try:
            # 简化的降级逻辑
            return {
                'user_input': user_input,
                'memories': [],
                'total_memories': 0,
                'fallback': True
            }
        except Exception as e:
            logger.error(f"降级查询失败: {e}")
            return {'error': str(e)}


# 使用示例
async def integration_example():
    """
    分层系统集成使用示例
    """
    # 假设已有的组件
    db_manager = None  # YourDatabaseManager()
    vectorizer = None  # YourVectorizer()
    faiss_retriever = None  # YourFAISSRetriever()
    association_network = None  # YourAssociationNetwork()
    history_retriever = None  # YourHistoryRetriever()
    scorer = None  # YourMemoryScorer()
    async_evaluator = None  # YourAsyncEvaluator()
    context_builder = None  # YourContextBuilder()
    
    # 创建增强版记忆系统
    enhanced_memory = EnhancedEstiaMemorySystem(
        db_manager=db_manager,
        vectorizer=vectorizer,
        faiss_retriever=faiss_retriever,
        association_network=association_network,
        history_retriever=history_retriever,
        scorer=scorer,
        async_evaluator=async_evaluator,
        context_builder=context_builder
    )
    
    # 初始化分层系统
    layered_success = await enhanced_memory.initialize_layered_system()
    if layered_success:
        print("✅ 分层系统初始化成功")
    else:
        print("❌ 分层系统初始化失败")
        return
    
    # 使用增强功能
    try:
        # 1. 增强查询
        context = await enhanced_memory.enhance_query(
            user_input="我喜欢什么类型的音乐？",
            session_id="session_123"
        )
        print(f"查询结果: {len(context.get('memories', []))} 条记忆")
        
        # 2. 存储交互
        store_success = await enhanced_memory.store_interaction(
            user_input="我喜欢古典音乐",
            ai_response="我记住了，您喜欢古典音乐。有什么特别喜欢的作曲家吗？",
            session_id="session_123"
        )
        print(f"存储结果: {'成功' if store_success else '失败'}")
        
        # 3. 获取系统状态
        stats = enhanced_memory.get_system_stats()
        print(f"系统统计: {stats.get('total_memories', 0)} 条记忆")
        if 'layered_system' in stats:
            print(f"分层状态: {stats['sync_status']}")
        
        # 4. 运行维护
        maintenance_result = await enhanced_memory.run_maintenance()
        print(f"维护结果: {maintenance_result.get('layered_maintenance', {}).get('success', False)}")
        
    except Exception as e:
        print(f"使用过程中出错: {e}")
    
    finally:
        # 优雅关闭
        await enhanced_memory.shutdown()
        print("系统已关闭")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(integration_example())