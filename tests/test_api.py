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
