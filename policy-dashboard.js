// 政策看板页面交互脚本

// 全局变量
let policiesData = [];
let matchedPolicies = [];
let isLoading = false;

// 动态API配置
const getApiBaseUrl = () => {
    // 如果是GitHub Pages环境
    if (window.location.hostname.includes('github.io')) {
        return 'https://policy-pilot-viktorsdb.herokuapp.com/api/v1'; // 使用Heroku后端
    }
    // 本地开发环境
    return 'http://localhost:8001/api/v1';
};

const API_BASE_URL = getApiBaseUrl();

// DOM 就绪后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    bindEvents();
    loadCompanyData();
    loadPoliciesFromAPI();
    initializeStatCounters();
    addRefreshButton();
});

// 添加刷新数据按钮
function addRefreshButton() {
    const header = document.querySelector('.header-right');
    if (header) {
        const refreshBtn = document.createElement('button');
        refreshBtn.className = 'action-btn btn-refresh';
        refreshBtn.innerHTML = `
            <i class="fas fa-sync-alt"></i>
            同步爬取数据
        `;
        refreshBtn.onclick = refreshCrawledData;
        
        // 插入到第一个按钮之前
        header.insertBefore(refreshBtn, header.firstChild);
    }
}

// 刷新爬取的政策数据
async function refreshCrawledData() {
    try {
        const refreshBtn = document.querySelector('.btn-refresh');
        const originalContent = refreshBtn.innerHTML;
        
        // 显示加载状态
        refreshBtn.innerHTML = `
            <i class="fas fa-spinner fa-spin"></i>
            正在刷新...
        `;
        refreshBtn.disabled = true;
        
        // 显示全局加载状态
        showCrawlingProgress();
        
        // 调用刷新API
        const response = await fetch(`${API_BASE_URL}/crawler/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // 显示刷新成功的详细信息
            showRefreshSuccessNotification(result);
            
            // 更新统计信息
            if (result.data) {
                updateRefreshStatistics(result.data);
            }
            
            // 延迟重新加载政策数据，确保后端数据已更新
            setTimeout(async () => {
                await loadPoliciesFromAPI();
                hideCrawlingProgress();
            }, 1000);
            
            console.log('✅ 成功刷新爬取数据:', result);
        } else {
            const error = await response.json();
            hideCrawlingProgress();
            showNotification(error.detail || '刷新数据失败', 'error');
        }
        
    } catch (error) {
        console.error('刷新数据失败:', error);
        hideCrawlingProgress();
        showNotification('网络错误，无法刷新数据', 'error');
    } finally {
        // 恢复按钮状态
        const refreshBtn = document.querySelector('.btn-refresh');
        if (refreshBtn) {
            refreshBtn.innerHTML = originalContent;
            refreshBtn.disabled = false;
        }
    }
}

// 显示爬取进度提示
function showCrawlingProgress() {
    // 移除已存在的进度提示
    const existingProgress = document.querySelector('.crawling-progress');
    if (existingProgress) {
        existingProgress.remove();
    }
    
    const progressEl = document.createElement('div');
    progressEl.className = 'crawling-progress';
    progressEl.innerHTML = `
        <div class="progress-content">
            <div class="progress-icon">
                <i class="fas fa-spider fa-spin"></i>
            </div>
            <div class="progress-text">
                <h3>正在实时爬取最新政策数据...</h3>
                <p>请稍候，我们正在从各个政府网站获取最新的政策信息</p>
                <div class="progress-steps">
                    <div class="step active">
                        <i class="fas fa-search"></i>
                        <span>搜索政策网站</span>
                    </div>
                    <div class="step">
                        <i class="fas fa-download"></i>
                        <span>下载政策文件</span>
                    </div>
                    <div class="step">
                        <i class="fas fa-cogs"></i>
                        <span>处理数据</span>
                    </div>
                    <div class="step">
                        <i class="fas fa-check"></i>
                        <span>完成同步</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(progressEl);
    
    // 动画效果
    setTimeout(() => {
        progressEl.classList.add('show');
    }, 100);
    
    // 模拟进度步骤
    let currentStep = 0;
    const steps = progressEl.querySelectorAll('.step');
    const stepInterval = setInterval(() => {
        if (currentStep < steps.length - 1) {
            steps[currentStep].classList.remove('active');
            steps[currentStep].classList.add('completed');
            currentStep++;
            steps[currentStep].classList.add('active');
        }
    }, 2000);
    
    // 保存interval ID以便清理
    progressEl.stepInterval = stepInterval;
}

// 隐藏爬取进度提示
function hideCrawlingProgress() {
    const progressEl = document.querySelector('.crawling-progress');
    if (progressEl) {
        // 清理interval
        if (progressEl.stepInterval) {
            clearInterval(progressEl.stepInterval);
        }
        
        progressEl.classList.remove('show');
        setTimeout(() => {
            progressEl.remove();
        }, 300);
    }
}

// 显示刷新成功的详细通知
function showRefreshSuccessNotification(result) {
    const data = result.data;
    let message = result.message;
    
    if (data) {
        message += `\n\n📊 数据详情：`;
        message += `\n• 总政策数：${data.total_policies}条`;
        if (data.new_policies > 0) {
            message += `\n• 新增政策：${data.new_policies}条`;
        }
        message += `\n• 更新时间：${new Date(data.refresh_time).toLocaleString('zh-CN')}`;
        
        if (data.by_region) {
            message += `\n\n🏢 按地区分布：`;
            if (data.by_region.xuhui) message += `\n• 徐汇区：${data.by_region.xuhui}条`;
            if (data.by_region.shanghai) message += `\n• 上海市：${data.by_region.shanghai}条`;
            if (data.by_region.national) message += `\n• 全国：${data.by_region.national}条`;
        }
    }
    
    showNotification(message, 'success');
}

// 更新刷新统计信息
function updateRefreshStatistics(data) {
    // 更新页面上的统计卡片
    const statCards = document.querySelectorAll('.stat-card');
    
    // 更新可申请政策数量
    const policyCountCard = statCards[0];
    if (policyCountCard && data.total_policies) {
        const numberEl = policyCountCard.querySelector('.stat-number');
        if (numberEl) {
            animateNumber(numberEl, parseInt(numberEl.textContent.replace(/,/g, '')), data.total_policies);
        }
    }
    
    // 可以根据需要更新其他统计信息
    console.log('📊 统计信息已更新:', data);
}

// 数字动画效果
function animateNumber(element, from, to) {
    const duration = 1000;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.floor(from + (to - from) * progress);
        element.textContent = currentValue.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

// 初始化看板
function initializeDashboard() {
    // 页面载入动画
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.6s ease';
        document.body.style.opacity = '1';
    }, 100);
}

// 加载企业数据和匹配结果
function loadCompanyData() {
    try {
        const companyInfo = sessionStorage.getItem('companyInfo');
        const policyMatches = sessionStorage.getItem('policyMatches');
        
        if (companyInfo && policyMatches) {
            const company = JSON.parse(companyInfo);
            matchedPolicies = JSON.parse(policyMatches);
            
            // 更新页面标题显示企业名称
            updateCompanyInfo(company);
            
            // 显示匹配的政策
            displayMatchedPolicies(matchedPolicies);
        } else {
            // 如果没有企业数据，显示默认政策
            loadDefaultPolicies();
        }
    } catch (error) {
        console.error('加载企业数据失败:', error);
        loadDefaultPolicies();
    }
}

// 更新企业信息显示
function updateCompanyInfo(company) {
    const companyNameElement = document.querySelector('.dashboard-title');
    if (companyNameElement) {
        companyNameElement.textContent = `${company.company_name} - 政策匹配结果`;
    }
}

// 从后端API加载政策数据
async function loadPoliciesFromAPI() {
    try {
        isLoading = true;
        showLoadingState();
        
        // 获取政策统计信息
        const statsResponse = await fetch(`${API_BASE_URL}/policies/count`);
        if (statsResponse.ok) {
            const statsData = await statsResponse.json();
            updateStatistics(statsData.data);
        }
        
        // 检查是否有企业信息
        const companyInfo = sessionStorage.getItem('companyInfo');
        
        if (companyInfo) {
            // 有企业信息，调用匹配API
            await loadMatchedPolicies(JSON.parse(companyInfo));
        } else {
            // 没有企业信息，获取增强的政策列表
            await loadEnhancedPolicies();
        }
        
    } catch (error) {
        console.error('加载政策数据失败:', error);
        // 使用备用政策数据
        loadFallbackPolicies();
        showNotification('后端服务暂时不可用，显示备用政策数据', 'warning');
    } finally {
        isLoading = false;
        hideLoadingState();
    }
}

// 加载备用政策数据
function loadFallbackPolicies() {
    const fallbackPolicies = getFallbackPoliciesData();
    displayAllPolicies(fallbackPolicies);
    
    // 更新统计信息
    updateStatistics({
        total_policies: fallbackPolicies.length,
        active_policies: fallbackPolicies.length,
        by_region: {
            xuhui: fallbackPolicies.filter(p => p.region === '徐汇区').length,
            shanghai: fallbackPolicies.filter(p => p.region === '上海市').length,
            national: fallbackPolicies.filter(p => p.region === '全国').length
        },
        by_type: {
            grant: fallbackPolicies.filter(p => p.support_type === 'grant').length,
            subsidy: fallbackPolicies.filter(p => p.support_type === 'subsidy').length,
            tax: fallbackPolicies.filter(p => p.support_type === 'tax').length,
            voucher: fallbackPolicies.filter(p => p.support_type === 'voucher').length
        }
    });
}

// 获取备用政策数据
function getFallbackPoliciesData() {
    return [
        {
            policy_id: "XH2024001",
            policy_name: "徐汇区关于推动人工智能产业高质量发展的若干意见",
            region: "徐汇区",
            support_type: "subsidy",
            max_amount: 50000000,
            deadline: "2024-12-31",
            industry_tags: ["人工智能", "科技创新", "制造业"],
            source_url: "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab01934dd52e3d09b9",
            requirements: [
                "企业注册地在徐汇区",
                "从事人工智能相关业务",
                "企业信用状况良好",
                "符合国家产业政策"
            ],
            target_industries: ["ai", "tech"],
            target_scale: ["small", "medium", "large"],
            target_rd: ["medium", "high"],
            base_score: 0.85,
            match_score: 0.85,
            application_period: "全年申报",
            approval_department: "徐汇区新型工业化推进办公室",
            description: "支持人工智能领域创新主体开展关键技术攻关，最高可给予5000万元支持。",
            last_updated: "2024-11-21",
            recommendation: "该政策对AI企业支持力度大，建议符合条件的企业积极申报。"
        },
        {
            policy_id: "XH2024002",
            policy_name: "徐汇区关于推动具身智能产业发展的若干意见",
            region: "徐汇区",
            support_type: "subsidy",
            max_amount: 20000000,
            deadline: "2024-12-31",
            industry_tags: ["具身智能", "机器人", "智能制造"],
            source_url: "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab01934dd6cfbd09bb",
            requirements: [
                "企业注册地在徐汇区",
                "从事具身智能相关业务",
                "企业信用状况良好"
            ],
            target_industries: ["ai", "robotics", "manufacturing"],
            target_scale: ["small", "medium", "large"],
            target_rd: ["medium", "high"],
            base_score: 0.80,
            match_score: 0.80,
            application_period: "全年申报",
            approval_department: "徐汇区新型工业化推进办公室",
            description: "支持具身智能产业发展，对规模以上创新企业最高可给予2000万元经营奖励。",
            last_updated: "2024-11-21",
            recommendation: "适合机器人和智能制造企业申报，支持力度较大。"
        },
        {
            policy_id: "XH2024003",
            policy_name: "关于支持上海市生成式人工智能创新生态先导区的若干措施",
            region: "徐汇区",
            support_type: "subsidy",
            max_amount: 50000000,
            deadline: "2024-12-31",
            industry_tags: ["生成式AI", "大模型", "创新生态"],
            source_url: "https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab019384dc95a70aed",
            requirements: [
                "企业注册地在先导区",
                "从事生成式AI相关业务",
                "企业信用状况良好"
            ],
            target_industries: ["ai", "tech", "software"],
            target_scale: ["small", "medium", "large"],
            target_rd: ["high"],
            base_score: 0.90,
            match_score: 0.90,
            application_period: "全年申报",
            approval_department: "徐汇区新型工业化推进办公室",
            description: "支持生成式AI技术研发创新，最高可给予5000万元支持。",
            last_updated: "2024-12-02",
            recommendation: "针对大模型和生成式AI企业的重点政策，支持力度最大。"
        },
        {
            policy_id: "GJ2024001",
            policy_name: "国家高新技术企业认定管理办法",
            region: "全国",
            support_type: "tax",
            max_amount: 0,
            deadline: "2024-12-31",
            industry_tags: ["高新技术", "税收优惠", "企业认定"],
            source_url: "http://www.most.gov.cn/",
            requirements: [
                "成立一年以上",
                "拥有核心自主知识产权",
                "研发投入占比不低于规定标准",
                "高新技术产品收入占比60%以上"
            ],
            target_industries: ["ai", "tech", "biotech", "newenergy"],
            target_scale: ["small", "medium", "large"],
            target_rd: ["medium", "high"],
            base_score: 0.80,
            match_score: 0.80,
            application_period: "每年4-6月",
            approval_department: "科技部",
            description: "享受15%企业所得税优惠税率，是最重要的税收优惠政策之一。",
            last_updated: "2024-06-12",
            recommendation: "所有符合条件的科技企业都应该申报，税收优惠显著。"
        },
        {
            policy_id: "GJ2024002",
            policy_name: "中小企业发展专项资金管理办法",
            region: "全国",
            support_type: "grant",
            max_amount: 2000000,
            deadline: "2024-10-15",
            industry_tags: ["中小企业", "专精特新", "创新发展"],
            source_url: "http://www.miit.gov.cn/",
            requirements: [
                "符合中小企业标准",
                "具有自主知识产权",
                "属于专精特新领域",
                "具有良好发展前景"
            ],
            target_industries: ["tech", "manufacturing", "service"],
            target_scale: ["small", "medium"],
            target_rd: ["medium", "high"],
            base_score: 0.78,
            match_score: 0.78,
            application_period: "每年7-10月",
            approval_department: "工信部",
            description: "支持中小企业创新发展和转型升级，最高可获得200万元资金支持。",
            last_updated: "2024-06-12",
            recommendation: "专精特新中小企业的重要资金来源，建议积极申报。"
        },
        {
            policy_id: "SH2024001",
            policy_name: "上海市科技创新券实施办法",
            region: "上海市",
            support_type: "voucher",
            max_amount: 500000,
            deadline: "2024-12-31",
            industry_tags: ["科技创新", "创新券", "研发服务"],
            source_url: "http://stcsm.sh.gov.cn/",
            requirements: [
                "注册地在上海市",
                "符合中小微企业标准",
                "具有研发需求",
                "信用状况良好"
            ],
            target_industries: ["tech", "biotech", "newenergy"],
            target_scale: ["small", "medium"],
            target_rd: ["low", "medium"],
            base_score: 0.75,
            match_score: 0.75,
            application_period: "全年申报",
            approval_department: "上海市科委",
            description: "为中小微企业提供科技创新券，用于购买研发服务，最高50万元。",
            last_updated: "2024-06-12",
            recommendation: "门槛较低，适合初创企业和中小微企业申报。"
        }
    ];
}

// 加载匹配的政策（基于企业信息）
async function loadMatchedPolicies(companyInfo) {
    try {
        console.log('🔍 开始基于企业信息匹配政策...');
        
        // 构建企业档案数据
        const companyProfile = {
            company_name: companyInfo.company_name || '',
            registration_location: companyInfo.registration_location || companyInfo.region || '',
            industry_match: companyInfo.industry || companyInfo.industry_match || '',
            operating_status: companyInfo.operating_status || '正常经营',
            credit_status: companyInfo.credit_status || '信用良好',
            patents: parseInt(companyInfo.patents) || 0,
            company_scale: companyInfo.company_scale || companyInfo.scale || '',
            rd_investment: companyInfo.rd_investment || '中等研发投入',
            enterprise_certification: companyInfo.enterprise_certification || null
        };
        
        console.log('📋 企业档案:', companyProfile);
        
        // 调用政策匹配API
        const response = await fetch(`${API_BASE_URL}/policies/match`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(companyProfile)
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ 政策匹配成功:', data);
            
            if (data.success && data.data.matched_policies) {
                matchedPolicies = data.data.matched_policies;
                
                // 显示匹配结果
                displayMatchedPolicies(matchedPolicies);
                
                // 更新页面标题
                updateCompanyInfo(companyInfo);
                
                // 显示匹配统计
                showMatchStatistics(data.data);
                
                // 保存匹配结果到sessionStorage
                sessionStorage.setItem('policyMatches', JSON.stringify(matchedPolicies));
                
                showNotification(
                    `成功为 ${companyInfo.company_name} 匹配到 ${data.data.total_policies} 个政策机会！`, 
                    'success'
                );
            } else {
                throw new Error('匹配API返回格式错误');
            }
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || '政策匹配API调用失败');
        }
        
    } catch (error) {
        console.error('政策匹配失败:', error);
        showNotification('政策匹配失败，将显示默认政策列表', 'warning');
        
        // 如果匹配失败，使用备用政策数据
        loadFallbackPolicies();
    }
}

