// AI对话页面交互脚本

// 全局变量
let messages = [];
let isAITyping = false;
let conversationId = null;
let consultPolicy = null;
let isConsultingPolicy = false;

// 动态API配置 - 支持多个后端服务
const getApiBaseUrl = () => {
    // 如果是GitHub Pages环境
    if (window.location.hostname.includes('github.io')) {
        // 优先尝试Render后端，然后降级到Heroku
        return 'https://policy-pilot.onrender.com/api/v1';
    }
    // 本地开发环境
    return 'http://localhost:8001/api/v1';
};

// 备用API地址列表
const BACKUP_API_URLS = [
    'https://policy-pilot.onrender.com/api/v1',
    'https://policy-pilot-viktorsdb.herokuapp.com/api/v1'
];

const API_BASE_URL = getApiBaseUrl();

// DOM 就绪后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    bindEvents();
    checkConsultTopic();
    checkPolicyConsult();
});

// 初始化聊天
function initializeChat() {
    conversationId = generateConversationId();
    
    // 页面载入动画
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.6s ease';
        document.body.style.opacity = '1';
    }, 100);
    
    // 添加欢迎消息
    setTimeout(() => {
        const welcomeMessage = `🤖 您好！我是PolicyPilot的AI助手，专门为企业提供政策咨询服务。

我可以帮助您：
• 🔍 分析适合的政策机会
• 📋 解读政策申请条件  
• 📝 指导申请材料准备
• 💡 提供申请成功技巧
• 📊 评估申请成功率

请告诉我您的具体需求，我会为您提供专业的建议！`;
        
        addMessage(welcomeMessage, 'ai');
        
        if (!isConsultingPolicy) {
            showQuickReplies();
        }
    }, 800);
    
    // 滚动到底部
    setTimeout(() => {
        scrollToBottom();
    }, 1000);
}

// 检查政策咨询
function checkPolicyConsult() {
    const policyData = sessionStorage.getItem('consultPolicy');
    const isMatched = sessionStorage.getItem('consultPolicyMatched') === 'true';
    
    if (policyData) {
        consultPolicy = JSON.parse(policyData);
        isConsultingPolicy = true;
        
        // 清除sessionStorage中的数据
        sessionStorage.removeItem('consultPolicy');
        sessionStorage.removeItem('consultPolicyMatched');
        
        // 显示政策咨询欢迎信息
        setTimeout(() => {
            showPolicyWelcome(consultPolicy, isMatched);
        }, 1200);
    }
}

// 显示政策咨询欢迎信息
function showPolicyWelcome(policy, isMatched) {
    const welcomeMessage = generatePolicyWelcome(policy, isMatched);
    addMessage(welcomeMessage, 'ai');
    
    // 显示针对性的快速回复选项
    setTimeout(() => {
        showPolicyQuickReplies(policy);
    }, 1000);
}

// 生成政策欢迎信息
function generatePolicyWelcome(policy, isMatched) {
    const maxAmount = formatAmount(policy.max_amount);
    const matchInfo = isMatched && policy.match_score ? 
        `\n\n🎯 <strong>匹配度评估：${Math.round(policy.match_score * 100)}%</strong>` : '';
    
    // 使用发布时间而不是申请截止时间
    const publishDate = policy.publish_date || policy.publish_time || policy.created_at;
    const formattedPublishDate = formatDate(publishDate) || '未知时间';
    
    return `🤖 您好！我看到您对"<strong>${policy.policy_name}</strong>"这项政策很感兴趣。让我为您详细介绍一下：

📍 <strong>适用地区：</strong>${policy.region}
💰 <strong>最高金额：</strong>${maxAmount}
📅 <strong>发布时间：</strong>${formattedPublishDate}
🏢 <strong>适用行业：</strong>${policy.industry_tags ? policy.industry_tags.join('、') : '通用'}${matchInfo}

我可以为您详细解答关于这个政策的任何问题，包括申请条件、申报流程、材料准备等。您希望了解哪个方面呢？`;
}

