# 📅 3-Week Project Documentation Log
# DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System

> **Project Duration:** Day 1 – Day 16 (2 Weeks)
> **Developer:** Lead Developer (Jeho)
> **Co-Programmer:** Raymund
> **QA Tester:** Trisha Dacumos
> **Tech Stack:** React 18 + TypeScript (Frontend) | Flask + SQLite (Backend)

---

## ✅ WEEK 1 — Foundation & Architecture Setup (Day 1–8)

---

### 📆 Day 1 — Project Initialization & Planning

**Tasks Completed:**
- Set up the project folder structure (`/app` for frontend, `/backend` for backend)
- Initialized the React + TypeScript project using Vite (`npm create vite@latest`)
- Installed core frontend dependencies: React Router DOM, Tailwind CSS, shadcn/ui, Recharts, Framer Motion
- Created the initial `README.md` with project overview, features list, and tech stack documentation
- Defined the two main user roles: **Administrator** and **Staff**
- Outlined system workflow: Pending → In Progress → Solved

**Fixed:**
- Resolved Vite configuration issue where `@` alias wasn't resolving correctly in `tsconfig.app.json`
- Fixed Tailwind CSS not applying styles due to missing `content` paths in `tailwind.config.js`


---

### 📆 Day 2 — NO TASK FINISH

> ❌ No development activity.
> Personal obligation prevented work today. Will resume on Day 3.


---

### 📆 Day 3 — JWT Authentication & Login Endpoint

**Tasks Completed:**
- Implemented `/api/auth/login` POST endpoint in `backend/app.py`
- Implemented `/api/auth/me` GET endpoint to fetch the currently authenticated user
- Set up Flask-JWT-Extended with `SECRET_KEY` and `JWT_SECRET_KEY` from `.env`
- Added Werkzeug password hashing on user creation and password verification on login
- Wrote protected route wrapper using JWT `@jwt_required()` decorator

**Fixed:**
- Fixed CORS error blocking frontend requests — configured `Flask-CORS` to allow `http://localhost:5173`
- Fixed JWT token not being read from the `Authorization` header correctly — updated header format to `Bearer <token>`

**Notes:**
> Authentication is fully working. Admin and staff login tested manually via Postman.

---

### 📆 Day 4 — Frontend: Login Page & Auth Context

**Tasks Completed:**
- Built `LoginPage.tsx` — single unified login form (to be split later by Raymund per `co_programmer_tasks.txt`)
- Implemented `AuthContext` under `src/contexts/` — manages JWT token, user state, login/logout functions
- Created `ProtectedRoute.tsx` component to block unauthenticated access
- Connected login form to `/api/auth/login` via `src/services/api.ts`
- Stored JWT token in `localStorage` on successful login
- Set up `App.tsx` routing with React Router DOM

**Fixed:**
- Fixed redirect loop on login — `ProtectedRoute` was checking `isAuthenticated` before context loaded; added loading state guard
- Fixed login form not clearing error message on re-submission

**Notes:**
> Login flow is end-to-end working. Token persists across page refreshes.

---

### 📆 Day 5 — Admin Dashboard & Analytics

**Tasks Completed:**
- Built `AdminDashboard.tsx` — main admin interface
- Integrated **Recharts** for 3 chart types:
  - Weekly frequency **Bar Chart**
  - Monthly trends **Line Chart**
  - Status breakdown **Pie Chart**
- Connected charts to `/api/analytics/dashboard` endpoint
- Displayed total incident counter card at the top
- Added animated stat cards using **Framer Motion**

**Fixed:**
- Fixed Recharts `ResponsiveContainer` not resizing properly when sidebar was toggled — wrapped in a `key`-reset div
- Fixed analytics API returning `null` for months with zero incidents — added default value handling on frontend

**Notes:**
> Admin dashboard is functional and visually polished with animations.

---

### 📆 Day 6 — NO PROGRESS

> ❌ No development activity.
> Personal obligation prevented work today. Will resume on Day 7.

---

### 📆 Day 7 — Incident Report Module (Backend)

