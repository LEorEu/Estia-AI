#!/usr/bin/env python3
"""
Estia AI项目快速状态检查工具
帮助Claude Code快速了解项目当前状态
"""

import os
import sys
import subprocess
from datetime import datetime

def check_git_status():
    """检查Git状态 - 重点关注工作区变更"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd='.')
        modified_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        print("📊 当前工作状态:")
        if not modified_files:
            print("  ✅ 工作区干净")
        else:
            print(f"  🔧 {len(modified_files)}个文件正在开发中")
            
            # 按文件类型分类显示
            core_files = [f for f in modified_files if 'core/' in f]
            config_files = [f for f in modified_files if 'config/' in f] 
            test_files = [f for f in modified_files if 'test' in f]
            other_files = [f for f in modified_files if f not in core_files + config_files + test_files]
            
            if core_files:
                print(f"    🧠 核心模块: {len(core_files)}个文件")
                for f in core_files[:3]:
                    print(f"      {f}")
            if config_files:
                print(f"    ⚙️ 配置文件: {len(config_files)}个文件")
            if test_files:
                print(f"    🧪 测试文件: {len(test_files)}个文件")
            if other_files:
                print(f"    📄 其他文件: {len(other_files)}个文件")
                
    except Exception as e:
        print(f"  ❌ Git检查失败: {e}")

def check_memory_system():
    """检查记忆系统状态"""
    try:
        from core.memory import create_estia_memory
        print("  ✅ 记忆系统模块可导入")
        
        # 检查关键文件
        key_files = [
            'core/memory/estia_memory_v6.py',
            'config/settings.py',
            'data/memory.db'  # 如果存在数据库文件
        ]
        
        for file in key_files:
            if os.path.exists(file):
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠️ {file} 不存在")
                
    except Exception as e:
        print(f"  ❌ 记忆系统检查失败: {e}")

def check_recent_changes():
    """检查最近的变更"""
    try:
        result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                              capture_output=True, text=True, cwd='.', encoding='utf-8')
        if result.stdout:
            commits = result.stdout.strip().split('\n')
            print("📈 最近提交:")
            for commit in commits:
                print(f"  {commit}")
        else:
            print("📈 最近提交: 无")
    except Exception as e:
        print(f"  ❌ 提交历史检查失败: {e}")

def check_session_log():
    """检查开发会话日志"""
    session_log = ".dev_session.log"
    
    print("📝 开发会话状态:")
    if os.path.exists(session_log):
        try:
            with open(session_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print(f"  📅 最后更新: {lines[-1].strip()}")
                    if len(lines) > 1:
                        print(f"  📋 今日已记录 {len(lines)} 条开发活动")
        except Exception as e:
            print(f"  ⚠️ 读取会话日志失败: {e}")
    else:
        print("  💡 建议: 运行 'python log_dev_session.py \"描述当前工作\"' 来记录开发进度")

def log_current_session(description):
    """记录当前开发会话"""
    session_log = ".dev_session.log" 
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(session_log, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {description}\n")
    
    print(f"✅ 已记录开发活动: {description}")

def main():
    print(f"🚀 Estia AI 项目状态检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    check_git_status()
    print()
    
    print("🧠 记忆系统状态:")
    check_memory_system()
    print()
    
    check_session_log()
    print()
    
    check_recent_changes()
    print("=" * 60)

if __name__ == "__main__":
    # 支持命令行参数记录开发活动
    if len(sys.argv) > 1 and sys.argv[1] == "log":
        if len(sys.argv) > 2:
            log_current_session(" ".join(sys.argv[2:]))
        else:
            description = input("请描述当前的开发活动: ")
            log_current_session(description)
    else:
        main()