# 📦 DMMMSU-SLUC Disaster Monitoring System — Module Documentation

> This document provides a full, detailed explanation of every module, class, function, and component in the project. It is organized by layer: **Backend (Python/Flask)** then **Frontend (React/TypeScript)**.

---

## 🗂️ Project Structure Overview

```
project_102/
├── backend/                    # Python Flask REST API
│   ├── app.py                  # Main Flask application & all API routes
│   ├── mysql_setup.py          # One-time database creation & seeding script
│   ├── schema.sql              # Raw SQL table definitions
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variable template
│   ├── models/
│   │   ├── database.py         # SQLAlchemy instance & DB URI builder
│   │   ├── user.py             # User ORM model
│   │   └── incident.py         # Incident ORM model
│   └── utils/
│       ├── notifications.py    # Email & SMS notification helpers
│       └── pdf_generator.py    # PDF report generation helpers
│
└── app/                        # React + TypeScript frontend (Vite)
    └── src/
        ├── main.tsx            # React DOM entry point
        ├── App.tsx             # Root component & router setup
        ├── contexts/
        │   ├── AuthContext.tsx  # Global authentication state
        │   └── ThemeContext.tsx # Global dark/light mode state
        ├── components/
        │   ├── Layout.tsx       # Sidebar + header shell
        │   ├── ProtectedRoute.tsx # Route access guard
        │   └── IncidentForm.tsx  # Reusable incident submission form
        ├── pages/
        │   ├── ChooseLogin.tsx      # Login role selection screen
        │   ├── AdminLogin.tsx       # Admin login page
        │   ├── StaffLogin.tsx       # Staff login page
        │   ├── AdminDashboard.tsx   # Admin analytics dashboard
        │   ├── StaffDashboard.tsx   # Staff overview dashboard
        │   ├── IncidentReports.tsx  # Full incident list & management
        │   ├── UserManagement.tsx   # Admin user CRUD page
        │   └── Settings.tsx         # Profile & preferences settings
        ├── services/
        │   └── api.ts           # Centralized fetch API client
        ├── types/
        │   └── index.ts         # All shared TypeScript interfaces
        └── lib/
            └── utils.ts         # Tailwind utility helper (cn)
```

---

# 🐍 BACKEND — Python / Flask

---

## 📁 `backend/models/`

### `database.py`

**Purpose:** Sets up the shared SQLAlchemy database instance and builds the database connection URI from environment variables.

| Item | Description |
|------|-------------|
| `db` | A global `SQLAlchemy()` instance shared across all models. It is initialized lazily via `db.init_app(app)` in `app.py`. |
| `get_database_uri()` | Reads `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` from the environment to build a MySQL+PyMySQL connection string. If `DATABASE_URL` is set directly (e.g. on a cloud host), it uses that instead. Returns a string like: `mysql+pymysql://root:password@127.0.0.1:3307/campus_incidents_db?charset=utf8mb4`. |
| `init_db()` | Calls `db.create_all()` to create any database tables that do not yet exist. Called inside an `app.app_context()` block at startup in `app.py`. |

---

### `user.py` — Class `User`

**Purpose:** Defines the `users` MySQL table and all user-related behavior via SQLAlchemy ORM.

**Table:** `users`  
**Engine:** InnoDB with `utf8mb4` charset for full Unicode support.

#### Columns

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | `Integer` (PK, auto-increment) | Unique identifier for each user. |
| `email` | `String(120)`, unique, not null | The user's login email address. Must be unique across all users. |
| `password` | `String(255)`, not null | Stored as a **Werkzeug PBKDF2-SHA256 hash** — never plain text. Maps to the `password_hash` column in the database. |
| `first_name` | `String(100)`, not null | User's given name. |
| `last_name` | `String(100)`, not null | User's family name. |
| `role` | `Enum('admin', 'staff')`, not null | Role-based access control enforced at the database level using MySQL ENUM. Defaults to `'staff'`. |
| `phone` | `String(20)`, nullable | Optional phone number for SMS notifications. |
| `is_active` | `Boolean`, not null, default `True` | Allows admins to deactivate accounts without deleting them. |
| `created_at` | `DateTime` | Timestamp of account creation, auto-set to UTC now. |
| `updated_at` | `DateTime` | Timestamp of last modification, auto-updated on every save. |

