// 政策分析图表配置
let policyChart = null;

// 图表数据
const chartData = {
    month: {
        labels: ['资金补贴', '税收优惠', '创新券', '其他'],
        data: [42, 25, 20, 13],
        colors: ['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b']
    },
    quarter: {
        labels: ['资金补贴', '税收优惠', '创新券', '其他'],
        data: [45, 28, 18, 9],
        colors: ['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b']
    },
    year: {
        labels: ['资金补贴', '税收优惠', '创新券', '其他'],
        data: [45, 28, 18, 9],
        colors: ['#06b6d4', '#8b5cf6', '#10b981', '#f59e0b']
    }
};

// 初始化图表
function initializePolicyChart() {
    const ctx = document.getElementById('policyChart');
    if (!ctx) return;

    // 图表配置
    const config = {
        type: 'doughnut',
        data: {
            labels: chartData.year.labels,
            datasets: [{
                data: chartData.year.data,
                backgroundColor: chartData.year.colors,
                borderWidth: 0,
                hoverBorderWidth: 3,
                hoverBorderColor: '#ffffff',
                cutout: '65%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((context.parsed / total) * 100);
                            return `${context.label}: ${percentage}% (${context.parsed}项)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1000,
                easing: 'easeOutQuart'
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            elements: {
                arc: {
                    borderWidth: 0,
                    hoverBorderWidth: 3
                }
            }
        }
    };

    // 创建图表
    policyChart = new Chart(ctx, config);

    // 添加中心文本
    addCenterText();
}

// 添加图表中心文本
function addCenterText() {
    Chart.register({
        id: 'centerText',
        beforeDraw: function(chart) {
            if (chart.config.type === 'doughnut') {
                const ctx = chart.ctx;
                const width = chart.width;
                const height = chart.height;
                const fontSize = Math.min(width, height) / 25;
                
                ctx.restore();
                ctx.font = `${fontSize}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`;
                ctx.textBaseline = 'middle';
                ctx.fillStyle = '#1f2937';
                
                const text = '政策分布';
                const textX = Math.round((width - ctx.measureText(text).width) / 2);
                const textY = height / 2 - fontSize / 2;
                
                ctx.fillText(text, textX, textY);
                
                // 添加副标题
                ctx.font = `${fontSize * 0.6}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`;
                ctx.fillStyle = '#6b7280';
                const subText = '类型统计';
                const subTextX = Math.round((width - ctx.measureText(subText).width) / 2);
                const subTextY = height / 2 + fontSize / 2;
                
                ctx.fillText(subText, subTextX, subTextY);
                ctx.save();
            }
        }
    });
}

// 更新图表数据
function updateChart(period) {
    if (!policyChart || !chartData[period]) return;

    const data = chartData[period];
    
    // 更新图表数据
    policyChart.data.labels = data.labels;
    policyChart.data.datasets[0].data = data.data;
    policyChart.data.datasets[0].backgroundColor = data.colors;
    
    // 添加动画效果
    policyChart.update('active');
    
    // 更新图例
    updateLegend(data);
}

// 更新图例
function updateLegend(data) {
    const legendItems = document.querySelectorAll('.legend-item');
    const total = data.data.reduce((a, b) => a + b, 0);
    
    legendItems.forEach((item, index) => {
        if (index < data.data.length) {
            const percentage = Math.round((data.data[index] / total) * 100);
            const valueElement = item.querySelector('.legend-value');
            
            // 添加动画效果
            valueElement.style.transform = 'scale(1.1)';
            setTimeout(() => {
                valueElement.textContent = percentage + '%';
                valueElement.style.transform = 'scale(1)';
            }, 200);
        }
    });
}

// 添加图表交互效果
function addChartInteractions() {
    const legendItems = document.querySelectorAll('.legend-item');
    
    legendItems.forEach((item, index) => {
        item.addEventListener('mouseenter', () => {
            if (policyChart) {
                // 高亮对应的图表段
                policyChart.setActiveElements([{
                    datasetIndex: 0,
                    index: index
                }]);
                policyChart.update('none');
            }
        });
        
        item.addEventListener('mouseleave', () => {
            if (policyChart) {
                policyChart.setActiveElements([]);
                policyChart.update('none');
            }
        });
        
        item.addEventListener('click', () => {
            // 可以添加点击事件，比如显示详细信息
            const label = item.querySelector('.legend-label').textContent;
            const value = item.querySelector('.legend-value').textContent;
            console.log(`点击了 ${label}: ${value}`);
        });
    });
}

// 监听时间期间选择器变化
function bindChartControls() {
    const periodSelect = document.getElementById('chartPeriod');
    if (periodSelect) {
        periodSelect.addEventListener('change', (e) => {
            updateChart(e.target.value);
        });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 等待Chart.js完全加载
    setTimeout(() => {
        initializePolicyChart();
        addChartInteractions();
        bindChartControls();
    }, 100);
});

// 响应式图表大小调整
window.addEventListener('resize', function() {
    if (policyChart) {
        policyChart.resize();
    }
});

// 导出图表数据（可选功能）
function exportChartData() {
    const period = document.getElementById('chartPeriod').value;
    const data = chartData[period];
    
    console.log('导出图表数据:', {
        period: period,
        data: data
    });
    
    // 这里可以添加实际的导出逻辑
    alert('图表数据导出功能开发中！');
}

// 刷新图表数据（模拟从API获取新数据）
async function refreshChartData() {
    try {
        // 模拟API调用
        console.log('刷新图表数据...');
        
        // 这里可以添加实际的API调用
        // const response = await fetch('/api/v1/policies/statistics');
        // const newData = await response.json();
        
        // 模拟数据更新
        const period = document.getElementById('chartPeriod').value;
        updateChart(period);
        
        console.log('图表数据已刷新');
    } catch (error) {
        console.error('刷新图表数据失败:', error);
    }
} 