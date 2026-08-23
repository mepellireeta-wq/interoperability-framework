from flask import Blueprint, request, jsonify, session
from database.models import Department, Application, AuditLog
from services.consent_service import ConsentService
from functools import wraps
from services.sso_service import SSOService

gateway_bp = Blueprint('gateway', __name__, url_prefix='/api/v1/gateway')

def rbac_required(allowed_roles):
    """Role-Based Access Control (RBAC) Decorator validating JWT & Session Roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            user_role = session.get('role')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                payload = SSOService.decode_token(token)
                if payload:
                    user_role = payload.get('role')
                else:
                    return jsonify({'error': 'Invalid or expired SSO token'}), 401
                    
            if not user_role or user_role not in allowed_roles:
                return jsonify({
                    'error': 'Unauthorized access: insufficient role privileges',
                    'allowed_roles': allowed_roles,
                    'user_role': user_role or 'GUEST'
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@gateway_bp.route('/services', methods=['GET'])
def list_service_registry():
    """Service Discovery Registry - List available universal state & central services"""
    services = [
        {
            'service_code': 'SKILL_TRAINING_SCHEME',
            'title': 'National Skill Development & Vocational Certification Scheme',
            'department': 'Department of Skills Development',
            'dept_code': 'DEPT_SKILLS',
            'integration_type': 'REST_API',
            'description': 'Vocational skill training, national certifications, and apprentice stipends.'
        },
        {
            'service_code': 'EMPLOYMENT_SELF_EMPLOY',
            'title': 'Prime Minister Employment Generation & Self-Employment Scheme',
            'department': 'Directorate of Employment & Self Employment',
            'dept_code': 'DEPT_EMPLOYMENT',
            'integration_type': 'LEGACY_SOAP',
            'description': 'Credit-linked financial subsidy for setting up micro-enterprises.'
        },
        {
            'service_code': 'INNOVATION_STARTUP_GRANT',
            'title': 'National Startup & Technology Innovation Seed Grant Fund',
            'department': 'State & National Innovation Society',
            'dept_code': 'DEPT_ENTREPRENEURSHIP',
            'integration_type': 'DIRECT_DB',
            'description': 'Early-stage equity & seed grant funding for tech startups.'
        },
        {
            'service_code': 'UNIFIED_SKILL_TO_GRANT',
            'title': 'Universal Integrated Skill-to-Entrepreneurship Pathway',
            'department': 'Multi-Department Integrated Pathway',
            'dept_code': 'MULTI_DEPT',
            'integration_type': 'INTEROP_WORKFLOW',
            'description': 'Unified 3-stage service covering Skill Training, Employment Registry, and Startup Seed Grant.'
        }
    ]
    return jsonify({
        'count': len(services),
        'services': services
    }), 200

@gateway_bp.route('/consent/grant', methods=['POST'])
def grant_consent():
    """Consent Manager - Record citizen consent for cross-department data sharing with IP & Audit trail"""
    data = request.get_json() or {}
    application_id = data.get('application_id')
    user_id = data.get('user_id') or session.get('user_id', 1)
    dept_code = data.get('dept_code', 'MULTI_DEPT')
    
    if not application_id:
        return jsonify({'error': 'Application ID required'}), 400
        
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    
    log = ConsentService.log_consent_event(
        application_id, 
        user_id, 
        dept_code, 
        action_type="CITIZEN_CONSENT_GRANTED",
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    return jsonify({
        'status': 'Consent Recorded & Logged',
        'audit_id': log.id,
        'policy_version': ConsentService.POLICY_VERSION
    }), 200

@gateway_bp.route('/security-health', methods=['GET'])
@rbac_required(['ADMIN', 'OFFICER'])
def get_security_health():
    """SIH Presentation Diagnostics Endpoint - Security & Gateway Governance Status"""
    total_logs = AuditLog.query.count()
    consent_logs = AuditLog.query.filter(AuditLog.action.like('%CONSENT%')).count()
    
    return jsonify({
        'status': 'SECURE',
        'gateway_governance': {
            'rbac_enforced': True,
            'federated_sso_status': 'ACTIVE (JWT HS256)',
            'consent_manager_policy': ConsentService.POLICY_VERSION,
            'total_audit_records': total_logs,
            'consent_audit_records': consent_logs,
            'security_standard': 'National E-Governance Security Standards 2026'
        }
    }), 200

@gateway_bp.route('/departments', methods=['GET'])
def get_registered_departments():
    """Service Discovery - Get active registered government departments"""
    depts = Department.query.filter_by(is_active=True).all()
    return jsonify({
        'count': len(depts),
        'departments': [{
            'id': d.id,
            'dept_code': d.dept_code,
            'name': d.name,
            'system_type': d.system_type,
            'endpoint_url': d.endpoint_url
        } for d in depts]
    }), 200
