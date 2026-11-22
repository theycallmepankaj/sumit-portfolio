"""Configuration, driven entirely by environment variables (see .env.example)."""
import os


def _bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    ENV_NAME = os.environ.get("APP_ENV", "development")

    # Public URL, used for canonical links, Open Graph and the sitemap.
    SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")

    # Behind Render / Heroku / Nginx, trust one hop of X-Forwarded-* headers.
    TRUST_PROXY = _bool("TRUST_PROXY", False)

    # SQLite file for contact messages. Relative paths resolve inside instance/.
    DATABASE = os.environ.get("DATABASE", "messages.sqlite3")

    # Contact form rate limit: N submissions per window, per client IP.
    CONTACT_RATE_LIMIT = _int("CONTACT_RATE_LIMIT", 5)
    CONTACT_RATE_WINDOW = _int("CONTACT_RATE_WINDOW", 600)

    # Optional email notification for new messages. Leave SMTP_HOST empty to disable.
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = _int("SMTP_PORT", 587)
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_USE_SSL = _bool("SMTP_USE_SSL", False)
    MAIL_FROM = os.environ.get("MAIL_FROM", "")
    MAIL_TO = os.environ.get("MAIL_TO", "")

    # Long-lived caching for static files; URLs are cache-busted by file mtime.
    SEND_FILE_MAX_AGE_DEFAULT = 0 if ENV_NAME == "development" else 31536000

    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 64 * 1024  # contact payloads are tiny


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test"
    DATABASE = ":memory:"
    SMTP_HOST = ""
    CONTACT_RATE_LIMIT = 3
