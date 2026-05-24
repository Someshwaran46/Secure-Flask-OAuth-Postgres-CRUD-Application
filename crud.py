import os
import json
import psycopg2
import psycopg2.extras
from functools import wraps
from flask import (
    Blueprint, request, jsonify, session, render_template
)

# ── Blueprint ────────────────────────────────────────────────────────────────
crud_bp = Blueprint("crud", __name__)


# ── PostgreSQL connection helper ─────────────────────────────────────────────
def get_db_connection():
    """
    Returns a psycopg2 connection using env-vars (set in main.py or your shell).
    Override any of these env-vars before starting the server:
        PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD
    """
    host     = os.environ.get("PG_HOST",     "localhost")
    port     = int(os.environ.get("PG_PORT", 5432))
    dbname   = os.environ.get("PG_DB",       "Test")
    user     = os.environ.get("PG_USER",     "postgres")
    password = os.environ.get("PG_PASSWORD", "root")

    try:
        return psycopg2.connect(
            host=host, port=port, dbname=dbname,
            user=user, password=password,
            cursor_factory=psycopg2.extras.RealDictCursor,
            connect_timeout=10,
        )
    except psycopg2.OperationalError as e:
        msg = str(e).strip()
        if "no password supplied" in msg or "fe_sendauth" in msg:
            raise RuntimeError(
                f"PostgreSQL requires a password for user '{user}'. "
                "Edit PG_PASSWORD in main.py (line ~17) or run: "
                "export PG_PASSWORD='yourpassword'"
            ) from e
        if "password authentication failed" in msg:
            raise RuntimeError(
                f"Wrong password for PostgreSQL user '{user}'. "
                "Check PG_PASSWORD in main.py."
            ) from e
        if "could not connect to server" in msg or "Connection refused" in msg:
            raise RuntimeError(
                f"Cannot reach PostgreSQL at {host}:{port}. "
                "Is the server running? Check PG_HOST / PG_PORT in main.py."
            ) from e
        raise


# ── Auth guard ───────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error": "Unauthorised – please log in first."}), 401
        return f(*args, **kwargs)
    return decorated


# ── Dashboard page ───────────────────────────────────────────────────────────
@crud_bp.route("/dashboard")
@login_required
def dashboard():
    """Renders the full UI (index.html) with user info injected."""
    user = session["user"]
    return render_template("index.html", user=user)


# ════════════════════════════════════════════════════════════════════════════
#  1.  SCHEMA HELPERS  (sidebar table list & column info)
# ════════════════════════════════════════════════════════════════════════════

