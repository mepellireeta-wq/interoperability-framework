from flask import Blueprint, request, jsonify, session
from database.models import db, User
from services.sso_service import SSOService
import secrets

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Federated SSO Login Endpoint - Generates JWT Token & establishes session"""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = SSOService.authenticate(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials or account does not exist'}), 401

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
            'role': user.role
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Citizen Registration API - Creates User & MDM Beneficiary Profile"""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    state_id = data.get('state_id', f"STATE-ID-{secrets.token_hex(4).upper()}")

    if not username or not password or not email or not full_name:
        return jsonify({'error': 'Full name, username, email, and password are required'}), 400

    user, msg = SSOService.register_citizen(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        phone=phone,
        state_id=state_id
    )

    if not user:
        return jsonify({'error': msg}), 400

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
