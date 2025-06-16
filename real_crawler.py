#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin
import os

class RealPolicyCrawler:
    """基于真实链接的政策爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 真实政策链接列表
        self.policy_urls = [
            {
                "url": "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab01934dd52e3d09b9",
                "title": "徐汇区关于推动人工智能产业高质量发展的若干意见",
                "category": "ai_development",
                "region": "徐汇区"
            },
            {
                "url": "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab01934dd6cfbd09bb", 
                "title": "徐汇区关于推动具身智能产业发展的若干意见",
                "category": "embodied_ai",
                "region": "徐汇区"
            },
            {
                "url": "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab019384dc95a70aed",
                "title": "关于支持上海市生成式人工智能创新生态先导区的若干措施",
                "category": "generative_ai",
                "region": "徐汇区"
            },
            {
                "url": "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab0192e1617de30643",
                "title": "徐汇区关于支持西岸人工智能大模型科创街区的扶持意见",
                "category": "ai_model_district",
                "region": "徐汇区"
            },
            {
                "url": "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0696c75c4d0195d6c9b66e0051",
                "title": "保障性安居工程专项补助资金分配结果",
                "category": "housing_subsidy",
                "region": "徐汇区"
            },
            {
                "url": "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab019361d266e109fc",
                "title": "徐汇区新型工业化发展专项资金管理办法",
                "category": "industrial_development",
                "region": "徐汇区"
            },
            {
                "url": "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c06920eedbe0192235ebcb3003e",
                "title": "2024年徐汇区小微企业贴息贴费审核通过名单",
                "category": "sme_subsidy",
                "region": "徐汇区"
            }
        ]
        
    def crawl_policy_content(self, url: str) -> Optional[Dict]:
        """爬取单个政策页面内容"""
        try:
            print(f"🔍 正在爬取: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = self.extract_title(soup)
            
            # 提取正文内容
            content = self.extract_content(soup)
            
            # 提取发布时间
            publish_date = self.extract_publish_date(soup)
            
            # 提取来源部门
            department = self.extract_department(soup)
            
            # 分析政策类型和支持金额
            policy_type, max_amount = self.analyze_policy_type(content)
            
            # 提取申请条件
            requirements = self.extract_requirements(content)
            
            # 提取行业标签
            industry_tags = self.extract_industry_tags(title, content)
            
            return {
                "url": url,
                "title": title,
                "content": content,
                "publish_date": publish_date,
                "department": department,
                "policy_type": policy_type,
                "max_amount": max_amount,
                "requirements": requirements,
                "industry_tags": industry_tags,
                "crawl_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 爬取失败 {url}: {str(e)}")
            return None
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """提取页面标题"""
        # 尝试多种标题选择器
        selectors = [
            'h1.article-title',
            'h1',
            '.article-header h1',
            '.content-title h1',
            'title'
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                title = title_elem.get_text().strip()
                # 清理标题
                if '|' in title:
                    title = title.split('|')[0].strip()
                if '-' in title and len(title.split('-')) > 1:
                    title = title.split('-')[0].strip()
                return title
        
        return "未知政策标题"
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """提取页面正文内容"""
        # 尝试多种内容选择器
        selectors = [
            '.article-content',
            '.content-main',
            '.policy-content',
            '.article-body',
            '#article-content',
            '.text-content'
        ]
        
        for selector in selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 移除脚本和样式标签
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                content = content_elem.get_text()
                # 清理文本
                content = re.sub(r'\s+', ' ', content).strip()
                if len(content) > 100:  # 确保内容有意义
                    return content
        
        # 如果专用选择器失败，尝试获取整个页面文本
        full_text = soup.get_text()
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        return full_text[:2000] if full_text else "无法提取内容"
    
    def extract_publish_date(self, soup: BeautifulSoup) -> str:
        """提取发布时间"""
        # 尝试多种时间选择器
        selectors = [
            '.publish-date',
            '.article-date',
            '.date',
            '.time',
            '[class*="date"]',
            '[class*="time"]'
        ]
        
        for selector in selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text().strip()
                # 提取日期格式
                date_match = re.search(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})', date_text)
                if date_match:
                    return date_match.group(1).replace('/', '-').replace('.', '-')
        
        # 在页面文本中搜索日期
        page_text = soup.get_text()
        date_match = re.search(r'(\d{4}[-./]\d{1,2}[-./]\d{1,2})', page_text)
        if date_match:
            return date_match.group(1).replace('/', '-').replace('.', '-')
        
        return "2024-01-01"  # 默认日期
    
    def extract_department(self, soup: BeautifulSoup) -> str:
        """提取发布部门"""
        # 在页面文本中搜索部门信息
        page_text = soup.get_text()
        
        # 常见部门名称模式
        dept_patterns = [
            r'(徐汇区[^，。]+?委员会)',
            r'(徐汇区[^，。]+?局)',
            r'(徐汇区[^，。]+?办)',
            r'(上海市[^，。]+?委员会)',
            r'(上海市[^，。]+?局)'
        ]
        
        for pattern in dept_patterns:
            match = re.search(pattern, page_text)
            if match:
                return match.group(1)
        
        # 如果在徐汇区网站，默认返回徐汇区政府
        if 'xuhui.gov.cn' in soup.find('base', href=True).get('href', '') if soup.find('base', href=True) else '':
            return "徐汇区人民政府"
        
        return "徐汇区相关部门"
    
    def analyze_policy_type(self, content: str) -> tuple:
        """分析政策类型和最大支持金额"""
        content_lower = content.lower()
        
        # 支持类型判断
        if any(word in content for word in ['补贴', '资助', '奖励', '扶持资金']):
            if any(word in content for word in ['无偿', '不予返还']):
                policy_type = 'grant'
            else:
                policy_type = 'subsidy'
        elif any(word in content for word in ['税收优惠', '减税', '免税']):
            policy_type = 'tax'
        elif any(word in content for word in ['贷款', '融资', '担保']):
            policy_type = 'loan'
        elif any(word in content for word in ['投资', '股权', '基金']):
            policy_type = 'investment'
        else:
            policy_type = 'subsidy'
        
        # 提取金额
        amount_patterns = [
            r'最高[不]?超过?(\d+)万元',
            r'不超过(\d+)万元',
            r'给予(\d+)万元',
            r'资助(\d+)万元',
            r'补贴(\d+)万元',
            r'奖励(\d+)万元'
        ]
        
        max_amount = 1000000  # 默认100万
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, content)
            if matches:
                try:
                    amount_wan = int(matches[0])
                    max_amount = amount_wan * 10000
                    break
                except:
                    continue
        
        return policy_type, max_amount
    
    def extract_requirements(self, content: str) -> List[str]:
        """提取申请条件"""
        requirements = []
        
        # 寻找条件相关段落
        condition_patterns = [
            r'申请条件[：:](.*?)(?=[。\n]|$)',
            r'支持对象[：:](.*?)(?=[。\n]|$)',
            r'适用范围[：:](.*?)(?=[。\n]|$)',
            r'支持条件[：:](.*?)(?=[。\n]|$)'
        ]
        
        for pattern in condition_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                # 分割条件
                conditions = re.split(r'[；;，,]', match)
                for condition in conditions:
                    condition = condition.strip()
                    if len(condition) > 10:  # 过滤太短的条件
                        requirements.append(condition)
        
        # 如果没有找到具体条件，添加通用条件
        if not requirements:
            if '徐汇区' in content:
                requirements.append('企业注册地在徐汇区')
            if '人工智能' in content:
                requirements.append('从事人工智能相关业务')
            requirements.append('企业信用状况良好')
            requirements.append('符合国家产业政策')
        
        return requirements[:6]  # 最多返回6个条件
    
    def extract_industry_tags(self, title: str, content: str) -> List[str]:
        """提取行业标签"""
        tags = []
        text = title + ' ' + content
        
        # 行业关键词映射
        industry_keywords = {
            '人工智能': ['人工智能', 'AI', '智能', '算法', '大模型'],
            '科技创新': ['科技', '创新', '研发', '技术'],
            '制造业': ['制造', '工业', '生产'],
            '数字经济': ['数字化', '信息化', '互联网'],
            '生物医药': ['生物', '医药', '医疗'],
            '新能源': ['新能源', '清洁能源', '节能'],
            '金融科技': ['金融科技', 'fintech', '支付'],
            '文创产业': ['文化', '创意', '设计'],
            '小微企业': ['小微企业', '中小企业'],
            '住房保障': ['住房', '保障房', '安居']
        }
        
        for tag, keywords in industry_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        
        return tags[:5]  # 最多返回5个标签
    
    def crawl_all_policies(self) -> List[Dict]:
        """爬取所有政策"""
        print("🚀 开始爬取真实政策数据...")
        policies = []
        
        for i, policy_info in enumerate(self.policy_urls):
            print(f"📄 [{i+1}/{len(self.policy_urls)}] {policy_info['title']}")
            
            policy_data = self.crawl_policy_content(policy_info['url'])
            if policy_data:
                # 合并基础信息
                policy_data.update({
                    'policy_id': f"XH2024{i+1:03d}",
                    'region': policy_info['region'],
                    'category': policy_info['category']
                })
                policies.append(policy_data)
                print(f"✅ 成功爬取: {policy_data['title']}")
            else:
                print(f"❌ 失败: {policy_info['title']}")
            
            # 延时避免被封
            time.sleep(2)
        
        print(f"🎉 爬取完成！共获取 {len(policies)} 条政策")
        return policies
    
    def save_policies(self, policies: List[Dict], filename: str = "real_policies.json"):
        """保存政策数据"""
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(policies, f, ensure_ascii=False, indent=2)
        
        print(f"💾 政策数据已保存到: {filepath}")

def main():
    """主函数"""
    crawler = RealPolicyCrawler()
    
    # 爬取所有政策
    policies = crawler.crawl_all_policies()
    
    # 保存数据
    crawler.save_policies(policies)
    
    # 显示统计信息
    print("\n📊 爬取统计:")
    print(f"  总政策数: {len(policies)}")
    print(f"  AI相关政策: {len([p for p in policies if '人工智能' in p.get('title', '')])}")
    print(f"  资金类政策: {len([p for p in policies if any(word in p.get('title', '') for word in ['资金', '补贴', '奖励'])])}")
    
    return policies

if __name__ == "__main__":
    main() 