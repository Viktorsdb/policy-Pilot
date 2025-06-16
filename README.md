# PolicyPilot - AI政策匹配平台

🚀 **基于AI的智能政策匹配平台，帮助企业发现适合的政策机会**

## 📋 项目概述

PolicyPilot是一个智能政策匹配平台，通过AI技术帮助企业快速找到适合的政策机会，提供专业的申请指导和咨询服务。

### ✨ 主要功能

- 🎯 **智能政策匹配** - 基于企业信息精准匹配政策
- 🤖 **AI智能咨询** - 24/7 AI助手提供专业政策咨询
- 📊 **实时政策爬取** - 自动获取最新政策信息
- 📋 **申请指导** - 详细的申请流程和材料准备指导
- 💡 **成功率评估** - 基于历史数据评估申请成功率

## 🌐 在线访问

### 🎯 直接使用（推荐）
- **🔗 在线演示**: [https://viktorsdb.github.io/policy-Pilot/](https://viktorsdb.github.io/policy-Pilot/)
- **📊 政策看板**: [https://viktorsdb.github.io/policy-Pilot/policy-dashboard.html](https://viktorsdb.github.io/policy-Pilot/policy-dashboard.html)
- **🤖 AI聊天**: [https://viktorsdb.github.io/policy-Pilot/ai-chat.html](https://viktorsdb.github.io/policy-Pilot/ai-chat.html)
- **🏢 企业信息**: [https://viktorsdb.github.io/policy-Pilot/company-info.html](https://viktorsdb.github.io/policy-Pilot/company-info.html)

### 🚀 后端服务状态
- **部署状态页面**: [https://viktorsdb.github.io/policy-Pilot/deploy_status.html](https://viktorsdb.github.io/policy-Pilot/deploy_status.html)
- **Heroku后端**: https://policy-pilot-viktorsdb.herokuapp.com/api/v1
- **健康检查**: https://policy-pilot-viktorsdb.herokuapp.com/api/v1/health

> **💡 智能降级机制**: 如果后端服务不可用，前端会自动使用备用政策数据，确保基本功能正常使用。

## 🚀 一键部署后端服务

### 方法一：Heroku一键部署（推荐）

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Viktorsdb/policy-Pilot)

**最简单的方式，无需安装任何工具！**

1. 点击上方部署按钮
2. 登录或注册Heroku账户（完全免费）
3. 填写应用名称（可选）
4. 点击"Deploy app"按钮
5. 等待2-3分钟部署完成

### 方法二：Render自动部署

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Viktorsdb/policy-Pilot)

**连接GitHub仓库，自动构建部署**

1. 点击部署按钮
2. 连接GitHub账户
3. 选择仓库并确认配置
4. 自动构建和部署

### 方法三：Railway自动部署

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

**现代化平台，GitHub集成**

1. 连接GitHub仓库
2. 自动检测配置
3. 一键部署

### 方法四：本地自动化部署

```bash
# 克隆项目
git clone https://github.com/Viktorsdb/policy-Pilot.git
cd policy-Pilot

# 运行自动化部署脚本
python auto_deploy.py

# 或者分步执行
python auto_deploy.py check      # 检查部署要求
python auto_deploy.py deploy     # 部署到Heroku
python auto_deploy.py test-heroku # 测试部署
```

## 📊 部署配置文件

项目包含多个平台的部署配置文件：

- **Heroku**: `Procfile`, `app.json`, `runtime.txt`
- **Render**: `render.yaml`
- **Railway**: `railway.json`
- **Fly.io**: `fly.toml`
- **Docker**: `Dockerfile`

所有平台都支持：
- ✅ 免费部署
- ✅ 自动构建
- ✅ 环境变量配置
- ✅ 健康检查
- ✅ 自动重启

## 🔧 技术架构

### 前端技术栈
- **HTML5/CSS3/JavaScript** - 现代Web技术
- **响应式设计** - 支持各种设备
- **PWA支持** - 可安装为桌面应用
- **智能降级** - 后端不可用时自动使用备用数据

### 后端技术栈
- **FastAPI** - 高性能Python Web框架
- **DeepSeek API** - 专业AI对话服务
- **BeautifulSoup** - 政策信息爬取
- **Uvicorn** - ASGI服务器
- **动态端口配置** - 支持多平台部署

### 部署平台
- **前端**: GitHub Pages（自动部署）
- **后端**: Heroku, Render, Railway, Fly.io（多选一）

## 📊 功能特性

### 🎯 智能匹配系统
- 基于企业规模、行业、地区等多维度匹配
- 智能评分算法，提供匹配度百分比
- 个性化推荐建议

### 🤖 AI咨询助手
- 集成DeepSeek大模型
- 专业政策知识库
- 24/7在线服务
- 上下文理解能力
- 智能备用回复系统

### 📋 政策数据库
- 实时爬取徐汇区政策
- 国家级政策支持
- 自动更新机制
- 结构化数据存储
- 备用数据保障

### 📱 用户体验
- 现代化UI设计
- 流畅的交互动画
- 智能表单填写
- 自动保存功能
- 容错机制

## 🔄 部署状态监控

### 实时状态检查
访问 [部署状态页面](https://viktorsdb.github.io/policy-Pilot/deploy_status.html) 查看：
- 各平台部署状态
- 服务健康检查
- 推荐API地址
- 部署统计信息

### 自动化监控
- 前端自动检测后端状态
- 智能降级到备用数据
- 定期健康检查
- 错误自动恢复

## 🛠️ 开发指南

### 环境要求
- Python 3.11+
- Git

### 本地开发
```bash
# 1. 克隆项目
git clone https://github.com/Viktorsdb/policy-Pilot.git
cd policy-Pilot

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动后端服务
python real_policy_server.py

# 4. 启动前端服务（新终端）
python -m http.server 8080
```

### API文档
启动后端服务后，访问：
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### 主要API端点
```
GET  /api/v1/health              # 健康检查
GET  /api/v1/policies            # 获取政策列表
POST /api/v1/policies/match      # 政策匹配
POST /api/v1/ai/chat            # AI聊天
POST /api/v1/crawler/refresh     # 刷新爬取数据
```

## ✅ 验证部署成功

### 1. 后端服务检查
访问：`https://your-app-name.herokuapp.com/api/v1/health`

应该看到：
```json
{
  "status": "healthy",
  "message": "PolicyPilot API is running!",
  "timestamp": "2024-12-12T10:30:00Z"
}
```

### 2. 前端功能检查
访问：https://viktorsdb.github.io/policy-Pilot/

- ✅ 页面正常加载
- ✅ 没有"后端服务需要部署"的提示
- ✅ 政策匹配功能正常
- ✅ AI聊天功能正常

## 🔍 故障排除

### 常见问题

**Q: 前端显示"后端服务不可用"**
A: 这是正常的降级机制，前端会使用备用数据继续工作。如需完整功能，请部署后端服务。

**Q: AI聊天功能不响应**
A: 检查DeepSeek API密钥配置，或使用备用智能回复。

**Q: 政策数据不是最新的**
A: 点击"同步爬取数据"按钮手动刷新，或等待自动更新。

**Q: 部署失败怎么办？**
A: 
1. 检查GitHub仓库是否为公开状态
2. 确认所有必要文件都已提交
3. 查看部署日志排查问题
4. 尝试其他部署平台

### 部署测试
```bash
# 测试本地和远程部署
python test_deployment.py

# 检查部署要求
python auto_deploy.py check

# 查看部署状态
python auto_deploy.py test-heroku
```

## 💰 费用说明

### 免费额度对比

| 平台 | 免费时间 | 休眠机制 | 启动时间 | 适用场景 |
|------|----------|----------|----------|----------|
| **Heroku** | 550小时/月 | 30分钟无访问后休眠 | 10-30秒 | 个人项目、演示 |
| **Render** | 750小时/月 | 15分钟无访问后休眠 | 10-60秒 | 小型应用 |
| **Railway** | $5免费额度 | 无休眠 | 即时 | 开发测试 |
| **Fly.io** | 3个应用免费 | 自动缩放到0 | 5-15秒 | 全球部署 |

### 推荐方案
- **个人使用**: Heroku（简单易用）
- **小团队**: Render（更多免费时间）
- **开发测试**: Railway（无休眠）
- **全球访问**: Fly.io（多地区部署）

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 技术支持

- 📧 **邮箱**: support@policypilot.com
- 🐛 **Bug报告**: [GitHub Issues](https://github.com/Viktorsdb/policy-Pilot/issues)
- 💬 **讨论**: [GitHub Discussions](https://github.com/Viktorsdb/policy-Pilot/discussions)
- 📖 **文档**: [部署指南](QUICK_DEPLOY.md)

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和用户！

---

**让AI为您的企业发现无限可能！** ✨

[![Star this repo](https://img.shields.io/github/stars/Viktorsdb/policy-Pilot?style=social)](https://github.com/Viktorsdb/policy-Pilot)
[![Fork this repo](https://img.shields.io/github/forks/Viktorsdb/policy-Pilot?style=social)](https://github.com/Viktorsdb/policy-Pilot/fork)

## 🎉 快速开始

### 🌟 用户使用（无需部署）
1. 直接访问：https://viktorsdb.github.io/policy-Pilot/
2. 填写企业信息，开始智能匹配
3. 使用AI助手获取专业咨询

### 🚀 开发者部署（完整功能）
1. 点击上方Heroku部署按钮
2. 等待2-3分钟部署完成
3. 享受完整的AI政策匹配服务

### 📊 监控部署状态
访问：https://viktorsdb.github.io/policy-Pilot/deploy_status.html

---

**现在就开始使用PolicyPilot，让AI帮您发现更多政策机会！** 🎯 