// 加载增强的政策列表（无企业信息时）
async function loadEnhancedPolicies() {
    try {
        console.log('📋 加载增强政策列表...');
        
        const response = await fetch(`${API_BASE_URL}/policies/enhanced`);
        if (response.ok) {
            const data = await response.json();
            
            if (data.success && data.data.policies) {
                // 转换为统一格式
                const policies = data.data.policies.map(policy => ({
                    ...policy,
                    match_score: policy.match_score || policy.base_score || 0.6,
                    recommendation: policy.recommendation || '请完善企业信息以获得更精准的匹配度评估。'
                }));
                
                displayAllPolicies(policies);
                showNotification('已显示推荐政策，完善企业信息可获得更精准匹配', 'info');
            } else {
                throw new Error('增强政策API返回格式错误');
            }
        } else {
            throw new Error('增强政策API调用失败');
        }
        
    } catch (error) {
        console.error('加载增强政策失败:', error);
        
        // 尝试加载基础政策列表
        try {
            const defaultResponse = await fetch(`${API_BASE_URL}/policies?limit=10`);
            if (defaultResponse.ok) {
                const defaultData = await defaultResponse.json();
                if (defaultData.success && defaultData.data.policies) {
                    displayAllPolicies(defaultData.data.policies);
                    showNotification('已显示基础政策列表', 'info');
                } else {
                    throw new Error('基础政策API返回格式错误');
                }
            } else {
                throw new Error('基础政策API调用失败');
            }
        } catch (fallbackError) {
            console.error('所有API调用都失败:', fallbackError);
            // 最终使用备用数据
            loadFallbackPolicies();
        }
    }
}

