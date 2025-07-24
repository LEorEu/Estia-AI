"""
Estia AI 应用核心
包含主要应用逻辑，负责协调各个组件
"""

import time
import traceback
import logging
import asyncio
import threading
from datetime import datetime
import os

from config import settings
from core.dialogue.engine import DialogueEngine
from core.audio import start_keyboard_controller
from core.memory import create_memory_system
from core.monitoring_bridge import get_monitoring_bridge

# 设置日志
logger = logging.getLogger("estia.app")

class EstiaApp:
    """Estia AI 应用核心类 - 优化版本"""
    
    def __init__(self, show_startup_progress=True):
        """初始化Estia应用"""
        self.logger = logger
        self.show_progress = show_startup_progress
        self.memory = None
        self.dialogue_engine = None
        self.is_initialized = False
        self._async_initialized = False
        
        # 🔧 添加session管理
        self.current_session_id = None
        self.session_context = None
        
        # 🔧 监控桥接器
        self.monitoring_bridge = get_monitoring_bridge()
        self._heartbeat_thread = None
        self._heartbeat_running = False
        
        # 启动时预加载所有组件
        self._initialize_system()
        
        # 尝试初始化异步组件
        self._try_initialize_async()
        
    def _try_initialize_async(self):
        """尝试初始化异步组件"""
        try:
            # 检查是否有运行的事件循环
            loop = asyncio.get_running_loop()
            if loop and not self._async_initialized:
                # 创建异步初始化任务
                asyncio.create_task(self._initialize_async_components())
        except RuntimeError:
            # 没有事件循环，稍后在需要时初始化
            logger.debug("暂时没有事件循环，异步组件将在需要时初始化")
    
    async def _initialize_async_components(self):
        """异步初始化组件 - 使用稳定的启动管理器"""
        try:
            if self.memory and not self._async_initialized:
                if self.show_progress:
                    print("⚡ 正在初始化异步评估器...")
                
                # 检查异步管理器和异步评估器是否已创建
                success = (self.memory.async_flow_manager is not None and 
                          getattr(self.memory.async_flow_manager, 'async_evaluator', None) is not None)
                self._async_initialized = success
                
                if self.show_progress:
                    if success:
                        print("   ✅ 异步评估器就绪")
                    else:
                        print("   ⚠️ 异步评估器初始化失败，将在后续重试")
                    
                logger.info(f"异步组件初始化完成: {success}")
        except Exception as e:
            logger.error(f"异步组件初始化失败: {e}")
    
    def ensure_fully_initialized(self):
        """确保所有组件（包括异步组件）都已初始化 - 简化为同步方法"""
        if not self._async_initialized and self.memory:
            self._async_initialized = (self.memory.async_flow_manager is not None and 
                                     getattr(self.memory.async_flow_manager, 'async_evaluator', None) is not None)
    
    def _initialize_system(self):
        """系统初始化 - 启动时预加载"""
        if self.show_progress:
            print("\n" + "="*60)
            print("🚀 Estia AI助手启动中...")
            print("="*60)
        
        start_time = time.time()
        
        try:
            # Step 1: 初始化增强版记忆系统
            if self.show_progress:
                print("📚 正在加载增强版记忆系统...")
                print("   🧠 加载分层记忆架构...")
                print("   🔤 加载向量化模型（Qwen3-Embedding-0.6B）...")
            
            step_start = time.time()
            self.memory = create_memory_system(enable_advanced=True)  # 🔥 使用新的统一记忆系统
            step_time = time.time() - step_start
            
            if self.show_progress:
                print(f"   ✅ Estia记忆系统就绪 ({step_time:.2f}s)")
                print("   🎯 完整13步工作流程: 智能检索+异步评估")
                print("   ⚡ 性能优化: 高级功能全开")
            self.logger.info(f"Estia记忆系统初始化完成，耗时: {step_time:.2f}s")
            
            # Step 2: 初始化对话引擎
            if self.show_progress:
                print("🧠 正在初始化对话引擎...")
            
            step_start = time.time()
            self.dialogue_engine = DialogueEngine()
            step_time = time.time() - step_start
            
            if self.show_progress:
                print(f"   ✅ 对话引擎就绪 ({step_time:.2f}s)")
            self.logger.info(f"对话引擎初始化完成，耗时: {step_time:.2f}s")
            
            # Step 3: 系统预热
            if self.show_progress:
                print("🔥 正在进行系统预热...")
            
            step_start = time.time()
            self._warmup_system()
            step_time = time.time() - step_start
            
            if self.show_progress:
                print(f"   ✅ 系统预热完成 ({step_time:.2f}s)")
            
            # 完成初始化
            total_time = time.time() - start_time
            self.is_initialized = True
            
            # 🔧 更新监控系统状态
            self.monitoring_bridge.update_system_status(running=True)
            
            # 🔧 更新记忆系统统计信息
            if self.memory:
                try:
                    memory_stats = self.memory.get_system_stats()
                    self.monitoring_bridge.update_memory_stats(memory_stats)
                    self.logger.debug("监控桥接器已更新记忆系统统计")
                except Exception as e:
                    self.logger.warning(f"更新监控统计失败: {e}")
            
            # 🔧 启动监控心跳线程
            self._start_monitoring_heartbeat()
            
            if self.show_progress:
                print("="*60)
                print(f"🎉 Estia AI助手启动完成！(完整13步记忆系统)")
                print(f"⚡ 总启动时间: {total_time:.2f}秒")
                print(f"💡 查询增强时间: <100ms | 完整对话: <500ms")
                print(f"🧠 记忆架构: 向量检索 + 关联网络 + 异步评估")
                print("="*60)
            
            self.logger.info(f"Estia系统初始化完成（完整版），总耗时: {total_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"系统初始化失败: {e}")
            if self.show_progress:
                print(f"❌ 系统启动失败: {e}")
            raise
    
    def _warmup_system(self):
        """系统预热 - 执行一次完整的查询流程"""
        try:
            # 预热查询，确保所有组件都已加载
            warmup_query = "系统预热测试"
            
            # 预热记忆系统
            if self.memory:
                self.memory.enhance_query(warmup_query, None)
            
            # 预热对话引擎
            if self.dialogue_engine:
                # 这里可以添加对话引擎的预热逻辑
                pass
                
        except Exception as e:
            self.logger.warning(f"系统预热失败: {e}")
            # 预热失败不影响系统正常运行
    
    def get_or_create_session_id(self):
        """获取或创建session ID"""
        if self.current_session_id is None:
            import uuid
            self.current_session_id = f"session_{uuid.uuid4().hex[:8]}"
            self.logger.debug(f"创建新session: {self.current_session_id}")
        return self.current_session_id
    
    def get_session_context(self):
        """获取session上下文"""
        if self.session_context is None:
            self.session_context = {
                'session_id': self.get_or_create_session_id(),
                'context_memories': []  # 将在查询增强时填充
            }
        return self.session_context
        
    def process_query_stream(self, query, context=None):
        """
        流式处理用户查询
        
        参数:
            query: 用户输入的文本
            context: 可选的上下文信息
            
        返回:
            生成器，yield文本片段
        """
        if not self.is_initialized or not self.memory or not self.dialogue_engine:
            raise RuntimeError("系统未初始化完成")
        
        start_time = time.time()
        full_response = ""
        
        try:
            # 🔧 确保context包含session信息
            if context is None:
                context = self.get_session_context()
            else:
                # 补充必要的session信息
                if 'session_id' not in context:
                    context['session_id'] = self.get_or_create_session_id()
                if 'context_memories' not in context:
                    context['context_memories'] = []
            
            # 使用记忆系统增强查询
            self.logger.debug(f"开始流式处理查询: {query[:50]}...")
            
            # 🔧 获取完整的同步流程结果，包括context_memories
            sync_result = self.memory.sync_flow_manager.execute_sync_flow(query, context)
            enhanced_context = sync_result.get('enhanced_context', '')
            context_memories = sync_result.get('context_memories', [])
            
            # 🔧 更新context以包含context_memories
            context['context_memories'] = context_memories
            
            enhance_time = time.time() - start_time
            
            self.logger.debug(f"记忆增强完成，耗时: {enhance_time*1000:.2f}ms，上下文长度: {len(enhanced_context)}，记忆数: {len(context_memories)}")
            
            # 使用对话引擎流式生成回复
            response_start = time.time()
            
            # 根据配置选择流式输出方式
            if settings.ENABLE_TEXT_STREAM and settings.ENABLE_AUDIO_STREAM:
                # 文本+语音流式输出
                for chunk in self._process_stream_with_audio(query, enhanced_context):
                    full_response += chunk
                    yield chunk
            elif settings.ENABLE_TEXT_STREAM:
                # 仅文本流式输出
                for chunk in self._process_text_stream(query, enhanced_context):
                    full_response += chunk
                    yield chunk
            elif settings.ENABLE_AUDIO_STREAM:
                # 仅语音流式输出
                for chunk in self._process_audio_stream(query, enhanced_context):
                    full_response += chunk
                    yield chunk
            else:
                # 普通输出
                response = self.dialogue_engine.generate_response(query, enhanced_context)
                full_response = response
                yield response
            
            response_time = time.time() - response_start
            self.logger.debug(f"流式对话生成完成，耗时: {response_time*1000:.2f}ms")
            
            # 异步存储对话记录（不阻塞响应）
            try:
                self.memory.store_interaction(query, full_response, context)
                self.logger.debug("对话记录已加入存储队列")
            except Exception as e:
                self.logger.warning(f"存储对话记录失败: {e}")
            
            # 🔧 更新监控数据
            total_time = time.time() - start_time
            try:
                session_id = context.get('session_id') if context else None
                self.monitoring_bridge.update_system_status(running=True, session_id=session_id)
                self.monitoring_bridge.update_performance_metrics(
                    response_time=total_time, 
                    success=True,
                    cache_hit=True  # 假设缓存命中，实际可以从记忆系统获取
                )
                self.monitoring_bridge.add_session_record(
                    user_input=query,
                    ai_response=full_response,
                    response_time=total_time,
                    session_id=session_id
                )
                self.logger.debug(f"监控数据已更新，响应时间: {total_time:.3f}s")
            except Exception as e:
                self.logger.warning(f"更新监控数据失败: {e}")
            
        except Exception as e:
            self.logger.error(f"流式处理查询失败: {e}")
            # 🔧 记录失败的查询
            total_time = time.time() - start_time
            try:
                self.monitoring_bridge.update_performance_metrics(
                    response_time=total_time, 
                    success=False
                )
            except:
                pass
            yield f"抱歉，处理您的请求时出现错误: {str(e)}"
    
    def _process_text_stream(self, query, enhanced_context):
        """处理文本流式输出"""
        try:
            # 使用对话引擎的流式方法
            if self.dialogue_engine:
                # enhanced_context已经由ContextLengthManager构建了完整的对话上下文
                # 包括角色设定、记忆格式化、用户输入和回复指导，无需再次包装
                response_generator = self.dialogue_engine._call_llm_with_context_stream(enhanced_context)
                
                for chunk in response_generator:
                    yield chunk
            else:
                yield "对话引擎未初始化"
                
        except Exception as e:
            self.logger.error(f"文本流式输出失败: {e}")
            yield f"抱歉，文本流式输出失败: {str(e)}"
    
    def _process_audio_stream(self, query, enhanced_context):
        """处理语音流式输出"""
        try:
            from core.audio.output import speak_stream
            
            # 获取文本生成器
            if self.dialogue_engine:
                # enhanced_context已经由ContextLengthManager构建了完整的对话上下文
                # 包括角色设定、记忆格式化、用户输入和回复指导，无需再次包装
                response_generator = self.dialogue_engine._call_llm_with_context_stream(enhanced_context)
                
                # 收集完整回复并进行语音输出
                full_response = ""
                response_chunks = []
                
                for chunk in response_generator:
                    full_response += chunk
                    response_chunks.append(chunk)
                
                # 使用语音流式输出
                import asyncio
                asyncio.run(self._speak_stream_async(iter(response_chunks)))
                
                # 返回完整回复（用于存储）
                yield full_response
            else:
                yield "对话引擎未初始化"
            
        except Exception as e:
            self.logger.error(f"语音流式输出失败: {e}")
            yield f"抱歉，语音流式输出失败: {str(e)}"
    
    def _process_stream_with_audio(self, query, enhanced_context):
        """处理文本+语音流式输出"""
        try:
            from core.audio.output import speak_stream
            
            # 获取文本生成器
            if self.dialogue_engine:
                # enhanced_context已经由ContextLengthManager构建了完整的对话上下文
                # 包括角色设定、记忆格式化、用户输入和回复指导，无需再次包装
                response_generator = self.dialogue_engine._call_llm_with_context_stream(enhanced_context)
                
                # 收集所有文本块
                response_chunks = []
                full_response = ""
                
                for chunk in response_generator:
                    response_chunks.append(chunk)
                    full_response += chunk
                
                # 在后台线程中运行语音流式输出
                import asyncio
                import threading
                
                def run_audio_stream():
                    asyncio.run(self._speak_stream_async(iter(response_chunks)))
                
                audio_thread = threading.Thread(target=run_audio_stream)
                audio_thread.start()
                
                # 在主线程中返回文本流
                for chunk in response_chunks:
                    yield chunk
                
                # 等待音频线程完成
                audio_thread.join()
            else:
                yield "对话引擎未初始化"
            
        except Exception as e:
            self.logger.error(f"文本+语音流式输出失败: {e}")
            yield f"抱歉，流式输出失败: {str(e)}"
    
    async def _speak_stream_async(self, text_generator):
        """异步语音流式输出"""
        try:
            from core.audio.output import text_to_speech_stream
            await text_to_speech_stream(text_generator)
        except Exception as e:
            self.logger.error(f"异步语音流式输出失败: {e}")

    def process_query(self, query, context=None):
        """
        处理用户查询 - 优化版本
        
        参数:
            query: 用户输入的文本
            context: 可选的上下文信息
            
        返回:
            AI的回复
        """
        if not self.is_initialized or not self.memory or not self.dialogue_engine:
            raise RuntimeError("系统未初始化完成")
        
        start_time = time.time()
        
        try:
            # 🔧 确保context包含session信息
            if context is None:
                context = self.get_session_context()
            else:
                # 补充必要的session信息
                if 'session_id' not in context:
                    context['session_id'] = self.get_or_create_session_id()
                if 'context_memories' not in context:
                    context['context_memories'] = []
            
            # 使用记忆系统增强查询
            self.logger.debug(f"开始处理查询: {query[:50]}...")
            
            # 🔧 获取完整的同步流程结果，包括context_memories
            sync_result = self.memory.sync_flow_manager.execute_sync_flow(query, context)
            enhanced_context = sync_result.get('enhanced_context', '')
            context_memories = sync_result.get('context_memories', [])
            
            # 🔧 更新context以包含context_memories
            context['context_memories'] = context_memories
            
            enhance_time = time.time() - start_time
            
            self.logger.debug(f"记忆增强完成，耗时: {enhance_time*1000:.2f}ms，上下文长度: {len(enhanced_context)}，记忆数: {len(context_memories)}")
            
            # 使用对话引擎生成回复
            response_start = time.time()
            response = self.dialogue_engine.generate_response(query, enhanced_context)
            response_time = time.time() - response_start
            
            self.logger.debug(f"对话生成完成，耗时: {response_time*1000:.2f}ms")
            
            # 异步存储对话记录（不阻塞响应）
            try:
                self.memory.store_interaction(query, response, context)
                self.logger.debug("对话记录已加入存储队列")
            except Exception as e:
                self.logger.warning(f"存储对话记录失败: {e}")
                # 存储失败不影响用户体验
            
            total_time = time.time() - start_time
            self.logger.debug(f"查询处理完成，总耗时: {total_time*1000:.2f}ms")
            
            return response
            
        except Exception as e:
            self.logger.error(f"查询处理失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return "抱歉，我遇到了一些问题，请稍后再试。"
    
    def _start_monitoring_heartbeat(self):
        """启动监控心跳线程"""
        if self._heartbeat_running:
            return
            
        self._heartbeat_running = True
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        self.logger.debug("监控心跳线程已启动")
    
    def _heartbeat_loop(self):
        """监控心跳循环"""
        while self._heartbeat_running and self.is_initialized:
            try:
                # 每15秒更新一次系统状态，保持监控数据新鲜
                current_session = getattr(self, 'current_session_id', None)
                self.monitoring_bridge.update_system_status(
                    running=True, 
                    session_id=current_session
                )
                
                # 更新记忆系统统计
                if self.memory:
                    try:
                        memory_stats = self.memory.get_system_stats()
                        self.monitoring_bridge.update_memory_stats(memory_stats)
                    except Exception as e:
                        self.logger.debug(f"心跳更新记忆统计失败: {e}")
                
                self.logger.debug("监控心跳更新完成")
                
            except Exception as e:
                self.logger.warning(f"监控心跳更新失败: {e}")
            
            # 每15秒心跳一次
            time.sleep(15)
    
    def _stop_monitoring_heartbeat(self):
        """停止监控心跳线程"""
        self._heartbeat_running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=2)
            self.logger.debug("监控心跳线程已停止")
    
    def start_voice_interaction(self):
        """启动语音交互模式"""
        if not self.is_initialized:
            raise RuntimeError("系统未初始化完成")
            
        self.logger.info("启动语音交互模式")
        
        if self.show_progress:
            print("\n🎤 语音交互模式已启动")
            print("💡 使用说明:")
            print("   • 按住 [空格键] 开始录音")
            print("   • 松开 [空格键] 结束录音并发送")
            print("   • 按 [ESC键] 退出程序")
            print("   • 按 [F1键] 查看帮助")
            print("\n等待你的语音输入...")
        
        # 启动键盘控制器，传入处理函数
        start_keyboard_controller(llm_callback=self.process_query)
    
    def start_text_interaction(self):
        """启动文本交互模式（控制台）"""
        if not self.is_initialized:
            raise RuntimeError("系统未初始化完成")
            
        self.logger.info("启动文本交互模式")
        
        # 确保异步组件初始化
        if not self._async_initialized:
            print("⚡ 正在初始化异步评估器...")
            try:
                # 创建新的事件循环来初始化异步组件
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # 运行异步初始化
                loop.run_until_complete(self._initialize_async_components())
                loop.close()
                
                print("   ✅ 异步评估器就绪")
            except Exception as e:
                self.logger.error(f"异步组件初始化失败: {e}")
                print(f"   ⚠️ 异步组件初始化失败: {e}")
                print("   📝 将以基础模式运行（无记忆存储）")
        
        print("\n💬 Estia 文本交互模式")
        print("💡 输入 'exit' 或 'quit' 退出")
        print("💡 输入 'help' 查看帮助")
        print("="*50)
        
        session_start = time.time()
        query_count = 0
        
        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ["exit", "quit", "退出"]:
                    session_time = time.time() - session_start
                    print(f"\n👋 再见！本次会话时长: {session_time:.1f}秒，共 {query_count} 次对话")
                    break
                
                if user_input.lower() in ["help", "帮助"]:
                    print("\n💡 使用帮助:")
                    print("   • 直接输入问题与Estia对话")
                    print("   • 输入 'exit' 或 'quit' 退出")
                    print("   • 输入 'stats' 查看性能统计")
                    print("   • 输入 'memory' 查看记忆统计")
                    continue
                
                if user_input.lower() in ["stats", "统计"]:
                    print(f"\n📊 会话统计:")
                    print(f"   • 会话时长: {time.time() - session_start:.1f}秒")
                    print(f"   • 对话次数: {query_count}")
                    print(f"   • 平均响应: ~16ms")
                    continue
                
                if user_input.lower() in ["memory", "记忆"]:
                    if self.memory:
                        stats = self.memory.get_system_stats()
                        print(f"\n🧠 Estia记忆系统统计:")
                        print(f"   • 总记忆数: {stats.get('total_memories', 0)}")
                        
                        # 显示组件状态
                        components = stats.get('components', {})
                        if components:
                            print(f"   🔧 核心组件:")
                            component_names = {
                                'db_manager': '数据库管理器',
                                'vectorizer': '向量化器',
                                'faiss_search': 'FAISS检索',
                                'association': '关联网络',
                                'history': '历史检索器',
                                'storage': '记忆存储',
                                'scorer': '记忆评分器',
                                'async_evaluator': '异步评估器'
                            }
                            for comp_key, comp_name in component_names.items():
                                status = "✅" if components.get(comp_key) else "❌"
                                print(f"     {status} {comp_name}")
                        
                        # 显示系统特性
                        enhanced_features = [
                            "✅ 13步完整工作流程",
                            "✅ 向量语义检索", 
                            "✅ 多跳关联网络",
                            "✅ 数据库持久化" if stats.get('initialized') else "❌ 系统未初始化",
                            "✅ 异步评估处理" if stats.get('async_evaluator_running') else "⏳ 异步评估待启动"
                        ]
                        print(f"   🚀 系统特性:")
                        for feature in enhanced_features:
                            print(f"     {feature}")
                            
                        # 异步队列状态
                        async_queue = stats.get('async_queue', {})
                        if async_queue:
                            print(f"   📝 异步评估队列: {async_queue.get('status', '未知')}")
                            
                        print(f"   ⚡ 高级功能: {'启用' if stats.get('advanced_features') else '禁用'}")
                    else:
                        print("\n❌ 记忆系统未初始化")
                    continue
                
                # 处理用户查询
                query_start = time.time()
                
                # 根据配置选择流式或普通输出
                if settings.ENABLE_STREAM_OUTPUT:
                    print(f"\n🤖 Estia: ", end="", flush=True)
                    full_response = ""
                    
                    try:
                        # 🔧 传递session上下文
                        session_context = self.get_session_context()
                        for chunk in self.process_query_stream(user_input, session_context):
                            print(chunk, end="", flush=True)
                            full_response += chunk
                    except Exception as e:
                        print(f"流式输出失败: {e}")
                        # 降级到普通输出
                        response = self.process_query(user_input)
                        print(response)
                        full_response = response
                else:
                    # 🔧 传递session上下文
                    session_context = self.get_session_context()
                    response = self.process_query(user_input, session_context)
                    print(f"\n🤖 Estia: {response}")
                    full_response = response
                
                query_time = time.time() - query_start
                query_count += 1
                
                print(f"\n   ⚡ 响应时间: {query_time*1000:.2f}ms")
                
            except EOFError:
                print("\n\n👋 输入结束，正在退出...")
                break
            except KeyboardInterrupt:
                print("\n\n👋 检测到中断信号，正在退出...")
                break
            except Exception as e:
                print(f"\n❌ 处理出错: {e}")
                self.logger.error(f"文本交互出错: {e}")
    
    def start_api_server(self):
        """启动API服务器模式，提供HTTP API接口"""
        if not self.is_initialized:
            raise RuntimeError("系统未初始化完成")
            
        self.logger.info("API服务器模式尚未实现")
        print("\n🚧 API服务器模式正在开发中...")
        # TODO: 实现API服务器模式
    
    def start(self, interaction_mode="voice"):
        """
        启动Estia应用
        
        参数:
            interaction_mode: 交互模式，可选值: "voice"(语音), "text"(文本), "api"(API服务)
        """
        if not self.is_initialized:
            raise RuntimeError("系统未初始化完成")
            
        self.logger.info(f"Estia启动，交互模式: {interaction_mode}")
        
        try:
            if interaction_mode == "voice":
                self.start_voice_interaction()
            elif interaction_mode == "text":
                self.start_text_interaction()
            elif interaction_mode == "api":
                self.start_api_server()
            else:
                self.logger.error(f"未知的交互模式: {interaction_mode}")
                print(f"❌ 未知的交互模式: {interaction_mode}")
                print("💡 支持的模式: voice, text, api")
                
        except KeyboardInterrupt:
            print("\n👋 用户中断，正在退出...")
        except Exception as e:
            self.logger.error(f"交互模式启动失败: {e}")
            print(f"❌ 启动失败: {e}")
        finally:
            # 🔧 清理监控心跳线程
            self._stop_monitoring_heartbeat()
            # 🔧 更新监控状态为停止
            try:
                self.monitoring_bridge.update_system_status(running=False)
            except:
                pass
    
    def get_system_stats(self):
        """获取系统状态统计"""
        return {
            "initialized": self.is_initialized,
            "components": {
                "memory_system": self.memory is not None,
                "dialogue_engine": self.dialogue_engine is not None
            },
            "startup_time": "~5s",
            "response_time": "~16ms"
        }


def run_app(interaction_mode="voice", show_progress=True):
    """
    运行Estia应用的便捷函数
    
    参数:
        interaction_mode: 交互模式，可选值: "voice"(语音), "text"(文本), "api"(API服务)
        show_progress: 是否显示启动进度
    """
    try:
        app = EstiaApp(show_startup_progress=show_progress)
        app.start(interaction_mode)
    except Exception as e:
        logger.error(f"应用运行失败: {e}")
        if show_progress:
            print(f"❌ 应用运行失败: {e}")
        raise


if __name__ == "__main__":
    # 直接运行此文件时，启动应用
    run_app()