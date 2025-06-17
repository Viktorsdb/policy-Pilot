// PolicyPilot 主页交互脚本

// 全局变量
let isAnimating = false;
let isMenuOpen = false;

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
    initializeAnimations();
    initializeCounters();
    initializeInteractions();
    initializePage();
    bindEvents();
    checkBackendStatus();
});

// 初始化动画效果
function initializeAnimations() {
    // 添加页面载入动画
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.6s ease';
        document.body.style.opacity = '1';
    }, 100);

    // 初始化滚动动画
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
    const animatedElements = document.querySelectorAll('.feature-card, .stat-card, .hero-badge');
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
            
            @keyframes countUp {
                from { transform: scale(0.5); opacity: 0; }
                to { transform: scale(1); opacity: 1; }
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            .animate-pulse {
                animation: pulse 2s infinite;
            }
        `;
        document.head.appendChild(style);
    }
}

// 初始化计数器动画
function initializeCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                animateCounter(entry.target);
                entry.target.dataset.animated = 'true';
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => {
        counterObserver.observe(counter);
    });
}

// 数字计数动画
function animateCounter(element) {
    const target = element.textContent;
    const isPercentage = target.includes('%');
    const numericValue = parseInt(target.replace(/[^\d]/g, ''));
    
    element.style.animation = 'countUp 0.6s ease';
    
    let current = 0;
    const increment = numericValue / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= numericValue) {
            current = numericValue;
            clearInterval(timer);
        }
        
        element.textContent = isPercentage ? 
            Math.floor(current) + '%' : 
            Math.floor(current).toLocaleString();
    }, 30);
}

// 初始化交互功能
function initializeInteractions() {
    // CTA按钮点击事件
    const ctaBtn = document.querySelector('.cta-btn');
    if (ctaBtn) {
        ctaBtn.addEventListener('click', handleCtaClick);
    }

    // 特性卡片悬停效果
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(-4px) scale(1)';
        });
    });

    // 统计卡片点击效果
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('click', () => {
            card.classList.add('animate-pulse');
            setTimeout(() => {
                card.classList.remove('animate-pulse');
            }, 2000);
            
            showStatDetail(card);
        });
    });

    // 工具按钮功能
    const toolBtn = document.querySelector('.tool-btn');
    if (toolBtn) {
        toolBtn.addEventListener('click', showToolMenu);
    }
}

// 处理CTA按钮点击
function handleCtaClick() {
    if (isAnimating) return;
    
    isAnimating = true;
    const btn = document.querySelector('.cta-btn');
    
    // 按钮动画
    btn.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        btn.style.transform = '';
        showPageSelectionMenu();
        isAnimating = false;
    }, 150);
}

// 显示页面选择菜单
function showPageSelectionMenu() {
    // 移除已存在的菜单
    const existingMenu = document.querySelector('.page-selection-menu');
    if (existingMenu) {
        existingMenu.remove();
    }

    // 创建菜单元素
    const menu = document.createElement('div');
    menu.className = 'page-selection-menu';
    menu.innerHTML = `
        <div class="menu-overlay" onclick="closePageSelectionMenu()"></div>
        <div class="menu-content">
            <h3 class="menu-title">选择功能模块</h3>
            <div class="menu-options">
                <button class="menu-option" onclick="goToPage('company-info.html')">
                    <div class="option-icon">
                        <i class="fas fa-building"></i>
                    </div>
                    <div class="option-text">
                        <div class="option-title">企业信息管理</div>
                        <div class="option-desc">填写和管理企业基本信息</div>
                    </div>
                </button>
                <button class="menu-option" onclick="goToPage('policy-dashboard.html')">
                    <div class="option-icon">
                        <i class="fas fa-chart-bar"></i>
                    </div>
                    <div class="option-text">
                        <div class="option-title">政策数据看板</div>
                        <div class="option-desc">查看政策分析和统计数据</div>
                    </div>
                </button>
                <button class="menu-option" onclick="goToPage('ai-chat.html')">
                    <div class="option-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="option-text">
                        <div class="option-title">AI智能咨询</div>
                        <div class="option-desc">智能政策匹配和咨询服务</div>
                    </div>
                </button>
            </div>
            <button class="menu-close" onclick="closePageSelectionMenu()">
                <i class="fas fa-times"></i> 取消
            </button>
        </div>
    `;

    // 添加样式
    addMenuStyles();
    
    // 添加到页面
    document.body.appendChild(menu);
    
    // 添加显示动画
    requestAnimationFrame(() => {
        menu.style.opacity = '1';
        menu.querySelector('.menu-content').style.transform = 'scale(1)';
    });
}

// 添加菜单样式
function addMenuStyles() {
    if (document.querySelector('#menu-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'menu-styles';
    style.textContent = `
        .page-selection-menu {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .menu-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(10px);
        }
        
        .menu-content {
            position: relative;
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 450px;
            width: 90%;
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
            transform: scale(0.9);
            transition: transform 0.3s ease;
        }
        
        .menu-title {
            font-size: 1.75rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
            color: #1f2937;
            background: linear-gradient(135deg, #ec4899, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .menu-options {
            display: flex;
            flex-direction: column;
            gap: 16px;
            margin-bottom: 30px;
        }
        
        .menu-option {
            display: flex;
            align-items: center;
            gap: 20px;
            padding: 20px;
            border: 2px solid #e5e7eb;
            border-radius: 16px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: left;
        }
        
        .menu-option:hover {
            border-color: #ec4899;
            background: linear-gradient(135deg, rgba(236, 72, 153, 0.05), rgba(139, 92, 246, 0.05));
            transform: translateY(-2px);
            box-shadow: 0 12px 30px rgba(236, 72, 153, 0.2);
        }
        
        .option-icon {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #ec4899, #8b5cf6);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
        }
        
        .option-text {
            flex: 1;
        }
        
        .option-title {
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 6px;
            font-size: 1.1rem;
        }
        
        .option-desc {
            font-size: 0.95rem;
            color: #6b7280;
            line-height: 1.4;
        }
        
        .menu-close {
            width: 100%;
            padding: 16px;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            background: white;
            color: #6b7280;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .menu-close:hover {
            background: #f8fafc;
            border-color: #d1d5db;
            color: #374151;
        }
    `;
    document.head.appendChild(style);
}

// 关闭页面选择菜单
function closePageSelectionMenu() {
    const menu = document.querySelector('.page-selection-menu');
    if (menu) {
        menu.style.opacity = '0';
        menu.querySelector('.menu-content').style.transform = 'scale(0.9)';
        
        setTimeout(() => {
            menu.remove();
        }, 300);
    }
}

// 跳转到页面
function goToPage(page) {
    closePageSelectionMenu();
    
    // 添加页面跳转动画
    document.body.style.transition = 'opacity 0.3s ease';
    document.body.style.opacity = '0.7';
    
    setTimeout(() => {
        window.location.href = page;
    }, 300);
}

// 显示统计详情
function showStatDetail(card) {
    const number = card.querySelector('.stat-number').textContent;
    const label = card.querySelector('.stat-label').textContent;
    
    let detail = '';
    switch(label) {
        case '政策案例':
            detail = '涵盖各行业政策案例，持续更新中';
            break;
        case '匹配精度':
            detail = 'AI算法精准匹配，智能推荐最适合的政策';
            break;
        case '关于项目':
            detail = '已完成项目案例，成功率保障';
            break;
    }
    
    showNotification(`${label}: ${number} - ${detail}`, 'info');
}

// 显示工具菜单
function showToolMenu() {
    showNotification('工具菜单功能即将上线，敬请期待！', 'info');
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

    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 
                              type === 'error' ? 'exclamation-circle' : 
                              type === 'warning' ? 'exclamation-triangle' : 
                              'info-circle'}"></i>
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

// 页面滚动效果
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = 'none';
    }
});

// 键盘快捷键
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closePageSelectionMenu();
    }
    
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        handleCtaClick();
    }
}); 

// 检查后端服务状态 - 支持多后端尝试
async function checkBackendStatus() {
    console.log('🔍 检查后端服务状态...');
    
    // 尝试所有可用的后端服务
    for (let i = 0; i < BACKUP_API_URLS.length; i++) {
        const apiUrl = BACKUP_API_URLS[i];
        try {
            console.log(`🔗 尝试连接: ${apiUrl}`);
            
            const response = await fetch(`${apiUrl}/health`, {
                method: 'GET',
                timeout: 8000 // 8秒超时
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ 后端服务正常 (${apiUrl}):`, data);
                
                // 更新全局API地址为可用的地址
                window.CURRENT_API_URL = apiUrl;
                
                hideBackendStatusBanner();
                showBackendStatusBanner('success', `后端服务已连接: ${apiUrl.includes('render') ? 'Render' : 'Heroku'}`);
                
                // 3秒后隐藏成功提示
                setTimeout(hideBackendStatusBanner, 3000);
                return; // 成功连接，退出函数
            } else {
                console.log(`❌ 后端服务异常 (${apiUrl}):`, response.status);
            }
        } catch (error) {
            console.log(`❌ 后端服务连接失败 (${apiUrl}):`, error);
        }
    }
    
    // 所有后端都不可用
    console.log('❌ 所有后端服务都不可用');
    
    // 如果是GitHub Pages环境且后端不可用，显示部署提示
    if (window.location.hostname.includes('github.io')) {
        showBackendDeploymentPrompt();
    } else {
        showBackendStatusBanner('info', '本地后端服务未启动，请运行 python real_policy_server.py');
    }
}

