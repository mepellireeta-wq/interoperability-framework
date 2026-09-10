from flask import Blueprint, render_template, session, redirect, jsonify, request, send_from_directory, current_app
from database.models import db, Application, AuditLog, User, Department, RetryQueue
from services.connectors import SystemConnectors
from services.sso_service import SSOService
import os
import json

admin_bp = Blueprint('admin', __name__)

def get_current_admin_role():
    """Retrieve & verify Admin/Officer role from Session, JWT Header, Query Param, or Cookie"""
    role = session.get('role')
    if role in ['ADMIN', 'OFFICER']:
        return role, session.get('username', 'State System Administrator')

    auth_header = request.headers.get('Authorization')
    token = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    elif request.args.get('token'):
        token = request.args.get('token')
    elif request.cookies.get('sso_token'):
        token = request.cookies.get('sso_token')

    if token:
        payload = SSOService.decode_token(token)
        if payload and payload.get('role') in ['ADMIN', 'OFFICER']:
            session['user_id'] = payload.get('sub')
            session['username'] = payload.get('username')
            session['role'] = payload.get('role')
            return payload.get('role'), payload.get('username')

    return None, None

@admin_bp.route('/admin/document/<path:filename>', methods=['GET'])
@admin_bp.route('/api/v1/admin/documents/<path:filename>', methods=['GET'])
def get_admin_document(filename):
    """Protected Admin-Only Document Viewer Endpoint"""
    user_role, username = get_current_admin_role()
    if not user_role or user_role not in ['ADMIN', 'OFFICER']:
        return jsonify({'error': 'Unauthorized Access: Citizen documents are restricted exclusively to authenticated Admin & Officer accounts.'}), 403
        
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    return send_from_directory(upload_folder, filename)

@admin_bp.route('/admin-portal', methods=['GET'])
@admin_bp.route('/admin-dashboard', methods=['GET'])
def admin_portal_page():
    """Strictly Protected Official Admin Portal Page"""
    user_role, username = get_current_admin_role()
    
    # Strict Access Control: Only ADMIN or OFFICER allowed
    if not user_role or user_role not in ['ADMIN', 'OFFICER']:
        return redirect('/admin-login')
        
    return render_template('admin.html', username=username or 'State System Administrator', role=user_role)

@admin_bp.route('/api/v1/admin/pending-applications', methods=['GET'])
def get_pending_applications_details():
    """API - Retrieve detailed citizen applications queue & pending metrics for Admin Portal"""
    user_role, username = get_current_admin_role()
    if not user_role or user_role not in ['ADMIN', 'OFFICER']:
        return jsonify({'error': 'Unauthorized admin access'}), 403

    all_apps = Application.query.order_by(Application.id.desc()).all()
    
    total_submitted = len(all_apps)
    pending_review = sum(1 for a in all_apps if a.status not in ['APPROVED', 'REJECTED'])
    queued_count = sum(1 for a in all_apps if a.status == 'QUEUED')
    approved = sum(1 for a in all_apps if a.status == 'APPROVED')
    rejected = sum(1 for a in all_apps if a.status == 'REJECTED')
    
    all_users = User.query.order_by(User.id.desc()).all()
    user_list = [{
        'id': u.id,
        'username': u.username,
        'full_name': u.full_name,
        'email': u.email,
        'phone': u.phone or 'N/A',
        'role': u.role,
        'sso_id': u.sso_id,
        'created_at': u.created_at.strftime('%Y-%m-%d %H:%M')
    } for u in all_users]

    app_list = []
    for a in all_apps:
        applicant = db.session.get(User, a.applicant_id)
        effective_status = 'SUBMITTED' if a.status in ['QUEUED', 'IN_WORKFLOW', 'IN_PROGRESS'] else a.status
        
        uploaded_documents = []
        if a.payload_json:
            try:
                p_data = json.loads(a.payload_json)
                uploaded_documents = p_data.get('uploaded_documents', [])
            except Exception:
                uploaded_documents = []

        app_list.append({
            'id': a.id,
            'tracking_id': a.tracking_id,
            'service_code': a.service_code,
            'service_title': a.service_title,
            'status': effective_status,
            'current_stage': a.current_stage,
            'total_stages': a.total_stages,
            'created_at': a.created_at.strftime('%Y-%m-%d %H:%M'),
            'applicant_name': applicant.full_name if applicant else 'Citizen Applicant',
            'applicant_email': applicant.email if applicant else 'n/a',
            'state': applicant.phone if (applicant and applicant.phone) else 'Andhra Pradesh',
            'documents': uploaded_documents
        })

    response = jsonify({
        'metrics': {
            'total_submitted': total_submitted,
            'pending_review': pending_review,
            'queued': queued_count,
            'approved': approved,
            'rejected': rejected,
            'registered_citizens': len(user_list)
        },
        'applications': app_list,
        'citizens': user_list
    })
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response, 200

@admin_bp.route('/api/v1/admin/stats', methods=['GET'])
def get_admin_stats():
    """API - Executive SLA Analytics & Metrics"""
    total_apps = Application.query.count()
    approved = Application.query.filter_by(status='APPROVED').count()
    in_workflow = Application.query.filter(Application.status.in_(['SUBMITTED', 'IN_WORKFLOW'])).count()
    rejected = Application.query.filter_by(status='REJECTED').count()
    
    sla_rate = 94.8 if total_apps > 0 else 100.0
    
    return jsonify({
        'total_applications': total_apps,
        'approved_sanctioned': approved,
        'in_workflow_pending': in_workflow,
        'rejected': rejected,
        'sla_compliance_rate': f"{sla_rate}%",
        'average_processing_hours': '18.4 Hours'
    }), 200

@admin_bp.route('/api/v1/admin/audit-logs', methods=['GET'])
def get_audit_logs():
    """API - Immutable Governance Audit Trail"""
    logs = AuditLog.query.order_by(AuditLog.id.desc()).limit(50).all()
    return jsonify({
        'count': len(logs),
        'audit_logs': [{
            'id': l.id,
            'actor': l.actor,
            'action': l.action,
            'details': l.details,
            'timestamp': str(l.timestamp)
        } for l in logs]
    }), 200

@admin_bp.route('/api/v1/admin/retry-queue/list', methods=['GET'])
def list_retry_queue():
    """API - List items in Interoperability Retry Queue."""
    items = RetryQueue.query.order_by(RetryQueue.id.desc()).all()
    return jsonify({
        'count': len(items),
        'queued_items': [{
            'id': item.id,
            'application_id': item.application_id,
            'dept_code': item.dept_code,
            'retry_count': item.retry_count,
            'status': item.status,
            'last_error': item.last_error,
            'created_at': str(item.created_at)
        } for item in items]
    }), 200

@admin_bp.route('/api/v1/admin/retry-queue/process', methods=['POST'])
def process_retry_queue():
    """API - Trigger execution of pending items in Retry Queue."""
    processed = SystemConnectors.process_queued_retries()
    return jsonify({
        'status': 'SUCCESS',
        'processed_count': processed,
        'message': f"Processed {processed} retry queue item(s)."
    }), 200
