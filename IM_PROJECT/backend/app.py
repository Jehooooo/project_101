"""
DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System
Backend API - Flask Application
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json

from models.database import db, init_db
from models.user import User
from models.incident import Incident
from utils.pdf_generator import generate_incident_pdf, generate_full_report_pdf
from utils.notifications import send_email_notification, send_sms_notification

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dmmmsu-sluc-secret-key-2024')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-dmmmsu')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///dmmmsu_disaster.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['REPORT_FOLDER'] = 'static/reports'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

# Initialize extensions
CORS(app)
jwt = JWTManager(app)
db.init_app(app)

# Initialize database
with app.app_context():
    init_db()
    # Create default admin if not exists
    admin = User.query.filter_by(email='admin@dmmmsu.edu.ph').first()
    if not admin:
        admin = User(
            email='admin@dmmmsu.edu.ph',
            password=generate_password_hash('admin123'),
            first_name='System',
            last_name='Administrator',
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: admin@dmmmsu.edu.ph / admin123")

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    access_token = create_access_token(
        identity=json.dumps({
            'id': user.id,
            'email': user.email,
            'role': user.role
        })
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user"""
    current_user_id = json.loads(get_jwt_identity())['id']
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

# ==================== USER MANAGEMENT ROUTES (Admin Only) ====================

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (Admin only)"""
    current_user = json.loads(get_jwt_identity())
    
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]}), 200

@app.route('/api/users', methods=['POST'])
@jwt_required()
def create_user():
    """Create new staff user (Admin only)"""
    current_user = json.loads(get_jwt_identity())
    
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    new_user = User(
        email=data['email'],
        password=generate_password_hash(data['password']),
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=data.get('role', 'staff'),
        phone=data.get('phone'),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully', 'user': new_user.to_dict()}), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user (Admin only)"""
    current_user = json.loads(get_jwt_identity())
    
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'role' in data:
        user.role = data['role']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'password' in data and data['password']:
        user.password = generate_password_hash(data['password'])
    
    db.session.commit()
    
    return jsonify({'message': 'User updated successfully', 'user': user.to_dict()}), 200

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete user (Admin only)"""
    current_user = json.loads(get_jwt_identity())
    
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200

# ==================== INCIDENT ROUTES ====================

@app.route('/api/incidents', methods=['GET'])
@jwt_required()
def get_incidents():
    """Get all incidents with filtering"""
    current_user = json.loads(get_jwt_identity())
    
    # Query parameters
    status = request.args.get('status')
    location = request.args.get('location')
    category = request.args.get('category')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build query
    query = Incident.query
    
    # Apply filters
    if status:
        query = query.filter(Incident.status == status)
    if location:
        query = query.filter(Incident.location.ilike(f'%{location}%'))
    if category:
        query = query.filter(Incident.cause.ilike(f'%{category}%'))
    if date_from:
        query = query.filter(Incident.date >= date_from)
    if date_to:
        query = query.filter(Incident.date <= date_to)
    if search:
        query = query.filter(
            db.or_(
                Incident.location.ilike(f'%{search}%'),
                Incident.cause.ilike(f'%{search}%'),
                Incident.description.ilike(f'%{search}%')
            )
        )
    
    # Staff can only see their own incidents
    if current_user['role'] == 'staff':
        query = query.filter(Incident.reported_by == current_user['id'])
    
    # Order by date desc
    query = query.order_by(Incident.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    incidents = pagination.items
    
    return jsonify({
        'incidents': [incident.to_dict() for incident in incidents],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    }), 200

@app.route('/api/incidents/<int:incident_id>', methods=['GET'])
@jwt_required()
def get_incident(incident_id):
    """Get single incident by ID"""
    current_user = json.loads(get_jwt_identity())
    
    incident = Incident.query.get(incident_id)
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    
    # Staff can only view their own incidents
    if current_user['role'] == 'staff' and incident.reported_by != current_user['id']:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    return jsonify({'incident': incident.to_dict()}), 200

@app.route('/api/incidents', methods=['POST'])
@jwt_required()
def create_incident():
    """Create new incident report (Staff only)"""
    current_user = json.loads(get_jwt_identity())
    
    # Get form data
    date = request.form.get('date')
    time = request.form.get('time')
    location = request.form.get('location')
    cause = request.form.get('cause')
    description = request.form.get('description')
    
    # Validate required fields
    if not all([date, time, location, cause, description]):
        return jsonify({'error': 'All required fields must be provided'}), 400
    
    # Handle file upload
    supporting_file = None
    if 'supporting_file' in request.files:
        file = request.files['supporting_file']
        if file.filename:
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            supporting_file = file_path
    
    # Create incident
    incident = Incident(
        date=datetime.strptime(date, '%Y-%m-%d').date(),
        time=datetime.strptime(time, '%H:%M').time(),
        location=location,
        cause=cause,
        description=description,
        supporting_file=supporting_file,
        status='Pending',
        reported_by=current_user['id']
    )
    
    db.session.add(incident)
    db.session.commit()
    
    # Generate PDF
    pdf_path = generate_incident_pdf(incident, app.config['REPORT_FOLDER'])
    incident.pdf_file = pdf_path
    db.session.commit()
    
    # Send notifications (mock implementation)
    try:
        send_email_notification(incident)
        send_sms_notification(incident)
    except Exception as e:
        print(f"Notification error: {e}")
    
    return jsonify({
        'message': 'Incident reported successfully',
        'incident': incident.to_dict()
    }), 201

@app.route('/api/incidents/<int:incident_id>/status', methods=['PUT'])
@jwt_required()
def update_incident_status(incident_id):
    """Update incident status"""
    current_user = json.loads(get_jwt_identity())
    
    incident = Incident.query.get(incident_id)
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400
    
    # Validate status transitions based on role
    if new_status == 'In Progress':
        if current_user['role'] != 'admin':
            return jsonify({'error': 'Only admin can set status to In Progress'}), 403
    elif new_status == 'Solved':
        if current_user['role'] != 'staff' or incident.reported_by != current_user['id']:
            return jsonify({'error': 'Only the reporting staff can mark as Solved'}), 403
    
    incident.status = new_status
    incident.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Send status update notification
    try:
        send_email_notification(incident, status_update=True)
    except Exception as e:
        print(f"Notification error: {e}")
    
    return jsonify({
        'message': 'Status updated successfully',
        'incident': incident.to_dict()
    }), 200

@app.route('/api/incidents/<int:incident_id>/pdf', methods=['GET'])
@jwt_required()
def download_incident_pdf(incident_id):
    """Download incident PDF report"""
    current_user = json.loads(get_jwt_identity())
    
    incident = Incident.query.get(incident_id)
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    
    # Staff can only download their own incidents
    if current_user['role'] == 'staff' and incident.reported_by != current_user['id']:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    if not incident.pdf_file or not os.path.exists(incident.pdf_file):
        # Regenerate PDF if missing
        pdf_path = generate_incident_pdf(incident, app.config['REPORT_FOLDER'])
        incident.pdf_file = pdf_path
        db.session.commit()
    
    return send_file(incident.pdf_file, as_attachment=True, download_name=f"incident_{incident.id}.pdf")

# ==================== ANALYTICS ROUTES ====================

@app.route('/api/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Get dashboard analytics data"""
    current_user = json.loads(get_jwt_identity())
    
    # Base query
    query = Incident.query
    
    # Staff can only see their own data
    if current_user['role'] == 'staff':
        query = query.filter(Incident.reported_by == current_user['id'])
    
    # Total incidents
    total_incidents = query.count()
    
    # Status breakdown
    pending_count = query.filter(Incident.status == 'Pending').count()
    in_progress_count = query.filter(Incident.status == 'In Progress').count()
    solved_count = query.filter(Incident.status == 'Solved').count()
    
    # Weekly data (last 7 days)
    from datetime import datetime, timedelta
    today = datetime.now().date()
    weekly_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = query.filter(Incident.date == date).count()
        weekly_data.append({
            'day': date.strftime('%a'),
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Monthly data (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i*30)
        month_start = month_date.replace(day=1)
        if i > 0:
            next_month = (month_start + timedelta(days=32)).replace(day=1)
        else:
            next_month = today + timedelta(days=1)
        count = query.filter(Incident.date >= month_start, Incident.date < next_month).count()
        monthly_data.append({
            'month': month_start.strftime('%b'),
            'count': count
        })
    
    # Recent incidents
    recent_incidents = query.order_by(Incident.created_at.desc()).limit(5).all()
    
    return jsonify({
        'total_incidents': total_incidents,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'solved_count': solved_count,
        'weekly_data': weekly_data,
        'monthly_data': monthly_data,
        'recent_incidents': [inc.to_dict() for inc in recent_incidents]
    }), 200

@app.route('/api/reports/full', methods=['GET'])
@jwt_required()
def generate_full_report():
    """Generate full compiled report"""
    current_user = json.loads(get_jwt_identity())
    
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get filter parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    status = request.args.get('status')
    
    query = Incident.query
    
    if date_from:
        query = query.filter(Incident.date >= date_from)
    if date_to:
        query = query.filter(Incident.date <= date_to)
    if status:
        query = query.filter(Incident.status == status)
    
    incidents = query.order_by(Incident.created_at.desc()).all()
    
    # Generate compiled PDF
    pdf_path = generate_full_report_pdf(incidents, app.config['REPORT_FOLDER'], date_from, date_to)
    
    return send_file(pdf_path, as_attachment=True, download_name=f"full_report_{datetime.now().strftime('%Y%m%d')}.pdf")

# ==================== NOTIFICATION ROUTES ====================

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get system notifications"""
    current_user = json.loads(get_jwt_identity())
    
    # Mock notifications - in production, this would come from a notifications table
    notifications = [
        {
            'id': 1,
            'title': 'New Incident Reported',
            'message': 'A new incident has been submitted and is pending review.',
            'type': 'info',
            'created_at': datetime.now().isoformat(),
            'read': False
        },
        {
            'id': 2,
            'title': 'Status Update',
            'message': 'Incident #123 has been marked as In Progress.',
            'type': 'warning',
            'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
            'read': True
        }
    ]
    
    return jsonify({'notifications': notifications}), 200

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