// 显示匹配的政策
function displayMatchedPolicies(matches) {
    const policiesContainer = document.querySelector('.policies-container');
    if (!policiesContainer) return;
    
    policiesContainer.innerHTML = '';
    
    if (matches.length === 0) {
        policiesContainer.innerHTML = `
            <div class="no-policies">
                <i class="fas fa-search"></i>
                <h3>暂未找到匹配的政策</h3>
                <p>请检查企业信息或联系客服</p>
            </div>
        `;
        return;
    }
    
    matches.forEach((policy, index) => {
        const policyCard = createPolicyCard(policy, index, true);
        policiesContainer.appendChild(policyCard);
    });
}

// 显示所有政策
function displayAllPolicies(policies) {
    const policiesContainer = document.querySelector('.policies-container');
    if (!policiesContainer) return;
    
    policiesContainer.innerHTML = '';
    
    if (!policies || policies.length === 0) {
        policiesContainer.innerHTML = `
            <div class="no-policies">
                <i class="fas fa-search"></i>
                <h3>暂无政策数据</h3>
                <p>请稍后重试或联系客服</p>
            </div>
        `;
        return;
    }
    
    policies.forEach((policy, index) => {
        // 确保每个政策都有匹配度信息
        const enhancedPolicy = {
            ...policy,
            match_score: policy.match_score || policy.base_score || 0.6,
            recommendation: policy.recommendation || '完善企业信息可获得更精准的政策匹配建议。'
        };
        
        const policyCard = createPolicyCard(enhancedPolicy, index, !!enhancedPolicy.match_score);
        policiesContainer.appendChild(policyCard);
    });
}

