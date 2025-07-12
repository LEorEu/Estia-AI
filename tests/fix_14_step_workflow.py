#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复14步工作流程 - 基于文档标准恢复完整功能
恢复 AssociationNetwork、HistoryRetriever、MemoryScorer 的正确初始化

基于: docs/old_estia_complete_workflow_detailed.md
目标: 让新系统v5.0完全符合文档中定义的14步工作流程
"""

import os
import re

def fix_estia_memory_v5_initialization():
    """修复 estia_memory_v5.py 中的核心组件初始化"""
    
    file_path = "core/memory/estia_memory_v5.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 保存原始文件
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 原始文件已备份到: {backup_path}")
        
        # 修复1: 在高级组件初始化部分添加缺失的核心组件
        # 找到高级组件初始化的位置
        advanced_components_pattern = r'(\s+# 🔥 可选高级组件\s+if self\.enable_advanced and components\.get\(\'db_manager\'\):\s+try:.*?FAISS搜索.*?\n)(\s+)(.*?self\.logger\.info\("✅ 高级检索组件初始化成功"\))'
        
        def replace_advanced_components(match):
            before_faiss = match.group(1)
            indent = match.group(2)
            after_faiss = match.group(3)
            
            # 添加缺失的核心组件初始化
            new_components = f"""{before_faiss}{indent}
{indent}                    # === 文档标准的核心组件初始化 ===
{indent}                    
{indent}                    # 关联网络 (Step 6 核心组件)
{indent}                    from ..old_memory.association.network import AssociationNetwork
{indent}                    association_network = AssociationNetwork(db_manager)
{indent}                    components['association_network'] = association_network
{indent}                    self.logger.info("✅ 关联网络初始化成功 (文档Step 6)")
{indent}                    
{indent}                    # 历史检索器 (Step 7 核心组件) - 使用现有的新系统实现
{indent}                    from .managers.sync_flow.context.history import HistoryRetriever
{indent}                    history_retriever = HistoryRetriever(db_manager)
{indent}                    components['history_retriever'] = history_retriever
{indent}                    self.logger.info("✅ 历史检索器初始化成功 (文档Step 7)")
{indent}                    
{indent}                    # 记忆评分器 (Step 8 核心组件) - 使用现有的新系统实现
{indent}                    from .managers.sync_flow.ranking.scorer import MemoryScorer
{indent}                    scorer = MemoryScorer()
{indent}                    components['scorer'] = scorer
{indent}                    self.logger.info("✅ 记忆评分器初始化成功 (文档Step 8)")
{indent}
{indent}                    {after_faiss}"""
            
            return new_components
        
        new_content = re.sub(advanced_components_pattern, replace_advanced_components, content, flags=re.DOTALL)
        
        if new_content == content:
            print("⚠️ 没有找到高级组件初始化部分，尝试备用方案")
            
            # 备用方案：在FAISS初始化后直接添加
            faiss_pattern = r'(components\[\'faiss_retriever\'\] = faiss_retriever\s+self\.logger\.info\("✅ 高级检索组件初始化成功"\))'
            
            def add_components_after_faiss(match):
                faiss_code = match.group(1)
                return f"""{faiss_code}
                    
                    # === 文档标准的核心组件初始化 ===
                    
                    # 关联网络 (Step 6 核心组件)
                    from ..old_memory.association.network import AssociationNetwork
                    association_network = AssociationNetwork(db_manager)
                    components['association_network'] = association_network
                    self.logger.info("✅ 关联网络初始化成功 (文档Step 6)")
                    
                    # 历史检索器 (Step 7 核心组件)
                    from .managers.sync_flow.context.history import HistoryRetriever
                    history_retriever = HistoryRetriever(db_manager)
                    components['history_retriever'] = history_retriever
                    self.logger.info("✅ 历史检索器初始化成功 (文档Step 7)")
                    
                    # 记忆评分器 (Step 8 核心组件)
                    from .managers.sync_flow.ranking.scorer import MemoryScorer
                    scorer = MemoryScorer()
                    components['scorer'] = scorer
                    self.logger.info("✅ 记忆评分器初始化成功 (文档Step 8)")"""
            
            new_content = re.sub(faiss_pattern, add_components_after_faiss, content)
        
        # 验证修改是否成功
        if 'AssociationNetwork' in new_content and 'HistoryRetriever' in new_content and 'MemoryScorer' in new_content:
            # 写入修改后的文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ estia_memory_v5.py 核心组件初始化修复完成")
            print("   - AssociationNetwork (Step 6): ✅")
            print("   - HistoryRetriever (Step 7): ✅") 
            print("   - MemoryScorer (Step 8): ✅")
            return True
        else:
            print("❌ 组件初始化添加失败")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def fix_association_network_method_name():
    """修复 AssociationNetwork 中的方法名匹配问题"""
    
    file_path = "core/old_memory/association/network.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经有 find_associated_memories 方法
        if 'def find_associated_memories(' in content:
            print("✅ find_associated_memories 方法已存在")
            return True
        
        # 在类的末尾添加别名方法
        class_end_pattern = r'(\s+def delete_association.*?return False\s+)(except Exception as e:.*?return False\s+)$'
        
        def add_alias_method(match):
            before_except = match.group(1)
            except_block = match.group(2)
            
            alias_method = """
    def find_associated_memories(self, memory_ids: List[str], depth: int = 2, 
                               max_results: int = 10, min_strength: float = 0.3) -> List[str]:
        \"\"\"
        查找关联记忆 - 为兼容同步流程管理器的调用
        
        参数:
            memory_ids: 记忆ID列表
            depth: 检索深度
            max_results: 最大结果数
            min_strength: 最小关联强度
            
        返回:
            List[str]: 关联记忆ID列表
        \"\"\"
        try:
            if not memory_ids:
                return []
            
            # 获取第一个记忆的关联
            primary_memory_id = memory_ids[0]
            related_memories = self.get_related_memories(primary_memory_id, depth, min_strength)
            
            # 提取记忆ID
            related_ids = []
            for memory in related_memories:
                memory_id = memory.get('memory_id')
                if memory_id and memory_id not in memory_ids:  # 避免重复
                    related_ids.append(memory_id)
            
            # 限制结果数量
            return related_ids[:max_results]
            
        except Exception as e:
            logger.error(f"查找关联记忆失败: {e}")
            return []

    """
            return before_except + alias_method + except_block
        
        new_content = re.sub(class_end_pattern, add_alias_method, content, flags=re.DOTALL)
        
        if new_content == content:
            # 备用方案：在文件末尾添加
            if content.strip().endswith('return False'):
                alias_method = """
    def find_associated_memories(self, memory_ids: List[str], depth: int = 2, 
                               max_results: int = 10, min_strength: float = 0.3) -> List[str]:
        \"\"\"
        查找关联记忆 - 为兼容同步流程管理器的调用
        
        参数:
            memory_ids: 记忆ID列表 
            depth: 检索深度
            max_results: 最大结果数
            min_strength: 最小关联强度
            
        返回:
            List[str]: 关联记忆ID列表
        \"\"\"
        try:
            if not memory_ids:
                return []
            
            # 获取第一个记忆的关联
            primary_memory_id = memory_ids[0]
            related_memories = self.get_related_memories(primary_memory_id, depth, min_strength)
            
            # 提取记忆ID
            related_ids = []
            for memory in related_memories:
                memory_id = memory.get('memory_id')
                if memory_id and memory_id not in memory_ids:  # 避免重复
                    related_ids.append(memory_id)
            
            # 限制结果数量
            return related_ids[:max_results]
            
        except Exception as e:
            logger.error(f"查找关联记忆失败: {e}")
            return []
