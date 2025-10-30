// ===== SISTEMA DE FILTROS AVANÇADOS =====
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

    // ===== RENDERIZAR PAINEL DE FILTROS =====
    renderFilterPanel(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="filters-panel">
                <div class="filters-header">
                    <h3>🎛️ Filtros Avançados</h3>
                    <button class="ai-btn ai-btn-secondary" onclick="filtersSystem.clearAllFilters()" ${this.isLoading ? 'disabled' : ''}>
                        ${this.isLoading ? '⏳' : '🔄'} Limpar Filtros
                    </button>
                </div>

                <div class="filters-grid">
                    <!-- Período -->
                    <div class="filter-group">
                        <label>📅 Período</label>
                        <select onchange="filtersSystem.setFilter('period', this.value)" ${this.isLoading ? 'disabled' : ''}>
                            <option value="today">Hoje</option>
                            <option value="7d" selected>Últimos 7 dias</option>
                            <option value="30d">Últimos 30 dias</option>
                            <option value="90d">Últimos 90 dias</option>
                            <option value="custom">Personalizado</option>
                        </select>
                    </div>

                    <!-- Status -->
                    <div class="filter-group">
                        <label>📊 Status</label>
                        <select onchange="filtersSystem.setFilter('status', this.value)" ${this.isLoading ? 'disabled' : ''}>
                            <option value="all" selected>Todos</option>
                            <option value="paid">Apenas Pagos</option>
                            <option value="canceled">Apenas Cancelados</option>
                            <option value="pending">Pendentes</option>
                        </select>
                    </div>

                    <!-- Conta ML -->
                    <div class="filter-group">
                        <label>🏪 Conta Mercado Livre</label>
                        <select onchange="filtersSystem.setFilter('account', this.value)" ${this.isLoading ? 'disabled' : ''}>
                            <option value="all" selected>Todas as Contas</option>
                            <option value="fisgar_shop">FISGAR SHOP</option>
                            <option value="conta_2">Conta Secundária</option>
                            <option value="conta_3">Conta Terciária</option>
                        </select>
                    </div>

                    <!-- Categoria -->
                    <div class="filter-group">
                        <label>📦 Categoria</label>
                        <select onchange="filtersSystem.setFilter('category', this.value)" ${this.isLoading ? 'disabled' : ''}>
                            <option value="all" selected>Todas</option>
                            <option value="A">Classe A (Alto Faturamento)</option>
                            <option value="B">Classe B (Médio Faturamento)</option>
                            <option value="C">Classe C (Baixo Faturamento)</option>
                        </select>
                    </div>
                </div>

                <div class="filters-actions">
                    <button class="ai-btn ai-btn-primary" onclick="filtersSystem.applyFilters()" ${this.isLoading ? 'disabled' : ''}>
                        ${this.isLoading ? '⏳ Aplicando...' : '✅ Aplicar Filtros'}
                    </button>
                    <span class="filters-info" id="filters-info">
                        Mostrando dados dos últimos 7 dias
                    </span>
                </div>

                <!-- Tags de Filtros Aplicados -->
                <div class="filters-tags" id="filters-tags">
                    <!-- Tags serão renderizadas aqui -->
                </div>
            </div>
        `;

        this.updateFiltersInfo();
        this.renderFilterTags();
    }

    // ===== APLICAR FILTROS =====
    async applyFilters() {
        if (this.isLoading) return;

        console.log('🎯 Aplicando filtros:', this.currentFilters);

        this.setLoading(true);

        try {
            // Simular delay de API
            await new Promise(resolve => setTimeout(resolve, 800));

            // Aqui integrar com API para buscar dados filtrados
            if (window.dashboard && dashboard.refreshDataWithFilters) {
                await dashboard.refreshDataWithFilters(this.currentFilters);
            }

            // Atualizar info dos filtros
            this.updateFiltersInfo();
            this.renderFilterTags();

            this.showNotification('Filtros aplicados com sucesso!', 'success');

        } catch (error) {
            console.error('❌ Erro ao aplicar filtros:', error);
            this.showNotification('Erro ao aplicar filtros', 'error');
        } finally {
            this.setLoading(false);
        }
    }

    // ===== DEFINIR FILTRO =====
    setFilter(type, value) {
        this.currentFilters[type] = value;
        console.log(`Filtro ${type} alterado para:`, value);

        // Se for período personalizado, mostrar campos de data
        if (type === 'period' && value === 'custom') {
            this.showCustomDatePicker();
        }
    }

    // ===== LIMPAR TODOS OS FILTROS =====
    clearAllFilters() {
        if (this.isLoading) return;

        this.currentFilters = {
            period: '7d',
            status: 'all',
            account: 'all',
            category: 'all'
        };

        // Resetar selects
        const panel = document.querySelector('.filters-panel');
        if (panel) {
            const selects = panel.querySelectorAll('select');
            selects.forEach(select => {
                if (select.querySelector('option[value="all"]')) {
                    select.value = 'all';
                }
                if (select.querySelector('option[value="7d"]')) {
                    select.value = '7d';
                }
            });
        }

        this.applyFilters();
        this.showNotification('Filtros limpos!', 'info');
    }

    // ===== ATUALIZAR INFO DOS FILTROS =====
    updateFiltersInfo() {
        const infoElement = document.getElementById('filters-info');
        if (!infoElement) return;

        const periodText = {
            'today': 'hoje',
            '7d': 'últimos 7 dias',
            '30d': 'últimos 30 dias',
            '90d': 'últimos 90 dias',
            'custom': 'período personalizado'
        };

        const statusText = {
            'all': 'Todos',
            'paid': 'Pagos',
            'canceled': 'Cancelados',
            'pending': 'Pendentes'
        };

        const accountText = {
            'all': 'Todas',
            'fisgar_shop': 'FISGAR SHOP',
            'conta_2': 'Conta Secundária',
            'conta_3': 'Conta Terciária'
        };

        const categoryText = {
            'all': 'Todas',
            'A': 'Classe A',
            'B': 'Classe B',
            'C': 'Classe C'
        };

        let info = `Mostrando dados dos ${periodText[this.currentFilters.period]}`;

        if (this.currentFilters.status !== 'all') {
            info += ` | Status: ${statusText[this.currentFilters.status]}`;
        }

        if (this.currentFilters.account !== 'all') {
            info += ` | Conta: ${accountText[this.currentFilters.account]}`;
        }

        if (this.currentFilters.category !== 'all') {
            info += ` | Categoria: ${categoryText[this.currentFilters.category]}`;
        }

        infoElement.textContent = info;
    }

    // ===== RENDERIZAR TAGS DE FILTROS =====
    renderFilterTags() {
        const tagsContainer = document.getElementById('filters-tags');
        if (!tagsContainer) return;

        const activeFilters = Object.entries(this.currentFilters)
            .filter(([key, value]) => value !== 'all' && value !== '7d')
            .map(([key, value]) => ({ key, value }));

        if (activeFilters.length === 0) {
            tagsContainer.innerHTML = '';
            return;
        }

        const tagsHTML = activeFilters.map(filter => {
            const filterText = this.getFilterDisplayText(filter.key, filter.value);
            return `
                <div class="filter-tag">
                    <span>${filterText}</span>
                    <button onclick="filtersSystem.removeFilter('${filter.key}')" title="Remover filtro">×</button>
                </div>
            `;
        }).join('');

        tagsContainer.innerHTML = tagsHTML;
    }

    // ===== REMOVER FILTRO ESPECÍFICO =====
    removeFilter(filterKey) {
        if (this.isLoading) return;

        const defaultValue = filterKey === 'period' ? '7d' : 'all';
        this.currentFilters[filterKey] = defaultValue;

        // Atualizar select correspondente
        const panel = document.querySelector('.filters-panel');
        if (panel) {
            const select = panel.querySelector(`select[onchange*="${filterKey}"]`);
            if (select) {
                select.value = defaultValue;
            }
        }

        this.applyFilters();
    }

    // ===== TEXTO DE EXIBIÇÃO DOS FILTROS =====
    getFilterDisplayText(key, value) {
        const texts = {
            period: {
                'today': '📅 Hoje',
                '30d': '📅 30 Dias',
                '90d': '📅 90 Dias',
                'custom': '📅 Personalizado'
            },
            status: {
                'paid': '📊 Pagos',
                'canceled': '📊 Cancelados',
                'pending': '📊 Pendentes'
            },
            account: {
                'fisgar_shop': '🏪 FISGAR SHOP',
                'conta_2': '🏪 Conta Secundária',
                'conta_3': '🏪 Conta Terciária'
            },
            category: {
                'A': '📦 Classe A',
                'B': '📦 Classe B',
                'C': '📦 Classe C'
            }
        };

        return texts[key]?.[value] || `${key}: ${value}`;
    }

    // ===== MOSTRAR SELETOR DE DATA PERSONALIZADA =====
    showCustomDatePicker() {
        // Implementação básica - pode ser expandida para datepicker real
        console.log('Mostrar datepicker personalizado');
        this.showNotification('Seletor de datas personalizado - em desenvolvimento', 'info');
    }

    // ===== CONTROLE DE LOADING =====
    setLoading(loading) {
        this.isLoading = loading;

        // Atualizar UI
        const panel = document.querySelector('.filters-panel');
        if (panel) {
            const buttons = panel.querySelectorAll('button');
            const selects = panel.querySelectorAll('select');

            if (loading) {
                panel.classList.add('filters-loading');
                buttons.forEach(btn => btn.disabled = true);
                selects.forEach(select => select.disabled = true);
            } else {
                panel.classList.remove('filters-loading');
                buttons.forEach(btn => btn.disabled = false);
                selects.forEach(select => select.disabled = false);
            }
        }
    }

    // ===== UTILITÁRIOS =====
    showNotification(message, type = 'info') {
        console.log(`🔔 ${type.toUpperCase()}: ${message}`);
        // Integrar com sistema de notificações do dashboard
        if (window.dashboard && dashboard.showNotification) {
            dashboard.showNotification(message, type);
        }
    }

    // ===== OBTER FILTROS ATUAIS =====
    getCurrentFilters() {
        return { ...this.currentFilters };
    }

    // ===== VALIDAR FILTROS =====
    validateFilters() {
        const errors = [];

        // Validar período personalizado
        if (this.currentFilters.period === 'custom') {
            // Aqui validaria as datas
            errors.push('Período personalizado requer datas específicas');
        }

        return errors;
    }

    // ===== EXPORTAR CONFIGURAÇÃO DE FILTROS =====
    exportFilterConfig() {
        return {
            filters: this.currentFilters,
            timestamp: new Date().toISOString(),
            version: '1.0'
        };
    }

    // ===== IMPORTAR CONFIGURAÇÃO DE FILTROS =====
    importFilterConfig(config) {
        if (config && config.filters) {
            this.currentFilters = { ...config.filters };
            this.applyFilters();
            this.showNotification('Configuração de filtros importada!', 'success');
        }
    }
}

// Instância global
window.filtersSystem = new FiltersSystem();