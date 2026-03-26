"""
Incident Model — DMMMSU-SLUC Disaster Monitoring System

File storage strategy
---------------------
Uploaded supporting files (DOCX, PDF, images, etc.) are stored in TWO places:

1. **BLOB in MySQL** (primary):
   - `file_data`  — raw binary bytes (LONGBLOB)
   - `file_name`  — original filename for Content-Disposition on download
   - `file_mime`  — MIME type for Content-Type on download

   The `GET /api/incidents/<id>/file` endpoint streams the BLOB directly to
   the browser without touching the filesystem.

2. **Filesystem path** (legacy / PDF generation):
   - `supporting_file` — relative path inside static/uploads/
     Kept so the PDF generator can still open the file locally.

Status workflow:
  Pending  →  In Progress (admin)  →  Solved (staff who reported it)
"""

from datetime import datetime
from models.database import db


class Incident(db.Model):
    """Incident report model."""

    __tablename__ = "incidents"

    __table_args__ = {
        "mysql_engine":  "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    # -----------------------------------------------------------------
    # Core columns
    # -----------------------------------------------------------------
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    incident_id = db.Column(db.String(30),  unique=True, nullable=False)
    date        = db.Column(db.Date,        nullable=False)
    time        = db.Column(db.Time,        nullable=False)
    location    = db.Column(db.String(255), nullable=False)
    cause       = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text,        nullable=False)

    # -----------------------------------------------------------------
    # BLOB storage (new — MySQL LONGBLOB)
    # -----------------------------------------------------------------
    file_data   = db.Column(db.LargeBinary(length=2**32 - 1), nullable=True,
                            comment="Binary content of the supporting file")
    file_name   = db.Column(db.String(255), nullable=True,
                            comment="Original filename for download header")
    file_mime   = db.Column(db.String(100), nullable=True,
                            comment="MIME type for Content-Type header")

    # -----------------------------------------------------------------
    # Legacy / PDF columns
    # -----------------------------------------------------------------
    supporting_file = db.Column(db.String(255), nullable=True)
    pdf_file        = db.Column(db.String(255), nullable=True)

    # -----------------------------------------------------------------
    # Status & metadata
    # -----------------------------------------------------------------
    status      = db.Column(
        db.Enum("Pending", "In Progress", "Solved", name="incident_status"),
        nullable=False,
        default="Pending",
    )
    reported_by = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at  = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # -----------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------
    def __init__(
        self,
        date,
        time,
        location: str,
        cause: str,
        description: str,
        reported_by: int,
        supporting_file: str = None,
        status: str = "Pending",
        pdf_file: str = None,
        file_data: bytes = None,
        file_name: str = None,
        file_mime: str = None,
    ):
        self.date            = date
        self.time            = time
        self.location        = location
        self.cause           = cause
        self.description     = description
        self.reported_by     = reported_by
        self.supporting_file = supporting_file
        self.status          = status
        self.pdf_file        = pdf_file
        self.file_data       = file_data
        self.file_name       = file_name
        self.file_mime       = file_mime

        # Generate unique incident ID
        self.incident_id = self._generate_incident_id()

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------
    def _generate_incident_id(self) -> str:
        """Generate ID in format DMMMSU-YYYYMMDD-XXXX."""
        date_str = datetime.now().strftime("%Y%m%d")
        count = Incident.query.filter(
            db.func.date(Incident.created_at) == datetime.now().date()
        ).count()
        sequence = str(count + 1).zfill(4)
        return f"DMMMSU-{date_str}-{sequence}"

    def has_blob(self) -> bool:
        """Return True if a file is stored in the database as BLOB."""
        return self.file_data is not None and len(self.file_data) > 0

    def __repr__(self) -> str:
        return f"<Incident {self.incident_id} [{self.status}]>"

    def to_dict(self) -> dict:
        """
        Serialize to JSON-safe dict.
        BLOB bytes are never included; only metadata (file_name, file_mime)
        and a boolean flag (has_file) are exposed.
        """
        return {
            "id":             self.id,
            "incident_id":    self.incident_id,
            "date":           self.date.isoformat()     if self.date       else None,
            "time":           self.time.isoformat()     if self.time       else None,
            "location":       self.location,
            "cause":          self.cause,
            "description":    self.description,
            # BLOB metadata (safe to expose; raw bytes are not)
            "has_file":       self.has_blob(),
            "file_name":      self.file_name,
            "file_mime":      self.file_mime,
            # Legacy filesystem path (may be None once fully migrated)
            "supporting_file": self.supporting_file,
            "pdf_file":       self.pdf_file,
            "status":         self.status,
            "reported_by":    self.reported_by,
            "reporter_name":  self.reporter.full_name if self.reporter else None,
            "created_at":     self.created_at.isoformat() if self.created_at else None,
            "updated_at":     self.updated_at.isoformat() if self.updated_at else None,
        }
