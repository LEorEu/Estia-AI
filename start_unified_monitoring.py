#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一监控系统启动器
==================

使用重新组织后的监控系统启动完整的监控服务。
"""

import sys
import os
sys.path.append('.')

from monitoring import create_monitoring_system, MonitoringConfig
from monitoring.web.dashboard import create_unified_dashboard

def main():
    """启动统一监控系统"""
    
    print("🚀 启动 Estia AI 统一监控系统")
    print("="*60)
    print("📁 使用重新组织的监控架构")
    print("🛡️ 安全设计：不影响核心记忆系统")
    print("🧩 模块化：所有监控代码统一管理")
    print("="*60)
    
    try:
        # 创建配置
        config = MonitoringConfig.from_env()
        
        # 验证配置
        errors = config.validate()
        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"  • {error}")
            return
        
        print(f"✅ 配置验证通过")
        print(f"📊 Web界面: http://{config.web.host}:{config.web.port}")
        print(f"🔄 监控间隔: {config.performance.collection_interval}秒")
        print(f"💾 缓存TTL: {config.cache.ttl_seconds}秒")
        print(f"🚨 告警功能: {'启用' if config.alerts.enabled else '禁用'}")
        print()
        
        # 创建监控系统
        monitoring_system = create_monitoring_system(config)
        monitoring_system.start()
        
        print("✅ 监控系统启动成功")
        
        # 显示系统状态
        status = monitoring_system.get_system_status()
        print(f"📊 组件状态:")
        for component, info in status['components'].items():
            status_text = info.get('status', 'unknown')
            print(f"  • {component}: {status_text}")
        
        print()
        print("🌐 创建Web仪表板...")
        
        # 创建Web仪表板
        app, socketio = create_unified_dashboard(monitoring_system, config)
        
        print("✅ Web仪表板创建成功")
        print()
        print("🎯 功能特性:")
        print("  ✅ 统一的监控架构")
        print("  ✅ 安全的记忆系统集成") 
        print("  ✅ 实时性能监控")
        print("  ✅ 智能告警系统")
        print("  ✅ Vue + Flask 一体化")
        print("  ✅ WebSocket 实时推送")
        print("="*60)
        print("🌐 访问地址: http://localhost:5000")
        print("⚠️  按 Ctrl+C 停止服务器")
        print("="*60)
        
        # 启动Web服务器
        socketio.run(
            app, 
            host=config.web.host, 
            port=config.web.port, 
            debug=config.web.debug,
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 正在关闭监控系统...")
        try:
            monitoring_system.stop()
            print("✅ 监控系统已安全关闭")
        except:
            pass
    
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 提示:")
        print("  - 检查端口5000是否被占用")
        print("  - 确保Vue前端已构建: cd web-vue && npm run build")
        print("  - 检查Python依赖: pip install flask flask-socketio psutil")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()