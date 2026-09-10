from flask import Blueprint, request, jsonify
import json

simulated_bp = Blueprint('simulated_depts', __name__, url_prefix='/api/v1/mock')

# Live demo simulated department health state tracking
DEPT_STATUS = {
    'SKILL_DEV_DEPT': 'UP',
    'EMPLOYMENT_DEPT': 'UP',
    'INNOVATION_DEPT': 'UP'
}

@simulated_bp.route('/demo/toggle-status', methods=['POST'])
def toggle_department_status():
    """Toggle simulated department operational status for testing and live demonstrations."""
    data = request.get_json() or {}
    dept = data.get('department', 'SKILL_DEV_DEPT')
    status = data.get('status', 'UP').upper()
    DEPT_STATUS[dept] = status
    return jsonify({
        'status': 'SUCCESS',
        'department': dept,
        'operational_status': status,
        'message': f"Simulated Department {dept} status set to {status}"
    }), 200

@simulated_bp.route('/demo/status', methods=['GET'])
def get_department_statuses():
    """Get status of all simulated departmental systems."""
    return jsonify({
        'system_label': 'Simulated Departmental Systems',
        'statuses': DEPT_STATUS
    }), 200

@simulated_bp.route('/dept-a/skills', methods=['POST'])
def mock_skills_dept():
    """Simulated Departmental System - Department of Skills Development & Entrepreneurship (REST API)"""
    if DEPT_STATUS.get('SKILL_DEV_DEPT') == 'DOWN':
        return jsonify({'error': 'Simulated Department System Down', 'code': 'DEPT_UNAVAILABLE'}), 503
        
    data = request.get_json() or {}
    return jsonify({
        'system_type': 'Simulated Departmental System (REST API)',
        'department': 'Department of Skills Development & Entrepreneurship',
        'status': 'VERIFIED',
        'skills_ack_id': 'SKILLS-2026-9912',
        'message': 'Beneficiary vocational skill records validated successfully.'
    }), 200

@simulated_bp.route('/dept-b/employment', methods=['POST'])
def mock_employment_legacy_dept():
    """Simulated Departmental System - Directorate of Employment (Legacy SOAP/XML)"""
    if DEPT_STATUS.get('EMPLOYMENT_DEPT') == 'DOWN':
        return jsonify({'error': 'Simulated Department System Down', 'code': 'DEPT_UNAVAILABLE'}), 503
        
    xml_data = request.data.decode('utf-8') if request.data else ''
    response_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
       <soapenv:Body>
          <emp:RegisterEligibilityResponse>
             <emp:Status>APPROVED</emp:Status>
             <emp:CMEGPEligibility>TRUE</emp:CMEGPEligibility>
          </emp:RegisterEligibilityResponse>
       </soapenv:Body>
    </soapenv:Envelope>"""
    return response_xml, 200, {'Content-Type': 'text/xml'}

@simulated_bp.route('/dept-c/innovation', methods=['POST'])
def mock_innovation_dept():
    """Simulated Departmental System - State Innovation Society (Direct DB API)"""
    if DEPT_STATUS.get('INNOVATION_DEPT') == 'DOWN':
        return jsonify({'error': 'Simulated Department System Down', 'code': 'DEPT_UNAVAILABLE'}), 503
        
    data = request.get_json() or {}
    return jsonify({
        'system_type': 'Simulated Departmental System (Direct DB API)',
        'department': 'State Innovation Society',
        'status': 'SANCTIONED',
        'grant_id': 'INNOV-2026-GRANT-8821',
        'sanction_amount': '₹ 1,00,000 Seed Grant',
        'message': 'Startup grant sanctioned under Innovation Policy.'
    }), 200
