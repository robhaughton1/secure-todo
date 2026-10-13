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

  /* Companion messages are chosen on request, never timed or tied to progress. */
  const thought = document.querySelector('[data-companion-thought]');
  const companion = document.querySelector('[data-companion-message]');
  if (thought && companion) {
    const messages = [
      'We can start small. I’ll keep you company.',
      'There’s room for a pause, too.',
      'A cup of tea and a fresh page. That sounds lovely.',
      'Your pace is a perfectly good pace.',
      'You don’t have to fill the whole page today.'
    ];
    let messageIndex = 0;
    thought.hidden = false;
    thought.addEventListener('click', () => {
      messageIndex = (messageIndex + 1) % messages.length;
      companion.textContent = messages[messageIndex];
    });
  }

  /* Isolated, labeled design specimens only. No task data, network or storage. */
  document.querySelectorAll('[data-design-preview]').forEach(preview => {
    const controls = preview.querySelector('[data-preview-controls]');
    const buttons = preview.querySelectorAll('[data-preview-state]');
    const checkbox = preview.querySelector('[data-preview-complete]');
    const card = preview.querySelector('.preview-task');
    const reaction = preview.querySelector('[data-preview-reaction]');
    const announcement = preview.querySelector('[data-preview-announcement]');
    const status = preview.querySelector('[data-preview-status]');
    const showState = (state, announce = true) => {
      const completed = state === 'completed';
      preview.querySelectorAll('[data-preview-panel]').forEach(panel => {
        panel.hidden = panel.dataset.previewPanel !== (state === 'pending' || completed ? 'task' : state);
      });
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.previewState === state)));
      checkbox.checked = completed;
      card.classList.toggle('is-complete', completed);
      reaction.hidden = !completed;
      reaction.classList.toggle('is-celebrating', completed);
      status.textContent = completed ? 'Completed · design example' : 'Pending · design example';
      if (announce) announcement.textContent = completed || state === 'all-done' ? 'Design preview: Yay! You did it! No task was saved.' : `Design preview: ${state === 'empty' ? 'a fresh page' : 'a small next step'}. No task was saved.`;
    };
    controls.hidden = false;
    checkbox.disabled = false;
    buttons.forEach(button => button.addEventListener('click', () => showState(button.dataset.previewState)));
    checkbox.addEventListener('change', () => showState(checkbox.checked ? 'completed' : 'pending'));
    showState('pending', false);
  });
})();
