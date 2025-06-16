from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import time
import logging
from typing import List

from ..models.schemas import (
    MatchRequest, MatchResponse, PolicyMatch, CompanyProfile,
    APIResponse
)
from ..services.policy_matcher import policy_matcher_service
from ..database import get_db, Company, MatchHistory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/match", response_model=MatchResponse)
async def match_policies(
    request: MatchRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    匹配政策
    
    根据企业画像信息，返回最匹配的政策列表
    """
    start_time = time.time()
    
    try:
        logger.info(f"开始为企业 {request.company_profile.company_name} 匹配政策")
        
        # 匹配政策
        matches = await policy_matcher_service.match_policies(
            company_profile=request.company_profile,
            top_k=request.top_k,
            min_score=request.min_score
        )
        
        # 获取总政策数量
        total_policies = await _get_total_policies_count(db)
        
        processing_time = time.time() - start_time
        
        # 异步保存匹配记录
        background_tasks.add_task(
            _save_match_history,
            request.company_profile,
            matches,
            db
        )
        
        response = MatchResponse(
            matches=matches,
            total_policies=total_policies,
            processing_time=processing_time
        )
        
        logger.info(f"政策匹配完成，返回 {len(matches)} 个结果，耗时 {processing_time:.2f}秒")
        return response
        
    except Exception as e:
        logger.error(f"政策匹配失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"政策匹配服务异常: {str(e)}"
        )

@router.post("/match/simple")
async def match_policies_simple(
    company_profile: CompanyProfile,
    top_k: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    简化的政策匹配接口
    
    直接传入企业信息，返回匹配结果
    """
    try:
        request = MatchRequest(
            company_profile=company_profile,
            top_k=top_k,
            min_score=0.3
        )
        
        matches = await policy_matcher_service.match_policies(
            company_profile=company_profile,
            top_k=top_k,
            min_score=0.3
        )
        
        return APIResponse(
            success=True,
            message=f"成功匹配到 {len(matches)} 个政策",
            data={
                "matches": matches,
                "count": len(matches)
            }
        )
        
    except Exception as e:
        logger.error(f"简化政策匹配失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"政策匹配失败: {str(e)}"
        )

@router.get("/policies/count")
async def get_policies_count(db: AsyncSession = Depends(get_db)):
    """获取政策总数"""
    try:
        total_count = await _get_total_policies_count(db)
        active_count = await _get_active_policies_count(db)
        
        return APIResponse(
            success=True,
            message="获取政策统计成功",
            data={
                "total_policies": total_count,
                "active_policies": active_count
            }
        )
        
    except Exception as e:
        logger.error(f"获取政策统计失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取政策统计失败: {str(e)}"
        )

@router.get("/match/history/{company_name}")
async def get_match_history(
    company_name: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """获取企业匹配历史"""
    try:
        # 查询企业
        stmt = select(Company).where(Company.company_name == company_name)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"未找到企业: {company_name}"
            )
        
        # 查询匹配历史
        stmt = (
            select(MatchHistory)
            .where(MatchHistory.company_id == company.id)
            .order_by(MatchHistory.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        history = result.scalars().all()
        
        return APIResponse(
            success=True,
            message=f"获取匹配历史成功",
            data={
                "company_name": company_name,
                "history": [
                    {
                        "policy_id": h.policy_id,
                        "match_score": h.match_score,
                        "matched_requirements": h.matched_requirements,
                        "missing_requirements": h.missing_requirements,
                        "recommendation": h.recommendation,
                        "created_at": h.created_at.isoformat()
                    }
                    for h in history
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取匹配历史失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取匹配历史失败: {str(e)}"
        )

async def _get_total_policies_count(db: AsyncSession) -> int:
    """获取政策总数"""
    from ..database import Policy
    stmt = select(Policy).where(Policy.is_active == True)
    result = await db.execute(stmt)
    policies = result.scalars().all()
    return len(policies)

async def _get_active_policies_count(db: AsyncSession) -> int:
    """获取活跃政策数"""
    from ..database import Policy
    from datetime import datetime
    
    stmt = select(Policy).where(
        Policy.is_active == True,
        (Policy.deadline.is_(None)) | (Policy.deadline > datetime.now())
    )
    result = await db.execute(stmt)
    policies = result.scalars().all()
    return len(policies)

async def _save_match_history(
    company_profile: CompanyProfile,
    matches: List[PolicyMatch],
    db: AsyncSession
):
    """保存匹配历史"""
    try:
        # 查找或创建企业记录
        stmt = select(Company).where(Company.company_name == company_profile.company_name)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()
        
        if not company:
            # 创建新的企业记录
            company_data = {
                "company_name": company_profile.company_name,
                "registration_location": company_profile.registration_location,
                "industry_match": company_profile.industry_match,
                "operating_status": company_profile.operating_status,
                "credit_status": company_profile.credit_status,
                "patents": company_profile.patents,
                "company_scale": company_profile.company_scale,
                "rd_investment": company_profile.rd_investment,
                "enterprise_certification": company_profile.enterprise_certification,
                "contact_phone": company_profile.contact_phone,
                "contact_email": company_profile.contact_email,
            }
            
            stmt = insert(Company).values(**company_data)
            result = await db.execute(stmt)
            await db.commit()
            
            # 重新查询获取ID
            stmt = select(Company).where(Company.company_name == company_profile.company_name)
            result = await db.execute(stmt)
            company = result.scalar_one()
        
        # 保存匹配历史
        for match in matches:
            history_data = {
                "company_id": company.id,
                "policy_id": match.policy_id,
                "match_score": match.match_score,
                "matched_requirements": match.matched_requirements,
                "missing_requirements": match.missing_requirements,
                "recommendation": match.recommendation,
            }
            
            stmt = insert(MatchHistory).values(**history_data)
            await db.execute(stmt)
        
        await db.commit()
        logger.info(f"保存匹配历史成功: {company_profile.company_name}, {len(matches)}条记录")
        
    except Exception as e:
        logger.error(f"保存匹配历史失败: {e}")
        await db.rollback() 