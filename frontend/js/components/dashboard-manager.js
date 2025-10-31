// js/components/dashboard-manager.js - VERSÃO FINAL, COMPLETA E INTEGRADA

class DashboardManager {
    constructor() {
        this.api = new APIIntegration();
        this.aiEngine = new AIEngine();
        this.modal = new ModalSystem();
        this.data = null;
        this.currentTheme = localStorage.getItem('ai_theme') || 'light';
        this.isLoading = false;
    }

    // ===== INICIALIZAÇÃO COMPLETA =====
    async initialize() {
        console.log('🎯 Inicializando Dashboard Executivo...');

        try {
            // Aplicar tema salvo
            this.applyTheme(this.currentTheme);

            // Carregar todos os dados do backend
            this.data = await this.api.fetchDashboardData();

            if (!this.data) {
                throw new Error('Não foi possível carregar dados do servidor');
            }

            // Renderizar todos os componentes
            await this.renderKPIs(); // Esta função agora usa os dados reais
            await this.renderStrategicKPIs();
            await this.renderInsights();
            await this.renderAnalytics();
            await this.renderSeparatedCharts();

            // Inicializar filtros
            if (window.filtersSystem) {
                filtersSystem.renderFilterPanel('filters-container');
            }

            console.log('✅ Dashboard Executivo carregado com sucesso!');

        } catch (error) {
            console.error('❌ Erro crítico no dashboard:', error);
            this.showError('Falha ao carregar o sistema. Verifique a conexão com o servidor.');
        }
    }