**Tasks Completed:**
- Built all incident-related API endpoints:
  - `GET /api/incidents` — fetch all incidents with filter support (date range, status, location, search text)
  - `POST /api/incidents` — create new incident
  - `GET /api/incidents/<id>` — fetch incident by ID
  - `PUT /api/incidents/<id>/status` — update incident status
  - `GET /api/incidents/<id>/pdf` — generate and download incident PDF
- Implemented auto-generated `incident_id` using format `DMMMSU-YYYYMMDD-XXXX`
- Set up secure file upload handling for supporting documents

**Fixed:**
- Fixed 500 error on `POST /api/incidents` when `supporting_file` was `None` — added null check before saving file
- Fixed incident filter by date range — date string comparison was case-sensitive; normalized to ISO format

**Notes:**
> All incident API routes tested. Filtering works correctly with multiple combined parameters.

---

### 📆 Day 8 — PDF Generation with ReportLab

**Tasks Completed:**
- Integrated **ReportLab** library for PDF report generation
- Built PDF template for individual incident reports (incident ID, date, time, location, description, status, file attachments reference)
- Implemented `/api/reports/full` endpoint for generating compiled multi-incident PDF reports
- Added PDF auto-generation trigger on each status update
- Set up `backend/static/` folder to store generated PDF files
- Added PDF download link in the incident detail view

**Fixed:**
- Fixed PDF encoding error for special characters in incident descriptions — set encoding to `UTF-8` in ReportLab canvas
- Fixed compiled report crashing when there were zero incidents — added empty state handling

**Notes:**
> PDF feature is fully working. Individual and compiled reports can be downloaded.

---

## ✅ WEEK 2 — Frontend Pages, Staff Module & Notifications (Day 9–16)

---

### 📆 Day 9 — Incident Reports Page (Frontend)

**Tasks Completed:**
- Built `IncidentReports.tsx` — full table view of all incidents
- Implemented **Search & Filter** bar: filter by date range, status, location, and text search
- Implemented status badge styling (Pending = yellow, In Progress = blue, Solved = green)
- Connected incident table to `GET /api/incidents` with query params for filters
- Added loading skeleton and empty state UI

---

### 📆 Day 10 — Incident Form & Staff Submission

**Tasks Completed:**
- Built `IncidentForm.tsx` — form for staff to submit a new incident
- Form fields: Date, Time, Location, Cause, Description, File Attachment (supporting document)
- Added client-side form validation with error messages
- Connected form submission to `POST /api/incidents`
- Added success toast notification and redirect after submission
- Implemented file type and size validation on upload

**Fixed:**
- Fixed form date/time not submitting correct format — converted to ISO 8601 before sending to API
- Fixed file upload field not clearing after successful form submission

**Notes:**
> Staff can successfully submit incident reports with file attachments.

---

### 📆 Day 11 — Staff Dashboard

**Tasks Completed:**
- Built `StaffDashboard.tsx` — dashboard view for logged-in staff
- Displayed a list of incidents submitted by the current staff user only
- Added **status update button** — "Mark as Solved" (only visible when status is "In Progress")
- Connected to `PUT /api/incidents/<id>/status` for status updates
- Integrated PDF download button per incident row
- Added incident count summary cards (Total, Pending, In Progress, Solved)

**Fixed:**
- Fixed staff being able to see other users' incidents — added `reported_by` filter in `GET /api/incidents` based on JWT identity
- Fixed "Mark as Solved" button appearing on already-solved incidents — added conditional rendering based on `status`

**Notes:**
> Staff dashboard is role-isolated and correctly shows only their own submitted reports.

---

### 📆 Day 12 — NO PROGRESS

> ❌ No development activity.
> Unexpected absence. Tasks resumed the following day.

---

### 📆 Day 13 — User Management Module

**Tasks Completed:**
- Built `UserManagement.tsx` — admin page for managing staff accounts
- Features:
  - List all users with name, email, role, and active status
  - Create new staff user (modal form)
  - Edit existing user details
  - Deactivate/reactivate user accounts (soft delete toggle)
- Built user management API endpoints:
  - `GET /api/users`
  - `POST /api/users`
  - `PUT /api/users/<id>`
  - `DELETE /api/users/<id>`
- Added hash password on user creation from admin panel