#### Relationships

| Relationship | Description |
|--------------|-------------|
| `incidents` | One-to-many: a `User` can have many `Incident` records. The backref `reporter` allows `incident.reporter` to return the `User` who filed it. |

#### Methods & Properties

| Method/Property | Description |
|-----------------|-------------|
| `__init__(...)` | Constructor. Accepts all user fields and sets them directly. |
| `full_name` *(property)* | Returns `"{first_name} {last_name}"` as a single string. |
| `is_admin()` | Returns `True` if the user's role is `'admin'`. |
| `is_staff()` | Returns `True` if the user's role is `'staff'`. |
| `__repr__()` | Returns a developer-friendly string like `<User admin@dmmmsu.edu.ph [admin]>`. |
| `to_dict()` | Serializes the user to a safe JSON dictionary. **Deliberately omits the password hash.** Includes: `id`, `email`, `first_name`, `last_name`, `full_name`, `role`, `phone`, `is_active`, `created_at`, `updated_at`. |

---

### `incident.py` — Class `Incident`

**Purpose:** Defines the `incidents` MySQL table and manages the full incident lifecycle — from creation and file storage to status tracking.

**Table:** `incidents`  
**Engine:** InnoDB with `utf8mb4` charset.

#### File Storage Strategy

Each incident supports two parallel storage mechanisms for supporting files:

1. **BLOB in MySQL** (primary): Raw binary bytes stored in `file_data` (LONGBLOB). The `/api/incidents/<id>/file` endpoint streams this directly from the database — no filesystem needed.
2. **Filesystem path** (legacy): The actual file is also saved to `static/uploads/` and its path is stored in `supporting_file`. This is used by the PDF generator which reads files locally.

#### Status Workflow

```
Pending → In Progress (set by Admin) → Solved (set by the Staff who reported it)
```

#### Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | `Integer` (PK, auto-increment) | Internal numeric ID used in API URLs. |
| `incident_id` | `String(30)`, unique | Human-readable ID in the format `DMMMSU-YYYYMMDD-XXXX`, e.g. `DMMMSU-20251109-0001`. Auto-generated. |
| `date` | `Date`, not null | The date the incident actually occurred. |
| `time` | `Time`, not null | The time the incident occurred. |
| `location` | `String(255)`, not null | Where the incident happened. |
| `cause` | `String(255)`, not null | Category or cause of the incident. |
| `description` | `Text`, not null | Full narrative of the incident. |
| `file_data` | `LargeBinary` (LONGBLOB), nullable | Raw binary content of the uploaded supporting file. |
| `file_name` | `String(255)`, nullable | Original filename, used for the `Content-Disposition` download header. |
| `file_mime` | `String(100)`, nullable | MIME type, used for the `Content-Type` download header. |
| `supporting_file` | `String(255)`, nullable | Relative filesystem path (`static/uploads/...`) for backward compatibility. |
| `pdf_file` | `String(255)`, nullable | Path to the auto-generated PDF report (`static/reports/...`). |
| `status` | `Enum('Pending', 'In Progress', 'Solved')` | Current status of the incident, enforced at DB level. |
| `reported_by` | `Integer` (FK → `users.user_id`) | ID of the staff member who submitted the report. |
| `created_at` | `DateTime` | Timestamp of submission. |
| `updated_at` | `DateTime` | Timestamp of last modification. |

#### Methods

