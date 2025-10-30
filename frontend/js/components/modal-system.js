// ===== MODAL SYSTEM PREMIUM COM SUPORTE COMPLETO A TEMA =====
class ModalSystem {
    constructor() {
        this.container = document.getElementById('modal-container');
        if (!this.container) {
            this.createModalContainer();
        }
        this.currentModal = null;
        this.modalStack = [];
    }

    // ===== CRIAR CONTAINER DE MODAL =====
    createModalContainer() {
        this.container = document.createElement('div');
        this.container.id = 'modal-container';
        this.container.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            padding: 2rem;
        `;
        document.body.appendChild(this.container);
        this.addModalStyles();

        // Adicionar event listener para clique fora
        this.container.addEventListener('click', (e) => {
            if (e.target === this.container) {
                this.close();
            }
        });
    }

    // ===== ABRIR MODAL =====
    open(options) {
        const { title, content, size = 'medium', onClose, onOpen } = options;

        // Fechar modal anterior se existir
        if (this.currentModal) {
            this.close();
        }

        // DETECTAR TEMA ATUAL
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';

        // CORES BASEADAS NO TEMA - CORREÇÃO DEFINITIVA
        const themeStyles = currentTheme === 'dark' ? `
            background: #1e293b;
            color: #f8fafc;
            border: 1px solid #475569;
        ` : `
            background: white;
            color: #0f172a;
        `;

        const headerStyles = currentTheme === 'dark' ? `
            background: #1e293b;
            color: #f8fafc;
            border-bottom: 1px solid #475569;
        ` : `
            background: white;
            color: #0f172a;
            border-bottom: 1px solid #e2e8f0;
        `;

        const bodyStyles = currentTheme === 'dark' ? `
            background: #1e293b;
            color: #f8fafc;
        ` : `
            background: white;
            color: #0f172a;
        `;

        const closeButtonStyles = currentTheme === 'dark' ? `
            color: #94a3b8;
        ` : `
            color: #64748b;
        `;

        const sizeStyles = {
            small: 'max-width: 400px;',
            medium: 'max-width: 600px;',
            large: 'max-width: 800px;',
            full: 'max-width: 95%; height: 95%;'
        };

        const modalHTML = `
            <div class="modal-overlay" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                padding: 2rem;
            " onclick="modalSystem.close()">
                <div class="modal-content" style="
                    ${themeStyles}
                    border-radius: 16px;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                    width: 100%;
                    ${sizeStyles[size]}
                    max-height: 90vh;
                    overflow: hidden;
                    animation: modalSlideIn 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                " onclick="event.stopPropagation()">
                    <div class="modal-header" style="
                        ${headerStyles}
                        padding: 1.5rem;
                        border-bottom: 1px solid;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                    ">
                        <h3 style="font-size: 1.25rem; font-weight: 600; margin: 0;">
                            ${title}
                        </h3>
                        <button onclick="modalSystem.close()" style="
                            background: none;
                            border: none;
                            font-size: 1.5rem;
                            cursor: pointer;
                            ${closeButtonStyles}
                            padding: 0.25rem;
                            border-radius: 8px;
                            transition: all 0.15s ease;
                            width: 32px;
                            height: 32px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        " onmouseover="this.style.color='${currentTheme === 'dark' ? '#ffffff' : '#0f172a'}'"
                         onmouseout="this.style.color='${currentTheme === 'dark' ? '#94a3b8' : '#64748b'}'"
                         aria-label="Fechar modal">
                            ✕
                        </button>
                    </div>
                    <div class="modal-body" style="
                        ${bodyStyles}
                        padding: 1.5rem;
                        max-height: calc(90vh - 120px);
                        overflow-y: auto;
                    ">
                        ${content}
                    </div>
                </div>
            </div>
        `;

        // Adicionar novo modal
        this.container.innerHTML = modalHTML;
        this.container.style.display = 'flex';

        this.attachModalEvents();

        // Adicionar ao stack
        this.currentModal = {
            element: this.container,
            onClose: onClose,
            onOpen: onOpen
        };
        this.modalStack.push(this.currentModal);

        // Executar callback de abertura
        if (onOpen) {
            onOpen();
        }

        // Adicionar event listener para ESC key
        this.addEscapeListener();

        // Focar no modal para acessibilidade
        this.focusModal();
    }

    // ===== ADICIONAR EVENTOS AO MODAL =====
    attachModalEvents() {
        // CORREÇÃO: Fechar ao clicar no overlay
        const overlay = this.container.querySelector('.modal-overlay');
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.close();
                }
            });
        }

        // CORREÇÃO: Fechar ao clicar no botão X
        const closeBtn = this.container.querySelector('button[onclick="modalSystem.close()"]');
        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.close();
            });
        }

        // CORREÇÃO: Prevenir que clique no conteúdo feche o modal
        const modalContent = this.container.querySelector('.modal-content');
        if (modalContent) {
            modalContent.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
    }

    // ===== FECHAR MODAL =====
    close() {
        if (this.modalStack.length === 0) return;

        const currentModal = this.modalStack.pop();

        // Executar callback de fechamento
        if (currentModal.onClose) {
            currentModal.onClose();
        }

        if (this.modalStack.length > 0) {
            // Mostrar modal anterior
            this.currentModal = this.modalStack[this.modalStack.length - 1];
            this.container.style.display = 'flex';
        } else {
            // Fechar todos os modais
            this.container.innerHTML = '';
            this.container.style.display = 'none';
            this.currentModal = null;
        }

        // Remover event listener se não houver mais modais
        if (this.modalStack.length === 0) {
            this.removeEscapeListener();
        }
    }

    // ===== FECHAR TODOS OS MODAIS =====
    closeAll() {
        while (this.modalStack.length > 0) {
            const modal = this.modalStack.pop();
            if (modal.onClose) {
                modal.onClose();
            }
        }

        this.container.innerHTML = '';
        this.container.style.display = 'none';
        this.currentModal = null;
        this.removeEscapeListener();
    }

    // ===== ADICIONAR ESTILOS CSS =====
    addModalStyles() {
        if (!document.getElementById('modal-styles')) {
            const styles = document.createElement('style');
            styles.id = 'modal-styles';
            styles.textContent = `
                @keyframes modalSlideIn {
                    from {
                        opacity: 0;
                        transform: scale(0.9) translateY(-20px);
                    }
                    to {
                        opacity: 1;
                        transform: scale(1) translateY(0);
                    }
                }

                @keyframes modalSlideOut {
                    from {
                        opacity: 1;
                        transform: scale(1) translateY(0);
                    }
                    to {
                        opacity: 0;
                        transform: scale(0.9) translateY(-20px);
                    }
                }

                .modal-content {
                    transition: all 0.3s ease;
                }

                /* Scrollbar customizada para o modal */
                .modal-body::-webkit-scrollbar {
                    width: 6px;
                }

                .modal-body::-webkit-scrollbar-track {
                    background: transparent;
                }

                .modal-body::-webkit-scrollbar-thumb {
                    background: #cbd5e1;
                    border-radius: 3px;
                }

                .modal-body::-webkit-scrollbar-thumb:hover {
                    background: #94a3b8;
                }

                [data-theme="dark"] .modal-body::-webkit-scrollbar-thumb {
                    background: #475569;
                }

                [data-theme="dark"] .modal-body::-webkit-scrollbar-thumb:hover {
                    background: #64748b;
                }

                /* === CORREÇÃO RADICAL PARA MODO ESCURO === */
                [data-theme="dark"] .modal-overlay .modal-content,
                [data-theme="dark"] .modal-overlay .modal-content * {
                    background: #1e293b !important;
                    color: #f8fafc !important;
                }

                [data-theme="dark"] .modal-overlay .modal-header {
                    background: #1e293b !important;
                    border-bottom-color: #475569 !important;
                }

                [data-theme="dark"] .modal-overlay .modal-body {
                    background: #1e293b !important;
                }

                [data-theme="dark"] .modal-overlay .modal-body *:not(button) {
                    color: #f8fafc !important;
                }

                /* Forçar cores em elementos específicos */
                [data-theme="dark"] .modal-overlay input,
                [data-theme="dark"] .modal-overlay select,
                [data-theme="dark"] .modal-overlay textarea {
                    background: #334155 !important;
                    color: #f8fafc !important;
                    border: 1px solid #475569 !important;
                }

                [data-theme="dark"] .modal-overlay table {
                    background: #1e293b !important;
                    color: #f8fafc !important;
                }

                [data-theme="dark"] .modal-overlay table * {
                    background: #1e293b !important;
                    color: #f8fafc !important;
                    border-color: #475569 !important;
                }

                /* Remover qualquer fundo branco */
                [data-theme="dark"] .modal-overlay [style*="background: white"],
                [data-theme="dark"] .modal-overlay [style*="background: #fff"],
                [data-theme="dark"] .modal-overlay [style*="background-color: white"],
                [data-theme="dark"] .modal-overlay [style*="background-color: #fff"] {
                    background: #334155 !important;
                }

                [data-theme="dark"] .modal-overlay [style*="color: black"],
                [data-theme="dark"] .modal-overlay [style*="color: #000"],
                [data-theme="dark"] .modal-overlay [style*="color: #0f172a"] {
                    color: #f8fafc !important;
                }
            `;
            document.head.appendChild(styles);
        }
    }

    // ===== ADICIONAR LISTENER PARA TECLA ESC =====
    addEscapeListener() {
        this.escapeHandler = (event) => {
            if (event.key === 'Escape') {
                this.close();
            }
        };
        document.addEventListener('keydown', this.escapeHandler);
    }

    // ===== REMOVER LISTENER PARA TECLA ESC =====
    removeEscapeListener() {
        if (this.escapeHandler) {
            document.removeEventListener('keydown', this.escapeHandler);
            this.escapeHandler = null;
        }
    }

    // ===== FOCO NO MODAL =====
    focusModal() {
        const modalContent = this.container.querySelector('.modal-content');
        if (modalContent) {
            modalContent.focus();
        }
    }

    // ===== ATUALIZAR CONTEÚDO DO MODAL =====
    updateContent(newContent) {
        if (!this.currentModal) return;

        const modalBody = this.container.querySelector('.modal-body');
        if (modalBody) {
            modalBody.innerHTML = newContent;
        }
    }

    // ===== ATUALIZAR TÍTULO DO MODAL =====
    updateTitle(newTitle) {
        if (!this.currentModal) return;

        const modalHeader = this.container.querySelector('.modal-header h3');
        if (modalHeader) {
            modalHeader.textContent = newTitle;
        }
    }

    // ===== MOSTRAR LOADING NO MODAL =====
    showLoading(message = 'Carregando...') {
        if (!this.currentModal) return;

        const loadingHTML = `
            <div style="text-align: center; padding: 3rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⏳</div>
                <h3 style="margin-bottom: 1rem; color: inherit;">${message}</h3>
                <div style="display: inline-block; width: 40px; height: 40px; border: 3px solid #f3f4f6; border-top: 3px solid #3b82f6; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            </div>

            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;

        this.updateContent(loadingHTML);
    }

