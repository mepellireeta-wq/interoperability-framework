import jwt
from datetime import datetime, timedelta
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash
from database.models import db, User, BeneficiaryMDM
import hashlib
import json

class SSOService:
    """Federated Identity & Single Sign-On (SSO) Management Service"""
    
    @staticmethod
    def generate_token(user):
        """Generate JWT Federated SSO Access Token"""
        payload = {
            'sub': user.id,
            'sso_id': user.sso_id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'full_name': user.full_name,
            'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def decode_token(token):
        """Decode and Verify JWT SSO Access Token"""
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None # Expired token
        except jwt.InvalidTokenError:
            return None # Invalid token

    @staticmethod
    def authenticate(username_or_email, password):
        """Authenticate user and return user instance if valid"""
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

    @staticmethod
    def register_citizen(username, email, password, full_name, phone, state_id):
        """Register a new citizen and initialize their MDM Profile"""
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return None, "Username or Email already registered"
            
        sso_id = f"SSO-CITIZEN-MH-{int(datetime.utcnow().timestamp())}"
        password_hash = generate_password_hash(password)
        
        user = User(
            sso_id=sso_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role='CITIZEN',
            full_name=full_name,
            phone=phone
        )
        db.session.add(user)
        db.session.commit()
        
        # Initialize Master Data Management (MDM) Profile
        state_hash = hashlib.sha256(f"{state_id}-{current_app.config['STATE_ID_SALT']}".encode()).hexdigest()
        mdm = BeneficiaryMDM(
            user_id=user.id,
            state_id_hash=state_hash,
            master_profile_json=json.dumps({
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'verification_status': 'PENDING'
            }),
            is_verified=True
        )
        db.session.add(mdm)
        db.session.commit()
        
        return user, "Registration successful"
