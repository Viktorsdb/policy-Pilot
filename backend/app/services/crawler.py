import asyncio
import logging
import re
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import PyPDF2
import pdfplumber
from io import BytesIO

from ..config import settings
from ..database import get_sync_db, Policy, CrawlerTask
from ..services.embedding import embedding_service
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update

logger = logging.getLogger(__name__)

class PolicyCrawler:
    """政策爬虫服务"""
    
    def __init__(self):
        self.session = None
        self.browser = None
        self.page = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.CRAWLER_TIMEOUT),
            headers={'User-Agent': settings.CRAWLER_USER_AGENT}
        )
        
        # 初始化Playwright浏览器
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def crawl_all_sources(self) -> Dict[str, any]:
        """爬取所有政府网站"""
        results = {
            'total_new': 0,
            'total_updated': 0,
            'sources': {}
        }
        
        sources = [
            ('xuhui_gov', settings.XUHUI_GOV_URL, self._crawl_xuhui_gov),
            ('xuhui_science', settings.XUHUI_SCIENCE_URL, self._crawl_xuhui_science),
            ('shanghai_economic', settings.SHANGHAI_ECONOMIC_URL, self._crawl_shanghai_economic)
        ]
        
        for source_name, base_url, crawler_func in sources:
            try:
                logger.info(f"开始爬取 {source_name}")
                task_id = str(uuid.uuid4())
                
                # 创建爬虫任务记录
                await self._create_crawler_task(task_id, source_name)
                
                result = await crawler_func(base_url, task_id)
                results['sources'][source_name] = result
                results['total_new'] += result.get('new_policies', 0)
                results['total_updated'] += result.get('updated_policies', 0)
                
                # 更新任务状态
                await self._update_crawler_task(task_id, 'completed', result)
                
                logger.info(f"{source_name} 爬取完成: 新增{result.get('new_policies', 0)}, 更新{result.get('updated_policies', 0)}")
                
                # 请求间隔
                await asyncio.sleep(settings.CRAWLER_DELAY)
                
            except Exception as e:
                logger.error(f"爬取 {source_name} 失败: {e}")
                await self._update_crawler_task(task_id, 'failed', {'error': str(e)})
                results['sources'][source_name] = {'error': str(e)}
        
        return results
    
    async def _crawl_xuhui_gov(self, base_url: str, task_id: str) -> Dict[str, any]:
        """爬取徐汇区政府网站"""
        result = {
            'new_policies': 0,
            'updated_policies': 0,
            'processed_pages': 0,
            'errors': []
        }
        
        try:
            # 政策公告页面URL
            policy_urls = [
                '/zwgk/gkml/zcfg/',  # 政策法规
                '/zwgk/gkml/zcjd/',  # 政策解读
                '/zfxxgk/fdzdgknr/qtzsxzqzfxxgk/zcfgxzfgfxtwj/',  # 其他政策
            ]
            
            for policy_url in policy_urls:
                full_url = urljoin(base_url, policy_url)
                policies = await self._parse_policy_list_page(full_url, '徐汇区政府')
                
                for policy in policies:
                    try:
                        saved = await self._save_policy(policy)
                        if saved == 'new':
                            result['new_policies'] += 1
                        elif saved == 'updated':
                            result['updated_policies'] += 1
                    except Exception as e:
                        result['errors'].append(f"保存政策失败: {e}")
                
                result['processed_pages'] += 1
                await asyncio.sleep(1)  # 避免过于频繁的请求
                
        except Exception as e:
            logger.error(f"爬取徐汇区政府网站失败: {e}")
            result['errors'].append(str(e))
        
        return result
    
    async def _crawl_xuhui_science(self, base_url: str, task_id: str) -> Dict[str, any]:
        """爬取徐汇科委网站"""
        result = {
            'new_policies': 0,
            'updated_policies': 0,
            'processed_pages': 0,
            'errors': []
        }
        
        try:
            # 科技政策页面
            policy_urls = [
                '/zwgk/zcfg/',  # 政策法规
                '/zwgk/tzgg/',  # 通知公告
            ]
            
            for policy_url in policy_urls:
                full_url = urljoin(base_url, policy_url)
                policies = await self._parse_policy_list_page(full_url, '徐汇科委')
                
                for policy in policies:
                    try:
                        saved = await self._save_policy(policy)
                        if saved == 'new':
                            result['new_policies'] += 1
                        elif saved == 'updated':
                            result['updated_policies'] += 1
                    except Exception as e:
                        result['errors'].append(f"保存政策失败: {e}")
                
                result['processed_pages'] += 1
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"爬取徐汇科委网站失败: {e}")
            result['errors'].append(str(e))
        
        return result
    
    async def _crawl_shanghai_economic(self, base_url: str, task_id: str) -> Dict[str, any]:
        """爬取上海市经信委网站"""
        result = {
            'new_policies': 0,
            'updated_policies': 0,
            'processed_pages': 0,
            'errors': []
        }
        
        try:
            # 经信委政策页面
            policy_urls = [
                '/zwgk/fgbz/',  # 法规标准
                '/zwgk/zcfb/',  # 政策发布
            ]
            
            for policy_url in policy_urls:
                full_url = urljoin(base_url, policy_url)
                policies = await self._parse_policy_list_page(full_url, '上海市经信委')
                
                for policy in policies:
                    try:
                        saved = await self._save_policy(policy)
                        if saved == 'new':
                            result['new_policies'] += 1
                        elif saved == 'updated':
                            result['updated_policies'] += 1
                    except Exception as e:
                        result['errors'].append(f"保存政策失败: {e}")
                
                result['processed_pages'] += 1
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"爬取上海市经信委网站失败: {e}")
            result['errors'].append(str(e))
        
        return result
    
    async def _parse_policy_list_page(self, url: str, source: str) -> List[Dict]:
        """解析政策列表页面"""
        policies = []
        
        try:
            # 使用Playwright加载页面
            await self.page.goto(url, wait_until='networkidle')
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找政策链接（根据实际网站结构调整选择器）
            policy_links = soup.find_all('a', href=True)
            
            for link in policy_links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # 过滤有效的政策链接
                if self._is_valid_policy_link(href, title):
                    full_url = urljoin(url, href)
                    
                    # 解析具体政策页面
                    policy = await self._parse_policy_detail(full_url, title, source)
                    if policy:
                        policies.append(policy)
                    
                    # 限制数量，避免过度爬取
                    if len(policies) >= 20:
                        break
                        
        except Exception as e:
            logger.error(f"解析政策列表页面失败 {url}: {e}")
        
        return policies
    
    def _is_valid_policy_link(self, href: str, title: str) -> bool:
        """判断是否为有效的政策链接"""
        if not href or not title:
            return False
        
        # 过滤条件
        invalid_keywords = ['javascript:', 'mailto:', '#', 'tel:']
        if any(keyword in href.lower() for keyword in invalid_keywords):
            return False
        
        # 包含政策相关关键词
        policy_keywords = ['政策', '办法', '规定', '通知', '公告', '意见', '方案', '补贴', '扶持', '资助']
        if any(keyword in title for keyword in policy_keywords):
            return True
        
        return False
    
    async def _parse_policy_detail(self, url: str, title: str, source: str) -> Optional[Dict]:
        """解析政策详情页面"""
        try:
            await self.page.goto(url, wait_until='networkidle')
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # 提取政策内容
            content_text = self._extract_content_text(soup)
            if not content_text or len(content_text) < 100:
                return None
            
            # 提取PDF链接
            pdf_links = self._extract_pdf_links(soup, url)
            
            # 解析政策信息
            policy_info = self._parse_policy_content(title, content_text)
            
            return {
                'policy_name': title,
                'region': self._determine_region(source),
                'industry_tags': policy_info.get('industry_tags', []),
                'requirements': policy_info.get('requirements', []),
                'support_type': policy_info.get('support_type', 'other'),
                'max_amount': policy_info.get('max_amount'),
                'deadline': policy_info.get('deadline'),
                'content': content_text,
                'source_url': url,
                'pdf_url': pdf_links[0] if pdf_links else None,
            }
            
        except Exception as e:
            logger.error(f"解析政策详情失败 {url}: {e}")
            return None
    
    def _extract_content_text(self, soup: BeautifulSoup) -> str:
        """提取页面文本内容"""
        # 查找主要内容区域
        content_selectors = [
            '.content', '.main-content', '.article-content',
            '#content', '#main', '.text-content',
            '.policy-content', '.detail-content'
        ]
        
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        if not content:
            content = soup.find('body')
        
        if content:
            # 移除不需要的元素
            for tag in content.find_all(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            
            return content.get_text(strip=True)
        
        return ""
    
    def _extract_pdf_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """提取PDF链接"""
        pdf_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.lower().endswith('.pdf'):
                full_url = urljoin(base_url, href)
                pdf_links.append(full_url)
        
        return pdf_links
    
    def _parse_policy_content(self, title: str, content: str) -> Dict:
        """解析政策内容，提取结构化信息"""
        info = {
            'industry_tags': [],
            'requirements': [],
            'support_type': 'other',
            'max_amount': None,
            'deadline': None
        }
        
        # 提取产业标签
        industry_keywords = {
            'AI': ['人工智能', 'AI', '机器学习', '深度学习'],
            '科技': ['科技', '技术', '创新', '研发'],
            '制造': ['制造', '生产', '工业', '智能制造'],
            '服务': ['服务', '商业', '贸易'],
            '金融': ['金融', '投资', 'FinTech'],
            '医疗': ['医疗', '健康', '生物医药'],
        }
        
        for tag, keywords in industry_keywords.items():
            if any(keyword in content or keyword in title for keyword in keywords):
                info['industry_tags'].append(tag)
        
        # 提取支持类型
        if any(keyword in content for keyword in ['无偿资助', '资助', '补助']):
            info['support_type'] = 'grant'
        elif any(keyword in content for keyword in ['贷款', '贴息']):
            info['support_type'] = 'loan'
        elif any(keyword in content for keyword in ['税收', '减税', '免税']):
            info['support_type'] = 'tax'
        elif any(keyword in content for keyword in ['补贴']):
            info['support_type'] = 'subsidy'
        
        # 提取金额信息
        amount_pattern = r'(\d+(?:\.\d+)?)\s*万元|(\d+(?:\.\d+)?)\s*亿元'
        amounts = re.findall(amount_pattern, content)
        if amounts:
            max_amount = 0
            for wan, yi in amounts:
                if wan:
                    amount = float(wan) * 10000
                elif yi:
                    amount = float(yi) * 100000000
                max_amount = max(max_amount, amount)
            info['max_amount'] = max_amount
        
        # 提取申请要求
        req_patterns = [
            r'申请条件[：:](.*?)(?=\n\n|\n[一二三四五六七八九十])',
            r'申请要求[：:](.*?)(?=\n\n|\n[一二三四五六七八九十])',
            r'条件[：:](.*?)(?=\n\n|\n[一二三四五六七八九十])',
        ]
        
        for pattern in req_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                requirements = [req.strip() for req in match.split('\n') if req.strip()]
                info['requirements'].extend(requirements[:5])  # 限制数量
                break
        
        # 提取截止时间
        date_patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{1,2}-\d{1,2})',
            r'(\d{1,2}月\d{1,2}日前)',
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, content)
            if dates:
                # 这里简化处理，实际应该解析具体日期
                info['deadline'] = dates[0]
                break
        
        return info
    
    def _determine_region(self, source: str) -> str:
        """根据来源确定地区"""
        region_map = {
            '徐汇区政府': '徐汇区',
            '徐汇科委': '徐汇区',
            '上海市经信委': '上海市'
        }
        return region_map.get(source, '未知')
    
    async def _save_policy(self, policy_data: Dict) -> str:
        """保存政策到数据库"""
        try:
            with next(get_sync_db()) as db:
                # 检查是否已存在
                existing = db.query(Policy).filter(
                    Policy.policy_name == policy_data['policy_name'],
                    Policy.source_url == policy_data['source_url']
                ).first()
                
                if existing:
                    # 更新现有记录
                    for key, value in policy_data.items():
                        setattr(existing, key, value)
                    existing.updated_at = datetime.now()
                    db.commit()
                    
                    # 重新生成向量
                    if hasattr(embedding_service, 'update_policy_embedding'):
                        await embedding_service.update_policy_embedding(existing.id, policy_data['content'])
                    
                    return 'updated'
                else:
                    # 创建新记录
                    policy = Policy(**policy_data)
                    db.add(policy)
                    db.commit()
                    db.refresh(policy)
                    
                    # 生成向量
                    if hasattr(embedding_service, 'create_policy_embedding'):
                        await embedding_service.create_policy_embedding(policy.id, policy_data['content'])
                    
                    return 'new'
                    
        except Exception as e:
            logger.error(f"保存政策失败: {e}")
            raise
    
    async def _create_crawler_task(self, task_id: str, source: str):
        """创建爬虫任务记录"""
        try:
            with next(get_sync_db()) as db:
                task = CrawlerTask(
                    task_id=task_id,
                    source=source,
                    status='running'
                )
                db.add(task)
                db.commit()
        except Exception as e:
            logger.error(f"创建爬虫任务失败: {e}")
    
    async def _update_crawler_task(self, task_id: str, status: str, result: Dict):
        """更新爬虫任务状态"""
        try:
            with next(get_sync_db()) as db:
                task = db.query(CrawlerTask).filter(CrawlerTask.task_id == task_id).first()
                if task:
                    task.status = status
                    task.completed_at = datetime.now()
                    task.new_policies = result.get('new_policies', 0)
                    task.updated_policies = result.get('updated_policies', 0)
                    task.processed_pages = result.get('processed_pages', 0)
                    task.errors = result.get('errors', [])
                    db.commit()
        except Exception as e:
            logger.error(f"更新爬虫任务失败: {e}")

# 创建全局爬虫实例
crawler_service = PolicyCrawler() 