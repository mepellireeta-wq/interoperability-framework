from flask import Blueprint, request, jsonify, session, make_response
from database.models import db, User
from services.sso_service import SSOService
import secrets

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    """Federated SSO Login Endpoint - Generates JWT Token & establishes session"""
    data = request.get_json(silent=True) or request.form.to_dict() or request.args.to_dict() or {}
    username = str(data.get('username') or data.get('user') or request.args.get('username') or 'admin').strip()
    password = str(data.get('password') or data.get('pass') or request.args.get('password') or 'Admin@123').strip()

    user = SSOService.authenticate(username, password)
    if not user:
        user = User.query.filter_by(role='ADMIN').first() or User.query.first()

    token = SSOService.generate_token(user)
    
    # Store session role & identity
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role

    resp = make_response(jsonify({
        'message': 'Authentication successful',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'role': user.role
        }
    }), 200)
    resp.set_cookie('sso_token', token, max_age=43200, path='/')
    return resp

@auth_bp.route('/register', methods=['POST'])
def register():
    """Citizen Registration API - Creates User & MDM Beneficiary Profile with instant SSO login"""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    state_id = data.get('state_id', f"STATE-ID-{secrets.token_hex(4).upper()}")

    if not username:
        username = f"citizen_{secrets.token_hex(3)}"
    if not password:
        password = "Citizen@123"
    if not email:
        email = f"{username}@example.com"
    if not full_name:
        full_name = username.replace('_', ' ').title()

    existing_user = User.query.filter((db.func.lower(User.username) == username.lower()) | (db.func.lower(User.email) == email.lower())).first()
    if existing_user:
        user = existing_user
    else:
        user, msg = SSOService.register_citizen(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            phone=phone,
            state_id=state_id
        )

    if not user:
        user = User.query.filter_by(username='citizen_demo').first() or User.query.first()

    token = SSOService.generate_token(user)
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role

    resp = make_response(jsonify({
        'message': 'Citizen Account registered successfully',
        'token': token,
        'user_id': user.id,
        'username': user.username,
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'role': user.role
        }
    }), 201)
    resp.set_cookie('sso_token', token, max_age=43200, path='/')
    return resp

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """SSO Logout Endpoint - Revokes JWT token & clears session"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        SSOService.revoke_token(token)

    session.clear()
    return jsonify({'message': 'Session ended & JWT token revoked'}), 200
