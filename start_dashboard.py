#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动Web监控仪表板
"""

import sys
import os
sys.path.append('.')

# 确保模板目录存在
if not os.path.exists('templates'):
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
    print("🚀 启动Estia记忆监控仪表板...")
    print("📊 可用的访问地址:")
    print("http://localhost:5000")
    print("🔄 实时监控已启用")
    print("🧪 如果没有数据，点击'加载测试数据'按钮查看效果")
    print("⚠️  按 Ctrl+C 停止服务器")
    print("="*60)

    try:
        # 启动Flask-SocketIO服务器
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n👋 仪表板已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请检查端口5000是否被占用，或尝试使用其他端口")