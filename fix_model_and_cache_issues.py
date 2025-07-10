#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复模型路径和高级组件初始化问题
解决Qwen3-Embedding-0.6B模型加载失败和UnifiedCacheManager变量作用域问题
"""

import os
import re

def fix_model_path_configuration():
    """修复模型路径配置问题"""
    
    file_path = "core/memory/estia_memory_v5.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复1: 更正模型缓存路径
        # 将 core\cache 改为正确的路径 ..\cache
        cache_path_pattern = r'project_cache = os\.path\.join\(os\.path\.dirname\(__file__\), "[^"]*", "[^"]*", "cache"\)'
        new_cache_path = 'project_cache = os.path.join(os.path.dirname(__file__), "..", "..", "..", "cache")'
        
        content = re.sub(cache_path_pattern, new_cache_path, content)
        
        # 修复2: 添加更多缓存路径尝试
        env_setup_pattern = r'(# 设置离线模式环境变量，使用本地缓存\s+import os\s+project_cache = os\.path\.join\(os\.path\.dirname\(__file__\), "[^"]*", "[^"]*", "[^"]*", "cache"\))'
        
        enhanced_env_setup = '''# 设置离线模式环境变量，使用本地缓存
            import os
            
            # 尝试多个可能的缓存路径
            possible_cache_paths = [
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "cache"),  # \\estia\\cache
                os.path.join(os.path.dirname(__file__), "..", "..", "cache"),        # 项目根目录cache
                os.path.expanduser("~/.cache/huggingface"),                          # 用户主目录
                "cache"                                                               # 当前目录
            ]
            
            project_cache = None
            for cache_path in possible_cache_paths:
                if os.path.exists(cache_path):
                    project_cache = cache_path
                    self.logger.info(f"🎯 找到模型缓存路径: {cache_path}")
                    break
            
            if not project_cache:
                project_cache = possible_cache_paths[0]  # 使用第一个作为默认值
                self.logger.warning(f"⚠️ 未找到现有缓存，使用默认路径: {project_cache}")'''
        
        content = re.sub(env_setup_pattern, enhanced_env_setup, content, flags=re.DOTALL)
        
        # 修复3: 添加离线模式优先级
        vectorizer_init_pattern = r'(# 尝试使用本地缓存的模型，失败时回退到简化版本\s+vectorizer = None\s+vector_dim = 384\s+\s+try:)'
        
        enhanced_vectorizer_init = '''# 尝试使用本地缓存的模型，失败时回退到简化版本
            vectorizer = None
            vector_dim = 384
            
            # 强制离线模式，优先使用本地缓存
            os.environ['TRANSFORMERS_OFFLINE'] = '1'
            os.environ['HF_HUB_OFFLINE'] = '1'
            
            try:'''
        
        content = re.sub(vectorizer_init_pattern, enhanced_vectorizer_init, content, flags=re.DOTALL)
        
        # 写入修改后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 模型路径配置修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 模型路径修复失败: {e}")
        return False

def fix_unified_cache_manager_scope():
    """修复UnifiedCacheManager变量作用域问题"""
    
    file_path = "core/memory/estia_memory_v5.py"
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找高级组件初始化部分
        advanced_init_pattern = r'(# 🔥 可选高级组件\s+if self\.enable_advanced and components\.get\(\'db_manager\'\):\s+try:)'
        
        def fix_cache_manager_reference(match):
            return '''# 🔥 可选高级组件
            if self.enable_advanced and components.get('db_manager'):
                try:
                    # 确保UnifiedCacheManager可用
                    unified_cache = components.get('unified_cache')
                    if not unified_cache:
                        from .shared.caching.cache_manager import UnifiedCacheManager
                        unified_cache = UnifiedCacheManager.get_instance()'''
        
        new_content = re.sub(advanced_init_pattern, fix_cache_manager_reference, content)
        
        # 如果第一种方法没有匹配，尝试更具体的模式
        if new_content == content:
            # 在高级组件初始化的开始添加缓存管理器确保
            try_pattern = r'(if self\.enable_advanced and components\.get\(\'db_manager\'\):\s+try:)'
            
            def add_cache_manager_fix(match):
                return '''if self.enable_advanced and components.get('db_manager'):
                try:
                    # 确保UnifiedCacheManager在作用域内可用
                    unified_cache = components.get('unified_cache')
                    if not unified_cache:
                        from .shared.caching.cache_manager import UnifiedCacheManager
                        unified_cache = UnifiedCacheManager.get_instance()
                        components['unified_cache'] = unified_cache'''
            
            new_content = re.sub(try_pattern, add_cache_manager_fix, content)
        
        if new_content != content:
            # 写入修改后的文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ UnifiedCacheManager作用域问题修复完成")
            return True
        else:
            print("⚠️ 未找到需要修复的UnifiedCacheManager作用域问题")
            return True
        
    except Exception as e:
        print(f"❌ UnifiedCacheManager作用域修复失败: {e}")
        return False

def create_model_path_debug_script():
    """创建模型路径调试脚本"""
    
    debug_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试模型路径 - 查找Qwen3-Embedding-0.6B模型的实际位置
"""

