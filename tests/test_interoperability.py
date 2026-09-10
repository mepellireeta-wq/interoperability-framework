import sys
import os
import json
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.models import db, User, Application, ConsentRecord, RetryQueue, WorkflowStep, AuditLog
from services.consent_service import create_consent, verify_consent, mask_pii
from services.interop_service import InteroperabilityEngine
from services.mdm_service import MDMEngine
from services.connectors import SystemConnectors

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

def test_canonical_data_contract(client):
    """Test E-GOV-STD-INTEROP-2026 canonical schema standardization and validation."""
    raw_input = {
        "service_code": "UNIFIED_SKILL_TO_GRANT",
        "beneficiary": {
            "full_name": "Rahul Ramesh Kumar",
            "email": "rahul.kumar@example.com",
            "phone": "9123456789",
            "district": "Visakhapatnam",
            "state": "Andhra Pradesh",
            "state_id_type": "NATIONAL_ID",
            "state_id_hash": "a4f91c8812e99b01247d519bca8817ff8199201a0812b18991aa671991c019a8"
        },
        "security_metadata": {
            "quantum_signature": "Q-SIG-9912A88F",
            "dpdp_consent_granted": True,
            "ip_address": "127.0.0.1"
        }
    }
    
    canonical = InteroperabilityEngine.standardize_payload(raw_input)
    assert canonical["schema_version"] == "E-GOV-STD-INTEROP-2026"
    assert canonical["beneficiary"]["district"] == "Visakhapatnam"
    
    val_res = InteroperabilityEngine.validate_payload(canonical)
    assert val_res["is_valid"] is True

def test_consent_service_and_pii_masking(client):
    """Test consent verification under DPDP Act 2023 and PII masking."""
    consent_id = create_consent(
        citizen_id="NAT-ID-TEST-123",
        scope="SKILL_GRANT_INTEGRATION",
        purpose="Cross-Department Verification"
    )
    assert consent_id.startswith("CNS-2026-")
    
    is_valid, record = verify_consent(consent_id)
    assert is_valid is True
    assert record.status == "ACTIVE"
    
    masked_phone = mask_pii("9123456789", pii_type="phone")
    assert masked_phone == "91*****789"
    
    masked_aadhaar = mask_pii("123456789012", pii_type="aadhaar")
    assert masked_aadhaar == "XXXX-XXXX-9012"

def test_mdm_deduplication(client):
    """Test privacy-preserving deterministic deduplication key generation."""
    key1 = MDMEngine.generate_dedup_key("Rahul Ramesh Kumar", "9123456789", "a4f91c8812e99b01247d519bca8817ff8199201a0812b18991aa671991c019a8")
    key2 = MDMEngine.generate_dedup_key("rahul ramesh kumar", "9123456789", "a4f91c8812e99b01247d519bca8817ff8199201a0812b18991aa671991c019a8")
    assert key1 == key2

def test_retry_queue_and_recovery(client):
    """Test failure handling when simulated department is DOWN and recovery via RetryQueue."""
    # 1. Toggle simulated department to DOWN
    client.post('/api/v1/mock/demo/toggle-status', json={'department': 'SKILL_DEV_DEPT', 'status': 'DOWN'})
    
    payload = {
        'service_code': 'UNIFIED_SKILL_TO_GRANT',
        'service_title': 'Universal Integrated Skill-to-Entrepreneurship Pathway',
        'applicant': {
            'full_name': 'Retry Test User',
            'email': 'retry@example.com',
            'phone': '9988776655',
            'state_id_number': 'NAT-ID-RETRY-001'
        }
    }
    
    res = client.post('/api/v1/applications/submit', json=payload)
    assert res.status_code == 201
    
    # 2. Check retry queue count
    queue_res = client.get('/api/v1/admin/retry-queue/list')
    assert queue_res.status_code == 200
    queue_data = queue_res.get_json()
    assert len(queue_data['queued_items']) >= 1
    
    # 3. Toggle department back to UP and process retry queue
    client.post('/api/v1/mock/demo/toggle-status', json={'department': 'SKILL_DEV_DEPT', 'status': 'UP'})
    proc_res = client.post('/api/v1/admin/retry-queue/process')
    assert proc_res.status_code == 200
    proc_data = proc_res.get_json()
    assert proc_data['processed_count'] >= 1

def test_demo_scenarios(client):
    """Test 1-Click Demo Presentation Scenarios A through E."""
    for scenario_id in ['A', 'B', 'C', 'D', 'E']:
        res = client.post(f'/api/v1/demo/run-scenario/{scenario_id}')
        assert res.status_code == 200
        data = res.get_json()
        assert data['status'] == 'SUCCESS'
        assert 'scenario' in data
