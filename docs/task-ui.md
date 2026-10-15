# Task interface refinement

Latest input/auth polish: native empty-task failures and whitespace-only submissions get a styled inline warning and an associated invalid-field state, cleared when corrected. Backend title validation remains authoritative. Task warnings retain the shared SVG icon when messages change. Login/register replace the repeated small brand mark with an original fern-and-open-journal SVG and remove the top “Come in. Get comfortable.” banner; the main navigation logo is unchanged. Eight route tests, JS syntax, XML, and template checks pass. This pass's localhost browser preview timed out, so visual validation of these final touches remains manual.

The task notebook now has a styled creation form, wrapping titles, accessible trash controls, and muted completed rows. Decorative and repeated captions were trimmed; the woodland header, fox interactions, unavailable filters/navigation, growth illustration, and sketchbook remain. The sketchbook clearly identifies unsaved design examples; it no longer says real task management is unavailable.

## Files

- `app.py`: content negotiation and JSON task responses on the existing three task routes; server-rendered deletion confirmation for form fallback.
- `templates/dashboard.html`: concise layout, live task list, status/error feedback, empty state, confirmation dialog, inert row template.
- `templates/partials/live-task.html`: shared escaped task-row macro for initial rendering and client cloning.
- `templates/task-delete-confirm.html`: normal POST confirmation without JavaScript.
- `static/js/tasks.js`: Fetch enhancement, pending guards, failure rollback, safe DOM updates, dialog/focus management.
- `static/js/interface.js`: load the task module only on the task workspace.
- `static/css/tasks.css`: theme-aware task controls, states, mobile layout, focus-compatible styling.
- `templates/partials/icons.html`, `design-sketchbook.html`, `journal-empty.html`: trash icon and concise, accurate preview copy.
- `templates/home.html`, `templates/about.html`: removed obsolete task-management-coming-soon copy.
- `tests/test_tasks.py`: eight standard-library unittest regressions using real Flask routes, in-memory SQLite, and mocked Redis.

## Behavior and security

Every mutation still checks the existing Redis-backed authenticated session and CSRF token. Completion/deletion queries still require both task ID and the authenticated user's ID. Models, login, registration, logout, session handling, CAPTCHA, rate limiting, dependencies, and configuration are unchanged. JSON is selected via `Accept: application/json`; ordinary forms retain redirects. Creation returns the committed task with its ID and action URLs, completion returns its committed state, and deletion returns the deleted ID.

Fetch uses same-origin credentials and each form's CSRF field. No credentials or task data enter browser storage. Titles and errors use textContent or escaped Jinja output, never innerHTML. Creation inserts a row only after success; deletion removes it only after success. A pending row blocks conflicting completion/deletion. Failed completion restores the prior check state, failed deletion retains the row, and a failed creation keeps the input. Network uncertainty asks users to reload before retrying; mutations are never retried automatically.

Deletion requires explicit confirmation in both modes: a keyboard-accessible native dialog with Cancel focused first, or a server-rendered POST confirmation page. Checkbox changes use Fetch with JavaScript; an Apply change button is available without it. Focus returns to the creation field after adding, a nearby task after deletion, or the original control after cancellation/error. The native dialog contains keyboard focus while open and supports Escape.

## Validation

- Eight route regressions pass: create/escaping, length validation, CSRF rejection for all mutations in both formats, cross-user rejection/list isolation, completion/reversal persistence, explicit deletion confirmation, HTML redirects, and expired/missing/Redis-unavailable sessions.
- Browser checked async creation, persistence after reload, completion/reversal, cancel/Escape, deletion, empty-list transitions, simulated create/update/delete failures with rollback, long HTML-looking titles rendered literally, and script-free form creation/completion/deletion confirmation.
- Dashboard at 375/768/1024/1440/1920/2560px in both themes: no horizontal overflow or broken images. Mobile navigation and existing fox responses checked. JavaScript syntax and whitespace checks pass.
- Existing global reduced-motion CSS and companion guards remain; no new continuous animation added. OS reduced-motion switching was not emulated.

Tests use isolated SQLite and a mocked Redis boundary, not the owner's data. No live Redis/Turnstile end-to-end authentication test was performed. One initial temporary preview failed to locate templates; its test-only loader path was corrected before browser checks. No remaining checks fail.

## Manual review

On the configured app, add a task, complete/reopen it, cancel then confirm deletion, and reload to verify persistence. Check your preferred desktop/mobile size and both themes. Disable JavaScript and repeat with Apply change and the confirmation page. Verify expired-session and service-unavailable messages against your real Redis setup. No deployment or merge performed.
