// js/services/api-integration.js - VERSÃO FINAL, COMPLETA E INTEGRADA

class APIIntegration {
    constructor() {
        this.endpoints = {
            vendas: '/api/ml/vendas', // ÚNICO ENDPOINT FUNCIONAL
            // Os endpoints abaixo são placeholders para o futuro
            overview: '/api/ml/analytics/overview',
            trends: '/api/ml/analytics/trends',
            abc: '/api/ml/analytics/abc'
        };
    }

    async fetchDashboardData() {
        console.log(`📡 Chamando API principal: ${this.endpoints.vendas}`);
        try {
            // A única chamada real que faremos é para o endpoint de vendas
            const vendasResponse = await this.retryableFetch(this.endpoints.vendas);

            // Retornamos um objeto que o dashboard-manager espera,
            // com os dados de vendas no lugar certo.
            return {
                vendas: vendasResponse,
                // Os outros dados são placeholders para não quebrar o resto do código
                overview: { data: { kpis: [] } },
                trends: { data: { sales_data: [] } },
                abc: { data: { items: [] } }
            };
        } catch (error) {
            console.error(`❌ Falha grave ao buscar dados de ${this.endpoints.vendas}:`, error);
            return null;
        }
    }

    async retryableFetch(url, retries = 3) {
        for (let i = 0; i < retries; i++) {
            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`Erro de servidor: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.warn(`Tentativa ${i + 1} de ${retries} para ${url} falhou.`, error.message);
                if (i === retries - 1) {
                    throw error;
                }
                await new Promise(res => setTimeout(res, 1000));
            }
        }
    }
}
