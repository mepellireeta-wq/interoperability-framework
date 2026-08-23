from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User Identity Model supporting Federated SSO & Role-Based Access"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    sso_id = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='CITIZEN', nullable=False) # CITIZEN, BUSINESS, OFFICER, ADMIN
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='applicant', lazy=True)
    mdm_profile = db.relationship('BeneficiaryMDM', backref='user', uselist=False, lazy=True)

class BeneficiaryMDM(db.Model):
    """Master Data Management (MDM) - Resolved Single Master Profile"""
    __tablename__ = 'beneficiary_mdm'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    state_id_hash = db.Column(db.String(64), unique=True, nullable=False) # Hashed identity key
    master_profile_json = db.Column(db.Text, nullable=False) # Standardized JSON profile
    is_verified = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Department(db.Model):
    """Government Department Registry"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    dept_code = db.Column(db.String(30), unique=True, nullable=False) # e.g. DEPT_SKILLS, DEPT_EMPLOYMENT
    name = db.Column(db.String(150), nullable=False)
    system_type = db.Column(db.String(30), default='REST_API') # REST_API, LEGACY_SOAP, DIRECT_DB
    endpoint_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

class Application(db.Model):
    """Unified Service Application Record"""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(30), unique=True, nullable=False) # e.g. MH-2026-X8F9
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_code = db.Column(db.String(50), nullable=False) # e.g. SKILL_ENTREPRENEURSHIP_GRANT
    service_title = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(30), default='SUBMITTED') # SUBMITTED, IN_WORKFLOW, APPROVED, REJECTED
    payload_json = db.Column(db.Text, nullable=False) # Standardized payload
    consent_given = db.Column(db.Boolean, default=True)
    current_stage = db.Column(db.Integer, default=1)
    total_stages = db.Column(db.Integer, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    steps = db.relationship('WorkflowStep', backref='application', lazy=True, cascade="all, delete-orphan")
    audit_logs = db.relationship('AuditLog', backref='application', lazy=True, cascade="all, delete-orphan")

class WorkflowStep(db.Model):
    """Workflow Engine Approval Stage Execution"""
    __tablename__ = 'workflow_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    stage_number = db.Column(db.Integer, nullable=False)
    stage_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30), default='PENDING') # PENDING, IN_PROGRESS, COMPLETED, REJECTED
    remarks = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    department = db.relationship('Department')

class AuditLog(db.Model):
    """Immutable System Audit Log for Interoperability Compliance"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=True)
    actor = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
