/**
 * @class APIIntegration
 * @description Centraliza todas as chamadas à API do backend.
 *
 * @version 2.0 - Otimizada e Corrigida para CORS
 * [CORREÇÃO] As URLs agora são relativas (ex: '/api/...') para evitar
 * problemas de CORS durante o desenvolvimento local (localhost vs 127.0.0.1).
 */
class APIIntegration {
    constructor() {
        // [CORREÇÃO] A base da URL não é mais necessária aqui, pois usaremos caminhos relativos.
        this.endpoints = {
            overview: '/api/ml/analytics/overview',
            trends: '/api/ml/analytics/trends',
            abc: '/api/ml/analytics/abc',
            topItems: '/api/ml/analytics/top-items',
            syncStatus: '/api/ml/sync/status'
            // Adicione outros endpoints aqui se necessário
        };
    }

    /**
     * Busca dados do dashboard de forma centralizada.
     * @param {string|object} options - Pode ser uma string (nome do endpoint) ou um objeto com filtros.
     * @returns {Promise<object>} - Os dados retornados pela API.
     */
    async fetchDashboardData(options) {
        let endpointKey = 'overview'; // Endpoint padrão
        let queryParams = '';

        if (typeof options === 'string') {
            endpointKey = options;
        } else if (typeof options === 'object' && options !== null) {
            endpointKey = options.endpoint || endpointKey;
            // Lógica para construir query params a partir de filtros (se houver)
            const filters = options.filters || {};
            const params = new URLSearchParams();
            for (const key in filters) {
                if (filters[key]) {
                    params.append(key, filters[key]);
                }
            }
            queryParams = params.toString();
        }

        const url = this.endpoints[endpointKey] || this.endpoints.overview;
        const finalUrl = queryParams ? `${url}?${queryParams}` : url;

        console.log(`📡 Chamando API: ${finalUrl}`);

        try {
            // Usa a função de fetch com tentativas
            const data = await this.retryableFetch(finalUrl);
            return { data }; // Retorna um objeto para manter a consistência
        } catch (error) {
            console.error(`❌ Falha grave ao buscar dados de ${finalUrl}:`, error);
            // Retorna um objeto com `data` como null para que o DashboardManager possa tratar o erro.
            return { data: null };
        }
    }

    /**
     * Função de fetch que tenta novamente em caso de falha de rede.
     * @param {string} url - A URL para a requisição.
     * @param {number} retries - O número de tentativas.
     * @returns {Promise<object>} - O JSON retornado pela API.
     */
    async retryableFetch(url, retries = 3) {
        for (let i = 0; i < retries; i++) {
            try {
                const response = await fetch(url);

                if (!response.ok) {
                    // Se o status não for OK (ex: 404, 500), joga um erro.
                    throw new Error(`Erro de servidor: ${response.status} ${response.statusText}`);
                }

                return await response.json(); // Sucesso, retorna os dados em JSON.

            } catch (error) {
                console.warn(`Tentativa ${i + 1} de ${retries} para ${url} falhou.`, error.message);
                if (i === retries - 1) {
                    // Se for a última tentativa, joga o erro para ser pego pelo `fetchDashboardData`.
                    throw error;
                }
                // Espera um pouco antes de tentar novamente
                await new Promise(res => setTimeout(res, 1000));
            }
        }
    }
}
