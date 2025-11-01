// js/services/api-integration.js - VERSÃO CORRIGIDA E COMPLETA
// Sistema de integração com API do backend - ESTRUTURA DE DADOS NORMALIZADA

class APIIntegration {
    constructor() {
        this.baseURL = '/api/ml';
        this.retryAttempts = 3;
        this.retryDelay = 1000;
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutos
    }

    // ===== MÉTODO PRINCIPAL: BUSCAR DADOS DO DASHBOARD =====
    async fetchDashboardData() {
        console.log('📡 APIIntegration: Iniciando busca de dados...');

        try {
            // Buscar dados de todas as APIs em paralelo
            const [overviewResponse, trendsResponse, abcResponse] = await Promise.all([
                this.retryableFetch(`${this.baseURL}/analytics/overview`),
                this.retryableFetch(`${this.baseURL}/analytics/trends`),
                this.retryableFetch(`${this.baseURL}/analytics/abc`)
            ]);

            console.log('📦 Respostas brutas recebidas:');
            console.log('  - Overview:', overviewResponse);
            console.log('  - Trends:', trendsResponse);
            console.log('  - ABC:', abcResponse);

            // ✅ CORREÇÃO CRÍTICA: Normalizar estrutura de dados
            const normalizedData = {
                overview: {
                    data: this.normalizeOverviewData(overviewResponse)
                },
                trends: {
                    data: this.normalizeTrendsData(trendsResponse)
                },
                abc: {
                    data: this.normalizeABCData(abcResponse)
                }
            };

            console.log('✅ Dados normalizados:', normalizedData);
            console.log('✅ KPIs disponíveis:', normalizedData.overview.data.kpis);

            return normalizedData;

        } catch (error) {
            console.error('❌ Erro ao buscar dados do dashboard:', error);
            return this.getFallbackData();
        }
    }

    // ===== NORMALIZAÇÃO DE DADOS: OVERVIEW =====
    normalizeOverviewData(response) {
        console.log('🔧 Normalizando dados de overview...');

        // Caso 1: Resposta já tem a estrutura correta {kpis: [...]}
        if (response && Array.isArray(response.kpis)) {
            console.log('✅ Estrutura correta detectada (kpis no root)');
            return {
                kpis: response.kpis,
                raw_data: response.raw_data || {}
            };
        }

        // Caso 2: Resposta tem {data: {kpis: [...]}}
        if (response && response.data && Array.isArray(response.data.kpis)) {
            console.log('✅ Estrutura correta detectada (kpis em data)');
            return {
                kpis: response.data.kpis,
                raw_data: response.data.raw_data || {}
            };
        }

        // Caso 3: Resposta é um array direto (formato antigo)
        if (Array.isArray(response)) {
            console.log('⚠️ Formato legado detectado (array direto), convertendo...');
            return {
                kpis: response,
                raw_data: {}
            };
        }

        // Caso 4: Estrutura desconhecida
        console.error('❌ Estrutura de dados desconhecida:', response);
        return {
            kpis: [],
            raw_data: {},
            error: 'Estrutura de dados inválida'
        };
    }

    // ===== NORMALIZAÇÃO DE DADOS: TRENDS =====
    normalizeTrendsData(response) {
        console.log('🔧 Normalizando dados de trends...');

        // Caso 1: Resposta é um array direto
        if (Array.isArray(response)) {
            console.log('✅ Array de trends detectado');
            return response;
        }

        // Caso 2: Resposta tem {data: [...]}
        if (response && Array.isArray(response.data)) {
            console.log('✅ Trends em data detectado');
            return response.data;
        }

        // Caso 3: Resposta tem {trends: [...]}
        if (response && Array.isArray(response.trends)) {
            console.log('✅ Trends em trends detectado');
            return response.trends;
        }

        console.warn('⚠️ Nenhum dado de trends encontrado');
        return [];
    }

    // ===== NORMALIZAÇÃO DE DADOS: ABC =====
    normalizeABCData(response) {
        console.log('🔧 Normalizando dados de ABC...');

        // Caso 1: Resposta tem {produtos: [...]}
        if (response && Array.isArray(response.produtos)) {
            console.log('✅ Estrutura ABC correta detectada');
            return {
                produtos: response.produtos,
                faturamento_total: response.faturamento_total || 0,
                summary: response.summary || {}
            };
        }

        // Caso 2: Resposta tem {data: {produtos: [...]}}
        if (response && response.data && Array.isArray(response.data.produtos)) {
            console.log('✅ Estrutura ABC em data detectada');
            return {
                produtos: response.data.produtos,
                faturamento_total: response.data.faturamento_total || 0,
                summary: response.data.summary || {}
            };
        }

        // Caso 3: Resposta é um array direto
        if (Array.isArray(response)) {
            console.log('⚠️ Array direto detectado, convertendo...');
            return {
                produtos: response,
                faturamento_total: 0,
                summary: {}
            };
        }

        console.warn('⚠️ Nenhum dado ABC encontrado');
        return {
            produtos: [],
            faturamento_total: 0,
            summary: {}
        };
    }

