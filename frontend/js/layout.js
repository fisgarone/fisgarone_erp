document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('app-sidebar');
    const appShell = document.getElementById('app-shell');
    const submenuToggles = document.querySelectorAll('[data-submenu-id]');
    const themeToggleButton = document.getElementById('theme-toggle-button');
    const commandPaletteButton = document.getElementById('command-palette-button');
    const commandPaletteOverlay = document.getElementById('command-palette-overlay');

    // Lógica para expandir/colapsar a sidebar
    if (sidebar && appShell) {
        sidebar.addEventListener('mouseenter', () => appShell.classList.add('sidebar-expanded'));
        sidebar.addEventListener('mouseleave', () => appShell.classList.remove('sidebar-expanded'));
    }

    // Lógica para abrir/fechar submenus
    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const submenuId = toggle.dataset.submenuId;
            const submenu = document.getElementById(submenuId);

            // Fecha outros submenus abertos
            document.querySelectorAll('.submenu').forEach(otherSubmenu => {
                if (otherSubmenu !== submenu && otherSubmenu.style.maxHeight) {
                    otherSubmenu.style.maxHeight = null;
                    otherSubmenu.previousElementSibling.classList.remove('open');
                }
            });

            toggle.classList.toggle('open');
            if (submenu.style.maxHeight) {
                submenu.style.maxHeight = null;
            } else {
                submenu.style.maxHeight = submenu.scrollHeight + "px";
            }
        });
    });

    // Lógica para alternar tema
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('fisgarone-theme', newTheme);
        });
    }

    // Carregar tema salvo
    const savedTheme = localStorage.getItem('fisgarone-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // Lógica da Paleta de Comando
    if (commandPaletteButton && commandPaletteOverlay) {
        const showCommandPalette = () => commandPaletteOverlay.classList.add('visible');
        const hideCommandPalette = () => commandPaletteOverlay.classList.remove('visible');

        commandPaletteButton.addEventListener('click', showCommandPalette);
        commandPaletteOverlay.addEventListener('click', (e) => {
            if (e.target === commandPaletteOverlay) {
                hideCommandPalette();
            }
        });
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                showCommandPalette();
            }
            if (e.key === 'Escape' && commandPaletteOverlay.classList.contains('visible')) {
                hideCommandPalette();
            }
        });
    }
});
