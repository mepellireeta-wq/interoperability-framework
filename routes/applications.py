from flask import Blueprint, request, jsonify, session
from database.models import db, Application, WorkflowStep, Department, AuditLog
from services.interop_service import InteroperabilityEngine
from services.mdm_service import MDMService
import json
import random
import string
from datetime import datetime

applications_bp = Blueprint('applications', __name__, url_prefix='/api/v1/applications')

def generate_tracking_id():
    """Generate unique state tracking identifier (e.g. GOV-2026-8A4F)"""
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"GOV-2026-{random_str}"

@applications_bp.route('/submit', methods=['POST'])
def submit_application():
    """Unified Service Application Submission Endpoint"""
    data = request.get_json() or {}
    user_id = session.get('user_id', 1)
    service_code = data.get('service_code', 'UNIFIED_SKILL_TO_GRANT')
    service_title = data.get('service_title', 'Universal Integrated Skill-to-Entrepreneurship Pathway')
    
    # 1. Standardize Data Schema
    standardized_payload = InteroperabilityEngine.standardize_payload(data, service_code)
    
    # 2. Validate Data Quality
    is_valid, errors = InteroperabilityEngine.validate_data_quality(standardized_payload)
    if not is_valid:
        return jsonify({'error': 'Data Quality Check Failed', 'details': errors}), 400
        
    # 3. Master Data Management (MDM) Processing
    beneficiary = standardized_payload['beneficiary']
    state_id_num = beneficiary.get('state_id_number') or f"NAT-ID-{user_id}"
    mdm_profile, is_new = MDMService.get_or_create_master_record(user_id, state_id_num, beneficiary)
    
    # 4. Create Unified Application Record
    tracking_id = generate_tracking_id()
    app_record = Application(
        tracking_id=tracking_id,
        applicant_id=user_id,
        service_code=service_code,
        service_title=service_title,
        status='SUBMITTED',
        payload_json=json.dumps(standardized_payload),
        consent_given=True,
        current_stage=1,
        total_stages=3
    )
    db.session.add(app_record)
    db.session.commit()
    
    # 5. Initialize Multi-Department Workflow Steps
    depts = Department.query.all()
    if not depts:
        dept_ids = [1, 2, 3]
    else:
        dept_ids = [d.id for d in depts]
        
    steps_meta = [
        {'stage': 1, 'name': 'Skill Development Verification', 'dept_id': dept_ids[0] if len(dept_ids)>0 else 1},
        {'stage': 2, 'name': 'Employment Registry Cross-Check', 'dept_id': dept_ids[1] if len(dept_ids)>1 else 2},
        {'stage': 3, 'name': 'Innovation Seed Grant Approval', 'dept_id': dept_ids[2] if len(dept_ids)>2 else 3}
    ]
    
    for meta in steps_meta:
        ws = WorkflowStep(
            application_id=app_record.id,
            department_id=meta['dept_id'],
            stage_number=meta['stage'],
            stage_name=meta['name'],
            status='IN_PROGRESS' if meta['stage'] == 1 else 'PENDING',
            remarks='Awaiting Stage Processing'
        )
        db.session.add(ws)
        
    # Log Audit Record
    audit = AuditLog(
        application_id=app_record.id,
        actor=f"USER_ID:{user_id}",
        action="APPLICATION_SUBMITTED",
        details=f"Submitted tracking ID {tracking_id} under schema {InteroperabilityEngine.SCHEMA_VERSION}"
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({
        'message': 'Application Successfully Submitted & Standardized',
        'tracking_id': tracking_id,
        'application_id': app_record.id,
        'status': app_record.status,
        'mdm_status': 'New Profile Created' if is_new else 'Master Profile Linked',
        'schema_version': InteroperabilityEngine.SCHEMA_VERSION
    }), 201

@applications_bp.route('/track/<tracking_id>', methods=['GET'])
def track_application(tracking_id):
    """Retrieve 360-Degree Unified Application Timeline"""
    app_record = Application.query.filter_by(tracking_id=tracking_id).first()
    if not app_record:
        return jsonify({'error': 'Application not found with given tracking ID'}), 404
        
    steps = WorkflowStep.query.filter_by(application_id=app_record.id).order_by(WorkflowStep.stage_number).all()
    logs = AuditLog.query.filter_by(application_id=app_record.id).order_by(AuditLog.timestamp.desc()).all()
    
    return jsonify({
        'tracking_id': app_record.tracking_id,
        'service_title': app_record.service_title,
        'service_code': app_record.service_code,
        'status': app_record.status,
        'current_stage': app_record.current_stage,
        'total_stages': app_record.total_stages,
        'created_at': app_record.created_at.isoformat(),
        'workflow_timeline': [{
            'stage_number': s.stage_number,
            'stage_name': s.stage_name,
            'department_name': s.department.name if s.department else 'Government Department',
            'status': s.status,
            'remarks': s.remarks,
            'updated_at': s.updated_at.isoformat()
        } for s in steps],
        'audit_logs': [{
            'actor': l.actor,
            'action': l.action,
            'details': l.details,
            'timestamp': l.timestamp.isoformat()
        } for l in logs]
    }), 200

@applications_bp.route('/my-applications', methods=['GET'])
def my_applications():
    """List applications for currently logged-in user"""
    user_id = session.get('user_id', 1)
    apps = Application.query.filter_by(applicant_id=user_id).order_by(Application.created_at.desc()).all()
    
    return jsonify({
        'count': len(apps),
        'applications': [{
            'id': a.id,
            'tracking_id': a.tracking_id,
            'service_title': a.service_title,
            'status': a.status,
            'created_at': a.created_at.isoformat()
        } for a in apps]
    }), 200
