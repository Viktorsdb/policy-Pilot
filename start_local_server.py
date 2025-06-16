#!/usr/bin/env python3
"""
本地HTTP服务器启动脚本
用于在本地测试GitHub Pages部署效果
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def start_local_server():
    """启动本地HTTP服务器"""
    
    # 设置端口
    PORT = 8080
    
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🚀 启动PolicyPilot本地测试服务器...")
    print(f"📁 服务目录: {project_root}")
    print(f"🌐 服务端口: {PORT}")
    print("-" * 50)
    
    # 创建HTTP服务器
    Handler = http.server.SimpleHTTPRequestHandler
    
    # 添加MIME类型支持
    Handler.extensions_map.update({
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.html': 'text/html',
        '.json': 'application/json',
    })
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"✅ 服务器启动成功！")
            print(f"🔗 本地访问地址:")
            print(f"   主页: http://localhost:{PORT}/")
            print(f"   政策看板: http://localhost:{PORT}/policy-dashboard.html")
            print(f"   AI聊天: http://localhost:{PORT}/ai-chat.html")
            print(f"   企业信息: http://localhost:{PORT}/company-info.html")
            print("-" * 50)
            print("💡 提示:")
            print("   - 修改文件后刷新浏览器即可看到效果")
            print("   - 按 Ctrl+C 停止服务器")
            print("   - 后端API功能需要单独启动 real_policy_server.py")
            print("-" * 50)
            
            # 自动打开浏览器
            try:
                webbrowser.open(f'http://localhost:{PORT}/')
                print("🌐 已自动打开浏览器")
            except:
                print("⚠️ 无法自动打开浏览器，请手动访问上述地址")
            
            print("\n🔄 服务器运行中...")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {PORT} 已被占用，请尝试其他端口或关闭占用该端口的程序")
        else:
            print(f"❌ 启动服务器失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_local_server() 