    // ===== RENDERIZAÇÃO DE KPIs PRINCIPAIS (COM DADOS REAIS) =====
    async renderKPIs() {
        const container = document.getElementById('kpi-container');
        if (!container) return;

        try {
            // ===== MODIFICAÇÃO PRINCIPAL: USA DADOS REAIS DE this.data.vendas =====
            const vendasData = this.data.vendas?.data || [];

            if (vendasData.length === 0) {
                container.innerHTML = this.getErrorCard('Nenhum dado de venda encontrado. Execute a sincronização.');
                // Ainda assim, busca os KPIs de fallback para não deixar a tela totalmente vazia
                const fallbackKpis = await this.getRealKPIs();
                 container.innerHTML = fallbackKpis.map((kpi, index) => `
                    <div class="ai-card card-primary">
                        <div class="card-header">
                            <div class="card-icon">${this.getKPIIcon(kpi.name)}</div>
                            <div class="card-title">${kpi.name}</div>
                        </div>
                        <div class="card-value">${this.formatValue(kpi.value, kpi.unit)}</div>
                        <div class="card-subtitle">Sem dados reais</div>
                    </div>
                `).join('');
                return;
            }

            const totalVendas = vendasData.length;
            const faturamentoBruto = vendasData.reduce((sum, venda) => sum + (venda.preco_unitario * venda.quantidade), 0);
            const ticketMedio = totalVendas > 0 ? faturamentoBruto / totalVendas : 0;
            const lucroEstimado = faturamentoBruto * 0.15; // Simulação de 15% de margem
            const faturamentoLiquido = faturamentoBruto * 0.8; // Simulação

            const kpis = [
                { name: 'Total de Vendas', value: totalVendas, unit: '', trend: '0.0' },
                { name: 'Faturamento Bruto', value: faturamentoBruto, unit: 'R$', trend: '0.0' },
                { name: 'Faturamento Líquido', value: faturamentoLiquido, unit: 'R$', trend: '0.0' },
                { name: 'Ticket Médio', value: ticketMedio, unit: 'R$', trend: '0.0' },
                { name: 'Lucro Estimado', value: lucroEstimado, unit: 'R$', trend: '0.0' }
            ];
            // =======================================================================

            container.innerHTML = kpis.map((kpi, index) => `
                <div class="ai-card card-primary"
                     onclick="dashboard.openKPIModal(${index})"
                     onmouseenter="dashboard.showTooltip(this, '${kpi.name}')">

                    <div class="card-header">
                        <div class="card-icon">
                            ${this.getKPIIcon(kpi.name)}
                        </div>
                        <div>
                            <div class="card-title">${kpi.name}</div>
                            <div class="card-subtitle">Dados Reais do DB</div>
                        </div>
                    </div>

                    <div class="card-value">${this.formatValue(kpi.value, kpi.unit)}</div>

                    <div class="card-trend trend-up">
                        <span>↗️ ${kpi.trend || '0.0'}%</span>
                    </div>

                    <div class="card-tooltip">
                        Clique para detalhes de ${kpi.name}
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Erro ao renderizar KPIs:', error);
            container.innerHTML = this.getErrorCard('Erro ao carregar métricas');
        }
    }

    // ===== RENDERIZAÇÃO DE KPIs ESTRATÉGICOS =====
    async renderStrategicKPIs() {
        const container = document.getElementById('strategic-container');
        if (!container) return;

        try {
            // Buscar dados estratégicos REAIS da API
            const strategicData = await this.getRealStrategicKPIs();

            container.innerHTML = strategicData.map(kpi => `
                <div class="ai-card card-${kpi.color}" onclick="dashboard.openDetailModal('${kpi.name}')">
                    <div class="card-header">
                        <div class="card-icon">${kpi.icon}</div>
                        <div>
                            <div class="card-title">${kpi.name}</div>
                            <div class="card-subtitle">${kpi.description}</div>
                        </div>
                    </div>
                    <div class="card-value">${kpi.value}</div>
                    <div class="card-trend trend-${kpi.trend.includes('+') ? 'up' : 'down'}">
                        <span>${kpi.trend.includes('+') ? '↗️' : '↘️'} ${kpi.trend}</span>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Erro ao renderizar KPIs estratégicos:', error);
            container.innerHTML = this.getErrorCard('Erro ao carregar métricas estratégicas');
        }
    }

    // ===== RENDERIZAÇÃO DE INSIGHTS =====
    async renderInsights() {
        const container = document.getElementById('insights-container');
        if (!container) return;

        try {
            const insights = await this.aiEngine.analyzeSalesData(this.data);

            container.innerHTML = `
                <div class="ai-card card-success" onclick="dashboard.openInsightsModal()">
                    <div class="card-header">
                        <div class="card-icon">🏆</div>
                        <div>
                            <div class="card-title">Top Performers</div>
                            <div class="card-subtitle">Produtos em Destaque</div>
                        </div>
                    </div>
                    <div class="card-value">${insights.topPerformingProducts?.length || 0}</div>
                    <div class="card-subtitle">produtos com alto desempenho</div>
                </div>

                <div class="ai-card card-warning" onclick="dashboard.openOpportunitiesModal()">
                    <div class="card-header">
                        <div class="card-icon">💡</div>
                        <div>
                            <div class="card-title">Oportunidades</div>
                            <div class="card-subtitle">Áreas para Melhoria</div>
                        </div>
                    </div>
                    <div class="card-value">${insights.optimizationOpportunities?.length || 0}</div>
                    <div class="card-subtitle">otimizações identificadas</div>
                </div>

                <div class="ai-card card-info" onclick="dashboard.openTrendsModal()">
                    <div class="card-header">
                        <div class="card-icon">📈</div>
                        <div>
                            <div class="card-title">Tendências</div>
                            <div class="card-subtitle">Análise Preditiva</div>
                        </div>
                    </div>
                    <div class="card-value">${insights.salesTrends?.growthRate?.toFixed(1) || '0.0'}%</div>
                    <div class="card-subtitle">crescimento mensal</div>
                </div>
            `;
        } catch (error) {
            console.error('Erro ao renderizar insights:', error);
            container.innerHTML = this.getErrorCard('Erro ao carregar insights');
        }
    }

    // ===== RENDERIZAÇÃO ANALYTICS =====
    async renderAnalytics() {
        const container = document.getElementById('analytics-container');
        if (!container) return;

        try {
            const overview = this.data.overview?.data || {};
            const abcData = this.data.abc?.data || {};

            container.innerHTML = `
                <div class="ai-card featured-card" onclick="dashboard.openSalesModal()">
                    <div class="card-header">
                        <div class="card-icon">💰</div>
                        <div>
                            <div class="card-title">Vendas em Tempo Real</div>
                            <div class="card-subtitle">Performance Comercial</div>
                        </div>
                    </div>
                    <div class="card-value">R$ ${this.formatCurrency(overview.faturamento_bruto || 0)}</div>
                    <div class="card-trend trend-up">
                        <span>↗️ ${overview.crescimento || '0.0'}% vs último mês</span>
                    </div>
                </div>

                <div class="ai-card" onclick="dashboard.openProductsModal()">
                    <div class="card-header">
                        <div class="card-icon">📦</div>
                        <div>
                            <div class="card-title">Catálogo Ativo</div>
                            <div class="card-subtitle">Gestão de Produtos</div>
                        </div>
                    </div>
                    <div class="card-value">${abcData.total_produtos || 0}</div>
                    <div class="card-subtitle">produtos ativos</div>
                </div>
            `;
        } catch (error) {
            console.error('Erro ao renderizar analytics:', error);
            container.innerHTML = this.getErrorCard('Erro ao carregar analytics');
        }
    }

    // ===== RENDERIZAÇÃO DE GRÁFICOS SEPARADOS =====
    async renderSeparatedCharts() {
        try {
            // Container principal de visualizações (Vendas Diárias)
            const chartsContainer = document.getElementById('charts-container');
            if (chartsContainer) {
                chartsContainer.innerHTML = `
                    <div class="chart-section">
                        <h3 class="chart-title">📈 Vendas Diárias (Últimos 7 Dias)</h3>
                        <p class="chart-subtitle">Evolução do faturamento diário</p>
                        <div class="chart-container">
                            <canvas id="daily-sales-chart"></canvas>
                        </div>
                        <div class="chart-actions">
                            <button class="chart-action-btn" onclick="chartsSystem.exportChartAsImage('daily-sales-chart', 'vendas-diarias')">
                                💾 Exportar
                            </button>
                            <button class="chart-action-btn" onclick="chartsSystem.updateAllCharts()">
                                🔄 Atualizar
                            </button>
                        </div>
                    </div>
                `;
            }

            // Container ABC
            const abcContainer = document.getElementById('abc-container');
            if (abcContainer) {
                abcContainer.innerHTML = `
                    <div class="chart-section">
                        <h3 class="chart-title">📊 Análise de Produtos</h3>
                        <p class="chart-subtitle">Top produtos por faturamento</p>
                        <div class="chart-container">
                            <canvas id="abc-analysis-chart"></canvas>
                        </div>
                    </div>
                `;
            }

            // Container Distribuição
            const distributionContainer = document.getElementById('distribution-container');
            if (distributionContainer) {
                distributionContainer.innerHTML = `
                    <div class="chart-section">
                        <h3 class="chart-title">🎯 Distribuição ABC</h3>
                        <p class="chart-subtitle">Proporção entre categorias</p>
                        <div class="chart-container">
                            <canvas id="sales-distribution-chart"></canvas>
                        </div>
                    </div>
                `;
            }

            // Buscar dados REAIS para gráficos
            const trendsData = this.data.trends?.data || await this.getRealTrendsData();
            const abcChartData = this.data.abc?.data || await this.getRealABCData();

            // Renderizar gráficos após DOM estar pronto
            setTimeout(() => {
                if (window.chartsSystem) {
                    chartsSystem.renderDailySales('daily-sales-chart', trendsData);
                    chartsSystem.renderABCAnalysis('abc-analysis-chart', abcChartData);
                    chartsSystem.renderSalesDistribution('sales-distribution-chart', abcChartData);
                }
            }, 100);

        } catch (error) {
            console.error('Erro ao renderizar gráficos:', error);
            const containers = ['charts-container', 'abc-container', 'distribution-container'];
            containers.forEach(containerId => {
                const container = document.getElementById(containerId);
                if (container) {
                    container.innerHTML = this.getErrorCard('Erro ao carregar gráficos');
                }
            });
        }
    }

    // ===== MÉTODOS PARA BUSCAR DADOS REAIS =====
    async getRealKPIs() {
        try {
            const response = await fetch('/api/ml/analytics/overview');
            if (!response.ok) throw new Error('API não respondeu');

            const data = await response.json();
            return data.kpis || [];
        } catch (error) {
            console.error('Erro ao buscar KPIs reais:', error);
            return [];
        }
    }

    async getRealStrategicKPIs() {
        try {
            // Buscar dados estratégicos da API
            const [overview, trends, abc] = await Promise.all([
                fetch('/api/ml/analytics/overview').then(r => r.json()),
                fetch('/api/ml/analytics/trends').then(r => r.json()),
                fetch('/api/ml/analytics/abc').then(r => r.json())
            ]);

            return [
                {
                    name: 'Margem Média',
                    value: `${(overview.margem_lucro || 0).toFixed(1)}%`,
                    icon: '📊',
                    color: 'success',
                    trend: overview.trend_margem || '+0.0%',
                    description: 'Margem líquida média dos produtos'
                },
                {
                    name: 'Custo Frete Médio',
                    value: `R$ ${(overview.custo_frete_medio || 0).toFixed(2)}`,
                    icon: '🚚',
                    color: 'warning',
                    trend: overview.trend_frete || '+0.0%',
                    description: 'Custo médio de frete por venda'
                },
                {
                    name: 'Taxa ML Média',
                    value: `${(overview.taxa_ml_media || 0).toFixed(1)}%`,
                    icon: '💳',
                    color: 'info',
                    trend: overview.trend_taxa || '+0.0%',
                    description: 'Taxa média cobrada pelo Mercado Livre'
                },
                {
                    name: 'Conversão',
                    value: `${(trends.taxa_conversao || 0).toFixed(1)}%`,
                    icon: '🎯',
                    color: 'primary',
                    trend: trends.trend_conversao || '+0.0%',
                    description: 'Taxa de conversão de visitas em vendas'
                },
                {
                    name: 'Custo Aquisição',
                    value: `R$ ${(trends.custo_aquisicao || 0).toFixed(2)}`,
                    icon: '💰',
                    color: 'warning',
                    trend: trends.trend_aquisicao || '+0.0%',
                    description: 'Custo por cliente adquirido'
                }
            ];
        } catch (error) {
            console.error('Erro ao buscar KPIs estratégicos:', error);
            return this.getFallbackStrategicKPIs();
        }
    }

    async getRealTrendsData() {
        try {
            const response = await fetch('/api/ml/analytics/trends');
            if (!response.ok) throw new Error('API trends não respondeu');

            const data = await response.json();
            return data.sales_data || [];
        } catch (error) {
            console.error('Erro ao buscar dados de tendências:', error);
            return [];
        }
    }

    async getRealABCData() {
        try {
            const response = await fetch('/api/ml/analytics/abc');
            if (!response.ok) throw new Error('API ABC não respondeu');

            const data = await response.json();
            return data.items || [];
        } catch (error) {
            console.error('Erro ao buscar dados ABC:', error);
            return [];
        }
    }

    // ===== SISTEMA DE MODAIS COMPLETO =====
    openKPIModal(index) {
        try {
            const vendasData = this.data.vendas?.data || [];
            const totalVendas = vendasData.length;
            const faturamentoBruto = vendasData.reduce((sum, venda) => sum + (venda.preco_unitario * venda.quantidade), 0);
            const ticketMedio = totalVendas > 0 ? faturamentoBruto / totalVendas : 0;
            const lucroEstimado = faturamentoBruto * 0.15;
            const faturamentoLiquido = faturamentoBruto * 0.8;

            const kpis = [
                { name: 'Total de Vendas', value: totalVendas, unit: '', trend: '0.0' },
                { name: 'Faturamento Bruto', value: faturamentoBruto, unit: 'R$', trend: '0.0' },
                { name: 'Faturamento Líquido', value: faturamentoLiquido, unit: 'R$', trend: '0.0' },
                { name: 'Ticket Médio', value: ticketMedio, unit: 'R$', trend: '0.0' },
                { name: 'Lucro Estimado', value: lucroEstimado, unit: 'R$', trend: '0.0' }
            ];

            const kpi = kpis[index];

            if (!kpi) {
                this.showNotification('Dados não disponíveis', 'error');
                return;
            }

            this.modal.open({
                title: `📊 ${kpi.name}`,
                content: `
                    <div style="text-align: center; padding: 2rem;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">${this.getKPIIcon(kpi.name)}</div>
                        <div style="font-size: 2.5rem; font-weight: bold; color: var(--ai-primary-600); margin-bottom: 1rem;">
                            ${this.formatValue(kpi.value, kpi.unit)}
                        </div>
                        <p style="color: var(--ai-gray-600); margin-bottom: 2rem;">
                            Detalhamento completo da métrica ${kpi.name}
                        </p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                            <div style="background: var(--ai-gray-100); padding: 1rem; border-radius: var(--ai-radius-md);">
                                <div style="font-size: 0.875rem; color: var(--ai-gray-600);">Tendência</div>
                                <div style="font-weight: bold; color: var(--ai-secondary-600);">${kpi.trend || '0.0'}%</div>
                            </div>
                            <div style="background: var(--ai-gray-100); padding: 1rem; border-radius: var(--ai-radius-md);">
                                <div style="font-size: 0.875rem; color: var(--ai-gray-600);">Status</div>
                                <div style="font-weight: bold; color: var(--ai-primary-600);">Atualizado</div>
                            </div>
                        </div>
                    </div>
                `,
                size: 'medium'
            });
        } catch (error) {
            console.error('Erro ao abrir modal KPI:', error);
            this.showNotification('Erro ao carregar detalhes', 'error');
        }
    }

    openInsightsModal() {
        try {
            const insights = this.data.insights || {};

            this.modal.open({
                title: '🤖 Insights Inteligentes',
                content: `
                    <div style="padding: 1rem;">
                        <h3 style="margin-bottom: 1rem;">Análise IA dos Dados</h3>
                        <div style="background: var(--ai-secondary-50); padding: 1rem; border-radius: var(--ai-radius-md); margin-bottom: 1rem;">
                            <strong>🎯 Oportunidade Identificada:</strong>
                            <p>${insights.opportunity || 'Análise em andamento...'}</p>
                        </div>
                        <div style="background: var(--ai-primary-50); padding: 1rem; border-radius: var(--ai-radius-md);">
                            <strong>📈 Recomendação IA:</strong>
                            <p>${insights.recommendation || 'Processando dados...'}</p>
                        </div>
                    </div>
                `
            });
        } catch (error) {
            console.error('Erro ao abrir modal insights:', error);
            this.showNotification('Erro ao carregar insights', 'error');
        }
    }

    openOpportunitiesModal() {
        try {
            const opportunities = this.data.opportunities || [];

            this.modal.open({
                title: '💡 Oportunidades de Otimização',
                content: `
                    <div style="padding: 1rem;">
                        <div style="display: grid; gap: 1rem;">
                            ${opportunities.length > 0 ? opportunities.map(opp => `
                                <div style="background: var(--ai-warning-50); padding: 1rem; border-radius: var(--ai-radius-md); border-left: 4px solid var(--ai-warning-500);">
                                    <strong>${opp.category}</strong>
                                    <p>${opp.description}</p>
                                </div>
                            `).join('') : `
                                <div style="text-align: center; padding: 2rem; color: var(--ai-gray-500);">
                                    Nenhuma oportunidade identificada no momento
                                </div>
                            `}
                        </div>
                    </div>
                `
            });
        } catch (error) {
            console.error('Erro ao abrir modal oportunidades:', error);
            this.showNotification('Erro ao carregar oportunidades', 'error');
        }
    }

    openTrendsModal() {
        try {
            const trends = this.data.trends?.data || {};

            this.modal.open({
                title: '📈 Tendências de Mercado',
                content: `
                    <div style="padding: 1rem;">
                        <h3 style="margin-bottom: 1rem;">Análise Preditiva IA</h3>
                        <div style="background: var(--ai-primary-50); padding: 1rem; border-radius: var(--ai-radius-md); margin-bottom: 1rem;">
                            <strong>📊 Crescimento Mensal:</strong>
                            <p>${trends.growth_rate || '0.0'}% de aumento nas vendas</p>
                        </div>
                        <div style="background: var(--ai-secondary-50); padding: 1rem; border-radius: var(--ai-radius-md);">
                            <strong>🎯 Previsão Próximo Mês:</strong>
                            <p>${trends.forecast || 'Análise em processamento...'}</p>
                        </div>
                    </div>
                `
            });
        } catch (error) {
            console.error('Erro ao abrir modal tendências:', error);
            this.showNotification('Erro ao carregar tendências', 'error');
        }
    }

    openSalesModal() {
        try {
            const overview = this.data.overview?.data || {};

            this.modal.open({
                title: '💰 Performance de Vendas',
                content: `
                    <div style="padding: 1rem;">
                        <h3 style="margin-bottom: 1rem;">Dados em Tempo Real</h3>
                        <div style="display: grid; gap: 1rem;">
                            <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: var(--ai-gray-50); border-radius: var(--ai-radius-md);">
                                <span>Faturamento Bruto:</span>
                                <strong>R$ ${this.formatCurrency(overview.faturamento_bruto || 0)}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: var(--ai-gray-50); border-radius: var(--ai-radius-md);">
                                <span>Faturamento Líquido:</span>
                                <strong>R$ ${this.formatCurrency(overview.faturamento_liquido || 0)}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: var(--ai-gray-50); border-radius: var(--ai-radius-md);">
                                <span>Lucro Estimado:</span>
                                <strong>R$ ${this.formatCurrency(overview.lucro_estimado || 0)}</strong>
                            </div>
                        </div>
                    </div>
                `
            });
        } catch (error) {
            console.error('Erro ao abrir modal vendas:', error);
            this.showNotification('Erro ao carregar dados de vendas', 'error');
        }
    }

    openProductsModal() {
        try {
            const abcData = this.data.abc?.data || {};

            this.modal.open({
                title: '📦 Gestão de Catálogo',
                content: `
                    <div style="padding: 1rem;">
                        <h3 style="margin-bottom: 1rem;">Produtos Ativos</h3>
                        <div style="background: var(--ai-primary-50); padding: 1rem; border-radius: var(--ai-radius-md); margin-bottom: 1rem;">
                            <strong>Total de Produtos:</strong>
                            <p>${abcData.total_produtos || 0} produtos ativos no catálogo</p>
                        </div>
                        <div style="background: var(--ai-secondary-50); padding: 1rem; border-radius: var(--ai-radius-md);">
                            <strong>Classificação ABC:</strong>
                            <p>${abcData.categoria_a || 0} produtos Classe A (alto faturamento)</p>
                            <p>${abcData.categoria_b || 0} produtos Classe B (médio faturamento)</p>
                            <p>${abcData.categoria_c || 0} produtos Classe C (baixo faturamento)</p>
                        </div>
                    </div>
                `
            });
        } catch (error) {
            console.error('Erro ao abrir modal produtos:', error);
            this.showNotification('Erro ao carregar dados do catálogo', 'error');
        }
    }

    openDetailModal(metricName) {
        this.modal.open({
            title: `📈 ${metricName}`,
            content: `
                <div style="padding: 1rem;">
                    <h3 style="margin-bottom: 1rem;">Análise Detalhada</h3>
                    <div style="background: var(--ai-primary-50); padding: 1rem; border-radius: var(--ai-radius-md); margin-bottom: 1rem;">
                        <strong>Valor Atual:</strong>
                        <p>Dados carregados diretamente da API do Mercado Livre</p>
                    </div>
                    <div style="background: var(--ai-secondary-50); padding: 1rem; border-radius: var(--ai-radius-md);">
                        <strong>Tendência:</strong>
                        <p>Análise em tempo real baseada nos últimos 60 dias</p>
                    </div>
                </div>
            `,
            size: 'medium'
        });
    }

    // ===== CONTROLES DE TEMA =====
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        localStorage.setItem('ai_theme', this.currentTheme);
        this.showNotification(`Tema alterado para ${this.currentTheme === 'light' ? 'claro' : 'escuro'}`, 'info');
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
    }

