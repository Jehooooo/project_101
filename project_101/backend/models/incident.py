"""
Incident Model for DMMMSU-SLUC Disaster Monitoring System
"""

from datetime import datetime
from models.database import db

class Incident(db.Model):
    """Incident report model"""
    
    __tablename__ = 'incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.String(20), unique=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    cause = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    supporting_file = db.Column(db.String(255))
    pdf_file = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Pending')  # Pending, In Progress, Solved
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, date, time, location, cause, description, reported_by, 
                 supporting_file=None, status='Pending', pdf_file=None):
        self.date = date
        self.time = time
        self.location = location
        self.cause = cause
        self.description = description
        self.reported_by = reported_by
        self.supporting_file = supporting_file
        self.status = status
        self.pdf_file = pdf_file
        
        # Generate unique incident ID
        self.incident_id = self._generate_incident_id()
    
    def _generate_incident_id(self):
        """Generate unique incident ID format: DMMMSU-YYYYMMDD-XXXX"""
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        
        # Get the count of incidents for today
        count = Incident.query.filter(
            db.func.date(Incident.created_at) == datetime.now().date()
        ).count()
        
        sequence = str(count + 1).zfill(4)
        return f"DMMMSU-{date_str}-{sequence}"
    
    def __repr__(self):
        return f'<Incident {self.incident_id}>'
    
    def to_dict(self):
        """Convert incident object to dictionary"""
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time.isoformat() if self.time else None,
            'location': self.location,
            'cause': self.cause,
            'description': self.description,
            'supporting_file': self.supporting_file,
            'pdf_file': self.pdf_file,
            'status': self.status,
            'reported_by': self.reported_by,
            'reporter_name': self.reporter.full_name if self.reporter else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_status_color(self):
        """Get status color for UI"""
        colors = {
            'Pending': '#EF4444',      # Red
            'In Progress': '#F59E0B',  # Amber
            'Solved': '#10B981'        # Green
        }
        return colors.get(self.status, '#6B7280')
    
    def get_status_badge_class(self):
        """Get status badge class for UI"""
        classes = {
            'Pending': 'bg-red-100 text-red-800',
            'In Progress': 'bg-amber-100 text-amber-800',
            'Solved': 'bg-green-100 text-green-800'
        }
        return classes.get(self.status, 'bg-gray-100 text-gray-800')
