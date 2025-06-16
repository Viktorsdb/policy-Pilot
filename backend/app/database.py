from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import asyncio

from .config import settings

# 创建基础模型类
Base = declarative_base()

class Policy(Base):
    """政策信息表"""
    __tablename__ = "policies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_name = Column(String, nullable=False, index=True)
    region = Column(String, nullable=False, index=True)
    industry_tags = Column(JSON, nullable=False)  # 存储标签列表
    requirements = Column(JSON, nullable=False)   # 存储要求列表
    support_type = Column(String, nullable=False, index=True)
    max_amount = Column(Float, nullable=True)
    deadline = Column(DateTime, nullable=True)
    content = Column(Text, nullable=False)
    source_url = Column(String, nullable=False)
    pdf_url = Column(String, nullable=True)
    embedding_id = Column(String, nullable=True)  # ChromaDB中的向量ID
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)

class CrawlerTask(Base):
    """爬虫任务表"""
    __tablename__ = "crawler_tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, nullable=False, unique=True, index=True)
    source = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, running, completed, failed
    total_pages = Column(Integer, default=0)
    processed_pages = Column(Integer, default=0)
    new_policies = Column(Integer, default=0)
    updated_policies = Column(Integer, default=0)
    errors = Column(JSON, default=list)
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)

class Company(Base):
    """企业信息表"""
    __tablename__ = "companies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String, nullable=False, index=True)
    registration_location = Column(String, nullable=False)
    industry_match = Column(String, nullable=False)
    operating_status = Column(String, nullable=False)
    credit_status = Column(String, nullable=False)
    patents = Column(Integer, default=0)
    company_scale = Column(String, nullable=False)
    rd_investment = Column(String, nullable=False)
    enterprise_certification = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class MatchHistory(Base):
    """匹配历史表"""
    __tablename__ = "match_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, nullable=False, index=True)
    policy_id = Column(String, nullable=False, index=True)
    match_score = Column(Float, nullable=False)
    matched_requirements = Column(JSON, nullable=False)
    missing_requirements = Column(JSON, nullable=False)
    recommendation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# 创建数据库引擎
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)

# 创建会话
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 同步数据库引擎（用于Celery任务）
sync_engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

def get_sync_db():
    """获取同步数据库会话"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close() 