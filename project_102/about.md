# About the Project

**DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System**

---

## ❓ What is the Project?

The **DMMMSU-SLUC Incident Monitoring System** is a web-based application developed for **Don Mariano Marcos Memorial State University – San Luis Campus (DMMMSU-SLUC)**. It provides a centralized, digital platform for reporting, tracking, and managing disaster and emergency incidents that occur within the campus.

The system replaces manual, paper-based incident reporting with an automated, role-based digital workflow — ensuring that incidents are logged accurately, acted upon quickly, and fully documented from submission to resolution.

The project was built as a full-stack application using:
- **Frontend:** React 18 + TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Backend:** Flask (Python), SQLAlchemy, Flask-JWT-Extended
- **Database:** MySQL (`campus_incidents_db`)

---

## ❓ What Does the System Do?

The system manages the full lifecycle of a campus incident report — from initial submission by staff, through administrative review, to final resolution — with automated tracking and documentation at every step.

### 📋 Core Functions

| Feature | Description |
|---|---|
| **Incident Reporting** | Staff submit incidents with date, time, location, cause, description, and optional file attachments |
| **Automated Workflow** | Incidents follow a structured status pipeline: **Pending → In Progress → Solved** |
| **Analytics Dashboard** | Admins view real-time data: total incident counts, weekly bar charts, monthly trend lines, and status pie charts |
| **Search & Filtering** | Filter incidents by date range, status, location, or keyword search |
| **PDF Report Generation** | Individual incident PDFs and compiled full reports are auto-generated at each workflow step |
| **User Management** | Admins can create, edit, and deactivate staff accounts |
| **Notifications** | Automated email and SMS notifications sent to relevant parties on status changes |
| **Secure Authentication** | JWT-based login with role-based access control and hashed passwords |

### 🔄 Incident Workflow

```
Staff submits incident  →  Status: Pending
        ↓
Admin reviews & acts   →  Status: In Progress
        ↓
Staff resolves issue   →  Status: Solved
        ↓
PDF auto-generated & email/SMS notification sent
```

---

## ❓ Who Uses It?

The system has two defined user roles, each with their own login, dashboard, and set of permissions.

---

### 👤 Staff

Staff members are campus personnel responsible for reporting and resolving incidents.

**What they can do:**
- Log in to the staff portal
- Submit new incident reports (with supporting file attachments)
- View only their own submitted reports
- Mark an incident as **Solved** once it has been resolved
- Download PDF copies of their incident reports

---

### 🛡️ Administrator

Administrators are system managers (e.g., campus safety officers or IT administrators) who oversee all reported incidents and system users.

**What they can do:**
- Log in to the admin portal
- View **all** incident reports from all staff
- Update incident status to **In Progress**
- Access the analytics dashboard (charts, trends, totals)
- Generate and download compiled PDF reports
- Create, edit, and deactivate staff user accounts
- Manage notification preferences and system settings

---

### 👥 Development Team

| Role | Name | Responsibility |
|---|---|---|
| **Lead Developer** | Jeho | Core architecture, backend logic, frontend, system integration |
| **Co-Programmer** | Raymund | Database refactoring, separated login pages, module assistance |
| **QA Tester** | Trisha Dacumos | Manual testing, bug reporting, UX/UI recommendations |

---

*© 2026 DMMMSU – South La Union Campus. All rights reserved.*
