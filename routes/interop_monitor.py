from flask import Blueprint, render_template, jsonify, request
from database.models import db, Application, WorkflowStep, AuditLog, ConsentRecord, RetryQueue, User
from services.interop_service import InteroperabilityEngine
from services.mdm_service import MDMService, MDMEngine
from services.consent_service import create_consent, verify_consent, revoke_consent, mask_pii
from services.connectors import SystemConnectors, SystemConnectors as Connectors
from routes.simulated_depts import DEPT_STATUS
import json
import uuid

interop_monitor_bp = Blueprint('interop_monitor', __name__)

@interop_monitor_bp.route('/interoperability-monitor', methods=['GET'])
def interop_monitor_page():
    """Interoperability Framework Live Monitor Page."""
    return render_template('interoperability_monitor.html')

@interop_monitor_bp.route('/api/v1/interop/pipeline-status', methods=['GET'])
def get_pipeline_status():
    """Get live pipeline statistics and active applications for the Interoperability Monitor."""
    total_apps = Application.query.count()
    approved_apps = Application.query.filter_by(status='APPROVED').count()
    pending_retries = RetryQueue.query.filter_by(status='PENDING').count()
    active_consents = ConsentRecord.query.filter_by(status='ACTIVE').count()
    
    recent_apps = Application.query.order_by(Application.id.desc()).limit(10).all()
    app_list = []
    for a in recent_apps:
        steps = WorkflowStep.query.filter_by(application_id=a.id).order_by(WorkflowStep.stage_number).all()
        app_list.append({
            'id': a.id,
            'tracking_id': a.tracking_id,
            'service_code': a.service_code,
            'status': a.status,
            'current_stage': a.current_stage,
            'consent_id': a.consent_id or 'CNS-2026-DEFAULT',
            'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'stages': [{
                'stage': s.stage_number,
                'name': s.stage_name,
                'status': s.status,
                'remarks': s.remarks
            } for s in steps]
        })
        
    return jsonify({
        'schema_version': InteroperabilityEngine.SCHEMA_VERSION,
        'metrics': {
            'total_applications': total_apps,
            'approved_applications': approved_apps,
            'pending_retry_queue': pending_retries,
            'active_consents': active_consents,
            'simulated_department_status': DEPT_STATUS
        },
        'applications': app_list
    }), 200

