# 📘 DMMMSU-SLUC Disaster/Emergency Incident Reports Management System
### Complete User & System Guide

> **Don Mariano Marcos Memorial State University – South La Union Campus**
> Disaster Monitoring & Incident Management System

---

## 📑 Table of Contents

1. [System Overview](#1-system-overview)
2. [Live URLs & Access](#2-live-urls--access)
3. [Login Credentials](#3-login-credentials)
4. [Admin Guide](#4-admin-guide)
   - [Dashboard](#41-admin-dashboard)
   - [Incident Reports](#42-incident-reports)
   - [User Management](#43-user-management)
   - [Generate Reports](#44-generate-reports)
   - [Settings](#45-settings)
5. [Staff Guide](#5-staff-guide)
   - [Staff Dashboard](#51-staff-dashboard)
   - [Submitting an Incident](#52-submitting-an-incident)
   - [Tracking My Incidents](#53-tracking-my-incidents)
6. [Notification System](#6-notification-system)
7. [System Architecture](#7-system-architecture)
8. [API Reference](#8-api-reference)
9. [Troubleshooting](#9-troubleshooting)
10. [Deployment Info](#10-deployment-info)

---

## 1. System Overview

The **DMMMSU-SLUC Disaster/Emergency Incident Reports Management System** is a web-based platform designed to help campus administrators and staff efficiently report, track, and resolve disaster and emergency incidents within the Don Mariano Marcos Memorial State University – South La Union Campus.

### Key Features

| Feature | Description |
|---------|-------------|
| 🔐 Role-Based Access | Separate Admin and Staff views with secure JWT authentication |
| 📋 Incident Reporting | Staff can submit detailed incident reports with location, cause, and description |
| 📊 Analytics Dashboard | Real-time charts showing incident frequency, status breakdown, and trends |
| 📧 Email Notifications | Automated email alerts sent to relevant staff when incidents are filed |
| 📱 Telegram Alerts | Instant Telegram bot notifications for critical incidents |
| 📄 PDF Report Generation | One-click PDF export of incident reports |
| 👥 User Management | Admin can add, edit, and deactivate staff accounts |
| 🔍 Search & Filter | Filter incidents by status, date range, cause, and location |

---

## 2. Live URLs & Access

| Component | URL |
|-----------|-----|
| 🌐 **Frontend (Web App)** | https://project-101-ashy.vercel.app |
| ⚙️ **Backend API** | https://project-101-1z6q.onrender.com |
| 💓 **Health Check** | https://project-101-1z6q.onrender.com/api/health |
| 💻 **GitHub Repository** | https://github.com/Jehooooo/project_101 |

> **Note:** The backend is hosted on Render's free tier. If the server has been idle for more than 15 minutes, the **first request may take 30–60 seconds** to wake up. This is normal — subsequent requests will be fast.

---

## 3. Login Credentials

### Admin Account

| Field | Value |
|-------|-------|
| **Email** | `admin@dmmmsu.edu.ph` |
| **Password** | `admin123` |
| **Role** | Administrator |
| **Access** | Full system access — dashboard, incidents, user management, settings |

### Staff Account (Default)

| Field | Value |
|-------|-------|
| **Email** | `staff@dmmmsu.edu.ph` |
| **Password** | `staff123` |
| **Role** | Staff |
| **Access** | Submit reports, view own incidents, download PDFs |

> ⚠️ **Security Note:** Change default passwords immediately in a production environment via Settings → Change Password.

---

## 4. Admin Guide

### How to Log In as Admin

1. Open https://project-101-ashy.vercel.app
2. Click **"Admin Login"** (blue button)
3. Enter your **Email** and **Password**
4. Click **"Sign In"**
5. You will be redirected to the **Admin Dashboard**

---

### 4.1 Admin Dashboard

The dashboard gives you a bird's-eye view of all incidents on campus.

**What you can see:**

| Card | Description |
|------|-------------|
| **Total Incidents** | Total number of all filed reports |
| **Pending Review** | Incidents waiting for admin acknowledgment |
| **In Progress** | Incidents currently being handled |
| **Resolved** | Incidents that have been closed/solved |

**Charts included:**
- 📈 **Weekly Incident Frequency** — Bar chart of incidents over the past 7 days
- 🍩 **Status Breakdown** — Donut chart showing the proportion of each status

**Top Buttons:**
- 🔄 **Refresh** — Reload latest data from the server
- 📥 **Generate Report** — Download a PDF summary of all incidents

---

### 4.2 Incident Reports

**Location:** Sidebar → *Incident Reports*

This page shows a table of **all incidents** submitted by all staff members.

#### Viewing Incidents

Each row shows:
- **Incident ID** (e.g., `DMMMSU-20251109-0001`)
- **Date** of incident
- **Cause** (e.g., *Typhoon Uwan – Natural Disaster*)
- **Location** (e.g., *DMMMSU-SLUC, Agoo, La Union*)
- **Status** badge: `Pending` / `In Progress` / `Solved`
- **Reported By**

#### Filtering & Searching

Use the search bar to filter by:
- Keyword (incident ID, cause, location)
- Status dropdown
- Date range picker

#### Updating Incident Status

1. Click on any incident row to open its detail view
2. Use the **Status** dropdown to change: `Pending → In Progress → Solved`
3. Add admin notes/remarks in the **Notes** field
4. Click **Save Changes**

#### Downloading a Single Incident PDF

1. Click on an incident row
2. Click the **⬇ Download PDF** button
3. A formatted PDF report will be saved to your device

---

### 4.3 User Management

**Location:** Sidebar → *User Management*

This section lets you manage all staff accounts.

#### Viewing Users

The table shows:
- Full Name
- Email
- Role (admin/staff)
- Status (Active/Inactive)
- Date Created

#### Adding a New Staff Account

1. Click **"+ Add User"** button
2. Fill in the form:
   - **First Name** and **Last Name**
   - **Email Address** (must be unique)
   - **Phone Number** (optional, used for Telegram alerts)
   - **Telegram Chat ID** (optional, for direct bot messages)
   - **Password** (min 8 characters)
   - **Role:** Select *Staff*
3. Click **"Create User"**
4. The new user can now log in via the Staff Login page

#### Editing a User

1. Click the **✏️ Edit** icon next to the user
2. Update any field
3. Click **Save**

#### Deactivating a User

1. Click the **🚫 Deactivate** toggle next to the user
2. Confirm the action
3. The user will no longer be able to log in

---

### 4.4 Generate Reports

**Available from:** Dashboard → *Generate Report* button OR Incident Reports page

**Report includes:**
- University header (DMMMSU-SLUC logo and name)
- Date range of the report
- Summary statistics (total, pending, in-progress, resolved)
- Full table of all incidents with details
- Formatted for A4 printing

**Steps:**
1. Click **"Generate Report"**
2. (Optional) Set a date range filter first
3. PDF will automatically download to your device

---

### 4.5 Settings

**Location:** Sidebar → *Settings*

| Setting | Description |
|---------|-------------|
| **Change Password** | Update your admin account password |
| **Notification Preferences** | Toggle email/Telegram notifications on or off |
| **Profile Information** | Update your name, email, and contact details |

---

## 5. Staff Guide

### How to Log In as Staff

1. Open https://project-101-ashy.vercel.app
2. Click **"Staff Login"** (green button)
3. Enter your **Email** and **Password** (provided by your admin)
4. Click **"Sign In"**
5. You will be redirected to the **Staff Dashboard**

---

### 5.1 Staff Dashboard

The Staff Dashboard shows a personal summary of your submitted incidents.

| Card | Description |
|------|-------------|
| **My Reports** | Total number of incidents you have filed |
| **Pending** | Your reports waiting for admin review |
| **Resolved** | Your reports that have been closed |

**My Recent Incidents** section shows your latest 5 submitted reports with:
- Incident ID
- Date
- Location
- Cause/description
- Current status badge
- Download PDF button

---

### 5.2 Submitting an Incident

1. From the Staff Dashboard, click **"+ Report Incident"** (top right)
   - OR go to Sidebar → *Incident Reports* → click **"+ New Report"**

2. Fill in the **Incident Report Form**:

| Field | Description | Required |
|-------|-------------|----------|
| **Date of Incident** | When it occurred | ✅ |
| **Time of Incident** | Approximate time | ✅ |
| **Location** | Specific area on campus | ✅ |
| **Type of Incident** | Natural Disaster / Fire / Medical / Other | ✅ |
| **Cause** | Short title (e.g., "Typhoon Uwan – Natural Disaster") | ✅ |
| **Description** | Detailed account of what happened | ✅ |
| **Number of Affected** | Estimated people affected | Optional |
| **Damages** | Description of property/equipment damage | Optional |
| **Actions Taken** | Immediate response steps already done | Optional |
| **Recommendations** | Suggested next steps | Optional |

3. Click **"Submit Report"**
4. You will see a success notification
5. The report is immediately visible to the Admin
6. **Email and Telegram notifications** are automatically sent to the admin team

---

### 5.3 Tracking My Incidents

1. Go to Sidebar → **Incident Reports**
2. The table shows all your submitted reports
3. Click any row to view full details
4. Check the **Status** column to see if admin has reviewed it:
   - 🟡 `Pending` — Not yet reviewed
   - 🔵 `In Progress` — Admin is handling it
   - 🟢 `Solved` — Resolved and closed
5. Click **⬇ Download** to export the report as PDF

---

## 6. Notification System

The system sends automatic notifications when a new incident is reported.

### Email Notifications

- **Trigger:** A new incident is submitted by a staff member
- **Recipients:** All admin accounts on file
- **Content:** Incident ID, cause, location, date, reported by
- **Provider:** Gmail SMTP

### Telegram Notifications

- **Trigger:** A new incident is submitted
- **Recipients:** Configured Telegram chat ID
- **Bot Token:** Configured in backend environment
- **Command to test:** Admin Settings → Test Notification

> 💡 **To set up Telegram for yourself:** Ask the admin for your **Chat ID** and provide it to them. They can add it to your staff profile.

---

## 7. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSER                          │
│  https://project-101-ashy.vercel.app (React + Vite)     │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS API calls
                       ▼
┌─────────────────────────────────────────────────────────┐
│               BACKEND API (Flask + Python)               │
│       https://project-101-1z6q.onrender.com             │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Routes: /api/auth  /api/incidents  /api/users  │    │
│  │          /api/analytics  /api/notifications     │    │
│  └──────────────────┬──────────────────────────────┘    │
└─────────────────────┼───────────────────────────────────┘
                      │ SQLAlchemy ORM
                      ▼
┌─────────────────────────────────────────────────────────┐
│              MySQL DATABASE (Aiven Cloud)                │
│  Database: campus_incidents_db                           │
│  Tables: users, incidents, notifications                 │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Recharts |
| **Backend** | Python 3, Flask, Flask-JWT-Extended, SQLAlchemy |
| **Database** | MySQL (hosted on Aiven) |
| **Frontend Hosting** | Vercel |
| **Backend Hosting** | Render (Free Tier) |
| **Authentication** | JWT (JSON Web Tokens) |
| **Email** | Gmail SMTP |
| **Instant Alerts** | Telegram Bot API |
| **PDF Generation** | ReportLab (server-side) |

---

## 8. API Reference

All API endpoints are prefixed with `/api`.

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/auth/login` | Log in and receive JWT token | ❌ |
| `GET` | `/api/auth/me` | Get current logged-in user info | ✅ |
| `POST` | `/api/auth/logout` | Invalidate session | ✅ |

**Login Request Body:**
```json
{
  "email": "admin@dmmmsu.edu.ph",
  "password": "admin123"
}
```

**Login Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "user_id": 1,
    "email": "admin@dmmmsu.edu.ph",
    "full_name": "System Administrator",
    "role": "admin"
  }
}
```

---

### Incidents

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/incidents` | List all incidents (admin) or own (staff) | ✅ |
| `POST` | `/api/incidents` | Submit a new incident report | ✅ |
| `GET` | `/api/incidents/:id` | Get a single incident by ID | ✅ |
| `PUT` | `/api/incidents/:id` | Update incident (status, notes) | ✅ Admin |
| `DELETE` | `/api/incidents/:id` | Delete an incident | ✅ Admin |
| `GET` | `/api/incidents/:id/pdf` | Download PDF of incident | ✅ |

---

### Users (Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users` | List all users |
| `POST` | `/api/users` | Create a new user |
| `PUT` | `/api/users/:id` | Update a user |
| `DELETE` | `/api/users/:id` | Deactivate a user |

---

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/analytics/dashboard` | Get dashboard stats |
| `GET` | `/api/analytics/weekly` | Incidents per day (last 7 days) |
| `GET` | `/api/analytics/by-status` | Count grouped by status |

---

### Health & Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Backend health check |
| `GET` | `/api/notifications` | Get notifications for current user |
| `POST` | `/api/notifications/test` | Send a test email/Telegram alert |

---

## 9. Troubleshooting

### ❌ Problem: "Network error. Please try again."

**Cause:** The backend server is sleeping (Render free tier).

**Fix:**
1. Wait **30–60 seconds** and try again
2. Or visit https://project-101-1z6q.onrender.com/api/health first to wake up the server
3. Then go back to the app and log in

---

### ❌ Problem: "Login failed! Check your credentials."

**Cause:** Wrong email or password.

**Fix:**
- Admin: `admin@dmmmsu.edu.ph` / `admin123`
- Staff: `staff@dmmmsu.edu.ph` / `staff123`
- Make sure there are no extra spaces when typing

---

### ❌ Problem: Page shows 404 or blank on refresh

**Cause:** Older Vercel deployments may not have the `vercel.json` routing fix.

**Fix:** Hard-refresh the browser with `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac).

---

### ❌ Problem: Email notifications not arriving

**Fix:**
1. Check spam/junk folder
2. Admin can go to Settings → Test Notification to verify email is working
3. Confirm `SMTP_USERNAME` and `SMTP_PASSWORD` are correct in Render environment variables

---

### ❌ Problem: Telegram notifications not sent

**Fix:**
1. Ensure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set in Render env
2. Test via Settings → Test Notification (Telegram)
3. Make sure you have started the bot by sending `/start` to it

---

### ❌ Problem: Backend crashes on Render

**Check:**
1. Go to https://dashboard.render.com
2. Click on `project_101` → **Logs**
3. Look for error messages at the bottom

**Common cause:** Database connection issue. Verify all `DB_*` environment variables are correct in Render → Environment tab.

---

## 10. Deployment Info

### Frontend (Vercel)

| Setting | Value |
|---------|-------|
| **Platform** | Vercel |
| **Repository** | `Jehooooo/project_101` |
| **Root Directory** | `project_102/app` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Live URL** | https://project-101-ashy.vercel.app |
| **Key Env Var** | `VITE_API_URL=https://project-101-1z6q.onrender.com` |

### Backend (Render)

| Setting | Value |
|---------|-------|
| **Platform** | Render Free Tier |
| **Repository** | `Jehooooo/project_101` |
| **Root Directory** | `project_102/backend` |
| **Start Command** | `gunicorn app:app` |
| **Live URL** | https://project-101-1z6q.onrender.com |
| **Sleep Policy** | Sleeps after 15 min of inactivity |

### Backend Environment Variables (Render)

| Variable | Description |
|----------|-------------|
| `DB_HOST` | Aiven MySQL hostname |
| `DB_PORT` | Aiven MySQL port |
| `DB_USER` | Database username |
| `DB_PASSWORD` | Database password |
| `DB_NAME` | `campus_incidents_db` |
| `SECRET_KEY` | Flask secret key |
| `JWT_SECRET_KEY` | JWT signing key |
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | Gmail address |
| `SMTP_PASSWORD` | Gmail App Password |
| `FROM_EMAIL` | Sender email address |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram recipient chat ID |
| `FRONTEND_URL` | `https://project-101-ashy.vercel.app` |

### Keep-Alive Setup (Recommended)

To prevent the Render backend from sleeping, set up a free cron job:

1. Go to https://cron-job.org and sign up free
2. Click **Create Cronjob**
3. URL: `https://project-101-1z6q.onrender.com/api/health`
4. Schedule: **Every 10 minutes**
5. Click **Create**

This pings the server every 10 minutes so it never sleeps.

---

## 📞 Support

For technical issues with the system, contact the development team or check the GitHub repository at:

**https://github.com/Jehooooo/project_101**

---

*© 2026 DMMMSU – South La Union Campus. All rights reserved.*
*System developed for the Don Mariano Marcos Memorial State University – South La Union Campus.*
