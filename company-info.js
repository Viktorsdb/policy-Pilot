// 企业信息填写页面交互脚本

// 全局变量
let formData = {};
let isAutoSaving = false;
let autoSaveTimer = null;
const API_BASE_URL = 'http://localhost:8000/api/v1';

// DOM 就绪后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    bindEvents();
    setupAutoSave();
});

// 初始化表单
function initializeForm() {
    // 页面载入动画
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.6s ease';
        document.body.style.opacity = '1';
    }, 100);
    
    // 加载保存的数据（如果有的话）
    loadSavedData();
    
    // 设置默认值
    setDefaultValues();
    
    // 添加清除数据按钮
    addClearDataButton();
}

// 添加清除数据按钮
function addClearDataButton() {
    const formActions = document.querySelector('.form-actions');
    if (formActions) {
        const clearBtn = document.createElement('button');
        clearBtn.type = 'button';
        clearBtn.id = 'clearDataBtn';
        clearBtn.className = 'clear-btn';
        clearBtn.innerHTML = '<i class="fas fa-trash-alt"></i> 清除数据';
        clearBtn.onclick = clearSavedData;
        
        // 插入到提交按钮之前
        const submitBtn = document.getElementById('submitBtn');
        formActions.insertBefore(clearBtn, submitBtn);
    }
}

// 设置自动保存
function setupAutoSave() {
    const inputs = document.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        // 监听输入变化
        input.addEventListener('input', debounceAutoSave);
        input.addEventListener('change', debounceAutoSave);
    });
}

// 防抖自动保存
function debounceAutoSave() {
    if (autoSaveTimer) {
        clearTimeout(autoSaveTimer);
    }
    
    autoSaveTimer = setTimeout(() => {
        performAutoSave();
    }, 1000); // 1秒后自动保存
}

// 执行自动保存
function performAutoSave() {
    if (isAutoSaving) return;
    
    isAutoSaving = true;
    saveFormData();
    showAutoSaveIndicator();
    
    setTimeout(() => {
        isAutoSaving = false;
    }, 500);
}

