#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estia 监控系统依赖安装器
=======================

自动检查和安装监控系统所需的依赖包。
"""

import subprocess
import sys
import importlib.util


def check_package(package_name):
    """检查包是否已安装"""
    spec = importlib.util.find_spec(package_name.replace('-', '_'))
    return spec is not None


def install_package(package_name):
    """安装包"""
    try:
        print(f"📦 正在安装 {package_name}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
        print(f"✅ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {package_name} 安装失败")
        return False


def main():
    """主函数"""
    print("🧠 Estia 监控系统依赖检查")
    print("="*40)
    
    # 必需的包
    required_packages = [
        'flask',
        'flask-socketio',
        'python-socketio[client]'
    ]
    
    # 可选的包（用于更好的可视化效果）
    optional_packages = [
        'requests',  # 用于API调用
    ]
    
    print("\n🔍 检查必需依赖...")
    missing_required = []
    
    for package in required_packages:
        if check_package(package):
            print(f"✅ {package} - 已安装")
        else:
            print(f"❌ {package} - 未安装")
            missing_required.append(package)
    
    print("\n🔍 检查可选依赖...")
    missing_optional = []
    
    for package in optional_packages:
        if check_package(package):
            print(f"✅ {package} - 已安装")
        else:
            print(f"⚠️ {package} - 未安装 (可选)")
            missing_optional.append(package)
    
    # 安装缺失的必需包
    if missing_required:
        print(f"\n📦 需要安装 {len(missing_required)} 个必需包:")
        for package in missing_required:
            print(f"   - {package}")
        
        user_input = input("\n是否现在安装这些包？(y/n): ")
        if user_input.lower() in ['y', 'yes', '是']:
            success_count = 0
            for package in missing_required:
                if install_package(package):
                    success_count += 1
            
            if success_count == len(missing_required):
                print(f"\n🎉 所有必需包安装完成！")
            else:
                print(f"\n⚠️ {len(missing_required) - success_count} 个包安装失败")
        else:
            print("\n⏭️ 跳过安装")
    
    # 询问是否安装可选包
    if missing_optional:
        print(f"\n📦 发现 {len(missing_optional)} 个可选包未安装:")
        for package in missing_optional:
            print(f"   - {package}")
        
        user_input = input("\n是否安装可选包以获得更好体验？(y/n): ")
        if user_input.lower() in ['y', 'yes', '是']:
            for package in missing_optional:
                install_package(package)
    
    print("\n" + "="*40)
    
    # 最终检查
    if not missing_required:
        print("✅ 所有依赖都已满足！")
        print("\n🚀 你现在可以运行监控系统:")
        print("   python start_monitoring_demo.py --demo    # 终端演示")
        print("   python start_monitoring_demo.py --web     # Web界面")
        print("   python start_monitoring_demo.py --both    # 完整体验")
        print("   python start_monitoring_demo.py --test    # 运行测试")
    else:
        print("⚠️ 仍有必需依赖未安装，请手动安装:")
        print(f"   pip install {' '.join(missing_required)}")
        
    print("\n💡 更多信息:")
    print("   python start_monitoring_demo.py --help")


if __name__ == "__main__":
    main() 