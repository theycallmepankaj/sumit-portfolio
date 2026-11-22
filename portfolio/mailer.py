"""Optional SMTP notification when someone submits the contact form."""
import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app


def mail_enabled():
    cfg = current_app.config
    return bool(cfg.get("SMTP_HOST") and cfg.get("MAIL_TO"))


def send_contact_notification(name, email, message):
    """Send a notification email. Returns True on success; never raises."""
    if not mail_enabled():
        return False

    cfg = current_app.config
    msg = EmailMessage()
    msg["Subject"] = f"Portfolio enquiry from {name}"
    msg["From"] = cfg.get("MAIL_FROM") or cfg.get("SMTP_USER") or cfg["MAIL_TO"]
    msg["To"] = cfg["MAIL_TO"]
    msg["Reply-To"] = email
    msg.set_content(f"{message}\n\n— {name}\n{email}\n")

    try:
        context = ssl.create_default_context()
        if cfg.get("SMTP_USE_SSL"):
            server = smtplib.SMTP_SSL(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=10, context=context)
        else:
            server = smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=10)
            server.starttls(context=context)
        with server:
            if cfg.get("SMTP_USER"):
                server.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
            server.send_message(msg)
        return True
    except Exception:  # noqa: BLE001 — a mail outage must never break the form
        current_app.logger.exception("Failed to send contact notification")
        return False