"""
                new_content = content + alias_method
        
        # 验证修改
        if 'def find_associated_memories(' in new_content:
            # 写入修改后的文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ AssociationNetwork 方法名匹配修复完成")
            print("   - find_associated_memories() 方法已添加")
            return True
        else:
            print("❌ 方法名修复失败")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def create_test_script():
    """创建测试脚本验证14步工作流程"""
    
    test_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试14步工作流程 - 验证文档标准的完整流程
"""

import sys
import os
import time

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_14_step_workflow():
    """测试完整的14步工作流程"""
    
    print("🚀 开始测试14步工作流程...")
    
    try:
        # 导入系统
        from core.memory.estia_memory_v5 import EstiaMemorySystem
        
        # 创建系统实例
        memory_system = EstiaMemorySystem(enable_advanced=True)
        
        print(f"📊 系统初始化状态: {memory_system.initialized}")
        
        # 检查核心组件
        components_status = {
            'sync_flow_manager': memory_system.sync_flow_manager is not None,
            'async_flow_manager': memory_system.async_flow_manager is not None
        }
        
        print("🔍 核心管理器状态:")
        for component, status in components_status.items():
            status_symbol = "✅" if status else "❌"
            print(f"   - {component}: {status_symbol}")
        
        if not memory_system.sync_flow_manager:
            print("❌ 同步流程管理器未初始化，无法继续测试")
            return False
        
        # 检查同步流程管理器的组件
        sync_manager = memory_system.sync_flow_manager
        sync_components = {
            'db_manager': sync_manager.db_manager is not None,
            'vectorizer': sync_manager.vectorizer is not None,
            'memory_store': sync_manager.memory_store is not None,
            'unified_cache': sync_manager.unified_cache is not None,
            'association_network': sync_manager.association_network is not None,  # 新修复
            'history_retriever': sync_manager.history_retriever is not None,      # 新修复
            'scorer': sync_manager.scorer is not None,                            # 新修复
            'faiss_retriever': sync_manager.faiss_retriever is not None,
            'smart_retriever': sync_manager.smart_retriever is not None
        }
        
        print("\\n🔍 同步流程组件状态 (文档标准14步工作流程):")
        critical_components = 0
        working_components = 0
        
        for component, status in sync_components.items():
            status_symbol = "✅" if status else "❌"
            print(f"   - {component}: {status_symbol}")
            
            # 关键组件计数
            if component in ['db_manager', 'vectorizer', 'memory_store', 'unified_cache']:
                critical_components += 1 if status else 0
            else:
                working_components += 1 if status else 0
        
        # 评估状态
        print(f"\\n📊 组件评估:")
        print(f"   - 关键组件 (4/4): {critical_components}/4")
        print(f"   - 工作组件 (5/5): {working_components}/5")
        
        if critical_components < 4:
            print("❌ 关键组件不完整，系统无法正常工作")
            return False
        
        # 测试查询增强 (Step 4-9)
        print("\\n🧪 测试查询增强流程 (Step 4-9)...")
        
        test_query = "今天工作压力很大，需要一些建议"
        start_time = time.time()
        
        try:
            enhanced_context = memory_system.enhance_query(test_query)
            processing_time = (time.time() - start_time) * 1000
            
            print(f"✅ 查询增强成功")
            print(f"   - 处理时间: {processing_time:.2f}ms")
            print(f"   - 输入长度: {len(test_query)} 字符")
            print(f"   - 输出长度: {len(enhanced_context)} 字符")
            print(f"   - 增强比例: {len(enhanced_context)/len(test_query):.1f}x")
            
            # 显示部分增强内容
            preview = enhanced_context[:200] + "..." if len(enhanced_context) > 200 else enhanced_context
            print(f"   - 内容预览: {preview}")
            
        except Exception as e:
            print(f"❌ 查询增强失败: {e}")
            return False
        
        # 测试交互存储 (Step 11-14)
        print("\\n🧪 测试交互存储流程 (Step 11-14)...")
        
        try:
            ai_response = "我理解你的工作压力。建议你可以..."
            store_result = memory_system.store_interaction(test_query, ai_response)
            
            if store_result.get('error'):
                print(f"❌ 交互存储失败: {store_result['error']}")
                return False
            else:
                print(f"✅ 交互存储成功")
                print(f"   - 用户记忆ID: {store_result.get('user_memory_id')}")
                print(f"   - AI记忆ID: {store_result.get('ai_memory_id')}")
                print(f"   - 状态: {store_result.get('status')}")
                
        except Exception as e:
            print(f"❌ 交互存储失败: {e}")
            return False
        
        # 测试缓存性能
        print("\\n🧪 测试缓存性能...")
        
        try:
            cache_stats = memory_system.get_cache_stats()
            
            if cache_stats.get('error'):
                print(f"⚠️ 缓存统计获取失败: {cache_stats['error']}")
            else:
                print(f"✅ 缓存系统正常")
                hit_ratio = cache_stats.get('cache_performance', {}).get('hit_ratio', 0)
                total_hits = cache_stats.get('cache_performance', {}).get('total_hits', 0)
                print(f"   - 缓存命中率: {hit_ratio*100:.1f}%")
                print(f"   - 总命中次数: {total_hits}")
                
        except Exception as e:
            print(f"⚠️ 缓存性能测试失败: {e}")
        
        # 最终评估
        print("\\n" + "="*60)
        print("📋 14步工作流程测试结果:")
        print("="*60)
        
        step_status = {
            "Step 1-3: 系统初始化": critical_components == 4,
            "Step 4-9: 查询增强": enhanced_context and len(enhanced_context) > len(test_query),
            "Step 11-14: 交互存储": store_result and not store_result.get('error'),
            "缓存系统": not cache_stats.get('error') if cache_stats else False,
            "关键组件完整性": working_components >= 3  # 至少3个工作组件
        }
        
        passed_tests = sum(step_status.values())
        total_tests = len(step_status)
        
        for step, status in step_status.items():
            status_symbol = "✅" if status else "❌"
            print(f"{status_symbol} {step}")
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\\n🎯 总体成功率: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if success_rate >= 80:
            print("\\n🎉 14步工作流程基本恢复成功!")
            print("   符合文档标准，可以继续使用")
        elif success_rate >= 60:
            print("\\n⚠️ 14步工作流程部分恢复")
            print("   基本功能可用，但仍有改进空间")
        else:
            print("\\n❌ 14步工作流程恢复失败")
            print("   需要进一步修复")
        
        return success_rate >= 60
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_14_step_workflow()
    exit_code = 0 if success else 1
    print(f"\\n📤 退出代码: {exit_code}")
    sys.exit(exit_code)
