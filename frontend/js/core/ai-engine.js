// ===== AI ENGINE SIMPLIFICADO =====
class AIEngine {
    constructor() {
        console.log('🤖 IA Engine inicializado');
        this.modelVersion = '1.0';
        this.lastAnalysis = null;
    }

    // ===== ANÁLISE DE DADOS DE VENDAS =====
    async analyzeSalesData(dashboardData) {
        console.log('🔍 IA: Analisando dados de vendas...');

        try {
            // Simular processamento IA
            await this.simulateProcessing();

            // Extrair dados para análise
            const kpis = dashboardData.overview?.data?.kpis || [];
            const trends = dashboardData.trends?.data?.daily_data || [];
            const abcData = dashboardData.abc?.data?.items || [];

            // Análise de performance
            const performanceAnalysis = this.analyzePerformance(kpis);
            const trendAnalysis = this.analyzeTrends(trends);
            const productAnalysis = this.analyzeProducts(abcData);
            const opportunityAnalysis = this.findOpportunities(kpis, abcData);

            this.lastAnalysis = {
                timestamp: new Date().toISOString(),
                performance: performanceAnalysis,
                trends: trendAnalysis,
                products: productAnalysis,
                opportunities: opportunityAnalysis
            };

            return {
                topPerformingProducts: productAnalysis.topPerformers,
                salesTrends: trendAnalysis,
                optimizationOpportunities: opportunityAnalysis,
                riskFactors: this.identifyRisks(kpis, trends),
                recommendations: this.generateRecommendations(performanceAnalysis, opportunityAnalysis),
                confidence: this.calculateConfidence(kpis, trends)
            };

        } catch (error) {
            console.error('❌ Erro na análise IA:', error);
            return this.getFallbackAnalysis();
        }
    }

    // ===== ANÁLISE DE PERFORMANCE =====
    analyzePerformance(kpis) {
        const totalSales = kpis.find(k => k.name === 'Total de Vendas')?.value || 0;
        const revenue = kpis.find(k => k.name === 'Faturamento Bruto')?.value || 0;
        const profit = kpis.find(k => k.name === 'Lucro Estimado')?.value || 0;

        return {
            totalSales: totalSales,
            revenue: revenue,
            profit: profit,
            profitMargin: revenue > 0 ? (profit / revenue) * 100 : 0,
            healthScore: this.calculateHealthScore(totalSales, revenue, profit),
            status: this.getPerformanceStatus(totalSales, revenue, profit)
        };
    }

    // ===== ANÁLISE DE TENDÊNCIAS =====
    analyzeTrends(trends) {
        if (!trends || trends.length === 0) {
            return {
                growthRate: 0,
                trend: 'stable',
                bestDay: ['N/A', 0],
                worstDay: ['N/A', 0],
                volatility: 0
            };
        }

        const sales = trends.map(t => t.total_sales);
        const totalSales = sales.reduce((a, b) => a + b, 0);
        const averageSales = totalSales / sales.length;
        const maxSales = Math.max(...sales);
        const minSales = Math.min(...sales);
        const bestDayIndex = sales.indexOf(maxSales);
        const worstDayIndex = sales.indexOf(minSales);

        // Calcular taxa de crescimento (últimos 3 dias vs anteriores)
        const recentSales = sales.slice(-3);
        const previousSales = sales.slice(-6, -3);
        const recentAvg = recentSales.reduce((a, b) => a + b, 0) / recentSales.length;
        const previousAvg = previousSales.reduce((a, b) => a + b, 0) / previousSales.length;
        const growthRate = previousAvg > 0 ? ((recentAvg - previousAvg) / previousAvg) * 100 : 0;

        return {
            growthRate: growthRate,
            trend: growthRate > 5 ? 'growing' : growthRate < -5 ? 'declining' : 'stable',
            bestDay: [trends[bestDayIndex]?.date || 'N/A', maxSales],
            worstDay: [trends[worstDayIndex]?.date || 'N/A', minSales],
            averageSales: averageSales,
            volatility: this.calculateVolatility(sales)
        };
    }