// 显示自动保存指示器
function showAutoSaveIndicator() {
    // 移除已存在的指示器
    const existingIndicator = document.querySelector('.auto-save-indicator');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    const indicator = document.createElement('div');
    indicator.className = 'auto-save-indicator';
    indicator.innerHTML = '<i class="fas fa-check-circle"></i> 已自动保存';
    
    // 添加样式
    indicator.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        font-size: 0.875rem;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
        z-index: 10000;
        transform: translateX(300px);
        transition: transform 0.3s ease;
        display: flex;
        align-items: center;
        gap: 8px;
    `;
    
    document.body.appendChild(indicator);
    
    // 显示动画
    requestAnimationFrame(() => {
        indicator.style.transform = 'translateX(0)';
    });
    
    // 3秒后隐藏
    setTimeout(() => {
        indicator.style.transform = 'translateX(300px)';
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.remove();
            }
        }, 300);
    }, 3000);
}

// 设置默认值
function setDefaultValues() {
    // 设置经营状态和信用情况为默认良好
    const operatingStatus = document.getElementById('operatingStatus');
    const creditStatus = document.getElementById('creditStatus');
    
    if (operatingStatus && !operatingStatus.value) operatingStatus.value = 'good';
    if (creditStatus && !creditStatus.value) creditStatus.value = 'good';
}

// 验证表单
function validateForm() {
    const requiredFields = document.querySelectorAll('[required]');
    let isValid = true;
    let firstInvalidField = null;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.style.borderColor = '#ef4444';
            
            if (!firstInvalidField) {
                firstInvalidField = field;
            }
            
            // 添加失去焦点时恢复边框颜色的事件
            field.addEventListener('input', function() {
                this.style.borderColor = '#e5e7eb';
            }, { once: true });
        }
    });
    
    // 特殊验证：注册地必须是徐汇区
    const registrationLocation = document.getElementById('registrationLocation');
    if (registrationLocation && registrationLocation.value !== 'xuhui') {
        isValid = false;
        registrationLocation.style.borderColor = '#ef4444';
        showNotification('目前仅支持徐汇区注册企业申请', 'error');
        
        if (!firstInvalidField) {
            firstInvalidField = registrationLocation;
        }
    }
    
    if (!isValid) {
        showNotification('请填写所有必填字段', 'error');
        if (firstInvalidField) {
            firstInvalidField.focus();
            firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    return isValid;
}

// 保存表单数据
function saveFormData() {
    const inputs = document.querySelectorAll('input, select, textarea');
    formData = {};
    
    inputs.forEach(input => {
        if (input.id) {
            formData[input.id] = input.value;
        }
    });
    
    // 添加保存时间戳
    formData._savedAt = new Date().toISOString();
    
    // 保存到本地存储
    localStorage.setItem('companyFormData', JSON.stringify(formData));
}

// 加载保存的数据
function loadSavedData() {
    const savedData = localStorage.getItem('companyFormData');
    if (savedData) {
        try {
            formData = JSON.parse(savedData);
            
            // 检查数据是否过期（7天）
            if (formData._savedAt) {
                const savedTime = new Date(formData._savedAt);
                const currentTime = new Date();
                const daysDiff = (currentTime - savedTime) / (1000 * 60 * 60 * 24);
                
                if (daysDiff > 7) {
                    // 数据过期，清除
                    localStorage.removeItem('companyFormData');
                    showNotification('保存的数据已过期，已自动清除', 'warning');
                    return;
                }
            }
            
            // 填充表单字段
            Object.keys(formData).forEach(fieldId => {
                if (fieldId === '_savedAt') return; // 跳过时间戳
                
                const field = document.getElementById(fieldId);
                if (field && formData[fieldId]) {
                    field.value = formData[fieldId];
                }
            });
            
            // 显示恢复信息
            const savedTime = formData._savedAt ? 
                new Date(formData._savedAt).toLocaleString('zh-CN') : '未知时间';
            
            showDataRestoredNotification(savedTime);
            
        } catch (error) {
            console.error('加载保存的数据失败:', error);
            localStorage.removeItem('companyFormData');
        }
    }
}

// 显示数据恢复通知
function showDataRestoredNotification(savedTime) {
    const notification = document.createElement('div');
    notification.className = 'data-restored-notification';
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-history"></i>
            <div class="notification-text">
                <strong>已恢复保存的数据</strong>
                <small>保存时间: ${savedTime}</small>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="close-btn">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.3);
        z-index: 10000;
        max-width: 400px;
        width: 90%;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    const contentStyle = `
        .notification-content {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .notification-text {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .notification-text small {
            opacity: 0.8;
            font-size: 0.75rem;
        }
        .close-btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
        }
        .close-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
    `;
    
    if (!document.querySelector('#notification-content-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-content-styles';
        style.textContent = contentStyle;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // 显示动画
    requestAnimationFrame(() => {
        notification.style.opacity = '1';
    });
    
    // 10秒后自动隐藏
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 10000);
}

// 清除保存的数据
function clearSavedData() {
    if (confirm('确定要清除所有保存的数据吗？此操作无法撤销。')) {
        localStorage.removeItem('companyFormData');
        
        // 清空表单
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
        
        // 重新设置默认值
        setDefaultValues();
        
        showNotification('数据已清除', 'success');
        
        // 移除自动保存指示器
        const indicator = document.querySelector('.auto-save-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
}

// 构建企业画像数据
function buildCompanyProfile() {
    const profile = {
        company_name: document.getElementById('companyName').value,
        registration_location: document.getElementById('registrationLocation').value,
        industry_match: document.getElementById('industryMatch').value,
        operating_status: document.getElementById('operatingStatus').value,
        credit_status: document.getElementById('creditStatus').value,
        patents: parseInt(document.getElementById('patents').value) || 0,
        company_scale: document.getElementById('companyScale').value,
        rd_investment: document.getElementById('rdInvestment').value,
        enterprise_certification: document.getElementById('enterpriseCertification').value || null,
        contact_phone: document.getElementById('contactPhone').value || null,
        contact_email: document.getElementById('contactEmail').value || null,
    };
    
    return profile;
}

// 提交表单
async function submitForm() {
    if (!validateForm()) {
        return;
    }
    
    // 保存最新数据
    saveFormData();
    
    // 显示提交中状态
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 提交中...';
    submitBtn.disabled = true;
    
    try {
        // 构建企业画像数据
        const companyProfile = buildCompanyProfile();
        
        showNotification('正在提交企业信息并进行政策匹配分析...', 'info');
        
        // 调用后端API进行政策匹配
        const response = await fetch(`${API_BASE_URL}/match/simple`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(companyProfile)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '政策匹配失败');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // 清除保存的数据
            localStorage.removeItem('companyFormData');
            
            // 保存匹配结果到session storage供政策看板使用
            sessionStorage.setItem('companyInfo', JSON.stringify(companyProfile));
            sessionStorage.setItem('policyMatches', JSON.stringify(result.data.matches));
            
            showNotification(`企业信息提交成功！匹配到 ${result.data.count} 个政策机会`, 'success');
            
            // 延迟跳转到政策看板
        setTimeout(() => {
                window.location.href = 'policy-dashboard.html';
            }, 2000);
        } else {
            throw new Error(result.message || '政策匹配失败');
        }
        
    } catch (error) {
        console.error('提交失败:', error);
        showNotification(`提交失败: ${error.message}`, 'error');
        
        // 恢复按钮状态
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// 绑定事件
function bindEvents() {
    // 表单字段实时验证
    const formInputs = document.querySelectorAll('.form-input, .form-select, .form-textarea');
    formInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            // 清除错误样式
            this.style.borderColor = '#e5e7eb';
            // 实时保存
            saveFormData();
        });
        
        input.addEventListener('change', function() {
            // 处理select变化
            if (this.tagName === 'SELECT') {
                validateField(this);
                saveFormData();
            }
        });
    });
    
    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            submitForm();
        } else if (e.key === 'Escape') {
            if (confirm('确定要退出填写吗？未保存的数据将丢失。')) {
                goHome();
            }
        } else if (e.key === 's' && e.ctrlKey) {
            e.preventDefault();
            saveFormData();
            showNotification('数据已保存', 'success');
        }
    });
    
    // 页面离开前提醒保存
    window.addEventListener('beforeunload', function(e) {
        const hasUnsavedData = checkUnsavedData();
        if (hasUnsavedData) {
            e.preventDefault();
            e.returnValue = '您有未保存的数据，确定要离开吗？';
            return e.returnValue;
        }
    });
}

// 检查是否有未保存的数据
function checkUnsavedData() {
    const currentData = {};
    const inputs = document.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        if (input.id) {
            currentData[input.id] = input.value;
        }
    });
    
    const savedData = localStorage.getItem('companyFormData');
    if (!savedData) return Object.values(currentData).some(value => value.trim() !== '');
    
    try {
        const parsed = JSON.parse(savedData);
        return JSON.stringify(currentData) !== JSON.stringify(parsed);
    } catch {
        return true;
    }
}

// 验证单个字段
function validateField(field) {
    // 必填字段验证
    if (field.hasAttribute('required') && !field.value.trim()) {
        field.style.borderColor = '#ef4444';
        return false;
    }
    
    // 邮箱验证
    if (field.type === 'email' && field.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
            field.style.borderColor = '#ef4444';
            showNotification('请输入有效的邮箱地址', 'error');
            return false;
        }
    }
    
    // 电话号码验证
    if (field.type === 'tel' && field.value) {
        const phoneRegex = /^[\d\-\+\(\)\s]{10,}$/;
        if (!phoneRegex.test(field.value)) {
            field.style.borderColor = '#ef4444';
            showNotification('请输入有效的电话号码', 'error');
            return false;
        }
    }
    
    // 专利数量验证
    if (field.id === 'patents' && field.value) {
        const patentCount = parseInt(field.value);
        if (isNaN(patentCount) || patentCount < 0) {
            field.style.borderColor = '#ef4444';
            showNotification('专利数量必须是非负整数', 'error');
            return false;
        }
    }
    
    // 注册地验证
    if (field.id === 'registrationLocation' && field.value && field.value !== 'xuhui') {
        field.style.borderColor = '#ef4444';
        showNotification('目前仅支持徐汇区注册企业', 'error');
        return false;
    }
    
    field.style.borderColor = '#10b981';
    return true;
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

// 自动保存功能
setInterval(() => {
    const hasData = document.querySelector('input[value], select[value], textarea[value]');
    if (hasData) {
        saveFormData();
    }
}, 30000); // 每30秒自动保存一次 