**Fixed:**
- Fixed admin being able to delete their own account — added guard in `DELETE /api/users/<id>` to reject self-deletion requests
- Fixed user creation not validating duplicate emails — added unique constraint check with meaningful error message

**Notes:**
> User management page is fully functional. Admin can manage all staff accounts.

---

### 📆 Day 14 — Layout, Sidebar & Navigation

**Tasks Completed:**
- Built `Layout.tsx` — master layout wrapper with responsive sidebar
- Sidebar contains: navigation links, user info display, logout button
- Admin sidebar links: Dashboard, Incident Reports, User Management, Settings
- Staff sidebar links: Dashboard, My Reports, Submit Incident
- Added Framer Motion slide-in animation for sidebar on mobile
- Implemented active route highlighting in sidebar

**Fixed:**
- Fixed sidebar collapse not persisting across page navigation — stored collapse state in `localStorage`
- Fixed logout clearing only the token but not the auth context — updated logout to also clear user state and redirect to login

**Notes:**
> Navigation is polished and consistent across all pages. Mobile responsive.

---

### 📆 Day 15 — Email & SMS Notification Setup

**Tasks Completed:**
- Created `backend/utils/` folder and notification utilities
- Implemented SMTP email sender function — triggered on status changes (Pending → In Progress, In Progress → Solved)
- Added configurable SMTP settings via `.env` file
- Implemented notification content templates (incident ID, new status, timestamp)
- Documented all environment variables in `README.md`

**Fixed:**
- Fixed SMTP connection hanging when credentials were incorrect — added `try/except` with timeout and graceful error logging
- Fixed email sending blocking the API response — wrapped send in a background thread so the API response returns immediately

**Notes:**
> Email notifications are non-blocking and fully configurable via `.env`.

---

### 📆 Day 16 — Settings Page

**Tasks Completed:**
- Built `Settings.tsx` — system settings page for admins
- Sections: Account Info (view/edit name, email), Change Password, Notification Preferences
- Change password form validates current password before updating
- Connected to backend profile update endpoint
- Added success/error feedback toasts on save

**Fixed:**
- Fixed password change allowing blank new password — added minimum length validation
- Fixed settings page not loading current user data on mount — added `useEffect` to fetch `/api/auth/me` on page load

**Notes:**
> Settings page is clean and functional. Password security properly enforced.

---

## ✅ WEEK 3 — Refinement, QA, Bug Fixes & Final Delivery (Day 17–24)


---

**Notes:**
> ✅ Project fully completed and delivered. All 3 team roles fulfilled their responsibilities:
> - **Lead Developer (Jeho):** Architecture, backend, frontend, integration
> - **Co-Programmer (Raymund):** Database refactoring, separated login pages
> - **QA Tester (Trisha):** Full manual testing, bug reporting, UX feedback

---

## 📊 Summary Table

| Day | Status | Key Achievement |
|-----|--------|----------------|
| 1 | ✅ Done | Project setup, folder structure, Vite + React initialized |
| 2 | ✅ Done | Flask backend, DB models (Users + Incidents) designed |
| 3 | ✅ Done | JWT authentication, login endpoints working |
| 4 | ✅ Done | LoginPage, AuthContext, ProtectedRoute built |
| 5 | ✅ Done | AdminDashboard with Recharts analytics |
| 6 | ❌ No Progress | Personal obligation |
| 7 | ✅ Done | All Incident API endpoints built + filtering |
| 8 | ✅ Done | PDF generation with ReportLab integrated |
| 9 | ✅ Done | IncidentReports page, hardcoded data removed |
| 10 | ✅ Done | IncidentForm, staff incident submission working |
| 11 | ✅ Done | StaffDashboard, role-isolated incident view |
| 12 | ❌ No Progress | Unexpected absence |
| 13 | ✅ Done | UserManagement module (CRUD for staff accounts) |
| 14 | ✅ Done | Layout, sidebar, navigation finalized |
| 15 | ✅ Done | Email/SMS notifications (SMTP, non-blocking) |
| 16 | ✅ Done | Settings page (profile, change password) |


---

*Documentation prepared by: Lead Developer*
*Date Completed: March 14, 2026*
*© 2026 DMMMSU – South La Union Campus. All rights reserved.*
