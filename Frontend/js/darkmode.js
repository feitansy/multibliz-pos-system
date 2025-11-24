/**
 * Dark Mode Toggle System
 * Manages light/dark theme persistence using localStorage
 * Applies CSS variables for real-time theme switching
 */

class DarkModeManager {
    constructor() {
        this.storageKey = 'multibliz-darkmode';
        this.darkModeClass = 'dark-mode';
        this.init();
    }

    init() {
        // Load saved preference or use system preference
        const savedMode = localStorage.getItem(this.storageKey);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedMode !== null) {
            this.setMode(savedMode === 'true');
        } else {
            this.setMode(prefersDark);
        }

        // Setup toggle buttons
        this.setupToggleButtons();

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addListener((e) => {
            if (localStorage.getItem(this.storageKey) === null) {
                this.setMode(e.matches);
            }
        });
    }

    setupToggleButtons() {
        const toggles = document.querySelectorAll('[data-toggle="darkmode"]');
        toggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggle();
                this.updateToggleButtons();
            });
        });

        // Update button state on load
        this.updateToggleButtons();
    }

    toggle() {
        const isDark = document.documentElement.classList.contains(this.darkModeClass);
        this.setMode(!isDark);
    }

    setMode(isDark) {
        if (isDark) {
            document.documentElement.classList.add(this.darkModeClass);
            localStorage.setItem(this.storageKey, 'true');
        } else {
            document.documentElement.classList.remove(this.darkModeClass);
            localStorage.setItem(this.storageKey, 'false');
        }

        // Trigger custom event for other components
        const event = new CustomEvent('darkmodechange', { 
            detail: { isDark } 
        });
        document.dispatchEvent(event);
    }

    updateToggleButtons() {
        const isDark = document.documentElement.classList.contains(this.darkModeClass);
        const toggles = document.querySelectorAll('[data-toggle="darkmode"]');
        
        toggles.forEach(toggle => {
            if (isDark) {
                toggle.classList.add('active');
                toggle.innerHTML = '<i class="fas fa-moon"></i>';
                toggle.title = 'Switch to Light Mode';
            } else {
                toggle.classList.remove('active');
                toggle.innerHTML = '<i class="fas fa-sun"></i>';
                toggle.title = 'Switch to Dark Mode';
            }
        });
    }

    isDarkMode() {
        return document.documentElement.classList.contains(this.darkModeClass);
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    window.darkModeManager = new DarkModeManager();
});
