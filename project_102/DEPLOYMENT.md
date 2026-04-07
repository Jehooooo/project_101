# 🚀 Free Deployment Guide
## DMMMSU-SLUC Incident Monitoring System

> **Stack:** React + Vite (Frontend) · Python/Flask (Backend) · MySQL (Database)

---

## 📋 Overview

| Layer | Service | Cost |
|-------|---------|------|
| 🗄️ Database (MySQL) | [Aiven](https://aiven.io) | **FREE** — 5 GB forever |
| ⚙️ Backend (Flask) | [Render.com](https://render.com) | **FREE** — 750 hrs/month |
| 🌐 Frontend (React) | [Vercel](https://vercel.com) | **FREE** — unlimited |

> ⚠️ **Do this in order:** GitHub → Database → Backend → Frontend

---

## STEP 1 — Push Code to GitHub

### 1.1 Create a GitHub Repository

1. Go to [github.com](https://github.com) → Log in
2. Click **"+"** (top right) → **New repository**
3. Name it: `dmmmsu-incident-system`
4. Set to **Public** or **Private** (either works)
5. Click **Create repository**

### 1.2 Push Your Code

Open a terminal in your project folder (`project_102/`) and run:

```bash
git init
git add .
git commit -m "Initial commit - production ready"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dmmmsu-incident-system.git
git push -u origin main
```

> 🔐 **Before pushing**, run `git status` and confirm `backend/.env` is **NOT** listed.
> Your `.gitignore` already excludes it — but always verify.

### ✅ Files That Will Be Pushed

```
project_102/
├── .gitignore
├── README.md
├── backend/
│   ├── app.py
│   ├── Procfile            ← required by Render
│   ├── requirements.txt    ← includes gunicorn
│   ├── schema.sql
│   ├── mysql_setup.py
│   ├── .env.example        ← template only, safe to push
│   ├── models/
│   └── utils/
└── app/
    ├── src/
    ├── public/
    ├── index.html
    ├── package.json
    ├── package-lock.json
    ├── vite.config.ts
    └── (other config files)
```

### ❌ Files That Will NOT Be Pushed (gitignore)

```
backend/.env          ← your real passwords
backend/__pycache__/
backend/instance/
backend/static/uploads/
backend/static/reports/
app/node_modules/
app/dist/
```

---

## STEP 2 — Database on Aiven (Free MySQL)

### 2.1 Create Your Free Database

1. Go to [aiven.io](https://aiven.io) → **Sign Up** (use Google or GitHub)
2. Click **Create Service**
3. Choose **MySQL**
4. Select Plan: **Free**
5. Choose any region (pick one closest to Philippines, e.g., `google-asia-southeast1`)
6. Click **Create Free Service**
7. Wait ~1–2 minutes for it to start

### 2.2 Copy Your Credentials

Once the service is **Running**, click on it and go to the **Overview** tab:

```
Host:     mysql-xxxxxxxx.aivencloud.com
Port:     (shown — save this)
User:     avnadmin
Password: (shown — save this)
```

### 2.3 Create the Database

1. Go to the **Databases** tab inside your Aiven service
2. Click **Create Database**
3. Name it: `campus_incidents_db`
4. Click **Add**

### 2.4 Run Your Schema

Download the **CA Certificate** from the **Connection Information** tab (`ca.pem`).

Then run your schema to create the tables:

```bash
mysql \
  --host=mysql-xxxxxxxx.aivencloud.com \
  --port=YOUR_PORT \
  --user=avnadmin \
  --password=YOUR_PASSWORD \
  --ssl-ca=ca.pem \
  campus_incidents_db < backend/schema.sql
```

> 💡 Alternatively, use **MySQL Workbench**: connect using SSL with the `ca.pem` file, then run `schema.sql`

---

## STEP 3 — Backend on Render.com (Free Flask)

### 3.1 Create a Render Account

1. Go to [render.com](https://render.com) → **Get Started for Free**
2. Sign up with **GitHub** (easiest — gives automatic access to your repo)

### 3.2 Create a Web Service

1. From the Render dashboard, click **New +** → **Web Service**
2. Click **Connect a repository** → select `dmmmsu-incident-system`
3. Fill in the settings:

| Field | Value |
|-------|-------|
| **Name** | `dmmmsu-backend` |
| **Region** | Singapore (closest to PH) |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | **Free** |

### 3.3 Add Environment Variables

Click **Advanced** → **Add Environment Variable** and add ALL of these:

| Key | Value |
|-----|-------|
| `DB_HOST` | `mysql-xxxxxxxx.aivencloud.com` (from Aiven) |
| `DB_PORT` | Your Aiven port number |
| `DB_USER` | `avnadmin` |
| `DB_PASSWORD` | Your Aiven password |
| `DB_NAME` | `campus_incidents_db` |
| `SECRET_KEY` | Any random 32-character string |
| `JWT_SECRET_KEY` | Another random 32-character string |
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | `jehosuebiscarra09@gmail.com` |
| `SMTP_PASSWORD` | `qgup fuuc hycu kimz` |
| `FROM_EMAIL` | `jehosuebiscarra09@gmail.com` |
| `TELEGRAM_BOT_TOKEN` | Your bot token |
| `TELEGRAM_CHAT_ID` | Your real group/personal chat ID |
| `FRONTEND_URL` | `https://dmmmsu-incident-system.vercel.app` *(fill after Step 4)* |

> 💡 To generate a random secret key, run: `python -c "import secrets; print(secrets.token_hex(32))"`

### 3.4 Deploy

1. Click **Create Web Service**
2. Wait ~3–5 minutes for the first build
3. Once deployed, your backend URL is:
   ```
   https://dmmmsu-backend.onrender.com
   ```
4. Test it by visiting: `https://dmmmsu-backend.onrender.com/api/health`
   - You should see: `{"status": "ok"}`

> ⚠️ **Free Tier Warning:** Render's free tier **sleeps after 15 minutes** of no traffic.
> The first request after sleeping takes ~30 seconds to wake up. Fix this in Step 5.

---

## STEP 4 — Frontend on Vercel (Free React/Vite)

### 4.1 Create a Vercel Account

1. Go to [vercel.com](https://vercel.com) → **Sign Up**
2. Sign up with **GitHub**

### 4.2 Connect Your API URL in Code

Before deploying, make sure your frontend points to the live backend.

Find where your frontend calls the API (look in `app/src/services/` or similar).
Make sure the base URL uses an environment variable like:

```ts
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
```

> If it's currently hardcoded to `localhost:5000`, update it to use `import.meta.env.VITE_API_URL`.

### 4.3 Deploy on Vercel

1. From the Vercel dashboard, click **Add New** → **Project**
2. Import your GitHub repo: `dmmmsu-incident-system`
3. Fill in the settings:

| Field | Value |
|-------|-------|
| **Root Directory** | `app` |
| **Framework Preset** | `Vite` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

4. Under **Environment Variables**, add:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://dmmmsu-backend.onrender.com` |

5. Click **Deploy**
6. Wait ~2 minutes.
7. Your live frontend URL:
   ```
   https://dmmmsu-incident-system.vercel.app
   ```

### 4.4 Update CORS on Render

Go back to Render → your `dmmmsu-backend` service → **Environment** tab.
Update (or add) this variable:

| Key | Value |
|-----|-------|
| `FRONTEND_URL` | `https://dmmmsu-incident-system.vercel.app` |

Render will auto-redeploy after you save.

---

## STEP 5 — Keep the Backend Awake (Free)

Render's free tier sleeps after 15 minutes. Set up a free cron job to ping it every 10 minutes.

1. Go to [cron-job.org](https://cron-job.org) → **Sign Up free**
2. Click **CREATE CRONJOB**
3. Fill in:

| Field | Value |
|-------|-------|
| **Title** | `DMMMSU Keep Alive` |
| **URL** | `https://dmmmsu-backend.onrender.com/api/health` |
| **Schedule** | Every **10 minutes** |

4. Click **Create** → Done ✅

---

## ✅ Final Test Checklist

After all steps are done, verify everything works:

- [ ] Visit your Vercel URL — login page loads
- [ ] Log in with `admin@dmmmsu.edu.ph` / `admin123`
- [ ] Dashboard shows the seeded incident (Typhoon Uwan)
- [ ] Create a new incident — email notification arrives
- [ ] Visit `https://dmmmsu-backend.onrender.com/api/health` — returns `{"status":"ok"}`

---

## 🏗️ Final Architecture

```
[User Browser]
     │
     ▼
┌─────────────────────────┐       ┌──────────────────────────────┐
│   Vercel  (FREE)        │─API──▶│   Render.com  (FREE)         │
│   React + Vite + TS     │◀─────│   Python / Flask / gunicorn  │
│   Global CDN            │       │   /api/health  ← ping        │
└─────────────────────────┘       └────────────┬─────────────────┘
                                               │ SSL/TLS
                                               ▼
                                  ┌──────────────────────────────┐
                                  │   Aiven  (FREE)              │
                                  │   MySQL · 5 GB               │
                                  │   campus_incidents_db        │
                                  └──────────────────────────────┘
                                               ▲
                                               │ Every 10 min
                                  ┌──────────────────────────────┐
                                  │   cron-job.org  (FREE)       │
                                  │   Keeps Render awake         │
                                  └──────────────────────────────┘
```

---

## 🆘 Troubleshooting

| Problem | Fix |
|---------|-----|
| Render build fails | Check `requirements.txt` has `gunicorn>=21.2.0` and `Procfile` says `web: gunicorn app:app` |
| CORS error in browser | Make sure `FRONTEND_URL` env var on Render matches your exact Vercel URL |
| Database connection error | Double-check all 5 DB env vars on Render; ensure schema was run on `campus_incidents_db` |
| Login works locally but not in production | Verify `VITE_API_URL` on Vercel points to your Render backend URL |
| First request takes 30s | Normal on free tier. Set up cron-job.org ping to prevent this |
| Vercel build fails | Make sure **Root Directory** is set to `app`, not the project root |
