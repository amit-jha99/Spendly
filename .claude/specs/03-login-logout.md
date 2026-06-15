# Spec: Login and Logout

## Overview
This feature lets registered users authenticate into Spendly and end their
session. Step 02 created accounts (`POST /register`) and stored
`werkzeug`-hashed passwords, but there is currently no way to actually sign in
— `GET /login` only renders the form and `GET /logout` is a stub. Step 03 adds
the `POST /login` handler that verifies credentials and establishes a Flask
session, plus a working `GET /logout` that clears it. This is the gateway to
every logged-in feature that follows (profile in Step 04, expense CRUD in
Steps 07–09), so it must establish the session pattern those steps will rely on.

## Depends on
- **Step 01 — Database setup:** requires the `users` table and `get_db()`.
- **Step 02 — Registration:** requires `get_user_by_email()`, the
  `password_hash` column, and the existing `login.html` template (which already
  renders the "Account created — please sign in" flash via `?registered=1`).

## Routes
- `POST /login` — verify submitted email + password against the stored hash;
  on success set the session and redirect, on failure re-render the form with
  an error — **public**
- `GET /login` — render the login form (already implemented; no behavior
  change) — **public**
- `GET /logout` — clear the session and redirect to the landing page
  (currently a stub — to be implemented) — **public** (no-op if not logged in)

## Database changes
No schema changes. The `users` table already has `id`, `email`, and
`password_hash`. One new read helper is added to `database/db.py`:

- `get_user_by_id(user_id)` — `SELECT * FROM users WHERE id = ?`, returns the
  row or `None`. Needed so later steps (and an optional logged-in nav) can
  resolve `session['user_id']` back to a user.

`get_user_by_email(email)` already exists and is reused for login lookup.

## Templates
- **Create:** none.
- **Modify:**
  - `templates/login.html` — change the hardcoded `action="/login"` to
    `action="{{ url_for('login') }}"` (per CLAUDE.md: never hardcode URLs). The
    existing `{% if error %}` and `{% if request.args.get('registered') %}`
    blocks already cover the messaging this feature needs — reuse them, do not
    add new markup.

## Files to change
- `app.py` — import `session` (from `flask`) and `check_password_hash` (from
  `werkzeug.security`); set `app.secret_key` for session signing; implement the
  `POST /login` branch on the existing `login()` route; implement the `logout()`
  route to clear the session and redirect to `landing`.
- `database/db.py` — add `get_user_by_id(user_id)`.
- `templates/login.html` — fix the form `action` to use `url_for`.
- `CLAUDE.md` — update the route status table: add `POST /login` as
  *Implemented* and change `GET /logout` from *Stub — Step 3* to *Implemented*.

## Files to create
- None (no new routes file, template, or stylesheet — login styling already
  exists via `.auth-*` classes in `style.css`).

## New dependencies
No new dependencies. `flask` (sessions) and `werkzeug` (`check_password_hash`)
are already in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs — use `get_db()` and raw SQLite only.
- Parameterised queries only (`?` placeholders) — never f-strings in SQL.
- Passwords verified with `werkzeug.security.check_password_hash` — never
  compare hashes or plaintext manually.
- DB access stays in `database/db.py` — the route must not run SQL inline.
- All templates extend `base.html`; use `url_for()` for every internal link.
- Use CSS variables and the existing `.auth-error` / `.auth-success` classes —
  never hardcode hex values and do not add inline `<style>`.
- The `login()` route handles both GET and POST in one function (mirroring how
  `register()` is structured) — one responsibility: authenticate, then render
  or redirect.
- On failed login, return a single generic error (e.g. "Invalid email or
  password.") for both unknown-email and wrong-password cases — do not reveal
  which field was wrong.
- Store only `session['user_id']` (the integer id) in the session — do not
  store the password hash or the whole user row.
- `app.secret_key` must be set so sessions are signed; keep the existing
  port (5001) unchanged.

## Definition of done
1. Running `python app.py` starts the server on port 5001 with no import errors.
2. Visiting `GET /login` shows the form; viewing source confirms the form posts
   to `/login` via `url_for` (no hardcoded action).
3. Submitting valid credentials for a seeded/registered user redirects away from
   the login page and creates a session (the `session` cookie is set in the
   browser).
4. Submitting a wrong password (or unknown email) re-renders `login.html` with
   the generic "Invalid email or password." error and does **not** set a session.
5. Completing registration then landing on `/login?registered=1` still shows the
   "Account created — please sign in" success message (unchanged behavior).
6. Visiting `GET /logout` clears the session and redirects to the landing page;
   the session cookie no longer authenticates the user.
7. `database/db.py` exposes `get_user_by_id()` returning the correct row for a
   valid id and `None` for a missing id.
8. `CLAUDE.md` route table reflects `POST /login` and `GET /logout` as
   implemented.
