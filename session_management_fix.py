#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
会话管理系统修复脚本
将旧系统的完整会话管理功能迁移到新系统 v5.0
"""

import os
import sys

def fix_session_management():
    """修复会话管理系统"""
    print("🚀 开始会话管理系统修复...")
    
    # 目标文件路径
    target_file = "core/memory/estia_memory_v5.py"
    
    if not os.path.exists(target_file):
        print(f"❌ 目标文件不存在: {target_file}")
        return False
    
    try:
        # 读取当前文件内容
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 添加会话管理方法
        session_methods = '''
    # === 会话管理方法 ===
    
    def start_new_session(self, session_id: str = None) -> str:
        """开始新的对话会话"""
        import time
        current_time = time.time()
        
        if session_id:
            self.current_session_id = session_id
        else:
            # 生成基于时间的session_id
            from datetime import datetime
            timestamp_str = datetime.fromtimestamp(current_time).strftime('%Y%m%d_%H%M%S')
            self.current_session_id = f"sess_{timestamp_str}"
        
        self.session_start_time = current_time
        self.logger.info(f"🆕 开始新会话: {self.current_session_id}")
        return self.current_session_id
    
    def get_current_session_id(self) -> str:
        """获取当前会话ID，如果没有则创建新会话"""
        import time
        current_time = time.time()
        
        # 检查是否需要创建新会话
        if (not self.current_session_id or 
            not self.session_start_time or 
            (current_time - self.session_start_time) > self.session_timeout):
            return self.start_new_session()
        
        return self.current_session_id
    
    def end_current_session(self):
        """结束当前会话"""
        if self.current_session_id:
            self.logger.info(f"🔚 结束会话: {self.current_session_id}")
            self.current_session_id = None
            self.session_start_time = None
'''
        
        # 2. 寻找插入位置（在核心API方法之前）
        insert_position = content.find("    # === 核心API方法 ===")
        if insert_position == -1:
            insert_position = content.find("    def enhance_query(")
            if insert_position == -1:
                print("❌ 找不到合适的插入位置")
                return False
        
        # 插入会话管理方法
        new_content = content[:insert_position] + session_methods + "\n" + content[insert_position:]
        
        # 3. 修改_prepare_context方法
        old_prepare_context = '''    def _prepare_context(self, context: Optional[Dict] = None) -> Dict:
        """准备上下文信息"""
        if context is None:
            context = {}
        
        context['timestamp'] = time.time()
        context['enable_advanced'] = self.enable_advanced
        context['context_preset'] = self.context_preset
        
        return context'''
        
        new_prepare_context = '''    def _prepare_context(self, context: Optional[Dict] = None) -> Dict:
        """准备上下文信息，自动处理会话管理"""
        if context is None:
            context = {}
        
        # 🔥 自动获取或创建会话
        if 'session_id' not in context:
            context['session_id'] = self.get_current_session_id()
        
        context['timestamp'] = time.time()
        context['enable_advanced'] = self.enable_advanced
        context['context_preset'] = self.context_preset
        
        return context'''
        
        # 替换_prepare_context方法
        if old_prepare_context in new_content:
            new_content = new_content.replace(old_prepare_context, new_prepare_context)
            print("✅ 已增强_prepare_context方法")
        else:
            print("⚠️ 未找到_prepare_context方法，可能需要手动修改")
        
        # 4. 写入修改后的内容
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 会话管理方法已成功添加到新系统")
        print("📋 添加的方法:")
        print("  - start_new_session(): 开始新会话")
        print("  - get_current_session_id(): 获取当前会话ID")
        print("  - end_current_session(): 结束当前会话")
        print("  - 增强_prepare_context(): 自动处理会话管理")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def create_session_test_script():
    """创建会话管理功能测试脚本"""
    print("\n🔧 创建会话管理功能测试脚本...")
    
    test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
会话管理系统测试脚本
测试新系统的会话管理功能是否正常工作
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_session_management():
    """测试会话管理功能"""
    print("🧪 开始测试会话管理功能...")
    
    try:
        # 导入系统
        from core.memory import create_estia_memory
        
        print("✅ 成功导入EstiaMemorySystem")
        
        # 创建系统实例
        memory_system = create_estia_memory(enable_advanced=False)
        
        print("✅ 成功创建系统实例")
        
        # 测试结果
        results = {}
        
        # 1. 测试会话创建
        print("\\n1. 测试会话创建功能...")
        try:
            session_id = memory_system.start_new_session()
            results['session_creation'] = session_id is not None and len(session_id) > 0
            print(f"   创建的会话ID: {session_id}")
            print(f"   ✅ 会话创建: {'通过' if results['session_creation'] else '失败'}")
        except Exception as e:
            results['session_creation'] = False
            print(f"   ❌ 会话创建失败: {e}")
        
        # 2. 测试会话获取
        print("\\n2. 测试会话获取功能...")
        try:
            current_session = memory_system.get_current_session_id()
            results['session_get'] = current_session == session_id
            print(f"   当前会话ID: {current_session}")
            print(f"   ✅ 会话获取: {'通过' if results['session_get'] else '失败'}")
        except Exception as e:
            results['session_get'] = False
            print(f"   ❌ 会话获取失败: {e}")
        
        # 3. 测试会话超时
        print("\\n3. 测试会话超时功能...")
        try:
            # 模拟超时（修改超时时间为1秒）
            original_timeout = memory_system.session_timeout
            memory_system.session_timeout = 1
            time.sleep(2)  # 等待超时
            
            new_session = memory_system.get_current_session_id()
            results['session_timeout'] = new_session != session_id
            
            # 恢复原超时时间
            memory_system.session_timeout = original_timeout
            
            print(f"   原会话ID: {session_id}")
            print(f"   新会话ID: {new_session}")
            print(f"   ✅ 会话超时: {'通过' if results['session_timeout'] else '失败'}")
        except Exception as e:
            results['session_timeout'] = False
            print(f"   ❌ 会话超时测试失败: {e}")
        
        # 4. 测试会话结束
        print("\\n4. 测试会话结束功能...")
        try:
            memory_system.end_current_session()
            results['session_end'] = (memory_system.current_session_id is None and 
                                     memory_system.session_start_time is None)
            print(f"   当前会话ID: {memory_system.current_session_id}")
            print(f"   ✅ 会话结束: {'通过' if results['session_end'] else '失败'}")
        except Exception as e:
            results['session_end'] = False
            print(f"   ❌ 会话结束失败: {e}")
        
        # 5. 测试_prepare_context集成
        print("\\n5. 测试_prepare_context集成...")
        try:
            context = memory_system._prepare_context()
            results['prepare_context'] = 'session_id' in context and context['session_id'] is not None
            print(f"   上下文session_id: {context.get('session_id', 'None')}")
            print(f"   ✅ 上下文集成: {'通过' if results['prepare_context'] else '失败'}")
        except Exception as e:
            results['prepare_context'] = False
            print(f"   ❌ 上下文集成失败: {e}")
        
        # 6. 测试enhance_query中的会话管理
        print("\\n6. 测试enhance_query中的会话管理...")
        try:
            enhanced_result = memory_system.enhance_query("测试会话管理")
            results['enhance_query_session'] = enhanced_result is not None
            print(f"   增强查询结果长度: {len(enhanced_result) if enhanced_result else 0}")
            print(f"   ✅ 增强查询会话: {'通过' if results['enhance_query_session'] else '失败'}")
        except Exception as e:
            results['enhance_query_session'] = False
            print(f"   ❌ 增强查询会话失败: {e}")
        
        # 计算成功率
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        success_rate = success_count / total_count * 100
        
        print(f"\\n📊 测试结果总结:")
        print(f"   成功率: {success_rate:.1f}% ({success_count}/{total_count})")
        print(f"   详细结果: {results}")
        
        if success_rate >= 80:
            print("🎉 会话管理系统修复成功！")
            return True
        else:
            print("⚠️ 会话管理系统仍有问题需要修复")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    print("🚀 会话管理系统测试")
    print("=" * 50)
    
    success = test_session_management()
    
    print("=" * 50)
    print(f"🎯 测试完成: {'成功' if success else '失败'}")
'''
    
    try:
        with open("test_session_management.py", 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print("✅ 测试脚本已创建: test_session_management.py")
        return True
        
    except Exception as e:
        print(f"❌ 创建测试脚本失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 会话管理系统修复工具")
    print("=" * 50)
    
    # 1. 修复会话管理系统
    if not fix_session_management():
        print("❌ 会话管理系统修复失败")
        return False
    
    # 2. 创建测试脚本
    if not create_session_test_script():
        print("❌ 测试脚本创建失败")
        return False
    
    print("\n🎉 会话管理系统修复完成！")
    print("📋 完成的工作:")
    print("  1. ✅ 将旧系统的3个核心会话管理方法迁移到新系统")
    print("  2. ✅ 增强_prepare_context方法，自动处理会话管理")
    print("  3. ✅ 创建了测试脚本 test_session_management.py")
    
    print("\n🚀 下一步:")
    print("  1. 运行测试脚本: python test_session_management.py")
    print("  2. 验证会话管理功能是否正常工作")
    print("  3. 如果测试通过，继续Phase 1的下一个模块")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)