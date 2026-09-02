from database.models import db, Application, WorkflowStep, AuditLog
from services.connectors import SystemConnectors
from services.blockchain_service import blockchain_instance
from datetime import datetime
import json

class WorkflowEngine:
    """Configurable Multi-Department Workflow Orchestrator"""
    
    @staticmethod
    def process_next_stage(application_id, decision="APPROVE", remarks="Passed Verification", officer_name="System Automated"):
        """Advance application through its multi-department workflow pipeline"""
        app_record = Application.query.get(application_id)
        if not app_record:
            return False, "Application not found"
            
        if decision == "REJECT":
            app_record.status = 'REJECTED'
            steps = WorkflowStep.query.filter_by(application_id=app_record.id).all()
            for step in steps:
                if step.status != 'COMPLETED':
                    step.status = 'REJECTED'
                    step.remarks = remarks
            db.session.commit()
            
            audit = AuditLog(
                application_id=app_record.id,
                actor=officer_name,
                action="APPLICATION_REJECTED",
                details=f"Application REJECTED by Admin/Officer: {remarks}"
            )
            db.session.add(audit)
            db.session.commit()
            return True, "Application Rejected"

        # Direct Full Approval when Admin approves from Admin Portal
        app_record.status = 'APPROVED'
        app_record.current_stage = app_record.total_stages
        
        # Mark all steps as COMPLETED
        steps = WorkflowStep.query.filter_by(application_id=app_record.id).all()
        for step in steps:
            step.status = 'COMPLETED'
            step.remarks = remarks
            step.updated_at = datetime.utcnow()

        db.session.commit()

        # Mine Immutable SHA-256 Blockchain Block for Approved Certificate
        try:
            blockchain_instance.add_application_record(
                tracking_id=app_record.tracking_id,
                applicant_name=app_record.applicant.full_name if app_record.applicant else 'Citizen Applicant',
                scheme_title=app_record.service_title,
                status='APPROVED'
            )
        except Exception as e:
            print(f"[BLOCKCHAIN_LOG] Auto block mining notice: {e}")

        audit = AuditLog(
            application_id=app_record.id,
            actor=officer_name,
            action="APPLICATION_FULLY_APPROVED",
            details=f"Application FULLY APPROVED & Sanction Certificate Issued by {officer_name}"
        )
        db.session.add(audit)
        db.session.commit()
        
        return True, "Application Fully Approved & Sanctioned"
