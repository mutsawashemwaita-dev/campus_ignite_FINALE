# Campus Ignite
Campus Christian Institution Management System
Built with Python 3.12 · Django 4.2 · MySQL · Bootstrap 5

## Folder Structure

```
campus_ignite/
├── backend/        ← Django + Python code
└── frontend/       ← HTML templates + CSS + JS
```

### Step 1 — Install Python 3.12
Download from: https://www.python.org/downloads/release/python-3129/
- Choose Windows installer (64-bit)
- Tick "Add Python to PATH" during install

### Step 2 — Open backend/ in VS Code terminal

### Step 3 — Create virtual environment using Python 3.12
```
py -3.12 -m venv venv
venv\Scripts\activate
```
You should see (venv) at the start of your terminal line.

### Step 4 — Install dependencies
```
pip install -r requirements.txt
```

### Step 5 — Configure environment
```
copy .env.example .env
```
Open .env and fill in your MySQL password.

### Step 6 — Create MySQL database in MySQL Workbench
```sql
CREATE DATABASE campus_ignite_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 7 — Run migrations
```
python manage.py makemigrations
python manage.py migrate
```

### Step 8 — Create admin user
```
python manage.py setup_admin
```
This creates: username=admin / password=1234

### Step 9 — Start the server
```
python manage.py runserver
```
Open browser: http://127.0.0.1:8000
Login: admin / 1234

## Default Login
| Field    | Value |
|----------|-------|
| Username | admin |
| Password | 1234  |
