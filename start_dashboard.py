#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动Web监控仪表板
"""

import sys
import os
sys.path.append('.')

# 确保模板目录存在
if not os.path.exists('web-vue/dist'):
    print("❌ 模板目录不存在，请确保在正确的目录下运行")
    sys.exit(1)

try:
    from web.web_dashboard import app, socketio
    print("✅ Web仪表板模块加载成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保所有依赖已安装: pip install flask flask-socketio")
    sys.exit(1)

if __name__ == '__main__':
    print("🚀 启动 Estia AI 一体化监控仪表板...")
    print("="*60)
    print("📦 集成服务包括:")
    print("  • Vue.js 前端界面")
    print("  • Flask 后端API")
    print("  • 实时监控系统")
    print("  • 告警管理系统")
    print("="*60)
    print("🌐 访问地址: http://localhost:5000")
    print("⏱️  启动中，请稍候...")
    print("⚠️  按 Ctrl+C 停止服务器")
    print("="*60)

    try:
        # 启动Flask-SocketIO服务器
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n👋 仪表板已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请检查端口5000是否被占用，或尝试使用其他端口")
        print("💡 提示: 确保Vue前端已构建 (cd web-vue && npm run build)")