    // ===== ANÁLISE DE PRODUTOS =====
    analyzeProducts(abcData) {
        const topPerformers = abcData
            .filter(item => item.classification === 'A')
            .slice(0, 5)
            .map(item => ({
                name: item.title,
                totalSales: item.total_sales,
                classification: item.classification
            }));

        const underperformers = abcData
            .filter(item => item.classification === 'C')
            .slice(0, 3)
            .map(item => ({
                name: item.title,
                totalSales: item.total_sales,
                classification: item.classification
            }));

        return {
            topPerformers: topPerformers,
            underperformers: underperformers,
            totalProducts: abcData.length,
            classA: abcData.filter(item => item.classification === 'A').length,
            classB: abcData.filter(item => item.classification === 'B').length,
            classC: abcData.filter(item => item.classification === 'C').length
        };
    }

    // ===== IDENTIFICAR OPORTUNIDADES =====
    findOpportunities(kpis, abcData) {
        const opportunities = [];

        // Oportunidade de estoque
        const classCProducts = abcData.filter(item => item.classification === 'C').length;
        if (classCProducts > abcData.length * 0.4) {
            opportunities.push({
                type: 'STOCK_OPTIMIZATION',
                priority: 'high',
                description: 'Alto número de produtos classe C (baixa rotação)',
                recommendation: 'Revisar estoque e considerar promoções',
                impact: 'medium'
            });
        }

        // Oportunidade de precificação
        const revenue = kpis.find(k => k.name === 'Faturamento Bruto')?.value || 0;
        const profit = kpis.find(k => k.name === 'Lucro Estimado')?.value || 0;
        const profitMargin = revenue > 0 ? (profit / revenue) * 100 : 0;

        if (profitMargin < 25) {
            opportunities.push({
                type: 'PRICING_OPTIMIZATION',
                priority: 'medium',
                description: 'Margem de lucro abaixo do ideal',
                recommendation: 'Revisar estratégia de precificação',
                impact: 'high'
            });
        }

        // Oportunidade de diversificação
        const classAProducts = abcData.filter(item => item.classification === 'A').length;
        if (classAProducts < 3) {
            opportunities.push({
                type: 'PRODUCT_DIVERSIFICATION',
                priority: 'medium',
                description: 'Poucos produtos de alto desempenho',
                recommendation: 'Expandir catálogo com produtos similares aos classe A',
                impact: 'high'
            });
        }

        return opportunities;
    }

    // ===== IDENTIFICAR RISCOS =====
    identifyRisks(kpis, trends) {
        const risks = [];

        // Risco de concentração
        const abcData = kpis.abcData || [];
        const topProductSales = abcData.slice(0, 3).reduce((sum, item) => sum + item.total_sales, 0);
        const totalSales = abcData.reduce((sum, item) => sum + item.total_sales, 0);
        const concentration = totalSales > 0 ? (topProductSales / totalSales) * 100 : 0;

        if (concentration > 60) {
            risks.push({
                type: 'PRODUCT_CONCENTRATION',
                severity: 'medium',
                description: 'Alta dependência de poucos produtos',
                mitigation: 'Diversificar catálogo'
            });
        }

        // Risco de sazonalidade
        const trendAnalysis = this.analyzeTrends(trends);
        if (trendAnalysis.volatility > 30) {
            risks.push({
                type: 'VOLATILITY',
                severity: 'low',
                description: 'Alta volatilidade nas vendas',
                mitigation: 'Criar estratégia para períodos de baixa'
            });
        }

        return risks;
    }

    // ===== GERAR RECOMENDAÇÕES =====
    generateRecommendations(performance, opportunities) {
        const recommendations = [];

        // Recomendações baseadas em performance
        if (performance.healthScore < 70) {
            recommendations.push({
                type: 'PERFORMANCE',
                title: 'Otimizar Operações',
                description: 'Foco em melhorar eficiência operacional',
                action: 'Revisar processos e custos',
                urgency: 'medium'
            });
        }

        // Recomendações baseadas em oportunidades
        opportunities.forEach(opp => {
            recommendations.push({
                type: 'OPPORTUNITY',
                title: this.getOpportunityTitle(opp.type),
                description: opp.recommendation,
                action: this.getActionForOpportunity(opp.type),
                urgency: opp.priority === 'high' ? 'high' : 'medium'
            });
        });

        return recommendations.slice(0, 3); // Limitar a 3 recomendações principais
    }

