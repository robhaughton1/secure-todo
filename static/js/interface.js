(() => {
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
  const date = document.querySelector('[data-current-date]');
  if (date) {
    const now = new Date();
    date.dateTime = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    date.textContent = new Intl.DateTimeFormat(undefined, { weekday: 'long', month: 'long', day: 'numeric' }).format(now);
  }
  const menu = document.querySelector('[data-menu-toggle]');
  const sidebar = document.querySelector('.sidebar');
  if (menu && sidebar) {
    menu.hidden = false;
    const setMenu = open => { menu.setAttribute('aria-expanded', String(open)); sidebar.classList.toggle('is-open', open); };
    menu.addEventListener('click', () => {
      const open = menu.getAttribute('aria-expanded') !== 'true';
      setMenu(open);
      if (open) sidebar.querySelector('a').focus();
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') { setMenu(false); menu.focus(); }
    });
    document.addEventListener('click', event => {
      if (menu.getAttribute('aria-expanded') === 'true' && !sidebar.contains(event.target) && !menu.contains(event.target)) setMenu(false);
    });
    window.matchMedia('(min-width: 901px)').addEventListener('change', () => setMenu(false));
  }
  /* Decorative focus response only. Never inspect field values. */
  document.querySelectorAll('.authForm').forEach(form => {
    form.addEventListener('focusin', () => document.body.classList.add('form-engaged'));
    form.addEventListener('focusout', event => { if (!form.contains(event.relatedTarget)) document.body.classList.remove('form-engaged'); });
  });
})();
