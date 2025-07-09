#!/usr/bin/env python3
"""
Estia-AI 缓存系统深度测试和修复验证脚本
基于旧系统对比分析，测试新系统缓存功能完整性和性能表现

测试重点：
1. 关键词缓存功能测试
2. 深度集成效果验证
3. 性能提升测试
4. 缓存命中率分析
5. 内存使用效率测试
"""

import sys
import os
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_cache_system_completeness():
    """测试缓存系统功能完整性"""
    print("=" * 60)
    print("🔍 测试1: 缓存系统功能完整性")
    print("=" * 60)
    
    test_results = {
        "unified_cache_manager": False,
        "keyword_cache": False,
        "multi_level_cache": False,
        "smart_promotion": False,
        "performance_monitoring": False,
        "deep_integration": False
    }
    
    try:
        # 1. 测试统一缓存管理器
        print("\n1.1 测试统一缓存管理器...")
        from core.memory.shared.caching.cache_manager import UnifiedCacheManager
        
        cache_manager = UnifiedCacheManager.get_instance()
        print(f"✅ 统一缓存管理器: {type(cache_manager).__name__}")
        test_results["unified_cache_manager"] = True
        
        # 检查基础方法
        basic_methods = ['get', 'put', 'delete', 'clear', 'get_stats']
        for method in basic_methods:
            if hasattr(cache_manager, method):
                print(f"   ✅ {method} 方法存在")
            else:
                print(f"   ❌ {method} 方法缺失")
        
        # 2. 测试关键词缓存功能
        print("\n1.2 测试关键词缓存功能...")
        if hasattr(cache_manager, 'search_by_content'):
            print("   ✅ search_by_content 方法存在")
            
            # 测试关键词提取
            test_query = "今天天气很好，我想出去散步"
            try:
                results = cache_manager.search_by_content(test_query)
                print(f"   ✅ 关键词搜索功能正常，返回 {len(results)} 个结果")
                test_results["keyword_cache"] = True
            except Exception as e:
                print(f"   ❌ 关键词搜索功能异常: {e}")
        else:
            print("   ❌ search_by_content 方法缺失")
        
        # 3. 测试多级缓存
        print("\n1.3 测试多级缓存...")
        if hasattr(cache_manager, 'caches'):
            cache_levels = len(cache_manager.caches) if cache_manager.caches else 0
            print(f"   缓存级别数量: {cache_levels}")
            
            if cache_levels >= 3:
                print("   ✅ 多级缓存功能完整")
                test_results["multi_level_cache"] = True
            else:
                print("   ❌ 多级缓存功能不完整")
        else:
            print("   ❌ 缓存级别信息不可用")
        
        # 4. 测试智能提升
        print("\n1.4 测试智能提升...")
        if hasattr(cache_manager, 'record_memory_access'):
            try:
                cache_manager.record_memory_access("test_memory", 5.0)
                print("   ✅ 记忆访问记录功能正常")
                test_results["smart_promotion"] = True
            except Exception as e:
                print(f"   ❌ 记忆访问记录功能异常: {e}")
        else:
            print("   ❌ record_memory_access 方法缺失")
        
        # 5. 测试性能监控
        print("\n1.5 测试性能监控...")
        try:
            stats = cache_manager.get_stats()
            print(f"   ✅ 性能统计获取成功: {type(stats).__name__}")
            print(f"   统计信息: {json.dumps(stats, indent=2, default=str)}")
            test_results["performance_monitoring"] = True
        except Exception as e:
            print(f"   ❌ 性能统计获取失败: {e}")
        
    except Exception as e:
        print(f"❌ 缓存系统测试失败: {e}")
        return test_results
    
    # 计算完整性分数
    completeness_score = sum(test_results.values()) / len(test_results)
    print(f"\n📊 缓存系统完整性得分: {completeness_score:.2%}")
    
    return test_results

