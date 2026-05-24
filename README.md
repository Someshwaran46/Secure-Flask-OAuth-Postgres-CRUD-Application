# Secure-Flask-OAuth-Postgres-CRUD-Application
A Flask web application implementing Google OAuth 2.0 authentication with PostgreSQL CRUD operations, session management, and secure user login.

## Features : 

- Google OAuth 2.0 Authentication
- PostgreSQL CRUD Operations
- Flask Session Management
- Secure User Login System

---

# Project Structure

```text
project/
│
├── templates/
│   └── index.html
│
├── crud.py
├── main.py
├── requirements.txt
└── README.md
```


---

# Step 1 — Clone Repository

```bash
git clone https://github.com/yourusername/Flask-Google-OAuth-PostgreSQL-CRUD.git
```

Move into project directory:

```bash
cd Flask-Google-OAuth-PostgreSQL-CRUD
```

---

# Step 2 — Create Virtual Environment

```bash
python -m venv myenv
```

Activate virtual environment:

## macOS/Linux

```bash
source myenv/bin/activate
```

## Windows

```bash
myenv\\Scripts\\activate
```

---

# Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Step 4 — PostgreSQL Setup

Create PostgreSQL database:

```sql
CREATE DATABASE flaskoauth;
```

Create table:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150)
);
```

---

# Step 5 — Configure Environment Variables

Create file:

```text
project/.env
```

Add:

```env
SECRET_KEY=supersecretkey

GOOGLE_CLIENT_ID=YOUR_CLIENT_ID

GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET

DATABASE_URL=postgresql://postgres:password@localhost/flaskoauth
```

---

# Step 6 — File Paths

## Main Flask Application

```text
project/main.py
```

## CRUD Operations

```text
project/crud.py
```

## HTML Template

```text
project/templates/index.html
```

## Dependencies

```text
project/requirements.txt
```

---

# Step 7 — Run Application

Run Flask server:

```bash
python main.py
```

---

# Step 8 — Open Browser

Open:

```text
http://127.0.0.1:5000
```

---

# Application Workflow

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

# Author

Someshwaran S
