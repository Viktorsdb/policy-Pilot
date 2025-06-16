from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # 基本配置
    APP_NAME: str = "PolicyPilot"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/policypilot"
    
    # ChromaDB配置
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8000
    CHROMADB_COLLECTION: str = "policy_embeddings"
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY: str = "sk-e51ff57edcae48a2b5b462d9f8abcd49"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # BGE模型配置
    BGE_MODEL_NAME: str = "BAAI/bge-large-zh"
    BGE_MODEL_PATH: str = "./models/bge-large-zh"
    
    # Redis配置（用于Celery）
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # 爬虫配置
    CRAWLER_USER_AGENT: str = "PolicyPilot-Crawler/1.0"
    CRAWLER_DELAY: float = 1.0  # 请求间隔
    CRAWLER_TIMEOUT: int = 30
    
    # 政府网站URL
    XUHUI_GOV_URL: str = "https://www.xuhui.gov.cn"
    XUHUI_SCIENCE_URL: str = "https://kjw.xuhui.gov.cn"
    SHANGHAI_ECONOMIC_URL: str = "https://jxw.sh.gov.cn"
    
    # 文件存储配置
    UPLOAD_DIR: str = "./uploads"
    PDF_STORAGE_DIR: str = "./storage/pdfs"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局设置实例
settings = Settings()

# 创建必要的目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PDF_STORAGE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True) 