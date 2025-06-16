# GitHub 托管设置指南

本指南将帮助您将PolicyPilot项目托管到GitHub，并设置自动部署。

## 📋 准备工作

### 1. 创建GitHub账户
如果您还没有GitHub账户，请访问 [github.com](https://github.com) 注册。

### 2. 安装Git
- **Windows**: 下载 [Git for Windows](https://git-scm.com/download/win)
- **Mac**: 使用 Homebrew `brew install git`
- **Linux**: `sudo apt install git` 或 `sudo yum install git`

## 🚀 创建GitHub仓库

### 方法一：通过GitHub网站创建

1. 登录GitHub
2. 点击右上角的 "+" 按钮
3. 选择 "New repository"
4. 填写仓库信息：
   - **Repository name**: `policy-pilot`
   - **Description**: `PolicyPilot - AI政策匹配平台`
   - **Visibility**: Public（公开）或 Private（私有）
   - ✅ 勾选 "Add a README file"
   - ✅ 选择 "Python" 作为 .gitignore 模板
   - ✅ 选择 "MIT License"
5. 点击 "Create repository"

### 方法二：通过命令行创建

```bash
# 1. 在项目目录中初始化Git
cd /path/to/policy-pilot
git init

# 2. 添加所有文件
git add .

# 3. 创建初始提交
git commit -m "🎉 Initial commit: PolicyPilot AI政策匹配平台"

# 4. 添加远程仓库（替换YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/policy-pilot.git

# 5. 推送到GitHub
git branch -M main
git push -u origin main
```

## 🔧 配置项目

### 1. 更新README中的链接

编辑 `README.md` 文件，将所有 `YOUR_USERNAME` 替换为您的GitHub用户名：

```markdown
# 替换这些链接
https://github.com/YOUR_USERNAME/policy-pilot
# 改为
https://github.com/your-actual-username/policy-pilot
```

### 2. 更新部署配置

编辑以下文件中的用户名：
- `app.json`
- `DEPLOYMENT.md`
- `.github/workflows/deploy.yml`

## 🌐 设置自动部署

### 1. Heroku部署设置

#### 创建Heroku应用
```bash
# 安装Heroku CLI
# 登录Heroku
heroku login

# 创建应用
heroku create your-app-name

# 连接GitHub仓库
heroku git:remote -a your-app-name
```

#### 设置GitHub Secrets
在GitHub仓库中设置以下Secrets：
1. 进入仓库 → Settings → Secrets and variables → Actions
2. 添加以下Secrets：
   - `HEROKU_API_KEY`: 您的Heroku API密钥
   - `HEROKU_APP_NAME`: 您的Heroku应用名称
   - `HEROKU_EMAIL`: 您的Heroku邮箱

### 2. Vercel部署设置

#### 连接Vercel
1. 访问 [vercel.com](https://vercel.com)
2. 使用GitHub账户登录
3. 导入您的仓库
4. 配置构建设置：
   - **Framework Preset**: Other
   - **Build Command**: `pip install -r requirements.txt`
   - **Output Directory**: `.`
   - **Install Command**: `pip install -r requirements.txt`

#### 设置环境变量
在Vercel项目设置中添加：
- `OPENAI_API_KEY`: 您的OpenAI API密钥（可选）

### 3. Railway部署设置

1. 访问 [railway.app](https://railway.app)
2. 使用GitHub账户登录
3. 点击 "New Project"
4. 选择 "Deploy from GitHub repo"
5. 选择您的 `policy-pilot` 仓库
6. Railway会自动检测并部署

## 📝 项目管理

### 分支管理策略

```bash
# 创建开发分支
git checkout -b develop

# 创建功能分支
git checkout -b feature/new-feature

# 合并到主分支
git checkout main
git merge feature/new-feature

# 推送更改
git push origin main
```

### 版本标签

```bash
# 创建版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0

# 查看所有标签
git tag -l
```

## 🔒 安全设置

### 1. 保护主分支

1. 进入仓库 → Settings → Branches
2. 点击 "Add rule"
3. 设置分支名称模式：`main`
4. 启用以下保护：
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging

### 2. 设置Secrets管理

将敏感信息存储在GitHub Secrets中：
- API密钥
- 数据库连接字符串
- 第三方服务凭证

### 3. 依赖安全扫描

启用GitHub的安全功能：
1. 进入仓库 → Settings → Security & analysis
2. 启用：
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates

## 📊 项目统计和徽章

### 添加项目徽章

在README.md中添加以下徽章：

```markdown
![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/policy-pilot?style=social)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/policy-pilot?style=social)
![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/policy-pilot)
![GitHub license](https://img.shields.io/github/license/YOUR_USERNAME/policy-pilot)
![Python version](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
```

### 设置项目主题

在仓库首页添加主题标签：
- `ai`
- `policy`
- `matching`
- `fastapi`
- `python`
- `government`
- `enterprise`

## 🤝 社区建设

### 1. 创建Issue模板

创建 `.github/ISSUE_TEMPLATE/` 目录，添加：
- `bug_report.md` - Bug报告模板
- `feature_request.md` - 功能请求模板
- `question.md` - 问题咨询模板

### 2. 创建Pull Request模板

创建 `.github/pull_request_template.md`：

```markdown
## 变更描述
请简要描述此PR的变更内容。

## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 性能优化
- [ ] 代码重构

## 测试
- [ ] 已通过所有现有测试
- [ ] 已添加新的测试用例
- [ ] 已在本地环境测试

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 已更新相关文档
- [ ] 已测试在不同环境下的兼容性
```

### 3. 设置贡献指南

创建 `CONTRIBUTING.md` 文件，说明：
- 如何报告Bug
- 如何提交功能请求
- 代码规范要求
- Pull Request流程

## 📈 监控和分析

### GitHub Insights

定期查看仓库的Insights页面：
- **Traffic**: 访问量统计
- **Commits**: 提交活动
- **Contributors**: 贡献者统计
- **Community**: 社区健康度

### 设置Webhooks

配置Webhooks以集成外部服务：
1. 进入仓库 → Settings → Webhooks
2. 添加Webhook URL
3. 选择触发事件
4. 配置密钥验证

## 🔄 持续集成/持续部署 (CI/CD)

### GitHub Actions工作流

项目已包含 `.github/workflows/deploy.yml`，提供：
- 自动测试
- 多平台部署
- 代码质量检查

### 自定义工作流

可以添加更多工作流：
- 代码格式检查
- 安全扫描
- 性能测试
- 文档生成

## 📞 获取帮助

### GitHub官方资源
- [GitHub文档](https://docs.github.com)
- [GitHub学习实验室](https://lab.github.com)
- [GitHub社区论坛](https://github.community)

### 项目支持
如果在设置过程中遇到问题：
1. 查看项目Issues页面
2. 创建新Issue描述问题
3. 联系项目维护者

## ✅ 完成检查清单

设置完成后，请确认以下项目：

- [ ] ✅ 仓库已创建并设置为公开
- [ ] ✅ 所有代码已推送到GitHub
- [ ] ✅ README中的链接已更新
- [ ] ✅ 部署配置已设置
- [ ] ✅ 自动部署已配置
- [ ] ✅ 分支保护已启用
- [ ] ✅ Secrets已正确设置
- [ ] ✅ 项目徽章已添加
- [ ] ✅ 社区文件已创建

---

**恭喜！您的PolicyPilot项目现在已经成功托管在GitHub上，其他人可以访问和使用了！** 🎉

记住要定期更新项目，回应社区反馈，让您的项目持续改进和发展。 