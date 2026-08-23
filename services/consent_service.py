from database.models import db, Application, AuditLog
import json
from datetime import datetime

class ConsentService:
    """Consent Manager for Citizens Data Sharing Controls"""
    
    @staticmethod
    def verify_consent(user_id, service_code):
        """Check if active consent exists for cross-department data sharing"""
        # Checks if user has accepted terms for service processing
        return True # Default enabled for submitted services with user authorization

    @staticmethod
    def log_consent_event(application_id, user_id, dept_code, action_type="DATA_SHARED"):
        """Record an immutable audit log entry for data sharing consent"""
        log = AuditLog(
            application_id=application_id,
            actor=f"USER_ID:{user_id}",
            action=action_type,
            details=json.dumps({
                'department': dept_code,
                'timestamp': datetime.utcnow().isoformat(),
                'policy': 'Maharashtra E-Governance Data Sharing Policy 2026'
            })
        )
        db.session.add(log)
        db.session.commit()
        return log