| Method | Description |
|--------|-------------|
| `__init__(...)` | Constructor. Accepts all field values and calls `_generate_incident_id()` automatically. |
| `_generate_incident_id()` | Generates a unique ID in the format `DMMMSU-YYYYMMDD-XXXX`. The sequence number (`XXXX`) is determined by counting how many incidents were already created today, then padding to 4 digits. |
| `has_blob()` | Returns `True` if `file_data` is not `None` and has length > 0. Used by the download endpoint to decide whether to serve from BLOB or fall back to the filesystem. |
| `__repr__()` | Returns `<Incident DMMMSU-YYYYMMDD-XXXX [Status]>`. |
| `to_dict()` | Serializes to a JSON-safe dictionary. **Raw BLOB bytes are never exposed.** Instead, it exposes `has_file` (boolean), `file_name`, and `file_mime` as safe metadata. Also includes `reporter_name` from the joined `User` relationship. |

---

## 📁 `backend/utils/`

### `notifications.py`

**Purpose:** Sends automated email and SMS notifications whenever an incident is created or its status is updated.

#### Module-level Configuration

Read from environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_SERVER` | `smtp.gmail.com` | SMTP host server. |
| `SMTP_PORT` | `587` | SMTP port (STARTTLS). |
| `SMTP_USERNAME` | *(empty)* | Email account used to send notifications. |
| `SMTP_PASSWORD` | *(empty)* | Password/App password for the sender account. |
| `FROM_EMAIL` | `noreply@dmmmsu.edu.ph` | The "From" address shown in sent emails. |
| `ADMIN_EMAILS` | `['admin@dmmmsu.edu.ph']` | List of recipients for incident notifications. |
| `SMS_GATEWAYS` | `{globe, smart, tm, tnt}` | Dictionary mapping Philippine carriers to email-to-SMS gateway addresses. |

#### Functions

---

**`send_email_notification(incident, status_update=False)`**

Sends an HTML-formatted email notification.

- If `status_update=False`: Sends a **"New Incident Reported"** email with incident details (ID, location, cause, date, reporter name) to all admin emails.
- If `status_update=True`: Sends a **"Incident Status Update"** email showing the new status with color coding (`#dc2626` for Pending, `#d97706` for In Progress, `#059669` for Solved).
- Skips silently if `SMTP_USERNAME` or `SMTP_PASSWORD` are not configured.
- Uses `smtplib` with STARTTLS for secure delivery.
- Returns `True` on success, `False` on failure.

---

**`send_sms_notification(incident)`**

Currently a **simulation stub** — prints a console message indicating an SMS would be sent. In a production scenario, this would be integrated with a real SMS API (e.g., Semaphore, Vonage) or use the email-to-SMS gateway approach via `SMS_GATEWAYS`. Returns `True`.

---

**`get_status_color(status)`**

A helper that maps a status string to its corresponding hex color code:

| Status | Color |
|--------|-------|
| `Pending` | `#dc2626` (red) |
| `In Progress` | `#d97706` (amber) |
| `Solved` | `#059669` (green) |
| *(default)* | `#6b7280` (gray) |

Used for inline styling in HTML email bodies.

---

**`send_password_reset_email(user, reset_token)`**

Sends an HTML email to a user with a password reset token. Includes:
- A personalized greeting using `user.first_name`.
- A `reset_token` displayed in a `<code>` block.
- A note that the token expires in 1 hour.
- Skips silently if SMTP is not configured.

> ⚠️ Note: The "Reset Password" button link is currently a placeholder (`href="#"`). A real implementation would generate a full URL with the token.

---

### `pdf_generator.py`

**Purpose:** Generates PDF reports using the `reportlab` library. Two types of PDFs are supported.

#### Functions

---

**`generate_incident_pdf(incident, report_folder)`**

Generates a single-incident PDF report.