// 创建政策卡片
function createPolicyCard(policy, index, isMatched = false) {
    const card = document.createElement('div');
    card.className = 'policy-card';
    card.setAttribute('data-policy-id', policy.policy_id || policy.id);
    
    // 根据支持类型设置图标和颜色
    const typeConfig = {
        'grant': { icon: 'fas fa-gift', color: '#10b981', label: '无偿资助', class: 'grant' },
        'subsidy': { icon: 'fas fa-hand-holding-usd', color: '#f59e0b', label: '补贴', class: 'subsidy' },
        'loan': { icon: 'fas fa-university', color: '#3b82f6', label: '贷款贴息', class: 'loan' },
        'tax': { icon: 'fas fa-percent', color: '#8b5cf6', label: '税收优惠', class: 'tax' },
        'voucher': { icon: 'fas fa-ticket-alt', color: '#06b6d4', label: '创新券', class: 'voucher' },
        'other': { icon: 'fas fa-star', color: '#6b7280', label: '其他支持', class: 'other' }
    };
    
    const config = typeConfig[policy.support_type] || typeConfig['other'];
    const matchScore = isMatched ? policy.match_score : null;
    const maxAmount = policy.max_amount ? formatAmount(policy.max_amount) : '未限定';
    
    // 使用发布时间而不是申请截止时间
    const publishDate = policy.publish_date || policy.publish_time || policy.created_at;
    const formattedPublishDate = publishDate ? formatDate(publishDate) : '未知时间';
    
    // 判断是否为最新爬取的数据
    const isNewData = policy.last_updated && 
                     new Date(policy.last_updated) > new Date(new Date().setDate(new Date().getDate() - 1));
    
    // 生成标签列表
    const industryTags = policy.industry_tags || [];
    const tagsHtml = industryTags.slice(0, 3).map(tag => 
        `<span class="policy-tag">${tag}</span>`
    ).join('');
    
    // 判断政策优先级（基于金额和匹配度）
    const isHighPriority = (policy.max_amount > 2000000) || (matchScore && matchScore > 0.8);
    
    // 判断发布时间是否为最近发布（30天内）
    const isRecentlyPublished = publishDate && 
                               new Date(publishDate) > new Date(new Date().setDate(new Date().getDate() - 30));
    
    card.innerHTML = `
        <div class="policy-header">
            <div class="policy-type ${config.class}">
                <i class="${config.icon}"></i>
                <span>${config.label}</span>
            </div>
            <div class="policy-header-right">
                ${isNewData ? `
                    <div class="new-badge" title="最新爬取数据">
                        <i class="fas fa-sparkles"></i>
                        <span>最新</span>
                    </div>
                ` : ''}
                ${isRecentlyPublished ? `
                    <div class="recent-badge" title="近期发布">
                        <i class="fas fa-clock"></i>
                        <span>新发布</span>
                    </div>
                ` : ''}
                ${isHighPriority ? `
                    <div class="priority-badge" title="优先推荐">
                        <i class="fas fa-star"></i>
                    </div>
                ` : ''}
                ${isMatched ? `
                    <div class="match-score" title="匹配度评分">
                        <i class="fas fa-chart-line"></i>
                        <span>${Math.round(matchScore * 100)}%</span>
                    </div>
                ` : ''}
                <button class="ask-ai-btn" onclick="askAIAboutPolicy(event, '${policy.policy_id || policy.id}')" title="询问AI关于此政策">
                    <i class="fas fa-robot"></i>
                </button>
            </div>
        </div>
        
        <h3 class="policy-title">${policy.policy_name}</h3>
        
        <div class="policy-info">
            <div class="info-row">
                <div class="info-item">
                    <i class="fas fa-map-marker-alt"></i>
                    <span class="info-label">适用地区</span>
                    <span class="info-value">${policy.region}</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-coins"></i>
                    <span class="info-label">最高金额</span>
                    <span class="info-value amount">${maxAmount}</span>
                </div>
            </div>
            
            <div class="info-row">
                <div class="info-item">
                    <i class="fas fa-calendar-check"></i>
                    <span class="info-label">发布时间</span>
                    <span class="info-value ${isRecentlyPublished ? 'recent-publish' : ''}">${formattedPublishDate}</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-building"></i>
                    <span class="info-label">审批部门</span>
                    <span class="info-value">${policy.approval_department || policy.department || '相关部门'}</span>
                </div>
            </div>
        </div>
        
        ${tagsHtml ? `
            <div class="policy-tags">
                ${tagsHtml}
                ${industryTags.length > 3 ? `<span class="more-tags">+${industryTags.length - 3}</span>` : ''}
            </div>
        ` : ''}
        
        ${policy.description ? `
            <div class="policy-description">
                <p>${truncateText(policy.description, 120)}</p>
            </div>
        ` : ''}
        
        ${isMatched && policy.recommendation ? `
            <div class="match-recommendation">
                <div class="recommendation-header">
                    <i class="fas fa-lightbulb"></i>
                    <span>AI建议</span>
                </div>
                <p class="recommendation-text">${truncateText(policy.recommendation, 100)}</p>
            </div>
        ` : ''}
        
        <div class="policy-actions">
            <button class="action-btn secondary" onclick="showPolicyDetail('${policy.policy_id || policy.id}')">
                <i class="fas fa-info-circle"></i>
                查看详情
            </button>
            ${policy.source_url ? `
                <button class="action-btn primary" onclick="openPolicyLink('${policy.source_url}')">
                    <i class="fas fa-external-link-alt"></i>
                    官方原文
                </button>
            ` : ''}
            <button class="action-btn ai-consult" onclick="consultAI('${policy.policy_name}')">
                <i class="fas fa-comments"></i>
                AI咨询
            </button>
        </div>
        
        ${policy.last_updated ? `
            <div class="policy-footer">
                <div class="update-time">
                    <i class="fas fa-sync-alt"></i>
                    <span>数据更新于 ${formatUpdateTime(policy.last_updated)}</span>
                </div>
                ${policy.source_url ? `
                    <div class="data-source">
                        <i class="fas fa-link"></i>
                        <span>数据来源：政府官网</span>
                    </div>
                ` : ''}
            </div>
        ` : ''}
    `;
    
    // 添加动画效果
    card.style.animationDelay = `${index * 0.1}s`;
    
    return card;
}

