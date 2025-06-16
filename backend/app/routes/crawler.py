from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging
from datetime import datetime

from ..models.schemas import APIResponse, CrawlerStatus
from ..services.crawler import crawler_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/crawler/start")
async def start_crawler(background_tasks: BackgroundTasks):
    """启动爬虫任务"""
    try:
        logger.info("手动启动爬虫任务")
        
        # 在后台启动爬虫
        background_tasks.add_task(run_crawler_task)
        
        return APIResponse(
            success=True,
            message="爬虫任务已启动，正在后台运行",
            data={"task_started": True}
        )
        
    except Exception as e:
        logger.error(f"启动爬虫失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"启动爬虫失败: {str(e)}"
        )

@router.get("/crawler/status")
async def get_crawler_status():
    """获取爬虫状态"""
    try:
        # 这里应该从数据库查询实际状态
        # 简化实现，返回模拟状态
        status = CrawlerStatus(
            is_running=False,
            last_run=datetime.now(),
            next_run=None,
            total_policies=150,
            recent_tasks=[]
        )
        
        return APIResponse(
            success=True,
            message="获取爬虫状态成功",
            data=status.dict()
        )
        
    except Exception as e:
        logger.error(f"获取爬虫状态失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取爬虫状态失败: {str(e)}"
        )

async def run_crawler_task():
    """运行爬虫任务"""
    try:
        async with crawler_service as crawler:
            result = await crawler.crawl_all_sources()
            logger.info(f"爬虫任务完成: 新增{result['total_new']}, 更新{result['total_updated']}")
            return result
    except Exception as e:
        logger.error(f"爬虫任务执行失败: {e}")
        raise 