// 显示政策相关的快速回复
function showPolicyQuickReplies(policy) {
    const quickReplies = document.getElementById('quickReplies');
    if (!quickReplies) return;
    
    quickReplies.innerHTML = `
        <div class="quick-reply-title">💡 您可能想了解的问题：</div>
        <div class="quick-replies">
            <button class="quick-reply-btn" onclick="sendQuickReply('这个政策的具体申请条件是什么？')">
                <i class="fas fa-clipboard-check"></i>
                申请条件
            </button>
            <button class="quick-reply-btn" onclick="sendQuickReply('申请流程是怎样的？需要准备哪些材料？')">
                <i class="fas fa-list-alt"></i>
                申请流程
            </button>
            <button class="quick-reply-btn" onclick="sendQuickReply('我的企业符合申请条件吗？')">
                <i class="fas fa-search"></i>
                匹配度分析
            </button>
            <button class="quick-reply-btn" onclick="sendQuickReply('有什么注意事项或申请技巧吗？')">
                <i class="fas fa-lightbulb"></i>
                申请技巧
            </button>
            <button class="quick-reply-btn" onclick="sendQuickReply('这个政策的成功率怎么样？')">
                <i class="fas fa-chart-line"></i>
                成功率分析
            </button>
            <button class="quick-reply-btn" onclick="sendQuickReply('帮我分析其他相似的政策')">
                <i class="fas fa-search-plus"></i>
                相似政策
            </button>
        </div>
    `;
    
    quickReplies.style.display = 'block';
}

// 检查是否有特定咨询主题
function checkConsultTopic() {
    const consultTopic = sessionStorage.getItem('aiConsultTopic');
    if (consultTopic) {
        sessionStorage.removeItem('aiConsultTopic');
        
        // 自动发送关于该主题的问题
        setTimeout(() => {
            const question = `我想了解关于"${consultTopic}"的详细信息，包括申请条件、流程和注意事项。`;
            sendMessage(question);
        }, 1500);
    }
}

// 处理键盘按键
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// 发送消息
async function sendMessage(customMessage = null) {
    const input = document.getElementById('chatInput');
    const message = customMessage || input.value.trim();
    
    if (!message || isAITyping) return;
    
    // 清空输入框（如果不是自定义消息）
    if (!customMessage) {
        input.value = '';
        input.style.height = 'auto';
    }
    
    // 添加用户消息
    addMessage(message, 'user');
    
    // 隐藏快速回复
    hideQuickReplies();
    
    // 显示AI正在输入
    showAITyping();
    
    try {
        // 调用真正的DeepSeek API
        const aiResponse = await callDeepSeekAPI(message);
        hideAITyping();
        addMessage(aiResponse, 'ai');
        
        if (!isConsultingPolicy) {
            showQuickReplies();
        }
    } catch (error) {
        hideAITyping();
        console.error('AI回复失败:', error);
        addMessage('抱歉，AI服务暂时不可用，请稍后重试。', 'ai');
        showNotification('AI服务连接失败', 'error');
    }
}

