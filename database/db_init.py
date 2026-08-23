import sys
import os
import json
import hashlib
from werkzeug.security import generate_password_hash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.models import db, User, Department, BeneficiaryMDM, Application, WorkflowStep, AuditLog

def init_db():
    """Seed initial data into SQLite database"""
    app = create_app('dev')
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()
        
        # 1. Seed Default Admin & Sample Citizen Users
        if not User.query.filter_by(username='admin').first():
            print("Seeding Default Admin & Officer Accounts...")
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
            
            # Create Beneficiary Master Data (MDM) profile for Rahul
            state_hash = hashlib.sha256('NAT-ID-9988'.encode()).hexdigest()
            mdm_profile = BeneficiaryMDM(
                user_id=citizen_user.id,
                state_id_hash=state_hash,
                master_profile_json=json.dumps({
                    'full_name': 'Rahul Kumar',
                    'dob': '1998-05-14',
                    'district': 'Central Zone',
                    'state': 'National Jurisdiction',
                    'qualification': 'Graduate in Engineering',
                    'category': 'General'
                }),
                is_verified=True
            )
            db.session.add(mdm_profile)
            db.session.commit()
            print("Users and MDM profiles seeded.")
            
        # 2. Seed Government Departments
        if not Department.query.first():
            print("Seeding Government Departments...")
            dept_a = Department(
                dept_code='DEPT_SKILLS',
                name='Department of Skills & Vocational Development',
                system_type='REST_API',
                endpoint_url='http://127.0.0.1:5001/api/v1/skills'
            )
            
            dept_b = Department(
                dept_code='DEPT_EMPLOYMENT',
                name='Directorate of Employment & Self Employment',
                system_type='LEGACY_SOAP',
                endpoint_url='http://127.0.0.1:5002/soap/employment'
            )
            
            dept_c = Department(
                dept_code='DEPT_ENTREPRENEURSHIP',
                name='State & National Startup Innovation Society',
                system_type='DIRECT_DB',
                endpoint_url='http://127.0.0.1:5003/db/innovation'
            )
            
            db.session.add_all([dept_a, dept_b, dept_c])
            db.session.commit()
            print("Departments seeded.")
            
        print("Database initialization complete!")

if __name__ == '__main__':
    init_db()
