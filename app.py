import os
from flask import Flask, jsonify, render_template, request
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

def create_app(config_name='dev'):
    """Flask Application Factory for Universal Government Interoperability Middleware"""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    
    app.config.from_object(config_by_name[config_name])
    
    # Initialize Database Extension
    db.init_app(app)
    
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
                'Blockchain_Verifier', 'AI_Chatbot_Assistant', 'State_Localization'
            ],
            'version': '1.0.0-SIH'
        }), 200
    
    # Template View Routes
    @app.route('/', methods=['GET'])
    def home():
        return render_template('index.html')

    @app.route('/schemes', methods=['GET'])
    def schemes_page():
        return render_template('schemes.html')

    @app.route('/governance', methods=['GET'])
    def governance_page():
        return render_template('governance.html')

    @app.route('/apply-page', methods=['GET'])
    def apply_page():
        return render_template('apply.html')

    @app.route('/track-page', methods=['GET'])
    def track_page():
        tracking_id = request.args.get('id', '')
        return render_template('track.html', tracking_id=tracking_id)

    @app.route('/admin-dashboard', methods=['GET'])
    def admin_dashboard():
        return render_template('admin.html')
        
    return app

app = create_app(os.getenv('FLASK_ENV', 'dev'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
