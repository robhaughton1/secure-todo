export function initializeTasks() {
  const workspace = document.querySelector('[data-task-workspace]');
  if (!workspace || !window.fetch || !window.FormData) return;
  const create = workspace.querySelector('[data-task-create]');
  const input = create.elements.title;
  const list = workspace.querySelector('[data-task-list]');
  const empty = workspace.querySelector('[data-task-empty]');
  const template = workspace.querySelector('[data-task-template]');
  const status = workspace.querySelector('[data-task-status]');
  const error = workspace.querySelector('[data-task-error]');
  const dialog = workspace.querySelector('[data-delete-dialog]');
  const busy = new WeakSet();
  let pendingDelete;
  let titleInvalid = false;
  const titleDescription = input.getAttribute('aria-describedby');

  const announce = message => { status.textContent = message; };
  const showError = message => { error.querySelector('[data-task-error-text]').textContent = message; error.hidden = !message; };
  const titleError = () => {
    titleInvalid = true;
    input.setAttribute('aria-invalid', 'true');
    input.setAttribute('aria-describedby', [titleDescription, error.id].filter(Boolean).join(' '));
    announce(''); showError('Enter a task title.'); input.focus();
  };
  input.addEventListener('invalid', event => {
    if (!input.validity.valueMissing) return;
    event.preventDefault();
    titleError();
  });
  input.addEventListener('input', () => {
    if (!titleInvalid || !input.value.trim()) return;
    titleInvalid = false;
    input.removeAttribute('aria-invalid');
    if (titleDescription) input.setAttribute('aria-describedby', titleDescription);
    else input.removeAttribute('aria-describedby');
    showError('');
  });
  const syncEmpty = () => { const hasTasks = !!list.children.length; list.hidden = !hasTasks; empty.hidden = hasTasks; };
  const setBusy = (element, value) => {
    element.setAttribute('aria-busy', String(value));
    element.querySelectorAll('button, input:not([type=hidden])').forEach(control => { control.disabled = value; });
    if (value) busy.add(element); else busy.delete(element);
  };
  const post = async (form, data) => {
    let response;
    try {
      response = await fetch(form.action, { method: 'POST', body: data, credentials: 'same-origin', headers: { Accept: 'application/json' }, redirect: 'error' });
    } catch (_) {
      throw new Error('Could not confirm the change. Reload to check your tasks before trying again.');
    }
    if (!response.headers.get('content-type')?.includes('application/json')) {
      throw new Error('The server could not complete the request. Reload to check your tasks.');
    }
    let payload;
    try { payload = await response.json(); }
    catch (_) { throw new Error('Unexpected server response. Reload to check your tasks.'); }
    if (!response.ok) throw new Error(payload.error || 'The change could not be saved.');
    return payload;
  };
  const setTask = (row, task) => {
    if (!Number.isInteger(task?.id) || typeof task.title !== 'string' || typeof task.completed !== 'boolean') throw new Error('Unexpected server response. Reload to check your tasks.');
    for (const [selector, url] of [['[data-task-toggle]', task.toggle_url], ['[data-task-delete]', task.delete_url]]) {
      const target = new URL(url, location.href);
      if (target.origin !== location.origin) throw new Error('Unexpected server response. Reload to check your tasks.');
      row.querySelector(selector).action = target.href;
    }
    row.dataset.taskId = String(task.id);
    row.querySelector('.task-title').textContent = task.title;
    row.querySelector('input[type=checkbox]').checked = task.completed;
    row.querySelector('.task-delete-button').setAttribute('aria-label', `Delete task: ${task.title}`);
    row.classList.toggle('is-complete', task.completed);
  };

  create.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy.has(create)) return;
    if (!input.value.trim()) { titleError(); return; }
    const data = new FormData(create);
    showError('');
    setBusy(create, true);
    announce('Adding task…');
    try {
      const payload = await post(create, data);
      const row = template.content.firstElementChild.cloneNode(true);
      setTask(row, payload.task);
      list.prepend(row);
      input.value = '';
      syncEmpty();
      announce('Task added.');
    } catch (failure) { announce(''); showError(failure.message); }
    finally { setBusy(create, false); input.focus(); }
  });

  const toggle = async form => {
    const row = form.closest('[data-task-row]');
    if (busy.has(row)) return;
    const checkbox = form.querySelector('input[type=checkbox]');
    const previous = row.classList.contains('is-complete');
    const data = new FormData(form);
    row.classList.toggle('is-complete', checkbox.checked);
    showError('');
    setBusy(row, true);
    announce('Saving task…');
    try {
      const payload = await post(form, data);
      setTask(row, payload.task);
      announce(payload.task.completed ? 'Task completed.' : 'Task marked incomplete.');
    } catch (failure) {
      checkbox.checked = previous;
      row.classList.toggle('is-complete', previous);
      announce(''); showError(failure.message);
    } finally { setBusy(row, false); checkbox.focus(); }
  };
  list.addEventListener('change', event => {
    if (event.target.matches('[data-task-toggle] input[type=checkbox]')) toggle(event.target.form);
  });
  const remove = async form => {
    const row = form.closest('[data-task-row]');
    if (busy.has(row)) return;
    const data = new FormData(form);
    data.set('confirm_delete', 'yes');
    showError(''); setBusy(row, true); announce('Deleting task…');
    try {
      const payload = await post(form, data);
      if (String(payload.deleted_id) !== row.dataset.taskId) throw new Error('Unexpected server response. Reload to check your tasks.');
      const next = row.nextElementSibling || row.previousElementSibling;
      row.remove(); syncEmpty(); announce('Task deleted.');
      (next?.querySelector('input[type=checkbox]') || input).focus();
    } catch (failure) {
      announce(''); showError(failure.message); setBusy(row, false);
      form.querySelector('button').focus();
    }
  };
  const confirm = form => {
    if (busy.has(form.closest('[data-task-row]'))) return;
    if (typeof dialog.showModal !== 'function') {
      if (window.confirm('Delete this task? This cannot be undone.')) remove(form);
      return;
    }
    pendingDelete = form;
    dialog.querySelector('[data-delete-title]').textContent = form.closest('[data-task-row]').querySelector('.task-title').textContent;
    dialog.showModal();
    dialog.querySelector('[data-delete-cancel]').focus();
  };
  dialog.querySelector('[data-delete-cancel]').addEventListener('click', () => dialog.close());
  dialog.querySelector('[data-delete-confirm]').addEventListener('click', () => {
    const form = pendingDelete;
    dialog.close();
    if (form) remove(form);
  });
  dialog.addEventListener('close', () => {
    pendingDelete?.querySelector('button').focus();
    pendingDelete = undefined;
  });
  list.addEventListener('submit', event => {
    if (event.target.matches('[data-task-toggle]')) { event.preventDefault(); toggle(event.target); }
    if (event.target.matches('[data-task-delete]')) { event.preventDefault(); confirm(event.target); }
  });
  workspace.classList.add('task-enhanced');
}
