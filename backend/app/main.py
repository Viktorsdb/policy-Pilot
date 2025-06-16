#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime, date
import json
import sqlite3
import os
from pathlib import Path
import asyncio
import time
import httpx
import logging

# 导入AI聊天路由
try:
    from app.routes.ai_chat import router as ai_chat_router
    AI_CHAT_AVAILABLE = True
    print("✅ AI聊天模块导入成功")
except ImportError as e:
    AI_CHAT_AVAILABLE = False
    print(f"⚠️ AI聊天模块导入失败: {e}")

# 创建FastAPI应用
app = FastAPI(
    title="PolicyPilot API",
    description="PolicyPilot - 智能政策匹配平台",
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

# 注册AI聊天路由
if AI_CHAT_AVAILABLE:
    app.include_router(ai_chat_router, prefix="/api/v1/ai", tags=["AI聊天"])
    print("✅ AI聊天路由已注册: /api/v1/ai/chat")
else:
    print("❌ AI聊天路由注册失败")

# AI聊天相关配置
DEEPSEEK_API_KEY = "sk-e51ff57edcae48a2b5b462d9f8abcd49"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

# AI聊天数据模型
class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    messages: Optional[List[ChatMessage]] = Field(default=[], description="历史消息")
    policy_context: Optional[Dict[str, Any]] = Field(None, description="政策上下文")

# 数据模型
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
    contact_phone: Optional[str] = Field(None, description="联系电话")
    contact_email: Optional[str] = Field(None, description="联系邮箱")

class PolicyMatch(BaseModel):
    policy_id: str
    policy_name: str
    region: str
    support_type: str
    max_amount: int
    deadline: str
    industry_tags: List[str]
    source_url: str
    requirements: List[str]
    match_score: float
    matched_requirements: List[str]
    missing_requirements: List[str]
    recommendation: str

class MatchResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]

# 全局政策数据库（动态更新）
POLICIES_DATABASE = []

# 加载爬取的政策数据
def load_crawled_policies():
    """从爬虫数据文件加载政策"""
    global POLICIES_DATABASE
    
    # 尝试从爬虫输出文件加载
    crawl_data_path = "data/real_policies.json"
    if os.path.exists(crawl_data_path):
        try:
            with open(crawl_data_path, 'r', encoding='utf-8') as f:
                crawled_data = json.load(f)
            
            # 转换爬取数据为标准格式
            converted_policies = []
            for i, policy in enumerate(crawled_data):
                converted_policy = {
                    "policy_id": policy.get("policy_id", f"CRAWL_{i+1:03d}"),
                    "policy_name": policy.get("title", "未知政策"),
                    "region": policy.get("region", "徐汇区"),
                    "support_type": policy.get("policy_type", "subsidy"),
                    "max_amount": policy.get("max_amount", 1000000),
                    "deadline": policy.get("publish_date", "2024-12-31"),
                    "industry_tags": policy.get("industry_tags", ["科技创新"]),
                    "source_url": policy.get("url", ""),
                    "requirements": policy.get("requirements", ["企业注册地在徐汇区", "符合相关条件"]),
                    "target_industries": ["ai", "tech"],
                    "target_scale": ["small", "medium", "large"],
                    "target_rd": ["medium", "high"],
                    "base_score": 0.75,
                    "application_period": "全年申报",
                    "approval_department": policy.get("department", "徐汇区相关部门")
                }
                converted_policies.append(converted_policy)
            
            POLICIES_DATABASE.extend(converted_policies)
            print(f"✅ 成功加载 {len(converted_policies)} 条爬取的政策数据")
            return len(converted_policies)
            
        except Exception as e:
            print(f"⚠️ 加载爬取数据失败: {e}")
    
    # 如果没有爬取数据，使用基础模拟数据
    if not POLICIES_DATABASE:
        POLICIES_DATABASE.extend(get_fallback_policies())
        print("📋 使用默认政策数据")
    
    return len(POLICIES_DATABASE)

