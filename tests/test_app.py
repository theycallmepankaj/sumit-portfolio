import pytest

from portfolio import create_app, db
from portfolio.config import TestConfig
from portfolio.content import EXPERIENCE, PROFILE, PROJECTS
from portfolio.ratelimit import limiter

VALID = {"name": "Asha Recruiter", "email": "asha@example.com", "message": "We'd love to chat about an LLM evaluation role."}


@pytest.fixture()
def app():
    db.reset_memory_db()
    limiter.reset()
    app = create_app(TestConfig)
    yield app
    db.reset_memory_db()


@pytest.fixture()
def client(app):
    return app.test_client()


def post_contact(client, payload, **headers):
    return client.post("/api/contact", json=payload, headers=headers)


# ---------- Pages ----------

def test_home_renders_all_sections(client):
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert PROFILE["name"] in html
    for section in ("about", "experience", "skills", "work", "contact"):
        assert f'id="{section}"' in html
    for job in EXPERIENCE:
        assert job["company"] in html
    assert PROJECTS[0]["url"] in html


def test_rich_filter_escapes_then_bolds(client):
    html = client.get("/").get_data(as_text=True)
    assert "<strong>15+ annotation &amp; evaluation projects</strong>" in html
    assert "**" not in html


def test_resume_serves_pdf(client):
    resp = client.get("/resume")
    assert resp.status_code == 200
    assert resp.mimetype == "application/pdf"
    assert resp.data[:4] == b"%PDF"


def test_seo_endpoints(client):
    assert "Sitemap:" in client.get("/robots.txt").get_data(as_text=True)
    sm = client.get("/sitemap.xml")
    assert sm.mimetype == "application/xml" and "<urlset" in sm.get_data(as_text=True)
    assert client.get("/healthz").get_json() == {"status": "ok"}


def test_404_page_and_api_404(client):
    page = client.get("/nope")
    assert page.status_code == 404 and "pass QA" in page.get_data(as_text=True)
    api = client.get("/api/nope")
    assert api.status_code == 404 and api.get_json()["ok"] is False


def test_security_headers_and_csp_nonce(client):
    resp = client.get("/")
    csp = resp.headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in csp
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    nonce = csp.split("'nonce-")[1].split("'")[0]
    assert f'nonce="{nonce}"' in resp.get_data(as_text=True)


def test_static_assets_are_cache_busted(client):
    html = client.get("/").get_data(as_text=True)
    assert "/static/css/styles.css?v=" in html
    assert "/static/js/main.js?v=" in html


# ---------- Contact API ----------

def test_contact_success_is_stored(client, app):
    resp = post_contact(client, VALID)
    assert resp.status_code == 201
    assert resp.get_json()["ok"] is True
    with app.app_context():
        rows = db.list_messages()
    assert len(rows) == 1 and rows[0]["email"] == VALID["email"]


@pytest.mark.parametrize(
    "field,value",
    [("name", ""), ("name", "A"), ("email", "not-an-email"), ("message", "too short"), ("message", "x" * 5001)],
)
def test_contact_validation_errors(client, field, value):
    resp = post_contact(client, {**VALID, field: value})
    assert resp.status_code == 400
    assert field in resp.get_json()["fields"]


def test_contact_honeypot_pretends_success_but_stores_nothing(client, app):
    resp = post_contact(client, {**VALID, "company": "Spam Inc"})
    assert resp.status_code == 200
    with app.app_context():
        assert db.list_messages() == []


def test_contact_requires_json(client):
    resp = client.post("/api/contact", data=VALID)
    assert resp.status_code == 415


def test_contact_rejects_cross_origin(client):
    resp = post_contact(client, VALID, Origin="https://evil.example")
    assert resp.status_code == 403


def test_contact_allows_same_origin(client):
    resp = post_contact(client, VALID, Origin="http://localhost")
    assert resp.status_code == 201


def test_contact_rate_limited(client):
    for _ in range(TestConfig.CONTACT_RATE_LIMIT):
        assert post_contact(client, VALID).status_code == 201
    resp = post_contact(client, VALID)
    assert resp.status_code == 429
    assert int(resp.headers["Retry-After"]) > 0


def test_contact_strips_newlines_from_name(client, app):
    post_contact(client, {**VALID, "name": "Eve\r\nBcc: x@y.z"})
    with app.app_context():
        assert "\n" not in db.list_messages()[0]["name"]


# ---------- Static export ----------

def test_freeze_writes_portable_static_site(app, tmp_path):
    out = tmp_path / "build"
    result = app.test_cli_runner().invoke(args=["freeze", "--out", str(out)])
    assert result.exit_code == 0, result.output
    html = (out / "index.html").read_text(encoding="utf-8")
    assert 'href="/static/' not in html and 'src="/static/' not in html
    assert 'data-endpoint=""' in html
    assert 'href="static/assets/Sumit_Kanchole_Resume.pdf"' in html
    assert (out / "static" / "assets" / "Sumit_Kanchole_Resume.pdf").exists()


def test_every_rendered_icon_has_svg(client):
    """Guards against an icon name missing from partials/icons.html (renders as an empty slot)."""
    import re
    html = client.get("/").get_data(as_text=True)
    steps = re.findall(r'<span class="step-icon">(.*?)</span>', html, flags=re.S)
    assert steps and all("<svg" in s for s in steps)
    ctas = re.findall(r'<span class="cta-icon">(.*?)</span>', html, flags=re.S)
    assert ctas and all("<svg" in c for c in ctas)
