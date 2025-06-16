#!/usr/bin/env python3
"""
PolicyPilot 自动化部署脚本
确保后端服务能够正常运行，支持多平台部署
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path

class PolicyPilotDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.heroku_app_name = "policy-pilot-viktorsdb"
        self.heroku_url = f"https://{self.heroku_app_name}.herokuapp.com"
        
    def check_requirements(self):
        """检查部署要求"""
        print("🔍 检查部署要求...")
        
        # 检查必要文件
        required_files = [
            'real_policy_server.py',
            'requirements.txt',
            'Procfile',
            'app.json'
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
            return False
        
        print("✅ 所有必要文件都存在")
        return True
    
    def test_local_server(self):
        """测试本地服务器"""
        print("🧪 测试本地服务器...")
        
        try:
            # 启动本地服务器
            process = subprocess.Popen([
                sys.executable, 'real_policy_server.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服务器启动
            time.sleep(3)
            
            # 测试健康检查
            response = requests.get('http://localhost:8001/api/v1/health', timeout=5)
            
            if response.status_code == 200:
                print("✅ 本地服务器测试通过")
                process.terminate()
                return True
            else:
                print(f"❌ 本地服务器测试失败: {response.status_code}")
                process.terminate()
                return False
                
        except Exception as e:
            print(f"❌ 本地服务器测试出错: {e}")
            try:
                process.terminate()
            except:
                pass
            return False
    
    def deploy_to_heroku(self):
        """部署到Heroku"""
        print("🚀 开始部署到Heroku...")
        
        try:
            # 检查Git状态
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                print("📝 提交本地更改...")
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-m', 'Auto deploy: Update backend configuration'], 
                             check=True)
            
            # 检查Heroku远程仓库
            result = subprocess.run(['git', 'remote', 'get-url', 'heroku'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"📱 添加Heroku远程仓库...")
                subprocess.run(['heroku', 'git:remote', '-a', self.heroku_app_name], 
                             check=True)
            
            # 部署到Heroku
            print("📤 推送到Heroku...")
            result = subprocess.run(['git', 'push', 'heroku', 'main'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Heroku部署成功")
                return True
            else:
                print(f"❌ Heroku部署失败: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Heroku部署出错: {e}")
            return False
        except FileNotFoundError:
            print("❌ Heroku CLI未安装，请先安装: https://devcenter.heroku.com/articles/heroku-cli")
            return False
    
    def test_heroku_deployment(self):
        """测试Heroku部署"""
        print("🧪 测试Heroku部署...")
        
        # 等待部署完成
        print("⏳ 等待服务启动...")
        time.sleep(30)
        
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.heroku_url}/api/v1/health", timeout=10)
                
                if response.status_code == 200:
                    print("✅ Heroku部署测试通过")
                    print(f"🌐 后端服务地址: {self.heroku_url}/api/v1")
                    return True
                else:
                    print(f"⏳ 尝试 {i+1}/{max_retries}: 状态码 {response.status_code}")
                    
            except requests.RequestException as e:
                print(f"⏳ 尝试 {i+1}/{max_retries}: {e}")
            
            if i < max_retries - 1:
                time.sleep(10)
        
        print("❌ Heroku部署测试失败")
        return False
    
    def update_frontend_config(self):
        """更新前端配置"""
        print("🔧 更新前端配置...")
        
        # 更新API配置
        config_files = [
            'policy-dashboard.js',
            'ai-chat.js',
            'script.js'
        ]
        
        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                
                # 更新Heroku URL
                updated_content = content.replace(
                    'https://policy-pilot-viktorsdb.herokuapp.com',
                    self.heroku_url
                )
                
                if content != updated_content:
                    file_path.write_text(updated_content, encoding='utf-8')
                    print(f"✅ 更新 {config_file}")
        
        print("✅ 前端配置更新完成")
    
    def create_deployment_status(self):
        """创建部署状态文件"""
        status = {
            "deployment_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "backend_url": f"{self.heroku_url}/api/v1",
            "frontend_url": "https://viktorsdb.github.io/policy-Pilot/",
            "status": "deployed",
            "version": "1.0.0"
        }
        
        status_file = self.project_root / 'deployment_status.json'
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        
        print("✅ 部署状态文件已创建")
    
    def run_full_deployment(self):
        """运行完整部署流程"""
        print("🚀 PolicyPilot 自动化部署开始")
        print("=" * 50)
        
        # 1. 检查要求
        if not self.check_requirements():
            return False
        
        # 2. 测试本地服务器
        if not self.test_local_server():
            print("⚠️ 本地服务器测试失败，但继续部署...")
        
        # 3. 部署到Heroku
        if not self.deploy_to_heroku():
            print("❌ 部署失败")
            return False
        
        # 4. 测试Heroku部署
        if not self.test_heroku_deployment():
            print("❌ 部署测试失败")
            return False
        
        # 5. 更新前端配置
        self.update_frontend_config()
        
        # 6. 创建部署状态
        self.create_deployment_status()
        
        print("\n🎉 部署完成！")
        print(f"🌐 前端地址: https://viktorsdb.github.io/policy-Pilot/")
        print(f"🔗 后端地址: {self.heroku_url}/api/v1")
        print(f"📊 健康检查: {self.heroku_url}/api/v1/health")
        
        return True

def main():
    """主函数"""
    deployer = PolicyPilotDeployer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            deployer.check_requirements()
        elif command == "test-local":
            deployer.test_local_server()
        elif command == "deploy":
            deployer.deploy_to_heroku()
        elif command == "test-heroku":
            deployer.test_heroku_deployment()
        elif command == "update-config":
            deployer.update_frontend_config()
        else:
            print("❌ 未知命令")
            print("可用命令: check, test-local, deploy, test-heroku, update-config")
    else:
        # 运行完整部署
        deployer.run_full_deployment()

if __name__ == "__main__":
    main() 