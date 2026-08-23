from flask import Blueprint, request, jsonify
import json

simulated_bp = Blueprint('simulated_depts', __name__, url_prefix='/api/v1/mock')

@simulated_bp.route('/dept-a/skills', methods=['POST'])
def mock_skills_dept():
    """Mock Modern REST API Endpoint - Department of Skills Development"""
    data = request.get_json() or {}
    return jsonify({
        'department': 'Department of Skills Development & Entrepreneurship',
        'status': 'VERIFIED',
        'skills_ack_id': 'SKILLS-2026-9912',
        'message': 'Beneficiary vocational skill records validated successfully.'
    }), 200

@simulated_bp.route('/dept-b/employment', methods=['POST'])
def mock_employment_legacy_dept():
    """Mock Legacy SOAP/XML Endpoint - Directorate of Employment"""
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
    """Mock Direct DB REST Endpoint - Maharashtra State Innovation Society"""
    data = request.get_json() or {}
    return jsonify({
        'department': 'Maharashtra State Innovation Society',
        'status': 'SANCTIONED',
        'grant_id': 'MSINS-2026-GRANT-8821',
        'sanction_amount': '₹ 1,00,000 Seed Grant',
        'message': 'Startup grant sanctioned under Maharashtra Innovation Policy.'
    }), 200