// 截断文本函数
function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// 格式化更新时间
function formatUpdateTime(timestamp) {
    try {
        const date = new Date(timestamp);
        const now = new Date();
        const diffHours = Math.floor((now - date) / (1000 * 60 * 60));
        
        if (diffHours < 1) {
            return '刚刚';
        } else if (diffHours < 24) {
            return `${diffHours}小时前`;
        } else if (diffHours < 48) {
            return '昨天';
        } else {
            return date.toLocaleDateString('zh-CN');
        }
    } catch {
        return timestamp;
    }
}

// 跳转到AI咨询页面
function jumpToAIConsult() {
    // 页面跳转动画
    document.body.style.transition = 'opacity 0.3s ease';
    document.body.style.opacity = '0.7';
    
    setTimeout(() => {
        window.location.href = 'ai-chat.html';
    }, 300);
}

// 显示政策详情
async function showPolicyDetail(policyId) {
    try {
        // 从匹配结果中查找政策
        let policy = matchedPolicies.find(p => (p.policy_id || p.id) === policyId);
        
        // 如果没找到，从API获取
        if (!policy) {
            const response = await fetch(`${API_BASE_URL}/policies/${policyId}`);
            if (response.ok) {
                const data = await response.json();
                policy = data.data;
            }
        }
        
        if (!policy) {
            showNotification('未找到政策详情', 'error');
            return;
        }
        
        const modal = createPolicyModal(policy);
        document.body.appendChild(modal);
        
        // 显示动画
        requestAnimationFrame(() => {
            modal.style.opacity = '1';
            modal.querySelector('.modal-content').style.transform = 'scale(1)';
        });
        
    } catch (error) {
        console.error('获取政策详情失败:', error);
        showNotification('获取政策详情失败', 'error');
    }
}