    // ===== MOSTRAR ERRO NO MODAL =====
    showError(message, details = '') {
        if (!this.currentModal) return;

        const errorHTML = `
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">❌</div>
                <h3 style="margin-bottom: 1rem; color: #ef4444;">Erro</h3>
                <p style="color: inherit; margin-bottom: 1.5rem;">${message}</p>
                ${details ? `<p style="color: #94a3b8; font-size: 0.875rem;">${details}</p>` : ''}
                <button onclick="modalSystem.close()" style="
                    margin-top: 1.5rem;
                    padding: 0.75rem 1.5rem;
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                ">
                    Fechar
                </button>
            </div>
        `;

        this.updateContent(errorHTML);
    }

    // ===== CONFIRMAÇÃO SIMPLES =====
    confirm(options) {
        return new Promise((resolve) => {
            const { title, message, confirmText = 'Confirmar', cancelText = 'Cancelar', type = 'warning' } = options;

            const icon = {
                warning: '⚠️',
                danger: '🚨',
                info: 'ℹ️',
                success: '✅'
            }[type] || '⚠️';

            const confirmHTML = `
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">${icon}</div>
                    <h3 style="margin-bottom: 1rem; color: inherit;">${title}</h3>
                    <p style="color: inherit; margin-bottom: 2rem;">${message}</p>
                    <div style="display: flex; gap: 1rem; justify-content: center;">
                        <button onclick="modalSystem.handleConfirm(false)" style="
                            padding: 0.75rem 1.5rem;
                            background: #f8fafc;
                            color: #0f172a;
                            border: 1px solid #e2e8f0;
                            border-radius: 8px;
                            cursor: pointer;
                            font-weight: 600;
                            flex: 1;
                        ">
                            ${cancelText}
                        </button>
                        <button onclick="modalSystem.handleConfirm(true)" style="
                            padding: 0.75rem 1.5rem;
                            background: ${type === 'danger' ? '#ef4444' : '#3b82f6'};
                            color: white;
                            border: none;
                            border-radius: 8px;
                            cursor: pointer;
                            font-weight: 600;
                            flex: 1;
                        ">
                            ${confirmText}
                        </button>
                    </div>
                </div>
            `;

            // Armazenar a promise resolve function
            this.pendingConfirm = resolve;

            this.open({
                title: title,
                content: confirmHTML,
                size: 'small',
                onClose: () => {
                    if (this.pendingConfirm) {
                        this.pendingConfirm(false);
                        this.pendingConfirm = null;
                    }
                }
            });
        });
    }

    // ===== MANIPULAR CONFIRMAÇÃO =====
    handleConfirm(result) {
        if (this.pendingConfirm) {
            this.pendingConfirm(result);
            this.pendingConfirm = null;
        }
        this.close();
    }

    // ===== OBTER INFO DO MODAL ATUAL =====
    getCurrentModal() {
        return this.currentModal;
    }

    // ===== VERIFICAR SE HÁ MODAL ABERTO =====
    isOpen() {
        return this.modalStack.length > 0;
    }

    // ===== OBTER CONTADOR DE MODAIS =====
    getModalCount() {
        return this.modalStack.length;
    }

    // ===== DESTRUIDOR =====
    destroy() {
        this.closeAll();
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        const styles = document.getElementById('modal-styles');
        if (styles) {
            styles.parentNode.removeChild(styles);
        }
    }
}

// Instância global
window.modalSystem = new ModalSystem();