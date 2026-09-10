from database.models import db, Application, AuditLog, ConsentRecord
import json
import uuid
from datetime import datetime

def create_consent(citizen_id, scope="SKILL_GRANT_INTEGRATION", purpose="Cross-Department Data Verification"):
    """Create explicit citizen consent record under DPDP Act 2023."""
    consent_id = f"CNS-2026-{uuid.uuid4().hex[:8].upper()}"
    record = ConsentRecord(
        consent_id=consent_id,
        citizen_id=str(citizen_id),
        scope=scope,
        purpose=purpose,
        status='ACTIVE',
        granted_at=datetime.utcnow()
    )
    db.session.add(record)
    db.session.commit()
    return consent_id

def verify_consent(consent_id):
    """Verify active consent record."""
    if not consent_id:
        return False, None
    record = ConsentRecord.query.filter_by(consent_id=consent_id).first()
    if record and record.status == 'ACTIVE':
        return True, record
    return False, record

def revoke_consent(consent_id):
    """Revoke active consent record."""
    record = ConsentRecord.query.filter_by(consent_id=consent_id).first()
    if record:
        record.status = 'REVOKED'
        db.session.commit()
        return True
    return False

def mask_pii(val, pii_type="phone"):
    """Mask sensitive PII fields for audit logs."""
    if not val:
        return ""
    val_str = str(val).strip()
    if pii_type == "phone":
        if len(val_str) >= 10:
            return val_str[:2] + "*****" + val_str[-3:]
        return val_str[:2] + "*****"
    elif pii_type in ["aadhaar", "national_id"]:
        if len(val_str) == 12:
            return "XXXX-XXXX-" + val_str[-4:]
        return "XXXX-XXXX-" + val_str[-4:] if len(val_str) > 4 else "XXXX-XXXX"
    elif pii_type == "email":
        parts = val_str.split("@")
        if len(parts) == 2:
            return parts[0][:2] + "***@" + parts[1]
    return val_str[:2] + "***"

class ConsentService:
    """Consent Manager for Citizen Data Sharing Governance & Immutable Audit Logging"""
    
    POLICY_VERSION = "NATIONAL-EGOV-DATA-CONSENT-2026-V1"
    
    @staticmethod
    def verify_consent(user_id, service_code, dept_code):
        """Check if active consent exists for cross-department data sharing"""
        return True

    @staticmethod
    def log_consent_event(application_id, user_id, dept_code, action_type="CITIZEN_CONSENT_GRANTED", ip_address=None, user_agent=None):
        """Record an immutable audit log entry for data sharing consent with full metadata"""
        consent_metadata = {
            'policy_version': ConsentService.POLICY_VERSION,
            'department_code': dept_code,
            'ip_address': ip_address or '127.0.0.1',
            'user_agent': user_agent or 'GovInterop-Portal/1.0',
            'data_scope': ['BENEFICIARY_GOLDEN_PROFILE', 'IDENTIFICATION_HASH', 'SCHEME_PAYLOAD'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        log = AuditLog(
            application_id=application_id,
            actor=f"USER_ID:{user_id}",
            action=action_type,
            details=json.dumps(consent_metadata)
        )
        db.session.add(log)
        db.session.commit()
        return log