// 创建政策详情模态框
function createPolicyModal(policy) {
    const modal = document.createElement('div');
    modal.className = 'policy-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(10px);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    const matchScore = policy.match_score ? Math.round(policy.match_score * 100) : null;
    const maxAmount = policy.max_amount ? formatAmount(policy.max_amount) : '未限定';
    
    modal.innerHTML = `
        <div class="modal-content" style="
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 700px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
            transform: scale(0.9);
            transition: transform 0.3s ease;
        ">
            <div class="modal-header" style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
                <h2 style="color: #1f2937; font-size: 1.75rem; font-weight: 700; margin: 0; line-height: 1.2;">${policy.policy_name}</h2>
                <button class="modal-close" onclick="closeModal()" style="
                    background: transparent;
                    border: none;
                    font-size: 24px;
                    color: #6b7280;
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 8px;
                    transition: all 0.2s ease;
                ">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="modal-body">
                ${matchScore ? `
                    <div class="match-rate" style="
                        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1));
                        padding: 16px;
                        border-radius: 12px;
                        margin-bottom: 24px;
                        border-left: 4px solid #10b981;
                    ">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                            <i class="fas fa-chart-line" style="color: #10b981;"></i>
                            <span style="font-weight: 600; color: #1f2937;">匹配度评估</span>
                        </div>
                        <div style="font-size: 2rem; font-weight: 800; color: #10b981;">${matchScore}%</div>
                        <div style="font-size: 0.875rem; color: #6b7280;">基于您的企业信息分析</div>
                    </div>
                ` : ''}
                
                <div class="policy-basic-info" style="
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 16px;
                    margin-bottom: 24px;
                ">
                    <div class="info-card" style="padding: 16px; background: #f8fafc; border-radius: 12px;">
                        <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 4px;">适用地区</div>
                        <div style="color: #1f2937; font-weight: 600;">${policy.region || '未指定'}</div>
                    </div>
                    <div class="info-card" style="padding: 16px; background: #f8fafc; border-radius: 12px;">
                        <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 4px;">最高金额</div>
                        <div style="color: #1f2937; font-weight: 600;">${maxAmount}</div>
                    </div>
                    <div class="info-card" style="padding: 16px; background: #f8fafc; border-radius: 12px;">
                        <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 4px;">发布时间</div>
                        <div style="color: #1f2937; font-weight: 600;">${policy.publish_date ? formatDate(policy.publish_date) : '未知时间'}</div>
                    </div>
                </div>
                
                ${policy.industry_tags && policy.industry_tags.length > 0 ? `
                    <div class="policy-section" style="margin-bottom: 24px;">
                        <h3 style="color: #1f2937; font-size: 1.125rem; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-tags" style="color: #f59e0b;"></i>
                            适用行业
                        </h3>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            ${policy.industry_tags.map(tag => `
                                <span style="
                                    background: linear-gradient(135deg, #3b82f6, #2563eb);
                                    color: white;
                                    padding: 6px 12px;
                                    border-radius: 20px;
                                    font-size: 0.875rem;
                                    font-weight: 500;
                                ">${tag}</span>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${policy.matched_requirements && policy.matched_requirements.length > 0 ? `
                    <div class="policy-section" style="margin-bottom: 24px;">
                        <h3 style="color: #1f2937; font-size: 1.125rem; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-check-circle" style="color: #10b981;"></i>
                            符合条件
                        </h3>
                        <ul style="list-style: none; padding: 0;">
                            ${policy.matched_requirements.map(req => `
                                <li style="
                                    padding: 8px 0;
                                    color: #374151;
                                    display: flex;
                                    align-items: center;
                                    gap: 8px;
                                ">
                                    <i class="fas fa-check" style="color: #10b981; font-size: 14px;"></i>
                                    ${req}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${policy.missing_requirements && policy.missing_requirements.length > 0 ? `
                    <div class="policy-section" style="margin-bottom: 24px;">
                        <h3 style="color: #1f2937; font-size: 1.125rem; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-exclamation-triangle" style="color: #f59e0b;"></i>
                            需要完善
                        </h3>
                        <ul style="list-style: none; padding: 0;">
                            ${policy.missing_requirements.map(req => `
                                <li style="
                                    padding: 8px 0;
                                    color: #374151;
                                    display: flex;
                                    align-items: center;
                                    gap: 8px;
                                ">
                                    <i class="fas fa-exclamation-circle" style="color: #f59e0b; font-size: 14px;"></i>
                                    ${req}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${policy.requirements && policy.requirements.length > 0 ? `
                    <div class="policy-section" style="margin-bottom: 24px;">
                        <h3 style="color: #1f2937; font-size: 1.125rem; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-clipboard-check" style="color: #8b5cf6;"></i>
                            申请条件
                        </h3>
                        <ul style="list-style: none; padding: 0;">
                            ${policy.requirements.map(req => `
                                <li style="
                                    padding: 8px 0;
                                    color: #374151;
                                    display: flex;
                                    align-items: center;
                                    gap: 8px;
                                ">
                                    <i class="fas fa-dot-circle" style="color: #8b5cf6; font-size: 14px;"></i>
                                    ${req}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${policy.recommendation ? `
                    <div class="policy-section" style="margin-bottom: 24px;">
                        <h3 style="color: #1f2937; font-size: 1.125rem; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                            <i class="fas fa-lightbulb" style="color: #f59e0b;"></i>
                            AI推荐建议
                        </h3>
                        <div style="
                            background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(245, 158, 11, 0.1));
                            padding: 16px;
                            border-radius: 12px;
                            border-left: 4px solid #f59e0b;
                            color: #374151;
                            line-height: 1.6;
                        ">
                            ${policy.recommendation}
                        </div>
                    </div>
                ` : ''}
                
                <div class="modal-actions" style="
                    display: flex;
                    gap: 12px;
                    margin-top: 32px;
                    padding-top: 24px;
                    border-top: 1px solid #e5e7eb;
                ">
                    <button onclick="openPolicyLink('${policy.source_url}')" style="
                        flex: 1;
                        background: linear-gradient(135deg, #3b82f6, #2563eb);
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 12px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.2s ease;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 8px;
                    ">
                        <i class="fas fa-external-link-alt"></i>
                        查看政策原文
                    </button>
                    <button onclick="consultAI('${policy.policy_name}')" style="
                        flex: 1;
                        background: linear-gradient(135deg, #10b981, #059669);
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 12px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.2s ease;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 8px;
                    ">
                        <i class="fas fa-robot"></i>
                        AI智能咨询
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // 点击模态框外部关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    return modal;
}

// 格式化金额
function formatAmount(amount) {
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

// 打开政策链接
function openPolicyLink(url) {
    if (url) {
        window.open(url, '_blank');
    } else {
        showNotification('政策链接不可用', 'warning');
    }
}

// 更新统计数据
function updateStatistics(stats) {
    const elements = {
        totalPolicies: document.querySelector('.stat-number[data-target="1247"]'),
        activePolicies: document.querySelector('.stat-number[data-target="100"]'),
        matchedPolicies: document.querySelector('.stat-number[data-target="127"]')
    };
    
    if (elements.totalPolicies) {
        elements.totalPolicies.setAttribute('data-target', stats.total_policies || 0);
        elements.totalPolicies.textContent = stats.total_policies || 0;
    }
    
    if (elements.activePolicies) {
        elements.activePolicies.setAttribute('data-target', stats.active_policies || 0);
        elements.activePolicies.textContent = stats.active_policies || 0;
    }
    
    if (elements.matchedPolicies && matchedPolicies.length > 0) {
        elements.matchedPolicies.setAttribute('data-target', matchedPolicies.length);
        elements.matchedPolicies.textContent = matchedPolicies.length;
    }
}

// 显示加载状态
function showLoadingState() {
    const container = document.querySelector('.policies-container');
    if (container) {
        container.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <p>正在加载政策数据...</p>
            </div>
        `;
    }
}

// 隐藏加载状态
function hideLoadingState() {
    // 加载完成后会被实际内容替换
}

// 显示错误状态
function showErrorState() {
    const container = document.querySelector('.policies-container');
    if (container) {
        container.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>加载失败</h3>
                <p>请检查网络连接或稍后重试</p>
                <button onclick="loadPoliciesFromAPI()" class="retry-btn">重试</button>
            </div>
        `;
    }
}

// 加载默认政策（备用方案）
function loadDefaultPolicies() {
    const defaultPolicies = [
        {
            policy_id: 'default_001',
            policy_name: '徐汇区AI产业发展扶持资金',
            region: '徐汇区',
            support_type: 'grant',
            max_amount: 1000000,
            deadline: '2024-12-31',
            industry_tags: ['AI', '科技'],
            source_url: 'https://www.xuhui.gov.cn',
            requirements: ['企业注册地在徐汇区', 'AI相关业务占比>50%', '年营收>100万元'],
            recommendation: '您的企业符合AI产业发展要求，建议重点准备技术专利和营收证明材料。'
        },
        {
            policy_id: 'default_002',
            policy_name: '上海市科技型中小企业技术创新资金',
            region: '上海市',
            support_type: 'subsidy',
            max_amount: 500000,
            deadline: '2024-10-30',
            industry_tags: ['科技', '创新'],
            source_url: 'https://jxw.sh.gov.cn',
            requirements: ['中小企业认定', '研发投入占比>3%', '拥有自主知识产权'],
            recommendation: '该政策适合技术创新型企业，您需要提供研发投入证明和专利材料。'
        },
        {
            policy_id: 'default_003',
            policy_name: '高新技术企业认定税收优惠',
            region: '全国',
            support_type: 'tax',
            max_amount: 2000000,
            deadline: '2024-09-30',
            industry_tags: ['高新技术', '研发'],
            source_url: 'https://www.most.gov.cn',
            requirements: ['成立满一年', '研发费用占比达标', '高新技术产品收入占比>60%'],
            recommendation: '高新技术企业认定可享受15%所得税优惠，建议尽早申请。'
        },
        {
            policy_id: 'default_004',
            policy_name: '中小企业融资担保贷款贴息',
            region: '上海市',
            support_type: 'loan',
            max_amount: 3000000,
            deadline: '2024-11-15',
            industry_tags: ['制造业', '服务业'],
            source_url: 'https://www.shanghai.gov.cn',
            requirements: ['中小企业认定', '信用记录良好', '有固定资产抵押'],
            recommendation: '该贷款政策利率优惠，适合有资金需求的成长期企业。'
        }
    ];
    
    displayAllPolicies(defaultPolicies);
}

// 关闭模态框
function closeModal() {
    const modal = document.querySelector('.policy-modal');
    if (modal) {
        modal.style.opacity = '0';
        modal.querySelector('.modal-content').style.transform = 'scale(0.9)';
        
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

// 刷新政策数据
function refreshPolicies() {
    if (isLoading) return;
    
    isLoading = true;
    const btn = event.target.closest('.action-btn');
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 刷新中...';
    btn.disabled = true;
    
    // 模拟数据刷新
    setTimeout(() => {
        loadPoliciesFromAPI();
        btn.innerHTML = originalText;
        btn.disabled = false;
        isLoading = false;
        
        showNotification('政策数据已更新', 'success');
    }, 2000);
}

// 打开AI咨询
function openAIConsult() {
    // 页面跳转动画
    document.body.style.transition = 'opacity 0.3s ease';
    document.body.style.opacity = '0.7';
    
    setTimeout(() => {
        window.location.href = 'ai-chat.html';
    }, 300);
}

// AI咨询特定政策
function consultAI(policyTitle) {
    closeModal();
    
    // 保存咨询主题到session storage
    sessionStorage.setItem('aiConsultTopic', policyTitle);
    
    setTimeout(() => {
        openAIConsult();
    }, 300);
}

// 处理聊天输入
function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendToAI();
    }
}

// 发送消息给AI
function sendToAI() {
    const input = document.getElementById('aiChatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    input.value = '';
    
    // 简单的AI回复模拟
    const responses = [
        '我正在为您查询相关政策信息，请稍候...',
        '根据您的问题，我建议您关注以下几个方面...',
        '这个政策确实很适合您的企业类型，让我为您详细解释...',
        '您可以准备以下材料来提高申请成功率...'
    ];
    
    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    
    setTimeout(() => {
        showNotification(`AI助手: ${randomResponse}`, 'info');
    }, 1000);
}

// 快速AI提问
function askAI(question) {
    showNotification(`正在为您查询: ${question}`, 'info');
    
    setTimeout(() => {
        openAIConsult();
    }, 1500);
}

// 初始化统计数据计数动画
function initializeStatCounters() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                animateCounter(entry.target);
                entry.target.dataset.animated = 'true';
            }
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(counter => {
        observer.observe(counter);
    });
}

// 数字计数动画
function animateCounter(element) {
    const target = element.textContent;
    const isPercentage = target.includes('%');
    const hasPlus = target.includes('+');
    const numericValue = parseInt(target.replace(/[^\d]/g, ''));
    
    let current = 0;
    const increment = numericValue / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= numericValue) {
            current = numericValue;
            clearInterval(timer);
        }
        
        let displayValue = Math.floor(current).toLocaleString();
        if (isPercentage) displayValue += '%';
        if (hasPlus) displayValue += '+';
        
        element.textContent = target.includes('h') ? Math.floor(current) + 'h' : displayValue;
    }, 30);
}

// 绑定事件
function bindEvents() {
    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
        
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            refreshPolicies();
        }
        
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            openAIConsult();
        }
    });
    
    // 滚动动画
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
            }
        });
    }, observerOptions);

    // 观察需要动画的元素
    const animatedElements = document.querySelectorAll('.policy-card, .stat-card, .ai-card');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        observer.observe(el);
    });
    
    // 添加动画样式
    if (!document.querySelector('#animation-styles')) {
        const style = document.createElement('style');
        style.id = 'animation-styles';
        style.textContent = `
            @keyframes fadeInUp {
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    }
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

// 询问AI关于特定政策
async function askAIAboutPolicy(event, policyId) {
    // 阻止事件冒泡，避免触发卡片点击事件
    event.stopPropagation();
    
    try {
        // 查找政策信息
        let targetPolicy = null;
        
        // 首先从匹配的政策中查找
        if (matchedPolicies.length > 0) {
            targetPolicy = matchedPolicies.find(p => (p.policy_id || p.id) === policyId);
        }
        
        // 如果没找到，从API获取政策信息
        if (!targetPolicy) {
            const response = await fetch(`${API_BASE_URL}/policies`);
            if (response.ok) {
                const data = await response.json();
                targetPolicy = data.data.policies.find(p => (p.policy_id || p.id) === policyId);
            }
        }
        
        if (!targetPolicy) {
            showNotification('未找到政策信息', 'error');
            return;
        }
        
        // 保存政策信息到sessionStorage，供AI聊天页面使用
        sessionStorage.setItem('consultPolicy', JSON.stringify(targetPolicy));
        sessionStorage.setItem('policyConsultMode', 'true');
        
        // 添加视觉反馈
        const button = event.target.closest('.ask-ai-btn');
        const originalContent = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        button.disabled = true;
        
        // 显示准备消息
        showNotification(`正在为您准备关于"${targetPolicy.policy_name}"的AI咨询...`, 'info');
        
        // 延迟跳转，让用户看到反馈
        setTimeout(() => {
            // 页面跳转动画
            document.body.style.transition = 'opacity 0.3s ease';
            document.body.style.opacity = '0.7';
            
            setTimeout(() => {
                window.location.href = 'ai-chat.html';
            }, 300);
        }, 1500);
        
    } catch (error) {
        console.error('询问AI失败:', error);
        showNotification('AI咨询功能暂时不可用', 'error');
        
        // 恢复按钮状态
        const button = event.target.closest('.ask-ai-btn');
        button.innerHTML = '<i class="fas fa-robot"></i>';
        button.disabled = false;
    }
}

// 显示匹配统计信息
function showMatchStatistics(matchData) {
    const { high_match_count, medium_match_count, low_match_count, total_policies } = matchData;
    
    // 创建匹配统计提示
    const matchStatsHtml = `
        <div class="match-statistics">
            <div class="match-stats-header">
                <i class="fas fa-chart-pie"></i>
                <span>政策匹配统计</span>
            </div>
            <div class="match-stats-grid">
                <div class="match-stat-item high">
                    <span class="count">${high_match_count}</span>
                    <span class="label">高匹配</span>
                </div>
                <div class="match-stat-item medium">
                    <span class="count">${medium_match_count}</span>
                    <span class="label">中匹配</span>
                </div>
                <div class="match-stat-item low">
                    <span class="count">${low_match_count}</span>
                    <span class="label">低匹配</span>
                </div>
            </div>
        </div>
    `;
    
    // 插入到页面标题下方
    const pageHeader = document.querySelector('.page-header');
    if (pageHeader) {
        const existingStats = document.querySelector('.match-statistics');
        if (existingStats) {
            existingStats.remove();
        }
        
        pageHeader.insertAdjacentHTML('afterend', matchStatsHtml);
    }
} 