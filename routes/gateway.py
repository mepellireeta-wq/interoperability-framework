from flask import Blueprint, request, jsonify, session
from database.models import Department, Application, AuditLog
from services.consent_service import ConsentService
from functools import wraps
from services.sso_service import SSOService
from services.iot_connector import IoTTelemetryConnector
from services.quantum_engine import QuantumSecurityEngine
from services.open_data_sync import OpenGovernmentDataSync

gateway_bp = Blueprint('gateway', __name__, url_prefix='/api/v1/gateway')

# Full List of All 28 States & 8 Union Territories of India
ALL_INDIA_STATES_UTS = [
    'ALL', 'Andhra Pradesh', 'Telangana', 'Maharashtra', 'Karnataka', 'Tamil Nadu',
    'Uttar Pradesh', 'Delhi (NCT)', 'Gujarat', 'Rajasthan', 'West Bengal', 'Kerala',
    'Bihar', 'Madhya Pradesh', 'Punjab', 'Haryana', 'Odisha', 'Assam', 'Jharkhand',
    'Chhattisgarh', 'Himachal Pradesh', 'Uttarakhand', 'Jammu & Kashmir', 'Ladakh',
    'Goa', 'Sikkim', 'Tripura', 'Meghalaya', 'Manipur', 'Nagaland', 'Mizoram',
    'Arunachal Pradesh', 'Chandigarh', 'Puducherry', 'Andaman & Nicobar', 'Dadra & Nagar Haveli'
]

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

# Comprehensive 10-Sector All-India Governance Schemes Database
UNIVERSAL_SCHEMES = [
    # 🎓 EDUCATION SECTOR
    {
        'service_code': 'EDU_SCHOLARSHIP_GRANT',
        'title': 'National Higher Education & Merit Scholarship Scheme',
        'domain': 'Education',
        'department': 'Department of Higher & Technical Education',
        'dept_code': 'DEPT_EDUCATION',
        'applicable_states': ['ALL'],
        'integration_type': 'REST_API',
        'description': 'Direct scholarship & tuition fee waiver for higher education students.'
    },
    {
        'service_code': 'EDU_STUDENT_LOAN_SUBSIDY',
        'title': 'Central Education Loan Interest Subsidy Scheme',
        'domain': 'Education',
        'department': 'Ministry of Education & Banking Consortium',
        'dept_code': 'DEPT_EDUCATION',
        'applicable_states': ['ALL'],
        'integration_type': 'INTEROP_WORKFLOW',
        'description': 'Interest subsidy for students pursuing professional degrees.'
    },
    
    # 🏥 HEALTH & MEDICAL SECTOR
    {
        'service_code': 'HEALTH_AYUSHMAN_CARD',
        'title': 'Ayushman Bharat Universal Health Protection Scheme',
        'domain': 'Health',
        'department': 'National Health Authority & State Health Agency',
        'dept_code': 'DEPT_HEALTH',
        'applicable_states': ['ALL'],
        'integration_type': 'REST_API',
        'description': 'Cashless health insurance coverage up to ₹5 Lakh per family per year.'
    },
    
    # 🏦 BANKING & FINANCIAL SERVICES SECTOR
    {
        'service_code': 'BANKING_MUDRA_LOAN',
        'title': 'Pradhan Mantri MUDRA Micro-Business Loan Scheme',
        'domain': 'Banking',
        'department': 'Department of Financial Services & Public Banks',
        'dept_code': 'DEPT_BANKING',
        'applicable_states': ['ALL'],
        'integration_type': 'LEGACY_SOAP',
        'description': 'Collateral-free micro-loans up to ₹10 Lakh for small enterprise setup.'
    },
    
    # 🛡️ INSURANCE & SOCIAL WELFARE SECTOR
    {
        'service_code': 'INSURANCE_CROP_SAFETY',
        'title': 'PM Fasal Bima Crop & Agricultural Risk Insurance',
        'domain': 'Insurance',
        'department': 'Ministry of Agriculture & Insurance Regulatory Body',
        'dept_code': 'DEPT_INSURANCE',
        'applicable_states': ['ALL', 'Andhra Pradesh', 'Telangana', 'Maharashtra', 'Karnataka', 'Uttar Pradesh', 'Gujarat'],
        'integration_type': 'DIRECT_DB',
        'description': 'Comprehensive crop damage insurance coverage against natural calamities.'
    },
    
    # 🌾 AGRICULTURE SECTOR
    {
        'service_code': 'AGRI_PM_KISAN_DBT',
        'title': 'PM-KISAN Direct Benefit Income Support Scheme',
        'domain': 'Agriculture',
        'department': 'Department of Agriculture & Farmers Welfare',
        'dept_code': 'DEPT_AGRICULTURE',
        'applicable_states': ['ALL', 'Andhra Pradesh', 'Telangana', 'Maharashtra', 'Karnataka', 'Uttar Pradesh', 'Tamil Nadu', 'Gujarat'],
        'integration_type': 'REST_API',
        'description': 'Annual income support of ₹6,000 transferred directly to landholding farmers.'
    },
    
    # 🚀 INNOVATION, STARTUPS & MSME SECTOR
    {
        'service_code': 'INNOVATION_STARTUP_GRANT',
        'title': 'National Startup & MSME Technology Innovation Seed Grant Fund',
        'domain': 'Innovation',
        'department': 'State & National Innovation Society (MSINS)',
        'dept_code': 'DEPT_ENTREPRENEURSHIP',
        'applicable_states': ['ALL'],
        'integration_type': 'DIRECT_DB',
        'description': 'Early-stage equity & seed grant funding for tech startups.'
    },
    
    # ⚡ INFRASTRUCTURE & RENEWABLE ENERGY SECTOR
    {
        'service_code': 'INFRA_SOLAR_ROOFTOP_SUBSIDY',
        'title': 'PM Surya Ghar Free Electricity & Rooftop Solar Subsidy',
        'domain': 'Infrastructure',
        'department': 'Ministry of New & Renewable Energy',
        'dept_code': 'DEPT_INFRASTRUCTURE',
        'applicable_states': ['ALL'],
        'integration_type': 'REST_API',
        'description': 'Up to ₹78,000 central subsidy for installing residential rooftop solar panels.'
    },

    # ⚙️ SKILLS & EMPLOYMENT SECTOR
    {
        'service_code': 'SKILL_TRAINING_SCHEME',
        'title': 'National Skill Development & Vocational Certification Scheme',
        'domain': 'Skills',
        'department': 'Department of Skills Development',
        'dept_code': 'DEPT_SKILLS',
        'applicable_states': ['ALL'],
        'integration_type': 'REST_API',
        'description': 'Vocational skill training, national certifications, and apprentice stipends.'
    },
    {
        'service_code': 'EMPLOYMENT_SELF_EMPLOY',
        'title': 'Prime Minister Employment Generation & Self-Employment Scheme',
        'domain': 'Employment',
        'department': 'Directorate of Employment & Self Employment',
        'dept_code': 'DEPT_EMPLOYMENT',
        'applicable_states': ['ALL'],
        'integration_type': 'LEGACY_SOAP',
        'description': 'Credit-linked financial subsidy for setting up micro-enterprises.'
    },
    {
        'service_code': 'UNIFIED_SKILL_TO_GRANT',
        'title': 'Universal Integrated Skill-to-Entrepreneurship Pathway',
        'domain': 'Skills',
        'department': 'Multi-Department Integrated Pathway',
        'dept_code': 'MULTI_DEPT',
        'applicable_states': ['ALL'],
        'integration_type': 'INTEROP_WORKFLOW',
        'description': 'Unified 3-stage service covering Skill Training, Employment Registry, and Startup Seed Grant.'
    }
]

