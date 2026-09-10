import os
from flask import Flask, jsonify, render_template, request, session, redirect
from config import config_by_name
from database.models import db
from routes.auth import auth_bp
from routes.gateway import gateway_bp
from routes.applications import applications_bp
from routes.workflows import workflows_bp
from routes.simulated_depts import simulated_bp
from routes.admin import admin_bp
from routes.ai_chat import ai_chat_bp
from routes.blockchain import blockchain_bp
from routes.developer import developer_bp
from routes.citizen import citizen_bp
from routes.interop_monitor import interop_monitor_bp

def create_app(config_name='dev'):
    """Flask Application Factory for Universal Government Interoperability Middleware"""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    
    app.config.from_object(config_by_name[config_name])
    
    # Initialize Database Extension
    db.init_app(app)
    
    # Ensure database schema and seed users exist
    with app.app_context():
        try:
            db.create_all()
            from database.models import User
            from werkzeug.security import generate_password_hash
            if not User.query.filter_by(username='admin').first():
                admin_user = User(
                    sso_id='SSO-GOV-NAT-001',
                    username='admin',
                    email='admin@interop.gov.in',
                    password_hash=generate_password_hash('Admin@123'),
                    role='ADMIN',
                    full_name='System Governance Administrator',
                    phone='9876543210'
                )
                officer_user = User(
                    sso_id='SSO-GOV-NAT-002',
                    username='officer_skills',
                    email='officer@skills.interop.gov.in',
                    password_hash=generate_password_hash('Officer@123'),
                    role='OFFICER',
                    full_name='Skills Review Officer',
                    phone='9876543211'
                )
                citizen_user = User(
                    sso_id='SSO-CITIZEN-NAT-101',
                    username='citizen_demo',
                    email='citizen@example.com',
                    password_hash=generate_password_hash('Citizen@123'),
                    role='CITIZEN',
                    full_name='Rahul Kumar',
                    phone='9123456789'
                )
                db.session.add_all([admin_user, officer_user, citizen_user])
                db.session.commit()
        except Exception as e:
            db.session.rollback()
    
    # Ensure necessary folders exist
    os.makedirs(os.path.join(app.root_path, 'database'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'uploads'), exist_ok=True)
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(gateway_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(workflows_bp)
    app.register_blueprint(simulated_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_chat_bp)
    app.register_blueprint(blockchain_bp)
    app.register_blueprint(developer_bp)
    app.register_blueprint(citizen_bp)
    app.register_blueprint(interop_monitor_bp)
    
    # Health Check API
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'active',
            'middleware': 'Universal Government Interoperability & Federated Service Delivery Framework',
            'active_modules': [
                'SSO_Auth', 'API_Gateway', 'Service_Discovery', 
                'Consent_Manager', 'Data_Standardization', 'MDM_Deduplication',
                'Unified_Applications', 'Workflow_Engine', 'Department_Connectors',
                'Legacy_SOAP_Adapters', 'Event_Bus', 'Audit_Logs', 'SLA_Analytics',
                'Blockchain_Verifier', 'AI_Chatbot_Assistant', 'State_Localization',
                'Developer_Tech_Portal', 'Citizen_Portal', 'Role_Separation'
            ],
            'version': '1.0.0-SIH'
        }), 200
    
    # Template View Routes
    @app.route('/', methods=['GET'])
    def home():
        return render_template('index.html')

    @app.route('/login-page', methods=['GET'])
    def login_page():
        return render_template('login.html')

    @app.route('/admin-login', methods=['GET', 'POST'])
    @app.route('/admin-login-page', methods=['GET', 'POST'])
    def admin_login_page():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            from services.sso_service import SSOService
            user = SSOService.authenticate(username, password)
            if user and user.role in ['ADMIN', 'OFFICER']:
                token = SSOService.generate_token(user)
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                res = redirect(f'/admin-portal?token={token}')
                res.set_cookie('sso_token', token, max_age=43200)
                return res
        return render_template('admin_login.html')

    @app.route('/register-page', methods=['GET'])
    def register_page():
        return render_template('register.html')

    @app.route('/schemes', methods=['GET'])
    def schemes_page():
        user = None
        user_id = session.get('user_id')
        if user_id:
            from database.models import User
            user = db.session.get(User, user_id)
        return render_template('schemes.html', user=user)

    @app.route('/governance', methods=['GET'])
    def governance_page():
        return render_template('governance.html')

    @app.route('/apply-page', methods=['GET'])
    def apply_page():
        user_id = session.get('user_id')
        if user_id:
            from database.models import User
            user = db.session.get(User, user_id)
            if not user:
                session.clear()
                user_id = None
                
        if not user_id:
            return redirect('/login-page?required=true')
            
        selected_service = request.args.get('service', 'UNIFIED_SKILL_TO_GRANT')
        return render_template('apply.html', user=user, selected_service=selected_service)

    @app.route('/track-page', methods=['GET'])
    def track_page():
        tracking_id = request.args.get('id', '')
        return render_template('track.html', tracking_id=tracking_id)

    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return app

app = create_app(os.getenv('FLASK_ENV', 'dev'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
