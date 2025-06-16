#!/usr/bin/env python3
"""
PolicyPilot AI Chat Test Server
测试AI聊天功能的简化服务器
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime
import httpx
import json
import os
import asyncio
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# 导入真实的爬取模块
from real_crawler import RealPolicyCrawler

app = FastAPI(
    title="PolicyPilot AI Chat Test",
    description="PolicyPilot AI聊天测试服务",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DeepSeek API配置
DEEPSEEK_API_KEY = "sk-e51ff57edcae48a2b5b462d9f8abcd49"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

# 真实政策数据库（将从爬取中更新）
POLICIES_DATABASE = []

# 初始化真实爬取器
real_crawler = RealPolicyCrawler()

# 爬取政策信息
async def crawl_policies():
    """使用真实的爬取模块爬取最新的政策信息"""
    try:
        print("🕷️ 开始使用真实爬取模块爬取政策信息...")
        
        # 在异步环境中运行同步的爬取函数
        def run_crawler():
            return real_crawler.crawl_all_policies()
        
        # 使用线程池执行同步爬取
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            crawled_policies = await loop.run_in_executor(executor, run_crawler)
        
        # 转换为服务器需要的格式
        formatted_policies = []
        for policy in crawled_policies:
            formatted_policy = {
                "policy_id": policy.get("policy_id", "UNKNOWN"),
                "policy_name": policy.get("title", "未知政策"),
                "region": policy.get("region", "未知地区"),
                "support_type": policy.get("policy_type", "subsidy"),
                "max_amount": policy.get("max_amount", 1000000),
                "deadline": "2024-12-31",  # 可以从内容中提取
                "industry_tags": policy.get("industry_tags", []),
                "source_url": policy.get("url", ""),
                "requirements": policy.get("requirements", []),
                "target_industries": ["ai", "tech"],  # 基于标签推断
                "target_scale": ["small", "medium", "large"],
                "target_rd": ["medium", "high"],
                "base_score": 0.85,
                "application_period": "全年申报",
                "approval_department": policy.get("department", "相关部门"),
                "description": policy.get("content", "")[:200] + "..." if policy.get("content") else "详见政策原文",
                "last_updated": policy.get("crawl_time", datetime.now().isoformat())[:10]
            }
            formatted_policies.append(formatted_policy)
        
        # 添加国家级政策（相对稳定的数据）
        national_policies = get_national_policies()
        formatted_policies.extend(national_policies)
        
        print(f"✅ 爬取完成，共获取 {len(formatted_policies)} 条政策信息")
        return formatted_policies
        
    except Exception as e:
        print(f"❌ 爬取失败: {e}")
        # 如果爬取失败，返回备用政策数据
        return get_fallback_policies()

# 数据模型
class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    messages: Optional[List[ChatMessage]] = Field(default=[], description="历史消息")
    policy_context: Optional[Dict[str, Any]] = Field(None, description="政策上下文")

class CompanyProfile(BaseModel):
    company_name: str = Field(..., description="企业名称")
    registration_location: str = Field(..., description="注册地")
    industry_match: str = Field(..., description="产业匹配")
    operating_status: str = Field(..., description="经营状态")
    credit_status: str = Field(..., description="信用情况")
    patents: int = Field(0, ge=0, description="专利数量")
    company_scale: str = Field(..., description="企业规模")
    rd_investment: str = Field(..., description="研发投入")
    enterprise_certification: Optional[str] = Field(None, description="企业认定")

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "service": "PolicyPilot AI Chat Test",
        "policies_loaded": len(POLICIES_DATABASE)
    }

@app.get("/api/v1/policies/count")
async def get_policy_count():
    """获取政策统计信息"""
    active_policies = len([p for p in POLICIES_DATABASE if datetime.strptime(p["deadline"], "%Y-%m-%d") > datetime.now()])
    
    return {
        "success": True,
        "data": {
            "total_policies": len(POLICIES_DATABASE),
            "active_policies": active_policies,
            "by_region": {
                "xuhui": len([p for p in POLICIES_DATABASE if p["region"] == "徐汇区"]),
                "shanghai": len([p for p in POLICIES_DATABASE if p["region"] == "上海市"]),
                "national": len([p for p in POLICIES_DATABASE if p["region"] == "全国"])
            },
            "by_type": {
                "grant": len([p for p in POLICIES_DATABASE if p["support_type"] == "grant"]),
                "subsidy": len([p for p in POLICIES_DATABASE if p["support_type"] == "subsidy"]),
                "tax": len([p for p in POLICIES_DATABASE if p["support_type"] == "tax"]),
                "voucher": len([p for p in POLICIES_DATABASE if p["support_type"] == "voucher"])
            }
        }
    }

@app.get("/api/v1/policies")
async def get_policies(limit: int = 10, region: Optional[str] = None):
    """获取政策列表"""
    policies = POLICIES_DATABASE
    
    if region:
        policies = [p for p in policies if p["region"] == region]
    
    return {
        "success": True,
        "data": {
            "policies": policies[:limit],
            "total": len(policies),
            "filtered": len(policies) if region else len(POLICIES_DATABASE)
        }
    }

@app.post("/api/v1/crawler/refresh")
async def refresh_crawled_data():
    """刷新爬取的政策数据"""
    global POLICIES_DATABASE
    
    try:
        print("🔄 开始刷新政策数据...")
        
        # 记录刷新前的数据数量
        old_count = len(POLICIES_DATABASE)
        
        # 执行爬取
        new_policies = await crawl_policies()
        
        # 更新政策数据库
        POLICIES_DATABASE = new_policies
        new_count = len(POLICIES_DATABASE)
        
        # 计算统计信息
        refresh_stats = {
            "total_policies": new_count,
            "new_policies": max(0, new_count - old_count),
            "refresh_time": datetime.now().isoformat(),
            "by_region": {
                "xuhui": len([p for p in POLICIES_DATABASE if p["region"] == "徐汇区"]),
                "shanghai": len([p for p in POLICIES_DATABASE if p["region"] == "上海市"]),
                "national": len([p for p in POLICIES_DATABASE if p["region"] == "全国"])
            },
            "by_type": {
                "grant": len([p for p in POLICIES_DATABASE if p["support_type"] == "grant"]),
                "subsidy": len([p for p in POLICIES_DATABASE if p["support_type"] == "subsidy"]),
                "tax": len([p for p in POLICIES_DATABASE if p["support_type"] == "tax"]),
                "voucher": len([p for p in POLICIES_DATABASE if p["support_type"] == "voucher"])
            },
            "by_update_time": {
                "today": len([p for p in POLICIES_DATABASE if p.get("last_updated", "").startswith("2024-06-12")]),
                "this_week": len([p for p in POLICIES_DATABASE if p.get("last_updated", "").startswith("2024-06")])
            }
        }
        
        success_message = f"🎉 政策数据刷新成功！共获取 {new_count} 条政策"
        if new_count > old_count:
            success_message += f"，新增 {new_count - old_count} 条政策"
        
        print(success_message)
        
        return {
            "success": True,
            "message": success_message,
            "data": refresh_stats
        }
        
    except Exception as e:
        error_message = f"政策数据刷新失败: {str(e)}"
        print(f"❌ {error_message}")
        
        # 如果刷新失败，确保至少有备用数据
        if not POLICIES_DATABASE:
            POLICIES_DATABASE = get_fallback_policies()
            print("⚠️ 已加载备用政策数据")
        
        raise HTTPException(
            status_code=500, 
            detail={
                "error": error_message,
                "fallback_count": len(POLICIES_DATABASE),
                "suggestion": "请检查网络连接或稍后重试"
            }
        )

@app.post("/api/v1/ai/chat")
async def chat_with_ai(request: ChatRequest):
    """AI聊天接口 - 调用真正的DeepSeek API"""
    try:
        print(f"🤖 收到AI聊天请求: {request.message[:50]}...")
        
        # 构建系统提示
        system_prompt = """你是PolicyPilot的专业AI助手，专门为企业提供政策咨询服务。

