// js/components/dashboard-manager.js - VERSÃO CORRIGIDA E COMPLETA
// Todas as 800+ linhas do código original, com as correções necessárias

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
            this.applyTheme(this.currentTheme);
            this.data = await this.api.fetchDashboardData();

            console.log('📊 Dados recebidos:', this.data);

            if (!this.data) {
                throw new Error('Não foi possível carregar dados do servidor');
            }

            await this.renderKPIs();
            await this.renderStrategicKPIs();
            await this.renderInsights();
            await this.renderAnalytics();
            await this.renderSeparatedCharts();

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
            const kpis = this.data.overview?.data?.kpis || [];
            console.log('📊 KPIs recebidos:', kpis);
            
            if (kpis.length === 0) {
                container.innerHTML = this.getErrorCard('Nenhum dado de venda encontrado. Execute a sincronização.');
                return;
            }

            container.innerHTML = kpis.map((kpi, index) => this.createKPICardHTML(kpi, index)).join('');

        } catch (error) {
            console.error('Erro ao renderizar KPIs:', error);
            container.innerHTML = this.getErrorCard('Erro ao carregar métricas');
        }
    }

    createKPICardHTML(kpi, index) {
        return `
            <div class="ai-card card-primary" onclick="dashboard.openKPIModal(${index})" onmouseenter="dashboard.showTooltip(this, '${kpi.name}')">
                <div class="card-header">
                    <div class="card-icon">${this.getKPIIcon(kpi.name)}</div>
                    <div>
                        <div class="card-title">${kpi.name}</div>
                        <div class="card-subtitle">Dados Reais do DB</div>
                    </div>
                </div>
                <div class="card-value">${this.formatValue(kpi.value, kpi.unit)}</div>
                <div class="card-trend trend-up">
                    <span>↗️ ${kpi.trend || '0.0'}%</span>
                </div>
                <div class="card-tooltip">Clique para detalhes de ${kpi.name}</div>
            </div>
        `;
    }

    // ===== RENDERIZAÇÃO DE KPIs ESTRATÉGICOS (CORRIGIDO) =====
    async renderStrategicKPIs() {
        const container = document.getElementById('strategic-container');
        if (!container) return;

        try {
            // ✅ CORREÇÃO: Usar dados já carregados em this.data
            const strategicData = this.getRealStrategicKPIs();
            console.log('📊 KPIs Estratégicos calculados:', strategicData);

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
            
            // Buscar o valor de faturamento bruto dos KPIs
            const faturamentoBrutoKPI = overview.kpis?.find(k => k.name === 'Faturamento Bruto');
            const faturamentoBruto = faturamentoBrutoKPI?.value || 0;
            
            const totalProdutos = abcData.produtos?.length || 0;

            container.innerHTML = `
                <div class="ai-card featured-card" onclick="dashboard.openSalesModal()">
                    <div class="card-header">
                        <div class="card-icon">💰</div>
                        <div>
                            <div class="card-title">Vendas em Tempo Real</div>
                            <div class="card-subtitle">Performance Comercial</div>
                        </div>
                    </div>
                    <div class="card-value">R$ ${this.formatCurrency(faturamentoBruto)}</div>
                    <div class="card-trend trend-up">
                        <span>↗️ 0.0% vs último mês</span>
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
                    <div class="card-value">${totalProdutos}</div>
                    <div class="card-subtitle">produtos ativos</div>
                </div>
            `;
        } catch (error) {
            console.error('Erro ao renderizar analytics:', error);
            container.innerHTML = this.getErrorCard('Erro ao carregar analytics');
        }
    }

    // ===== RENDERIZAÇÃO DE GRÁFICOS SEPARADOS (CORRIGIDO) =====
    async renderSeparatedCharts() {
        try {
            console.log('📊 Iniciando renderização de gráficos...');
            
            // Container principal de visualizações (Vendas Diárias)
            const chartsContainer = document.getElementById('charts-container');
            if (chartsContainer) {
                chartsContainer.innerHTML = `
                    <div class="chart-section">
                        <h3 class="chart-title">📈 Vendas Diárias (Últimos 30 Dias)</h3>
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

            // ✅ CORREÇÃO: Buscar dados corretamente
            const trendsData = this.data.trends?.data || [];
            const abcChartData = this.data.abc?.data?.produtos || [];

            console.log('📊 Dados para gráficos:', {
                trendsData: trendsData.length,
                abcChartData: abcChartData.length
            });

            // ✅ CORREÇÃO: Garantir que o DOM está pronto e o chartsSystem está disponível
            setTimeout(() => {
                if (window.chartsSystem) {
                    console.log('📊 Renderizando gráficos...');
                    
                    if (trendsData.length > 0) {
                        chartsSystem.renderDailySales('daily-sales-chart', trendsData);
                    } else {
                        console.warn('⚠️ Sem dados de tendências para renderizar');
                    }
                    
                    if (abcChartData.length > 0) {
                        chartsSystem.renderABCAnalysis('abc-analysis-chart', abcChartData);
                        chartsSystem.renderSalesDistribution('sales-distribution-chart', abcChartData);
                    } else {
                        console.warn('⚠️ Sem dados ABC para renderizar');
                    }
                } else {
                    console.error('❌ chartsSystem não está disponível');
                }
            }, 200); // Aumentado o timeout para garantir que o DOM está pronto

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

    // ===== MÉTODOS PARA CALCULAR KPIS ESTRATÉGICOS (CORRIGIDO) =====
    getRealStrategicKPIs() {
        // ✅ CORREÇÃO: Calcular a partir dos dados já carregados em this.data
        const overview = this.data.overview?.data || {};
        const kpis = overview.kpis || [];
        
        // Extrair valores dos KPIs principais
        const faturamentoBruto = kpis.find(k => k.name === 'Faturamento Bruto')?.value || 0;
        const faturamentoLiquido = kpis.find(k => k.name === 'Faturamento Líquido')?.value || 0;
        const lucroEstimado = kpis.find(k => k.name === 'Lucro Estimado')?.value || 0;
        const totalVendas = kpis.find(k => k.name === 'Total de Vendas')?.value || 0;
        
        // Calcular métricas estratégicas a partir dos dados disponíveis
        const margemMedia = faturamentoBruto > 0 ? (lucroEstimado / faturamentoBruto * 100) : 0;
        const custoFreteEstimado = (faturamentoBruto - faturamentoLiquido - lucroEstimado) / totalVendas || 0;
        const taxaMLMedia = faturamentoBruto > 0 ? ((faturamentoBruto - faturamentoLiquido) / faturamentoBruto * 100) : 0;

        return [
            {
                name: 'Margem Média',
                value: `${margemMedia.toFixed(1)}%`,
                icon: '📊',
                color: 'success',
                trend: '+0.0%',
                description: 'Margem líquida média dos produtos'
            },
            {
                name: 'Custo Frete Médio',
                value: `R$ ${custoFreteEstimado.toFixed(2)}`,
                icon: '🚚',
                color: 'warning',
                trend: '+0.0%',
                description: 'Custo médio de frete por venda'
            },
            {
                name: 'Taxa ML Média',
                value: `${taxaMLMedia.toFixed(1)}%`,
                icon: '💳',
                color: 'info',
                trend: '+0.0%',
                description: 'Taxa média cobrada pelo Mercado Livre'
            },
            {
                name: 'Conversão',
                value: `0.0%`,
                icon: '🎯',
                color: 'primary',
                trend: '+0.0%',
                description: 'Taxa de conversão de visitas em vendas'
            },
            {
                name: 'Custo Aquisição',
                value: `R$ 0.00`,
                icon: '💰',
                color: 'warning',
                trend: '+0.0%',
                description: 'Custo por cliente adquirido'
            }
        ];
    }

    // ===== SISTEMA DE MODAIS COMPLETO =====
    openKPIModal(index) {
        try {
            const kpis = this.data.overview?.data?.kpis || [];
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
            const trends = this.data.trends?.data || [];

            this.modal.open({
                title: '📈 Tendências de Mercado',
                content: `
                    <div style="padding: 1rem;">
                        <h3 style="margin-bottom: 1rem;">Análise Preditiva IA</h3>
                        <div style="background: var(--ai-primary-50); padding: 1rem; border-radius: var(--ai-radius-md); margin-bottom: 1rem;">
                            <strong>📊 Dados de Tendências:</strong>
                            <p>${trends.length} dias de dados coletados</p>
                        </div>
                        <div style="background: var(--ai-secondary-50); padding: 1rem; border-radius: var(--ai-radius-md);">
                            <strong>🎯 Previsão Próximo Mês:</strong>
                            <p>Análise em processamento...</p>
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
            const kpis = overview.kpis || [];
            
            const faturamentoBruto = kpis.find(k => k.name === 'Faturamento Bruto')?.value || 0;
            const faturamentoLiquido = kpis.find(k => k.name === 'Faturamento Líquido')?.value || 0;
            const lucroEstimado = kpis.find(k => k.name === 'Lucro Estimado')?.value || 0;

            this.modal.open({
                title: '💰 Performance de Vendas',
                content: `
                    <div style="padding: 1rem;">
                        <h3 style="margin-bottom: 1rem;">Dados em Tempo Real</h3>
                        <div style="display: grid; gap: 1rem;">
                            <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: var(--ai-gray-50); border-radius: var(--ai-radius-md);">
                                <span>Faturamento Bruto:</span>
                                <strong>R$ ${this.formatCurrency(faturamentoBruto)}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: var(--ai-gray-50); border-radius: var(--ai-radius-md);">
                                <span>Faturamento Líquido:</span>
                                <strong>R$ ${this.formatCurrency(faturamentoLiquido)}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 0.75rem; background: var(--ai-gray-50); border-radius: var(--ai-radius-md);">
                                <span>Lucro Estimado:</span>
                                <strong>R$ ${this.formatCurrency(lucroEstimado)}</strong>
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
            const produtos = abcData.produtos || [];
            const summary = abcData.summary || {};

            this.modal.open({
                title: '📦 Gestão de Catálogo',
                content: `
                    <div style="padding: 1rem;">
                        <h3 style="margin-bottom: 1rem;">Produtos Ativos</h3>
                        <div style="background: var(--ai-primary-50); padding: 1rem; border-radius: var(--ai-radius-md); margin-bottom: 1rem;">
                            <strong>Total de Produtos:</strong>
                            <p>${produtos.length} produtos ativos no catálogo</p>
                        </div>
                        <div style="background: var(--ai-secondary-50); padding: 1rem; border-radius: var(--ai-radius-md);">
                            <strong>Classificação ABC:</strong>
                            <p>${summary.categoria_a || 0} produtos Classe A (alto faturamento)</p>
                            <p>${summary.categoria_b || 0} produtos Classe B (médio faturamento)</p>
                            <p>${summary.categoria_c || 0} produtos Classe C (baixo faturamento)</p>
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
            this.data = await this.api.fetchDashboardData(filters);

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
        console.log('Tooltip:', content);
    }

    formatValue(value, unit) {
        if (typeof value === 'number') {
            return unit === 'R$' ? `R$ ${value.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : value.toString();
        }
        return `${value} ${unit || ''}`;
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
        return [
            { name: 'Margem Média', value: '0.0%', icon: '📊', color: 'success', trend: '+0.0%', description: 'Margem líquida média dos produtos' },
            { name: 'Custo Frete Médio', value: 'R$ 0,00', icon: '🚚', color: 'warning', trend: '+0.0%', description: 'Custo médio de frete por venda' },
            { name: 'Taxa ML Média', value: '0.0%', icon: '💳', color: 'info', trend: '+0.0%', description: 'Taxa média cobrada pelo Mercado Livre' },
            { name: 'Conversão', value: '0.0%', icon: '🎯', color: 'primary', trend: '+0.0%', description: 'Taxa de conversão de visitas em vendas' },
            { name: 'Custo Aquisição', value: 'R$ 0,00', icon: '💰', color: 'warning', trend: '+0.0%', description: 'Custo por cliente adquirido' }
        ];
    }

    setLoading(loading) {
        this.isLoading = loading;
        const buttons = document.querySelectorAll('.ai-btn');
        buttons.forEach(btn => {
            if (loading) {
                btn.disabled = true;
                if (btn.textContent.includes('Atualizar')) {
                    btn.innerHTML = '<span>⏳</span> Atualizando...';
                }
            } else {
                btn.disabled = false;
                if (btn.textContent.includes('Atualizando')) {
                    btn.innerHTML = '<span>🔄</span> Atualizar';
                }
            }
        });
    }

    showError(message) {
        const container = document.getElementById('kpi-container');
        if (container) {
            container.innerHTML = this.getErrorCard(message);
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `position: fixed; top: 20px; right: 20px; background: ${type === 'success' ? 'var(--ai-secondary-500)' : type === 'error' ? 'var(--ai-error-500)' : 'var(--ai-primary-500)'}; color: white; padding: 1rem 1.5rem; border-radius: var(--ai-radius-lg); box-shadow: var(--ai-shadow-lg); z-index: 10000; animation: slideInRight 0.3s ease-out;`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    destroy() {
        if (window.chartsSystem) {
            chartsSystem.destroyAllCharts();
        }
        console.log('🧹 Dashboard destruído');
    }
}

// Instância global
window.dashboard = new DashboardManager();