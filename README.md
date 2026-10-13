# Fernward

Fernward is a Flask-based web application with registration, login, an authenticated dashboard, and security controls for login abuse. It is currently configured for **local development**, not production deployment.

## Prerequisites

- Python 3 and `pip`
- Docker Desktop (or a locally running Redis server)
- A Cloudflare Turnstile widget configured to accept `localhost` and `127.0.0.1`, with its site key and secret key

## Local setup

Clone the repository, open its project directory, and create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a file named `.env` in the repository root. It must define these **four environment variables**, with your own values:

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Random Flask session-signing secret |
| `USERNAME_HMAC_KEY` | A separate random secret used to derive non-plaintext username identifiers for Redis |
| `TURNSTILE_SITE_KEY` | Public site key from your Cloudflare Turnstile widget |
| `TURNSTILE_SECRET_KEY` | Private key for server-side Turnstile verification |

Generate two independent, unpredictable values for the first two variables. For example, you can run `python -c "import secrets; print(secrets.token_hex(32))"` twice and use each resulting value for a different key. Do not commit `.env` or share secret keys.

## Start Redis

Fernward uses Redis both for IP-based login request limits and per-username failed-login counters. With Docker Desktop running, create the local Redis container:

```powershell
docker run -d --name fernward-redis -p 127.0.0.1:6379:6379 redis:7-alpine
```

On subsequent runs, start the existing container instead:

```powershell
docker start fernward-redis
```

Check connectivity:

```powershell
docker exec fernward-redis redis-cli ping
```

Redis should reply `PONG`. Do not run `docker run` again if a container with that name already exists.

## Run the application

With your virtual environment active and Redis running:

```powershell
python app.py
```

Visit `http://127.0.0.1:5000`.

The application currently creates its SQLite tables during local startup. Registration creates an account; use the login page to establish an authenticated session before visiting the dashboard.

## Login security behavior

- Login POST requests are limited to **10 per minute per client IP** using Flask-Limiter and Redis.
- **Five failed password attempts** for the same case-sensitive username trigger Turnstile verification on subsequent attempts during the counter window.
- Failed-login counters expire **15 minutes after the first failed attempt** in that window. The counter is not reset by successful authentication.
- Redis keys identify usernames using keyed HMAC-SHA256 hashes rather than plaintext username values.
- Turnstile tokens are validated **server-side** with Cloudflare. A missing, invalid, or unverifiable required CAPTCHA response blocks login.
- A Redis outage prevents login attempts from proceeding; the app returns a generic server error rather than silently disabling the protections.

## Development and deployment considerations

This project currently uses local Redis at `127.0.0.1:6379` and verifies Turnstile hostnames only for `localhost` and `127.0.0.1`. A deployment requires suitable Redis connection configuration, a production Turnstile hostname allowlist, HTTPS, and a production WSGI server.
