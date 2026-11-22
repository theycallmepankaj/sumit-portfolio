"""WSGI entry point: `gunicorn wsgi:app` in production, `python wsgi.py` locally."""
import os

from portfolio import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=os.environ.get("APP_ENV", "development") == "development")
