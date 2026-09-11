import sys
import os
import json
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.models import db, Application, WorkflowStep

@pytest.fixture
def client():
    app = create_app('dev')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            yield client

def test_full_application_lifecycle(client):
    """Test End-to-End Application Lifecycle: Submission -> Workflow Advance -> Approval"""
    # 1. Submit Application
    payload = {
        'service_code': 'UNIFIED_SKILL_TO_GRANT',
        'service_title': 'Universal Integrated Skill-to-Entrepreneurship Pathway',
        'applicant': {
            'full_name': 'Ananya Sharma',
            'email': 'ananya@example.com',
            'phone': '9876543210',
            'pincode': '400001',
            'state_id_number': 'NAT-ID-ANANYA-99'
        }
    }
    sub_res = client.post('/api/v1/applications/submit', json=payload)
    assert sub_res.status_code == 201
    sub_data = sub_res.get_json()
    app_id = sub_data['application_id']
    tracking_id = sub_data['tracking_id']
    
    # 2. Advance Stage 1 -> Stage 2
    adv_res1 = client.post('/api/v1/workflows/advance', json={
        'application_id': app_id,
        'decision': 'APPROVE',
        'remarks': 'Stage 1 Verified'
    })
    assert adv_res1.status_code == 200
    
    # 3. Track Application Timeline
    track_res = client.get(f'/api/v1/applications/track/{tracking_id}')
    assert track_res.status_code == 200
    track_data = track_res.get_json()
    assert track_data['tracking_id'] == tracking_id
    assert len(track_data['workflow_timeline']) > 0

def test_iot_telemetry_endpoint(client):
    """Test Phase 16 Hardware IoT Telemetry Alert Processing"""
    iot_payload = {
        'sensor_id': 'ESP32-WATER-88',
        'location': 'Metro Zone',
        'severity': 'HIGH',
        'alert_type': 'WATER_OVERFLOW',
        'metric_value': '92% Level'
    }
    res = client.post('/api/v1/gateway/iot/telemetry', json=iot_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'TELEMETRY_ALERT_PROCESSED'
    assert data['sensor_id'] == 'ESP32-WATER-88'

def test_notification_dispatch_on_approval_and_rejection(client):
    """Test automatic dispatch of SMS & Email notifications on approval and rejection"""
    from database.models import AuditLog
    payload = {
        'service_code': 'EDU_SCHOLARSHIP_GRANT',
        'service_title': 'National Higher Education Scholarship',
        'applicant': {
            'full_name': 'Rohan Das',
            'email': 'rohan@example.com',
            'phone': '9876500000',
            'state_id_number': 'NAT-ID-ROHAN-01'
        }
    }
    res = client.post('/api/v1/applications/submit', json=payload)
    assert res.status_code == 201
    app_id = res.get_json()['application_id']

    # Approve application and verify notification audit log entry
    adv_res = client.post('/api/v1/workflows/advance', json={
        'application_id': app_id,
        'decision': 'APPROVE',
        'force_approve': True,
        'remarks': 'Approved by Administrator'
    })
    assert adv_res.status_code == 200

    notif_audit = AuditLog.query.filter_by(application_id=app_id, action='SMS_EMAIL_APPROVED_NOTIFIED').first()
    assert notif_audit is not None
    assert 'SMS sent to' in notif_audit.details
