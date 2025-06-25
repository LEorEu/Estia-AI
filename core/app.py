"""
Estia AI 应用核心
包含主要应用逻辑，负责协调各个组件
"""

import time
import traceback
from datetime import datetime

from config import settings
from core.audio_input import record_audio, transcribe_audio
from core.audio_output import speak
from core.dialogue_engine import generate_response
from core.intent_parser import parse_intent, evaluate_importance
from core.score_async_executor import ScoreAsyncExecutor
from core.personality import PERSONAS
from core.memory import (
    MemoryManager, 
    MemoryAssociationNetwork, 
    MemoryConflictDetector, 
    MemorySummarizer
)

class EstiaApp:
    """Estia AI 应用核心类"""
    
    def __init__(self, logger):
        """初始化应用"""
        self.logger = logger
        self.memory_manager = None
        self.score_executor = None
        self.vector_store = None
    
    def initialize(self):
        """初始化所有组件"""
        self.logger.info("🔧 初始化应用组件...")
        
        # 初始化异步执行器
        self.score_executor = ScoreAsyncExecutor()
        self.logger.info("✅ 异步执行器初始化完成")
        
        # 初始化向量数据库
        try:
            self.logger.info("📦 加载向量数据库...")
            try:
                from summer.faiss_search import FaissStore
                self.vector_store = FaissStore()
                self.logger.info("✅ 向量数据库加载成功")
            except ImportError:
                self.logger.warning("⚠️ FaissStore未找到，使用默认向量存储")
            self.logger.info("✅ 向量数据库初始化完成")
        except Exception as e:
            self.logger.error(f"❌ 向量数据库加载失败: {e}")
        
        # 初始化记忆管理器
        self.logger.info("🧠 初始化记忆管理器...")
        self.memory_manager = MemoryManager(self.vector_store)
        
        # 初始化高级记忆功能
        try:
            # 确保已创建关联网络和冲突检测
            if not hasattr(self.memory_manager, 'association_network'):
                self.memory_manager.association_network = MemoryAssociationNetwork()
                self.logger.info("✅ 记忆关联网络初始化成功")
            
            if not hasattr(self.memory_manager, 'conflict_detector'):
                self.memory_manager.conflict_detector = MemoryConflictDetector(
                    self.memory_manager, 
                    self.memory_manager.association_network
                )
                self.logger.info("✅ 冲突检测器初始化成功")
            
            if not hasattr(self.memory_manager, 'summarizer'):
                self.memory_manager.summarizer = MemorySummarizer(
                    self.memory_manager, 
                    self.memory_manager.association_network
                )
                self.logger.info("✅ 记忆总结器初始化成功")
                
            self.logger.info("✅ 高级记忆功能初始化完成")
        except Exception as e:
            self.logger.error(f"❌ 高级记忆功能初始化失败: {e}")
        
        self.logger.info("✅ 应用初始化完成")
    
    def run(self):
        """运行主循环"""
        self.logger.info("🔄 开始对话处理...")
        
        while True:
            try:
                # 语音输入
                user_input = self.get_audio_input()
                if not user_input:
                    continue
                
                # 处理用户输入
                self.process_user_input(user_input)
                
            except Exception as e:
                self.logger.error(f"❌ 处理失败: {e}")
                traceback.print_exc()
                time.sleep(2)
    
    def get_audio_input(self):
        """获取并处理语音输入"""
        print("🎤 请说话...")
        audio_file = record_audio()
        if not audio_file:
            print("❌ 录音失败")
            return None
        
        print("🔍 转录中...")
        text = transcribe_audio(audio_file)
        if text:
            print(f"👤 用户: {text}")
        else:
            print("❌ 转录失败")
        
        return text
    
    def process_user_input(self, user_input):
        """处理用户输入"""
        if not user_input or not user_input.strip():
            return
        
        # 1. 分析意图和重要性
        try:
            intent = parse_intent(user_input)
            importance = evaluate_importance(user_input)
            self.logger.info(f"🧠 意图分析: {intent}, 重要性: {importance}")
            
            # 准备上下文信息
            context = f"意图: {intent}"
        except Exception as e:
            self.logger.error(f"意图解析失败: {e}")
            intent = "对话"
            importance = 5.0
            context = ""
        
        # 2. 创建记忆条目
        memory_item = {
            "content": user_input,
            "role": "user",
            "timestamp": time.time(),
            "weight": importance,
            "context": context
        }
        
        # 3. 记忆管理
        try:
            # 添加记忆并自动进行关联和冲突检测
            memory_key = self.memory_manager.add_memory(memory_item)
            
            # 增强检索记忆，现在支持关联和冲突感知
            memory_results = self.memory_manager.retrieve_memory(
                user_input, 
                limit=7,
                parallel=True,
                include_associations=True,
                check_conflicts=True
            )
            
            # 格式化记忆结果用于LLM
            memory_context = self.format_memory_for_llm(memory_results)
        except Exception as e:
            self.logger.error(f"记忆处理失败: {e}")
            memory_context = ""
        
        # 4. 思考并生成响应
        try:
            # 选择人格
            personality = PERSONAS.get("默认", "")
            
            # 使用LLM生成回复
            response = generate_response(user_input, memory_context, personality)
            print(f"🤖 Estia: {response}")
            
            # 添加AI回复到记忆
            ai_memory = {
                "content": response,
                "role": "assistant",
                "timestamp": time.time(),
                "weight": importance * 0.8,  # AI回复权重稍低于用户输入
                "context": context
            }
            self.memory_manager.add_memory(ai_memory)
            
            # 5. 语音回应
            self.score_executor.submit_task(speak, response)
            
        except Exception as e:
            self.logger.error(f"生成响应失败: {e}")
            speak("抱歉，我现在处理不了这个问题。")
    
    def format_memory_for_llm(self, memory_results):
        """增强的记忆格式化，支持关联记忆和冲突标记"""
        if not memory_results:
            return ""
        
        formatted_memories = []
        
        for memory in memory_results:
            role = memory.get("role", "system")
            content = memory.get("content", "")
            timestamp = memory.get("timestamp", "")
            
            # 格式化时间
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
            
            # 处理特殊标记
            prefix = ""
            if memory.get("is_associated", False):
                prefix = "[关联记忆] "
            elif memory.get("is_summary", False):
                prefix = "[记忆摘要] "
            elif memory.get("status") == "superseded":
                prefix = "[已更新的信息] "
            
            # 添加上下文信息
            context = ""
            if "context" in memory:
                context = f" (备注: {memory['context']})"
            
            formatted_memories.append(f"{prefix}[{timestamp}] {role}: {content}{context}")
        
        # 添加一个简短的介绍
        header = "系统记忆:"
        formatted_text = header + "\n" + "\n".join(formatted_memories)
        
        return formatted_text
    
    def perform_memory_maintenance(self):
        """执行记忆维护任务"""
        if self.memory_manager:
            self.logger.info("🧠 开始执行记忆维护...")
            self.memory_manager.consolidate_memories()
            self.logger.info("✅ 记忆维护完成") 