def get_fallback_policies():
    """获取基础模拟政策数据（当爬取失败时使用）"""
    return [
        {
            "policy_id": "XH2024001",
            "policy_name": "徐汇区人工智能产业发展专项扶持资金",
            "region": "徐汇区",
            "support_type": "grant",
            "max_amount": 3000000,
            "deadline": "2024-12-31",
            "industry_tags": ["人工智能", "AI", "科技创新"],
            "source_url": "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab01934dd52e3d09b9",
            "requirements": [
                "企业注册地在徐汇区",
                "从事人工智能相关业务",
                "企业信用等级B级以上"
            ],
            "target_industries": ["ai", "tech"],
            "target_scale": ["small", "medium", "large"],
            "target_rd": ["medium", "high"],
            "base_score": 0.85,
            "application_period": "全年申报",
            "approval_department": "徐汇区科委"
        },
        {
            "policy_id": "XH2024002",
            "policy_name": "徐汇区关于推动具身智能产业发展的若干意见",
            "region": "徐汇区",
            "support_type": "subsidy",
            "max_amount": 2000000,
            "deadline": "2024-11-30",
            "industry_tags": ["具身智能", "AI", "机器人"],
            "source_url": "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab01934dd6cfbd09bb",
            "requirements": [
                "企业注册地在徐汇区",
                "从事具身智能产业",
                "拥有相关技术专利"
            ],
            "target_industries": ["ai", "tech"],
            "target_scale": ["medium", "large"],
            "target_rd": ["high"],
            "base_score": 0.80,
            "application_period": "每年8-11月",
            "approval_department": "徐汇区科委"
        },
        {
            "policy_id": "XH2024003",
            "policy_name": "关于支持上海市生成式人工智能创新生态先导区的若干措施",
            "region": "徐汇区",
            "support_type": "grant",
            "max_amount": 5000000,
            "deadline": "2024-10-31",
            "industry_tags": ["生成式AI", "大模型", "创新生态"],
            "source_url": "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab019384dc95a70aed",
            "requirements": [
                "企业注册地在徐汇区",
                "从事生成式AI相关业务",
                "具有重大技术突破"
            ],
            "target_industries": ["ai", "tech"],
            "target_scale": ["small", "medium", "large"],
            "target_rd": ["high"],
            "base_score": 0.90,
            "application_period": "全年申报",
            "approval_department": "徐汇区政府"
        }
    ]

def calculate_policy_match(company: CompanyProfile, policy: dict) -> Optional[PolicyMatch]:
    """使用真实数据计算企业与政策的匹配度"""
    
    # 基础匹配分数
    match_score = policy["base_score"]
    matched_requirements = []
    missing_requirements = []
    
    # 地区匹配检查（徐汇区政策必须在徐汇区注册）
    if policy["region"] == "徐汇区" and company.registration_location != "xuhui":
        return None  # 不符合地区要求，直接排除
    
    # 行业匹配度评估
    industry_match_bonus = 0
    if company.industry_match in policy["target_industries"]:
        industry_match_bonus = 0.15
        matched_requirements.append(f"✅ 行业匹配: {get_industry_name(company.industry_match)}")
    else:
        industry_match_bonus = -0.05
        missing_requirements.append(f"⚠️ 行业匹配度较低，建议关注{', '.join([get_industry_name(ind) for ind in policy['target_industries'][:2]])}")
    
    match_score += industry_match_bonus
    
    # 企业规模匹配
    scale_match_bonus = 0
    if company.company_scale in policy["target_scale"]:
        scale_match_bonus = 0.10
        matched_requirements.append(f"✅ 企业规模符合: {get_scale_name(company.company_scale)}")
    else:
        missing_requirements.append(f"📏 建议企业规模达到: {', '.join([get_scale_name(s) for s in policy['target_scale']])}")
    
    match_score += scale_match_bonus
    
    # 研发投入评估
    rd_match_bonus = 0
    if company.rd_investment in policy["target_rd"]:
        rd_match_bonus = 0.12
        matched_requirements.append(f"✅ 研发投入水平: {get_rd_name(company.rd_investment)}")
    else:
        rd_match_bonus = -0.08
        missing_requirements.append(f"🔬 建议提升研发投入至: {', '.join([get_rd_name(rd) for rd in policy['target_rd']])}")
    
    match_score += rd_match_bonus
    
    # 专利数量评估
    patent_bonus = 0
    if company.patents >= 5:
        patent_bonus = 0.15
        matched_requirements.append(f"🏆 拥有{company.patents}项专利，知识产权优势明显")
    elif company.patents >= 1:
        patent_bonus = 0.08
        matched_requirements.append(f"📋 拥有{company.patents}项专利")
    else:
        patent_bonus = -0.05
        missing_requirements.append("💡 建议申请相关技术专利或软件著作权")
    
    match_score += patent_bonus
    
    # 企业认定加分
    certification_bonus = 0
    if company.enterprise_certification:
        if company.enterprise_certification == "high_tech":
            certification_bonus = 0.20
            matched_requirements.append("🎖️ 高新技术企业认定 - 重大优势")
        elif company.enterprise_certification == "specialized":
            certification_bonus = 0.15
            matched_requirements.append("⭐ 专精特新企业认定 - 显著优势")
        elif company.enterprise_certification == "sme":
            certification_bonus = 0.10
            matched_requirements.append("🏢 中小企业认定")
        elif company.enterprise_certification == "startup":
            certification_bonus = 0.08
            matched_requirements.append("🚀 初创企业")
    else:
        missing_requirements.append("🏅 建议申请高新技术企业或专精特新认定")
    
    match_score += certification_bonus
    
    # 信用状况评估
    if company.credit_status == "good":
        match_score += 0.05
        matched_requirements.append("✅ 企业信用状况良好")
    else:
        match_score -= 0.10
        missing_requirements.append("⚠️ 需要改善企业信用状况")
    
    # 经营状况评估
    if company.operating_status == "good":
        match_score += 0.05
        matched_requirements.append("✅ 企业经营状况良好")
    else:
        match_score -= 0.10
        missing_requirements.append("⚠️ 需要改善企业经营状况")
    
    # 特殊政策匹配逻辑
    if policy["support_type"] == "tax" and company.enterprise_certification != "high_tech":
        missing_requirements.append("🎯 税收优惠政策建议先申请高新技术企业认定")
    
    if policy["support_type"] == "loan" and company.credit_status != "good":
        match_score -= 0.15
        missing_requirements.append("💳 融资类政策对信用要求较高")
    
    # 确保分数在0-1之间
    match_score = max(0.0, min(1.0, match_score))
    
    # 生成个性化推荐建议
    recommendation = generate_smart_recommendation(company, policy, match_score, missing_requirements)
    
    return PolicyMatch(
        policy_id=policy["policy_id"],
        policy_name=policy["policy_name"],
        region=policy["region"],
        support_type=policy["support_type"],
        max_amount=policy["max_amount"],
        deadline=policy["deadline"],
        industry_tags=policy["industry_tags"],
        source_url=policy["source_url"],
        requirements=policy["requirements"],
        match_score=match_score,
        matched_requirements=matched_requirements,
        missing_requirements=missing_requirements,
        recommendation=recommendation
    )