// 调用DeepSeek API - 支持多后端尝试
async function callDeepSeekAPI(userMessage) {
    // 构建请求数据
    const requestData = {
        message: userMessage,
        messages: messages.slice(-10).map(msg => ({
            role: msg.sender === 'user' ? 'user' : 'assistant',
            content: msg.text,
            timestamp: msg.timestamp
        })),
        policy_context: consultPolicy ? {
            policy_name: consultPolicy.policy_name,
            region: consultPolicy.region,
            support_type: consultPolicy.support_type,
            max_amount: consultPolicy.max_amount,
            deadline: consultPolicy.deadline,
            industry_tags: consultPolicy.industry_tags,
            requirements: consultPolicy.requirements
        } : null,
        stream: false
    };
    
    // 尝试所有可用的后端服务
    for (let i = 0; i < BACKUP_API_URLS.length; i++) {
        const apiUrl = BACKUP_API_URLS[i];
        try {
            console.log(`🔗 尝试AI API: ${apiUrl}`);
            
            // 发送请求到后端
            const response = await fetch(`${apiUrl}/ai/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
                timeout: 25000 // 25秒超时
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.log(`❌ AI API失败 (${apiUrl}): ${response.status}`);
                continue; // 尝试下一个后端
            }
            
            const data = await response.json();
            
            if (data.success && data.data.response) {
                console.log(`✅ AI回复成功 (${apiUrl})，使用token: ${data.data.tokens_used || 0}`);
                return data.data.response;
            } else {
                console.log(`❌ AI API返回格式错误 (${apiUrl})`);
                continue; // 尝试下一个后端
            }
            
        } catch (error) {
            console.error(`❌ AI API连接失败 (${apiUrl}):`, error);
            continue; // 尝试下一个后端
        }
    }
    
    // 所有后端都失败，返回智能备用响应
    console.log('❌ 所有AI后端都不可用，使用备用响应');
    return generateFallbackResponse(userMessage);
}

// 生成智能备用响应
function generateFallbackResponse(userMessage) {
    const message = userMessage.toLowerCase();
    
    // 政策相关问题的智能回复
    if (message.includes('政策') || message.includes('申请') || message.includes('条件')) {
        if (consultPolicy) {
            return generatePolicySpecificResponse(userMessage, consultPolicy);
        } else {
            return `关于您询问的政策问题，我建议您：

📋 **查看政策详情**
• 访问我们的政策看板页面
• 查看具体的申请条件和要求
• 了解申请流程和时间节点

📞 **联系专业顾问**
• 电话：400-123-4567
• 邮箱：policy@policypilot.com
• 在线客服：工作日 9:00-18:00

🔍 **推荐操作**
• 完善企业信息以获得精准匹配
• 查看相似企业的成功案例
• 关注政策更新通知

如需更详细的指导，建议您联系我们的专业政策顾问团队。`;
        }
    }
    
    // 高新技术企业认定相关
    if (message.includes('高新') || message.includes('认定')) {
        return `关于高新技术企业认定，我为您提供基本信息：

📋 **主要认定条件**
1. 企业成立一年以上
2. 拥有核心自主知识产权
3. 产品属于《国家重点支持的高新技术领域》
4. 科技人员占比不低于10%
5. 研发费用占比符合要求

📊 **评分标准（总分100分）**
• 知识产权（30分）
• 科技成果转化（30分）
• 研发组织管理（20分）
• 企业成长性（20分）

⭐ **优惠政策**
• 企业所得税减按15%征收
• 研发费用加计扣除
• 各类政府补贴优先支持

📞 如需详细指导，请联系：400-123-4567`;
    }
    
    // 申请流程相关
    if (message.includes('流程') || message.includes('步骤') || message.includes('怎么申请')) {
        return `政策申请一般流程如下：

📝 **第一步：准备阶段**
• 了解政策详细要求
• 评估企业匹配度
• 准备基础材料

📋 **第二步：材料准备**
• 企业基本信息
• 财务报表
• 相关证明文件
• 项目计划书

📤 **第三步：提交申请**
• 在线填写申请表
• 上传相关材料
• 提交审核

⏰ **第四步：审核流程**
• 初审（5-10个工作日）
• 专家评审
• 现场核查（如需要）
• 结果公示

💡 **温馨提示**
建议您先通过我们的政策匹配系统评估申请成功率，然后联系专业顾问获得个性化指导。`;
    }
    
    // 材料准备相关
    if (message.includes('材料') || message.includes('文件') || message.includes('准备什么')) {
        return `政策申请通常需要以下材料：

📄 **基础材料**
• 营业执照副本
• 组织机构代码证
• 税务登记证
• 企业章程

💰 **财务材料**
• 近三年财务报表
• 审计报告
• 纳税证明
• 银行资信证明

🔬 **技术材料**
• 知识产权证书
• 研发项目资料
• 技术合同
• 检测报告

👥 **人员材料**
• 员工花名册
• 学历证明
• 社保缴费证明
• 研发人员统计

📋 **项目材料**
• 项目可行性报告
• 商业计划书
• 市场分析报告
• 预期效益分析

💡 **建议**：不同政策要求的材料可能有所差异，建议根据具体政策要求准备。`;
    }
    
    // 默认通用回复
    return `感谢您的咨询！虽然AI服务暂时不可用，但我仍然可以为您提供帮助：

🎯 **我可以协助您**
• 政策查询和匹配
• 申请条件解读
• 流程指导
• 材料准备建议

📞 **获得专业帮助**
• 热线电话：400-123-4567
• 在线客服：工作日 9:00-18:00
• 邮箱咨询：policy@policypilot.com

🔍 **推荐功能**
• 访问政策看板查看最新政策
• 使用企业信息匹配功能
• 查看成功案例和申请技巧

如果您有具体的政策问题，请详细描述，我会尽力为您提供有用的信息！`;
}

// 生成特定政策的智能回复
function generatePolicySpecificResponse(userMessage, policy) {
    const message = userMessage.toLowerCase();
    const maxAmount = formatAmount(policy.max_amount);
    
    if (message.includes('条件') || message.includes('要求')) {
        return `关于"${policy.policy_name}"的申请条件：

📍 **基本要求**
${policy.requirements ? policy.requirements.map(req => `• ${req}`).join('\n') : '• 请查看政策原文了解详细要求'}

💰 **支持金额**：最高 ${maxAmount}
📅 **发布时间**：${formatDate(policy.publish_date)}
🏢 **适用地区**：${policy.region}
🏭 **适用行业**：${policy.industry_tags ? policy.industry_tags.join('、') : '通用'}

📞 **获得详细指导**
建议您联系我们的专业顾问团队，获得针对性的申请指导：
• 电话：400-123-4567
• 在线咨询：工作日 9:00-18:00`;
    }
    
    if (message.includes('流程') || message.includes('申请')) {
        return `"${policy.policy_name}"申请流程指导：

📝 **申请准备**
• 仔细阅读政策文件
• 评估企业匹配度
• 准备相关材料

📋 **材料清单**
• 企业基本信息
• 财务证明材料
• 项目相关文件
• 其他政策要求的特定材料

📤 **提交方式**
• 在线申报系统
• 现场提交
• 邮寄申报

⏰ **时间安排**
• 申报期：${policy.application_period || '请关注官方通知'}
• 审核周期：一般15-30个工作日

💡 **成功建议**
建议您在申请前咨询专业顾问，提高申请成功率。`;
    }
    
    return `关于"${policy.policy_name}"：

💰 **支持金额**：最高 ${maxAmount}
📍 **适用地区**：${policy.region}
🏭 **支持类型**：${policy.support_type === 'grant' ? '资金补贴' : policy.support_type === 'tax' ? '税收优惠' : '政策支持'}

📞 **专业咨询**
如需了解更多详情，建议联系我们的政策顾问：
• 电话：400-123-4567
• 在线客服：工作日 9:00-18:00

您还有其他想了解的问题吗？`;
}

// 格式化金额
function formatAmount(amount) {
    if (!amount) return '未限定';
    if (amount >= 100000000) {
        return `${(amount / 100000000).toFixed(1)}亿元`;
    } else if (amount >= 10000) {
        return `${(amount / 10000).toFixed(1)}万元`;
    } else {
        return `${amount}元`;
    }
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '长期有效';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch {
        return dateString;
    }
}

// 添加消息到聊天区域
function addMessage(text, sender) {
    const chatArea = document.getElementById('chatArea');
    const messageEl = document.createElement('div');
    messageEl.className = `message ${sender}-message`;
    
    const timestamp = new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    // 如果是AI消息，格式化文本
    const formattedText = sender === 'ai' ? formatAIResponse(text) : text;
    
    if (sender === 'user') {
        messageEl.innerHTML = `
            <div class="message-content">
                <div class="message-bubble">
                    <div class="message-text">${formattedText}</div>
                </div>
                <div class="message-time">${timestamp}</div>
            </div>
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
        `;
    } else {
        messageEl.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
                <div class="message-bubble">
                    <div class="message-text">${formattedText}</div>
                </div>
                <div class="message-time">${timestamp}</div>
        </div>
    `;
    }
    
    chatArea.appendChild(messageEl);
    
    // 保存到消息历史
    messages.push({
        text: text,
        sender: sender,
        timestamp: new Date()
    });
    
    // 滚动到底部
    setTimeout(() => {
        scrollToBottom();
    }, 100);
}

// 格式化AI回答，去除markdown并美化显示
function formatAIResponse(text) {
    if (!text) return '';
    
    let formatted = text;
    
    // 先处理代码块，避免被其他规则影响
    formatted = formatted.replace(/```[\s\S]*?```/g, (match) => {
        const code = match.replace(/```/g, '').trim();
        return `<div class="ai-code-block">${escapeHtml(code)}</div>`;
    });
    
    // 处理行内代码
    formatted = formatted.replace(/`([^`]+)`/g, '<span class="ai-inline-code">$1</span>');
    
    // 处理标题（需要在行首）
    formatted = formatted.replace(/^### (.+$)/gm, '<div class="ai-heading-3">$1</div>');
    formatted = formatted.replace(/^## (.+$)/gm, '<div class="ai-heading-2">$1</div>');
    formatted = formatted.replace(/^# (.+$)/gm, '<div class="ai-heading-1">$1</div>');
    
    // 处理加粗文本
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<span class="ai-bold">$1</span>');
    formatted = formatted.replace(/__([^_]+)__/g, '<span class="ai-bold">$1</span>');
    
    // 处理斜体文本（注意避免与列表符号冲突）
    formatted = formatted.replace(/\*([^*\n]+)\*/g, '<span class="ai-italic">$1</span>');
    formatted = formatted.replace(/_([^_\n]+)_/g, '<span class="ai-italic">$1</span>');
    
    // 处理链接
    formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="ai-link">$1</a>');
    
    // 处理无序列表项
    let listCounter = 0;
    formatted = formatted.replace(/^[\-\*\+] (.+$)/gm, (match, content) => {
        return `<div class="ai-list-item">• ${content}</div>`;
    });
    
    // 处理有序列表项
    formatted = formatted.replace(/^\d+\. (.+$)/gm, '<div class="ai-list-item-numbered">$1</div>');
    
    // 处理段落分隔（双换行）
    formatted = formatted.replace(/\n\s*\n/g, '<div class="ai-paragraph-break"></div>');
    
    // 处理单个换行
    formatted = formatted.replace(/\n/g, '<br>');
    
    // 清理多余的空白
    formatted = formatted.replace(/<div class="ai-paragraph-break"><\/div>\s*<div class="ai-paragraph-break"><\/div>/g, '<div class="ai-paragraph-break"></div>');
    
    return formatted;
}

// HTML转义函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 显示AI正在输入
function showAITyping() {
    if (isAITyping) return;
    
    isAITyping = true;
    const chatArea = document.getElementById('chatArea');
    
    const typingEl = document.createElement('div');
    typingEl.className = 'message ai-message typing-message';
    typingEl.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-bubble">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <div class="typing-text">AI正在思考中...</div>
            </div>
        </div>
    `;
    
    chatArea.appendChild(typingEl);
    scrollToBottom();
}

// 隐藏AI正在输入
function hideAITyping() {
    isAITyping = false;
    const typingEl = document.querySelector('.typing-message');
    if (typingEl) {
        typingEl.remove();
    }
}

// 快速回复
function sendQuickReply(message) {
    sendMessage(message);
}

// 显示快速回复
function showQuickReplies() {
    const quickReplies = document.getElementById('quickReplies');
    if (quickReplies && !isConsultingPolicy) {
        quickReplies.innerHTML = `
            <div class="quick-reply-title">💡 您可能想了解：</div>
            <div class="quick-replies">
                <button class="quick-reply-btn" onclick="sendQuickReply('什么是高新技术企业认定？如何申请？')">
                    <i class="fas fa-award"></i>
                    高新技术企业
                </button>
                <button class="quick-reply-btn" onclick="sendQuickReply('中小企业有哪些创新基金可以申请？')">
                    <i class="fas fa-rocket"></i>
                    创新基金
                </button>
                <button class="quick-reply-btn" onclick="sendQuickReply('上海市有哪些针对AI企业的政策？')">
                    <i class="fas fa-brain"></i>
                    AI产业政策
                </button>
                <button class="quick-reply-btn" onclick="sendQuickReply('如何提高政策申请的成功率？')">
                    <i class="fas fa-chart-line"></i>
                    申请技巧
                </button>
            </div>
        `;
        quickReplies.style.display = 'block';
    }
}

// 隐藏快速回复
function hideQuickReplies() {
    const quickReplies = document.getElementById('quickReplies');
    if (quickReplies) {
        quickReplies.style.display = 'none';
    }
}

// 滚动到底部
function scrollToBottom() {
    const chatArea = document.getElementById('chatArea');
    chatArea.scrollTo({
        top: chatArea.scrollHeight,
        behavior: 'smooth'
    });
    
    // 更新滚动到底部按钮
    updateScrollButton();
}

// 更新滚动按钮
function updateScrollButton() {
    const chatArea = document.getElementById('chatArea');
    const scrollBtn = document.getElementById('scrollToBottomBtn');
    
    if (!scrollBtn) {
        createScrollButton();
        return;
    }
    
    const isAtBottom = chatArea.scrollTop + chatArea.clientHeight >= chatArea.scrollHeight - 100;
    
    if (isAtBottom) {
        scrollBtn.classList.remove('visible');
    } else {
        scrollBtn.classList.add('visible');
    }
}

// 创建滚动到底部按钮
function createScrollButton() {
    const button = document.createElement('button');
    button.id = 'scrollToBottomBtn';
    button.className = 'scroll-to-bottom';
    button.innerHTML = '<i class="fas fa-arrow-down"></i>';
    button.onclick = scrollToBottom;
    
    document.querySelector('.main-content').appendChild(button);
}

// 清空对话
function clearChat() {
    if (confirm('确定要清空所有对话记录吗？')) {
        const chatArea = document.getElementById('chatArea');
        chatArea.innerHTML = '';
        
        messages = [];
        isConsultingPolicy = false;
        consultPolicy = null;
        
        // 重新初始化
        setTimeout(() => {
            initializeChat();
        }, 300);
        
        showNotification('对话记录已清空', 'success');
    }
}

// 显示附件菜单
function showAttachmentMenu() {
    showNotification('附件功能开发中，敬请期待！', 'info');
}

// 切换侧边栏
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

// AI助手功能选择
function askAI(topic) {
    const input = document.getElementById('chatInput');
    input.value = `请详细介绍${topic}的相关信息`;
    input.focus();
}

// 绑定事件
function bindEvents() {
    // 聊天区域滚动监听
    const chatArea = document.getElementById('chatArea');
    chatArea.addEventListener('scroll', () => {
        updateScrollButton();
    });
    
    // 输入框自适应高度
    const chatInput = document.getElementById('chatInput');
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
    
    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const sidebar = document.getElementById('sidebar');
            if (sidebar.classList.contains('open')) {
                toggleSidebar();
            }
        }
        
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            chatInput.focus();
        }
        
        if (e.ctrlKey && e.key === 'l') {
            e.preventDefault();
            clearChat();
        }
    });
    
    // 页面可见性变化
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            chatInput.focus();
        }
    });
}

// 返回首页
function goHome() {
    // 页面跳转动画
    document.body.style.transition = 'opacity 0.3s ease';
    document.body.style.opacity = '0.7';
    
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 300);
    }

// 生成对话ID
function generateConversationId() {
    return 'conv_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
}

// 显示通知
function showNotification(message, type = 'success') {
    // 移除已存在的通知
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const colors = {
        success: 'linear-gradient(135deg, #10b981, #059669)',
        error: 'linear-gradient(135deg, #ef4444, #dc2626)',
        info: 'linear-gradient(135deg, #3b82f6, #2563eb)',
        warning: 'linear-gradient(135deg, #f59e0b, #d97706)'
    };

    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        info: 'info-circle',
        warning: 'exclamation-triangle'
    };

    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${icons[type]}"></i>
            <span>${message}</span>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        z-index: 20000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        max-width: 350px;
        font-weight: 500;
    `;

    const contentStyle = `
        .notification-content {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .notification-content i {
            font-size: 18px;
        }
    `;

    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = contentStyle;
        document.head.appendChild(style);
    }

    document.body.appendChild(notification);

    // 显示动画
    requestAnimationFrame(() => {
        notification.style.transform = 'translateX(0)';
    });

    // 自动隐藏
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 4000);
}

// 自动获取焦点
window.addEventListener('load', function() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.focus();
    }
}); 