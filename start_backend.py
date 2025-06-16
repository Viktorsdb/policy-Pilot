#!/usr/bin/env python3
"""
PolicyPilot后端服务启动脚本
确保在各种部署环境中都能正常启动
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def start_backend_server():
    """启动后端服务器"""
    
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🚀 启动PolicyPilot后端服务...")
    print(f"📁 工作目录: {project_root}")
    
    # 检查Python环境
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    print(f"🐍 Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查依赖
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI和Uvicorn已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 设置环境变量
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🌐 服务地址: http://{host}:{port}")
    print("-" * 50)
    
    try:
        # 启动服务器
        if os.path.exists("real_policy_server.py"):
            print("📋 启动主服务器...")
            subprocess.run([sys.executable, "real_policy_server.py"], check=True)
        else:
            print("❌ 找不到real_policy_server.py文件")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_backend_server() 