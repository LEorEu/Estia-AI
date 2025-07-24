#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estia AI 监控系统启动脚本 - 重构版
"""

import sys
import os
import logging
import argparse
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging(debug=False):
    """设置日志"""
    os.makedirs('logs', exist_ok=True)
    
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'logs/monitoring_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
        ]
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Estia AI 重构版监控系统")
    parser.add_argument("--host", default="127.0.0.1", help="服务器地址")
    parser.add_argument("--port", type=int, default=5000, help="端口号")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    print("🚀 启动 Estia AI 重构版监控系统")
    print("="*60)
    
    # 设置日志
    setup_logging(args.debug)
    
    try:
        # 导入监控系统组件
        print("📦 加载监控系统组件...")
        from monitoring import create_monitoring_system, MonitoringConfig
        from monitoring.web.dashboard import create_unified_dashboard
        
        # 创建配置
        config = MonitoringConfig()
        config.web.host = args.host
        config.web.port = args.port
        config.web.debug = args.debug
        
        print(f"⚙️  配置: {config.web.host}:{config.web.port} (调试模式: {'开启' if args.debug else '关闭'})")
        
        # 创建和启动监控系统
        print("🔧 初始化监控系统...")
        monitoring_system = create_monitoring_system(config)
        monitoring_system.start()
        print("✅ 监控系统启动成功")
        
        # 创建Web仪表板
        print("🌐 创建Web仪表板...")
        app, socketio = create_unified_dashboard(monitoring_system, config)
        print("✅ Web仪表板创建成功")
        
        print("\n" + "="*60)
        print("🎉 Estia AI 重构版监控系统已就绪！")
        print("="*60)
        print(f"🌐 主页面: http://{config.web.host}:{config.web.port}")
        print(f"📊 API接口: http://{config.web.host}:{config.web.port}/api/monitoring/")
        print("⚡ 实时监控: WebSocket已启用")
        print("🛑 按 Ctrl+C 停止系统")
        print("="*60)
        
        # 启动Web服务器
        socketio.run(
            app,
            host=config.web.host,
            port=config.web.port,
            debug=config.web.debug,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n🛑 接收到停止信号，正在关闭系统...")
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        print("\n💡 如果遇到问题，可以尝试:")
        print("   1. 运行 rollback_system.bat 回滚到原版系统")
        print("   2. 使用 --debug 参数查看详细错误信息")
        return 1
    finally:
        # 确保监控系统正确停止
        try:
            if 'monitoring_system' in locals():
                monitoring_system.stop()
                print("✅ 监控系统已安全停止")
        except:
            pass
    
    print("👋 Estia AI 监控系统已退出")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)