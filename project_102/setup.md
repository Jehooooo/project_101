# DMMMSU-SLUC Incident Monitoring System — Full Setup Guide

This guide walks you through setting up the **entire project** from scratch, including the database, backend server, and frontend application.

---

## 📋 Table of Contents

1. [Prerequisites & Required Software](#1-prerequisites--required-software)
2. [Project Structure Overview](#2-project-structure-overview)
3. [Database Setup](#3-database-setup)
4. [Database Connection (Environment Variables)](#4-database-connection-environment-variables)
5. [Backend Server Setup](#5-backend-server-setup)
6. [Frontend Setup](#6-frontend-setup)
7. [Running the Full Project](#7-running-the-full-project)
8. [Default Credentials](#8-default-credentials)

---

## 1. Prerequisites & Required Software

Make sure the following software is installed on your machine **before** proceeding.

### 🔧 Required Software

| Software | Version | Purpose | Download |
|---|---|---|---|
| **Python** | 3.10 or higher | Backend (Flask) runtime | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18.x or higher | Frontend (React/Vite) runtime | [nodejs.org](https://nodejs.org/) |
| **npm** | 9.x or higher | Frontend package manager (comes with Node.js) | — |
| **XAMPP** | 8.0 or higher | Local MySQL + phpMyAdmin (recommended) | [apachefriends.org](https://www.apachefriends.org/download.html) |
| **MySQL** | 8.0 or higher | Database server *(skip if using XAMPP)* | [mysql.com](https://dev.mysql.com/downloads/mysql/) |
| **Git** | Latest | Version control | [git-scm.com](https://git-scm.com/) |

> **💡 Recommended for beginners:** Use **XAMPP** instead of a standalone MySQL installation. XAMPP bundles MySQL and phpMyAdmin into one easy installer with a graphical control panel — no command-line MySQL setup required.

### ✅ Verify Installations

After installing, verify each tool is working by running these commands in your terminal:

```bash
python --version
# Expected: Python 3.10.x or higher

node --version
# Expected: v18.x.x or higher

npm --version
# Expected: 9.x.x or higher

mysql --version
# Expected: mysql  Ver 8.0.x ...

git --version
# Expected: git version 2.x.x
```

> **⚠️ Windows Users:** Make sure Python is added to your system's **PATH** during installation (check *"Add Python to PATH"* in the installer). If using standalone MySQL, also ensure it is added to PATH.

---

## 2. Project Structure Overview

```
project_102/
├── app/                   # Frontend — React + Vite + TypeScript
│   ├── src/               # Source files
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── vite.config.ts     # Vite configuration
│
├── backend/               # Backend — Flask + SQLAlchemy
│   ├── app.py             # Main Flask application
│   ├── models/            # SQLAlchemy database models
│   ├── utils/             # Utility functions
│   ├── schema.sql         # MySQL database schema
│   ├── mysql_setup.py     # Database setup & seed script
│   ├── requirements.txt   # Python dependencies
│   ├── .env               # Environment variables (you create this)
│   └── .env.example       # Template for .env
│
└── setup.md               # This file
```

---

## 3. Database Setup

You can use **XAMPP** (recommended) or a **standalone MySQL** installation. Choose one of the options below.

---

### Option A — Using XAMPP ✅ Recommended

XAMPP is the easiest way to get MySQL running locally. It includes MySQL and phpMyAdmin out of the box.

#### Step 1 — Download and Install XAMPP

1. Download XAMPP from [apachefriends.org](https://www.apachefriends.org/download.html).
2. Run the installer and make sure **MySQL** (and optionally **phpMyAdmin**) is checked during installation.
3. Install to the default path (e.g., `C:\xampp`).

#### Step 2 — Start MySQL via XAMPP Control Panel

1. Open the **XAMPP Control Panel** (search for it in the Start Menu).
2. Click **Start** next to **MySQL**.
3. The status indicator turns **green** when MySQL is running.

   > **Note:** Do **not** start Apache unless you need it — only MySQL is required for this project.

#### Step 3 — Verify MySQL is Running

Open your browser and go to **http://localhost/phpmyadmin** — if phpMyAdmin loads, MySQL is working.

Alternatively, test via terminal:
```bash
"C:\xampp\mysql\bin\mysql.exe" -u root -p
# Press Enter when asked for a password (XAMPP root has no password by default)
```

> **XAMPP Default Settings:**
> - Host: `127.0.0.1`
> - Port: `3306`
> - User: `root`
> - Password: *(empty — no password by default)*

Update your `.env` accordingly (see Section 4).

---

### Option B — Using Standalone MySQL

1. Install **MySQL 8.0+** from [mysql.com](https://dev.mysql.com/downloads/mysql/).
2. During installation, set a **root password** (remember this — you'll need it later).
3. Make sure the MySQL service is **running**.

   **Windows:** Open *Services* → find `MySQL80` → click *Start*.

   Or via Command Prompt (run as Administrator):
   ```bash
   net start MySQL80
   ```
4. Verify the connection:
   ```bash
   mysql -u root -p
   # Enter your password when prompted
   ```

> **Note:** The backend `.env.example` defaults to port `3307`. Standalone MySQL typically runs on `3306`. Update `DB_PORT` in your `.env` to match (see Section 4).

---

## 4. Database Connection (Environment Variables)

The backend reads database credentials from a `.env` file. You **must** create this file before running the server.

### Step 1 — Create the `.env` File

Navigate to the `backend/` folder and copy the example file:

```bash
# In your terminal, from the project root:
cd backend
copy .env.example .env       # Windows
# cp .env.example .env       # Mac/Linux
```

### Step 2 — Fill in Your Credentials

Open `backend/.env` in a text editor and update the values:

**If using XAMPP** (default settings — no password):
```env
# MySQL Connection
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=campus_incidents_db

# Flask / JWT Secrets (change these in production!)
SECRET_KEY=dmmmsu-sluc-secret-key-2024
JWT_SECRET_KEY=jwt-secret-key-dmmmsu
```

**If using standalone MySQL** (with a password set during install):
```env
# MySQL Connection
DB_HOST=127.0.0.1
DB_PORT=3306          # or 3307 if configured differently
DB_USER=root
DB_PASSWORD=your_mysql_root_password_here
DB_NAME=campus_incidents_db

# Flask / JWT Secrets (change these in production!)
SECRET_KEY=dmmmsu-sluc-secret-key-2024
JWT_SECRET_KEY=jwt-secret-key-dmmmsu
```

> **⚠️ Important:** Replace `your_mysql_root_password_here` with the actual root password you set during MySQL installation. Never commit your `.env` file to Git — it is already listed in `.gitignore`.

### Step 3 — Initialize the Database

With your `.env` configured, run the automated setup script from the `backend/` directory:

```bash
cd backend
python mysql_setup.py
```

This script will:
- ✅ Create the `campus_incidents_db` database (if it doesn't exist)
- ✅ Run `schema.sql` to create all tables (`users`, `incidents`)
- ✅ Seed two default accounts (admin + staff)

Expected output:
```
============================================================
  DMMMSU-SLUC Incident System — MySQL Setup
============================================================
  Host    : 127.0.0.1:3307
  User    : root
  Database: campus_incidents_db
------------------------------------------------------------

[1/3] Creating database (if not exists)…
   ✅ Database `campus_incidents_db` ready.

[2/3] Running schema.sql…
   ✅ Tables created (or already up-to-date).

[3/3] Seeding default users…
   ✅ Created user: admin@dmmmsu.edu.ph (role=admin)
   ✅ Created user: staff@dmmmsu.edu.ph (role=staff)

============================================================
  ✅ Setup complete!
============================================================
```

If you see any `❌` error, double-check your `.env` values and make sure MySQL is running.

---

## 5. Backend Server Setup

### Step 1 — Navigate to the Backend Directory

```bash
cd backend
```

### Step 2 — Create a Python Virtual Environment

It is strongly recommended to use a virtual environment to isolate dependencies.

```bash
# Create virtual environment
python -m venv venv

# Activate it:
# Windows (Command Prompt):
venv\Scripts\activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Mac/Linux:
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt.

### Step 3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:

| Package | Purpose |
|---|---|
| `flask` | Web framework |
| `flask-cors` | Cross-Origin Resource Sharing |
| `flask-jwt-extended` | JWT authentication |
| `flask-sqlalchemy` | ORM for database models |
| `werkzeug` | Password hashing, WSGI utilities |
| `PyMySQL` | MySQL database driver |
| `mysql-connector-python` | MySQL connector (used by setup script) |
| `python-dotenv` | Loads `.env` file |
| `reportlab` | PDF generation |
| `pillow` | Image processing |
| `cryptography` | Encryption support |
| `email-validator` | Email validation |
| `phonenumbers` | Phone number validation |

### Step 4 — Run the Backend Server

Make sure your virtual environment is **activated** and the `.env` file is properly configured, then:

```bash
python app.py
```

The Flask server will start on **http://127.0.0.1:5000** by default.

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

> **Keep this terminal open.** The backend must be running for the frontend to work.

---

## 6. Frontend Setup

Open a **new terminal window/tab** for the frontend (keep the backend running in the other one).

### Step 1 — Navigate to the Frontend Directory

```bash
cd app
```

### Step 2 — Install Node.js Dependencies

```bash
npm install
```

This will install all packages listed in `package.json`, including:

| Package | Purpose |
|---|---|
| `react` + `react-dom` | UI framework |
| `vite` | Build tool & dev server |
| `typescript` | Type-safe JavaScript |
| `react-router-dom` | Client-side routing |
| `tailwindcss` | Utility-first CSS framework |
| `@radix-ui/*` | Accessible UI component primitives |
| `react-hook-form` + `zod` | Form handling & validation |
| `recharts` | Charts and data visualization |
| `framer-motion` | Animations |
| `lucide-react` | Icon library |

> **Note:** Installation may take a few minutes. The `node_modules/` folder will be created — do **not** commit it to Git.

### Step 3 — Run the Frontend Dev Server

```bash
npm run dev
```

The frontend will start on **http://localhost:5173** by default.

```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Open your browser and go to **http://localhost:5173**.

---

## 7. Running the Full Project

To run the complete system, you need **two terminals** open simultaneously:

### Terminal 1 — Backend

```bash
cd backend
venv\Scripts\activate       # Activate virtual environment
python app.py               # Start Flask server → http://127.0.0.1:5000
```

### Terminal 2 — Frontend

```bash
cd app
npm run dev                 # Start Vite dev server → http://localhost:5173
```

Then open **http://localhost:5173** in your browser.

---

## 8. Default Credentials

After running `mysql_setup.py`, the following accounts are seeded into the database:

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@dmmmsu.edu.ph` | `admin123` |
| **Staff** | `staff@dmmmsu.edu.ph` | `staff123` |

> **⚠️ Security Warning:** Change these default passwords **immediately** before deploying to a production or public environment.

---

## 🛠️ Troubleshooting

### ❌ `Cannot connect to MySQL` error
- **XAMPP users:** Open the XAMPP Control Panel and make sure the **MySQL** row shows a green *Running* status.
- **Standalone MySQL users:** Open *Services* and confirm `MySQL80` is started.
- Double-check `DB_HOST`, `DB_PORT`, `DB_USER`, and `DB_PASSWORD` in your `.env` file.
- XAMPP default port is `3306` with an empty password — make sure `DB_PORT=3306` and `DB_PASSWORD=` in `.env`.
- Try connecting manually:
  ```bash
  # XAMPP
  "C:\xampp\mysql\bin\mysql.exe" -u root

  # Standalone MySQL
  mysql -u root -p -P 3306
  ```

### ❌ `ModuleNotFoundError` in the backend
- Make sure your virtual environment is **activated** (`venv\Scripts\activate`).
- Re-run `pip install -r requirements.txt`.

### ❌ `npm install` fails
- Make sure Node.js v18+ is installed: `node --version`.
- Delete `node_modules/` and `package-lock.json`, then re-run `npm install`.

### ❌ Frontend can't reach the backend (API errors)
- Make sure the Flask backend is running on port `5000`.
- Check that CORS is not blocking requests — the backend uses `flask-cors`.
- Confirm the API base URL in the frontend source matches `http://127.0.0.1:5000`.


---

*Last updated: April 2026*
