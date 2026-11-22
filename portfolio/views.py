"""Page routes: the portfolio itself plus SEO/ops endpoints."""
from datetime import date

from flask import Blueprint, Response, current_app, render_template, request, send_from_directory

from .content import PROFILE, site_context

bp = Blueprint("main", __name__)


def site_url():
    """Public base URL: SITE_URL if configured, else derived from the request."""
    return current_app.config.get("SITE_URL") or request.url_root.rstrip("/")


@bp.route("/")
def index():
    return render_template("index.html", **site_context(), site_url=site_url())


@bp.route("/resume")
@bp.route("/resume.pdf")
def resume():
    """Stable, shareable résumé URL (served inline so it opens in the browser)."""
    return send_from_directory(
        current_app.static_folder,
        PROFILE["resume_file"],
        mimetype="application/pdf",
        download_name="Sumit_Kanchole_Resume.pdf",
        max_age=3600,
    )


@bp.route("/robots.txt")
def robots():
    body = f"User-agent: *\nAllow: /\nSitemap: {site_url()}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap():
    base = site_url()
    today = date.today().isoformat()
    urls = [(f"{base}/", "1.0"), (f"{base}/resume", "0.6")]
    items = "".join(
        f"<url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>{prio}</priority></url>"
        for loc, prio in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>'
    )
    return Response(xml, mimetype="application/xml")


@bp.route("/healthz")
def healthz():
    return {"status": "ok"}


@bp.app_errorhandler(404)
def not_found(_err):
    if request.path.startswith("/api/"):
        return {"ok": False, "error": "Not found."}, 404
    return render_template("404.html", **site_context(), site_url=site_url()), 404