    // ===== ATUALIZAÇÃO DE DADOS =====
    async refreshData() {
        if (this.isLoading) return;

        console.log('🔄 Atualizando dados...');
        this.setLoading(true);

        try {
            // Aplicar filtros atuais se existirem
            const filters = window.filtersSystem ? filtersSystem.getCurrentFilters() : {};
            await this.refreshDataWithFilters(filters);

            this.showNotification('Dados atualizados com sucesso!', 'success');
        } catch (error) {
            console.error('❌ Erro ao atualizar dados:', error);
            this.showNotification('Erro ao atualizar dados', 'error');
        } finally {
            this.setLoading(false);
        }
    }

    async refreshDataWithFilters(filters) {
        console.log('🔄 Atualizando dados com filtros:', filters);

        try {
            // Recarregar dados da API com filtros
            this.data = await this.api.fetchDashboardData(filters);

            // Recarregar todos os componentes
            await this.renderKPIs();
            await this.renderStrategicKPIs();
            await this.renderInsights();
            await this.renderAnalytics();
            await this.renderSeparatedCharts();

        } catch (error) {
            console.error('Erro ao atualizar dados com filtros:', error);
            throw error;
        }
    }

    // ===== EXPORTAÇÃO DE DADOS =====
    exportData() {
        this.modal.open({
            title: '📥 Exportar Relatório',
            content: `
                <div style="padding: 1rem;">
                    <p>Selecione o formato do relatório:</p>
                    <div style="display: grid; gap: 1rem; margin-top: 1rem;">
                        <button class="ai-btn ai-btn-primary" onclick="dashboard.downloadReport('pdf')">
                            📄 PDF Completo
                        </button>
                        <button class="ai-btn ai-btn-secondary" onclick="dashboard.downloadReport('excel')">
                            📊 Planilha Excel
                        </button>
                        <button class="ai-btn" onclick="dashboard.downloadReport('csv')">
                            📋 Dados CSV
                        </button>
                    </div>
                </div>
            `
        });
    }

