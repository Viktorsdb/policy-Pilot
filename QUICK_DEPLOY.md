# PolicyPilot 快速部署指南

## 🚀 一键部署后端服务

### 方法一：Heroku一键部署（推荐）

**最简单的方式，无需安装任何工具！**

1. **点击部署按钮**
   
   [![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Viktorsdb/policy-Pilot)

2. **登录Heroku**
   - 如果没有账户，点击"Sign up"免费注册
   - 已有账户直接登录

3. **配置应用**
   - App name: 可以留空（系统自动生成）或填写自定义名称
   - Choose a region: 选择 United States 或 Europe
   - 其他配置保持默认即可

4. **开始部署**
   - 点击 "Deploy app" 按钮
   - 等待 2-3 分钟部署完成

5. **验证部署**
   - 部署成功后，点击 "View" 按钮
   - 看到 "PolicyPilot API is running!" 表示成功
   - 复制应用URL（如：https://your-app-name.herokuapp.com）

### 方法二：本地自动化部署

**适合有技术背景的用户**

```bash
# 1. 克隆项目
git clone https://github.com/Viktorsdb/policy-Pilot.git
cd policy-Pilot

# 2. 安装Heroku CLI
# Windows: 下载安装包 https://devcenter.heroku.com/articles/heroku-cli
# Mac: brew install heroku/brew/heroku
# Linux: curl https://cli-assets.heroku.com/install.sh | sh

# 3. 登录Heroku
heroku login

# 4. 运行自动化部署
python auto_deploy.py

# 5. 等待部署完成
```

## 📊 部署状态检查

### 在线检查
访问以下链接检查后端服务状态：
- https://policy-pilot-viktorsdb.herokuapp.com/api/v1/health

### 本地检查
```bash
python test_deployment.py
```

## 🔧 部署后配置

### 更新前端配置（如果需要）

如果您使用了自定义的Heroku应用名称，需要更新前端配置：

1. **编辑配置文件**
   - `policy-dashboard.js`
   - `ai-chat.js`
   - `script.js`

2. **替换API地址**
   ```javascript
   // 将这行
   return 'https://policy-pilot-viktorsdb.herokuapp.com/api/v1';
   
   // 替换为您的应用地址
   return 'https://your-app-name.herokuapp.com/api/v1';
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "Update API configuration"
   git push origin main
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

## 🆘 常见问题

### Q: 部署失败怎么办？
A: 
1. 检查GitHub仓库是否为公开状态
2. 确认所有必要文件都已提交
3. 重新点击部署按钮尝试

### Q: 部署成功但访问失败？
A: 
1. 等待2-3分钟让服务完全启动
2. 检查应用日志：`heroku logs --tail -a your-app-name`
3. 重启应用：`heroku restart -a your-app-name`

### Q: 如何查看应用日志？
A: 
```bash
heroku logs --tail -a your-app-name
```

### Q: 如何更新部署？
A: 
```bash
git push heroku main
```

## 💰 费用说明

### Heroku免费额度
- **免费时间**: 每月550小时
- **休眠机制**: 30分钟无访问后休眠
- **启动时间**: 休眠后首次访问需要10-30秒启动
- **适用场景**: 个人项目、演示、小团队使用

### 升级选项
- **Hobby ($7/月)**: 无休眠，自定义域名
- **Standard ($25/月)**: 更多资源，指标监控

## 🔄 自动化维护

### 定期检查
系统会自动检查后端服务状态，如果发现问题会：
1. 显示状态提示
2. 提供一键修复选项
3. 自动切换到备用数据模式

### 手动维护
```bash
# 检查服务状态
python test_deployment.py

# 重新部署
python auto_deploy.py

# 更新配置
python auto_deploy.py update-config
```

---

## 🎉 部署完成！

恭喜！您已经成功部署了PolicyPilot后端服务。

**访问地址：**
- 🌐 前端：https://viktorsdb.github.io/policy-Pilot/
- 🔗 后端：https://your-app-name.herokuapp.com/api/v1
- 📊 健康检查：https://your-app-name.herokuapp.com/api/v1/health

现在其他用户访问您的应用时，前端和后端都能正常工作了！

如有问题，请查看 [完整部署指南](DEPLOYMENT_GUIDE.md) 或提交 [Issue](https://github.com/Viktorsdb/policy-Pilot/issues)。 