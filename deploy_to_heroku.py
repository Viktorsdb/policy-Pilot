#!/usr/bin/env python3
"""
PolicyPilot Heroku部署工具
提供多种部署方式，确保后端服务正常运行
"""

import os
import sys
import subprocess
import webbrowser
import json
from pathlib import Path

def check_heroku_cli():
    """检查Heroku CLI是否安装"""
    try:
        result = subprocess.run(['heroku', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Heroku CLI已安装: {result.stdout.strip()}")
            return True
        else:
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_heroku_login():
    """检查Heroku登录状态"""
    try:
        result = subprocess.run(['heroku', 'auth:whoami'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            email = result.stdout.strip()
            print(f"✅ 已登录Heroku: {email}")
            return True
        else:
            print("❌ 未登录Heroku")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Heroku登录检查超时")
        return False

def deploy_via_cli():
    """通过Heroku CLI部署"""
    print("\n🚀 通过Heroku CLI部署...")
    
    try:
        # 检查是否已有Heroku远程仓库
        result = subprocess.run(['git', 'remote', 'get-url', 'heroku'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            # 创建新的Heroku应用
            app_name = "policy-pilot-" + os.urandom(4).hex()
            print(f"📱 创建Heroku应用: {app_name}")
            
            create_result = subprocess.run(['heroku', 'create', app_name], 
                                         capture_output=True, text=True)
            if create_result.returncode != 0:
                print(f"❌ 创建应用失败: {create_result.stderr}")
                return False
        
        # 部署到Heroku
        print("📤 推送代码到Heroku...")
        deploy_result = subprocess.run(['git', 'push', 'heroku', 'main'], 
                                     capture_output=True, text=True)
        
        if deploy_result.returncode == 0:
            print("✅ 部署成功！")
            
            # 获取应用URL
            url_result = subprocess.run(['heroku', 'apps:info', '--json'], 
                                      capture_output=True, text=True)
            if url_result.returncode == 0:
                app_info = json.loads(url_result.stdout)
                app_url = app_info.get('app', {}).get('web_url', '')
                if app_url:
                    print(f"🌐 应用地址: {app_url}")
                    print(f"🔗 API地址: {app_url}api/v1")
                    return True
        else:
            print(f"❌ 部署失败: {deploy_result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ CLI部署出错: {e}")
        return False

def deploy_via_github():
    """通过GitHub集成部署"""
    print("\n🔗 通过GitHub集成部署...")
    
    github_url = "https://github.com/Viktorsdb/policy-Pilot"
    heroku_deploy_url = f"https://heroku.com/deploy?template={github_url}"
    
    print(f"📋 部署步骤:")
    print(f"1. 点击链接打开Heroku部署页面")
    print(f"2. 登录您的Heroku账户")
    print(f"3. 填写应用名称（可选）")
    print(f"4. 点击'Deploy app'按钮")
    print(f"5. 等待部署完成")
    
    print(f"\n🔗 部署链接: {heroku_deploy_url}")
    
    try:
        webbrowser.open(heroku_deploy_url)
        print("✅ 已在浏览器中打开部署页面")
    except:
        print("⚠️ 无法自动打开浏览器，请手动复制链接")
    
    return True

def deploy_via_railway():
    """通过Railway部署"""
    print("\n🚄 通过Railway部署...")
    
    railway_url = "https://railway.app/template/your-template"
    
    print(f"📋 Railway部署步骤:")
    print(f"1. 访问Railway部署页面")
    print(f"2. 连接您的GitHub账户")
    print(f"3. 选择仓库并部署")
    print(f"4. 配置环境变量（可选）")
    
    print(f"\n🔗 Railway部署: {railway_url}")
    
    return True

def deploy_via_render():
    """通过Render部署"""
    print("\n🎨 通过Render部署...")
    
    render_url = "https://render.com/deploy"
    
    print(f"📋 Render部署步骤:")
    print(f"1. 访问Render部署页面")
    print(f"2. 连接GitHub仓库")
    print(f"3. 选择Web Service")
    print(f"4. 配置构建和启动命令")
    print(f"   - Build Command: pip install -r requirements.txt")
    print(f"   - Start Command: python real_policy_server.py")
    
    print(f"\n🔗 Render部署: {render_url}")
    
    return True

def show_deployment_status():
    """显示当前部署状态"""
    print("\n📊 当前部署状态:")
    print("=" * 50)
    
    # 检查本地服务
    try:
        import requests
        response = requests.get("http://localhost:8001/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ 本地服务: 正常运行 (localhost:8001)")
        else:
            print("❌ 本地服务: 异常")
    except:
        print("⚠️ 本地服务: 未启动")
    
    # 检查Heroku部署
    try:
        import requests
        response = requests.get("https://policy-pilot-viktorsdb.herokuapp.com/api/v1/health", timeout=10)
        if response.status_code == 200:
            print("✅ Heroku部署: 正常运行")
        else:
            print("❌ Heroku部署: 异常")
    except:
        print("🔄 Heroku部署: 不可用或正在重启")
    
    # 检查前端状态
    try:
        import requests
        response = requests.get("https://viktorsdb.github.io/policy-Pilot/", timeout=10)
        if response.status_code == 200:
            print("✅ 前端页面: 正常访问")
        else:
            print("❌ 前端页面: 异常")
    except:
        print("⚠️ 前端页面: 网络问题")

def main():
    """主函数"""
    print("🚀 PolicyPilot Heroku部署工具")
    print("=" * 50)
    
    # 显示当前状态
    show_deployment_status()
    
    print("\n📦 可用的部署方式:")
    print("1. 🔗 GitHub集成部署 (推荐，无需CLI)")
    print("2. 💻 Heroku CLI部署 (需要安装CLI)")
    print("3. 🚄 Railway部署 (备用方案)")
    print("4. 🎨 Render部署 (备用方案)")
    print("5. 📊 查看部署状态")
    print("6. 🏠 启动本地服务")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请选择部署方式 (0-6): ").strip()
            
            if choice == "0":
                print("👋 再见！")
                break
            elif choice == "1":
                deploy_via_github()
            elif choice == "2":
                if check_heroku_cli() and check_heroku_login():
                    deploy_via_cli()
                else:
                    print("\n❌ Heroku CLI未安装或未登录")
                    print("📥 请先安装Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli")
                    print("🔑 然后运行: heroku login")
            elif choice == "3":
                deploy_via_railway()
            elif choice == "4":
                deploy_via_render()
            elif choice == "5":
                show_deployment_status()
            elif choice == "6":
                print("\n🏠 启动本地服务...")
                try:
                    subprocess.run([sys.executable, "real_policy_server.py"])
                except KeyboardInterrupt:
                    print("\n⏹️ 服务已停止")
            else:
                print("❌ 无效选择，请输入0-6")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main() 