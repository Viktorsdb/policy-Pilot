# PolicyPilot Backend API

PolicyPilot 是一个专为徐汇区 AI 创业公司设计的政策匹配平台后端系统。

## 🎯 系统功能

### 核心模块

1. **政策匹配引擎**
   - 基于企业画像智能匹配政策
   - 使用 DeepSeek AI 进行精准分析
   - 支持向量搜索和语义匹配

2. **数据爬虫系统**
   - 自动抓取政府网站政策信息
   - 支持 PDF 文档解析
   - 增量更新和去重处理

3. **向量化存储**
   - BGE-large-zh 模型生成向量
   - ChromaDB 存储和检索
   - 高效相似度搜索

4. **定时任务调度**
   - Celery Beat 每日自动爬取
   - 实时数据更新
   - 任务状态监控

## 🚀 快速启动

### 环境要求

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Chrome/Chromium (用于 Playwright)

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 数据库配置

1. 创建 PostgreSQL 数据库：
```sql
CREATE DATABASE policypilot;
CREATE USER policypilot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE policypilot TO policypilot_user;
```

2. 创建 `.env` 文件：
```env
DATABASE_URL=postgresql://policypilot_user:your_password@localhost:5432/policypilot
DEEPSEEK_API_KEY=sk-e51ff57edcae48a2b5b462d9f8abcd49
REDIS_URL=redis://localhost:6379/0
```

### 启动服务

```bash
# 启动后端API
python run.py

# 启动Redis (另一个终端)
redis-server

# 启动Celery worker (另一个终端)
celery -A app.celery worker --loglevel=info

# 启动Celery beat (另一个终端)
celery -A app.celery beat --loglevel=info
```

## 📖 API 文档

### 访问地址

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **API 根路径**: http://localhost:8000/api/v1

### 主要端点

#### 政策匹配

```http
POST /api/v1/match/simple
Content-Type: application/json

{
  "company_name": "AI创新科技公司",
  "registration_location": "xuhui",
  "industry_match": "ai-tech",
  "company_scale": "5m-20m",
  "rd_investment": "5-10",
  "patents": 5,
  "enterprise_certification": "high-tech"
}
```

#### 政策查询

```http
GET /api/v1/policies?page=1&limit=10&region=徐汇区
```

#### 爬虫控制

```http
POST /api/v1/crawler/start
GET /api/v1/crawler/status
```

## 🔧 配置说明

### 主要配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接字符串 | - |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - |
| `CHROMADB_COLLECTION` | ChromaDB 集合名 | `policy_embeddings` |
| `BGE_MODEL_NAME` | BGE 模型名称 | `BAAI/bge-large-zh` |
| `CRAWLER_DELAY` | 爬虫请求间隔 | `1.0` 秒 |

### 政府网站配置

系统默认配置了以下政府网站：

- **徐汇区政府**: https://www.xuhui.gov.cn
- **徐汇科委**: https://kjw.xuhui.gov.cn  
- **上海市经信委**: https://jxw.sh.gov.cn

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL   │
│   (HTML/JS)     │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ChromaDB      │◄──►│   Celery        │◄──►│   Redis         │
│   (Vectors)     │    │   (Tasks)       │    │   (Queue)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                      ┌─────────────────┐
                      │   Playwright    │
                      │   (Crawler)     │
                      └─────────────────┘
```

## 🔍 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 PostgreSQL 服务是否运行
   - 验证数据库连接字符串
   - 确认用户权限设置

2. **BGE模型加载失败**
   - 检查网络连接
   - 手动下载模型到本地
   - 使用镜像源加速下载

3. **Playwright 浏览器问题**
   - 重新安装浏览器：`playwright install chromium`
   - 检查系统依赖：`playwright install-deps`

4. **DeepSeek API 调用失败**
   - 验证 API Key 是否正确
   - 检查网络连接
   - 查看API配额和限制

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看Celery日志
celery -A app.celery events
```

## 📊 性能优化

### 生产环境建议

1. **数据库优化**
   - 为查询字段添加索引
   - 配置连接池
   - 启用查询缓存

2. **向量搜索优化**
   - 调整 ChromaDB 参数
   - 批量处理向量操作
   - 定期清理无效向量

3. **API性能优化**
   - 启用响应缓存
   - 使用异步处理
   - 配置负载均衡

## 🛠️ 开发指南

### 代码结构

```
backend/
├── app/
│   ├── models/          # 数据模型
│   ├── routes/          # API路由
│   ├── services/        # 业务逻辑
│   ├── database.py      # 数据库配置
│   ├── config.py        # 应用配置
│   └── main.py          # 应用入口
├── requirements.txt     # Python依赖
└── run.py              # 启动脚本
```

### 添加新功能

1. 在 `models/schemas.py` 中定义数据模型
2. 在 `services/` 中实现业务逻辑
3. 在 `routes/` 中添加API端点
4. 在 `main.py` 中注册路由

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**PolicyPilot Backend** - 让AI为企业发现政策机会 🚀 