def test_cache_integration_depth():
    """测试缓存系统集成深度"""
    print("\n" + "=" * 60)
    print("🔗 测试2: 缓存系统集成深度")
    print("=" * 60)
    
    integration_results = {
        "vectorizer_integration": False,
        "memory_system_integration": False,
        "retrieval_integration": False,
        "auto_caching": False
    }
    
    try:
        # 1. 测试向量化器集成
        print("\n2.1 测试向量化器集成...")
        from core.memory.estia_memory_v5 import EstiaMemorySystem
        
        memory_system = EstiaMemorySystem()
        
        # 检查统一缓存是否正确初始化
        if hasattr(memory_system, 'unified_cache') and memory_system.unified_cache:
            print("   ✅ 统一缓存在记忆系统中正确初始化")
            integration_results["memory_system_integration"] = True
        else:
            print("   ❌ 统一缓存在记忆系统中未正确初始化")
        
        # 2. 测试向量化缓存
        print("\n2.2 测试向量化缓存...")
        if hasattr(memory_system, 'vectorizer') and memory_system.vectorizer:
            try:
                # 测试向量化缓存
                test_text = "这是一个测试文本"
                
                # 第一次向量化
                start_time = time.time()
                vector1 = memory_system.vectorizer.encode(test_text)
                first_time = time.time() - start_time
                
                # 第二次向量化（应该命中缓存）
                start_time = time.time()
                vector2 = memory_system.vectorizer.encode(test_text)
                second_time = time.time() - start_time
                
                print(f"   第一次向量化时间: {first_time:.4f}s")
                print(f"   第二次向量化时间: {second_time:.4f}s")
                
                if second_time < first_time * 0.1:  # 第二次应该快得多
                    print("   ✅ 向量化缓存工作正常")
                    integration_results["vectorizer_integration"] = True
                else:
                    print("   ❌ 向量化缓存未生效")
                
            except Exception as e:
                print(f"   ❌ 向量化缓存测试失败: {e}")
        else:
            print("   ❌ 向量化器未正确初始化")
        
        # 3. 测试自动缓存
        print("\n2.3 测试自动缓存...")
        try:
            # 测试查询增强的缓存效果
            test_query = "今天天气怎么样？"
            
            # 第一次查询
            start_time = time.time()
            result1 = memory_system.enhance_query(test_query)
            first_query_time = time.time() - start_time
            
            # 第二次查询（应该有缓存效果）
            start_time = time.time()
            result2 = memory_system.enhance_query(test_query)
            second_query_time = time.time() - start_time
            
            print(f"   第一次查询时间: {first_query_time:.4f}s")
            print(f"   第二次查询时间: {second_query_time:.4f}s")
            
            if second_query_time < first_query_time * 0.8:  # 第二次应该更快
                print("   ✅ 查询缓存工作正常")
                integration_results["auto_caching"] = True
            else:
                print("   ❌ 查询缓存效果不明显")
                
        except Exception as e:
            print(f"   ❌ 自动缓存测试失败: {e}")
        
    except Exception as e:
        print(f"❌ 集成深度测试失败: {e}")
        return integration_results
    
    # 计算集成深度分数
    integration_score = sum(integration_results.values()) / len(integration_results)
    print(f"\n📊 缓存系统集成深度得分: {integration_score:.2%}")
    
    return integration_results