- **Filename format:** `incident_{incident_id}_{timestamp}.pdf`
- **Saved to:** `static/reports/`
- **Contents:**
  - Header: Institution name, report type, and `Report ID`.
  - **Incident Details** table: Date, time, location, cause, status (color-coded), reporter name, and date reported.
  - **Description** section: Full incident narrative.
  - **Supporting Information** section: Notes whether a supporting file was attached.
  - **Footer:** Auto-generation timestamp and copyright.
- Returns the full file path as a string so `app.py` can store it in `incident.pdf_file`.

---

**`generate_full_report_pdf(incidents, report_folder, date_from=None, date_to=None)`**

Generates a compiled PDF report covering multiple incidents.

- **Filename format:** `full_report_{timestamp}.pdf`
- **Contents:**
  - Report period header (e.g., "All Time" or a date range).
  - **Summary Statistics** table: Total, Pending, In Progress, and Solved counts.
  - **Incident Details** section: Each incident listed with date, time, location, cause, status, reporter, and a truncated description (200 characters max).
  - Footer with generation timestamp.
- Returns the full file path.

---

**`get_status_color(status)`**

Same color mapping as in `notifications.py`, but used for inline PDF text color formatting via ReportLab's `<font color='...'>` tags.

---

## 📄 `backend/app.py`

**Purpose:** The main Flask application. It wires together all extensions, seeds the database, and defines every REST API endpoint.

### Application Bootstrap

| Item | Description |
|------|-------------|
| Flask app init | Creates the Flask app with config for `SECRET_KEY`, `JWT_SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, upload folders, and connection pool settings. |
| `CORS(app)` | Allows cross-origin requests from the React frontend running on a different port. |
| `JWTManager(app)` | Initializes Flask-JWT-Extended for token-based authentication. Tokens expire after **24 hours**. |
| `db.init_app(app)` | Attaches the SQLAlchemy instance to the app. |
| Seed block | On every startup, inside `app.app_context()`: creates tables (`init_db()`), inserts a default admin user, a default staff user, and one seed incident (Typhoon Uwan) if the database is empty. |

### Helper Function

**`require_role(*roles)`**

A role guard used inside route handlers. It decodes the JWT identity, checks if the current user's role is within the allowed `roles` tuple, and returns a `403 JSON error` response if not. Returns `None` if access is granted.

```python
guard = require_role("admin")
if guard:
    return guard  # Blocks non-admins
```

---

### API Route Groups

#### 🔑 Auth Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Validates email + password, returns a JWT `access_token` and the full user object. Returns `401` for invalid credentials, `403` for deactivated accounts. |
| `GET` | `/api/auth/me` | Returns the currently authenticated user's data based on their JWT token. Requires a valid token. |

---

#### 👤 User Management Routes *(Admin Only)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users` | Returns a list of all users. Restricted to `admin`. |
| `POST` | `/api/users` | Creates a new user. Requires `email`, `password`, `first_name`, `last_name`. Role must be `'admin'` or `'staff'`. Hashes the password before saving. |
| `PUT` | `/api/users/<user_id>` | Updates any combination of: `first_name`, `last_name`, `phone`, `role`, `is_active`, `password`. Validates role values. |
| `DELETE` | `/api/users/<user_id>` | Permanently deletes a user record. |

---

#### 🚨 Incident Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/incidents` | Returns a **paginated** list of incidents. Supports query filters: `status`, `location`, `category`, `date_from`, `date_to`, `search`, `page`, `per_page`. **Staff only sees their own incidents.** |
| `GET` | `/api/incidents/<id>` | Returns a single incident. Staff cannot view incidents they did not report. |
| `POST` | `/api/incidents` | Creates a new incident. Accepts `multipart/form-data`. Saves the file to disk AND stores it as a BLOB in MySQL. Auto-generates a PDF and sends email/SMS notifications. |
| `PUT` | `/api/incidents/<id>/status` | Updates an incident's status. **Role-based rules:** Only admin can set `In Progress`; only the reporting staff can set `Solved`. |
| `GET` | `/api/incidents/<id>/file` | Streams the supporting file for download. Serves from BLOB first; falls back to the filesystem path if no BLOB exists. |
| `GET` | `/api/incidents/<id>/pdf` | Downloads the generated PDF for an incident. Re-generates the PDF on the fly if the file no longer exists on disk. |
| `DELETE` | `/api/incidents/<id>` | Deletes an incident and its filesystem files. Admin can delete any; staff can only delete their own. |

