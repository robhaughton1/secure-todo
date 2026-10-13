/* Presentation only. Flask remains authoritative for application/security behavior. */
import { initializeThemeControls } from './theme-controls.js';
import { initializeNavigation } from './navigation.js';
import { initializeAuthForms } from './auth-forms.js';
import { initializeCompanion } from './companion.js';
import { initializeDesignPreviews } from './design-previews.js';

initializeThemeControls();
initializeNavigation();
initializeAuthForms();
initializeCompanion();
initializeDesignPreviews();
