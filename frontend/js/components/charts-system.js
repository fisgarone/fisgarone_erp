// ===== CHARTS SYSTEM PRECISO =====
class ChartsSystem {
    constructor() {
        this.charts = new Map();
        this.colors = {
            primary: '#3b82f6',
            success: '#10b981',
            warning: '#f59e0b',
            error: '#ef4444',
            purple: '#8b5cf6',
            pink: '#ec4899',
            indigo: '#6366f1'
        };

        this.init();
    }

    // ===== INICIALIZAÇÃO =====
    init() {
        console.log('📊 Sistema de Gráficos inicializado');
        this.setupThemeListener();
    }

    // ===== GRÁFICO DE VENDAS DIÁRIAS =====
    renderDailySales(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) {
            console.warn(`Container #${containerId} não encontrado`);
            return;
        }

        const chartData = {
            labels: data.map(item => {
                const date = new Date(item.date);
                return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
            }),
            datasets: [{
                label: 'Vendas Diárias (R$)',
                data: data.map(item => item.total_sales),
                borderColor: this.colors.primary,
                backgroundColor: this.hexToRgba(this.colors.primary, 0.1),
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: this.colors.primary,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        };

        this.createChart(ctx, 'line', chartData, {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: this.getThemeColor(),
                        font: {
                            size: 12,
                            family: 'Plus Jakarta Sans, sans-serif'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: this.getTooltipBackground(),
                    titleColor: this.getThemeColor(),
                    bodyColor: this.getThemeColor(),
                    borderColor: this.getGridColor(),
                    borderWidth: 1,
                    callbacks: {
                        label: (context) => `R$ ${context.raw.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
                        title: (context) => `Data: ${context[0].label}`
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: this.getGridColor(),
                        drawBorder: false
                    },
                    ticks: {
                        color: this.getThemeColor(),
                        font: {
                            family: 'Plus Jakarta Sans, sans-serif'
                        }
                    }
                },
                y: {
                    grid: {
                        color: this.getGridColor(),
                        drawBorder: false
                    },
                    ticks: {
                        color: this.getThemeColor(),
                        callback: (value) => `R$ ${value.toLocaleString('pt-BR')}`,
                        font: {
                            family: 'Plus Jakarta Sans, sans-serif'
                        }
                    },
                    beginAtZero: true
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animations: {
                tension: {
                    duration: 1000,
                    easing: 'linear'
                }
            }
        });
    }

    // ===== GRÁFICO ABC PRODUTOS =====
    renderABCAnalysis(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) {
            console.warn(`Container #${containerId} não encontrado`);
            return;
        }

        const sortedData = data.slice(0, 8); // Top 8 produtos
        const backgroundColors = sortedData.map((item, index) => {
            if (index < 2) return this.hexToRgba(this.colors.success, 0.8);    // A
            if (index < 5) return this.hexToRgba(this.colors.warning, 0.8);    // B
            return this.hexToRgba(this.colors.error, 0.8);                     // C
        });

        const chartData = {
            labels: sortedData.map(item => this.truncateText(item.title, 18)),
            datasets: [{
                label: 'Faturamento (R$)',
                data: sortedData.map(item => item.total_sales),
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color.replace('0.8', '1')),
                borderWidth: 2,
                borderRadius: 6,
                borderSkipped: false
            }]
        };

        this.createChart(ctx, 'bar', chartData, {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: this.getTooltipBackground(),
                    titleColor: this.getThemeColor(),
                    bodyColor: this.getThemeColor(),
                    borderColor: this.getGridColor(),
                    borderWidth: 1,
                    callbacks: {
                        label: (context) => `R$ ${context.raw.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
                        afterLabel: (context) => {
                            const item = sortedData[context.dataIndex];
                            return `Classificação: ${item.classification}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: this.getGridColor(),
                        display: false
                    },
                    ticks: {
                        color: this.getThemeColor(),
                        font: {
                            family: 'Plus Jakarta Sans, sans-serif',
                            size: 11
                        },
                        maxRotation: 45
                    }
                },
                y: {
                    grid: {
                        color: this.getGridColor(),
                        drawBorder: false
                    },
                    ticks: {
                        color: this.getThemeColor(),
                        callback: (value) => `R$ ${value.toLocaleString('pt-BR')}`,
                        font: {
                            family: 'Plus Jakarta Sans, sans-serif'
                        }
                    },
                    beginAtZero: true
                }
            }
        });
    }

    // ===== GRÁFICO PIZZA CATEGORIAS =====
    renderSalesDistribution(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) {
            console.warn(`Container #${containerId} não encontrado`);
            return;
        }

        const classA = data.filter(item => item.classification === 'A').length;
        const classB = data.filter(item => item.classification === 'B').length;
        const classC = data.filter(item => item.classification === 'C').length;

        const chartData = {
            labels: ['Classe A', 'Classe B', 'Classe C'],
            datasets: [{
                data: [classA, classB, classC],
                backgroundColor: [
                    this.hexToRgba(this.colors.success, 0.8),
                    this.hexToRgba(this.colors.warning, 0.8),
                    this.hexToRgba(this.colors.error, 0.8)
                ],
                borderColor: [
                    this.colors.success,
                    this.colors.warning,
                    this.colors.error
                ],
                borderWidth: 2,
                hoverOffset: 15
            }]
        };

        this.createChart(ctx, 'doughnut', chartData, {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: this.getThemeColor(),
                        font: {
                            size: 12,
                            family: 'Plus Jakarta Sans, sans-serif'
                        },
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: this.getTooltipBackground(),
                    titleColor: this.getThemeColor(),
                    bodyColor: this.getThemeColor(),
                    borderColor: this.getGridColor(),
                    borderWidth: 1,
                    callbacks: {
                        label: (context) => {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.raw / total) * 100).toFixed(1);
                            return `${context.label}: ${context.raw} produtos (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        });
    }

    // ===== GRÁFICO DE COMPARAÇÃO MENSAL =====
    renderMonthlyComparison(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return;

        const chartData = {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out'],
            datasets: [
                {
                    label: '2024',
                    data: [12500, 13800, 14200, 15600, 14800, 16200, 17500, 16800, 18200, 19500],
                    borderColor: this.colors.primary,
                    backgroundColor: this.hexToRgba(this.colors.primary, 0.1),
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: '2025',
                    data: [14200, 15800, 16500, 17800, 19200, 20500, 21800, 22500, 23800, 25200],
                    borderColor: this.colors.success,
                    backgroundColor: this.hexToRgba(this.colors.success, 0.1),
                    borderWidth: 2,
                    fill: true
                }
            ]
        };

        this.createChart(ctx, 'line', chartData, {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: this.getThemeColor(),
                        font: {
                            size: 12,
                            family: 'Plus Jakarta Sans, sans-serif'
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: this.getGridColor() },
                    ticks: { color: this.getThemeColor() }
                },
                y: {
                    grid: { color: this.getGridColor() },
                    ticks: {
                        color: this.getThemeColor(),
                        callback: (value) => `R$ ${(value/1000).toFixed(0)}k`
                    }
                }
            }
        });
    }

    // ===== MÉTODOS AUXILIARES PRECISOS =====
    createChart(ctx, type, data, options) {
        // Destruir chart anterior se existir
        if (this.charts.has(ctx.id)) {
            this.charts.get(ctx.id).destroy();
        }

        const chart = new Chart(ctx, {
            type: type,
            data: data,
            options: options
        });

        this.charts.set(ctx.id, chart);
        return chart;
    }

    getThemeColor() {
        return document.documentElement.getAttribute('data-theme') === 'dark' ? '#ffffff' : '#0f172a';
    }

    getGridColor() {
        return document.documentElement.getAttribute('data-theme') === 'dark' ? '#334155' : '#e2e8f0';
    }

    getTooltipBackground() {
        return document.documentElement.getAttribute('data-theme') === 'dark' ? '#1e293b' : '#ffffff';
    }

    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    // ===== OUVINTE DE MUDANÇA DE TEMA =====
    setupThemeListener() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-theme') {
                    this.updateAllCharts();
                }
            });
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    }

    // ===== ATUALIZAR TODOS OS GRÁFICOS =====
    updateAllCharts() {
        console.log('🔄 Atualizando gráficos para o tema atual...');
        this.charts.forEach((chart, id) => {
            try {
                chart.update('none'); // Atualizar sem animação
            } catch (error) {
                console.warn(`Erro ao atualizar gráfico ${id}:`, error);
            }
        });
    }

    // ===== DESTRUIR TODOS OS GRÁFICOS =====
    destroyAllCharts() {
        console.log('🧹 Destruindo todos os gráficos...');
        this.charts.forEach((chart, id) => {
            try {
                chart.destroy();
            } catch (error) {
                console.warn(`Erro ao destruir gráfico ${id}:`, error);
            }
        });
        this.charts.clear();
    }

    // ===== EXPORTAR GRÁFICO COMO IMAGEM =====
    exportChartAsImage(chartId, filename = 'grafico') {
        const chart = this.charts.get(chartId);
        if (!chart) {
            console.warn(`Gráfico ${chartId} não encontrado`);
            return;
        }

        const image = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `${filename}-${new Date().toISOString().split('T')[0]}.png`;
        link.href = image;
        link.click();
    }

    // ===== OBTER ESTATÍSTICAS DOS GRÁFICOS =====
    getChartStats(chartId) {
        const chart = this.charts.get(chartId);
        if (!chart) return null;

        const data = chart.data.datasets[0].data;
        return {
            total: data.reduce((a, b) => a + b, 0),
            average: data.reduce((a, b) => a + b, 0) / data.length,
            max: Math.max(...data),
            min: Math.min(...data),
            count: data.length
        };
    }

    // ===== REDEFINIR ZOOM DOS GRÁFICOS =====
    resetZoom() {
        this.charts.forEach((chart, id) => {
            if (chart.resetZoom) {
                chart.resetZoom();
            }
        });
    }
}

// Instância global
window.chartsSystem = new ChartsSystem();