---

#### 📊 Analytics & Report Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/analytics/dashboard` | Returns dashboard statistics: total, pending, in-progress, and solved counts; 7-day daily breakdown; 6-month monthly breakdown; and the 5 most recent incidents. Staff sees only their own data. |
| `GET` | `/api/reports/full` | Admin-only. Generates and streams a full compiled PDF report for all incidents. Supports `date_from`, `date_to`, and `status` filters. |

---

#### 🔔 Notifications Route

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/notifications` | Returns a static list of sample notifications. In the current implementation this is hardcoded; a real system would pull from a database table. |

---

#### ⚠️ Error Handlers

| Handler | Description |
|---------|-------------|
| `404` | Returns `{"error": "Resource not found"}` as JSON instead of an HTML page. |
| `500` | Rolls back the active database session to prevent broken transactions, then returns `{"error": "Internal server error"}`. |

---

## 📄 `backend/mysql_setup.py`

**Purpose:** A standalone one-time script to initialize the MySQL database from scratch. Run with `python mysql_setup.py` before starting the Flask server.

### Functions

| Function | Description |
|----------|-------------|
| `get_connection(database=None)` | Returns a raw `mysql.connector` connection. If `database` is given, it connects directly to that database; otherwise it connects without selecting any database (used for the `CREATE DATABASE` step). |
| `run_schema(cursor, sql_file)` | Reads `schema.sql`, splits it by `;`, and executes each statement. Skips `USE` statements since the database is already selected via the connection. |
| `seed_users(cursor, conn)` | Inserts the default admin (`admin@dmmmsu.edu.ph / admin123`) and default staff (`staff@dmmmsu.edu.ph / staff123`) users if they don't already exist. Uses `generate_password_hash()` from Werkzeug so passwords are securely hashed. |
| `main()` | Orchestrates the 3-step setup: **Step 1** — creates the database if it doesn't exist. **Step 2** — runs `schema.sql` to create tables. **Step 3** — seeds default users. Prints a summary with default credentials at the end. |

---

# ⚛️ FRONTEND — React / TypeScript (Vite)

---

## 📄 `app/src/main.tsx`

**Purpose:** The React DOM entry point. Mounts the root `<App />` component into the `#root` div in `index.html`. Imports global styles from `index.css`.

---

## 📄 `app/src/App.tsx`

**Purpose:** The root application component. Sets up the global provider hierarchy and defines all client-side routes using React Router v6.

### Provider Hierarchy

```
<ThemeProvider>     ← manages dark/light mode globally
  <AuthProvider>    ← manages login state globally
    <Router>        ← enables client-side navigation
      <Toaster />   ← global toast notifications (sonner)
      <Routes>      ← all route definitions
```

### Route Structure

| Path | Component | Access |
|------|-----------|--------|
| `/` | `ChooseLogin` | Public |
| `/admin-login` | `AdminLogin` | Public |
| `/staff-login` | `StaffLogin` | Public |
| `/admin/dashboard` | `AdminDashboard` | Admin only |
| `/admin/users` | `UserManagement` | Admin only |
| `/staff/dashboard` | `StaffDashboard` | Staff only |
| `/reports` | `IncidentReports` | Any authenticated user |
| `/settings` | `Settings` | Any authenticated user |
| `*` (fallback) | Redirects to `/` | — |

All protected routes are wrapped in `<ProtectedRoute>`, which checks authentication and role before rendering. All authenticated routes are also wrapped in `<Layout>` for the sidebar and navigation shell.

---

