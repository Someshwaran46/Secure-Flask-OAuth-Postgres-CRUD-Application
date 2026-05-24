# Secure-Flask-OAuth-Postgres-CRUD-Application

A Flask web application implementing Google OAuth 2.0 authentication with PostgreSQL CRUD operations and session management.

## Features
- Google OAuth 2.0 Authentication
- PostgreSQL CRUD Operations
- Flask Session Management
- Secure User Login

---

## Project Structure

```text
project/
│
├── templates/
│   └── index.html
├── crud.py
├── main.py
├── requirements.txt
└── README.md
```

---

## Step 1 — Generate Google OAuth Credentials

Open:

https://console.cloud.google.com/

Navigate to:

```text
APIs & Services → Credentials → Create Credentials → OAuth Client ID
```

Choose:
```text
Application Type → Web Application
```

Add Redirect URI:

```text
http://127.0.0.1:5000/callback
```

Copy:
- Client ID
- Client Secret

Update them directly inside:

```text
project/main.py
```

---

## Step 2 — Clone Repository

```bash
git clone https://github.com/yourusername/Secure-Flask-OAuth-Postgres-CRUD-Application.git

cd Secure-Flask-OAuth-Postgres-CRUD-Application
```

---

## Step 3 — Create Virtual Environment

```bash
python -m venv myenv
```

### macOS/Linux

```bash
source myenv/bin/activate
```

### Windows

```bash
myenv\Scripts\activate
```

---

## Step 4 — Install Requirements

```bash
pip install -r requirements.txt
```

---

## Step 5 — PostgreSQL Setup

```sql
CREATE DATABASE flaskoauth;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150)
);
```

---

## Step 6 — Run Application

```bash
python main.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## File Paths

```text
Main Flask App      → project/main.py
CRUD Operations     → project/crud.py
HTML Template       → project/templates/index.html
Requirements File   → project/requirements.txt
```

---

## Workflow

```text
User → Google Login
        ↓
OAuth Authorization
        ↓
Flask Callback
        ↓
Session Created
        ↓
CRUD Dashboard Access
```

---

## Author

Someshwaran S
