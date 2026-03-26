"""
DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System
Backend API - Flask Application (MySQL edition)
"""

import io
import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Load .env before anything else so env vars are available
load_dotenv()

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models.database import db, init_db, get_database_uri
from models.user import User
from models.incident import Incident
from utils.pdf_generator import generate_incident_pdf, generate_full_report_pdf
from utils.notifications import send_email_notification, send_sms_notification

# ======================================================================
# Flask app configuration
# ======================================================================

app = Flask(__name__)
app.config["SECRET_KEY"]                  = os.environ.get("SECRET_KEY", "dmmmsu-sluc-secret-key-2024")
app.config["JWT_SECRET_KEY"]              = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-dmmmsu")
app.config["JWT_ACCESS_TOKEN_EXPIRES"]    = timedelta(hours=24)
app.config["SQLALCHEMY_DATABASE_URI"]     = get_database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"]              = "static/uploads"
app.config["REPORT_FOLDER"]              = "static/reports"
# MySQL: raise max allowed packet to 64 MB for LONGBLOB uploads
app.config["SQLALCHEMY_ENGINE_OPTIONS"]  = {
    "pool_pre_ping": True,
    "pool_recycle":  3600,
}

# Ensure static directories exist (legacy PDF support)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["REPORT_FOLDER"], exist_ok=True)

# ======================================================================
# Extension initialisation
# ======================================================================

CORS(app)
JWTManager(app)
db.init_app(app)

# ======================================================================
# Database initialisation & seed data
# ======================================================================

with app.app_context():
    init_db()

    # ── Default admin ──────────────────────────────────────────────────
    if not User.query.filter_by(email="admin@dmmmsu.edu.ph").first():
        db.session.add(User(
            email="admin@dmmmsu.edu.ph",
            password=generate_password_hash("admin123"),
            first_name="System",
            last_name="Administrator",
            role="admin",
            is_active=True,
        ))
        db.session.commit()
        print("Default admin created: admin@dmmmsu.edu.ph / admin123")

    # ── Default staff ──────────────────────────────────────────────────
    staff = User.query.filter_by(email="staff@dmmmsu.edu.ph").first()
    if not staff:
        staff = User(
            email="staff@dmmmsu.edu.ph",
            password=generate_password_hash("staff123"),
            first_name="Salvador P.",
            last_name="Llavorre",
            role="staff",
            phone="09171534850",
            is_active=True,
        )
        db.session.add(staff)
        db.session.commit()
        print("Default staff created: staff@dmmmsu.edu.ph / staff123")

    # ── Seed existing incident ─────────────────────────────────────────
    if Incident.query.count() == 0:
        seed_incident = Incident(
            date=datetime.strptime("2025-11-09", "%Y-%m-%d").date(),
            time=datetime.strptime("21:00", "%H:%M").time(),
            location="DMMMSU-SLUC, Agoo, La Union",
            cause="Typhoon Uwan - Natural Disaster",
            description=(
                "As Typhoon Uwan approached Northern Luzon, the province of La Union activated its "
                "Incident Command System under the Provincial Disaster Risk Reduction and Management "
                "Office. Local governments began preemptive evacuations, moving over a thousand "
                "residents from low-lying and high-risk areas in towns such as San Fernando, Bangar, "
                "Bauang, Agoo, and Pugo. Emergency teams including rescue units, ambulances, and "
                "watercraft were pre-positioned. Within the DMMMSU community, classes were suspended "
                "and facilities were secured as strong winds and heavy rains were expected to intensify.\n\n"
                "After the storm passed, La Union reported extensive damage affecting tens of thousands "
                "of families across the province. Agricultural lands suffered major losses, and several "
                "schools, river walls, markets, and residential structures were either partially or "
                "severely damaged. Power outages also lasted for days, disrupting communication and "
                "campus operations, including those of DMMMSU. Although the university community "
                "remained safe due to early preparations, the aftermath highlighted the importance of "
                "disaster readiness and strengthened coordination among students, faculty, and local "
                "authorities in responding to extreme weather events.\n\n"
                "INCIDENT CAUSES:\n"
                "The incident was primarily caused by Typhoon Uwan's intense rainfall, strong winds, "
                "and wide storm circulation, which brought severe weather conditions across La Union.\n\n"
                "FOLLOW UP RECOMMENDATIONS:\n"
                "1. Strengthen Disaster Preparedness Plans\n"
                "2. Improve Infrastructure Resilience\n"
                "3. Enhance Early Warning and Information Dissemination\n"
                "4. Pre-position Emergency Supplies\n"
                "5. Strengthen Coordination With Local Agencies\n"
                "6. Conduct Environmental and Risk Assessments"
            ),
            supporting_file="static/uploads/20260309_224050_DMMMSU-SLUC_Incident_Form.docx",
            status="Solved",
            reported_by=staff.user_id,
        )
        seed_incident.incident_id = "DMMMSU-20251109-0001"
        db.session.add(seed_incident)
        db.session.commit()
        print("Existing incident seeded: DMMMSU-20251109-0001 - Typhoon Uwan")


