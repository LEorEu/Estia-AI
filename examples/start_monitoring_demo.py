#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estia 记忆监控演示启动器
========================

一键启动记忆监控系统的演示和可视化界面。

使用方法:
    python start_monitoring_demo.py [选项]
    
选项:
    --demo, -d      运行终端演示（默认）
    --web, -w       启动Web可视化界面
    --both, -b      同时运行演示和Web界面
    --test, -t      运行测试套件
    --help, -h      显示帮助信息
"""

import argparse
import sys
import threading
import time
import subprocess
import os


def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'flask',
        'flask-socketio'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("⚠️ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 请先安装依赖包:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


def run_terminal_demo():
    """运行终端演示"""
    print("🎯 启动终端监控演示...")
    print("="*60)
    
    try:
        from examples.demo_monitoring import main as demo_main
        demo_main()
        return True
    except ImportError as e:
        print(f"❌ 导入演示模块失败: {e}")
        print("请确保 demo_monitoring.py 文件存在且可访问")
        return False
    except Exception as e:
        print(f"❌ 演示运行失败: {e}")
        return False


def run_web_dashboard():
    """运行Web仪表板"""
    print("🌐 启动Web监控仪表板...")
    print("="*60)
    
    if not check_dependencies():
        return False
    
    try:
        from web.web_dashboard import run_dashboard
        run_dashboard(host='127.0.0.1', port=5000, debug=False)
        return True
    except ImportError as e:
        print(f"❌ 导入Web模块失败: {e}")
        print("请确保 web_dashboard.py 文件存在且可访问")
        return False
    except Exception as e:
        print(f"❌ Web界面启动失败: {e}")
        return False


def run_tests():
    """运行测试套件"""
    print("🧪 运行监控系统测试...")
    print("="*60)
    
    try:
        test_file = "tests/test_memory_monitoring.py"
        if os.path.exists(test_file):
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("错误输出:")
                print(result.stderr)
            return result.returncode == 0
        else:
            print(f"❌ 测试文件不存在: {test_file}")
            return False
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return False


def run_both():
    """同时运行演示和Web界面"""
    print("🚀 同时启动终端演示和Web界面...")
    print("="*60)
    
    # 先运行终端演示生成一些数据
    print("\n🎯 步骤1: 运行终端演示生成监控数据")
    demo_thread = threading.Thread(target=run_terminal_demo)
    demo_thread.daemon = True
    demo_thread.start()
    
    # 等待一下让演示完成
    demo_thread.join(timeout=30)
    
    print("\n🌐 步骤2: 启动Web监控界面")
    print("💡 提示: 在新的终端窗口中运行以下命令来生成更多数据:")
    print("   python demo_monitoring.py")
    print()
    
    # 启动Web界面
    return run_web_dashboard()


def show_help():
    """显示帮助信息"""
    help_text = """
🧠 Estia 记忆监控演示系统
========================

这个演示系统展示了13步记忆处理流程的完整监控功能，包括：

📊 核心功能:
  • 实时流程监控 - 跟踪每个处理步骤的执行状态
  • 性能分析 - 识别瓶颈和优化机会  
  • 关键词分析 - 提取和可视化对话关键词
  • 记忆内容分析 - 分析记忆检索和关联模式

🚀 使用方式:

1. 终端演示 (快速查看):
   python start_monitoring_demo.py --demo
   
2. Web可视化界面 (推荐):
   python start_monitoring_demo.py --web
   然后访问: http://127.0.0.1:5000
   
3. 完整体验:
   python start_monitoring_demo.py --both
   
4. 运行测试:
   python start_monitoring_demo.py --test

📋 依赖要求:
  • Python 3.7+
  • flask, flask-socketio (Web界面)
  
💡 提示:
  • 首次运行建议使用 --both 选项获得完整体验
  • Web界面支持实时监控和历史数据分析
  • 关键词云会根据对话内容动态更新
  • 所有监控数据都在内存中，重启后会清空

🔧 集成指南:
  1. 查看 core/memory/monitoring/ 目录了解监控架构
  2. 参考 integration_example.py 了解如何集成到现有系统
  3. 使用装饰器 @monitor_step 快速添加监控
  4. 通过 StepMonitorContext 获得更精细的控制

📚 更多信息:
  • 查看 core/memory/monitoring/__init__.py 了解API
  • 运行测试了解各个组件的功能
  • Web界面提供交互式的性能分析
"""
    print(help_text)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Estia 记忆监控演示启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --demo          # 运行终端演示
  %(prog)s --web           # 启动Web界面  
  %(prog)s --both          # 完整体验
  %(prog)s --test          # 运行测试
        """
    )
    
    parser.add_argument('--demo', '-d', action='store_true',
                       help='运行终端监控演示')
    parser.add_argument('--web', '-w', action='store_true',
                       help='启动Web可视化界面')
    parser.add_argument('--both', '-b', action='store_true',
                       help='同时运行演示和Web界面')
    parser.add_argument('--test', '-t', action='store_true',
                       help='运行测试套件')
    
    args = parser.parse_args()
    
    # 如果没有指定参数，显示帮助
    if not any([args.demo, args.web, args.both, args.test]):
        show_help()
        print("\n🚀 默认启动终端演示...")
        args.demo = True
    
    print("🧠 Estia 记忆监控演示系统")
    print("="*50)
    
    success = True
    
    try:
        if args.test:
            success = run_tests()
        elif args.both:
            success = run_both()
        elif args.web:
            success = run_web_dashboard()
        elif args.demo:
            success = run_terminal_demo()
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断，正在退出...")
        success = True
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        success = False
    
    if success:
        print("\n🎉 演示完成！")
        print("\n💡 接下来你可以:")
        print("  1. 查看监控系统的源代码了解实现细节")
        print("  2. 将监控功能集成到你的 EstiaMemorySystem 中")
        print("  3. 根据需要调整监控配置和可视化界面")
        print("  4. 在生产环境中部署监控系统")
    else:
        print("\n⚠️ 演示过程中遇到了一些问题")
        print("请检查错误信息并确保所有依赖都已正确安装")
        sys.exit(1)


if __name__ == "__main__":
    main() 