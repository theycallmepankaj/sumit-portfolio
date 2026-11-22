"""JSON API: the contact form endpoint."""
import re
from urllib.parse import urlparse

from flask import Blueprint, current_app, jsonify, request

from . import db, mailer
from .ratelimit import limiter

bp = Blueprint("api", __name__, url_prefix="/api")

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
LIMITS = {"name": (2, 100), "email": (5, 254), "message": (10, 5000)}


def _clean(value):
    return value.strip() if isinstance(value, str) else ""


def validate_contact(payload):
    """Return (data, errors). ``errors`` maps field -> human-readable message."""
    data = {field: _clean(payload.get(field)) for field in LIMITS}
    errors = {}

    for field, (lo, hi) in LIMITS.items():
        value = data[field]
        if not value:
            errors[field] = "This field is required."
        elif len(value) < lo:
            errors[field] = f"Please enter at least {lo} characters."
        elif len(value) > hi:
            errors[field] = f"Please keep this under {hi} characters."

    if "email" not in errors and not EMAIL_RE.match(data["email"]):
        errors["email"] = "Please enter a valid email address."

    # Strip header-injection characters from single-line fields.
    data["name"] = re.sub(r"[\r\n]+", " ", data["name"])
    return data, errors


def _same_origin():
    """Reject cross-site form posts (lightweight CSRF defence for a JSON API)."""
    origin = request.headers.get("Origin")
    if not origin:
        return True  # non-browser clients / same-origin requests without Origin
    return urlparse(origin).netloc == request.host


def _error(message, status, **extra):
    body = {"ok": False, "error": message}
    body.update(extra)
    return jsonify(body), status


@bp.route("/contact", methods=["POST"])
def contact():
    if not request.is_json:
        return _error("Expected a JSON body.", 415)
    if not _same_origin():
        return _error("Cross-origin requests are not allowed.", 403)

    cfg = current_app.config
    allowed, retry_after = limiter.hit(
        f"contact:{request.remote_addr}", cfg["CONTACT_RATE_LIMIT"], cfg["CONTACT_RATE_WINDOW"]
    )
    if not allowed:
        resp, status = _error("Too many messages. Please try again a little later.", 429)
        resp.headers["Retry-After"] = str(retry_after)
        return resp, status

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error("Invalid JSON body.", 400)

    # Honeypot: real users never see or fill the "company" field. Pretend success.
    if _clean(payload.get("company")):
        return jsonify({"ok": True}), 200

    data, errors = validate_contact(payload)
    if errors:
        return _error("Please fix the highlighted fields.", 400, fields=errors)

    message_id = db.save_message(
        data["name"], data["email"], data["message"], request.remote_addr, request.user_agent.string
    )
    emailed = mailer.send_contact_notification(data["name"], data["email"], data["message"])
    current_app.logger.info("Contact message #%s stored (emailed=%s)", message_id, emailed)

    return jsonify({"ok": True, "id": message_id}), 201
