// js/services/api-integration.js - VERSÃO COMPLETA E RESILIENTE

class APIIntegration {
    constructor() {
        this.endpoints = {
            overview: '/api/ml/analytics/overview',
            trends: '/api/ml/analytics/trends',
            abc: '/api/ml/analytics/abc',
            topItems: '/api/ml/analytics/top-items',
            syncStatus: '/api/ml/sync/status',
            // Adicionando o novo endpoint de dados brutos
            vendas: '/api/ml/vendas'
        };
    }

    async fetchDashboardData() {
        console.log('📡 Buscando todos os dados do dashboard...');
        try {
            // Executa todas as chamadas em paralelo
            const [overview, trends, abc, vendas] = await Promise.all([
                this.retryableFetch(this.endpoints.overview).catch(e => { console.error('Falha ao buscar overview:', e); return { data: {} }; }),
                this.retryableFetch(this.endpoints.trends).catch(e => { console.error('Falha ao buscar trends:', e); return { data: {} }; }),
                this.retryableFetch(this.endpoints.abc).catch(e => { console.error('Falha ao buscar abc:', e); return { data: {} }; }),
                this.retryableFetch(this.endpoints.vendas).catch(e => { console.error('Falha ao buscar vendas brutas:', e); return { data: [] }; })
            ]);

            // Combina os resultados em um único objeto de dados
            const dashboardData = {
                overview: overview,
                trends: trends,
                abc: abc,
                vendas: vendas // Adiciona os dados brutos ao objeto principal
            };

            console.log('✅ Dados combinados do dashboard recebidos.');
            return dashboardData;

        } catch (error) {
            console.error('❌ Falha grave ao buscar dados do dashboard:', error);
            return null;
        }
    }

    async retryableFetch(url, retries = 2) {
        for (let i = 0; i < retries; i++) {
            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`Erro de servidor: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.warn(`Tentativa ${i + 1} para ${url} falhou.`, error.message);
                if (i === retries - 1) throw error;
                await new Promise(res => setTimeout(res, 500));
            }
        }
    }
}
