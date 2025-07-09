#!/usr/bin/env python3
"""
异步评估器启动管理器
解决异步评估器启动时机不确定的问题
"""

import asyncio
import threading
import logging
import time
from typing import Optional, Callable, Any
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class AsyncStartupMode(Enum):
    """异步启动模式"""
    AUTO = "auto"           # 自动检测最佳模式
    EVENT_LOOP = "event_loop"  # 使用现有事件循环
    NEW_LOOP = "new_loop"   # 创建新的事件循环
    THREAD_POOL = "thread_pool"  # 使用线程池
    MANUAL = "manual"       # 手动启动

class AsyncEvaluatorStartupManager:
    """异步评估器启动管理器"""
    
    def __init__(self, max_workers: int = 2):
        """
        初始化启动管理器
        
        参数:
            max_workers: 线程池最大工作线程数
        """
        self.startup_mode = AsyncStartupMode.AUTO
        self.is_initialized = False
        self.evaluator = None
        self.event_loop = None
        self.thread_pool = None
        self.background_thread = None
        self.startup_lock = threading.Lock()
        self.max_workers = max_workers
        
        # 启动尝试计数和重试机制
        self.startup_attempts = 0
        self.max_startup_attempts = 3
        self.last_startup_error = None
        
        logger.info("AsyncEvaluatorStartupManager初始化完成")
    
    def detect_optimal_startup_mode(self) -> AsyncStartupMode:
        """
        检测最优的启动模式
        
        返回:
            最优的启动模式
        """
        try:
            # 尝试获取运行中的事件循环
            try:
                loop = asyncio.get_running_loop()
                if loop and loop.is_running():
                    logger.info("检测到运行中的事件循环，使用EVENT_LOOP模式")
                    return AsyncStartupMode.EVENT_LOOP
            except RuntimeError:
                pass
            
            # 检查是否在主线程且可以创建事件循环
            if threading.current_thread() == threading.main_thread():
                try:
                    # 尝试获取或创建事件循环
                    loop = asyncio.get_event_loop()
                    if not loop.is_running():
                        logger.info("主线程中可创建事件循环，使用NEW_LOOP模式")
                        return AsyncStartupMode.NEW_LOOP
                except RuntimeError:
                    pass
            
            # 默认使用线程池模式
            logger.info("使用THREAD_POOL模式作为默认选择")
            return AsyncStartupMode.THREAD_POOL
            
        except Exception as e:
            logger.warning(f"模式检测失败，使用THREAD_POOL模式: {e}")
            return AsyncStartupMode.THREAD_POOL
    
    def initialize_evaluator(self, evaluator_instance) -> bool:
        """
        初始化异步评估器
        
        参数:
            evaluator_instance: 异步评估器实例
            
        返回:
            是否初始化成功
        """
        with self.startup_lock:
            if self.is_initialized:
                logger.info("异步评估器已初始化，跳过重复初始化")
                return True
            
            self.evaluator = evaluator_instance
            
            # 自动检测启动模式
            if self.startup_mode == AsyncStartupMode.AUTO:
                self.startup_mode = self.detect_optimal_startup_mode()
            
            success = self._perform_startup()
            
            if success:
                self.is_initialized = True
                self.startup_attempts = 0
                logger.info(f"✅ 异步评估器启动成功，模式: {self.startup_mode.value}")
            else:
                self.startup_attempts += 1
                logger.error(f"❌ 异步评估器启动失败，尝试次数: {self.startup_attempts}")
                
                # 如果达到最大尝试次数，切换到线程池模式重试
                if (self.startup_attempts < self.max_startup_attempts and 
                    self.startup_mode != AsyncStartupMode.THREAD_POOL):
                    logger.info("切换到THREAD_POOL模式重试")
                    self.startup_mode = AsyncStartupMode.THREAD_POOL
                    success = self._perform_startup()
                    if success:
                        self.is_initialized = True
                        logger.info("✅ 重试启动成功")
            
            return self.is_initialized
    
    def _perform_startup(self) -> bool:
        """
        执行具体的启动操作
        
        返回:
            是否启动成功
        """
        try:
            if self.startup_mode == AsyncStartupMode.EVENT_LOOP:
                return self._start_with_existing_loop()
            elif self.startup_mode == AsyncStartupMode.NEW_LOOP:
                return self._start_with_new_loop()
            elif self.startup_mode == AsyncStartupMode.THREAD_POOL:
                return self._start_with_thread_pool()
            else:
                logger.warning(f"不支持的启动模式: {self.startup_mode}")
                return False
        except Exception as e:
            self.last_startup_error = str(e)
            logger.error(f"启动执行失败: {e}")
            return False
    
    def _start_with_existing_loop(self) -> bool:
        """使用现有事件循环启动"""
        try:
            loop = asyncio.get_running_loop()
            
            # 创建启动任务
            task = loop.create_task(self.evaluator.start())
            
            # 注册任务完成回调
            def on_startup_complete(future):
                try:
                    future.result()  # 检查是否有异常
                    logger.info("异步评估器在现有事件循环中启动成功")
                except Exception as e:
                    logger.error(f"异步评估器启动异常: {e}")
                    self.is_initialized = False
            
            task.add_done_callback(on_startup_complete)
            return True
            
        except Exception as e:
            logger.error(f"现有事件循环启动失败: {e}")
            return False
    
    def _start_with_new_loop(self) -> bool:
        """创建新事件循环启动"""
        try:
            # 在主线程中同步启动
            async def startup_coro():
                await self.evaluator.start()
                return True
            
            result = asyncio.run(startup_coro())
            logger.info("异步评估器在新事件循环中启动成功")
            return result
            
        except Exception as e:
            logger.error(f"新事件循环启动失败: {e}")
            return False
    
    def _start_with_thread_pool(self) -> bool:
        """使用线程池启动"""
        try:
            # 创建线程池（如果还没有）
            if self.thread_pool is None:
                self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
            
            # 在后台线程中运行事件循环
            def run_evaluator_loop():
                try:
                    # 创建新的事件循环
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    self.event_loop = loop
                    
                    # 启动评估器
                    loop.run_until_complete(self.evaluator.start())
                    
                    # 保持事件循环运行
                    logger.info("异步评估器后台事件循环开始运行")
                    loop.run_forever()
                    
                except Exception as e:
                    logger.error(f"后台事件循环异常: {e}")
                    self.is_initialized = False
                finally:
                    loop.close()
                    logger.info("后台事件循环已关闭")
            
            # 提交到线程池
            self.background_thread = self.thread_pool.submit(run_evaluator_loop)
            
            # 等待启动完成（最多等待5秒）
            time.sleep(0.5)  # 给启动一些时间
            
            if self.event_loop and not self.event_loop.is_closed():
                logger.info("异步评估器在线程池中启动成功")
                return True
            else:
                logger.error("线程池启动失败：事件循环未正常创建")
                return False
                
        except Exception as e:
            logger.error(f"线程池启动失败: {e}")
            return False
    
    def queue_evaluation_safely(self, evaluation_coro):
        """
        安全地将评估任务加入队列 - 改进版本
        
        参数:
            evaluation_coro: 评估协程
        """
        if not self.is_initialized:
            logger.warning("异步评估器未初始化，跳过评估任务")
            return False
        
        try:
            if self.startup_mode == AsyncStartupMode.EVENT_LOOP:
                # 使用现有事件循环
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(evaluation_coro)
                    return True
                except RuntimeError:
                    logger.warning("无法获取运行中的事件循环")
                    return False
                
            elif self.startup_mode in [AsyncStartupMode.NEW_LOOP, AsyncStartupMode.THREAD_POOL]:
                # 使用管理的事件循环
                if self.event_loop and not self.event_loop.is_closed():
                    try:
                        asyncio.run_coroutine_threadsafe(evaluation_coro, self.event_loop)
                        return True
                    except Exception as e:
                        logger.error(f"线程安全执行失败: {e}")
                        return False
                else:
                    logger.warning("管理的事件循环不可用，尝试使用新事件循环")
                    # 尝试使用新的事件循环
                    try:
                        asyncio.run(evaluation_coro)
                        return True
                    except Exception as e:
                        logger.error(f"新事件循环执行失败: {e}")
                        return False
            
            return False
            
        except Exception as e:
            logger.error(f"安全队列评估失败: {e}")
            return False
    
    def get_status(self) -> dict:
        """
        获取启动管理器状态
        
        返回:
            状态信息字典
        """
        return {
            "is_initialized": self.is_initialized,
            "startup_mode": self.startup_mode.value,
            "startup_attempts": self.startup_attempts,
            "last_error": self.last_startup_error,
            "has_thread_pool": self.thread_pool is not None,
            "has_event_loop": self.event_loop is not None,
            "thread_pool_active": (
                self.background_thread is not None and 
                not self.background_thread.done() if self.background_thread else False
            )
        }
    
    def manual_restart(self) -> bool:
        """
        手动重启异步评估器
        
        返回:
            是否重启成功
        """
        logger.info("开始手动重启异步评估器")
        
        # 先停止
        self.shutdown()
        
        # 重置状态
        self.is_initialized = False
        self.startup_attempts = 0
        self.startup_mode = AsyncStartupMode.AUTO
        
        # 重新启动
        if self.evaluator:
            return self.initialize_evaluator(self.evaluator)
        else:
            logger.error("无评估器实例，无法重启")
            return False
    
    def shutdown(self):
        """关闭启动管理器"""
        try:
            logger.info("开始关闭异步评估器启动管理器")
            
            # 停止评估器
            if self.evaluator and self.is_initialized:
                if self.event_loop and not self.event_loop.is_closed():
                    # 在事件循环中停止评估器
                    future = asyncio.run_coroutine_threadsafe(
                        self.evaluator.stop(), self.event_loop
                    )
                    try:
                        future.result(timeout=5.0)  # 等待最多5秒
                    except Exception as e:
                        logger.warning(f"停止评估器超时: {e}")
            
            # 停止事件循环
            if self.event_loop and not self.event_loop.is_closed():
                self.event_loop.call_soon_threadsafe(self.event_loop.stop)
            
            # 关闭线程池
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
                self.thread_pool = None
            
            # 等待后台线程结束
            if self.background_thread:
                try:
                    self.background_thread.result(timeout=3.0)
                except Exception as e:
                    logger.warning(f"后台线程停止超时: {e}")
            
            self.is_initialized = False
            logger.info("✅ 异步评估器启动管理器已关闭")
            
        except Exception as e:
            logger.error(f"关闭启动管理器失败: {e}")

# 全局启动管理器实例
_startup_manager: Optional[AsyncEvaluatorStartupManager] = None

def get_startup_manager() -> AsyncEvaluatorStartupManager:
    """获取全局启动管理器实例"""
    global _startup_manager
    if _startup_manager is None:
        _startup_manager = AsyncEvaluatorStartupManager()
    return _startup_manager

def initialize_async_evaluator_safely(evaluator_instance) -> bool:
    """
    安全地初始化异步评估器
    
    参数:
        evaluator_instance: 异步评估器实例
        
    返回:
        是否初始化成功
    """
    manager = get_startup_manager()
    return manager.initialize_evaluator(evaluator_instance)

def queue_evaluation_task_safely(evaluation_coro) -> bool:
    """
    安全地加入评估任务
    
    参数:
        evaluation_coro: 评估协程
        
    返回:
        是否成功加入队列
    """
    manager = get_startup_manager()
    return manager.queue_evaluation_safely(evaluation_coro) 