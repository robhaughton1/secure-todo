# Fernward frontend

## Design and scope

The identity uses one original violet woodland fox with a sage fern-shaped tail and a matching small fox-and-leaf mark. Both are local SVG assets. Silver, periwinkle, lavender and indigo aurora fields move and morph with different CSS animation periods. Authentication pairs a clear form with an illustrated woodland panel; the dashboard limits aurora to its welcome banner.

No backend files, routes, models, database records, environment configuration, authentication logic or security dependencies are changed. Existing POST form actions, field names, username and error variables, conditional Turnstile site key and POST logout are preserved. The existing unused cat/frog assets remain in the repository but are not used in the redesigned pages.

## Preview locally

Check out `feature/dashboard-ui`, install the existing `requirements.txt`, and follow the existing root README to configure your own local secrets, Turnstile widget and Redis service. With those prerequisites already configured:

```powershell
python app.py
```

Open `http://127.0.0.1:5000`. Visit `/login` and `/register`; use a real account to visit `/dashboard`. `/about` also uses the shared visual system. Do not change security settings to preview the design.

## Future task integration

The current dashboard intentionally has no task records. Summary cards show unavailable values rather than fabricated counts. Search, filters, Add Task and Create Your First Task are disabled and accompanied by a visible explanation. Future navigation destinations and Settings are noninteractive text marked Soon.

`templates/partials/task-card.html` is an unused, autoescaped component. Its proposed presentation fields are `title`, `description`, `priority`, `status` and `due_date_label`; these are a future integration suggestion, not an existing backend contract. It supports a completed checkbox, priority/status/due-date metadata and disabled edit/delete actions. When the owner builds secure task routes, connect verified server data, replace the empty state conditionally, compute summaries on the server, and then enable controls with their real actions. No browser task storage or fake endpoints exist.

Theme preference is the only persisted frontend state, under `fernward-theme` in local storage. System preference is used without a manual preference. If storage is blocked, theme toggling still works for the current page. With JavaScript unavailable, forms still submit and mobile sidebar/logout remain visible. Mobile menu uses an expanded state, focuses its first link on opening, and returns focus to its button on Escape.

## Validation performed

- Rendered landing, login, registration, dashboard and about through Flask/Jinja in a separate temporary preview harness, without importing or altering `app.py`.
- Verified login and registration POST contracts, input names/autocomplete, conditional Turnstile markup/site key, error alerts, preserved username values and POST logout.
- Tested escaping of markup in usernames, error messages and future task fields.
- Checked all four main pages in light and dark themes at 375, 768, 1024 and 1440 pixels: no horizontal overflow; SVG assets loaded.
- Visually reviewed desktop login, tablet dark login, mobile dashboard and landing composition. Checked the mobile menu’s open/closed state, keyboard focus and Escape handling, and theme persistence across navigation.
- Verified keyboard traversal from username to password and decorative focus response without inspecting password values.
- Observed changing aurora transforms and border radius, and inspected the loaded reduced-motion CSS rules that disable animation and transitions.
- Checked JavaScript syntax and Git whitespace/diff boundaries.
- Calculated contrast for core text, muted text and buttons in both themes: all exceed 4.5:1 (light muted text 5.48:1; dark muted text 8.18:1). This is a palette check, not a full automated accessibility audit.

## Remaining checks

Full end-to-end login, registration, session/logout and live Turnstile verification were not exercised: the original app requires the owner’s configured keys and Redis service. The temporary preview is rendered frontend HTML, not an authentication implementation. Reduced motion and automatic system theme changes were inspected in code but not toggled at OS level. No screen reader audit or device performance profiling was performed. Run those checks in the configured application before merging. No PR should be merged automatically.

## Modified and created files

Modified: `static/css/style.css`; `templates/home.html`; `templates/login.html`; `templates/register.html`; `templates/dashboard.html`; `templates/about.html`.

Created: `static/images/fernward-fox.svg`; `static/images/fernward-mark.svg`; `static/js/theme.js`; `static/js/interface.js`; `templates/base.html`; `templates/auth.html`; `templates/partials/brand.html`; `templates/partials/aurora.html`; `templates/partials/public-nav.html`; `templates/partials/theme-toggle.html`; `templates/partials/icons.html`; `templates/partials/task-card.html`; `docs/frontend-design.md`.