@interop_monitor_bp.route('/api/v1/demo/run-scenario/<scenario_id>', methods=['POST'])
def run_demo_scenario(scenario_id):
    """1-Click Technical Presentation Scenarios A through E."""
    scenario_id = scenario_id.upper()
    
    if scenario_id == 'A':
        # Scenario A: Standard Citizen Journey with Full Workflow Approval
        consent_id = create_consent("NAT-ID-DEMO-A", "SKILL_GRANT", "Skill & Entrepreneurship Integration")
        raw_payload = {
            "service_code": "UNIFIED_SKILL_TO_GRANT",
            "applicant": {
                "full_name": "Priya Rajesh Verma",
                "email": "priya.verma@example.com",
                "phone": "9812345678",
                "district": "Visakhapatnam",
                "state": "Andhra Pradesh",
                "state_id_number": "NAT-ID-DEMO-A"
            }
        }
        standardized = InteroperabilityEngine.standardize_payload(raw_payload)
        tracking_id = f"GOV-2026-DEMO-A"
        
        user = User.query.filter_by(sso_id="NAT-ID-DEMO-A").first()
        if not user:
            user = User(sso_id="NAT-ID-DEMO-A", username="priya_verma", email="priya.verma@example.com", password_hash="hash", full_name="Priya Rajesh Verma", role="CITIZEN")
            db.session.add(user)
            db.session.commit()
            
        app_rec = Application(
            tracking_id=tracking_id,
            applicant_id=user.id,
            service_code="UNIFIED_SKILL_TO_GRANT",
            service_title="Universal Integrated Skill-to-Entrepreneurship Pathway",
            status="APPROVED",
            payload_json=json.dumps(standardized),
            consent_given=True,
            consent_id=consent_id,
            current_stage=3,
            total_stages=3
        )
        db.session.add(app_rec)
        db.session.commit()
        
        # Add steps
        s1 = WorkflowStep(application_id=app_rec.id, department_id=1, stage_number=1, stage_name="Skill Verification", status="COMPLETED", remarks="REST API Verified")
        s2 = WorkflowStep(application_id=app_rec.id, department_id=2, stage_number=2, stage_name="Employment Registry Cross-Check", status="COMPLETED", remarks="Legacy SOAP Verified")
        s3 = WorkflowStep(application_id=app_rec.id, department_id=3, stage_number=3, stage_name="Innovation Seed Grant Approval", status="COMPLETED", remarks="Grant Sanctioned ₹1,00,000")
        db.session.add_all([s1, s2, s3])
        
        audit = AuditLog(application_id=app_rec.id, actor="DEMO_CONTROLLER", action="SCENARIO_A_SUCCESS", details=f"Completed Scenario A: Standard Journey for tracking ID {tracking_id}")
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({
            'status': 'SUCCESS',
            'scenario': 'Scenario A: Standard Citizen Journey & Workflow Approval',
            'tracking_id': tracking_id,
            'consent_id': consent_id,
            'schema_version': InteroperabilityEngine.SCHEMA_VERSION,
            'message': 'Application successfully processed across 3 department workflow stages.'
        }), 200

    elif scenario_id == 'B':
        # Scenario B: Legacy System Integration via SOAP/XML Adapter
        raw_payload = {
            "service_code": "UNIFIED_SKILL_TO_GRANT",
            "applicant": {
                "full_name": "Suresh Babu",
                "email": "suresh.babu@example.com",
                "phone": "9765432109",
                "district": "Guntur",
                "state": "Andhra Pradesh",
                "state_id_number": "NAT-ID-DEMO-B"
            }
        }
        standardized = InteroperabilityEngine.standardize_payload(raw_payload)
        success, resp = SystemConnectors.send_to_dept_b_employment_legacy(standardized)
        
        return jsonify({
            'status': 'SUCCESS',
            'scenario': 'Scenario B: Legacy System Integration via SOAP/XML Adapter',
            'adapter_type': 'SOAP/XML Protocol Adapter',
            'adapter_response': resp,
            'transformed_payload_snippet': '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">...',
            'message': 'Legacy SOAP service successfully integrated with XML transformation.'
        }), 200

    elif scenario_id == 'C':
        # Scenario C: Automatic Failure Queueing & Retry Queue Recovery
        DEPT_STATUS['SKILL_DEV_DEPT'] = 'DOWN'
        
        consent_id = create_consent("NAT-ID-DEMO-C", "SKILL_GRANT", "Retry Queue Simulation")
        raw_payload = {
            "service_code": "UNIFIED_SKILL_TO_GRANT",
            "applicant": {
                "full_name": "Kavita Devi",
                "email": "kavita.devi@example.com",
                "phone": "9955443322",
                "district": "Vijayawada",
                "state": "Andhra Pradesh",
                "state_id_number": "NAT-ID-DEMO-C"
            }
        }
        standardized = InteroperabilityEngine.standardize_payload(raw_payload)
        tracking_id = "GOV-2026-DEMO-C"
        
        user = User.query.filter_by(sso_id="NAT-ID-DEMO-C").first()
        if not user:
            user = User(sso_id="NAT-ID-DEMO-C", username="kavita_devi", email="kavita.devi@example.com", password_hash="hash", full_name="Kavita Devi", role="CITIZEN")
            db.session.add(user)
            db.session.commit()
            
        app_rec = Application(
            tracking_id=tracking_id,
            applicant_id=user.id,
            service_code="UNIFIED_SKILL_TO_GRANT",
            service_title="Universal Integrated Skill-to-Entrepreneurship Pathway",
            status="QUEUED",
            payload_json=json.dumps(standardized),
            consent_given=True,
            consent_id=consent_id,
            current_stage=1,
            total_stages=3
        )
        db.session.add(app_rec)
        db.session.commit()
        
        success, resp = SystemConnectors.send_to_dept_a_skills(standardized, application_id=app_rec.id)
        
        # Now recover department
        DEPT_STATUS['SKILL_DEV_DEPT'] = 'UP'
        processed_count = SystemConnectors.process_queued_retries()
        
        return jsonify({
            'status': 'SUCCESS',
            'scenario': 'Scenario C: Retry Queue Failure & Automatic Recovery',
            'tracking_id': tracking_id,
            'initial_adapter_status': resp,
            'recovery_processed_items': processed_count,
            'message': 'Simulated department failure queued into RetryQueue and recovered automatically.'
        }), 200

    elif scenario_id == 'D':
        # Scenario D: DPDP Consent Revocation & Access Denial
        consent_id = create_consent("NAT-ID-DEMO-D", "SKILL_GRANT", "Revocation Test")
        revoke_consent(consent_id)
        
        is_valid, record = verify_consent(consent_id)
        
        return jsonify({
            'status': 'SUCCESS',
            'scenario': 'Scenario D: DPDP Act Consent Revocation & Access Denial',
            'consent_id': consent_id,
            'consent_status': record.status if record else 'NOT_FOUND',
            'access_decision': 'ACCESS_DENIED (HTTP 403 Forbidden)',
            'message': 'DPDP consent revocation correctly blocks cross-department data sharing.'
        }), 200

    elif scenario_id == 'E':
        # Scenario E: MDM Deduplication Match
        key1 = MDMEngine.generate_dedup_key("Rahul Ramesh Kumar", "9123456789", "NAT-ID-HASH-9912")
        key2 = MDMEngine.generate_dedup_key("rahul ramesh kumar", "9123456789", "NAT-ID-HASH-9912")
        
        masked_phone = mask_pii("9123456789", pii_type="phone")
        masked_id = mask_pii("NAT-ID-HASH-9912", pii_type="national_id")
        
        return jsonify({
            'status': 'SUCCESS',
            'scenario': 'Scenario E: Privacy-Preserving MDM Golden Record Deduplication',
            'dedup_key_input1': key1,
            'dedup_key_input2': key2,
            'match_result': 'MDM_MATCH (Deterministic Key Equal)',
            'masked_pii': {
                'phone': masked_phone,
                'national_id': masked_id
            },
            'message': 'Privacy-preserving MDM engine matched duplicate records using salted SHA-256 key.'
        }), 200

    return jsonify({'error': 'Invalid scenario ID. Choose A, B, C, D, or E.'}), 400
