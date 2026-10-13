export function initializeDesignPreviews() {
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
}
