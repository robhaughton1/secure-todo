/* Progressive UI enhancements. Flask validates and persists every task change. */
import { initializeThemeControls } from './theme-controls.js';
initializeThemeControls();
if (document.querySelector('[data-task-workspace]')) {
  import('./tasks.js').then(({ initializeTasks }) => initializeTasks());
}

/* Load page-specific interactions only where their markup exists. */
if (document.querySelector('[data-menu-toggle], [data-current-date]')) {
  import('./navigation.js').then(({ initializeNavigation }) => initializeNavigation());
}
if (document.querySelector('.authForm')) {
  import('./auth-forms.js').then(({ initializeAuthForms }) => initializeAuthForms());
}
if (document.querySelector('[data-companion-thought]')) {
  import('./companion.js').then(({ initializeCompanion }) => initializeCompanion());
}
if (document.querySelector('[data-design-preview]')) {
  import('./design-previews.js').then(({ initializeDesignPreviews }) => initializeDesignPreviews());
}
