"""Tiny SQLite layer for contact-form messages (stdlib only)."""
import os
import sqlite3
from datetime import datetime, timezone

import click
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL,
    message     TEXT    NOT NULL,
    ip          TEXT,
    user_agent  TEXT,
    created_at  TEXT    NOT NULL
);
"""

# ":memory:" databases vanish when the connection closes, so tests share one.
_memory_conn = None


def _db_path():
    path = current_app.config["DATABASE"]
    if path == ":memory:" or os.path.isabs(path):
        return path
    return os.path.join(current_app.instance_path, path)


def get_db():
    global _memory_conn
    if "db" not in g:
        path = _db_path()
        if path == ":memory:":
            if _memory_conn is None:
                _memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
                _memory_conn.row_factory = sqlite3.Row
                _memory_conn.executescript(SCHEMA)
            g.db = _memory_conn
            g.db_shared = True
        else:
            conn = sqlite3.connect(path, timeout=10)
            conn.row_factory = sqlite3.Row
            g.db = conn
            g.db_shared = False
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    shared = g.pop("db_shared", False)
    if conn is not None and not shared:
        conn.close()


def reset_memory_db():
    """Used by tests to start from an empty in-memory database."""
    global _memory_conn
    if _memory_conn is not None:
        _memory_conn.close()
    _memory_conn = None


def init_db():
    get_db().executescript(SCHEMA)


def save_message(name, email, message, ip, user_agent):
    db = get_db()
    cur = db.execute(
        "INSERT INTO messages (name, email, message, ip, user_agent, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, email, message, ip, (user_agent or "")[:300], datetime.now(timezone.utc).isoformat(timespec="seconds")),
    )
    db.commit()
    return cur.lastrowid


def list_messages(limit=50):
    return get_db().execute(
        "SELECT id, name, email, message, created_at FROM messages ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()


@click.command("init-db")
def init_db_command():
    """Create the messages table."""
    init_db()
    click.echo(f"Database ready at {_db_path()}")


@click.command("messages")
@click.option("--limit", default=20, show_default=True)
def list_messages_command(limit):
    """Print the most recent contact-form messages."""
    rows = list_messages(limit)
    if not rows:
        click.echo("No messages yet.")
        return
    for row in rows:
        click.secho(f"#{row['id']}  {row['created_at']}  {row['name']} <{row['email']}>", bold=True)
        click.echo(f"    {row['message']}\n")


def init_app(app):
    os.makedirs(app.instance_path, exist_ok=True)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(list_messages_command)
    with app.app_context():
        init_db()
