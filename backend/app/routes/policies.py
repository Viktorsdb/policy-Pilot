from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import logging

from ..models.schemas import APIResponse, PolicyInfo
from ..database import get_db, Policy

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/policies")
async def get_policies(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=100, description="每页数量"),
    region: Optional[str] = Query(None, description="地区筛选"),
    industry: Optional[str] = Query(None, description="行业筛选"),
    support_type: Optional[str] = Query(None, description="支持类型筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取政策列表
    支持分页和筛选
    """
    try:
        # 构建查询
        stmt = select(Policy).where(Policy.is_active == True)
        
        # 添加筛选条件
        if region:
            stmt = stmt.where(Policy.region.ilike(f"%{region}%"))
        
        if industry:
            stmt = stmt.where(Policy.industry_tags.op('?')(industry))
        
        if support_type:
            stmt = stmt.where(Policy.support_type == support_type)
        
        # 计算总数
        count_stmt = select(func.count()).select_from(stmt.alias())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar()
        
        # 分页查询
        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit).order_by(Policy.created_at.desc())
        
        result = await db.execute(stmt)
        policies = result.scalars().all()
        
        # 转换为响应格式
        policy_list = []
        for policy in policies:
            policy_dict = {
                "id": policy.id,
                "policy_name": policy.policy_name,
                "region": policy.region,
                "industry_tags": policy.industry_tags,
                "requirements": policy.requirements,
                "support_type": policy.support_type,
                "max_amount": policy.max_amount,
                "deadline": policy.deadline.isoformat() if policy.deadline else None,
                "source_url": policy.source_url,
                "created_at": policy.created_at.isoformat(),
                "updated_at": policy.updated_at.isoformat()
            }
            policy_list.append(policy_dict)
        
        return APIResponse(
            success=True,
            message=f"获取政策列表成功",
            data={
                "policies": policy_list,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        )
        
    except Exception as e:
        logger.error(f"获取政策列表失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取政策列表失败: {str(e)}"
        )

@router.get("/policies/{policy_id}")
async def get_policy_detail(
    policy_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取政策详情"""
    try:
        stmt = select(Policy).where(
            Policy.id == policy_id,
            Policy.is_active == True
        )
        result = await db.execute(stmt)
        policy = result.scalar_one_or_none()
        
        if not policy:
            raise HTTPException(
                status_code=404,
                detail=f"未找到政策: {policy_id}"
            )
        
        policy_detail = {
            "id": policy.id,
            "policy_name": policy.policy_name,
            "region": policy.region,
            "industry_tags": policy.industry_tags,
            "requirements": policy.requirements,
            "support_type": policy.support_type,
            "max_amount": policy.max_amount,
            "deadline": policy.deadline.isoformat() if policy.deadline else None,
            "content": policy.content,
            "source_url": policy.source_url,
            "pdf_url": policy.pdf_url,
            "created_at": policy.created_at.isoformat(),
            "updated_at": policy.updated_at.isoformat()
        }
        
        return APIResponse(
            success=True,
            message="获取政策详情成功",
            data=policy_detail
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取政策详情失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取政策详情失败: {str(e)}"
        )

@router.get("/policies/stats/summary")
async def get_policy_stats(db: AsyncSession = Depends(get_db)):
    """获取政策统计信息"""
    try:
        # 总政策数
        total_stmt = select(func.count()).select_from(Policy).where(Policy.is_active == True)
        total_result = await db.execute(total_stmt)
        total_count = total_result.scalar()
        
        # 按地区统计
        region_stmt = select(Policy.region, func.count().label('count')).where(
            Policy.is_active == True
        ).group_by(Policy.region)
        region_result = await db.execute(region_stmt)
        region_stats = {row.region: row.count for row in region_result}
        
        # 按支持类型统计
        support_stmt = select(Policy.support_type, func.count().label('count')).where(
            Policy.is_active == True
        ).group_by(Policy.support_type)
        support_result = await db.execute(support_stmt)
        support_stats = {row.support_type: row.count for row in support_result}
        
        return APIResponse(
            success=True,
            message="获取政策统计信息成功",
            data={
                "total_policies": total_count,
                "by_region": region_stats,
                "by_support_type": support_stats,
            }
        )
        
    except Exception as e:
        logger.error(f"获取政策统计失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取政策统计失败: {str(e)}"
        ) 