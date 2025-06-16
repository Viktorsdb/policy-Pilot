# PolicyPilot 部署指南

本文档详细介绍如何将PolicyPilot AI政策匹配平台部署到各种云平台和本地环境。

## 🚀 快速部署选项

### 1. Heroku 部署（推荐新手）

#### 一键部署
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/YOUR_USERNAME/policy-pilot)

#### 手动部署
```bash
# 1. 安装Heroku CLI
# 2. 登录Heroku
heroku login

# 3. 创建应用
heroku create your-app-name

# 4. 设置环境变量（可选）
heroku config:set OPENAI_API_KEY=your_openai_key

# 5. 部署
git push heroku main

# 6. 查看日志
heroku logs --tail
```

### 2. Vercel 部署（推荐前端开发者）

```bash
# 1. 安装Vercel CLI
npm i -g vercel

# 2. 部署
vercel --prod

# 3. 设置环境变量
vercel env add OPENAI_API_KEY
```

### 3. Railway 部署（推荐）

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/YOUR_TEMPLATE_ID)

```bash
# 1. 安装Railway CLI
npm install -g @railway/cli

# 2. 登录
railway login

# 3. 部署
railway up
```

### 4. Render 部署

1. 连接GitHub仓库到Render
2. 选择Web Service
3. 设置构建命令：`pip install -r requirements.txt`
4. 设置启动命令：`uvicorn real_policy_server:app --host 0.0.0.0 --port $PORT`

### 5. Docker 部署（推荐生产环境）

```bash
# 构建镜像
docker build -t policypilot .

# 运行容器
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key policypilot

# 或使用docker-compose
docker-compose up -d
```

### 6. 云服务器部署

#### 阿里云/腾讯云/AWS EC2
```bash
# 1. 连接服务器
ssh user@your-server-ip

# 2. 安装依赖
sudo apt update
sudo apt install python3 python3-pip nginx

# 3. 克隆项目
git clone https://github.com/YOUR_USERNAME/policy-pilot.git
cd policy-pilot

# 4. 安装Python依赖
pip3 install -r requirements.txt

# 5. 使用systemd管理服务
sudo cp policypilot.service /etc/systemd/system/
sudo systemctl enable policypilot
sudo systemctl start policypilot

# 6. 配置Nginx反向代理
sudo cp nginx.conf /etc/nginx/sites-available/policypilot
sudo ln -s /etc/nginx/sites-available/policypilot /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## 🔧 本地开发

### 环境要求
- Python 3.8+
- pip 或 conda

### 快速启动

#### Windows用户
```batch
# 双击运行
start.bat

# 或命令行运行
.\start.bat
```

#### Linux/Mac用户
```bash
# 给脚本执行权限
chmod +x start.sh

# 运行脚本
./start.sh
```

#### 手动启动
```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/policy-pilot.git
cd policy-pilot

# 2. 创建虚拟环境
python -m venv venv

# Windows激活
venv\Scripts\activate
# Linux/Mac激活
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行应用
python real_policy_server.py
```

访问 `http://localhost:8000` 查看应用。

## 🌐 环境变量配置

| 变量名 | 描述 | 必需 | 默认值 | 示例 |
|--------|------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 否 | - | sk-xxx |
| `PORT` | 服务端口 | 否 | 8000 | 8000 |
| `HOST` | 服务主机 | 否 | 0.0.0.0 | 0.0.0.0 |
| `LOG_LEVEL` | 日志级别 | 否 | info | debug |

### 环境变量设置方法

#### 1. .env文件（推荐）
```bash
# 创建.env文件
echo "OPENAI_API_KEY=your_api_key_here" > .env
echo "PORT=8000" >> .env
```

#### 2. 系统环境变量
```bash
# Linux/Mac
export OPENAI_API_KEY=your_api_key_here

# Windows
set OPENAI_API_KEY=your_api_key_here
```

## 📁 项目结构详解

```
policy-pilot/
├── 🏠 index.html              # 主页面
├── 📊 policy-dashboard.html   # 政策看板
├── 🤖 ai-chat.html           # AI聊天界面
├── 🏢 company-info.html      # 企业信息页面
├── ⚙️ real_policy_server.py  # FastAPI主服务器
├── 🕷️ real_crawler.py        # 数据爬虫
├── 📂 data/                  # 数据文件目录
│   └── real_policies.json   # 真实政策数据
├── 🔧 backend/               # 后端代码
├── 📋 requirements.txt       # Python依赖
├── 🚀 Procfile              # Heroku配置
├── ⚡ vercel.json           # Vercel配置
├── 🐳 Dockerfile            # Docker配置
├── 🐙 docker-compose.yml    # Docker Compose配置
├── 🔄 .github/workflows/    # GitHub Actions
├── 📖 DEPLOYMENT.md         # 本部署指南
├── 🚀 start.sh              # Linux/Mac启动脚本
├── 🚀 start.bat             # Windows启动脚本
└── 📄 LICENSE               # MIT许可证
```