def generate_smart_recommendation(company: CompanyProfile, policy: dict, score: float, missing: List[str]) -> str:
    """生成智能化个性化推荐建议"""
    
    recommendations = []
    
    # 基于匹配度的主要建议
    if score >= 0.85:
        recommendations.append("🎯 **强烈推荐申请！** 您的企业条件与该政策高度匹配，成功概率很高。")
    elif score >= 0.70:
        recommendations.append("👍 **推荐申请** 您的企业具备良好的申请条件，建议积极准备材料。")
    elif score >= 0.50:
        recommendations.append("🤔 **可以考虑申请** 需要完善部分条件，建议评估投入产出比。")
    elif score >= 0.30:
        recommendations.append("📋 **暂不建议申请** 当前条件不够充分，建议先提升企业资质。")
    else:
        recommendations.append("❌ **不适合申请** 企业条件与政策要求差距较大。")
    
    # 基于企业特点的针对性建议
    if company.enterprise_certification == "high_tech":
        recommendations.append("🏆 作为高新技术企业，您在税收优惠和科技项目申报方面有显著优势。")
    
    if company.patents >= 5:
        recommendations.append("💎 您的知识产权储备丰富，在创新类政策申报中具有竞争优势。")
    
    if company.industry_match == "ai":
        recommendations.append("🤖 AI产业是当前政策重点支持领域，建议关注相关专项政策。")
    
    # 基于政策类型的申报建议
    support_type_advice = {
        "grant": "💰 **无偿资助政策** - 重点准备项目实施方案、预算明细和技术路线图。建议展示项目的创新性和产业化前景。",
        "subsidy": "💵 **补贴政策** - 准备相关支出凭证和财务审计报告。确保资金用途符合政策规定。",
        "tax": "🧾 **税收优惠政策** - 准备研发费用归集、知识产权证明等材料。建议提前规划税务筹划。",
        "loan": "🏦 **融资支持政策** - 准备完整的财务报表、资信证明和担保材料。确保还款能力充足。",
        "investment": "💼 **投资政策** - 准备详细的商业计划书和团队介绍。重点展示商业模式和市场前景。"
    }
    
    if policy["support_type"] in support_type_advice:
        recommendations.append(support_type_advice[policy["support_type"]])
    
    # 时间规划建议
    deadline_str = policy.get("deadline", "")
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            days_left = (deadline - datetime.now()).days
            if days_left <= 30:
                recommendations.append(f"⏰ **紧急提醒** 申报截止时间仅剩{days_left}天，请抓紧准备材料！")
            elif days_left <= 90:
                recommendations.append(f"📅 申报截止时间还有{days_left}天，建议尽快启动申报准备工作。")
        except:
            pass
    
    # 基于缺失条件的改进建议
    if missing:
        missing_str = " ".join(missing)
        if "专利" in missing_str:
            recommendations.append("📝 **知识产权建议**: 可以先申请实用新型专利或软件著作权，审批周期较短。")
        if "研发投入" in missing_str:
            recommendations.append("🔬 **研发投入建议**: 建立研发项目台账，规范研发费用归集和管理。")
        if "认定" in missing_str:
            recommendations.append("🏅 **资质认定建议**: 高新技术企业认定每年4-6月申报，专精特新认定通常在下半年。")
    
    return " ".join(recommendations)

