export function initializeAuthForms() {
  /* Decorative focus response only. Never inspect field values. */
  document.querySelectorAll('.authForm').forEach(form => {
    form.addEventListener('focusin', () => document.body.classList.add('form-engaged'));
    form.addEventListener('focusout', event => { if (!form.contains(event.relatedTarget)) document.body.classList.remove('form-engaged'); });
    /* Present native required-field failures inline; keep required and normal POST submission. */
    const fields = [...form.querySelectorAll('[data-required-message]')];
    const descriptions = new Map(fields.map(field => [field, field.getAttribute('aria-describedby') || '']));
    let focusQueued = false;
    form.addEventListener('invalid', event => {
      const field = event.target;
      if (!fields.includes(field) || !field.validity.valueMissing) return;
      const message = document.getElementById(`${field.id}-required`);
      const text = message?.querySelector('[data-field-error-text]');
      if (!text) return;
      event.preventDefault();
      text.textContent = field.dataset.requiredMessage;
      message.hidden = false;
      field.setAttribute('aria-invalid', 'true');
      field.setAttribute('aria-describedby', [descriptions.get(field), message.id].filter(Boolean).join(' '));
      if (!focusQueued) {
        focusQueued = true;
        queueMicrotask(() => {
          form.querySelector('[data-required-message][aria-invalid="true"]')?.focus();
          focusQueued = false;
        });
      }
    }, true);
    fields.forEach(field => field.addEventListener('input', () => {
      if (!field.validity.valid) return;
      document.getElementById(`${field.id}-required`).hidden = true;
      field.removeAttribute('aria-invalid');
      const original = descriptions.get(field);
      if (original) field.setAttribute('aria-describedby', original);
      else field.removeAttribute('aria-describedby');
    }));
  });
}
