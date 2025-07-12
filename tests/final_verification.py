#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终修复验证测试
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def final_verification():
    """最终修复验证"""
    print("🎯 最终修复验证测试")
    print("=" * 60)
    
    success_count = 0
    total_tests = 4
    
    # 测试1: v6记忆系统初始化
    print("1. 测试v6记忆系统初始化...")
    try:
        from core.memory.estia_memory_v6 import create_estia_memory
        
        memory_system = create_estia_memory(enable_advanced=True)
        
        if memory_system.initialized:
            print("   ✅ v6记忆系统初始化成功")
            success_count += 1
        else:
            print("   ❌ v6记忆系统初始化失败")
            
    except Exception as e:
        print(f"   ❌ v6初始化测试失败: {e}")
    
    # 测试2: 查询增强功能
    print("\n2. 测试查询增强功能...")
    try:
        if 'memory_system' in locals() and memory_system.initialized:
            test_query = "测试查询增强功能"
            enhanced_context = memory_system.enhance_query(test_query)
            
            if enhanced_context and len(enhanced_context) > len(test_query):
                print(f"   ✅ 查询增强成功: {len(enhanced_context)} 字符")
                success_count += 1
            else:
                print("   ❌ 查询增强功能异常")
        else:
            print("   ⚠️ 跳过（系统未初始化）")
            
    except Exception as e:
        print(f"   ❌ 查询增强测试失败: {e}")
    
    # 测试3: 交互存储功能
    print("\n3. 测试交互存储功能...")
    try:
        if 'memory_system' in locals() and memory_system.initialized:
            test_query = "测试交互存储"
            test_response = "这是一个测试回复"
            
            store_result = memory_system.store_interaction(test_query, test_response)
            
            if store_result and not store_result.get('error'):
                print("   ✅ 交互存储成功")
                success_count += 1
                
                # 检查是否有记忆ID
                if store_result.get('user_memory_id') and store_result.get('ai_memory_id'):
                    print("   ✅ 记忆ID生成正常")
                else:
                    print("   ⚠️ 记忆ID可能缺失")
            else:
                print(f"   ❌ 交互存储失败: {store_result.get('error', '未知错误')}")
        else:
            print("   ⚠️ 跳过（系统未初始化）")
            
    except Exception as e:
        print(f"   ❌ 交互存储测试失败: {e}")
    
    # 测试4: 向量维度一致性
    print("\n4. 测试向量维度一致性...")
    try:
        from core.memory.shared.embedding.simple_vectorizer import SimpleVectorizer
        from core.memory.shared.embedding.vectorizer import TextVectorizer
        
        # 测试SimpleVectorizer
        simple_vectorizer = SimpleVectorizer()
        simple_vector = simple_vectorizer.encode("测试文本")
        
        # 测试TextVectorizer
        text_vectorizer = TextVectorizer()
        text_vector = text_vectorizer.encode("测试文本")
        
        if simple_vector.shape == text_vector.shape and simple_vector.shape[0] == 1024:
            print(f"   ✅ 向量维度一致: {simple_vector.shape}")
            success_count += 1
        else:
            print(f"   ❌ 向量维度不一致: Simple={simple_vector.shape}, Text={text_vector.shape}")
            
    except Exception as e:
        print(f"   ❌ 向量维度测试失败: {e}")
    
    # 总结
    print(f"\n📊 测试总结")
    print("=" * 40)
    print(f"总测试数: {total_tests}")
    print(f"成功测试数: {success_count}")
    print(f"成功率: {success_count/total_tests*100:.1f}%")
    
    if success_count == total_tests:
        print("\n🎉 所有测试通过！系统修复完成！")
        print("💡 建议运行: python test_complete_14_step_workflow.py")
        return True
    elif success_count >= total_tests * 0.75:
        print(f"\n✅ 大部分测试通过（{success_count}/{total_tests}）")
        print("💡 系统基本可用，可以进行进一步测试")
        return True
    else:
        print(f"\n⚠️ 仍有问题需要解决（{success_count}/{total_tests}）")
        return False

if __name__ == "__main__":
    final_verification()