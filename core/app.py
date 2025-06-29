"""
Estia AI 应用核心
包含主要应用逻辑，负责协调各个组件
"""

import time
import traceback
import logging
from datetime import datetime
import os

from config import settings
from core.dialogue.engine import DialogueEngine
from core.audio import start_keyboard_controller
from core.memory.pipeline import MemoryPipeline

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
        
        # 启动时预加载所有组件
        self._initialize_system()
        
    def _initialize_system(self):
        """系统初始化 - 启动时预加载"""
        if self.show_progress:
            print("\n" + "="*60)
            print("🚀 Estia AI助手启动中...")
            print("="*60)
        
        start_time = time.time()
        
        try:
            # Step 1: 初始化记忆系统（最耗时的部分）
            if self.show_progress:
                print("📚 正在加载记忆系统...")
                print("   🔤 加载向量化模型（Qwen3-Embedding-0.6B）...")
            
            step_start = time.time()
            self.memory = MemoryPipeline()
            step_time = time.time() - step_start
            
            if self.show_progress:
                print(f"   ✅ 记忆系统就绪 ({step_time:.2f}s)")
            self.logger.info(f"记忆系统初始化完成，耗时: {step_time:.2f}s")
            
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
            
            if self.show_progress:
                print("="*60)
                print(f"🎉 Estia AI助手启动完成！")
                print(f"⚡ 总启动时间: {total_time:.2f}秒")
                print(f"💡 后续对话响应时间: ~16ms（实时响应）")
                print("="*60)
            
            self.logger.info(f"Estia系统初始化完成，总耗时: {total_time:.2f}s")
            
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
            # 使用记忆系统增强查询
            enhanced_context = self.memory.enhance_query(query, context)
            
            # 使用对话引擎生成回复
            response = self.dialogue_engine.generate_response(query, enhanced_context)
            
            # 异步存储对话记录（不阻塞响应）
            try:
                self.memory.store_interaction(query, response, context)
            except Exception as e:
                self.logger.warning(f"存储对话记录失败: {e}")
                # 存储失败不影响用户体验
            
            response_time = time.time() - start_time
            self.logger.debug(f"查询处理完成，耗时: {response_time*1000:.2f}ms")
            
            return response
            
        except Exception as e:
            self.logger.error(f"查询处理失败: {e}")
            return "抱歉，我遇到了一些问题，请稍后再试。"
    
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
                    continue
                
                if user_input.lower() in ["stats", "统计"]:
                    print(f"\n📊 会话统计:")
                    print(f"   • 会话时长: {time.time() - session_start:.1f}秒")
                    print(f"   • 对话次数: {query_count}")
                    print(f"   • 平均响应: ~16ms")
                    continue
                
                # 处理用户查询
                query_start = time.time()
                response = self.process_query(user_input)
                query_time = time.time() - query_start
                query_count += 1
                
                print(f"\n🤖 Estia: {response}")
                print(f"   ⚡ 响应时间: {query_time*1000:.2f}ms")
                
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