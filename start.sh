#!/bin/bash

# PolicyPilot 快速启动脚本
echo "🚀 PolicyPilot AI政策匹配平台启动脚本"
echo "=================================="

# 检查Python版本
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ Python环境: $python_version"
else
    echo "❌ 错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
mkdir -p data logs

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  警告: 端口8000已被占用，请先关闭占用该端口的程序"
    echo "💡 提示: 使用 'lsof -ti:8000 | xargs kill' 关闭占用进程"
    exit 1
fi

# 启动应用
echo "🎯 启动PolicyPilot服务器..."
echo "📍 访问地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo "💚 健康检查: http://localhost:8000/api/v1/health"
echo "=================================="
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动FastAPI应用
python real_policy_server.py 