## 🔍 功能特性

### 🧠 智能政策匹配
- 基于AI的政策推荐算法
- 多维度匹配评分系统
- 个性化推荐引擎

### 📊 实时数据分析
- 动态政策数据可视化
- 多维度数据分析
- 趋势预测报告

### 🤖 AI智能助手
- 24/7智能客服
- 政策解读服务
- 申请流程指导

### 🏢 企业信息管理
- 完整企业档案系统
- 资质认证管理
- 历史记录追踪

## 🛠️ 技术栈

### 后端技术
- **框架**: FastAPI 0.104+
- **服务器**: Uvicorn
- **数据处理**: pandas, numpy, scikit-learn
- **AI服务**: OpenAI GPT API
- **中文处理**: jieba分词

### 前端技术
- **基础**: HTML5, CSS3, JavaScript ES6+
- **样式**: CSS Grid, Flexbox, 渐变动画
- **交互**: Intersection Observer, 事件委托

### 部署技术
- **容器化**: Docker, Docker Compose
- **云平台**: Heroku, Vercel, Railway, Render
- **CI/CD**: GitHub Actions
- **反向代理**: Nginx

## 📊 性能优化

### 后端优化
- 异步请求处理
- 数据缓存机制
- API响应压缩
- 数据库连接池

### 前端优化
- 静态资源CDN加速
- 图片懒加载
- CSS/JS压缩
- 浏览器缓存策略

## 🔐 安全考虑

### API安全
- CORS跨域请求控制
- 输入数据验证和清理
- API访问频率限制
- 敏感信息加密存储

### 部署安全
- HTTPS强制重定向
- 环境变量管理
- 容器安全配置
- 定期安全更新

## 🐛 故障排除

### 常见问题

#### 1. 部署失败
```bash
# 检查Python版本
python --version

# 检查依赖安装
pip list

# 查看详细错误日志
python real_policy_server.py --log-level debug
```

#### 2. 端口占用
```bash
# 查看端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# 杀死占用进程
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # Linux/Mac
```

#### 3. AI功能不工作
- 验证OPENAI_API_KEY环境变量
- 检查API配额和权限
- 确认网络连接正常

#### 4. 静态文件404
- 确认文件路径正确
- 检查服务器静态文件配置
- 验证文件权限设置

### 日志查看

#### 本地开发
```bash
# 查看实时日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

#### 云平台日志
```bash
# Heroku
heroku logs --tail

# Vercel
vercel logs

# Railway
railway logs
```

## 🔄 更新部署

### 自动部署
项目配置了GitHub Actions，推送到main分支会自动触发部署。

### 手动更新
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 更新依赖
pip install -r requirements.txt

# 3. 重启服务
# Docker
docker-compose restart

# Systemd
sudo systemctl restart policypilot

# PM2
pm2 restart policypilot
```

## 📞 技术支持

### 获取帮助
- 📧 **邮箱**: support@policypilot.com
- 🐛 **Bug报告**: [GitHub Issues](https://github.com/YOUR_USERNAME/policy-pilot/issues)
- 💬 **讨论**: [GitHub Discussions](https://github.com/YOUR_USERNAME/policy-pilot/discussions)
- 📚 **文档**: [项目Wiki](https://github.com/YOUR_USERNAME/policy-pilot/wiki)

### 社区支持
- 💬 **QQ群**: 123456789
- 📱 **微信群**: 扫描二维码加入
- 🎯 **知乎专栏**: PolicyPilot技术分享

## 📈 监控和维护

### 健康检查
```bash
# API健康检查
curl http://your-domain.com/api/v1/health

# 服务状态检查
systemctl status policypilot
```

### 性能监控
- 使用Prometheus + Grafana监控
- 配置告警规则
- 定期性能测试

### 备份策略
- 数据库定期备份
- 配置文件版本控制
- 日志文件轮转

## 📄 许可证

本项目采用MIT许可证，详见[LICENSE](LICENSE)文件。

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和用户！

---

**祝您部署顺利！如有问题，欢迎随时联系我们。** 🎉

[![Star this repo](https://img.shields.io/github/stars/YOUR_USERNAME/policy-pilot?style=social)](https://github.com/YOUR_USERNAME/policy-pilot)
[![Fork this repo](https://img.shields.io/github/forks/YOUR_USERNAME/policy-pilot?style=social)](https://github.com/YOUR_USERNAME/policy-pilot/fork) 