// 显示后端部署提示
function showBackendDeploymentPrompt() {
    // 创建部署提示横幅
    const banner = document.createElement('div');
    banner.id = 'deploymentBanner';
    banner.className = 'deployment-banner';
    banner.innerHTML = `
        <div class="banner-content">
            <div class="banner-icon">
                <i class="fas fa-rocket"></i>
            </div>
            <div class="banner-text">
                <h4>后端服务需要部署</h4>
                <p>为了使用完整功能，需要部署后端服务到云平台</p>
            </div>
            <div class="banner-actions">
                <button class="deploy-now-btn" onclick="goToDeployPage()">
                    <i class="fas fa-cloud-upload-alt"></i>
                    立即部署
                </button>
                <button class="banner-close" onclick="closeBanner()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;
    
    // 添加样式
    if (!document.querySelector('#deployment-banner-styles')) {
        const style = document.createElement('style');
        style.id = 'deployment-banner-styles';
        style.textContent = `
            .deployment-banner {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                z-index: 10000;
                padding: 12px 20px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                transform: translateY(-100%);
                transition: transform 0.3s ease;
            }
            
            .deployment-banner.show {
                transform: translateY(0);
            }
            
            .banner-content {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                gap: 20px;
            }
            
            .banner-icon {
                width: 40px;
                height: 40px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
            }
            
            .banner-text {
                flex: 1;
            }
            
            .banner-text h4 {
                margin: 0 0 4px 0;
                font-size: 1rem;
                font-weight: 600;
            }
            
            .banner-text p {
                margin: 0;
                opacity: 0.9;
                font-size: 0.875rem;
            }
            
            .banner-actions {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .deploy-now-btn {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.3s ease;
                font-size: 0.875rem;
            }
            
            .deploy-now-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }
            
            .banner-close {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                padding: 6px;
                border-radius: 6px;
                opacity: 0.8;
                transition: opacity 0.3s ease;
            }
            
            .banner-close:hover {
                opacity: 1;
                background: rgba(255, 255, 255, 0.1);
            }
            
            @media (max-width: 768px) {
                .deployment-banner {
                    padding: 10px 16px;
                }
                
                .banner-content {
                    flex-direction: column;
                    gap: 12px;
                    text-align: center;
                }
                
                .banner-icon {
                    width: 36px;
                    height: 36px;
                    font-size: 18px;
                }
                
                .banner-text h4 {
                    font-size: 0.9rem;
                }
                
                .banner-text p {
                    font-size: 0.8rem;
                }
                
                .banner-actions {
                    width: 100%;
                    justify-content: center;
                }
                
                .deploy-now-btn {
                    padding: 6px 14px;
                    font-size: 0.8rem;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // 添加到页面顶部
    document.body.insertBefore(banner, document.body.firstChild);
    
    // 显示动画
    setTimeout(() => {
        banner.classList.add('show');
    }, 100);
    
    // 调整页面内容位置
    document.body.style.paddingTop = '50px';
}

// 跳转到部署页面
function goToDeployPage() {
    window.location.href = 'deploy_backend.html';
}

// 关闭横幅
function closeBanner() {
    const banner = document.getElementById('deploymentBanner');
    if (banner) {
        banner.classList.remove('show');
        setTimeout(() => {
            banner.remove();
            document.body.style.paddingTop = '';
        }, 300);
    }
}

// 显示后端状态横幅
function showBackendStatusBanner(type, message) {
    const banner = document.getElementById('backendStatus');
    const statusText = document.getElementById('statusText');
    const deployBtn = document.getElementById('deployBtn');
    
    if (!banner || !statusText) return;
    
    // 设置消息
    statusText.textContent = message;
    
    // 根据类型设置样式和按钮
    banner.className = `backend-status-banner ${type}`;
    
    if (type === 'deploy') {
        deployBtn.style.display = 'inline-flex';
    } else {
        deployBtn.style.display = 'none';
    }
    
    // 显示横幅
    banner.style.display = 'block';
    
    // 添加动画
    setTimeout(() => {
        banner.classList.add('show');
    }, 100);
}

// 隐藏后端状态横幅
function hideBackendStatusBanner() {
    const banner = document.getElementById('backendStatus');
    if (banner) {
        banner.style.display = 'none';
        banner.classList.remove('show');
    }
    
    // 隐藏部署横幅
    const deployBanner = document.getElementById('deploymentBanner');
    if (deployBanner) {
        deployBanner.classList.remove('show');
        setTimeout(() => {
            deployBanner.remove();
            document.body.style.paddingTop = '';
        }, 300);
    }
}

// 初始化页面
function initializePage() {
    // 页面载入动画
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.6s ease';
        document.body.style.opacity = '1';
    }, 100);
    
    // 初始化滚动动画
    initializeScrollAnimations();
    
    // 初始化统计数字动画
    initializeCounterAnimations();
}

