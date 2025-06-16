#!/usr/bin/env python3
"""
部署测试脚本
验证PolicyPilot后端服务是否正常工作
"""

import requests
import json
import time
import sys

def test_api_endpoint(url, description):
    """测试API端点"""
    try:
        print(f"🔍 测试 {description}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {description} - 正常")
            return True
        else:
            print(f"❌ {description} - 状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {description} - 连接失败: {e}")
        return False

def test_ai_chat(base_url):
    """测试AI聊天功能"""
    try:
        print("🤖 测试AI聊天功能...")
        
        chat_data = {
            "message": "什么是高新技术企业认定？",
            "messages": [],
            "policy_context": None,
            "stream": False
        }
        
        response = requests.post(
            f"{base_url}/ai/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ AI聊天功能 - 正常")
                return True
            else:
                print(f"❌ AI聊天功能 - API返回错误: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ AI聊天功能 - 状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ AI聊天功能 - 连接失败: {e}")
        return False

def test_policy_matching(base_url):
    """测试政策匹配功能"""
    try:
        print("📋 测试政策匹配功能...")
        
        company_data = {
            "company_name": "测试科技有限公司",
            "registration_location": "徐汇区",
            "industry_match": "AI/科技",
            "operating_status": "良好",
            "credit_status": "良好",
            "patents": 5,
            "company_scale": "500万-2000万",
            "rd_investment": "5%-10%",
            "enterprise_certification": "高新技术企业"
        }
        
        response = requests.post(
            f"{base_url}/policies/match",
            json=company_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                matched_count = len(result.get("data", {}).get("matched_policies", []))
                print(f"✅ 政策匹配功能 - 正常，匹配到 {matched_count} 个政策")
                return True
            else:
                print(f"❌ 政策匹配功能 - API返回错误: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 政策匹配功能 - 状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 政策匹配功能 - 连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试PolicyPilot部署...")
    print("=" * 50)
    
    # 测试不同环境的API地址
    test_urls = [
        ("本地环境", "http://localhost:8001/api/v1"),
        ("Heroku部署", "https://policy-pilot-viktorsdb.herokuapp.com/api/v1"),
    ]
    
    for env_name, base_url in test_urls:
        print(f"\n🌐 测试 {env_name}: {base_url}")
        print("-" * 40)
        
        # 基础API测试
        tests = [
            (f"{base_url}/health", "健康检查"),
            (f"{base_url}/policies/count", "政策统计"),
            (f"{base_url}/policies", "政策列表"),
            (f"{base_url}/policies/enhanced", "增强政策列表"),
        ]
        
        success_count = 0
        total_tests = len(tests) + 2  # 加上AI聊天和政策匹配测试
        
        # 执行基础测试
        for url, desc in tests:
            if test_api_endpoint(url, desc):
                success_count += 1
        
        # 执行功能测试
        if test_ai_chat(base_url):
            success_count += 1
            
        if test_policy_matching(base_url):
            success_count += 1
        
        # 显示结果
        print(f"\n📊 {env_name} 测试结果: {success_count}/{total_tests} 通过")
        
        if success_count == total_tests:
            print(f"🎉 {env_name} 部署完全正常！")
        elif success_count >= total_tests * 0.7:
            print(f"⚠️ {env_name} 部分功能正常，建议检查失败的服务")
        else:
            print(f"❌ {env_name} 存在严重问题，需要修复")
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")

if __name__ == "__main__":
    main() 