    // ===== SISTEMA DE RETRY COM EXPONENTIAL BACKOFF =====
    async retryableFetch(url, options = {}) {
        let lastError;

        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                console.log(`📡 Tentativa ${attempt}/${this.retryAttempts}: ${url}`);

                const response = await fetch(url, {
                    ...options,
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    }
                });

                if (!response.ok) {
                    throw new Error(`Erro de servidor: ${response.status} ${response.statusText}`);
                }

                const data = await response.json();
                console.log(`✅ Sucesso na tentativa ${attempt}: ${url}`);
                return data;

            } catch (error) {
                lastError = error;
                console.warn(`⚠️ Tentativa ${attempt} falhou: ${error.message}`);

                if (attempt < this.retryAttempts) {
                    const delay = this.retryDelay * Math.pow(2, attempt - 1);
                    console.log(`⏳ Aguardando ${delay}ms antes de tentar novamente...`);
                    await this.sleep(delay);
                }
            }
        }

        console.error(`❌ Falha após ${this.retryAttempts} tentativas: ${url}`);
        throw lastError;
    }

    // ===== DADOS DE FALLBACK (QUANDO A API FALHA) =====
    getFallbackData() {
        console.warn('⚠️ Usando dados de fallback');
        return {
            overview: {
                data: {
                    kpis: [
                        {
                            name: 'Total de Vendas',
                            value: 0,
                            unit: '',
                            trend: '0.0'
                        },
                        {
                            name: 'Faturamento Bruto',
                            value: 0,
                            unit: 'R$',
                            trend: '0.0'
                        },
                        {
                            name: 'Faturamento Líquido',
                            value: 0,
                            unit: 'R$',
                            trend: '0.0'
                        },
                        {
                            name: 'Ticket Médio',
                            value: 0,
                            unit: 'R$',
                            trend: '0.0'
                        },
                        {
                            name: 'Lucro Estimado',
                            value: 0,
                            unit: 'R$',
                            trend: '0.0'
                        }
                    ],
                    raw_data: {}
                }
            },
            trends: {
                data: []
            },
            abc: {
                data: {
                    produtos: [],
                    faturamento_total: 0,
                    summary: {}
                }
            }
        };
    }

    // ===== MÉTODOS AUXILIARES =====
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // ===== SISTEMA DE CACHE =====
    getCachedData(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            console.log(`📦 Dados em cache encontrados para: ${key}`);
            return cached.data;
        }
        return null;
    }

    setCachedData(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
        console.log(`💾 Dados armazenados em cache: ${key}`);
    }

    clearCache() {
        this.cache.clear();
        console.log('🗑️ Cache limpo');
    }

    // ===== MÉTODOS ESPECÍFICOS PARA CADA ENDPOINT =====
    async fetchVendas(filters = {}) {
        const queryString = new URLSearchParams(filters).toString();
        const url = `${this.baseURL}/vendas${queryString ? '?' + queryString : ''}`;
        return await this.retryableFetch(url);
    }

    async fetchAnalytics(type, filters = {}) {
        const queryString = new URLSearchParams(filters).toString();
        const url = `${this.baseURL}/analytics/${type}${queryString ? '?' + queryString : ''}`;
        return await this.retryableFetch(url);
    }

    async exportData(format = 'csv', filters = {}) {
        const queryString = new URLSearchParams({...filters, format}).toString();
        const url = `${this.baseURL}/export?${queryString}`;

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Erro ao exportar: ${response.status}`);
            }

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = `export_${Date.now()}.${format}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(downloadUrl);

            console.log('✅ Exportação concluída');
            return true;
        } catch (error) {
            console.error('❌ Erro na exportação:', error);
            return false;
        }
    }

    // ===== HEALTH CHECK =====
    async checkAPIHealth() {
        try {
            const response = await fetch(`${this.baseURL}/health`, {
                method: 'GET',
                headers: {'Content-Type': 'application/json'}
            });
            return response.ok;
        } catch (error) {
            console.error('❌ API não está respondendo:', error);
            return false;
        }
    }
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.APIIntegration = APIIntegration;
    console.log('✅ APIIntegration carregado e disponível globalmente');
}