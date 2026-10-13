/* Runs before CSS to avoid a theme flash, without inline scripts. */
(() => {
  document.documentElement.classList.add('has-js');
  let preference;
  try { preference = localStorage.getItem('fernward-theme'); } catch (_) { /* Storage unavailable. */ }
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const manual = preference === 'dark' || preference === 'light';
  document.documentElement.dataset.theme = manual ? preference : (system.matches ? 'dark' : 'light');
  if (manual) document.documentElement.dataset.manualTheme = 'true';
  system.addEventListener('change', event => {
    if (!document.documentElement.dataset.manualTheme) {
      document.documentElement.dataset.theme = event.matches ? 'dark' : 'light';
      document.dispatchEvent(new Event('fernward-theme-change'));
    }
  });
})();
