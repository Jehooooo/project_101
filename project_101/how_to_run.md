# 🚀 How to Run the Project

**DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System**

This guide walks you through running both the **backend (Flask)** and **frontend (React + Vite)** servers locally.

---

## ✅ Prerequisites

Make sure the following are installed on your machine before proceeding:

| Tool | Minimum Version | Download |
|------|----------------|---------|
| Node.js | 18+ | https://nodejs.org |
| Python | 3.9+ | https://python.org |
| pip | (comes with Python) | — |

---

## 📁 Project Structure

```
project_101/
├── app/          ← Frontend (React + Vite)
└── backend/      ← Backend (Flask + Python)
```

---

## 🖥️ Step 1 — Set Up and Run the Backend

Open a terminal and run the following commands:

```bash
cd backend
```

### Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file inside the `backend/` folder with the following contents:

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///dmmmsu_disaster.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@dmmmsu.edu.ph
```

> **Note:** For local testing, email/SMS settings can be left as placeholders. The app will still run.

### Start the backend server

```bash
python app.py
```

The backend will run at: **http://localhost:5000**

---

## 🌐 Step 2 — Set Up and Run the Frontend

Open a **new/separate terminal** and run:

```bash
cd app
npm install
npm run dev
```

The frontend will run at: **http://localhost:5173**

---

## 🔐 Step 3 — Log In

Once both servers are running, open your browser and go to:

```
http://localhost:5173
```

Use the default credentials to log in:

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@dmmmsu.edu.ph` | `admin123` |
| Staff | `staff@dmmmsu.edu.ph` | `staff123` |

---

## ⚠️ Common Issues & Fixes

| Problem | Possible Fix |
|---------|-------------|
| `ModuleNotFoundError` on backend | Run `pip install -r requirements.txt` again |
| Port 5000 already in use | Change the port in `app.py` or kill the process using that port |
| Frontend can't reach backend | Make sure the backend is running and CORS is configured |
| `npm install` fails | Delete `node_modules/` and `package-lock.json`, then re-run `npm install` |
| Virtual environment not activating | Make sure you're in the `backend/` directory first |

---

## 🔄 Running Order Summary

```
1. Activate Python venv → Install pip deps → python app.py     (Terminal 1)
2. cd app → npm install → npm run dev                          (Terminal 2)
3. Open browser → http://localhost:5173
```

---

> 📌 **Both the backend and frontend must be running at the same time for the system to work properly.**
