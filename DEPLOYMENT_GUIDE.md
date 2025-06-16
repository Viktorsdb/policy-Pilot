# PolicyPilot 部署指南

## 🎯 部署概述

PolicyPilot采用前后端分离架构：
- **前端**: 静态HTML/CSS/JS文件，部署在GitHub Pages
- **后端**: FastAPI服务器，部署在Heroku或其他云平台

## 🌐 前端部署（GitHub Pages）

### ✅ 已完成
前端已自动部署到GitHub Pages：
- 🔗 **访问地址**: https://viktorsdb.github.io/policy-Pilot/
- 🔄 **自动更新**: 每次推送代码后自动部署
- 📱 **响应式设计**: 支持桌面端和移动端

### 🔧 自定义部署
如需部署到自己的GitHub Pages：

1. **Fork仓库**
   ```bash
   # 在GitHub上Fork: https://github.com/Viktorsdb/policy-Pilot
   git clone https://github.com/你的用户名/policy-Pilot.git
   cd policy-Pilot
   ```

2. **启用GitHub Pages**
   - 进入仓库Settings → Pages
   - Source选择"GitHub Actions"
   - 等待自动部署完成

3. **访问应用**
   - 地址：https://你的用户名.github.io/policy-Pilot/

## 🚀 后端部署

### 方案一：Heroku部署（推荐）

#### 🎯 一键部署
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Viktorsdb/policy-Pilot)

1. 点击上方按钮
2. 填写应用名称（如：policy-pilot-yourname）
3. 可选：设置DEEPSEEK_API_KEY
4. 点击"Deploy app"
5. 记录应用URL

#### 🛠️ 手动部署
```bash
# 1. 安装Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. 登录Heroku
heroku login

# 3. 创建应用
heroku create policy-pilot-yourname

# 4. 设置环境变量（可选）
heroku config:set DEEPSEEK_API_KEY=your_api_key

# 5. 部署
git push heroku main

# 6. 查看应用
heroku open
```

#### 🔧 使用部署脚本
```bash
python deploy_to_heroku.py
```

### 方案二：Railway部署

1. 访问 [Railway](https://railway.app/)
2. 连接GitHub仓库
3. 选择policy-Pilot项目
4. 自动部署完成

### 方案三：Render部署

1. 访问 [Render](https://render.com/)
2. 创建新的Web Service
3. 连接GitHub仓库
4. 设置启动命令：`python real_policy_server.py`
5. 部署完成

## 🔗 连接前后端

### 更新API配置

部署后端后，需要更新前端的API配置：

1. **获取后端URL**
   - Heroku: `https://your-app-name.herokuapp.com`
   - Railway: `https://your-app.railway.app`
   - Render: `https://your-app.onrender.com`

2. **修改前端配置**
   
   编辑 `policy-dashboard.js`:
   ```javascript
   const getApiBaseUrl = () => {
       if (window.location.hostname.includes('github.io')) {
           return 'https://your-backend-url.herokuapp.com/api/v1';
       }
       return 'http://localhost:8001/api/v1';
   };
   ```
   
   编辑 `ai-chat.js`:
   ```javascript
   const getApiBaseUrl = () => {
       if (window.location.hostname.includes('github.io')) {
           return 'https://your-backend-url.herokuapp.com/api/v1';
       }
       return 'http://localhost:8001/api/v1';
   };
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "更新API配置"
   git push origin main
   ```

## 🧪 测试部署

### 自动测试
```bash
python test_deployment.py
```

### 手动测试

1. **前端测试**
   - 访问GitHub Pages地址
   - 测试页面加载和导航
   - 填写企业信息表单

2. **后端测试**
   - 访问 `https://your-backend-url/docs`
   - 测试API端点
   - 检查健康状态：`https://your-backend-url/api/v1/health`

3. **集成测试**
   - 在前端页面测试AI聊天
   - 测试政策匹配功能
   - 验证数据同步

## 🔧 环境变量配置

### 必需变量
- `PORT`: 服务端口（Heroku自动设置）
- `HOST`: 服务主机（默认0.0.0.0）

### 可选变量
- `DEEPSEEK_API_KEY`: DeepSeek API密钥（用于AI聊天）

### 设置方法

**Heroku:**
```bash
heroku config:set DEEPSEEK_API_KEY=your_key
```

**Railway:**
在项目设置中添加环境变量

**Render:**
在服务设置的Environment页面添加

## 🚨 常见问题

### 1. 后端部署失败
- 检查requirements.txt是否包含所有依赖
- 确认Python版本兼容（推荐3.11+）
- 查看部署日志排查错误

### 2. 前端无法连接后端
- 确认后端URL正确
- 检查CORS配置
- 验证API端点可访问

### 3. AI功能不工作
- 检查DEEPSEEK_API_KEY是否设置
- 确认API密钥有效
- 查看后端日志

### 4. 政策数据为空
- 后端会自动使用备用数据
- 检查爬虫功能是否正常
- 验证数据库初始化

## 📞 技术支持

如遇到部署问题：

1. **查看文档**: README.md
2. **检查日志**: 
   - Heroku: `heroku logs --tail`
   - Railway: 在控制台查看部署日志
3. **提交Issue**: [GitHub Issues](https://github.com/Viktorsdb/policy-Pilot/issues)

## 🎉 部署完成

部署成功后，您将拥有：

- ✅ 完整的AI政策匹配平台
- ✅ 智能聊天助手
- ✅ 政策数据看板
- ✅ 企业信息管理
- ✅ 自动化部署流程

**享受您的PolicyPilot之旅！** 🚀 