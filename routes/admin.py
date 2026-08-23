from flask import Blueprint, request, jsonify, session
from database.models import db, Application, WorkflowStep, Department, AuditLog
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

@admin_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Retrieve System-Wide Executive Interoperability Metrics & SLA Analytics"""
    total_apps = Application.query.count()
    submitted_apps = Application.query.filter_by(status='SUBMITTED').count()
    in_workflow_apps = Application.query.filter_by(status='IN_WORKFLOW').count()
    approved_apps = Application.query.filter_by(status='APPROVED').count()
    rejected_apps = Application.query.filter_by(status='REJECTED').count()
    
    # Calculate SLA Warning Thresholds (Created > 48 hours ago)
    sla_cutoff = datetime.utcnow() - timedelta(hours=48)
    sla_warning_count = Application.query.filter(
        Application.status.in_(['SUBMITTED', 'IN_WORKFLOW']),
        Application.created_at < sla_cutoff
    ).count()
    
    sla_compliance_rate = round(((total_apps - sla_warning_count) / max(total_apps, 1)) * 100, 1)
    
    return jsonify({
        'total_applications': total_apps,
        'submitted': submitted_apps,
        'in_workflow': in_workflow_apps,
        'approved': approved_apps,
        'rejected': rejected_apps,
        'sla_warnings': sla_warning_count,
        'sla_compliance_rate': f"{sla_compliance_rate}%",
        'active_departments': Department.query.filter_by(is_active=True).count()
    }), 200

@admin_bp.route('/audit-logs', methods=['GET'])
def get_audit_logs():
    """Retrieve Immutable Governance Audit Log Entries"""
    limit = request.args.get('limit', 50, type=int)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    return jsonify({
        'count': len(logs),
        'audit_logs': [{
            'id': l.id,
            'application_id': l.application_id,
            'actor': l.actor,
            'action': l.action,
            'details': l.details,
            'timestamp': l.timestamp.isoformat()
        } for l in logs]
    }), 200

@admin_bp.route('/sla-monitoring', methods=['GET'])
def get_sla_monitoring():
    """Department-wise SLA Compliance & Performance Metrics"""
    depts = Department.query.all()
    dept_metrics = []
    
    for d in depts:
        steps_total = WorkflowStep.query.filter_by(department_id=d.id).count()
        steps_completed = WorkflowStep.query.filter_by(department_id=d.id, status='COMPLETED').count()
        steps_pending = WorkflowStep.query.filter_by(department_id=d.id, status='IN_PROGRESS').count()
        
        dept_metrics.append({
            'department_name': d.name,
            'dept_code': d.dept_code,
            'system_type': d.system_type,
            'total_assigned_steps': steps_total,
            'completed': steps_completed,
            'pending': steps_pending,
            'efficiency_rate': f"{round((steps_completed / max(steps_total, 1)) * 100, 1)}%"
        })
        
    return jsonify({
        'department_count': len(dept_metrics),
        'department_metrics': dept_metrics
    }), 200
