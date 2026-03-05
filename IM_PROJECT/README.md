# DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System

A comprehensive web-based system for monitoring and managing disaster/emergency incidents at DMMMSU-San Luis Campus.

## 🌐 Live Demo

**Frontend**: 

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [User Roles](#user-roles)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)

## ✨ Features

### Core Features

- **Role-Based Access Control**: Separate login pages and dashboards for Administrators and Staff
- **Incident Reporting**: Staff can submit incidents with date, time, location, cause, description, and file attachments
- **Automated Workflow**: 
  - Pending → In Progress (Admin) → Solved (Staff)
  - Automatic PDF generation
  - Email and SMS notifications
- **Analytics Dashboard**: 
  - Total incidents counter
  - Weekly frequency bar chart
  - Monthly trends line chart
  - Status breakdown pie chart
- **Search & Filter**: Filter by date range, status, location, and search text
- **PDF Reports**: Download individual incident reports or generate compiled reports
- **User Management**: Admins can create, update, and deactivate staff accounts

### Security Features

- JWT-based authentication
- Password hashing with Werkzeug
- Role-based route protection
- Secure file upload handling

## 👥 User Roles

### Administrator
- Manage staff user accounts
- View all incident reports
- Update incident status to "In Progress"
- Access analytics dashboard
- Generate and download reports (PDF)
- Manage system notifications

### Staff
- Submit new incident reports
- View submitted reports
- Update status to "Solved" once resolved
- Download generated PDF reports

## 🛠️ Technology Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Charts**: Recharts
- **Animations**: Framer Motion
- **State Management**: React Context API
- **Routing**: React Router DOM

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite (configurable to PostgreSQL/MySQL)
- **Authentication**: Flask-JWT-Extended
- **PDF Generation**: ReportLab
- **Email**: SMTP (configurable)
- **CORS**: Flask-CORS

## 📦 Installation

### Prerequisites
- Node.js 18+
- Python 3.9+
- pip

### Frontend Setup

```bash
cd app
npm install
npm run dev
```

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

### Environment Variables

Create a `.env` file in the backend directory:

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

## 🚀 Usage

### Default Login Credentials

**Admin Account:**
- Email: `admin@dmmmsu.edu.ph`
- Password: `admin123`

**Staff Account (create via admin):**
- Email: `staff@dmmmsu.edu.ph`
- Password: `staff123`

### Workflow

1. **Staff submits incident** → Status: Pending
2. **Admin reviews and updates** → Status: In Progress
3. **Staff resolves and marks** → Status: Solved
4. **PDF generated automatically** at each step
5. **Notifications sent** via email/SMS

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/me` | Get current user |

### User Management (Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List all users |
| POST | `/api/users` | Create new user |
| PUT | `/api/users/<id>` | Update user |
| DELETE | `/api/users/<id>` | Delete user |

### Incident Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/incidents` | List incidents (with filters) |
| POST | `/api/incidents` | Create new incident |
| GET | `/api/incidents/<id>` | Get incident details |
| PUT | `/api/incidents/<id>/status` | Update incident status |
| GET | `/api/incidents/<id>/pdf` | Download incident PDF |

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | Get dashboard analytics |
| GET | `/api/reports/full` | Generate full report PDF |

## 📊 Database Schema

### Users Table
- id (Primary Key)
- email (Unique)
- password (Hashed)
- first_name
- last_name
- role (admin/staff)
- phone
- is_active
- created_at
- updated_at

### Incidents Table
- id (Primary Key)
- incident_id (Unique, formatted: DMMMSU-YYYYMMDD-XXXX)
- date
- time
- location
- cause
- description
- supporting_file
- pdf_file
- status (Pending/In Progress/Solved)
- reported_by (Foreign Key to Users)
- created_at
- updated_at

## 🔒 Security Considerations

1. **Password Security**: All passwords are hashed using Werkzeug
2. **JWT Tokens**: Short-lived access tokens (24 hours)
3. **CORS**: Configured for specific origins
4. **File Uploads**: Secure filename handling and type validation
5. **SQL Injection**: Protected via SQLAlchemy ORM

## 📝 License

© 2024 DMMMSU - SOUTH LA UNION CAMPUS. All rights reserved.

## 🤝 Support

For support or inquiries, please contact the DMMMSU-SLUC IT Department.

---

**Developed for**: Don Mariano Marcos Memorial State University - SOUTH LA UNION CAMPUS 
**Purpose**: Disaster and Emergency Incident Monitoring and Management