@crud_bp.route("/api/tables", methods=["GET"])
@login_required
def list_tables():
    """Return all user-visible tables in the connected database."""
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type   = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = [row["table_name"] for row in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({"tables": tables})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crud_bp.route("/api/tables/<table_name>/columns", methods=["GET"])
@login_required
def list_columns(table_name):
    """Return column names + data types for a given table."""
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name   = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        columns = cur.fetchall()
        cur.close(); conn.close()
        return jsonify({"columns": [dict(c) for c in columns]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════
#  2.  CRUD – READ  (paginated table rows)
# ════════════════════════════════════════════════════════════════════════════

@crud_bp.route("/api/tables/<table_name>/rows", methods=["GET"])
@login_required
def read_rows(table_name):
    """
    GET /api/tables/<table>/rows?page=1&limit=50&search=foo&col=bar
    Returns paginated rows + total count.
    """
    page   = max(1, int(request.args.get("page",  1)))
    limit  = min(200, int(request.args.get("limit", 50)))
    offset = (page - 1) * limit
    search = request.args.get("search", "").strip()
    col    = request.args.get("col", "").strip()       # column to search in

    try:
        conn = get_db_connection()
        cur  = conn.cursor()

        # Build a safe CAST-based search on a specific column if supplied
        where_clause = ""
        params: list = []
        if search and col:
            where_clause = f'WHERE "{col}"::text ILIKE %s'
            params.append(f"%{search}%")

        count_sql = f'SELECT COUNT(*) AS n FROM "{table_name}" {where_clause}'
        cur.execute(count_sql, params)
        total = cur.fetchone()["n"]

        data_sql = (
            f'SELECT * FROM "{table_name}" {where_clause} '
            f'LIMIT %s OFFSET %s'
        )
        cur.execute(data_sql, params + [limit, offset])
        rows = [dict(r) for r in cur.fetchall()]

        cur.close(); conn.close()
        return jsonify({
            "rows":  rows,
            "total": total,
            "page":  page,
            "limit": limit,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════
#  3.  CRUD – CREATE
# ════════════════════════════════════════════════════════════════════════════

@crud_bp.route("/api/tables/<table_name>/rows", methods=["POST"])
@login_required
def create_row(table_name):
    """
    POST /api/tables/<table>/rows
    Body: JSON object  { col1: val1, col2: val2, … }
    Returns the inserted row.
    """
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No data supplied."}), 400

    columns = list(data.keys())
    values  = list(data.values())
    col_sql = ", ".join(f'"{c}"' for c in columns)
    val_sql = ", ".join(["%s"] * len(values))

    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute(
            f'INSERT INTO "{table_name}" ({col_sql}) VALUES ({val_sql}) RETURNING *',
            values,
        )
        inserted = dict(cur.fetchone())
        conn.commit()
        cur.close(); conn.close()
        return jsonify({"inserted": inserted}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════
#  4.  CRUD – UPDATE
# ════════════════════════════════════════════════════════════════════════════

@crud_bp.route("/api/tables/<table_name>/rows/<pk_col>/<pk_val>", methods=["PUT"])
@login_required
def update_row(table_name, pk_col, pk_val):
    """
    PUT /api/tables/<table>/rows/<pk_column>/<pk_value>
    Body: JSON object of columns to update.
    """
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No data supplied."}), 400

    set_clause = ", ".join(f'"{k}" = %s' for k in data.keys())
    values     = list(data.values()) + [pk_val]

    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute(
            f'UPDATE "{table_name}" SET {set_clause} WHERE "{pk_col}" = %s RETURNING *',
            values,
        )
        updated = cur.fetchone()
        conn.commit()
        cur.close(); conn.close()
        if updated is None:
            return jsonify({"error": "Row not found."}), 404
        return jsonify({"updated": dict(updated)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════
#  5.  CRUD – DELETE
# ════════════════════════════════════════════════════════════════════════════

@crud_bp.route("/api/tables/<table_name>/rows/<pk_col>/<pk_val>", methods=["DELETE"])
@login_required
def delete_row(table_name, pk_col, pk_val):
    """
    DELETE /api/tables/<table>/rows/<pk_column>/<pk_value>
    """
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute(
            f'DELETE FROM "{table_name}" WHERE "{pk_col}" = %s RETURNING *',
            (pk_val,),
        )
        deleted = cur.fetchone()
        conn.commit()
        cur.close(); conn.close()
        if deleted is None:
            return jsonify({"error": "Row not found."}), 404
        return jsonify({"deleted": dict(deleted)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════════════════════════
#  6.  MANUAL SQL EDITOR
# ════════════════════════════════════════════════════════════════════════════

@crud_bp.route("/api/sql", methods=["POST"])
@login_required
def run_sql():
    """
    POST /api/sql
    Body: { "query": "SELECT ..." }

    Runs any SQL the user submits and returns:
      - rows + columns  for SELECT / RETURNING queries
      - rowcount        for INSERT / UPDATE / DELETE
      - nothing extra   for DDL
    """
    body  = request.get_json(force=True) or {}
    query = (body.get("query") or "").strip()

    if not query:
        return jsonify({"error": "No query supplied."}), 400

    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute(query)

        result: dict = {}

        if cur.description:                          # SELECT or RETURNING
            rows = cur.fetchall()
            result["columns"] = [d.name for d in cur.description]
            result["rows"]    = [list(r.values()) for r in rows]
            result["rowcount"]= len(rows)
        else:                                        # DML / DDL
            result["rowcount"] = cur.rowcount
            result["message"]  = f"{cur.rowcount} row(s) affected."

        conn.commit()
        cur.close(); conn.close()
        return jsonify(result)

    except psycopg2.Error as e:
        # Roll back so the connection stays usable
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
        return jsonify({"error": e.pgerror or str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
