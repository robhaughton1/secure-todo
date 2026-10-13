# Fernward frontend — cozy journal revision

## What changed in this revision

Fernward now feels like a personal journal and woodland study nook. Warm cream and parchment surfaces, dusty mauve, soft lavender and sage replace the previous silver/indigo direction. Dark mode uses warm brown paper, cream text and a soft lamplight wash. Serif headings and small, local handwriting-style accents complement readable system-font controls. Texture is made from lightweight CSS gradients; there are no remote fonts or image dependencies.

The landing page welcomes users with a taped notebook, a waving fox and personal copy. Login and registration keep their existing forms while adding paper rules, botanical drawings and a small note to yourself. Aurora motion remains on public/authentication pages at much lower opacity and softer blur. The actual task workspace does not animate continuously.

The dashboard is now **Your journal**. Analytics cards are removed entirely. The task notebook is the main visual area, with paper rules, binding loops and a resting-fox empty state. A smaller companion note sits alongside it; its gentle messages change only when the user requests another thought. A seed-to-sprout-to-fern sketch is explicitly decorative, a future feature, and not connected to tasks or progress. There are no counts, scores, streaks or pressure messages.

## Fox identity and artwork

The original violet fox, cream facial markings, forehead leaves and sage fern-tail identity are retained. Four original local SVG variations extend its personality:

- `fernward-fox-curious.svg`: tilted head and open, curious eyes; registration and companion nook.
- `fernward-fox-cheerful.svg`: smiling expression, warm cheeks and a waving paw; landing/login and completion preview.
- `fernward-fox-resting.svg`: curled-up body, lowered head and resting forepaws; genuine empty state and About page.
- `fernward-fox-celebrating.svg`: raised paws and a few quiet botanical marks; future all-done feedback.

`fern-sprig.svg` decorates authentication. `fern-growth.svg` is a small sequence of purely decorative growth sketches. The original `fernward-fox.svg` and small mark remain in the identity; the mark’s surrounding tile now uses dusty lavender.

## Design previews, not working task features

The actual dashboard remains empty. Add Task, first-task creation, search and filters are disabled, with a visible explanation that task management is not implemented. Future navigation destinations and Settings are noninteractive text marked Soon.

The collapsible **From the sketchbook** section is labeled **Frontend-only design previews**. It contains one illustrative task card and controls for pending, completed, empty and all-done visual states. Each example is identified as a design example, and the disclosure explicitly says no real tasks or saved changes exist. The example checkbox only changes the isolated preview’s DOM: a line through the title, a cheerful fox, a short single animation and “Yay! You did it!” feedback. A polite live region identifies the reaction as a design preview and states that nothing was saved. It resets on reload, uses no storage, and makes no network request.

These components are prepared for later integration:

- `partials/task-card.html`: future server-rendered task card, with an `is-complete` class when its status is completed. Task actions remain disabled.
- `partials/journal-empty.html`: the genuine unavailable/empty dashboard state, including the resting fox.
- `partials/completion-feedback.html`: a future all-done presentation. It is currently rendered only within the labeled sketchbook example, never as a claim about real user progress.
- `partials/design-sketchbook.html`: isolated demonstration UI, removable when real task functionality is ready.

The proposed task presentation fields remain `title`, `description`, `priority`, `status` and `due_date_label`. They are suggestions for future integration, not an existing backend contract. When secure task routes exist, connect authorized server data, choose appropriate empty/completed states on the server, and enable controls only with their actual actions. Do not treat the preview handler as a CRUD implementation.

## Preserved boundaries and accessibility

No changes to `app.py`, routes, authentication, sessions, models, Redis, security settings, dependencies or environment configuration. Existing login/register POST actions, input names and autocomplete, Jinja username/error variables, conditional Turnstile site key, and POST logout are retained. Untrusted fields remain autoescaped. No `safe` filter, inline script or HTML injection is introduced.

Theme preference is still the only persisted frontend state (`fernward-theme`); system preference applies when there is no manual preference. Storage failure does not prevent current-page theme switching. With JavaScript unavailable, forms submit normally, sidebar/logout remain reachable on mobile, and sketchbook interaction controls stay hidden/disabled. The static illustrative card remains labeled.

Mobile navigation exposes its expanded state, focuses its first link on opening, closes on Escape and returns focus to its button. Task preview controls retain keyboard focus, use pressed states and have explicit labels. The native sketchbook disclosure works with keyboard input. Companion messages are user-triggered and politely announced; they never rotate automatically. Global reduced-motion rules disable aurora, decorative focus movement, transitions and the short fox reaction.

## Preview locally

Use the existing `feature/dashboard-ui` branch and follow the root README for the application’s current Python requirements, your local keys and Redis setup. With those prerequisites already configured:

```powershell
python app.py
```

Open `http://127.0.0.1:5000`. Visit `/login` and `/register`, and use your account for `/dashboard`. Expand **From the sketchbook** to review the explicitly labeled visual states. No setup or security changes are required by this frontend revision.

## Verification for this revision

- Rendered all five pages through a separate temporary Flask/Jinja preview harness. Verified escaped usernames/errors/task fields, preserved login/register contracts, conditional CAPTCHA markup, authenticated username rendering and POST logout.
- Checked all five pages at 375, 768, 1024 and 1440 pixels in both themes: 40 layout combinations, no horizontal overflow, all rendered SVG assets loaded.
- Visually reviewed parchment landing, lamplit login, desktop journal, mobile login and mobile all-done preview.
- Exercised the example checkbox, completed/empty/all-done presentations, polite completion announcement and reset after reload. Real task controls remained disabled throughout.
- Checked keyboard checkbox/disclosure operation, username-to-password traversal, mobile menu opening/focus/Escape, companion message changes and theme persistence across navigation.
- Core palette contrast: light body 10.26:1, light muted text 5.05:1, sage on its soft background 4.96:1, light button 5.67:1; dark body 11.32:1, dark muted text 6.99:1 and dark button 8.65:1. This is not a full accessibility audit.
- Inspected loaded reduced-motion CSS; checked JavaScript syntax, SVG XML validity, diff whitespace and frontend-only file boundaries.

Limitations: full end-to-end authentication, registration, sessions/logout and live Turnstile verification require the owner’s configured keys and Redis service and were not exercised. The preview harness renders HTML and does not implement authentication. OS reduced-motion/system-theme settings were not toggled; their code and loaded styles were reviewed. No screen-reader audit or hardware performance profiling was performed. Run those checks in the configured application before merging.

## Files changed in this revision

Modified: `docs/frontend-design.md`; `static/css/style.css`; `static/images/fernward-mark.svg`; `static/js/interface.js`; `templates/base.html`; `templates/home.html`; `templates/auth.html`; `templates/login.html`; `templates/register.html`; `templates/dashboard.html`; `templates/about.html`; `templates/partials/task-card.html`.

Created: `static/css/cozy.css`; `static/images/fernward-fox-curious.svg`; `static/images/fernward-fox-cheerful.svg`; `static/images/fernward-fox-resting.svg`; `static/images/fernward-fox-celebrating.svg`; `static/images/fern-sprig.svg`; `static/images/fern-growth.svg`; `templates/partials/journal-empty.html`; `templates/partials/completion-feedback.html`; `templates/partials/design-sketchbook.html`.

The original PR also adds `templates/base.html`, `templates/auth.html`, shared brand/aurora/navigation/theme/icon/task-card partials, `static/js/theme.js`, the base fox and the brand mark. PR #7 remains the review location; it must remain unmerged.