// 绑定事件
function bindEvents() {
    // 导航菜单切换
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', toggleMobileMenu);
    }
    
    // 平滑滚动
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', handleSmoothScroll);
    });
    
    // 返回顶部按钮
    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        window.addEventListener('scroll', toggleBackToTopButton);
        backToTopBtn.addEventListener('click', scrollToTop);
    }
    
    // 键盘快捷键
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// 切换移动端菜单
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    const navToggle = document.querySelector('.nav-toggle');
    
    isMenuOpen = !isMenuOpen;
    
    if (isMenuOpen) {
        navMenu.classList.add('active');
        navToggle.classList.add('active');
        document.body.style.overflow = 'hidden';
    } else {
        navMenu.classList.remove('active');
        navToggle.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// 处理平滑滚动
function handleSmoothScroll(e) {
    e.preventDefault();
    
    const targetId = this.getAttribute('href');
    const targetElement = document.querySelector(targetId);
    
    if (targetElement) {
        const offsetTop = targetElement.offsetTop - 80; // 考虑导航栏高度
        
        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
        
        // 关闭移动端菜单
        if (isMenuOpen) {
            toggleMobileMenu();
        }
    }
}

// 切换返回顶部按钮
function toggleBackToTopButton() {
    const backToTopBtn = document.getElementById('backToTop');
    
    if (window.pageYOffset > 300) {
        backToTopBtn.classList.add('visible');
    } else {
        backToTopBtn.classList.remove('visible');
    }
}

// 滚动到顶部
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// 处理键盘快捷键
function handleKeyboardShortcuts(e) {
    // Ctrl + K 打开AI咨询
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        openAIChat();
    }
    
    // Ctrl + M 开始政策匹配
    if (e.ctrlKey && e.key === 'm') {
        e.preventDefault();
        startMatching();
    }
    
    // ESC 关闭模态框
    if (e.key === 'Escape') {
        closeDeploymentModal();
    }
}

