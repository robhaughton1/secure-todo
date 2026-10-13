export function initializeThemeControls() {
  const root = document.documentElement;
  const themeButtons = document.querySelectorAll('[data-theme-toggle]');
  const updateThemeLabels = () => themeButtons.forEach(button => {
    const dark = root.dataset.theme === 'dark';
    button.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
    button.querySelector('[data-theme-label]').textContent = dark ? 'Light' : 'Dark';
  });
  themeButtons.forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => {
      root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.manualTheme = 'true';
      try { localStorage.setItem('fernward-theme', root.dataset.theme); } catch (_) { /* Works without storage. */ }
      updateThemeLabels();
    });
  });
  updateThemeLabels();
  document.addEventListener('fernward-theme-change', updateThemeLabels);
}