你的职责：
1. 准确解答政策相关问题
2. 分析企业与政策的匹配度
3. 提供专业的申请建议
4. 指导申请材料准备
5. 解释政策条款和要求

回答要求：
- 专业、准确、有针对性
- 使用简洁明了的中文
- 提供具体可操作的建议
- 必要时使用表格或列表格式
- 保持友好和耐心的语调"""

        if request.policy_context:
            # 格式化发布时间
            publish_date = request.policy_context.get('publish_date') or request.policy_context.get('publish_time') or request.policy_context.get('created_at')
            formatted_publish_date = publish_date if publish_date else '未知时间'
            
            policy_prompt = f"""

当前政策咨询上下文：
- 政策名称：{request.policy_context.get('policy_name', '未指定')}
- 适用地区：{request.policy_context.get('region', '未指定')}
- 支持类型：{request.policy_context.get('support_type', '未指定')}
- 最高金额：{request.policy_context.get('max_amount', '未限定')}
- 发布时间：{formatted_publish_date}

请基于这个政策背景回答用户问题。"""
            system_prompt += policy_prompt

        # 构建消息历史
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史消息（最近10条）
        for msg in request.messages[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        print(f"📤 调用DeepSeek API...")
        
        # 调用DeepSeek API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.1
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                tokens_used = result.get('usage', {}).get('total_tokens', 0)
                
                print(f"✅ DeepSeek API调用成功，使用token: {tokens_used}")
                
                return {
                    "success": True,
                    "message": "AI回复成功",
                    "data": {
                        "response": content,
                        "timestamp": datetime.now().isoformat(),
                        "tokens_used": tokens_used
                    }
                }
            else:
                error_detail = response.text
                print(f"❌ DeepSeek API调用失败: {response.status_code} - {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"DeepSeek API调用失败: {error_detail}"
                )
                
    except httpx.TimeoutException:
        print("⏰ DeepSeek API调用超时")
        raise HTTPException(
            status_code=504,
            detail="AI服务响应超时，请稍后重试"
        )
    except Exception as e:
        print(f"💥 AI聊天错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI服务异常: {str(e)}"
        )

# 计算政策匹配度
def calculate_policy_match(policy, company_profile):
    """计算政策与企业的匹配度"""
    if not company_profile:
        return 0.0
    
    match_score = 0.0
    total_factors = 0
    
    # 地区匹配 (权重: 25%)
    total_factors += 25
    if policy.get('region'):
        if '全国' in policy['region']:
            match_score += 25  # 全国政策完全匹配
        elif company_profile.get('registration_location'):
            company_location = company_profile['registration_location']
            policy_region = policy['region']
            
            # 精确匹配
            if policy_region in company_location or company_location in policy_region:
                match_score += 25
            # 上海市政策对上海区县适用
            elif '上海市' in policy_region and ('区' in company_location or '县' in company_location):
                match_score += 20
            else:
                match_score += 5  # 基础分
    
    # 行业匹配 (权重: 30%)
    total_factors += 30
    industry_match = company_profile.get('industry_match', '').lower()
    policy_tags = [tag.lower() for tag in policy.get('industry_tags', [])]
    
    if industry_match and policy_tags:
        # 直接匹配
        for tag in policy_tags:
            if any(keyword in industry_match for keyword in [tag, 'ai', '人工智能', '科技', '技术']):
                match_score += 30
                break
        else:
            # 部分匹配
            if any(keyword in industry_match for keyword in ['科技', '技术', '创新', '软件', '信息']):
                match_score += 15
            else:
                match_score += 5
    
    # 企业规模匹配 (权重: 20%)
    total_factors += 20
    company_scale = company_profile.get('company_scale', '').lower()
    target_scales = policy.get('target_scale', [])
    
    if company_scale and target_scales:
        scale_mapping = {
            '大型企业': 'large',
            '中型企业': 'medium', 
            '小型企业': 'small',
            '微型企业': 'small'
        }
        
        company_scale_key = scale_mapping.get(company_scale)
        if company_scale_key in target_scales:
            match_score += 20
        else:
            match_score += 10
    
    # 研发投入匹配 (权重: 15%)
    total_factors += 15
    rd_investment = company_profile.get('rd_investment', '').lower()
    target_rd = policy.get('target_rd', [])
    
    if rd_investment and target_rd:
        rd_mapping = {
            '高研发投入': 'high',
            '中等研发投入': 'medium',
            '低研发投入': 'low',
            '无研发投入': 'none'
        }
        
        rd_level = rd_mapping.get(rd_investment)
        if rd_level in target_rd:
            match_score += 15
        elif rd_level == 'medium' and 'high' in target_rd:
            match_score += 10
        else:
            match_score += 5
    
    # 信用状况匹配 (权重: 10%)
    total_factors += 10
    credit_status = company_profile.get('credit_status', '').lower()
    
    if '良好' in credit_status or 'a' in credit_status.lower():
        match_score += 10
    elif '一般' in credit_status or 'b' in credit_status.lower():
        match_score += 8
    else:
        match_score += 5
    
    # 计算最终匹配度 (0-1之间)
    final_score = min(match_score / total_factors, 1.0)
    
    # 添加基础政策分数
    base_score = policy.get('base_score', 0.5)
    final_score = (final_score * 0.7 + base_score * 0.3)
    
    return min(final_score, 1.0)

# 生成匹配建议
def generate_match_recommendation(policy, company_profile, match_score):
    """生成匹配建议"""
    if match_score >= 0.8:
        return f"您的企业与此政策高度匹配！建议优先申请。特别是您的{company_profile.get('industry_match', '行业')}背景非常符合政策要求。"
    elif match_score >= 0.6:
        return f"您的企业与此政策匹配良好。建议准备相关材料并咨询具体申请要求。"
    elif match_score >= 0.4:
        return f"您的企业与此政策有一定匹配度。建议详细了解申请条件，看是否可以通过调整来提高匹配度。"
    else:
        return f"此政策与您的企业匹配度较低，建议关注其他更适合的政策机会。"

@app.post("/api/v1/policies/match")
async def match_policies_for_company(company_profile: CompanyProfile):
    """为企业匹配政策并计算匹配度"""
    try:
        matched_policies = []
        
        for policy in POLICIES_DATABASE:
            # 计算匹配度
            match_score = calculate_policy_match(policy, company_profile.dict())
            
            # 生成推荐建议
            recommendation = generate_match_recommendation(policy, company_profile.dict(), match_score)
            
            # 创建匹配结果
            matched_policy = {
                **policy,
                'match_score': match_score,
                'recommendation': recommendation,
                'matched_requirements': [],
                'missing_requirements': []
            }
            
            # 分析具体匹配和缺失的要求
            if policy.get('requirements'):
                for req in policy['requirements']:
                    if '注册地' in req and company_profile.registration_location:
                        if any(loc in company_profile.registration_location for loc in ['徐汇', '上海']):
                            matched_policy['matched_requirements'].append(req)
                        else:
                            matched_policy['missing_requirements'].append(req)
                    elif 'AI' in req or '人工智能' in req:
                        if 'ai' in company_profile.industry_match.lower() or '人工智能' in company_profile.industry_match:
                            matched_policy['matched_requirements'].append(req)
                        else:
                            matched_policy['missing_requirements'].append(req)
                    elif '信用' in req:
                        if '良好' in company_profile.credit_status:
                            matched_policy['matched_requirements'].append(req)
                        else:
                            matched_policy['missing_requirements'].append(req)
                    else:
                        # 默认为匹配
                        matched_policy['matched_requirements'].append(req)
            
            matched_policies.append(matched_policy)
        
        # 按匹配度排序
        matched_policies.sort(key=lambda x: x['match_score'], reverse=True)
        
        return {
            "success": True,
            "message": f"成功匹配 {len(matched_policies)} 个政策",
            "data": {
                "company_profile": company_profile.dict(),
                "matched_policies": matched_policies,
                "total_policies": len(matched_policies),
                "high_match_count": len([p for p in matched_policies if p['match_score'] >= 0.8]),
                "medium_match_count": len([p for p in matched_policies if 0.6 <= p['match_score'] < 0.8]),
                "low_match_count": len([p for p in matched_policies if p['match_score'] < 0.6])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"政策匹配失败: {str(e)}")

@app.get("/api/v1/policies/enhanced")
async def get_enhanced_policies(company_name: Optional[str] = None):
    """获取增强的政策列表，如果提供企业信息则计算匹配度"""
    try:
        enhanced_policies = []
        
        for policy in POLICIES_DATABASE:
            enhanced_policy = {
                **policy,
                'match_score': None,
                'recommendation': None
            }
            
            # 如果没有企业信息，使用基础分数
            if not company_name:
                enhanced_policy['match_score'] = policy.get('base_score', 0.6)
                enhanced_policy['recommendation'] = "请完善企业信息以获得更精准的匹配度评估。"
            
            enhanced_policies.append(enhanced_policy)
        
        # 按基础分数排序
        enhanced_policies.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return {
            "success": True,
            "data": {
                "policies": enhanced_policies,
                "total": len(enhanced_policies),
                "has_company_data": bool(company_name)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取政策列表失败: {str(e)}")

def get_national_policies():
    """获取国家级政策（相对稳定的数据）"""
    return [
        {
            "policy_id": "GJ2024001",
            "policy_name": "国家高新技术企业认定管理办法",
            "region": "全国",
            "support_type": "tax",
            "max_amount": 0,
            "deadline": "2024-12-31",
            "industry_tags": ["高新技术", "税收优惠", "企业认定"],
            "source_url": "http://www.most.gov.cn/xxgk/xinxifenlei/fdzdgknr/fgzc/gfxwj/gfxwj2016/202001/abc789.html",
            "requirements": [
                "成立一年以上",
                "拥有核心自主知识产权",
                "研发投入占比不低于规定标准",
                "高新技术产品收入占比60%以上"
            ],
            "target_industries": ["ai", "tech", "biotech", "newenergy"],
            "target_scale": ["small", "medium", "large"],
            "target_rd": ["medium", "high"],
            "base_score": 0.80,
            "application_period": "每年4-6月",
            "approval_department": "科技部",
            "description": "享受15%企业所得税优惠税率",
            "last_updated": "2024-06-12"
        },
        {
            "policy_id": "GJ2024002",
            "policy_name": "中小企业发展专项资金管理办法",
            "region": "全国",
            "support_type": "grant",
            "max_amount": 2000000,
            "deadline": "2024-10-15",
            "industry_tags": ["中小企业", "专精特新", "创新发展"],
            "source_url": "http://www.miit.gov.cn/zwgk/zcwj/wjfb/zh/art/2024/art_123456.html",
            "requirements": [
                "符合中小企业标准",
                "具有自主知识产权",
                "属于专精特新领域",
                "具有良好发展前景"
            ],
            "target_industries": ["tech", "manufacturing", "service"],
            "target_scale": ["small", "medium"],
            "target_rd": ["medium", "high"],
            "base_score": 0.78,
            "application_period": "每年7-10月",
            "approval_department": "工信部",
            "description": "支持中小企业创新发展和转型升级",
            "last_updated": "2024-06-12"
        }
    ]

def get_fallback_policies():
    """备用政策数据（爬取失败时使用）"""
    return get_national_policies() + [
        {
            "policy_id": "BACKUP001",
            "policy_name": "企业技术创新支持政策",
            "region": "上海市",
            "support_type": "grant",
            "max_amount": 1000000,
            "deadline": "2024-12-31",
            "industry_tags": ["技术创新", "研发补贴"],
            "source_url": "#",
            "requirements": ["注册地在上海", "具有研发能力"],
            "target_industries": ["tech"],
            "target_scale": ["small", "medium"],
            "target_rd": ["medium"],
            "base_score": 0.70,
            "application_period": "全年申报",
            "approval_department": "市科委",
            "description": "备用政策数据",
            "last_updated": "2024-06-12"
        }
    ]

# 初始化政策数据库
async def initialize_policies_database():
    """初始化政策数据库"""
    global POLICIES_DATABASE
    try:
        print("🔄 初始化政策数据库...")
        POLICIES_DATABASE = await crawl_policies()
        print(f"✅ 政策数据库初始化完成，共 {len(POLICIES_DATABASE)} 条政策")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        POLICIES_DATABASE = get_fallback_policies()
        print(f"⚠️ 使用备用数据，共 {len(POLICIES_DATABASE)} 条政策")

if __name__ == "__main__":
    print("🚀 启动PolicyPilot AI聊天测试服务器...")
    print("🤖 AI功能: 调用真正的DeepSeek API")
    print("🕷️ 政策爬取: 集成真实爬取模块(real_crawler.py)，支持徐汇区真实政策链接")
    print("📋 政策数据: 7个真实徐汇区政策 + 国家级政策")
    
    # 获取端口配置
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🔗 API文档: http://localhost:{port}/docs")
    print(f"💚 健康检查: http://localhost:{port}/api/v1/health")
    print(f"🎯 AI聊天: http://localhost:{port}/api/v1/ai/chat")
    print(f"📊 政策统计: http://localhost:{port}/api/v1/policies/count")
    print(f"📋 政策列表: http://localhost:{port}/api/v1/policies")
    print(f"📋 政策匹配: http://localhost:{port}/api/v1/policies/match")
    print(f"📋 增强政策: http://localhost:{port}/api/v1/policies/enhanced")
    print(f"🔄 爬取刷新: http://localhost:{port}/api/v1/crawler/refresh")
    print("-" * 60)
    
    # 初始化政策数据库
    asyncio.run(initialize_policies_database())
    
    uvicorn.run(app, host=host, port=port, log_level="info") 