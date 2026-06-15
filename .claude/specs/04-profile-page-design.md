# Spec: Profile Page

## Overview
The profile page gives a logged-in user a single place to see their own
account details — display name, email, and the date they joined Spendly.
It is the first authenticated, user-specific page in the roadmap: Steps 1–3
established the database, registration, and login/logout, and this step
(Step 4) turns the existing `/profile` stub into a real, protected page.
It also lays down the `.profile-*` visual pattern that later account/settings
work can build on. No data is editable yet — this step is read-only display.

## Depends on
- **Step 01 — Database Setup:** `users` table, `get_db()`, `init_db()`.
- **Step 02 — Registration:** users exist to view.
- **Step 03 — Login/Logout:** `session['user_id']` is set on login and
  `get_user_by_id()` already exists in `database/db.py`.

## Routes
- `GET /profile` — renders the current user's profile from their session;
  if no `user_id` is in the session, redirect to `/login` — **logged-in only**.

This replaces the current stub (`return "Profile page — coming in Step 4"`).
No other new routes.

## Database changes
No database changes. The `users` table already holds `name`, `email`, and
`created_at`, and `get_user_by_id(user_id)` already exists in
`database/db.py`. No new tables, columns, constraints, or helper functions
are required.

## Templates
- **Create:**
  - `templates/profile.html` — extends `base.html`, fills `{% block title %}`
    and `{% block content %}`. Displays the user's name, email, and join date
    inside a profile card. Reuses the established header/card layout pattern
    from the auth pages.
- **Modify:**
  - None required. `base.html` already renders the "Profile" nav link for
    logged-in users via `{{ url_for('profile') }}`.

## Files to change
- `app.py` — implement the `GET /profile` route: read `session.get('user_id')`,
  redirect to `login` if absent, fetch the user with `get_user_by_id()`,
  and render `profile.html`.
- `static/css/style.css` — add `.profile-*` styles (using existing CSS
  variables only).

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies. Works within the existing `requirements.txt`
(Flask + werkzeug already imported in `app.py`).

## Rules for implementation
- No SQLAlchemy or ORMs — SQLite via `database/db.py` only.
- Parameterised queries only (`?` placeholders) — no f-strings in SQL.
- Passwords hashed with werkzeug — never display or expose `password_hash`
  in the template or route.
- Use CSS variables (e.g. `--ink`, `--paper-card`, `--accent`, `--border`,
  `--radius-md`) — never hardcode hex values.
- All templates extend `base.html`.
- No DB logic inline in the route — use the existing `get_user_by_id()` helper.
- All internal links via `url_for()` — never hardcode URLs.
- Auth check pattern matches existing routes: `if not session.get('user_id'):`
  → `redirect(url_for('login'))`.
- Vanilla JS only (none expected for this page).
- The route stays single-responsibility: auth-check, fetch, render.

## Definition of done
Verifiable by running the app (`python app.py`, port 5001):

1. Visiting `/profile` while **logged out** redirects to the login page.
2. Visiting `/profile` while **logged in** renders `profile.html` (HTTP 200),
   not the old `"Profile page — coming in Step 4"` string.
3. The page displays the logged-in user's **name**, **email**, and
   **join date** (`created_at`) — verifiable with the seeded
   `demo@spendly.com` / `demo123` account.
4. The `password_hash` value never appears anywhere in the rendered page.
5. The "Profile" link in the navbar resolves and loads the page for a
   logged-in user.
6. The page extends `base.html` (shared navbar/footer present) and applies
   `.profile-*` styles defined with CSS variables — no inline `<style>`
   blocks and no hardcoded hex values.
7. App starts with no errors and existing routes/tests are unaffected
   (`pytest` passes).
