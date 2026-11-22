# Sumit Kanchole — Portfolio

Personal portfolio for an AI Data Annotator & LLM Evaluator, built with **Python + Flask**.
The front end is hand-written HTML/CSS/JS (no build step). The backend renders the pages and
runs a real contact form.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # optional; sensible defaults work without it

PORT=5050 python wsgi.py        # → http://127.0.0.1:5050
```

> macOS uses port 5000 for AirPlay Receiver, so use another port like 5050.

## Editing the content

Every word on the site lives in **`portfolio/content.py`**: profile, experience, skills,
projects, stats and so on. Change it there and refresh the page; you don't need to touch any HTML.
Wrap text in `**double asterisks**` to make it bold.

To replace the résumé, overwrite `portfolio/static/assets/Sumit_Kanchole_Resume.pdf`.
It's served at `/resume`.

## Project layout

```
portfolio/
  __init__.py      app factory, security headers (CSP with nonces), template helpers, `freeze` CLI
  config.py        all settings come from environment variables
  content.py       ← the site's content (single source of truth)
  views.py         /, /resume, /robots.txt, /sitemap.xml, /healthz, 404
  api.py           POST /api/contact  (validation, honeypot, same-origin check, rate limit)
  db.py            SQLite storage + `init-db` / `messages` CLI commands
  mailer.py        optional SMTP email notification
  ratelimit.py     in-memory sliding-window limiter
  templates/       base.html, index.html, partials/ (one file per section), 404.html
  static/          css/, js/, assets/ (résumé PDF), favicon.svg
tests/             pytest suite
wsgi.py            entry point (gunicorn wsgi:app)
```

## Contact form

The form posts JSON to `/api/contact`. The server then:

1. validates the name, email and message (the browser also checks them, so errors show inline),
2. rejects cross-origin posts and silently drops bots that fill the hidden honeypot field,
3. rate-limits each IP (5 per 10 minutes by default),
4. stores the message in SQLite (`instance/messages.sqlite3`),
5. emails it to you if SMTP is configured (see `.env.example`; Gmail needs an App Password).

If the server can't be reached, the form falls back to opening the visitor's email app.

To read messages, run:

```bash
flask --app portfolio messages
```

## Tests

```bash
pytest -q
```

## Deploy

**Render (recommended):** push this folder to GitHub, then in Render choose
*New → Blueprint* and pick the repo. `render.yaml` configures everything. After the first deploy,
add `SITE_URL` (and the SMTP settings if you want email notifications) in the dashboard.

> Render's free disk is temporary, so SQLite messages are lost on each redeploy. Set up SMTP so
> every message also reaches your inbox.

**Any host with a Procfile** (Railway, Heroku, Fly.io): `gunicorn wsgi:app` is already configured.

**Static hosting only** (GitHub Pages / Netlify):

```bash
flask --app portfolio freeze      # writes ./build
```

In the static build, the contact form opens the visitor's email app instead of posting to the API.