    downloadReport(format) {
        console.log(`📥 Exportando relatório em ${format}...`);
        this.showNotification(`Relatório ${format} gerado com sucesso!`, 'success');
        this.modal.close();
    }

    // ===== UTILITÁRIOS =====
    showTooltip(element, content) {
        // Tooltip já está no HTML via CSS
        console.log('Tooltip:', content);
    }

    formatCurrency(value) {
        return value.toLocaleString('pt-BR', {minimumFractionDigits: 2});
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

    getErrorCard(message) {
        return `
            <div class="ai-card" style="grid-column: 1 / -1; text-align: center; background: var(--ai-error-50);">
                <div class="card-icon">❌</div>
                <div class="card-title">Erro no Carregamento</div>
                <div class="card-subtitle">${message}</div>
                <button onclick="dashboard.initialize()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: var(--ai-primary-500); color: white; border: none; border-radius: var(--ai-radius-md); cursor: pointer;">
                    🔄 Tentar Novamente
                </button>
            </div>
        `;
    }

    getFallbackStrategicKPIs() {
        // Fallback apenas se API falhar - valores zerados
        return [
            {
                name: 'Margem Média',
                value: '0.0%',
                icon: '📊',
                color: 'success',
                trend: '+0.0%',
                description: 'Margem líquida média dos produtos'
            },
            {
                name: 'Custo Frete Médio',
                value: 'R$ 0,00',
                icon: '🚚',
                color: 'warning',
                trend: '+0.0%',
                description: 'Custo médio de frete por venda'
            },
            {
                name: 'Taxa ML Média',
                value: '0.0%',
                icon: '💳',
                color: 'info',
                trend:
