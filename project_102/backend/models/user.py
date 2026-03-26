"""
User Model — DMMMSU-SLUC Disaster Monitoring System

Role-based access control:
  - 'admin'  : full access (manage users, update statuses, view all incidents)
  - 'staff'  : can submit and view own incidents

Passwords are stored as Werkzeug PBKDF2-SHA256 hashes (never plain-text).
"""

from datetime import datetime
from models.database import db


class User(db.Model):
    """User model for administrators and staff."""

    __tablename__ = "users"

    # MySQL-specific table options (charset / engine)
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    user_id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    # Column stored in DB as 'password_hash'; application code accesses it via
    # the attribute name 'password' for backward compatibility.
    password   = db.Column("password_hash", db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name  = db.Column(db.String(100), nullable=False)

    # ENUM enforced at the DB level — only 'admin' or 'staff' are valid values
    role       = db.Column(
        db.Enum("admin", "staff", name="user_role"),
        nullable=False,
        default="staff",
    )

    phone      = db.Column(db.String(20), nullable=True)
    is_active  = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    incidents = db.relationship("Incident", backref="reporter", lazy=True)

    def __init__(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str = "staff",
        phone: str = None,
        is_active: bool = True,
    ):
        self.email      = email
        self.password   = password
        self.first_name = first_name
        self.last_name  = last_name
        self.role       = role
        self.phone      = phone
        self.is_active  = is_active

    # ------------------------------------------------------------------
    # Properties / helpers
    # ------------------------------------------------------------------

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_staff(self) -> bool:
        return self.role == "staff"

    def __repr__(self) -> str:
        return f"<User {self.email} [{self.role}]>"

    def to_dict(self) -> dict:
        """Serialize user to a safe JSON-friendly dictionary (no password)."""
        return {
            "id":         self.user_id,
            "email":      self.email,
            "first_name": self.first_name,
            "last_name":  self.last_name,
            "full_name":  self.full_name,
            "role":       self.role,
            "phone":      self.phone,
            "is_active":  self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