def test_cache_performance():
    """测试缓存性能表现"""
    print("\n" + "=" * 60)
    print("🚀 测试3: 缓存性能表现")
    print("=" * 60)
    
    performance_results = {
        "cache_hit_rate": 0.0,
        "average_speedup": 0.0,
        "memory_efficiency": 0.0,
        "concurrent_performance": 0.0
    }
    
    try:
        from core.memory.estia_memory_v5 import EstiaMemorySystem
        
        memory_system = EstiaMemorySystem()
        
        # 1. 测试缓存命中率
        print("\n3.1 测试缓存命中率...")
        
        test_queries = [
            "今天天气怎么样？",
            "我想了解人工智能",
            "帮我写一个Python函数",
            "什么是机器学习？",
            "如何提高工作效率？"
        ]
        
        # 预热缓存
        for query in test_queries:
            try:
                memory_system.enhance_query(query)
            except:
                pass
        
        # 测试命中率
        hits = 0
        total_tests = len(test_queries) * 2  # 每个查询测试两次
        
        for query in test_queries:
            for _ in range(2):  # 重复查询测试缓存命中
                try:
                    start_time = time.time()
                    result = memory_system.enhance_query(query)
                    query_time = time.time() - start_time
                    
                    if query_time < 0.1:  # 小于100ms认为命中缓存
                        hits += 1
                        
                except Exception as e:
                    print(f"   查询失败: {e}")
        
        hit_rate = hits / total_tests if total_tests > 0 else 0
        performance_results["cache_hit_rate"] = hit_rate
        print(f"   缓存命中率: {hit_rate:.2%}")
        
        # 2. 测试平均加速比
        print("\n3.2 测试平均加速比...")
        
        speedup_ratios = []
        for query in test_queries[:3]:  # 取前3个查询测试
            try:
                # 第一次查询（冷启动）
                start_time = time.time()
                memory_system.enhance_query(query)
                cold_time = time.time() - start_time
                
                # 第二次查询（热缓存）
                start_time = time.time()
                memory_system.enhance_query(query)
                hot_time = time.time() - start_time
                
                if hot_time > 0:
                    speedup = cold_time / hot_time
                    speedup_ratios.append(speedup)
                    print(f"   {query[:20]}... 加速比: {speedup:.2f}x")
                
            except Exception as e:
                print(f"   查询失败: {e}")
        
        avg_speedup = sum(speedup_ratios) / len(speedup_ratios) if speedup_ratios else 0
        performance_results["average_speedup"] = avg_speedup
        print(f"   平均加速比: {avg_speedup:.2f}x")
        
        # 3. 测试内存效率
        print("\n3.3 测试内存效率...")
        
        try:
            import psutil
            process = psutil.Process()
            
            # 获取缓存前内存使用
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行大量缓存操作
            for i in range(100):
                query = f"测试查询 {i}"
                try:
                    memory_system.enhance_query(query)
                except:
                    pass
            
            # 获取缓存后内存使用
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = memory_after - memory_before
            
            print(f"   缓存前内存使用: {memory_before:.2f}MB")
            print(f"   缓存后内存使用: {memory_after:.2f}MB")
            print(f"   内存增量: {memory_increase:.2f}MB")
            
            # 计算内存效率（内存增量越小越好）
            memory_efficiency = max(0, 1 - memory_increase / 100)  # 假设100MB为基准
            performance_results["memory_efficiency"] = memory_efficiency
            print(f"   内存效率: {memory_efficiency:.2%}")
            
        except ImportError:
            print("   ❌ psutil 未安装，跳过内存效率测试")
        except Exception as e:
            print(f"   ❌ 内存效率测试失败: {e}")
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return performance_results
    
    # 计算综合性能分数
    performance_score = (
        performance_results["cache_hit_rate"] * 0.3 +
        min(performance_results["average_speedup"] / 10, 1.0) * 0.4 +
        performance_results["memory_efficiency"] * 0.3
    )
    
    print(f"\n📊 缓存性能综合得分: {performance_score:.2%}")
    
    return performance_results

