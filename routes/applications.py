import os
import json
import random
import string
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, session, current_app
from database.models import db, Application, WorkflowStep, Department, AuditLog
from services.interop_service import InteroperabilityEngine
from services.mdm_service import MDMService

applications_bp = Blueprint('applications', __name__, url_prefix='/api/v1/applications')

def generate_tracking_id():
    """Generate unique state tracking identifier (e.g. GOV-2026-8A4F)"""
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"GOV-2026-{random_str}"

@applications_bp.route('/submit', methods=['POST'])
def submit_application():
    """Unified Service Application Submission Endpoint with Document Attachments"""
    user_id = session.get('user_id', 1)
    
    # Support both JSON payload and Multipart Form Data (for document uploads)
    if request.content_type and 'multipart/form-data' in request.content_type:
        payload_str = request.form.get('payload', '{}')
        try:
            data = json.loads(payload_str)
        except Exception:
            data = {}
    else:
        data = request.get_json() or {}

    service_code = data.get('service_code', 'UNIFIED_SKILL_TO_GRANT')
    service_title = data.get('service_title', 'Universal Integrated Skill-to-Entrepreneurship Pathway')
    
    # Process Uploaded Sector Documents
    uploaded_docs = []
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
    os.makedirs(upload_folder, exist_ok=True)
    
    for file_key in request.files:
        file = request.files[file_key]
        if file and file.filename:
            filename = secure_filename(f"{int(datetime.utcnow().timestamp())}_{file.filename}")
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            uploaded_docs.append({
                'doc_type': file_key,
                'filename': filename,
                'url': f"/static/uploads/documents/{filename}"
            })
            
    # 1. Standardize Data Schema
    standardized_payload = InteroperabilityEngine.standardize_payload(data, service_code)
    standardized_payload['attached_documents'] = uploaded_docs
    
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
    dept_ids = [d.id for d in depts] if depts else [1, 2, 3]
        
    steps_meta = [
        {'stage': 1, 'name': 'Skill & Sector Verification', 'dept_id': dept_ids[0] if len(dept_ids)>0 else 1},
        {'stage': 2, 'name': 'Registry & Document Cross-Check', 'dept_id': dept_ids[1] if len(dept_ids)>1 else 2},
        {'stage': 3, 'name': 'Final Grant & Sanction Approval', 'dept_id': dept_ids[2] if len(dept_ids)>2 else 3}
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
        details=f"Submitted tracking ID {tracking_id} with {len(uploaded_docs)} attached verification documents"
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({
        'message': 'Application Successfully Submitted & Standardized',
        'tracking_id': tracking_id,
        'application_id': app_record.id,
        'status': app_record.status,
        'attached_documents_count': len(uploaded_docs),
        'mdm_status': 'New Profile Created' if is_new else 'Master Profile Linked',
        'schema_version': InteroperabilityEngine.SCHEMA_VERSION
    }), 201

@applications_bp.route('/track/<tracking_id>', methods=['GET'])
def track_application(tracking_id):
    """Retrieve 360-Degree Unified Application Timeline & Document Verification Details"""
    app_record = Application.query.filter_by(tracking_id=tracking_id).first()
    if not app_record:
        return jsonify({'error': 'Application not found with given tracking ID'}), 404
        
    steps = WorkflowStep.query.filter_by(application_id=app_record.id).order_by(WorkflowStep.stage_number).all()
    logs = AuditLog.query.filter_by(application_id=app_record.id).order_by(AuditLog.timestamp.desc()).all()
    payload = json.loads(app_record.payload_json) if app_record.payload_json else {}
    
    return jsonify({
        'tracking_id': app_record.tracking_id,
        'service_title': app_record.service_title,
        'service_code': app_record.service_code,
        'status': app_record.status,
        'current_stage': app_record.current_stage,
        'total_stages': app_record.total_stages,
        'created_at': app_record.created_at.isoformat(),
        'attached_documents': payload.get('attached_documents', []),
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
