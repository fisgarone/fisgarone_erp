// ===== AI DASHBOARD COMPONENT =====
// Dashboard principal com IA integrada

class AIDashboard extends HTMLElement {
    constructor() {
        super();
        this.aiEngine = new AIEngine();
        this.apiService = new APIIntegration();
        this.initialized = false;

        // Bind methods
        this.initializeDashboard = this.initializeDashboard.bind(this);
        this.render = this.render.bind(this);
        this.handleAIAnalysis = this.handleAIAnalysis.bind(this);
    }

    async connectedCallback() {
        if (!this.initialized) {
            await this.initializeDashboard();
        }
    }

    // ===== INICIALIZAÇÃO DO DASHBOARD =====
    async initializeDashboard() {
        console.log('🚀 Inicializando Dashboard IA...');

        try {
            // 1. Carrega dados iniciais
            const dashboardData = await this.apiService.fetchDashboardData();

            // 2. IA analisa dados e sugere layout
            const aiInsights = await this.aiEngine.analyzeSalesData(dashboardData);

            // 3. Renderiza dashboard inteligente
            await this.render(dashboardData, aiInsights);

            // 4. Configura automações
            await this.setupAutomations(aiInsights);

            this.initialized = true;
            console.log('✅ Dashboard IA inicializado com sucesso!');

        } catch (error) {
            console.error('❌ Erro ao inicializar dashboard:', error);
            this.renderErrorState(error);
        }
    }

    // ===== RENDERIZAÇÃO INTELIGENTE =====
    async render(dashboardData, aiInsights) {
        const optimalLayout = this.calculateOptimalLayout(aiInsights);

        this.innerHTML = `
            <div class="ai-dashboard" data-layout="${optimalLayout}">
                <!-- Header Inteligente -->
                <header class="ai-dashboard-header">
                    <div class="header-content">
                        <h1 class="ai-text-gradient">FISGARONE AI</h1>
                        <p class="ai-subtitle">Dashboard Inteligente com Automação</p>
                    </div>
                    <div class="ai-controls">
                        <button class="ai-btn ai-btn-primary" onclick="dashboard.runAIAnalysis()">
                            🧠 Análise IA
                        </button>
                        <button class="ai-btn ai-btn-secondary" onclick="dashboard.toggleTheme()">
                            🌙 Tema
                        </button>
                    </div>
                </header>

                <!-- KPIs em Tempo Real -->
                <section class="kpi-section">
                    <div class="section-header">
                        <h2>📊 Métricas em Tempo Real</h2>
                        <span class="ai-badge ai-badge-success">IA Otimizado</span>
                    </div>
                    <div class="kpi-grid" id="kpi-container">
                        <!-- KPIs serão renderizados dinamicamente -->
                    </div>
                </section>

                <!-- Insights da IA -->
                <section class="ai-insights-section">
                    <div class="section-header">
                        <h2>🤖 Insights Inteligentes</h2>
                        <span class="ai-badge ai-badge-primary">IA Ativa</span>
                    </div>
                    <div class="insights-grid" id="insights-container">
                        <!-- Insights serão renderizados aqui -->
                    </div>
                </section>

                <!-- Gráficos Preditivos -->
                <section class="charts-section">
                    <div class="section-header">
                        <h2>📈 Análises Preditivas</h2>
                        <span class="ai-badge ai-badge-warning">Em Tempo Real</span>
                    </div>
                    <div class="charts-grid" id="charts-container">
                        <!-- Gráficos serão renderizados aqui -->
                    </div>
                </section>

                <!-- Painel de Automação -->
                <section class="automation-section">
                    <div class="section-header">
                        <h2>⚡ Automações Ativas</h2>
                        <span class="ai-badge ai-badge-info">Automático</span>
                    </div>
                    <div class="automation-panel" id="automation-container">
                        <!-- Automações serão listadas aqui -->
                    </div>
                </section>
            </div>
        `;

        // Renderiza componentes dinâmicos
        await this.renderKPIs(dashboardData.overview);
        await this.renderAIInsights(aiInsights);
        await this.renderCharts(dashboardData.trends);
        await this.renderAutomations(aiInsights.optimizationOpportunities);
    }

    // ===== RENDERIZAÇÃO DE KPIs =====
    async renderKPIs(overviewData) {
        const kpiContainer = this.querySelector('#kpi-container');
        if (!kpiContainer || !overviewData) return;

        const kpis = overviewData.kpis || [];

        kpiContainer.innerHTML = kpis.map(kpi => `
            <div class="kpi-card ${this.getKPIColorClass(kpi.value)}">
                <div class="kpi-icon">${this.getKPIIcon(kpi.name)}</div>
                <div class="kpi-content">
                    <h3 class="kpi-value">${kpi.value} ${kpi.unit || ''}</h3>
                    <p class="kpi-label">${kpi.name}</p>
                </div>
                <div class="kpi-trend">
                    ${this.getKPITrend(kpi)}
                </div>
            </div>
        `).join('');
    }

