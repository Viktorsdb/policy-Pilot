#!/usr/bin/env python3
"""
PolicyPilot Backend Server
启动脚本
"""

import uvicorn
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """启动FastAPI应用"""
    
    # 设置环境变量
    os.environ.setdefault("PYTHONPATH", str(project_root))
    
    print("🚀 PolicyPilot Backend 启动中...")
    print(f"📁 项目目录: {project_root}")
    print("🌐 访问地址:")
    print("   - API文档: http://localhost:8000/docs")
    print("   - 健康检查: http://localhost:8000/health")
    print("   - API根路径: http://localhost:8000/api/v1")
    print("-" * 50)
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式热重载
        log_level="info",
        access_log=True,
        reload_dirs=[str(project_root / "app")],
    )

if __name__ == "__main__":
    main() 