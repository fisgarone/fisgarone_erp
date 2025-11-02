// ===== SISTEMA DE FILTROS AVANÇADOS - VERSÃO OTIMIZADA =====
class FiltersSystem {
    constructor() {
        this.currentFilters = {
            period: '7d',
            status: 'all',
            account: 'all',
            category: 'all'
        };
        this.isLoading = false;
    }

    // ===== RENDERIZAR PAINEL DE FILTROS (1 LINHA HORIZONTAL) =====
    renderFilterPanel(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="filters-panel-horizontal">
                <div class="filters-row">
                    <!-- Período -->
                    <div class="filter-group-inline">
                        <label>📅 PERÍODO</label>
                        <select onchange="filtersSystem.setFilter('period', this.value)" ${this.isLoading ? 'disabled' : ''}>
                            <option value="7d" selected>Últimos 7 dias</option>
                            <option value="30d">Últimos 30 dias</option>
                            <option value="60d">Últimos 60 dias</option>
                            <option value="90d">Últimos 90 dias</option>
                        </select>
                    </div>

                    <!-- Status -->
                    <div class="filter-group-inline">
                        <label>📊 STATUS</label>
                        <select onchange="filtersSystem.setFilter('status', this.value)" ${this.isLoading ? 'disabled' : ''}>
                            <option value="all" selected>Todos</option>
                            <option value="paid">Pagos</option>
                            <option value="canceled">Cancelados</option>
                        </select>
                    </div>

                    <!-- Conta ML -->
                    <div class="filter-group-inline">
                        <label>🏪 CONTA MERCADO LIVRE</label>
                        <select onchange="filtersSystem.setFilter('account', this.value)" ${this.isLoading ? 'disabled' : ''}>
                            <option value="all" selected>Todas as Contas</option>
                            <option value="fisgar_shop">FISGAR SHOP</option>
                        </select>
                    </div>

                    <!-- Categoria -->
                    <div class="filter-group-inline">
                        <label>📦 CATEGORIA</label>
                        <select onchange="filtersSystem.setFilter('category', this.value)" ${this.isLoading ? 'disabled' : ''}>
                            <option value="all" selected>Todas</option>
                            <option value="A">Classe A</option>
                            <option value="B">Classe B</option>
                            <option value="C">Classe C</option>
                        </select>
                    </div>

                    <!-- Ações -->
                    <div class="filter-actions-inline">
                        <button class="ai-btn ai-btn-secondary btn-sm" onclick="filtersSystem.clearAllFilters()" ${this.isLoading ? 'disabled' : ''}>
                            🔄 Limpar
                        </button>
                        <button class="ai-btn ai-btn-primary btn-sm" onclick="filtersSystem.applyFilters()" ${this.isLoading ? 'disabled' : ''}>
                            ${this.isLoading ? '⏳ Aplicando...' : '✅ Aplicar'}
                        </button>
                    </div>
                </div>
            </div>
        `;

        this.updateFiltersInfo();
    }

    // ===== APLICAR FILTROS =====
    async applyFilters() {
        if (this.isLoading) return;

        console.log('🎯 Aplicando filtros:', this.currentFilters);

        this.setLoading(true);

        try {
            await new Promise(resolve => setTimeout(resolve, 800));

            if (window.dashboard) {
                await dashboard.updateWithFilters(this.currentFilters);
            }

            this.showNotification('Filtros aplicados com sucesso!', 'success');

        } catch (error) {
            console.error('Erro ao aplicar filtros:', error);
            this.showNotification('Erro ao aplicar filtros', 'error');
        } finally {
            this.setLoading(false);
        }
    }

    // ===== DEFINIR FILTRO =====
    setFilter(key, value) {
        this.currentFilters[key] = value;
        console.log(`Filtro ${key} definido para:`, value);
        this.updateFiltersInfo();
    }

    // ===== LIMPAR FILTROS =====
    clearAllFilters() {
        this.currentFilters = {
            period: '7d',
            status: 'all',
            account: 'all',
            category: 'all'
        };
        this.renderFilterPanel('filters-container');
        this.applyFilters();
    }

    // ===== ATUALIZAR INFO =====
    updateFiltersInfo() {
        const info = document.getElementById('filters-info');
        if (info) {
            const periodText = this.getPeriodText(this.currentFilters.period);
            info.textContent = `Mostrando dados de ${periodText}`;
        }
    }

    getPeriodText(period) {
        const texts = {
            '7d': 'últimos 7 dias',
            '30d': 'últimos 30 dias',
            '60d': 'últimos 60 dias',
            '90d': 'últimos 90 dias'
        };
        return texts[period] || 'período selecionado';
    }

    // ===== LOADING =====
    setLoading(loading) {
        this.isLoading = loading;
        this.renderFilterPanel('filters-container');
    }

    // ===== NOTIFICAÇÃO =====
    showNotification(message, type) {
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

// Inicializar globalmente
window.filtersSystem = new FiltersSystem();
