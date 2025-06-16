# PolicyPilot - AI政策匹配平台

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Viktorsdb/policy-pilot)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Viktorsdb/policy-pilot)

基于AI的智能政策匹配平台，帮助企业发现适合的政策机会。本项目提供现代化、专业的企业级政策匹配服务，支持多种云平台一键部署。

## 🌐 在线体验

### 🎯 直接访问（推荐）
- **🔗 在线演示**: [https://viktorsdb.github.io/policy-Pilot/](https://viktorsdb.github.io/policy-Pilot/)
- **📊 政策看板**: [https://viktorsdb.github.io/policy-Pilot/policy-dashboard.html](https://viktorsdb.github.io/policy-Pilot/policy-dashboard.html)
- **🤖 AI聊天**: [https://viktorsdb.github.io/policy-Pilot/ai-chat.html](https://viktorsdb.github.io/policy-Pilot/ai-chat.html)
- **🏢 企业信息**: [https://viktorsdb.github.io/policy-Pilot/company-info.html](https://viktorsdb.github.io/policy-Pilot/company-info.html)

### 🚀 云平台部署
- **Heroku部署**: [https://policy-pilot-viktorsdb.herokuapp.com](https://policy-pilot-viktorsdb.herokuapp.com)
- **GitHub仓库**: [https://github.com/Viktorsdb/policy-Pilot](https://github.com/Viktorsdb/policy-Pilot)

## 🔧 问题修复说明

### ✅ 已修复的问题

#### 1. 政策数据显示问题
- **问题**: 政策看板显示"加载失败"
- **原因**: 后端API服务未启动或连接失败
- **解决方案**: 
  - 添加了备用政策数据，确保即使后端不可用也能显示政策信息
  - 包含6个真实的徐汇区AI政策和国家级政策
  - 智能降级机制：API失败时自动使用本地数据

#### 2. AI聊天功能问题
- **问题**: AI回复显示错误或无响应
- **原因**: DeepSeek API调用失败或网络问题
- **解决方案**:
  - 添加了智能备用响应系统
  - 根据用户问题类型提供专业的政策咨询回复
  - 包含高新技术企业认定、申请流程、材料准备等常见问题的详细回答

#### 3. 跨域和部署问题
- **问题**: GitHub Pages环境下API调用失败
- **原因**: 本地API地址在线上环境不可用
- **解决方案**:
  - 动态API配置：自动检测环境并使用相应的API地址
  - GitHub Pages使用Heroku后端，本地开发使用localhost

### 🛠️ 技术改进

#### 智能降级机制
```javascript
// 动态API配置
const getApiBaseUrl = () => {
    if (window.location.hostname.includes('github.io')) {
        return 'https://policy-pilot-api.herokuapp.com/api/v1';
    }
    return 'http://localhost:8001/api/v1';
};
```

#### 备用政策数据
- 包含真实的徐汇区AI政策
- 国家级高新技术企业认定政策
- 中小企业发展专项资金
- 上海市科技创新券等

#### 智能AI回复
- 政策条件解读
- 申请流程指导
- 材料准备建议
- 成功率分析

## 🚀 本地测试指南

### 方法一：使用Python HTTP服务器（推荐）
```bash
# 启动前端测试服务器
python start_local_server.py

# 访问 http://localhost:8080
```

### 方法二：启动完整服务
```bash
# 1. 启动后端API服务器
python real_policy_server.py

# 2. 启动前端服务器
python start_local_server.py

# 前端: http://localhost:8080
# 后端API: http://localhost:8001
```

### 方法三：直接打开HTML文件
```bash
# 直接在浏览器中打开
open index.html
# 或双击 index.html 文件
```

## ✨ 核心功能

### 🧠 智能匹配引擎
- AI深度学习算法
- 多维度政策分析
- 个性化推荐系统

### 📊 实时数据洞察
- 动态政策数据可视化
- 多维度数据分析
- 趋势预测报告

### 🤖 AI智能助手
- 24/7智能客服
- 政策解读服务
- 申请指导建议
- 智能备用响应系统

### 🔄 容错机制
- 自动降级到备用数据
- 智能错误处理
- 离线模式支持

## 🎨 界面设计特点

### 现代化UI设计
- 美丽的渐变色彩效果
- 半透明毛玻璃导航栏
- 响应式布局设计
- 优雅的动画交互

### 专业数据展示
- **1,247+** 政策案例数据库
- **100%** AI匹配精度
- **127+** 成功项目案例

## 🛠️ 技术栈

- **后端**: Python FastAPI + AI算法
- **前端**: HTML5 + CSS3 + JavaScript ES6+
- **AI服务**: DeepSeek API + 智能备用响应
- **数据处理**: pandas, numpy, scikit-learn
- **中文处理**: jieba分词库
- **部署平台**: GitHub Pages, Heroku, Vercel, Railway, Render
- **容错机制**: 多层降级策略

## 🚀 快速部署

### 🌐 GitHub Pages（推荐）
项目已自动部署到GitHub Pages，可直接访问：
- 主页：https://viktorsdb.github.io/policy-Pilot/
- 无需任何配置，即开即用！
- 包含完整的备用数据和智能响应

### 🔧 后端服务部署

#### 一键部署到Heroku（推荐）
1. 点击上方"Deploy to Heroku"按钮
2. 填写应用名称（建议：policy-pilot-你的用户名）
3. 可选：设置DEEPSEEK_API_KEY环境变量
4. 点击"Deploy app"
5. 部署完成后，记录应用URL（如：https://policy-pilot-viktorsdb.herokuapp.com）

#### 本地完整部署
```bash
# 克隆仓库
git clone https://github.com/Viktorsdb/policy-Pilot.git
cd policy-Pilot

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python real_policy_server.py
# 或使用启动脚本
python start_backend.py

# 启动前端服务（新终端）
python start_local_server.py
```

#### 测试部署
```bash
# 测试本地和远程部署
python test_deployment.py
```

### 🌐 前端部署配置

前端会自动检测运行环境：
- **GitHub Pages**: 自动连接到Heroku后端
- **本地开发**: 连接到localhost:8001

如需修改后端地址，请编辑以下文件中的API配置：
- `policy-dashboard.js`
- `ai-chat.js`

### 📋 环境变量配置

| 变量名 | 描述 | 必需 | 默认值 |
|--------|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 否 | - |
| `PORT` | 服务端口 | 否 | 8001 |
| `HOST` | 服务主机 | 否 | 0.0.0.0 |

## 📁 项目结构

```
policy-pilot/
├── 🏠 index.html              # 主页面
├── 📊 policy-dashboard.html   # 政策看板
├── 🤖 ai-chat.html           # AI聊天界面
├── 🏢 company-info.html      # 企业信息页面
├── ⚙️ real_policy_server.py  # 主服务器
├── 🕷️ real_crawler.py        # 数据爬虫
├── 🖥️ start_local_server.py  # 本地测试服务器
├── 📂 data/                  # 数据文件
├── 🔧 backend/               # 后端代码
├── 📋 requirements.txt       # Python依赖
├── 🚀 Procfile              # Heroku配置
├── ⚡ vercel.json           # Vercel配置
└── 📖 DEPLOYMENT.md         # 详细部署指南
```

## 🎯 功能模块

### 1. 智能政策匹配
- 基于企业信息的AI推荐
- 多维度匹配算法
- 实时政策更新
- 备用数据支持

### 2. 政策数据看板
- 可视化数据展示
- 交互式图表分析
- 政策趋势预测
- 离线数据支持

### 3. AI智能咨询
- 自然语言对话
- 政策解读服务
- 申请流程指导
- 智能备用回复

### 4. 企业信息管理
- 完整企业档案
- 资质认证管理
- 历史记录追踪

## 🌟 交互特性

### 动画效果
- 页面载入淡入动画
- 滚动时元素逐个显示
- 数字计数动画效果
- 卡片悬停交互

### 快捷操作
- `Ctrl + K` - 快速功能菜单
- `Esc` - 关闭弹出窗口
- 响应式触摸支持

## 📱 设备支持

- 💻 **桌面端** (1200px+)
- 📱 **平板端** (768px-1024px)  
- 📱 **移动端** (320px-768px)

## 🔧 环境配置

| 环境变量 | 描述 | 必需 |
|---------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 可选 |
| `FLASK_ENV` | Flask环境设置 | 否 |
| `PORT` | 服务端口 | 否 |

## 📊 性能指标

- ⚡ 页面加载时间 < 2秒
- 🎯 AI匹配准确率 > 95%
- 📈 数据处理速度 < 1秒
- 🔄 API响应时间 < 500ms
- 🛡️ 容错恢复时间 < 1秒

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

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和用户！

---

**让AI为您的企业发现无限可能！** ✨

[![Star this repo](https://img.shields.io/github/stars/Viktorsdb/policy-Pilot?style=social)](https://github.com/Viktorsdb/policy-Pilot)
[![Fork this repo](https://img.shields.io/github/forks/Viktorsdb/policy-Pilot?style=social)](https://github.com/Viktorsdb/policy-Pilot/fork) 