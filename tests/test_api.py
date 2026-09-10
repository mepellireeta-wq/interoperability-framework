import sys
import os
import json
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.models import db, User, Application

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

def test_health_check(client):
    """Test Health Check Endpoint"""
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'active'

def test_service_discovery(client):
    """Test Service Discovery Registry Endpoint"""
    res = client.get('/api/v1/gateway/services')
    assert res.status_code == 200
    data = res.get_json()
    assert data['count'] > 0

def test_application_submission(client):
    """Test Unified Application Submission and Standardization"""
    payload = {
        'service_code': 'UNIFIED_SKILL_TO_GRANT',
        'service_title': 'Universal Integrated Skill-to-Entrepreneurship Pathway',
        'applicant': {
            'full_name': 'Test Citizen',
            'email': 'test@example.com',
            'phone': '9988776655',
            'state_id_number': 'NAT-ID-TEST-001'
        }
    }
    res = client.post('/api/v1/applications/submit', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert 'tracking_id' in data
    assert data['tracking_id'].startswith('GOV-2026-')

def test_document_upload_and_admin_access(client):
    """Test multipart file uploads and strict admin-only document access policy"""
    from io import BytesIO
    data = {
        'service_code': 'EDU_SCHOLARSHIP_GRANT',
        'service_title': 'National Merit Scholarship',
        'full_name': 'Ananya Sharma',
        'email': 'ananya@example.com',
        'phone': '9876543210',
        'doc_marks_memo': (BytesIO(b'Sample 10th Marks Memo PDF Content'), 'marks_memo.pdf')
    }
    res = client.post('/api/v1/applications/submit', data=data, content_type='multipart/form-data')
    assert res.status_code == 201
    res_data = res.get_json()
    assert 'tracking_id' in res_data

    # Unauthenticated document view attempt must return 403
    unauth_res = client.get('/admin/document/doc_marks_memo_1_123_marks_memo.pdf')
    assert unauth_res.status_code == 403

