# Fernward frontend — cozy journal revision

## Woodland and aurora refinement

The next visual pass restores a clearly visible animated periwinkle/blue/violet aurora rather than the previous near-invisible wash. The dashboard now has an illustrated clearing banner: flowing sky above layered original SVG pine trees, broadleaf trees, rolling green hills and foreground foliage. Text sits over a paper fade, and task cards remain quiet paper surfaces. Landing and authentication scenery also use the woodland artwork, with stronger aurora color. Sidebar, notebook heading, binding details, fox companion note and fern accents now carry more woodland green in both light and warm dark themes.

New assets are `static/images/woodland-clearing.svg` and `static/css/woodland.css`. Shared base, dashboard, home and authentication templates include the new visual layer. Backend and task-preview behavior are unchanged. Reduced motion still stops the sky animation. This refinement was re-rendered through the existing form-contract harness and rechecked at the four target responsive widths in both themes.

Authentication spacing fix: login and registration foxes are slightly smaller and sit lower in the scene, with space above “I saved you a little spot.” The stationery note is positioned separately and remains above the decorative artwork so the tail cannot obscure “Remember to pause.” Both pages were checked at 375, 768, 1024 and 1440 pixels with no horizontal overflow or note/intro collision; form contracts still pass the rendering checks.

Final illustrative touch: the aurora now includes three original translucent SVG wave ribbons over its soft color fields. Each ribbon independently translates, rotates/skews and stretches with different periods and phases, creating visibly overlapping geometric waves rather than hue cycling. The dashboard sky moves more slowly than the public/authentication scenes. The static SVG composition remains visible with reduced motion.

The curious fox holds a small journal, the cheerful fox has a cup of tea, and the resting fox curls over a book. These props connect the same character to the notebook, welcome ritual and empty-state message. On a user-requested companion thought, its pose alternates with a short greeting motion; no task data or authentication values are inspected. A quiet two-pixel breathing motion accompanies the resting empty-state fox, and the authentication fox settles into place once without fading out or hiding the form. All added motion honors reduced-motion preference, including the event-triggered greeting. Completion feedback stays confined to its labeled frontend-only sketchbook.

Final-touch verification: all three ribbons' computed geometry changed between browser observations, and the companion message action changed the fox pose while real task controls remained disabled. All five pages again passed the 40 layout combinations across both themes and four target widths, with their SVG assets loaded. Form rendering/escaping contracts, JavaScript syntax and mascot SVG XML were rechecked. The existing live-authentication, OS-motion and performance-testing limitations below still apply.

## Landscape, validation and wording polish

The home-page forest now spans the full content viewport, including mobile, with a soft top fade into the aurora. Its former partial-width hard edge and sideways clipping are removed; the artwork reads as a continuous landscape rather than a placed image.

Login and registration show required-field messages below the corresponding inputs, with an invalid border, `aria-invalid`, associated descriptions and focus on the first missing field. Correcting a field clears its local message and restores any existing server-error description. This presentation handles only native `valueMissing` failures. The `required` attributes, browser validity checks, form methods/actions, input names and server validation remain intact; no `novalidate` or programmatic submit bypass is introduced. With JavaScript unavailable, the browser’s original required-field UI remains the fallback. The password’s text is never read by this handler; it uses the browser validity state only.

The wording review removed repeated small/little/gentle marketing phrases, clarified Create an account, Search tasks and task labels, trimmed redundant decorative sparkles/empty markup, and replaced the sample’s invented Gentle priority with Medium priority. An About Fernward link uses the existing About route. The cheerful fox’s description now correctly refers to its tea rather than a journal. The woodland/fox identity and interactive design previews remain intact.

Verification: required errors appear on both forms without navigation, first-field focus is correct, and correcting the username clears only its own message. All five pages passed 40 responsive/theme combinations again, including registration with its errors visible. The forest covers the full content width at each target size; SVG images load and no horizontal overflow occurs. Existing Flask/Jinja form, CAPTCHA, username/error escaping and logout contract checks pass. Live authenticated submissions and Turnstile verification remain outside the temporary static preview.