## 📁 `app/src/contexts/`

### `AuthContext.tsx`

**Purpose:** Provides global authentication state across all components.

#### `AuthProvider` Component

Wraps the app and manages:

| State/Value | Description |
|-------------|-------------|
| `user` | The currently logged-in `User` object, or `null` if not authenticated. |
| `isAuthenticated` | `true` if `user` is not null. |
| `isLoading` | `true` while validating a stored token on initial load. |

**On mount (`useEffect`):** Checks `localStorage` for an `access_token`. If one exists, calls `fetchUserData()` to validate it with the backend (`GET /api/auth/me`). Clears the token if the API returns an error.

#### Methods Exposed via Context

| Method | Description |
|--------|-------------|
| `login(credentials)` | Posts to `/api/auth/login`. On success: stores the `access_token` in `localStorage` and sets `user` state. On failure: shows a toast error. Returns `true`/`false`. |
| `logout()` | Removes `access_token` from `localStorage`, clears `user` state, shows a toast. |
| `hasRole(role)` | Returns `true` if the current user's role matches the given string. |

#### `useAuth()` Hook

A convenience hook that returns the `AuthContext` value. Throws an error if used outside `<AuthProvider>`.

---

### `ThemeContext.tsx`

**Purpose:** Provides global dark/light mode state and persistence.

#### `ThemeProvider` Component

| State/Value | Description |
|-------------|-------------|
| `isDarkMode` | Boolean — `true` means dark mode is active. |

**On mount:** Reads `localStorage` for the previously stored `'theme'` value. Defaults to dark mode if no preference is stored.

