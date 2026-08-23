from database.models import db, Application, WorkflowStep, AuditLog
from services.connectors import SystemConnectors
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

        # Mark current step as COMPLETED
        current_step.status = 'COMPLETED'
        current_step.remarks = remarks
        current_step.updated_at = datetime.utcnow()
        
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
                    SystemConnectors.send_to_dept_b_employment_legacy(payload)
                elif app_record.current_stage == 3:
                    SystemConnectors.send_to_dept_c_innovation(payload)
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