## What changed in this revision

Fernward now feels like a personal journal and woodland study nook. Warm cream and parchment surfaces, dusty mauve, soft lavender and sage replace the previous silver/indigo direction. Dark mode uses warm brown paper, cream text and a soft lamplight wash. Serif headings and small, local handwriting-style accents complement readable system-font controls. Texture is made from lightweight CSS gradients; there are no remote fonts or image dependencies.

The landing page welcomes users with a taped notebook, a waving fox and personal copy. Login and registration keep their existing forms while adding paper rules, botanical drawings and a small note to yourself. Aurora motion remains around public/authentication scenery and in the dashboard clearing banner. The notebook task area does not animate continuously.

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
# Targeted UI refinement

## Responsive and performance pass

Root cause: at 2560px the body and atmosphere filled the viewport, but the public header's paper-to-transparent background stopped at its 1480px foreground cap (x=540). Moving that gradient into the full-width atmosphere removes the visible boundary without widening the foreground. The previous woodland SVG used preserveAspectRatio=none and was stretched to viewport width; the landing page now uses a seamless mirrored panorama at proportional sizing with horizontal repetition. The panorama reuses the original paths through SVG use elements rather than duplicating the artwork. Other pages retain the original SVG.

Consolidated superseded hero and aurora declarations and duplicate journal header/card properties. Removed the continuous border-radius morph (a paint-changing animation); transform drift and the three overlapping SVG ribbons remain. Page-specific interaction modules load only when needed. Companion DOM and motion-query references are cached, and rapid reactions cancel the previous animation; changing to reduced motion cancels a current reaction. No continuous JavaScript animation loop was added.

Checked all five pages at 375, 768, 1024, 1440, 1920, and 2560px, at 640px and 1080px heights, in both themes (120 combinations): no horizontal overflow or broken images. Full atmosphere bounds match available page width, allowing fractional pixels and the vertical scrollbar. Inspected the ultrawide artwork and phone error layout, mobile menu/Escape focus behavior, and companion reactions. Script-free rendered copies retain required input blocking and POST forms; dashboard navigation/logout remains accessible without scripts. Reviewed reduced-motion stylesheet rules and runtime guards; the browser tool cannot emulate the OS reduced-motion preference, so that preference was not toggled during testing. Live Flask authentication/CAPTCHA/Redis were not exercised. Template contracts, JS syntax, SVG XML, scope, and whitespace checks pass; no repository test suite was found. Palette, warning text, Jinja escaping, and all backend/security files remain unchanged.

The landing hero now gives the fox and notebook more presence, keeps the full woodland backdrop and moving overlapping aurora waves, and explains that organizing tasks is coming soon. The dashboard welcome area and companion are more compact; the task heading, disabled Add Task action, search, and filters take priority.

Login and registration share an original SVG warning icon and muted rose alert styling. Server messages remain escaped and unchanged. Inline required-field feedback only presents the browser's existing native required errors; normal POST submissions, native constraints, conditional Turnstile, and server validation remain authoritative.

Presentation JavaScript is organized into theme-controls, navigation, auth-forms, companion, and design-previews modules, with interface.js as their entry point. No authentication, CAPTCHA verification, session handling, task persistence, network requests, or unsafe HTML insertion were added. Companion responses are user-triggered; animation respects reduced motion. Design specimens remain explicitly labeled frontend-only examples.

Validation: all five pages checked at 375, 768, 1024, and 1440 pixels in both themes (40 combinations), with no horizontal overflow or broken images. Empty form submission retains native blocking, displays both required messages, focuses the first field, and clears the username message when filled. Mobile menu opening/Escape and companion responses checked. Template rendering checks cover POST actions, field names, conditional Turnstile, escaping, logout, and reusable task-card escaping. Live authentication and CAPTCHA verification require the owner's configured Flask services and were not exercised by the static preview.
