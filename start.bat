@echo off
chcp 65001 >nul
echo 🚀 PolicyPilot AI政策匹配平台启动脚本
echo ==================================

REM 检查Python版本
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set python_version=%%i
echo ✅ Python环境: %python_version%

REM 检查是否存在虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装依赖包...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 创建必要的目录
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM 启动应用
echo 🎯 启动PolicyPilot服务器...
echo 📍 访问地址: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
echo 💚 健康检查: http://localhost:8000/api/v1/health
echo ==================================
echo 按 Ctrl+C 停止服务器
echo.

REM 启动FastAPI应用
python real_policy_server.py

pause 