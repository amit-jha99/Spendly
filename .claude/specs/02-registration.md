# Spec: Registration

## Overview
This feature lets a new visitor create a Spendly account. It adds a `POST`
handler to the existing `/register` route that validates the submitted name,
email, and password, hashes the password with werkzeug, and persists the new
user to the `users` table via a dedicated `database/db.py` helper. On success
the user is shown with a  success message and then redirected to the login page; on failure the form re-renders with
a clear error message. This is the first write-path feature in the roadmap and
unlocks Step 3 (Login/Logout), which depends on real user records existing.

## Depends on
- **Step 1 — Database Setup** (complete): `users` table, `get_db()`,
  `init_db()`, and `seed_db()` already exist in `database/db.py`.

## Routes
- `GET /register` — render the registration form (already implemented; keep) — public
- `POST /register` — validate input, create the user, redirect to login on success or re-render with an error — public

No other new routes.

## Database changes
No schema changes. The `users` table already has all required columns:
`id`, `name`, `email` (UNIQUE NOT NULL), `password_hash`, `created_at`.

This step adds two helper functions to `database/db.py` (no new tables/columns):
- `get_user_by_email(email)` — return the user row or `None`.
- `create_user(name, email, password_hash)` — insert a user and return the new id.

## Templates
- **Create:** none.
- **Modify:**
  - `templates/register.html` — change the form `action="/register"` to
    `action="{{ url_for('register') }}"` to comply with the no-hardcoded-URL
    rule. The existing `{% if error %}` block already renders errors and needs
    no change. Field names (`name`, `email`, `password`) stay as-is.

## Files to change
- `app.py` — extend the `register` view to accept `POST`, add validation,
  call the db helpers, and redirect/re-render.
- `database/db.py` — add `get_user_by_email()` and `create_user()`.
- `templates/register.html` — use `url_for()` in the form action.
- `CLAUDE.md` — update the route status table: `POST /register` Implemented.

## Files to create
None.

## New dependencies
No new dependencies. `flask` and `werkzeug` are already in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only.
- Parameterised queries only (`?` placeholders) — never f-strings in SQL.
- Passwords hashed with `werkzeug.security.generate_password_hash`; never
  store or log the plaintext password.
- All DB access lives in `database/db.py` — no inline SQL in `app.py`.
- The `register` view stays single-responsibility: validate, delegate to db
  helpers, render/redirect.
- All internal links and form actions use `url_for()` — never hardcode URLs.
- All templates extend `base.html`.
- Use CSS variables — never hardcode hex values (no new CSS expected, but if
  any is added it must follow this rule).
- Do NOT log the user in or create a session — authentication is Step 3.
  Registration redirects to `GET /login` on success.
- Validation rules:
  - All three fields (`name`, `email`, `password`) required and non-empty
    (strip whitespace).
  - Password minimum length 8 characters (matches the form's placeholder).
  - Duplicate email must be rejected with a friendly error — check via
    `get_user_by_email()` before insert; the `UNIQUE` constraint is the
    backstop.
- On any validation/duplicate failure, re-render `register.html` with an
  `error` context variable and HTTP 200 (preserve the form). Use `abort()`
  only for genuine HTTP error conditions, not validation feedback.

## Definition of done
- `GET /register` still renders the form unchanged.
- Submitting valid new details creates exactly one row in `users` with a
  hashed `password_hash` (not plaintext) and redirects to `GET /login`.
- Submitting an email that already exists re-renders the form showing the
  duplicate-email error and creates no new row.
- Submitting a password shorter than 8 characters re-renders the form with a
  password-length error and creates no new row.
- Submitting with any blank field re-renders the form with an error and
  creates no new row.
- The `register.html` form action uses `url_for('register')` (no hardcoded
  URL remains).
- `database/db.py` exposes `get_user_by_email()` and `create_user()`, both
  using parameterised queries.
- `pytest` passes (existing tests remain green; new tests for the cases above
  pass if added).