// 初始化滚动动画
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // 观察需要动画的元素
    const animatedElements = document.querySelectorAll(
        '.feature-card, .step-item, .about-feature, .hero-content'
    );
    
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

// 初始化计数器动画
function initializeCounterAnimations() {
    const counters = document.querySelectorAll('.stat-number');
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                animateCounter(entry.target);
                entry.target.dataset.animated = 'true';
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => {
        counterObserver.observe(counter);
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
        
        let displayValue = Math.floor(current);
        if (isPercentage) displayValue += '%';
        if (hasPlus) displayValue += '+';
        if (target.includes('/')) displayValue = Math.floor(current) + '/7';
        
        element.textContent = displayValue;
    }, 30);
}

// 开始政策匹配
function startMatching() {
    // 页面跳转动画
    document.body.style.transition = 'opacity 0.3s ease';
    document.body.style.opacity = '0.7';
    
    setTimeout(() => {
        window.location.href = 'company-info.html';
    }, 300);
}

// 打开AI咨询
function openAIChat() {
    // 页面跳转动画
    document.body.style.transition = 'opacity 0.3s ease';
    document.body.style.opacity = '0.7';
    
    setTimeout(() => {
        window.location.href = 'ai-chat.html';
    }, 300);
}

// 页面可见性变化处理
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // 页面重新可见时，重新检查后端状态
        setTimeout(() => {
            checkBackendStatus();
        }, 1000);
    }
});

// 定期检查后端状态（每5分钟）
setInterval(() => {
    if (document.visibilityState === 'visible') {
        checkBackendStatus();
    }
}, 5 * 60 * 1000); 