def get_industry_name(code: str) -> str:
    """获取行业中文名称"""
    mapping = {
        "ai": "人工智能",
        "tech": "科技",
        "manufacturing": "制造业", 
        "service": "服务业",
        "biotech": "生物技术",
        "newenergy": "新能源",
        "software": "软件",
        "other": "其他"
    }
    return mapping.get(code, code)

def get_scale_name(code: str) -> str:
    """获取企业规模中文名称"""
    mapping = {
        "micro": "微型企业",
        "small": "小型企业", 
        "medium": "中型企业",
        "large": "大型企业",
        "startup": "初创企业"
    }
    return mapping.get(code, code)

def get_rd_name(code: str) -> str:
    """获取研发投入中文名称"""
    mapping = {
        "low": "较低(≤3%)",
        "medium": "中等(3-6%)",
        "high": "较高(≥6%)"
    }
    return mapping.get(code, code)

# API路由
@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "service": "PolicyPilot API",
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
                "loan": len([p for p in POLICIES_DATABASE if p["support_type"] == "loan"]),
                "tax": len([p for p in POLICIES_DATABASE if p["support_type"] == "tax"]),
                "investment": len([p for p in POLICIES_DATABASE if p["support_type"] == "investment"])
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
    try:
        # 重新加载爬取数据
        loaded_count = load_crawled_policies()
        
        return {
            "success": True,
            "message": f"成功刷新政策数据，共加载 {loaded_count} 条政策",
            "data": {
                "total_policies": len(POLICIES_DATABASE),
                "refresh_time": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新数据失败: {str(e)}")

@app.post("/api/v1/match/simple")
async def match_policies(company: CompanyProfile):
    """智能政策匹配 - 使用真实数据"""
    try:
        matches = []
        
        # 对每个政策进行匹配计算
        for policy in POLICIES_DATABASE:
            match_result = calculate_policy_match(company, policy)
            if match_result and match_result.match_score > 0.25:  # 只返回匹配度>25%的政策
                matches.append(match_result)
        
        # 按匹配度排序，返回Top5
        matches.sort(key=lambda x: x.match_score, reverse=True)
        top_matches = matches[:5]
        
        # 保存企业信息到数据库（可选）
        save_company_profile(company)
        
        return MatchResponse(
            success=True,
            message=f"基于 {len(POLICIES_DATABASE)} 条政策数据成功匹配到 {len(top_matches)} 个政策机会",
            data={
                "company_info": company.dict(),
                "matches": [match.dict() for match in top_matches],
                "count": len(top_matches),
                "total_checked": len(POLICIES_DATABASE),
                "match_timestamp": datetime.now().isoformat(),
                "avg_match_score": sum(m.match_score for m in top_matches) / len(top_matches) if top_matches else 0
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"政策匹配失败: {str(e)}")

def save_company_profile(company: CompanyProfile):
    """保存企业信息到数据库"""
    try:
        # 创建数据目录
        os.makedirs("data", exist_ok=True)
        
        # 简单的JSON文件存储
        profile_data = {
            "company_info": company.dict(),
            "submit_time": datetime.now().isoformat(),
            "id": f"company_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        with open(f"data/companies.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(profile_data, ensure_ascii=False) + "\n")
            
    except Exception as e:
        print(f"保存企业信息失败: {e}")

# 启动时初始化政策数据库
@app.on_event("startup")
async def startup_event():
    """应用启动时加载政策数据"""
    print("🚀 启动PolicyPilot API服务器...")
    loaded_count = load_crawled_policies()
    print(f"📋 政策数据库已就绪，共 {loaded_count} 条政策")

# 直接在main.py中添加AI聊天端点
@app.post("/api/v1/ai/chat")
async def chat_with_ai(request: ChatRequest):
    """AI聊天接口 - 调用DeepSeek API"""
    try:
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
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"DeepSeek API调用失败: {error_detail}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="AI服务响应超时，请稍后重试"
        )
    except Exception as e:
        print(f"AI聊天错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI服务异常: {str(e)}"
        )

if __name__ == "__main__":
    print("🚀 启动PolicyPilot API服务器...")
    print("📊 正在加载政策数据...")
    load_crawled_policies()
    print(f"📋 共加载 {len(POLICIES_DATABASE)} 条政策")
    print("🔗 API文档: http://localhost:8000/docs")
    print("💚 健康检查: http://localhost:8000/api/v1/health")
    print("🎯 政策匹配: http://localhost:8000/api/v1/match/simple")
    print("🔄 刷新数据: http://localhost:8000/api/v1/crawler/refresh")
    print("-" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 