**On `isDarkMode` change:** Adds or removes the `'dark'` CSS class on `document.documentElement` (used by Tailwind's `dark:` variants), and persists the preference to `localStorage`.

#### Methods Exposed via Context

| Method | Description |
|--------|-------------|
| `toggleTheme()` | Flips `isDarkMode` between `true` and `false`. |

#### `useTheme()` Hook

Returns the `ThemeContext`. Throws an error if used outside `<ThemeProvider>`.

---

## 📁 `app/src/components/`

### `ProtectedRoute.tsx`

**Purpose:** A route guard component that prevents unauthorized access to protected pages.

**How it works:**
1. Reads `isAuthenticated` and `isLoading` from `AuthContext`.
2. If still loading: renders a centered spinner (prevents flash of login page).
3. If not authenticated: redirects to `/` (Choose Login screen).
4. If `allowedRoles` is specified: checks if `user.role` is in the allowed list. If not: redirects to `/` (wrong role).
5. If all checks pass: renders `<Outlet />` (the child route's component).

**Props:**
- `allowedRoles?: string[]` — Optional list of roles allowed to access the route.

---

### `Layout.tsx`

**Purpose:** The persistent application shell that wraps all authenticated pages. Contains the sidebar navigation, top header bar, and the main content area.

**Key features:**
- Collapsible sidebar with navigation links that change depending on the user's role (admin sees different links than staff).
- Mobile-responsive: sidebar becomes an overlay on small screens.
- Top bar includes: page title, notification bell (badge count), dark mode toggle, and a user profile avatar with logout.
- Uses `useAuth()` to display the logged-in user's name and role.
- Uses `useTheme()` to apply and toggle the colour scheme.
- The active route is highlighted in the sidebar using `useLocation()`.

---

### `IncidentForm.tsx`

**Purpose:** A reusable, multi-mode form for creating and viewing incident reports.

**Key features:**
- Supports two input modes toggled by a tab UI:
  1. **Manual Entry:** Fill in date, time, location, cause, and description individually.
  2. **File Upload:** Upload a DOCX form file directly. Fields are auto-filled with defaults.
- Validates required fields before submission.
- On submit: builds a `FormData` object and calls `incidentsApi.create()`.
- On success: shows a success toast and calls the parent's `onSuccess` callback.
- Displays loading states on the submit button.

---

## 📁 `app/src/pages/`

### `ChooseLogin.tsx`

The landing page shown to unauthenticated users. Presents two cards — **Admin** and **Staff** — which navigate to their respective login pages (`/admin-login` and `/staff-login`).

---

### `AdminLogin.tsx`

Admin-specific login form. On submit, calls `authApi.login()`, then navigates to `/admin/dashboard` on success.

---

### `StaffLogin.tsx`

Staff-specific login form. On submit, calls `authApi.login()`, then navigates to `/staff/dashboard` on success.

---

### `AdminDashboard.tsx`

The main analytics dashboard for administrators.

**Features:**
- Fetches data from `/api/analytics/dashboard` via `analyticsApi.getDashboard()`.
- Displays 4 summary stat cards: Total, Pending, In Progress, and Solved incident counts.
- **Bar chart** showing incidents per day for the past 7 days.
- **Line chart** showing incidents per month for the past 6 months.
- **Recent Incidents** table showing the 5 most recent reports with status badges.
- **Full Report** button: triggers `analyticsApi.generateFullReport()` to download a compiled PDF.

---

### `StaffDashboard.tsx`

A simplified dashboard for staff users.

**Features:**
- Shows the staff member's own incident statistics (total, pending, solved).
- Displays a list of their own recent incidents.
- Provides a quick **"Submit New Incident"** button that opens `IncidentForm` in a modal.

---

### `IncidentReports.tsx`

The full incident management table, accessible to both admins and staff (with role-based filtering applied server-side).

**Features:**
- Fetches paginated incident data from `/api/incidents` with filter query parameters.
- **Filter bar:** Status dropdown, date range pickers, category input, and a free-text search box.
- **Incident table:** Columns for ID, date, location, cause, status, reporter, and actions.
- **Actions per row:**
  - **Download PDF** — calls `incidentsApi.downloadPdf()`.
  - **Update Status** — opens a status change modal (role-based transitions enforced).
  - **Delete** — calls `incidentsApi.delete()` with a confirmation prompt.
- **Pagination controls** at the bottom.
- **New Incident** button opens `IncidentForm` in a modal.

---

### `UserManagement.tsx`

Admin-only page for managing system users.

**Features:**
- Lists all users via `usersApi.getAll()`.
- **Create User** modal with fields: email, password, first name, last name, role, phone.
- **Edit User** modal: update name, phone, role, active status, and optionally reset password.
- **Delete User** with a confirmation dialog.
- Active/inactive badge indicator per user.

---

### `Settings.tsx`

Account and preference settings page.

**Features:**
- **Profile section:** Edit first name, last name, and phone. Saves via `usersApi.update()`.
- **Change Password** section: Requires current password, new password, and confirmation.
- **Theme toggle:** Switch between dark and light mode (calls `toggleTheme()` from `ThemeContext`).
- **Notification preferences** (UI only — no backend persistence in the current version).

---

## 📁 `app/src/services/`

### `api.ts`

**Purpose:** A centralized HTTP client that wraps all `fetch()` calls to the backend API. All components use these functions instead of calling `fetch()` directly, keeping network logic in one place.

#### Internal Helpers

| Helper | Description |
|--------|-------------|
| `getAuthHeaders()` | Reads the `access_token` from `localStorage` and returns `{ Authorization: 'Bearer <token>' }`. Applied to every authenticated request. |
| `handleResponse(response)` | Checks if the response is OK. If not, parses the JSON error body and throws an `Error`. If OK, returns the parsed JSON. |

#### Exported API Objects

---

**`authApi`**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `login(email, password)` | `POST /api/auth/login` | Sends credentials, returns token and user. |
| `getCurrentUser()` | `GET /api/auth/me` | Returns the current authenticated user. |

---

**`usersApi`**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `getAll()` | `GET /api/users` | Returns all users (admin only). |
| `create(userData)` | `POST /api/users` | Creates a new user. |
| `update(id, userData)` | `PUT /api/users/<id>` | Updates an existing user. |
| `delete(id)` | `DELETE /api/users/<id>` | Deletes a user. |

---

**`incidentsApi`**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `getAll(filters?)` | `GET /api/incidents` | Fetches paginated incidents with optional filters. Builds query string from filter object. |
| `getById(id)` | `GET /api/incidents/<id>` | Fetches a single incident. |
| `create(formData)` | `POST /api/incidents` | Submits a new incident (multipart/form-data). |
| `updateStatus(id, status)` | `PUT /api/incidents/<id>/status` | Updates an incident's status. |
| `downloadPdf(id)` | `GET /api/incidents/<id>/pdf` | Downloads the PDF, creates a temporary blob URL, and programmatically clicks an anchor tag to trigger the browser download dialog. |
| `delete(id)` | `DELETE /api/incidents/<id>` | Deletes an incident. |

---

**`analyticsApi`**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `getDashboard()` | `GET /api/analytics/dashboard` | Fetches dashboard stats, chart data, and recent incidents. |
| `generateFullReport(filters?)` | `GET /api/reports/full` | Downloads a compiled report PDF using the same blob/anchor technique as `downloadPdf()`. |

---

**`notificationsApi`**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `getAll()` | `GET /api/notifications` | Returns the current list of notifications. |

---

## 📁 `app/src/types/`

### `index.ts`

**Purpose:** Central repository of all TypeScript type definitions. Ensures type safety and consistency between the API responses and the React components.

| Interface | Description |
|-----------|-------------|
| `User` | Represents a system user with `id`, `email`, `first_name`, `last_name`, `full_name`, `role`, `phone`, `is_active`, and timestamps. |
| `LoginCredentials` | Shape of the login form: `{ email, password }`. |
| `AuthResponse` | Shape of the login API response: `{ access_token, user }`. |
| `Incident` | Full incident record matching the backend `to_dict()` output. |
| `IncidentFormData` | Shape of the incident submission form inputs. |
| `IncidentFilters` | Shape of the filter bar state: status, location, category, date range, search string. |
| `DashboardAnalytics` | Shape of the `/api/analytics/dashboard` response. |
| `WeeklyDataPoint` | `{ day, date, count }` — one data point in the 7-day chart. |
| `MonthlyDataPoint` | `{ month, count }` — one data point in the 6-month chart. |
| `Notification` | `{ id, title, message, type, created_at, read }`. |
| `ApiResponse<T>` | Generic wrapper: `{ data?, error?, message? }`. |
| `PaginatedResponse<T>` | Generic paginated response: `{ items, total, pages, current_page, per_page }`. |
| `ChartData` | Chart.js compatible data structure with `labels` and `datasets`. |

---

## 📁 `app/src/lib/`

### `utils.ts`

**Purpose:** Exports a single `cn()` utility function that merges Tailwind CSS class names conditionally. It combines `clsx` (conditional logic) and `tailwind-merge` (deduplication of conflicting Tailwind classes) to produce clean, correct class strings.

```typescript
// Example usage:
cn("px-4 py-2", isActive && "bg-blue-500", "px-6")
// → "py-2 bg-blue-500 px-6"  (px-4 overridden by px-6)
```

---

## 📁 `app/src/hooks/`

### `use-mobile.ts`

**Purpose:** A custom React hook that returns `true` if the current viewport width is less than `768px` (mobile breakpoint).

- Uses a `window.matchMedia()` listener to reactively update when the user resizes the window.
- Used by `Layout.tsx` to decide whether to render the sidebar as a persistent panel or a mobile overlay.

---

### `useAuth.ts`

A re-export or alias of the `useAuth` hook defined in `AuthContext.tsx`, kept in the `hooks/` folder for organizational consistency.

---

*This documentation was generated on **April 6, 2026** and reflects the current state of the codebase.*
