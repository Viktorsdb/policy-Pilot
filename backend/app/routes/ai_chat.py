from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, AsyncGenerator
import httpx
import json
import logging
from datetime import datetime

from ..config import settings
from ..models.schemas import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="消息角色: user, assistant, system")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息")
    messages: Optional[List[ChatMessage]] = Field(default=[], description="历史消息")
    policy_context: Optional[Dict[str, Any]] = Field(None, description="政策上下文信息")
    stream: bool = Field(False, description="是否流式返回")

class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str = Field(..., description="AI回复")
    timestamp: datetime = Field(default_factory=datetime.now)
    tokens_used: Optional[int] = Field(None, description="使用的token数量")

@router.post("/chat")
async def chat_with_ai(request: ChatRequest):
    """
    与AI聊天接口
    支持政策咨询和通用对话
    """
    try:
        # 构建系统提示
        system_prompt = build_system_prompt(request.policy_context)
        
        # 构建消息历史
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史消息
        for msg in request.messages[-10:]:  # 只保留最近10条消息
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
        response_text, tokens_used = await call_deepseek_api(messages)
        
        return APIResponse(
            success=True,
            message="AI回复成功",
            data={
                "response": response_text,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": tokens_used
            }
        )
        
    except Exception as e:
        logger.error(f"AI聊天失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI服务异常: {str(e)}"
        )

@router.post("/chat/stream")
async def chat_with_ai_stream(request: ChatRequest):
    """
    流式AI聊天接口
    """
    try:
        # 构建系统提示
        system_prompt = build_system_prompt(request.policy_context)
        
        # 构建消息历史
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史消息
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
        
        # 返回流式响应
        return StreamingResponse(
            stream_deepseek_response(messages),
            media_type="text/plain"
        )
        
    except Exception as e:
        logger.error(f"流式AI聊天失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI服务异常: {str(e)}"
        )

def build_system_prompt(policy_context: Optional[Dict[str, Any]] = None) -> str:
    """构建系统提示"""
    base_prompt = """你是PolicyPilot的专业AI助手，专门为企业提供政策咨询服务。

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

    if policy_context:
        # 格式化发布时间
        publish_date = policy_context.get('publish_date') or policy_context.get('publish_time') or policy_context.get('created_at')
        formatted_publish_date = publish_date if publish_date else '未知时间'
        
        policy_prompt = f"""

当前政策咨询上下文：
- 政策名称：{policy_context.get('policy_name', '未指定')}
- 适用地区：{policy_context.get('region', '未指定')}
- 支持类型：{policy_context.get('support_type', '未指定')}
- 最高金额：{policy_context.get('max_amount', '未限定')}
- 发布时间：{formatted_publish_date}

请基于这个政策背景回答用户问题。"""
        
        base_prompt += policy_prompt
    
    return base_prompt

async def call_deepseek_api(messages: List[Dict[str, str]]) -> tuple[str, int]:
    """调用DeepSeek API"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.DEEPSEEK_MODEL,
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
                return content, tokens_used
            else:
                error_detail = response.text
                logger.error(f"DeepSeek API错误 {response.status_code}: {error_detail}")
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
        logger.error(f"调用DeepSeek API异常: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI服务异常: {str(e)}"
        )

async def stream_deepseek_response(messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """流式调用DeepSeek API"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                'POST',
                f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.DEEPSEEK_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "stream": True
                }
            ) as response:
                if response.status_code != 200:
                    error_detail = await response.aread()
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"DeepSeek API调用失败: {error_detail.decode()}"
                    )
                
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        data = line[6:]  # 移除 'data: ' 前缀
                        if data.strip() == '[DONE]':
                            break
                        
                        try:
                            json_data = json.loads(data)
                            delta = json_data.get('choices', [{}])[0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
                            
    except Exception as e:
        logger.error(f"流式调用DeepSeek API异常: {e}")
        yield f"抱歉，AI服务出现异常: {str(e)}"

@router.get("/chat/models")
async def get_available_models():
    """获取可用的AI模型列表"""
    return APIResponse(
        success=True,
        message="获取模型列表成功",
        data={
            "models": [
                {
                    "id": "deepseek-chat",
                    "name": "DeepSeek Chat",
                    "description": "DeepSeek专业对话模型",
                    "capabilities": ["text-generation", "conversation", "analysis"]
                }
            ],
            "current_model": settings.DEEPSEEK_MODEL
        }
    ) 