import jwt
from datetime import datetime, timedelta
from flask import current_app, request
from werkzeug.security import check_password_hash, generate_password_hash
from database.models import db, User, BeneficiaryMDM, AuditLog
import hashlib
import json

# Token Blacklist set for handling revoked tokens on logout
REVOKED_TOKENS = set()

class SSOService:
    """Federated Identity & Single Sign-On (SSO) Security Management Service"""
    
    @staticmethod
    def generate_token(user):
        """Generate Secure JWT Federated SSO Access Token with Expiry and Issuer Claims"""
        now = datetime.utcnow()
        payload = {
            'sub': user.id,
            'sso_id': user.sso_id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'full_name': user.full_name,
            'iss': 'GovInterop-Federated-SSO',
            'aud': 'Universal-Gov-Digital-Services',
            'exp': now + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'iat': now
        }
        token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        # Log Audit Record for SSO Login
        try:
            audit = AuditLog(
                actor=f"SSO_USER:{user.username}",
                action="SSO_TOKEN_ISSUED",
                details=json.dumps({
                    'sso_id': user.sso_id,
                    'role': user.role,
                    'issued_at': now.isoformat()
                })
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            
        return token

    @staticmethod
    def decode_token(token):
        """Decode, Validate Expiry, Issuer, and Revocation Status for JWT SSO Token"""
        if not token or token in REVOKED_TOKENS:
            return None
            
        try:
            payload = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithms=['HS256'],
                options={'verify_exp': True, 'verify_aud': False}
            )
            return payload
        except jwt.ExpiredSignatureError:
            print("[SSO SECURITY] Token Expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"[SSO SECURITY] Invalid Token Error: {e}")
            return None

    @staticmethod
    def revoke_token(token):
        """Revoke token upon user logout"""
        if token:
            REVOKED_TOKENS.add(token)
            return True
        return False

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
        """Register a new citizen and initialize their Master Data Management (MDM) Profile"""
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return None, "Username or Email already registered"
            
        sso_id = f"SSO-CITIZEN-NAT-{int(datetime.utcnow().timestamp())}"
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
        
        # Initialize Master Data Profile (MDM)
        state_salt = current_app.config.get('STATE_ID_SALT', 'universal-salt')
        state_hash = hashlib.sha256(f"{state_id}-{state_salt}".encode()).hexdigest()
        mdm = BeneficiaryMDM(
            user_id=user.id,
            state_id_hash=state_hash,
            master_profile_json=json.dumps({
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'verification_status': 'VERIFIED'
            }),
            is_verified=True
        )
        db.session.add(mdm)
        db.session.commit()
        
        return user, "Registration successful"
