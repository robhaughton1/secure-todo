export function initializeNavigation() {
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
}
