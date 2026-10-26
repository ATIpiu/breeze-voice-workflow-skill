try { const theme = localStorage.getItem('atipiu-theme'); if (theme === 'dark' || theme === 'light') document.documentElement.dataset.theme = theme; } catch (_) {}
