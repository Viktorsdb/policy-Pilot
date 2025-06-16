import asyncio
import time
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings
import httpx
import json
import logging
from sentence_transformers import SentenceTransformer

from ..models.schemas import CompanyProfile, PolicyMatch, PolicyInfo
from ..database import get_db, Policy
from ..config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

class PolicyMatcherService:
    """政策匹配服务"""
    
    def __init__(self):
        # 初始化ChromaDB
        self.chroma_client = chromadb.Client(ChromaSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chromadb"
        ))
        
        # 获取或创建集合
        try:
            self.collection = self.chroma_client.get_collection(
                name=settings.CHROMADB_COLLECTION
            )
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name=settings.CHROMADB_COLLECTION,
                metadata={"hnsw:space": "cosine"}
            )
        
        # 初始化BGE模型
        try:
            self.embedding_model = SentenceTransformer(settings.BGE_MODEL_NAME)
        except Exception as e:
            logger.warning(f"无法加载BGE模型: {e}")
            self.embedding_model = None
    
    async def match_policies(
        self, 
        company_profile: CompanyProfile, 
        top_k: int = 5,
        min_score: float = 0.3
    ) -> List[PolicyMatch]:
        """匹配政策"""
        start_time = time.time()
        
        try:
            # 1. 生成企业画像描述
            company_description = self._generate_company_description(company_profile)
            
            # 2. 向量搜索相似政策
            similar_policies = await self._vector_search(company_description, top_k * 2)
            
            # 3. 获取政策详细信息
            policy_details = await self._get_policy_details(similar_policies)
            
            # 4. AI分析匹配度
            matches = await self._analyze_matches(company_profile, policy_details)
            
            # 5. 过滤和排序
            filtered_matches = [m for m in matches if m.match_score >= min_score]
            filtered_matches.sort(key=lambda x: x.match_score, reverse=True)
            
            processing_time = time.time() - start_time
            logger.info(f"政策匹配完成，耗时: {processing_time:.2f}秒，返回{len(filtered_matches[:top_k])}个结果")
            
            return filtered_matches[:top_k]
            
        except Exception as e:
            logger.error(f"政策匹配失败: {e}")
            raise
    
    def _generate_company_description(self, profile: CompanyProfile) -> str:
        """生成企业画像描述"""
        description_parts = [
            f"企业名称：{profile.company_name}",
            f"注册地：{profile.registration_location}",
            f"产业类型：{profile.industry_match}",
            f"企业规模：{profile.company_scale}",
            f"研发投入占比：{profile.rd_investment}",
        ]
        
        if profile.patents and profile.patents > 0:
            description_parts.append(f"拥有专利数量：{profile.patents}项")
        
        if profile.enterprise_certification:
            description_parts.append(f"企业认定：{profile.enterprise_certification}")
        
        return "；".join(description_parts)
    
    async def _vector_search(self, query: str, top_k: int) -> List[Dict]:
        """向量搜索"""
        try:
            if not self.embedding_model:
                logger.warning("BGE模型未加载，使用基础搜索")
                return []
            
            # 生成查询向量
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # 在ChromaDB中搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["metadatas", "distances"]
            )
            
            # 转换结果格式
            similar_policies = []
            if results['ids'] and results['ids'][0]:
                for i, policy_id in enumerate(results['ids'][0]):
                    similarity = 1 - results['distances'][0][i]  # 转换为相似度
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    
                    similar_policies.append({
                        'policy_id': policy_id,
                        'similarity': similarity,
                        'metadata': metadata
                    })
            
            return similar_policies
            
        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return []
    
    async def _get_policy_details(self, similar_policies: List[Dict]) -> List[Policy]:
        """获取政策详细信息"""
        if not similar_policies:
            return []
        
        policy_ids = [p['policy_id'] for p in similar_policies]
        
        async with AsyncSession(bind=get_db()) as session:
            stmt = select(Policy).where(
                Policy.id.in_(policy_ids),
                Policy.is_active == True
            )
            result = await session.execute(stmt)
            policies = result.scalars().all()
            
            # 添加相似度信息
            similarity_map = {p['policy_id']: p['similarity'] for p in similar_policies}
            for policy in policies:
                policy.similarity = similarity_map.get(policy.id, 0.0)
            
            return list(policies)
    
    async def _analyze_matches(
        self, 
        company_profile: CompanyProfile, 
        policies: List[Policy]
    ) -> List[PolicyMatch]:
        """AI分析匹配度"""
        matches = []
        
        for policy in policies:
            try:
                # 调用DeepSeek API分析匹配度
                analysis = await self._call_deepseek_api(company_profile, policy)
                
                if analysis:
                    match = PolicyMatch(
                        policy_id=policy.id,
                        policy_name=policy.policy_name,
                        match_score=analysis.get('match_score', 0.0),
                        support_type=policy.support_type,
                        max_amount=policy.max_amount,
                        deadline=policy.deadline,
                        matched_requirements=analysis.get('matched_requirements', []),
                        missing_requirements=analysis.get('missing_requirements', []),
                        recommendation=analysis.get('recommendation', ''),
                        source_url=policy.source_url
                    )
                    matches.append(match)
                    
            except Exception as e:
                logger.error(f"分析政策{policy.id}失败: {e}")
                continue
        
        return matches
    
    async def _call_deepseek_api(
        self, 
        company_profile: CompanyProfile, 
        policy: Policy
    ) -> Dict[str, Any]:
        """调用DeepSeek API分析"""
        try:
            # 构建分析提示
            prompt = self._build_analysis_prompt(company_profile, policy)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.DEEPSEEK_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": "你是一个专业的政策分析师，擅长分析企业与政策的匹配度。请严格按照JSON格式返回分析结果。"
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # 解析JSON响应
                    try:
                        analysis = json.loads(content)
                        return analysis
                    except json.JSONDecodeError:
                        logger.error(f"DeepSeek返回非JSON格式: {content}")
                        return self._fallback_analysis(company_profile, policy)
                else:
                    logger.error(f"DeepSeek API错误: {response.status_code}")
                    return self._fallback_analysis(company_profile, policy)
                    
        except Exception as e:
            logger.error(f"调用DeepSeek API失败: {e}")
            return self._fallback_analysis(company_profile, policy)
    
    def _build_analysis_prompt(self, company_profile: CompanyProfile, policy: Policy) -> str:
        """构建分析提示"""
        # 格式化发布时间
        publish_date = getattr(policy, 'publish_date', None) or getattr(policy, 'publish_time', None) or getattr(policy, 'created_at', None)
        formatted_publish_date = str(publish_date) if publish_date else '未知时间'
        
        return f"""
请分析以下企业与政策的匹配度：

**企业信息：**
- 企业名称：{company_profile.company_name}
- 注册地：{company_profile.registration_location}
- 产业类型：{company_profile.industry_match}
- 企业规模：{company_profile.company_scale}
- 研发投入占比：{company_profile.rd_investment}
- 专利数量：{company_profile.patents}
- 企业认定：{company_profile.enterprise_certification or '无'}
- 经营状态：{company_profile.operating_status}
- 信用状态：{company_profile.credit_status}

**政策信息：**
- 政策名称：{policy.policy_name}
- 适用地区：{policy.region}
- 产业标签：{policy.industry_tags}
- 申请要求：{policy.requirements}
- 支持类型：{policy.support_type}
- 最高金额：{policy.max_amount or '未限定'}
- 发布时间：{formatted_publish_date}

请返回JSON格式的分析结果，包含以下字段：
{{
    "match_score": 0.85,  // 匹配分数，0-1之间的浮点数
    "matched_requirements": ["满足的要求1", "满足的要求2"],  // 企业满足的政策要求
    "missing_requirements": ["不满足的要求1"],  // 企业不满足的政策要求
    "recommendation": "具体的申请建议和改进方向"  // AI推荐建议
}}

分析要点：
1. 根据企业的产业类型、规模、研发投入等与政策要求的匹配程度评分
2. 详细列出企业满足和不满足的具体要求
3. 提供实用的申请建议和改进建议
"""
    
    def _fallback_analysis(self, company_profile: CompanyProfile, policy: Policy) -> Dict[str, Any]:
        """备用分析方法"""
        # 基础匹配逻辑
        score = 0.5  # 基础分数
        matched_reqs = []
        missing_reqs = []
        
        # 地区匹配
        if company_profile.registration_location == "xuhui" and "徐汇" in policy.region:
            score += 0.2
            matched_reqs.append("注册地符合要求")
        
        # 产业匹配
        industry_keywords = {
            "ai-tech": ["AI", "人工智能", "科技", "技术"],
            "manufacturing": ["制造", "生产", "工业"],
            "service": ["服务", "商业"],
            "other": []
        }
        
        keywords = industry_keywords.get(company_profile.industry_match, [])
        if any(keyword in str(policy.industry_tags) for keyword in keywords):
            score += 0.2
            matched_reqs.append("产业类型匹配")
        else:
            missing_reqs.append("产业类型需要进一步确认")
        
        # 企业认定匹配
        if company_profile.enterprise_certification:
            score += 0.1
            matched_reqs.append("具有企业认定资质")
        
        return {
            "match_score": min(score, 1.0),
            "matched_requirements": matched_reqs,
            "missing_requirements": missing_reqs,
            "recommendation": f"建议详细了解{policy.policy_name}的具体申请条件，并准备相关材料。"
        }

# 创建全局服务实例
policy_matcher_service = PolicyMatcherService() 