import os
import sys

def find_qwen_model():
    """查找Qwen3-Embedding-0.6B模型"""
    
    print("🔍 查找Qwen3-Embedding-0.6B模型...")
    
    # 可能的搜索路径
    search_paths = [
        # 用户提到的路径
        "\\\\estia\\\\cache\\\\models--Qwen--Qwen3-Embedding-0.6B\\\\blobs",
        "estia\\\\cache\\\\models--Qwen--Qwen3-Embedding-0.6B\\\\blobs",
        
        # 标准Hugging Face缓存路径
        os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen3-Embedding-0.6B"),
        os.path.expanduser("~/.cache/huggingface/transformers"),
        
        # 项目相对路径
        os.path.join(os.getcwd(), "cache"),
        os.path.join(os.getcwd(), "..", "cache"),
        os.path.join(os.getcwd(), "..", "..", "cache"),
        os.path.join(os.getcwd(), "estia", "cache"),
        
        # Windows常见路径
        "C:\\\\Users\\\\{username}\\\\AppData\\\\Local\\\\huggingface".format(username=os.getenv('USERNAME', 'user')),
        "D:\\\\estia\\\\cache",
        "D:\\\\cache"
    ]
    
    found_paths = []
    
    for path in search_paths:
        try:
            if os.path.exists(path):
                print(f"✅ 找到路径: {path}")
                
                # 查找模型相关文件
                for root, dirs, files in os.walk(path):
                    if "Qwen" in root or "qwen" in root.lower():
                        print(f"   📁 Qwen相关目录: {root}")
                        
                        # 查找模型文件
                        model_files = [f for f in files if f.endswith(('.bin', '.safetensors', '.json', '.txt'))]
                        if model_files:
                            print(f"      📄 模型文件: {model_files[:5]}")  # 只显示前5个
                            found_paths.append(root)
            else:
                print(f"❌ 路径不存在: {path}")
                
        except Exception as e:
            print(f"⚠️ 检查路径失败 {path}: {e}")
    
    # 环境变量检查
    print("\\n🔍 检查环境变量:")
    env_vars = ['HF_HOME', 'HUGGINGFACE_HUB_CACHE', 'TRANSFORMERS_CACHE', 'SENTENCE_TRANSFORMERS_HOME']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   {var}: {value}")
            if os.path.exists(value):
                print(f"      ✅ 路径存在")
            else:
                print(f"      ❌ 路径不存在")
        else:
            print(f"   {var}: 未设置")
    
    # 推荐设置
    print("\\n💡 推荐配置:")
    if found_paths:
        best_path = found_paths[0]
        print(f"   建议设置环境变量:")
        print(f"   export HUGGINGFACE_HUB_CACHE='{best_path}'")
        print(f"   export SENTENCE_TRANSFORMERS_HOME='{best_path}'")
        print(f"   export HF_HOME='{best_path}'")
    else:
        print("   未找到Qwen模型，可能需要重新下载")
    
    return found_paths

if __name__ == "__main__":
    find_qwen_model()
'''
    
    script_path = "debug_model_path.py"
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(debug_script)
        
        print(f"✅ 模型路径调试脚本已创建: {script_path}")
        return True
        
    except Exception as e:
        print(f"❌ 创建调试脚本失败: {e}")
        return False

def main():
    """主修复流程"""
    
    print("🔧 开始修复模型路径和高级组件问题...")
    print("="*60)
    
    success_count = 0
    total_tasks = 3
    
    # 任务1: 修复模型路径配置
    print("\\n📋 任务1: 修复模型路径配置")
    if fix_model_path_configuration():
        success_count += 1
        print("✅ 任务1完成")
    else:
        print("❌ 任务1失败")
    
    # 任务2: 修复UnifiedCacheManager作用域
    print("\\n📋 任务2: 修复UnifiedCacheManager作用域")
    if fix_unified_cache_manager_scope():
        success_count += 1
        print("✅ 任务2完成")
    else:
        print("❌ 任务2失败")
    
    # 任务3: 创建调试脚本
    print("\\n📋 任务3: 创建模型路径调试脚本")
    if create_model_path_debug_script():
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
    
    if success_count >= 2:
        print("\\n🎉 主要修复完成!")
        print("\\n📋 下一步操作:")
        print("   1. 运行调试脚本找到模型: python debug_model_path.py")
        print("   2. 重新测试: python test_14_step_workflow.py")
        print("   3. 检查是否达到100%成功率")
    else:
        print("\\n⚠️ 修复失败，请检查错误信息")
    
    return success_count >= 2

if __name__ == "__main__":
    main()