# ======================================================================
# Helper: role guard (decorator-style check used in views)
# ======================================================================

def require_role(*roles):
    """Return 403 JSON if the current JWT user's role is not in *roles*."""
    current = json.loads(get_jwt_identity())
    if current.get("role") not in roles:
        return jsonify({"error": "Unauthorized access"}), 403
    return None  # allowed


# ======================================================================
# AUTH ROUTES
# ======================================================================

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    data     = request.get_json()
    email    = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403

    access_token = create_access_token(
        identity=json.dumps({
            "id":    user.user_id,
            "email": user.email,
            "role":  user.role,
        })
    )

    return jsonify({
        "access_token": access_token,
        "user":         user.to_dict(),
    }), 200


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get currently authenticated user."""
    user_id = json.loads(get_jwt_identity())["id"]
    user    = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


# ======================================================================
# USER MANAGEMENT ROUTES  (admin only)
# ======================================================================

@app.route("/api/users", methods=["GET"])
@jwt_required()
def get_users():
    guard = require_role("admin")
    if guard:
        return guard
    users = User.query.all()
    return jsonify({"users": [u.to_dict() for u in users]}), 200


@app.route("/api/users", methods=["POST"])
@jwt_required()
def create_user():
    guard = require_role("admin")
    if guard:
        return guard

    data = request.get_json()
    for field in ("email", "password", "first_name", "last_name"):
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    # Validate role value
    role = data.get("role", "staff")
    if role not in ("admin", "staff"):
        return jsonify({"error": "role must be 'admin' or 'staff'"}), 400

    new_user = User(
        email=data["email"],
        password=generate_password_hash(data["password"]),
        first_name=data["first_name"],
        last_name=data["last_name"],
        role=role,
        phone=data.get("phone"),
        is_active=data.get("is_active", True),
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully", "user": new_user.to_dict()}), 201


@app.route("/api/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    guard = require_role("admin")
    if guard:
        return guard

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if "first_name" in data:
        user.first_name = data["first_name"]
    if "last_name" in data:
        user.last_name = data["last_name"]
    if "phone" in data:
        user.phone = data["phone"]
    if "role" in data:
        if data["role"] not in ("admin", "staff"):
            return jsonify({"error": "role must be 'admin' or 'staff'"}), 400
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = data["is_active"]
    if data.get("password"):
        user.password = generate_password_hash(data["password"])

    db.session.commit()
    return jsonify({"message": "User updated successfully", "user": user.to_dict()}), 200


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    guard = require_role("admin")
    if guard:
        return guard

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200


# ======================================================================
# INCIDENT ROUTES
# ======================================================================

@app.route("/api/incidents", methods=["GET"])
@jwt_required()
def get_incidents():
    current_user = json.loads(get_jwt_identity())

    status    = request.args.get("status")
    location  = request.args.get("location")
    category  = request.args.get("category")
    date_from = request.args.get("date_from")
    date_to   = request.args.get("date_to")
    search    = request.args.get("search")
    page      = request.args.get("page", 1, type=int)
    per_page  = request.args.get("per_page", 10, type=int)

    query = Incident.query

    if status:
        query = query.filter(Incident.status == status)
    if location:
        query = query.filter(Incident.location.ilike(f"%{location}%"))
    if category:
        query = query.filter(Incident.cause.ilike(f"%{category}%"))
    if date_from:
        query = query.filter(Incident.date >= date_from)
    if date_to:
        query = query.filter(Incident.date <= date_to)
    if search:
        query = query.filter(
            db.or_(
                Incident.location.ilike(f"%{search}%"),
                Incident.cause.ilike(f"%{search}%"),
                Incident.description.ilike(f"%{search}%"),
            )
        )

    # Staff can only see their own incidents
    if current_user["role"] == "staff":
        query = query.filter(Incident.reported_by == current_user["id"])

    query      = query.order_by(Incident.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "incidents":    [i.to_dict() for i in pagination.items],
        "total":        pagination.total,
        "pages":        pagination.pages,
        "current_page": page,
        "per_page":     per_page,
    }), 200


@app.route("/api/incidents/<int:incident_id>", methods=["GET"])
@jwt_required()
def get_incident(incident_id):
    current_user = json.loads(get_jwt_identity())
    incident     = Incident.query.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404
    if current_user["role"] == "staff" and incident.reported_by != current_user["id"]:
        return jsonify({"error": "Unauthorized access"}), 403
    return jsonify({"incident": incident.to_dict()}), 200


@app.route("/api/incidents", methods=["POST"])
@jwt_required()
def create_incident():
    """Create a new incident report.

    Uploaded supporting files are:
      1. Saved to disk (static/uploads/) for legacy PDF generation.
      2. Read as bytes and stored as LONGBLOB in the incidents table.
    """
    current_user = json.loads(get_jwt_identity())

    date        = request.form.get("date")
    time        = request.form.get("time")
    location    = request.form.get("location")
    cause       = request.form.get("cause")
    description = request.form.get("description")

    has_file = (
        "supporting_file" in request.files
        and request.files["supporting_file"].filename != ""
    )

    if not all([date, time, location, cause, description]) and not has_file:
        return jsonify({"error": "Please provide all details manually or upload a DOCX form."}), 400

    # Defaults when only a file was provided
    date        = date        or datetime.now().strftime("%Y-%m-%d")
    time        = time        or datetime.now().strftime("%H:%M")
    location    = location    or "Provided in DOCX form"
    cause       = cause       or "Provided in DOCX form"
    description = description or "Detailed description provided in the attached supporting DOCX document."

    # ── File handling ─────────────────────────────────────────────────
    supporting_file_path = None
    file_data            = None
    file_name            = None
    file_mime            = None

    if has_file:
        file         = request.files["supporting_file"]
        safe_name    = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        file_path    = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)

        # Save to disk (legacy)
        file.save(file_path)
        supporting_file_path = file_path

        # Read bytes for BLOB storage
        with open(file_path, "rb") as fh:
            file_data = fh.read()

        file_name = file.filename
        file_mime = file.mimetype or "application/octet-stream"

    # ── Create incident ────────────────────────────────────────────────
    incident = Incident(
        date=datetime.strptime(date, "%Y-%m-%d").date(),
        time=datetime.strptime(time, "%H:%M").time(),
        location=location,
        cause=cause,
        description=description,
        supporting_file=supporting_file_path,
        status="Pending",
        reported_by=current_user["id"],
        file_data=file_data,
        file_name=file_name,
        file_mime=file_mime,
    )
    db.session.add(incident)
    db.session.commit()

    # Generate PDF
    pdf_path         = generate_incident_pdf(incident, app.config["REPORT_FOLDER"])
    incident.pdf_file = pdf_path
    db.session.commit()

    try:
        send_email_notification(incident)
        send_sms_notification(incident)
    except Exception as exc:
        print(f"Notification error: {exc}")

    return jsonify({
        "message":  "Incident reported successfully",
        "incident": incident.to_dict(),
    }), 201


@app.route("/api/incidents/<int:incident_id>/status", methods=["PUT"])
@jwt_required()
def update_incident_status(incident_id):
    current_user = json.loads(get_jwt_identity())
    incident     = Incident.query.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    data       = request.get_json()
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Status is required"}), 400

    # Role-based status transition rules
    if new_status == "In Progress":
        if current_user["role"] != "admin":
            return jsonify({"error": "Only admin can set status to In Progress"}), 403
    elif new_status == "Solved":
        if current_user["role"] != "staff" or incident.reported_by != current_user["id"]:
            return jsonify({"error": "Only the reporting staff can mark as Solved"}), 403

    incident.status     = new_status
    incident.updated_at = datetime.utcnow()
    db.session.commit()

    try:
        send_email_notification(incident, status_update=True)
    except Exception as exc:
        print(f"Notification error: {exc}")

    return jsonify({
        "message":  "Status updated successfully",
        "incident": incident.to_dict(),
    }), 200


@app.route("/api/incidents/<int:incident_id>/file", methods=["GET"])
@jwt_required()
def download_incident_file(incident_id):
    """Stream the BLOB supporting file stored in MySQL for an incident.

    Falls back to the filesystem path if no BLOB is found (backward compat).
    """
    current_user = json.loads(get_jwt_identity())
    incident     = Incident.query.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    # Staff can only download their own incidents
    if current_user["role"] == "staff" and incident.reported_by != current_user["id"]:
        return jsonify({"error": "Unauthorized access"}), 403

    # ── Serve from BLOB ───────────────────────────────────────────────
    if incident.has_blob():
        return send_file(
            io.BytesIO(incident.file_data),
            mimetype=incident.file_mime or "application/octet-stream",
            as_attachment=True,
            download_name=incident.file_name or f"incident_{incident.id}_file",
        )

    # ── Fallback: serve from filesystem ──────────────────────────────
    if incident.supporting_file and os.path.exists(incident.supporting_file):
        return send_file(
            incident.supporting_file,
            as_attachment=True,
            download_name=os.path.basename(incident.supporting_file),
        )

    return jsonify({"error": "No supporting file found for this incident"}), 404


@app.route("/api/incidents/<int:incident_id>/pdf", methods=["GET"])
@jwt_required()
def download_incident_pdf(incident_id):
    """Download the generated PDF report for an incident."""
    current_user = json.loads(get_jwt_identity())
    incident     = Incident.query.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    if current_user["role"] == "staff" and incident.reported_by != current_user["id"]:
        return jsonify({"error": "Unauthorized access"}), 403

    if not incident.pdf_file or not os.path.exists(incident.pdf_file):
        pdf_path          = generate_incident_pdf(incident, app.config["REPORT_FOLDER"])
        incident.pdf_file = pdf_path
        db.session.commit()

    return send_file(
        incident.pdf_file,
        as_attachment=True,
        download_name=f"incident_{incident.id}.pdf",
    )


@app.route("/api/incidents/<int:incident_id>", methods=["DELETE"])
@jwt_required()
def delete_incident(incident_id):
    current_user = json.loads(get_jwt_identity())
    incident     = Incident.query.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    if current_user["role"] != "admin" and incident.reported_by != current_user["id"]:
        return jsonify({"error": "Unauthorized to delete this incident"}), 403

    # Delete filesystem files (BLOB is removed automatically with the row)
    try:
        if incident.supporting_file and os.path.exists(incident.supporting_file):
            os.remove(incident.supporting_file)
        if incident.pdf_file and os.path.exists(incident.pdf_file):
            os.remove(incident.pdf_file)
    except Exception as exc:
        print(f"Error deleting files for incident {incident_id}: {exc}")

    db.session.delete(incident)
    db.session.commit()
    return jsonify({"message": "Incident deleted successfully"}), 200


# ======================================================================
# ANALYTICS ROUTES
# ======================================================================

@app.route("/api/analytics/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard_analytics():
    current_user = json.loads(get_jwt_identity())
    query        = Incident.query

    if current_user["role"] == "staff":
        query = query.filter(Incident.reported_by == current_user["id"])

    total_incidents  = query.count()
    pending_count    = query.filter(Incident.status == "Pending").count()
    in_progress_count = query.filter(Incident.status == "In Progress").count()
    solved_count     = query.filter(Incident.status == "Solved").count()

    today       = datetime.now().date()
    weekly_data = []
    for i in range(6, -1, -1):
        day   = today - timedelta(days=i)
        count = query.filter(Incident.date == day).count()
        weekly_data.append({
            "day":   day.strftime("%a"),
            "date":  day.strftime("%Y-%m-%d"),
            "count": count,
        })

    monthly_data = []
    for i in range(5, -1, -1):
        month_date  = today - timedelta(days=i * 30)
        month_start = month_date.replace(day=1)
        next_month  = (month_start + timedelta(days=32)).replace(day=1) if i > 0 else today + timedelta(days=1)
        count       = query.filter(Incident.date >= month_start, Incident.date < next_month).count()
        monthly_data.append({
            "month": month_start.strftime("%b"),
            "count": count,
        })

    recent_incidents = query.order_by(Incident.created_at.desc()).limit(5).all()

    return jsonify({
        "total_incidents":   total_incidents,
        "pending_count":     pending_count,
        "in_progress_count": in_progress_count,
        "solved_count":      solved_count,
        "weekly_data":       weekly_data,
        "monthly_data":      monthly_data,
        "recent_incidents":  [i.to_dict() for i in recent_incidents],
    }), 200


@app.route("/api/reports/full", methods=["GET"])
@jwt_required()
def generate_full_report():
    guard = require_role("admin")
    if guard:
        return guard

    date_from = request.args.get("date_from")
    date_to   = request.args.get("date_to")
    status    = request.args.get("status")

    query = Incident.query
    if date_from:
        query = query.filter(Incident.date >= date_from)
    if date_to:
        query = query.filter(Incident.date <= date_to)
    if status:
        query = query.filter(Incident.status == status)

    incidents = query.order_by(Incident.created_at.desc()).all()
    pdf_path  = generate_full_report_pdf(incidents, app.config["REPORT_FOLDER"], date_from, date_to)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"full_report_{datetime.now().strftime('%Y%m%d')}.pdf",
    )


# ======================================================================
# NOTIFICATIONS ROUTE
# ======================================================================

@app.route("/api/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    notifications = [
        {
            "id":         1,
            "title":      "New Incident Reported",
            "message":    "A new incident has been submitted and is pending review.",
            "type":       "info",
            "created_at": datetime.now().isoformat(),
            "read":       False,
        },
        {
            "id":         2,
            "title":      "Status Update",
            "message":    "Incident #123 has been marked as In Progress.",
            "type":       "warning",
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "read":       True,
        },
    ]
    return jsonify({"notifications": notifications}), 200


# ======================================================================
# ERROR HANDLERS
# ======================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
