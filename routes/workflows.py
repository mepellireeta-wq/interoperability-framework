from flask import Blueprint, request, jsonify, session
from services.workflow_engine import WorkflowEngine
from database.models import Application, WorkflowStep

workflows_bp = Blueprint('workflows', __name__, url_prefix='/api/v1/workflows')

@workflows_bp.route('/advance', methods=['POST'])
def advance_workflow_stage():
    """Advance an application to its next workflow approval stage"""
    data = request.get_json() or {}
    application_id = data.get('application_id')
    decision = data.get('decision', 'APPROVE') # APPROVE or REJECT
    remarks = data.get('remarks', 'Stage Verification Passed')
    officer_name = session.get('username', 'Officer Reviewer')
    
    if not application_id:
        return jsonify({'error': 'Application ID is required'}), 400
        
    success, msg = WorkflowEngine.process_next_stage(application_id, decision, remarks, officer_name)
    if not success:
        return jsonify({'error': msg}), 400
        
    return jsonify({
        'message': msg,
        'application_id': application_id,
        'decision': decision
    }), 200

@workflows_bp.route('/pending', methods=['GET'])
def get_pending_workflows():
    """List applications pending officer review across departments"""
    pending_apps = Application.query.filter(
        Application.status.in_(['SUBMITTED', 'IN_WORKFLOW'])
    ).all()
    
    return jsonify({
        'count': len(pending_apps),
        'pending_applications': [{
            'id': a.id,
            'tracking_id': a.tracking_id,
            'service_title': a.service_title,
            'current_stage': a.current_stage,
            'total_stages': a.total_stages,
            'status': a.status,
            'created_at': a.created_at.isoformat()
        } for a in pending_apps]
    }), 200
