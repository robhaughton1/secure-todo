# Fernward staging deployment (Render + Neon + Upstash)

This is a **staging** deployment guide. Do not use real passwords or sensitive task data until the deployment has been verified.

## 1. Neon: persistent PostgreSQL

Create a Neon project and copy its connection string. Set Render's `DATABASE_URL` to that value (use the provider's SSL-enabled connection string). The app converts `postgres://` or `postgresql://` URLs to the psycopg driver dialect.

Do **not** use SQLite on Render's ephemeral filesystem: user and task data can be lost when the service is replaced or restarted.

## 2. Upstash: Redis TCP/TLS

Create an Upstash Redis database and locate its **Redis TCP** endpoint and password. Set `REDIS_URL` to its `rediss://` connection string (TLS). **Do not use** an Upstash REST URL; Fernward uses Redis commands and Lua scripts through the Python Redis client.

Keep the Redis URL secret. If the provider restricts network access or commands, confirm that `GET`, `SET`, `DEL`, `EVALSHA`, `INCR`, and `EXPIRE` work.

## 3. Cloudflare Turnstile

Add the final Render hostname to the Turnstile widget's allowed hostnames. Set `TURNSTILE_ALLOWED_HOSTNAMES` to that exact hostname, **without** `https://` or a trailing slash. The site and secret keys must belong to the widget configured for this hostname.

## 4. Render web service

Connect the GitHub repository and select this deployment branch while testing.

- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --bind 0.0.0.0:$PORT app:application`
- One-time database initialization: `python init_db.py` (run with the same environment variables as the web service, before first use; this is not a migration tool)

Set these environment variables in Render, **not in GitHub**:

| Variable | Value |
| --- | --- |
| `APP_ENV` | `production` |
| `TRUST_PROXY` | `1` only when traffic comes through the expected single trusted reverse proxy |
| `SECRET_KEY` | A new random 32-byte-or-longer secret, separate from local development |
| `USERNAME_HMAC_KEY` | Another independent random secret |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `REDIS_URL` | Upstash Redis TCP/TLS connection string, starting with `rediss://` |
| `TURNSTILE_SITE_KEY` | Cloudflare widget site key |
| `TURNSTILE_SECRET_KEY` | Cloudflare widget secret |
| `TURNSTILE_ALLOWED_HOSTNAMES` | Exact Render hostname, e.g. `fernward-example.onrender.com` |

Generate each secret separately with `python -c "import secrets; print(secrets.token_hex(32))"`. Never commit secrets, provider URLs containing passwords, or `.env`.

**Important:** The initial schema must exist before registering an account. Run `python init_db.py` using the production environment through a secure one-time job or trusted shell. If your free hosting tier does not provide a shell, use an equivalent secure one-off process with the environment injected; do not add a public database initialization endpoint.

## 5. Verification checklist

- The public URL uses HTTPS, and Flask is running under Gunicorn with debug disabled.
- Register and log in using **test-only** credentials; create, complete, and delete a task.
- Restart/redeploy the web service; confirm the task persists in Neon.
- Confirm the session cookie has Secure, HttpOnly, and SameSite attributes.
- Confirm CSRF requests without a valid token are rejected (previous local tests do not replace staging verification).
- Trigger the failed-login threshold with a test account and verify Turnstile works on the hosted domain.
- Log out and verify the prior authenticated session cannot be replayed.
- Confirm rate limits and session storage use Upstash over TLS.

Free-tier quotas, billing rules, sleep behavior, and network support can change; check current provider terms before enabling services. Do not merge or invite your teammate until staging checks pass.