'''
    
    test_path = "test_14_step_workflow.py"
    
    try:
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"✅ 测试脚本已创建: {test_path}")
        return True
        
    except Exception as e:
        print(f"❌ 创建测试脚本失败: {e}")
        return False

def main():
    """主修复流程"""
    
    print("🚀 开始修复14步工作流程 - 基于文档标准")
    print("="*60)
    
    success_count = 0
    total_tasks = 3
    
    # 任务1: 修复核心组件初始化
    print("\\n📋 任务1: 修复 estia_memory_v5.py 核心组件初始化")
    if fix_estia_memory_v5_initialization():
        success_count += 1
        print("✅ 任务1完成")
    else:
        print("❌ 任务1失败")
    
    # 任务2: 修复方法名匹配
    print("\\n📋 任务2: 修复 AssociationNetwork 方法名匹配")
    if fix_association_network_method_name():
        success_count += 1
        print("✅ 任务2完成")
    else:
        print("❌ 任务2失败")
    
    # 任务3: 创建测试脚本
    print("\\n📋 任务3: 创建验证测试脚本")
    if create_test_script():
        success_count += 1
        print("✅ 任务3完成")
    else:
        print("❌ 任务3失败")
    
    # 总结
    print("\\n" + "="*60)
    print("📊 修复结果总结:")
    print("="*60)
    
    success_rate = (success_count / total_tasks) * 100
    print(f"成功率: {success_rate:.1f}% ({success_count}/{total_tasks})")
    
    if success_count == total_tasks:
        print("\\n🎉 所有修复任务完成!")
        print("\\n📋 下一步操作:")
        print("   1. 运行测试脚本: python test_14_step_workflow.py")
        print("   2. 检查14步工作流程是否完整恢复")
        print("   3. 如果测试通过，系统已恢复到文档标准")
    else:
        print("\\n⚠️ 部分修复任务失败，请检查错误信息")
    
    return success_count == total_tasks

if __name__ == "__main__":
    main()