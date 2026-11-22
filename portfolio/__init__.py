"""Sumit Kanchole — portfolio (Flask application factory)."""
import os
import re
import secrets
from datetime import date

from dotenv import load_dotenv

load_dotenv()  # must run before Config reads the environment

from flask import Flask, g, url_for  # noqa: E402
from markupsafe import Markup, escape  # noqa: E402
from werkzeug.middleware.proxy_fix import ProxyFix  # noqa: E402

from . import api, db, views  # noqa: E402
from .config import Config  # noqa: E402
from .content import PROFILE  # noqa: E402

_BOLD = re.compile(r"\*\*(.+?)\*\*")


def rich(text):
    """Escape text, then turn **bold** into <strong>. Safe for user-free content."""
    return Markup(_BOLD.sub(r"<strong>\1</strong>", str(escape(text))))


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object or Config)

    if app.config.get("TRUST_PROXY"):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    app.register_blueprint(views.bp)
    app.register_blueprint(api.bp)

    _register_template_helpers(app)
    _register_security_headers(app)
    _register_cli(app)
    return app


def _register_template_helpers(app):
    app.add_template_filter(rich, "rich")

    @app.before_request
    def _make_nonce():
        g.csp_nonce = secrets.token_urlsafe(16)

    @app.context_processor
    def _inject():
        def asset(filename):
            """url_for('static') with an mtime-based cache-busting query string."""
            path = os.path.join(app.static_folder, filename)
            try:
                version = int(os.path.getmtime(path))
            except OSError:
                version = 0
            return url_for("static", filename=filename, v=version)

        return {
            "asset": asset,
            "csp_nonce": lambda: g.get("csp_nonce", ""),
            "now_year": date.today().year,
        }


def _register_security_headers(app):
    @app.after_request
    def _headers(resp):
        nonce = g.get("csp_nonce", "")
        csp = "; ".join(
            [
                "default-src 'self'",
                f"script-src 'self' 'nonce-{nonce}'",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data:",
                "connect-src 'self'",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self' mailto:",
            ]
        )
        resp.headers.setdefault("Content-Security-Policy", csp)
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if app.config.get("ENV_NAME") == "production":
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return resp


def _register_cli(app):
    import shutil

    import click

    @app.cli.command("freeze")
    @click.option("--out", default="build", show_default=True, help="Output directory.")
    def freeze(out):
        """Export a static copy (for GitHub Pages / Netlify). The form falls back to mailto."""
        out = os.path.abspath(out)
        if os.path.exists(out):
            shutil.rmtree(out)
        shutil.copytree(app.static_folder, os.path.join(out, "static"))
        client = app.test_client()
        for route, filename in [("/", "index.html"), ("/robots.txt", "robots.txt"), ("/sitemap.xml", "sitemap.xml")]:
            resp = client.get(route)
            with open(os.path.join(out, filename), "wb") as fh:
                fh.write(resp.data)
        page = open(os.path.join(out, "index.html"), encoding="utf-8").read()
        page = re.sub(r'(href|src)="/static/', r'\1="static/', page)
        page = page.replace('data-endpoint="/api/contact"', 'data-endpoint=""')
        page = re.sub(r'href="/resume(\.pdf)?"', 'href="static/' + PROFILE["resume_file"] + '"', page)
        with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page)
        click.echo(f"Static site written to {out}")
