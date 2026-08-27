from flask import Blueprint, request, jsonify, session
from database.models import db, User, BeneficiaryMDM
from services.sso_service import SSOService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Federated SSO Login Endpoint - Generates JWT Token & establishes session"""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = SSOService.authenticate(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials or inactive account'}), 401

    token = SSOService.generate_token(user)
    
    # Store session role
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role

    return jsonify({
        'message': 'Authentication successful',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'role': user.role,
            'dept_code': user.dept_code
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Citizen Registration API - Creates User & MDM Beneficiary Profile"""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    full_name = data.get('full_name')
    phone = data.get('phone', '')
    state = data.get('state', 'Maharashtra')
    role = data.get('role', 'CITIZEN')

    if not username or not password or not email or not full_name:
        return jsonify({'error': 'Full name, username, email, and password are required'}), 400

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({'error': 'Username or Email already registered'}), 409

    user = User(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'Citizen Account registered successfully',
        'user_id': user.id,
        'username': user.username
    }), 201

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """SSO Logout Endpoint - Revokes JWT token & clears session"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        SSOService.revoke_token(token)

    session.clear()
    return jsonify({'message': 'Session ended & JWT token revoked'}), 200
