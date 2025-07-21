#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estia AI 系统综合验证测试
基于 test_complete_14_step_workflow.py 的增强版本
专门设计用于避免IDE终端问题，提供更详细的测试和验证

特点：
1. 自动选择最佳系统版本
2. 详细的错误处理和日志记录
3. 全面的功能验证
4. 性能和稳定性测试
5. 生成详细的测试报告
"""

import os
import sys
import time
import json
import logging
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置详细日志
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class EstiaSystemValidator:
    """Estia系统验证器"""
    
    def __init__(self):
        self.memory_system = None
        self.test_results = {}
        self.performance_metrics = {}
        self.start_time = None
        self.system_version = None
        
    def log_test_start(self, test_name):
        """记录测试开始"""
        logger.info(f"🧪 开始测试: {test_name}")
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print(f"{'='*60}")
        return time.time()
    
    def log_test_result(self, test_name, success, details=None, duration=None):
        """记录测试结果"""
        status = "✅ 成功" if success else "❌ 失败"
        self.test_results[test_name] = {
            'success': success,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"{status}: {test_name}")
        if details:
            logger.info(f"详情: {details}")
        if duration:
            logger.info(f"耗时: {duration:.3f}秒")
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   详情: {details}")
        if duration:
            print(f"   耗时: {duration:.3f}秒")
    
    def test_system_initialization(self):
        """测试系统初始化"""
        start_time = self.log_test_start("系统初始化测试")
        
        try:
            # 尝试导入不同版本的系统
            versions_to_try = [
                ("v6.0", "core.memory.estia_memory_v6"),
                ("v5.0", "core.memory.estia_memory_v5")
            ]
            
            for version, module_name in versions_to_try:
                try:
                    logger.info(f"尝试初始化 {version} 系统...")
                    print(f"   尝试初始化 {version} 系统...")
                    
                    module = __import__(module_name, fromlist=['create_estia_memory'])
                    create_estia_memory = getattr(module, 'create_estia_memory')
                    
                    init_start = time.time()
                    self.memory_system = create_estia_memory(
                        enable_advanced=True,
                        context_preset="balanced"
                    )
                    init_time = time.time() - init_start
                    
                    if hasattr(self.memory_system, 'initialized') and self.memory_system.initialized:
                        self.system_version = version
                        self.log_test_result(
                            "系统初始化测试", 
                            True, 
                            f"成功初始化 {version} 系统", 
                            time.time() - start_time
                        )
                        
                        # 记录初始化详情
                        print(f"   ✅ {version} 系统初始化成功")
                        print(f"   ⚡ 初始化耗时: {init_time*1000:.2f}ms")
                        print(f"   🔧 高级功能: {getattr(self.memory_system, 'enable_advanced', False)}")
                        
                        return True
                        
                except Exception as e:
                    logger.warning(f"{version} 系统初始化失败: {e}")
                    print(f"   ⚠️ {version} 系统初始化失败: {e}")
                    continue
            
            # 如果所有版本都失败
            self.log_test_result(
                "系统初始化测试", 
                False, 
                "所有系统版本初始化失败", 
                time.time() - start_time
            )
            return False
            
        except Exception as e:
            self.log_test_result(
                "系统初始化测试", 
                False, 
                f"初始化异常: {str(e)}", 
                time.time() - start_time
            )
            return False
    
    def test_core_components(self):
        """测试核心组件"""
        start_time = self.log_test_start("核心组件验证")
        
        if not self.memory_system:
            self.log_test_result("核心组件验证", False, "系统未初始化")
            return False
        
        try:
            # 定义要检查的核心组件
            core_components = {
                "数据库管理器": ['db_manager', 'database_manager'],
                "向量化器": ['vectorizer', 'vector_manager'],
                "缓存系统": ['unified_cache', 'cache_manager', 'cache'],
                "同步管理器": ['sync_flow_manager', 'sync_manager'],
                "异步管理器": ['async_flow_manager', 'async_manager'],
                "记忆存储": ['memory_store', 'memory_storage'],
                "查询处理器": ['query_processor', 'query_handler']
            }
            
            component_status = {}
            available_components = 0
            
            for component_name, possible_attrs in core_components.items():
                found = False
                for attr in possible_attrs:
                    if hasattr(self.memory_system, attr):
                        component_obj = getattr(self.memory_system, attr)
                        if component_obj is not None:
                            component_status[component_name] = f"✅ 可用 ({attr})"
                            available_components += 1
                            found = True
                            break
                
                if not found:
                    component_status[component_name] = "❌ 不可用"
                
                print(f"   {component_status[component_name]} {component_name}")
            
            # 计算组件可用率
            total_components = len(core_components)
            availability_rate = (available_components / total_components) * 100
            
            success = availability_rate >= 70  # 70%以上认为合格
            
            self.log_test_result(
                "核心组件验证", 
                success, 
                f"组件可用率: {availability_rate:.1f}% ({available_components}/{total_components})", 
                time.time() - start_time
            )
            
            return success
            
        except Exception as e:
            self.log_test_result(
                "核心组件验证", 
                False, 
                f"组件检查异常: {str(e)}", 
                time.time() - start_time
            )
            return False
    
    def test_query_enhancement(self):
        """测试查询增强功能"""
        start_time = self.log_test_start("查询增强功能测试")
        
        if not self.memory_system:
            self.log_test_result("查询增强功能测试", False, "系统未初始化")
            return False
        
        try:
            # 多样化的测试查询
            test_queries = [
                "你好，我想了解一下我的工作情况",
                "我今天工作很累，但很有成就感",
                "你能帮我记住我喜欢喝咖啡吗？",
                "我对编程很感兴趣，特别是Python",
                "请提醒我明天要开会",
                "我的爱好是什么？",
                "今天天气怎么样？",
                "帮我总结一下最近的对话"
            ]
            
            successful_queries = 0
            total_processing_time = 0
            enhancement_details = []
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n   测试查询 {i}/{len(test_queries)}: {query}")
                
                try:
                    query_start = time.time()
                    enhanced_context = self.memory_system.enhance_query(query)
                    query_time = time.time() - query_start
                    total_processing_time += query_time
                    
                    # 验证增强效果
                    if enhanced_context and len(enhanced_context) > 0:
                        enhancement_ratio = len(enhanced_context) / len(query)
                        print(f"      ⚡ 处理时间: {query_time*1000:.2f}ms")
                        print(f"      📏 增强比例: {enhancement_ratio:.2f}x")
                        print(f"      📝 上下文长度: {len(enhanced_context)}字符")
                        
                        if len(enhanced_context) >= len(query):  # 至少不能比原查询短
                            successful_queries += 1
                            enhancement_details.append({
                                'query': query,
                                'processing_time': query_time,
                                'enhancement_ratio': enhancement_ratio,
                                'context_length': len(enhanced_context)
                            })
                            print("      ✅ 查询增强成功")
                        else:
                            print("      ⚠️ 查询增强效果不明显")
                    else:
                        print("      ❌ 查询增强失败")
                        
                except Exception as e:
                    print(f"      ❌ 查询处理异常: {e}")
                    continue
            
            # 计算统计数据
            success_rate = (successful_queries / len(test_queries)) * 100
            avg_processing_time = total_processing_time / len(test_queries)
            
            # 记录性能指标
            self.performance_metrics['query_enhancement'] = {
                'success_rate': success_rate,
                'avg_processing_time': avg_processing_time,
                'total_queries': len(test_queries),
                'successful_queries': successful_queries,
                'details': enhancement_details
            }
            
            success = success_rate >= 75  # 75%以上认为合格
            
            details = f"成功率: {success_rate:.1f}%, 平均处理时间: {avg_processing_time*1000:.2f}ms"
            
            self.log_test_result(
                "查询增强功能测试", 
                success, 
                details, 
                time.time() - start_time
            )
            
            return success
            
        except Exception as e:
            self.log_test_result(
                "查询增强功能测试", 
                False, 
                f"测试异常: {str(e)}", 
                time.time() - start_time
            )
            return False
    
    def test_interaction_storage(self):
        """测试交互存储功能"""
        start_time = self.log_test_start("交互存储功能测试")
        
        if not self.memory_system:
            self.log_test_result("交互存储功能测试", False, "系统未初始化")
            return False
        
        try:
            # 测试对话对
            test_interactions = [
                ("你好，我是新用户", "欢迎！我是Estia，很高兴认识你。"),
                ("我喜欢喝咖啡", "好的，我记住了你喜欢喝咖啡。"),
                ("我是一名程序员", "了解了，你从事编程工作。"),
                ("我住在北京", "知道了，你居住在北京。"),
                ("我养了一只猫", "很棒，你有一只可爱的猫咪。"),
                ("我的生日是3月15日", "我会记住你的生日是3月15日。"),
                ("我最喜欢的颜色是蓝色", "蓝色是很好看的颜色，我记住了。"),
                ("我在学习Python编程", "Python是很优秀的编程语言。")
            ]
            
            successful_stores = 0
            storage_details = []
            total_storage_time = 0
            
            for i, (user_input, ai_response) in enumerate(test_interactions, 1):
                print(f"\n   测试交互 {i}/{len(test_interactions)}")
                print(f"      用户: {user_input}")
                print(f"      AI: {ai_response}")
                
                try:
                    # 创建会话上下文
                    session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
                    context = {
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "test_interaction": True
                    }
                    
                    # 执行存储
                    storage_start = time.time()
                    store_result = self.memory_system.store_interaction(user_input, ai_response, context)
                    storage_time = time.time() - storage_start
                    total_storage_time += storage_time
                    
                    print(f"      ⚡ 存储时间: {storage_time*1000:.2f}ms")
                    
                    # 验证存储结果
                    if store_result and not store_result.get('error'):
                        print(f"      📊 存储结果: {store_result}")
                        
                        # 检查记忆ID
                        has_user_id = store_result.get('user_memory_id') is not None
                        has_ai_id = store_result.get('ai_memory_id') is not None
                        
                        if has_user_id and has_ai_id:
                            print(f"      📝 用户记忆ID: {store_result['user_memory_id']}")
                            print(f"      🤖 AI记忆ID: {store_result['ai_memory_id']}")
                            print("      ✅ 交互存储成功")
                            successful_stores += 1
                            
                            storage_details.append({
                                'user_input': user_input,
                                'ai_response': ai_response,
                                'storage_time': storage_time,
                                'user_memory_id': store_result['user_memory_id'],
                                'ai_memory_id': store_result['ai_memory_id']
                            })
                        else:
                            print("      ⚠️ 记忆ID缺失")
                    else:
                        error_msg = store_result.get('error', '未知错误') if store_result else '存储返回空结果'
                        print(f"      ❌ 存储失败: {error_msg}")
                        
                except Exception as e:
                    print(f"      ❌ 存储异常: {e}")
                    continue
            
            # 等待异步处理
            print("\n   ⏳ 等待异步处理完成...")
            time.sleep(3)
            
            # 计算统计数据
            success_rate = (successful_stores / len(test_interactions)) * 100
            avg_storage_time = total_storage_time / len(test_interactions)
            
            # 记录性能指标
            self.performance_metrics['interaction_storage'] = {
                'success_rate': success_rate,
                'avg_storage_time': avg_storage_time,
                'total_interactions': len(test_interactions),
                'successful_stores': successful_stores,
                'details': storage_details
            }
            
            success = success_rate >= 80  # 80%以上认为合格
            
            details = f"成功率: {success_rate:.1f}%, 平均存储时间: {avg_storage_time*1000:.2f}ms"
            
            self.log_test_result(
                "交互存储功能测试", 
                success, 
                details, 
                time.time() - start_time
            )
            
            return success
            
        except Exception as e:
            self.log_test_result(
                "交互存储功能测试", 
                False, 
                f"测试异常: {str(e)}", 
                time.time() - start_time
            )
            return False
    
    def test_memory_retrieval(self):
        """测试记忆检索功能"""
        start_time = self.log_test_start("记忆检索功能测试")
        
        if not self.memory_system:
            self.log_test_result("记忆检索功能测试", False, "系统未初始化")
            return False
        
        try:
            # 基于之前存储的内容进行检索测试
            retrieval_tests = [
                {
                    "query": "我喜欢什么饮品？",
                    "expected_keywords": ["咖啡"],
                    "description": "应该能回忆起咖啡偏好"
                },
                {
                    "query": "我的职业是什么？",
                    "expected_keywords": ["程序员", "编程"],
                    "description": "应该能回忆起职业信息"
                },
                {
                    "query": "我住在哪里？",
                    "expected_keywords": ["北京"],
                    "description": "应该能回忆起居住地"
                },
                {
                    "query": "我养了什么宠物？",
                    "expected_keywords": ["猫"],
                    "description": "应该能回忆起宠物信息"
                },
                {
                    "query": "我的生日是什么时候？",
                    "expected_keywords": ["3月15日", "3月", "15日"],
                    "description": "应该能回忆起生日信息"
                }
            ]
            
            successful_retrievals = 0
            retrieval_details = []
            
            for i, test in enumerate(retrieval_tests, 1):
                print(f"\n   检索测试 {i}/{len(retrieval_tests)}: {test['query']}")
                print(f"      期望: {test['description']}")
                
                try:
                    retrieval_start = time.time()
                    enhanced_context = self.memory_system.enhance_query(test['query'])
                    retrieval_time = time.time() - retrieval_start
                    
                    print(f"      ⚡ 检索时间: {retrieval_time*1000:.2f}ms")
                    print(f"      📏 上下文长度: {len(enhanced_context)}字符")
                    
                    # 检查是否包含期望的关键词
                    found_keywords = []
                    for keyword in test['expected_keywords']:
                        if keyword in enhanced_context:
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"      ✅ 发现相关关键词: {found_keywords}")
                        successful_retrievals += 1
                        
                        retrieval_details.append({
                            'query': test['query'],
                            'expected_keywords': test['expected_keywords'],
                            'found_keywords': found_keywords,
                            'retrieval_time': retrieval_time,
                            'context_length': len(enhanced_context)
                        })
                    else:
                        print(f"      ❌ 未发现期望关键词: {test['expected_keywords']}")
                        print(f"      📝 上下文预览: {enhanced_context[:200]}...")
                        
                except Exception as e:
                    print(f"      ❌ 检索异常: {e}")
                    continue
            
            # 计算统计数据
            success_rate = (successful_retrievals / len(retrieval_tests)) * 100
            
            # 记录性能指标
            self.performance_metrics['memory_retrieval'] = {
                'success_rate': success_rate,
                'total_tests': len(retrieval_tests),
                'successful_retrievals': successful_retrievals,
                'details': retrieval_details
            }
            
            success = success_rate >= 60  # 60%以上认为合格（记忆检索相对困难）
            
            details = f"成功率: {success_rate:.1f}% ({successful_retrievals}/{len(retrieval_tests)})"
            
            self.log_test_result(
                "记忆检索功能测试", 
                success, 
                details, 
                time.time() - start_time
            )
            
            return success
            
        except Exception as e:
            self.log_test_result(
                "记忆检索功能测试", 
                False, 
                f"测试异常: {str(e)}", 
                time.time() - start_time
            )
            return False
    
    def test_system_statistics(self):
        """测试系统统计功能"""
        start_time = self.log_test_start("系统统计功能测试")
        
        if not self.memory_system:
            self.log_test_result("系统统计功能测试", False, "系统未初始化")
            return False
        
        try:
            # 获取系统统计
            print("   获取系统统计...")
            system_stats = self.memory_system.get_system_stats()
            
            if system_stats:
                print(f"   📊 系统版本: {system_stats.get('system_version', self.system_version)}")
                
                perf_stats = system_stats.get('performance_stats', {})
                print(f"   📈 查询总数: {perf_stats.get('total_queries', 0)}")
                print(f"   💾 存储总数: {perf_stats.get('total_stores', 0)}")
                print(f"   ⏱️ 平均响应时间: {perf_stats.get('avg_response_time', 0)*1000:.2f}ms")
                
                # 获取缓存统计
                print("\n   获取缓存统计...")
                cache_stats = self.memory_system.get_cache_stats()
                
                if cache_stats:
                    print(f"   📊 缓存统计: {cache_stats}")
                    
                    # 检查缓存命中率
                    cache_hit_ratio = None
                    if isinstance(cache_stats, dict):
                        # 尝试不同的缓存统计格式
                        for key in ['manager', 'unified', 'cache']:
                            if key in cache_stats and isinstance(cache_stats[key], dict):
                                cache_hit_ratio = cache_stats[key].get('hit_ratio')
                                if cache_hit_ratio is not None:
                                    break
                    
                    if cache_hit_ratio is not None:
                        print(f"   🎯 缓存命中率: {cache_hit_ratio:.2%}")
                else:
                    print("   ⚠️ 缓存统计不可用")
                
                # 获取记忆搜索工具
                print("\n   获取记忆搜索工具...")
                try:
                    search_tools = self.memory_system.get_memory_search_tools()
                    print(f"   🔍 可用工具数量: {len(search_tools)}")
                    
                    if search_tools:
                        for tool in search_tools[:3]:  # 只显示前3个工具
                            tool_name = tool.get('name', '未知工具')
                            print(f"      • {tool_name}")
                except Exception as e:
                    print(f"   ⚠️ 获取搜索工具失败: {e}")
                
                self.log_test_result(
                    "系统统计功能测试", 
                    True, 
                    "成功获取系统统计信息", 
                    time.time() - start_time
                )
                return True
            else:
                self.log_test_result(
                    "系统统计功能测试", 
                    False, 
                    "无法获取系统统计", 
                    time.time() - start_time
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "系统统计功能测试", 
                False, 
                f"测试异常: {str(e)}", 
                time.time() - start_time
            )
            return False
    
    def test_performance_benchmarks(self):
        """性能基准测试"""
        start_time = self.log_test_start("性能基准测试")
        
        if not self.memory_system:
            self.log_test_result("性能基准测试", False, "系统未初始化")
            return False
        
        try:
            # 性能测试配置
            test_query = "这是一个性能基准测试查询"
            test_iterations = 50  # 减少迭代次数避免超时
            
            print(f"   执行 {test_iterations} 次查询测试...")
            
            times = []
            errors = 0
            
            for i in range(test_iterations):
                try:
                    query_start = time.time()
                    self.memory_system.enhance_query(test_query)
                    query_end = time.time()
                    times.append((query_end - query_start) * 1000)
                    
                    if (i + 1) % 10 == 0:
                        print(f"      完成 {i + 1}/{test_iterations} 次测试")
                        
                except Exception as e:
                    errors += 1
                    logger.warning(f"性能测试第{i+1}次查询失败: {e}")
            
            if not times:
                self.log_test_result(
                    "性能基准测试", 
                    False, 
                    "所有查询都失败了", 
                    time.time() - start_time
                )
                return False
            
            # 计算统计数据
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            success_rate = ((test_iterations - errors) / test_iterations) * 100
            
            print(f"\n   📊 性能统计:")
            print(f"      平均响应时间: {avg_time:.2f}ms")
            print(f"      最快响应时间: {min_time:.2f}ms")
            print(f"      最慢响应时间: {max_time:.2f}ms")
            print(f"      成功率: {success_rate:.1f}%")
            print(f"      QPS: {1000/avg_time:.2f}")
            
            # 性能等级评估
            if avg_time < 50:
                performance_grade = "优秀"
            elif avg_time < 100:
                performance_grade = "良好"
            elif avg_time < 200:
                performance_grade = "一般"
            else:
                performance_grade = "需要优化"
            
            print(f"      性能等级: {performance_grade}")
            
            # 记录性能指标
            self.performance_metrics['benchmark'] = {
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'success_rate': success_rate,
                'qps': 1000/avg_time,
                'performance_grade': performance_grade,
                'test_iterations': test_iterations,
                'errors': errors
            }
            
            # 判断是否通过（平均时间<200ms且成功率>90%）
            success = avg_time < 200 and success_rate > 90
            
            details = f"平均时间: {avg_time:.2f}ms, 成功率: {success_rate:.1f}%, 等级: {performance_grade}"
            
            self.log_test_result(
                "性能基准测试", 
                success, 
                details, 
                time.time() - start_time
            )
            
            return success
            
        except Exception as e:
            self.log_test_result(
                "性能基准测试", 
                False, 
                f"测试异常: {str(e)}", 
                time.time() - start_time
            )
            return False
    
    def generate_comprehensive_report(self):
        """生成综合测试报告"""
        print(f"\n{'='*80}")
        print("📋 Estia AI 系统综合验证报告")
        print(f"{'='*80}")
        
        # 基本信息
        print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 系统版本: {self.system_version or '未知'}")
        print(f"📁 日志文件: {log_file}")
        
        # 测试结果总览
        print(f"\n📊 测试结果总览:")
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        overall_success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"   总测试数: {total_tests}")
        print(f"   通过测试: {passed_tests}")
        print(f"   失败测试: {total_tests - passed_tests}")
        print(f"   总体成功率: {overall_success_rate:.1f}%")
        
        # 详细测试结果
        print(f"\n📋 详细测试结果:")
        for test_name, result in self.test_results.items():
            status = "✅" if result['success'] else "❌"
            duration = f" ({result['duration']:.3f}s)" if result['duration'] else ""
            print(f"   {status} {test_name}{duration}")
            if result['details']:
                print(f"      {result['details']}")
        
        # 性能指标总结
        if self.performance_metrics:
            print(f"\n⚡ 性能指标总结:")
            
            if 'query_enhancement' in self.performance_metrics:
                qe = self.performance_metrics['query_enhancement']
                print(f"   查询增强: {qe['success_rate']:.1f}% 成功率, {qe['avg_processing_time']*1000:.2f}ms 平均时间")
            
            if 'interaction_storage' in self.performance_metrics:
                ist = self.performance_metrics['interaction_storage']
                print(f"   交互存储: {ist['success_rate']:.1f}% 成功率, {ist['avg_storage_time']*1000:.2f}ms 平均时间")
            
            if 'memory_retrieval' in self.performance_metrics:
                mr = self.performance_metrics['memory_retrieval']
                print(f"   记忆检索: {mr['success_rate']:.1f}% 成功率")
            
            if 'benchmark' in self.performance_metrics:
                bm = self.performance_metrics['benchmark']
                print(f"   性能基准: {bm['avg_time']:.2f}ms 平均时间, {bm['qps']:.2f} QPS, {bm['performance_grade']}")
        
        # 总体评估
        print(f"\n🎯 总体评估:")
        if overall_success_rate >= 90:
            grade = "优秀"
            emoji = "🎉"
        elif overall_success_rate >= 75:
            grade = "良好"
            emoji = "✅"
        elif overall_success_rate >= 60:
            grade = "一般"
            emoji = "⚠️"
        else:
            grade = "需要改进"
            emoji = "❌"
        
        print(f"   {emoji} 系统状态: {grade}")
        print(f"   📈 成功率: {overall_success_rate:.1f}%")
        
        # 建议
        print(f"\n💡 建议:")
        if overall_success_rate >= 90:
            print("   • 系统运行状态优秀，可以正常使用")
            print("   • 建议定期进行性能监控")
        elif overall_success_rate >= 75:
            print("   • 系统运行状态良好，大部分功能正常")
            print("   • 建议关注失败的测试项目")
        elif overall_success_rate >= 60:
            print("   • 系统存在一些问题，建议进行优化")
            print("   • 重点关注失败的核心功能")
        else:
            print("   • 系统存在严重问题，需要立即修复")
            print("   • 建议检查系统配置和依赖")
        
        # 保存详细报告到文件
        report_file = log_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'system_version': self.system_version,
            'test_results': self.test_results,
            'performance_metrics': self.performance_metrics,
            'overall_success_rate': overall_success_rate,
            'grade': grade,
            'log_file': str(log_file)
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            print(f"\n📄 详细报告已保存: {report_file}")
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
        
        return overall_success_rate >= 75  # 75%以上认为整体通过
    
    def run_comprehensive_validation(self):
        """运行综合验证"""
        self.start_time = time.time()
        
        print("🚀 Estia AI 系统综合验证开始")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"日志文件: {log_file}")
        print("="*80)
        
        try:
            # 按顺序执行所有测试
            test_sequence = [
                self.test_system_initialization,
                self.test_core_components,
                self.test_query_enhancement,
                self.test_interaction_storage,
                self.test_memory_retrieval,
                self.test_system_statistics,
                self.test_performance_benchmarks
            ]
            
            for test_func in test_sequence:
                try:
                    test_func()
                except Exception as e:
                    logger.error(f"测试函数 {test_func.__name__} 执行异常: {e}")
                    logger.error(traceback.format_exc())
                    continue
            
            # 生成综合报告
            overall_success = self.generate_comprehensive_report()
            
            total_time = time.time() - self.start_time
            print(f"\n⏱️ 总测试时间: {total_time:.2f}秒")
            print("🏁 综合验证完成")
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\n⏹️ 测试被用户中断")
            logger.info("测试被用户中断")
            return False
        except Exception as e:
            print(f"\n❌ 验证过程异常: {e}")
            logger.error(f"验证过程异常: {e}")
            logger.error(traceback.format_exc())
            return False

def main():
    """主函数"""
    print("🔍 Estia AI 系统综合验证工具")
    print("基于 test_complete_14_step_workflow.py 的增强版本")
    print("专门设计用于避免IDE终端问题")
    print("="*80)
    
    # 创建验证器
    validator = EstiaSystemValidator()
    
    # 运行综合验证
    success = validator.run_comprehensive_validation()
    
    # 退出码
    exit_code = 0 if success else 1
    print(f"\n退出码: {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)