    // ===== RENDERIZAÇÃO DE INSIGHTS IA =====
    async renderAIInsights(aiInsights) {
        const insightsContainer = this.querySelector('#insights-container');
        if (!insightsContainer) return;

        insightsContainer.innerHTML = `
            <div class="insight-card insight-success">
                <div class="insight-icon">🏆</div>
                <div class="insight-content">
                    <h4>Produtos em Destaque</h4>
                    <p>${aiInsights.topPerformingProducts.length} produtos com alto desempenho</p>
                    <ul class="insight-list">
                        ${aiInsights.topPerformingProducts.slice(0, 3).map(product =>
                            `<li>${product.name}: R$ ${product.totalSales.toFixed(2)}</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>

            <div class="insight-card insight-warning">
                <div class="insight-icon">💡</div>
                <div class="insight-content">
                    <h4>Oportunidades de Otimização</h4>
                    <p>${aiInsights.optimizationOpportunities.length} áreas para melhorias</p>
                    <ul class="insight-list">
                        ${aiInsights.optimizationOpportunities.slice(0, 2).map(opp =>
                            `<li>${opp.description}</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>

            <div class="insight-card insight-info">
                <div class="insight-icon">📈</div>
                <div class="insight-content">
                    <h4>Tendência de Vendas</h4>
                    <p>Crescimento de ${aiInsights.salesTrends.growthRate.toFixed(1)}%</p>
                    <p>Melhor dia: ${aiInsights.salesTrends.bestDay[0]} (R$ ${aiInsights.salesTrends.bestDay[1].toFixed(2)})</p>
                </div>
            </div>
        `;
    }

    // ===== MÉTODOS AUXILIARES =====
    getKPIColorClass(value) {
        if (value > 1000) return 'kpi-high';
        if (value > 500) return 'kpi-medium';
        return 'kpi-low';
    }

    getKPIIcon(kpiName) {
        const icons = {
            'Total de Vendas': '📦',
            'Faturamento Bruto': '💰',
            'Faturamento Líquido': '💸',
            'Ticket Médio': '🎫',
            'Lucro Estimado': '📊'
        };
        return icons[kpiName] || '📈';
    }

    getKPITrend(kpi) {
        // Simula tendência baseada no valor
        if (kpi.value > 1000) return '↗️';
        if (kpi.value > 500) return '→';
        return '↘️';
    }

    calculateOptimalLayout(aiInsights) {
        // IA decide o melhor layout baseado nos insights
        if (aiInsights.topPerformingProducts.length > 5) return 'expanded';
        if (aiInsights.optimizationOpportunities.length > 2) return 'focused';
        return 'standard';
    }

    // ===== AÇÕES DA IA =====
    async runAIAnalysis() {
        console.log('🧠 Executando análise IA...');
        const dashboardData = await this.apiService.fetchDashboardData();
        const aiInsights = await this.aiEngine.analyzeSalesData(dashboardData);
        await this.renderAIInsights(aiInsights);

        // Mostra notificação
        this.showNotification('Análise IA concluída! Novos insights disponíveis.', 'success');
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('ai_theme', newTheme);
    }

    showNotification(message, type = 'info') {
        // Implementar sistema de notificações
        console.log(`🔔 ${type.toUpperCase()}: ${message}`);
    }

    // ===== CONFIGURAÇÃO DE AUTOMAÇÕES =====
    async setupAutomations(aiInsights) {
        console.log('⚡ Configurando automações IA...');

        // Configura automações baseadas nos insights
        if (aiInsights.optimizationOpportunities.length > 0) {
            this.setupOptimizationAutomations(aiInsights.optimizationOpportunities);
        }

        if (aiInsights.salesTrends.growthRate < 0) {
            this.setupGrowthAutomations();
        }
    }

    setupOptimizationAutomations(opportunities) {
        opportunities.forEach(opp => {
            console.log(`🔧 Configurando automação para: ${opp.type}`);
            // Aqui configuraríamos automações específicas
        });
    }

    setupGrowthAutomations() {
        console.log('📈 Configurando automações para crescimento...');
        // Automações para impulsionar vendas
    }

    // ===== ESTADO DE ERRO =====
    renderErrorState(error) {
        this.innerHTML = `
            <div class="error-state">
                <div class="error-icon">❌</div>
                <h2>Erro ao Carregar Dashboard</h2>
                <p>${error.message}</p>
                <button class="ai-btn ai-btn-primary" onclick="dashboard.initializeDashboard()">
                    🔄 Tentar Novamente
                </button>
            </div>
        `;
    }
}

// Registra o Web Component
customElements.define('ai-dashboard', AIDashboard);

// Export para uso global
window.AIDashboard = AIDashboard;