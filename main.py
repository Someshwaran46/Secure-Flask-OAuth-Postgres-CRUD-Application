"""
main.py  –  One-click entry point
Wires together:  auth.py (Google OAuth)  +  crud.py (PostgreSQL CRUD / SQL editor)
Run with:  python main.py
"""

import os
from flask import Flask, redirect, url_for, session, render_template
from authlib.integrations.flask_client import OAuth

# ── PostgreSQL connection env-vars ───────────────────────────────────────────
# Set these before running, or just edit the defaults below.
os.environ.setdefault("PG_HOST",     "localhost")
os.environ.setdefault("PG_PORT",     "5432")
os.environ.setdefault("PG_DB",       "postgres")       # ← your database name
os.environ.setdefault("PG_USER",     "postgres")       # ← your pg username
os.environ.setdefault("PG_PASSWORD", "")               # ← your pg password

# ── Flask app ────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates")
app.secret_key = "super_secret_key"          # change to a long random string in prod

# ── Google OAuth ─────────────────────────────────────────────────────────────
GOOGLE_CLIENT_ID     = ""
GOOGLE_CLIENT_SECRET = ""

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# ── Register CRUD blueprint ──────────────────────────────────────────────────
from crud import crud_bp          # noqa: E402  (import after app is created)
app.register_blueprint(crud_bp)


# ── Auth routes (kept in main.py to share the same oauth object) ─────────────

@app.route("/")
def home():
    if session.get("user"):
        return redirect("/dashboard")
    return render_template("index.html")


@app.route("/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/authorize")
def authorize():
    token     = google.authorize_access_token()
    user_info = token.get("userinfo")
    session["user"] = {
        "name":    user_info["name"],
        "email":   user_info["email"],
        "picture": user_info["picture"],
    }
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "═" * 55)
    print("  Acme App  –  starting on  http://127.0.0.1:5000")
    print("  PostgreSQL →  {PG_USER}@{PG_HOST}:{PG_PORT}/{PG_DB}".format(
        **{k: os.environ[k] for k in ("PG_USER","PG_HOST","PG_PORT","PG_DB")}
    ))
    print("═" * 55 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=True)