#!/usr/bin/env python3
"""
PolicyPilot Heroku部署脚本
帮助用户一键部署到Heroku平台
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def check_heroku_cli():
    """检查Heroku CLI是否安装"""
    try:
        result = subprocess.run(['heroku', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Heroku CLI已安装: {result.stdout.strip()}")
            return True
        else:
            print("❌ Heroku CLI未安装")
            return False
    except FileNotFoundError:
        print("❌ Heroku CLI未安装")
        return False

def check_heroku_login():
    """检查Heroku登录状态"""
    try:
        result = subprocess.run(['heroku', 'auth:whoami'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 已登录Heroku: {result.stdout.strip()}")
            return True
        else:
            print("❌ 未登录Heroku")
            return False
    except Exception:
        print("❌ 检查Heroku登录状态失败")
        return False

def create_heroku_app(app_name=None):
    """创建Heroku应用"""
    try:
        if not app_name:
            app_name = input("请输入应用名称（留空自动生成）: ").strip()
        
        cmd = ['heroku', 'create']
        if app_name:
            cmd.append(app_name)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Heroku应用创建成功")
            print(result.stdout)
            return True
        else:
            print(f"❌ 创建应用失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 创建应用时出错: {e}")
        return False

def deploy_to_heroku():
    """部署到Heroku"""
    try:
        print("📤 开始部署到Heroku...")
        
        # 添加Heroku远程仓库（如果不存在）
        result = subprocess.run(['git', 'remote', 'get-url', 'heroku'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️ 未找到Heroku远程仓库，请先创建Heroku应用")
            return False
        
        # 推送到Heroku
        result = subprocess.run(['git', 'push', 'heroku', 'main'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 部署成功！")
            print(result.stdout)
            return True
        else:
            print(f"❌ 部署失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 部署时出错: {e}")
        return False

def set_environment_variables():
    """设置环境变量"""
    try:
        print("🔧 设置环境变量...")
        
        # 可选的环境变量
        env_vars = {
            "DEEPSEEK_API_KEY": "DeepSeek API密钥（可选）",
            "HOST": "0.0.0.0",
            "PYTHON_VERSION": "3.11.5"
        }
        
        for var, description in env_vars.items():
            if var == "DEEPSEEK_API_KEY":
                value = input(f"请输入 {description}（留空跳过）: ").strip()
                if value:
                    subprocess.run(['heroku', 'config:set', f'{var}={value}'], check=True)
                    print(f"✅ 设置 {var}")
            else:
                subprocess.run(['heroku', 'config:set', f'{var}={env_vars[var]}'], check=True)
                print(f"✅ 设置 {var}={env_vars[var]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置环境变量失败: {e}")
        return False

def get_app_url():
    """获取应用URL"""
    try:
        result = subprocess.run(['heroku', 'apps:info', '--json'], capture_output=True, text=True)
        if result.returncode == 0:
            app_info = json.loads(result.stdout)
            return app_info.get('web_url', '')
        return None
    except Exception:
        return None

def main():
    """主函数"""
    print("🚀 PolicyPilot Heroku部署工具")
    print("=" * 50)
    
    # 检查环境
    if not check_heroku_cli():
        print("\n📥 请先安装Heroku CLI:")
        print("https://devcenter.heroku.com/articles/heroku-cli")
        return
    
    if not check_heroku_login():
        print("\n🔑 请先登录Heroku:")
        print("运行命令: heroku login")
        return
    
    # 检查Git仓库
    if not os.path.exists('.git'):
        print("❌ 当前目录不是Git仓库")
        return
    
    print("\n📋 部署选项:")
    print("1. 创建新应用并部署")
    print("2. 部署到现有应用")
    print("3. 仅设置环境变量")
    
    choice = input("\n请选择操作 (1-3): ").strip()
    
    if choice == "1":
        print("\n🆕 创建新应用...")
        if create_heroku_app():
            if set_environment_variables():
                deploy_to_heroku()
                
                # 显示应用信息
                app_url = get_app_url()
                if app_url:
                    print(f"\n🎉 部署完成！")
                    print(f"🔗 应用地址: {app_url}")
                    print(f"📊 API地址: {app_url}api/v1/")
                    
                    # 更新前端配置
                    print(f"\n💡 请更新前端配置文件中的API地址:")
                    print(f"   policy-dashboard.js")
                    print(f"   ai-chat.js")
                    print(f"   将Heroku地址改为: {app_url}api/v1")
    
    elif choice == "2":
        print("\n📤 部署到现有应用...")
        if deploy_to_heroku():
            app_url = get_app_url()
            if app_url:
                print(f"\n🎉 部署完成！")
                print(f"🔗 应用地址: {app_url}")
    
    elif choice == "3":
        print("\n🔧 设置环境变量...")
        set_environment_variables()
    
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main() 