def analyze_cache_issues():
    """分析缓存系统问题"""
    print("\n" + "=" * 60)
    print("🔍 测试4: 缓存系统问题分析")
    print("=" * 60)
    
    issues = []
    
    try:
        # 1. 检查关键词缓存功能
        print("\n4.1 检查关键词缓存功能...")
        
        from core.memory.shared.caching.cache_manager import UnifiedCacheManager
        cache_manager = UnifiedCacheManager.get_instance()
        
        # 检查关键词相关方法
        keyword_methods = ['_extract_keywords', 'keyword_cache', '_update_keyword_cache']
        missing_keyword_features = []
        
        for method in keyword_methods:
            if not hasattr(cache_manager, method):
                missing_keyword_features.append(method)
        
        if missing_keyword_features:
            issues.append({
                "type": "功能缺失",
                "severity": "高",
                "description": "关键词缓存功能缺失",
                "missing_features": missing_keyword_features,
                "impact": "内容搜索性能下降，无法快速定位相关记忆"
            })
        
        # 2. 检查深度集成
        print("\n4.2 检查深度集成...")
        
        from core.memory.estia_memory_v5 import EstiaMemorySystem
        memory_system = EstiaMemorySystem()
        
        # 检查核心方法中的缓存使用
        enhance_query_code = None
        try:
            import inspect
            enhance_query_code = inspect.getsource(memory_system.enhance_query)
        except:
            pass
        
        if enhance_query_code:
            cache_usage_count = enhance_query_code.count('cache')
            if cache_usage_count < 3:  # 旧系统在3个关键位置使用缓存
                issues.append({
                    "type": "集成深度不足",
                    "severity": "中",
                    "description": "enhance_query方法中缓存使用不足",
                    "current_usage": cache_usage_count,
                    "expected_usage": 3,
                    "impact": "缓存优势未充分发挥，性能提升效果不明显"
                })
        
        # 3. 检查性能监控
        print("\n4.3 检查性能监控...")
        
        try:
            stats = cache_manager.get_stats()
            
            # 检查统计信息完整性
            expected_stats = [
                'hit_rate', 'miss_rate', 'total_operations',
                'cache_levels', 'memory_usage', 'performance_metrics'
            ]
            
            missing_stats = []
            for stat in expected_stats:
                if stat not in str(stats):
                    missing_stats.append(stat)
            
            if missing_stats:
                issues.append({
                    "type": "监控不完整",
                    "severity": "低",
                    "description": "性能监控信息不完整",
                    "missing_stats": missing_stats,
                    "impact": "难以准确评估缓存性能和调优"
                })
                
        except Exception as e:
            issues.append({
                "type": "监控失败",
                "severity": "中",
                "description": "性能监控功能异常",
                "error": str(e),
                "impact": "无法获取缓存性能统计"
            })
        
        # 4. 检查缓存一致性
        print("\n4.4 检查缓存一致性...")
        
        # 测试缓存一致性
        test_key = "consistency_test"
        test_value = "test_value"
        
        try:
            # 写入缓存
            cache_manager.put(test_key, test_value)
            
            # 从不同路径读取
            value1 = cache_manager.get(test_key)
            
            # 检查一致性
            if value1 != test_value:
                issues.append({
                    "type": "一致性问题",
                    "severity": "高",
                    "description": "缓存读写一致性问题",
                    "expected": test_value,
                    "actual": value1,
                    "impact": "数据不一致可能导致错误结果"
                })
            
        except Exception as e:
            issues.append({
                "type": "一致性测试失败",
                "severity": "中",
                "description": "缓存一致性测试失败",
                "error": str(e),
                "impact": "无法验证缓存一致性"
            })
        
    except Exception as e:
        issues.append({
            "type": "系统错误",
            "severity": "高",
            "description": "缓存系统分析失败",
            "error": str(e),
            "impact": "无法正常分析缓存系统"
        })
    
    # 按严重程度排序
    severity_order = {"高": 3, "中": 2, "低": 1}
    issues.sort(key=lambda x: severity_order.get(x["severity"], 0), reverse=True)
    
    print(f"\n📋 发现 {len(issues)} 个问题:")
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. 【{issue['severity']}】{issue['type']}: {issue['description']}")
        if 'impact' in issue:
            print(f"   影响: {issue['impact']}")
    
    return issues

def generate_optimization_plan(test_results, integration_results, performance_results, issues):
    """生成优化方案"""
    print("\n" + "=" * 60)
    print("🎯 缓存系统优化方案")
    print("=" * 60)
    
    optimization_plan = {
        "short_term": [],  # 1-2周
        "medium_term": [], # 2-4周
        "long_term": []    # 1-2月
    }
    
    # 根据测试结果生成优化建议
    
    # 1. 短期优化（基于关键问题）
    if not test_results.get("keyword_cache", False):
        optimization_plan["short_term"].append({
            "task": "恢复关键词缓存功能",
            "priority": "高",
            "estimated_time": "3-5天",
            "description": "实现关键词提取、索引和搜索功能",
            "implementation": [
                "在 UnifiedCacheManager 中添加 KeywordCache 类",
                "实现 _extract_keywords 方法",
                "实现 _update_keyword_cache 方法",
                "在 search_by_content 中集成关键词搜索"
            ]
        })
    
    if integration_results.get("auto_caching", False) == False:
        optimization_plan["short_term"].append({
            "task": "增强系统集成深度",
            "priority": "高",
            "estimated_time": "2-3天",
            "description": "在核心流程中深度集成缓存功能",
            "implementation": [
                "在 enhance_query 方法中添加向量缓存检查",
                "实现记忆访问记录和缓存更新",
                "添加查询结果缓存机制"
            ]
        })
    
    # 2. 中期优化（基于性能提升）
    if performance_results.get("average_speedup", 0) < 5.0:
        optimization_plan["medium_term"].append({
            "task": "优化缓存性能",
            "priority": "中",
            "estimated_time": "1-2周",
            "description": "提升缓存命中率和访问速度",
            "implementation": [
                "实现智能缓存预加载",
                "优化缓存淘汰策略",
                "添加缓存预测算法",
                "实现批量缓存操作"
            ]
        })
    
    if performance_results.get("memory_efficiency", 0) < 0.8:
        optimization_plan["medium_term"].append({
            "task": "内存使用优化",
            "priority": "中",
            "estimated_time": "1周",
            "description": "优化内存使用效率",
            "implementation": [
                "实现缓存压缩算法",
                "优化数据结构设计",
                "添加内存监控和告警",
                "实现动态内存调整"
            ]
        })
    
    # 3. 长期优化（基于扩展性）
    optimization_plan["long_term"].append({
        "task": "分布式缓存支持",
        "priority": "低",
        "estimated_time": "2-3周",
        "description": "支持分布式缓存架构",
        "implementation": [
            "设计分布式缓存协议",
            "实现缓存同步机制",
            "添加节点发现和管理",
            "实现数据分片和负载均衡"
        ]
    })
    
    optimization_plan["long_term"].append({
        "task": "智能缓存管理",
        "priority": "低",
        "estimated_time": "3-4周",
        "description": "实现基于AI的缓存管理",
        "implementation": [
            "训练缓存访问预测模型",
            "实现自适应缓存策略",
            "添加异常检测和自动修复",
            "实现缓存效果评估和优化"
        ]
    })
    
    # 输出优化方案
    for term, tasks in optimization_plan.items():
        term_name = {"short_term": "短期", "medium_term": "中期", "long_term": "长期"}[term]
        print(f"\n🎯 {term_name}优化任务:")
        
        for i, task in enumerate(tasks, 1):
            print(f"\n{i}. {task['task']} 【{task['priority']}】")
            print(f"   预估时间: {task['estimated_time']}")
            print(f"   描述: {task['description']}")
            if 'implementation' in task:
                print("   实现步骤:")
                for step in task['implementation']:
                    print(f"     - {step}")
    
    return optimization_plan

