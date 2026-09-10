from database.models import db, Application, WorkflowStep, AuditLog
from services.connectors import SystemConnectors
from datetime import datetime, timezone
import json

class WorkflowEngine:
    """Configurable Multi-Department Workflow Orchestrator"""
    
    @staticmethod
    def process_next_stage(application_id, decision="APPROVE", remarks="Passed Verification", officer_name="System Automated", force_approve=False):
        """Advance application through its multi-department workflow pipeline"""
        app_record = db.session.get(Application, application_id)
        if not app_record:
            return False, "Application not found"
            
        current_step = WorkflowStep.query.filter_by(
            application_id=app_record.id, 
            stage_number=app_record.current_stage
        ).first()
        
        if not current_step:
            return False, "Current workflow step not found"
            
        payload = json.loads(app_record.payload_json) if app_record.payload_json else {}
        
        if decision == "REJECT":
            current_step.status = 'REJECTED'
            current_step.remarks = remarks
            app_record.status = 'REJECTED'
            db.session.commit()
            
            audit = AuditLog(
                application_id=app_record.id,
                actor=officer_name,
                action="WORKFLOW_STAGE_REJECTED",
                details=f"Stage {app_record.current_stage} rejected: {remarks}"
            )
            db.session.add(audit)
            db.session.commit()
            return True, "Application Rejected"

        if decision == "APPROVE" and force_approve:
            current_step.status = 'COMPLETED'
            current_step.remarks = remarks
            current_step.updated_at = datetime.now(timezone.utc)
            app_record.status = 'APPROVED'
            app_record.current_stage = app_record.total_stages
            
            all_steps = WorkflowStep.query.filter_by(application_id=app_record.id).all()
            for step in all_steps:
                step.status = 'COMPLETED'
                step.updated_at = datetime.now(timezone.utc)
                
            audit = AuditLog(
                application_id=app_record.id,
                actor=officer_name,
                action="APPLICATION_APPROVED",
                details=f"Application approved: {remarks}"
            )
            db.session.add(audit)
            db.session.commit()
            return True, "Application Approved"

        # Mark current step as COMPLETED
        current_step.status = 'COMPLETED'
        current_step.remarks = remarks
        current_step.updated_at = datetime.now(timezone.utc)
        
        # Check if more stages exist
        if app_record.current_stage < app_record.total_stages:
            app_record.current_stage += 1
            app_record.status = 'IN_WORKFLOW'
            
            next_step = WorkflowStep.query.filter_by(
                application_id=app_record.id, 
                stage_number=app_record.current_stage
            ).first()
            
            if next_step:
                next_step.status = 'IN_PROGRESS'
                next_step.remarks = "Awaiting Department Approval"
                
                # Trigger Department Connector based on Stage Number
                if app_record.current_stage == 2:
                    SystemConnectors.send_to_dept_b_employment_legacy(payload, application_id=app_record.id)
                elif app_record.current_stage == 3:
                    SystemConnectors.send_to_dept_c_innovation(payload, application_id=app_record.id)
        else:
            # Final Stage Completed!
            app_record.status = 'APPROVED'
            
        audit = AuditLog(
            application_id=app_record.id,
            actor=officer_name,
            action=f"STAGE_{current_step.stage_number}_COMPLETED",
            details=f"Passed Stage {current_step.stage_number} ({current_step.stage_name}) - {remarks}"
        )
        db.session.add(audit)
        db.session.commit()
        
        return True, f"Advanced to Stage {app_record.current_stage}"
