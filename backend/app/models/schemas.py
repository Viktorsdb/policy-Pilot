from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class IndustryType(str, Enum):
    """产业类型枚举"""
    AI_TECH = "ai-tech"
    MANUFACTURING = "manufacturing"
    SERVICE = "service"
    OTHER = "other"

class CompanyScale(str, Enum):
    """企业规模枚举"""
    UNDER_5M = "under-5m"
    RANGE_5M_20M = "5m-20m"
    RANGE_20M_100M = "20m-100m"
    OVER_100M = "over-100m"

class RDInvestment(str, Enum):
    """研发投入占比枚举"""
    UNDER_3 = "under-3"
    RANGE_3_5 = "3-5"
    RANGE_5_10 = "5-10"
    OVER_10 = "over-10"

class EnterpriseCertification(str, Enum):
    """企业认定类型枚举"""
    HIGH_TECH = "high-tech"
    SPECIALIZED = "specialized"
    LITTLE_GIANT = "little-giant"
    LISTED = "listed"

class SupportType(str, Enum):
    """政策支持类型枚举"""
    GRANT = "grant"  # 无偿资助
    LOAN = "loan"    # 贷款贴息
    TAX = "tax"      # 税收优惠
    SUBSIDY = "subsidy"  # 补贴
    OTHER = "other"

class CompanyProfile(BaseModel):
    """企业画像数据模型"""
    company_name: str = Field(..., description="企业名称")
    registration_location: str = Field("xuhui", description="注册地，目前仅支持徐汇区")
    industry_match: IndustryType = Field(..., description="企业产业匹配")
    operating_status: str = Field("good", description="企业经营状态")
    credit_status: str = Field("good", description="企业信用情况")
    patents: Optional[int] = Field(0, ge=0, description="企业科创专利数量")
    company_scale: CompanyScale = Field(..., description="企业规模")
    rd_investment: RDInvestment = Field(..., description="研发投入占比")
    enterprise_certification: Optional[EnterpriseCertification] = Field(None, description="企业认定类型")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    
    @validator('registration_location')
    def validate_location(cls, v):
        if v != 'xuhui':
            raise ValueError('目前仅支持徐汇区注册企业')
        return v

class PolicyInfo(BaseModel):
    """政策信息数据模型"""
    policy_name: str = Field(..., description="政策名称")
    region: str = Field(..., description="适用地区")
    industry_tags: List[str] = Field(..., description="产业标签")
    requirements: List[str] = Field(..., description="申请要求")
    support_type: SupportType = Field(..., description="支持类型")
    max_amount: Optional[float] = Field(None, description="最高支持金额")
    deadline: Optional[datetime] = Field(None, description="申请截止时间")
    content: str = Field(..., description="政策正文")
    source_url: str = Field(..., description="原文链接")
    pdf_url: Optional[str] = Field(None, description="PDF附件链接")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class PolicyMatch(BaseModel):
    """政策匹配结果数据模型"""
    policy_id: str = Field(..., description="政策ID")
    policy_name: str = Field(..., description="政策名称")
    match_score: float = Field(..., ge=0, le=1, description="匹配分数 (0-1)")
    support_type: SupportType = Field(..., description="支持类型")
    max_amount: Optional[float] = Field(None, description="最高支持金额")
    deadline: Optional[datetime] = Field(None, description="申请截止时间")
    matched_requirements: List[str] = Field(..., description="符合的要求")
    missing_requirements: List[str] = Field(..., description="不满足的要求")
    recommendation: str = Field(..., description="AI推荐建议")
    source_url: str = Field(..., description="政策原文链接")

class MatchRequest(BaseModel):
    """政策匹配请求模型"""
    company_profile: CompanyProfile
    top_k: int = Field(5, ge=1, le=20, description="返回top-k个匹配结果")
    min_score: float = Field(0.3, ge=0, le=1, description="最低匹配分数阈值")

class MatchResponse(BaseModel):
    """政策匹配响应模型"""
    matches: List[PolicyMatch] = Field(..., description="匹配的政策列表")
    total_policies: int = Field(..., description="总政策数量")
    processing_time: float = Field(..., description="处理时间（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class CrawlerTask(BaseModel):
    """爬虫任务模型"""
    task_id: str = Field(..., description="任务ID")
    source: str = Field(..., description="爬取来源")
    status: str = Field(..., description="任务状态")
    total_pages: int = Field(0, description="总页数")
    processed_pages: int = Field(0, description="已处理页数")
    new_policies: int = Field(0, description="新增政策数")
    updated_policies: int = Field(0, description="更新政策数")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    started_at: datetime = Field(default_factory=datetime.now, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

class CrawlerStatus(BaseModel):
    """爬虫状态响应模型"""
    is_running: bool = Field(..., description="是否正在运行")
    last_run: Optional[datetime] = Field(None, description="上次运行时间")
    next_run: Optional[datetime] = Field(None, description="下次运行时间")
    total_policies: int = Field(0, description="总政策数量")
    recent_tasks: List[CrawlerTask] = Field(default_factory=list, description="最近任务")

class APIResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间") 