from flask import Blueprint, request, jsonify, session
from services.sso_service import SSOService
from database.models import User, BeneficiaryMDM
import json

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Federated SSO Authentication Endpoint"""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
        
    user = SSOService.authenticate(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
        
    token = SSOService.generate_token(user)
    session['user_id'] = user.id
    session['sso_id'] = user.sso_id
    session['role'] = user.role
    
    return jsonify({
        'message': 'SSO Authentication Successful',
        'token': token,
        'user': {
            'id': user.id,
            'sso_id': user.sso_id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'full_name': user.full_name
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Citizen Registration & MDM Profile Initialization Endpoint"""
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    phone = data.get('phone', '')
    state_id = data.get('state_id', f"MH-CITIZEN-{username}")
    
    if not username or not email or not password or not full_name:
        return jsonify({'error': 'Missing required fields'}), 400
        
    user, msg = SSOService.register_citizen(username, email, password, full_name, phone, state_id)
    if not user:
        return jsonify({'error': msg}), 400
        
    token = SSOService.generate_token(user)
    return jsonify({
        'message': 'Citizen Account & Master Data Profile Created',
        'token': token,
        'user': {
            'sso_id': user.sso_id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    }), 201

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify JWT SSO Token for Inter-Departmental Services"""
    data = request.get_json() or {}
    token = data.get('token')
    
    if not token:
        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
    if not token:
        return jsonify({'valid': False, 'error': 'No token provided'}), 400
        
    payload = SSOService.decode_token(token)
    if not payload:
        return jsonify({'valid': False, 'error': 'Invalid or expired SSO token'}), 401
        
    return jsonify({
        'valid': True,
        'user': payload
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Clear SSO session"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200