def main():
    """主测试函数"""
    print("🚀 Estia-AI 缓存系统深度分析测试")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 执行测试
    test_results = test_cache_system_completeness()
    integration_results = test_cache_integration_depth()
    performance_results = test_cache_performance()
    issues = analyze_cache_issues()
    
    # 生成优化方案
    optimization_plan = generate_optimization_plan(
        test_results, integration_results, performance_results, issues
    )
    
    # 生成总结报告
    print("\n" + "=" * 80)
    print("📊 测试总结报告")
    print("=" * 80)
    
    # 计算总体评分
    completeness_score = sum(test_results.values()) / len(test_results)
    integration_score = sum(integration_results.values()) / len(integration_results)
    performance_score = (
        performance_results.get("cache_hit_rate", 0) * 0.3 +
        min(performance_results.get("average_speedup", 0) / 10, 1.0) * 0.4 +
        performance_results.get("memory_efficiency", 0) * 0.3
    )
    
    overall_score = (completeness_score + integration_score + performance_score) / 3
    
    print(f"\n📈 综合评分:")
    print(f"   功能完整性: {completeness_score:.2%}")
    print(f"   集成深度: {integration_score:.2%}")
    print(f"   性能表现: {performance_score:.2%}")
    print(f"   总体评分: {overall_score:.2%}")
    
    # 问题统计
    high_issues = sum(1 for issue in issues if issue["severity"] == "高")
    medium_issues = sum(1 for issue in issues if issue["severity"] == "中")
    low_issues = sum(1 for issue in issues if issue["severity"] == "低")
    
    print(f"\n🚨 问题统计:")
    print(f"   高优先级问题: {high_issues}")
    print(f"   中优先级问题: {medium_issues}")
    print(f"   低优先级问题: {low_issues}")
    
    # 建议
    print(f"\n💡 建议:")
    if overall_score < 0.5:
        print("   缓存系统需要重大改进，建议优先执行短期优化任务")
    elif overall_score < 0.8:
        print("   缓存系统基本可用，建议按计划执行优化任务")
    else:
        print("   缓存系统表现良好，可以考虑长期优化任务")
    
    print(f"\n🎯 下一步行动:")
    print("   1. 根据优化方案执行短期任务")
    print("   2. 解决高优先级问题")
    print("   3. 持续监控缓存性能")
    print("   4. 定期重新评估和优化")
    
    print("\n" + "=" * 80)
    print("测试完成！请查看详细报告进行优化。")
    print("=" * 80)

if __name__ == "__main__":
    main()