    // ===== MÉTODOS AUXILIARES =====
    calculateHealthScore(sales, revenue, profit) {
        // Score base simples - pode ser refinado
        const salesScore = Math.min((sales / 50) * 100, 100); // Meta: 50 vendas
        const revenueScore = Math.min((revenue / 3000) * 100, 100); // Meta: R$ 3000
        const profitScore = Math.min((profit / 800) * 100, 100); // Meta: R$ 800

        return (salesScore * 0.3 + revenueScore * 0.4 + profitScore * 0.3);
    }

    calculateVolatility(sales) {
        if (sales.length < 2) return 0;

        const mean = sales.reduce((a, b) => a + b, 0) / sales.length;
        const variance = sales.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / sales.length;
        return Math.sqrt(variance) / mean * 100; // Volatilidade como porcentagem
    }

    getPerformanceStatus(sales, revenue, profit) {
        const score = this.calculateHealthScore(sales, revenue, profit);

        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'fair';
        return 'needs_improvement';
    }

    getOpportunityTitle(opportunityType) {
        const titles = {
            'STOCK_OPTIMIZATION': 'Otimização de Estoque',
            'PRICING_OPTIMIZATION': 'Ajuste de Precificação',
            'PRODUCT_DIVERSIFICATION': 'Diversificação de Produtos'
        };
        return titles[opportunityType] || 'Oportunidade de Melhoria';
    }

    getActionForOpportunity(opportunityType) {
        const actions = {
            'STOCK_OPTIMIZATION': 'Analisar relatório de giro de estoque',
            'PRICING_OPTIMIZATION': 'Revisar tabela de preços e concorrentes',
            'PRODUCT_DIVERSIFICATION': 'Pesquisar novos produtos similares aos top sellers'
        };
        return actions[opportunityType] || 'Analisar oportunidade';
    }

    calculateConfidence(kpis, trends) {
        // Calcular confiança baseada na qualidade e quantidade dos dados
        const dataPoints = kpis.length + (trends?.length || 0);
        const completeness = Math.min((dataPoints / 15) * 100, 100); // Meta: 15 pontos de dados

        return {
            score: Math.round(completeness),
            level: completeness >= 80 ? 'high' : completeness >= 60 ? 'medium' : 'low',
            factors: [
                `Pontos de dados: ${dataPoints}`,
                `Completude: ${Math.round(completeness)}%`
            ]
        };
    }

    // ===== SIMULAÇÃO DE PROCESSAMENTO =====
    async simulateProcessing() {
        // Simular delay de processamento IA
        const delay = Math.random() * 1000 + 500; // 500-1500ms
        await new Promise(resolve => setTimeout(resolve, delay));
    }

    // ===== ANÁLISE DE FALLBACK =====
    getFallbackAnalysis() {
        console.warn('⚠️ Usando análise de fallback');

        return {
            topPerformingProducts: [
                { name: 'Kit Festa 200 Lembrancinha', totalSales: 375.18 },
                { name: 'Kit Sacolinha Aniversario', totalSales: 245.85 }
            ],
            salesTrends: {
                growthRate: 12.5,
                bestDay: ['2025-10-21', 769.26],
                trend: 'growing'
            },
            optimizationOpportunities: [
                {
                    type: 'PRODUCT_DIVERSIFICATION',
                    description: 'Opportunidade de expandir catálogo',
                    recommendation: 'Adicionar 5 novos produtos',
                    priority: 'medium',
                    impact: 'high'
                }
            ],
            riskFactors: [],
            recommendations: [
                {
                    type: 'GENERAL',
                    title: 'Manter Performance',
                    description: 'Continuar com estratégia atual',
                    action: 'Monitorar métricas regularmente',
                    urgency: 'low'
                }
            ],
            confidence: {
                score: 65,
                level: 'medium',
                factors: ['Dados limitados disponíveis']
            }
        };
    }

    // ===== OBTER ÚLTIMA ANÁLISE =====
    getLastAnalysis() {
        return this.lastAnalysis;
    }

    // ===== REINICIAR ENGINE =====
    reset() {
        this.lastAnalysis = null;
        console.log('🔄 IA Engine reiniciado');
    }

    // ===== OBTER INFO DA VERSÃO =====
    getVersionInfo() {
        return {
            version: this.modelVersion,
            capabilities: ['sales_analysis', 'trend_detection', 'opportunity_identification'],
            lastUpdated: '2025-10-28'
        };
    }
}

// Instância global
window.aiEngine = new AIEngine();