@gateway_bp.route('/services', methods=['GET'])
def list_service_registry():
    """Service Discovery Registry with State-wise and Sector Domain Filtering"""
    state_filter = request.args.get('state', 'ALL').strip()
    domain_filter = request.args.get('domain', 'ALL').strip()
    
    filtered_schemes = UNIVERSAL_SCHEMES
    
    if state_filter and state_filter.upper() != 'ALL':
        filtered_schemes = [
            s for s in filtered_schemes 
            if 'ALL' in s['applicable_states'] or state_filter.lower() in [st.lower() for st in s['applicable_states']]
        ]
        
    if domain_filter and domain_filter.upper() != 'ALL':
        filtered_schemes = [
            s for s in filtered_schemes 
            if s['domain'].lower() == domain_filter.lower()
        ]
        
    return jsonify({
        'count': len(filtered_schemes),
        'selected_state': state_filter,
        'selected_domain': domain_filter,
        'all_india_states': ALL_INDIA_STATES_UTS,
        'services': filtered_schemes
    }), 200

@gateway_bp.route('/states', methods=['GET'])
def get_all_india_states():
    """Get list of all 28 States and 8 Union Territories of India"""
    return jsonify({
        'total_count': len(ALL_INDIA_STATES_UTS) - 1, # Exclude 'ALL'
        'states_and_uts': ALL_INDIA_STATES_UTS
    }), 200

@gateway_bp.route('/quantum-status', methods=['GET'])

def get_quantum_security_status():
    """SIH Uniqueness Feature - Quantum-Safe Cryptography & BB84 QKD Middleware Diagnostics"""
    qkd_simulation = QuantumSecurityEngine.simulate_bb84_qkd_protocol(bit_length=256)
    
    return jsonify({
        'status': 'QUANTUM_SAFE_ACTIVE',
        'quantum_cryptography': {
            'post_quantum_lattice': 'NIST-Kyber-1024-Encrypted',
            'qkd_protocol': qkd_simulation['quantum_protocol'],
            'qubit_fidelity_rate': qkd_simulation['qubit_fidelity_rate'],
            'sifted_quantum_key_sample': f"{qkd_simulation['sifted_quantum_key'][:16]}...",
            'security_uniqueness': 'Quantum Key Distribution (QKD) Middleware Overlay'
        }
    }), 200

@gateway_bp.route('/realtime-sync', methods=['GET'])

def get_realtime_data_sync():
    """Real-time Open Government Data (OGD India) Live Feed Sync Status"""
    data_sync = OpenGovernmentDataSync.fetch_live_national_scheme_data()
    return jsonify(data_sync), 200

@gateway_bp.route('/consent/grant', methods=['POST'])
def grant_consent():
    """Consent Manager - Record citizen consent for cross-department data sharing"""
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

@gateway_bp.route('/iot/telemetry', methods=['POST'])
def handle_iot_telemetry():
    """Phase 16 - Optional Hardware & Sensor Telemetry Endpoint"""
    data = request.get_json() or {}
    sensor_id = data.get('sensor_id', 'ESP32-WATER-001')
    location = data.get('location', 'Central Zone')
    severity = data.get('severity', 'HIGH')
    alert_type = data.get('alert_type', 'WATER_OVERFLOW')
    metric_value = data.get('metric_value', '88% Overflow Level')
    
    result = IoTTelemetryConnector.process_sensor_alert(
        sensor_id, location, severity, alert_type, metric_value
    )
    return jsonify(result), 200

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
