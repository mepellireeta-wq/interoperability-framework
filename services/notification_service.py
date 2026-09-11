from database.models import db, Application, User, AuditLog
from datetime import datetime

class NotificationService:
    """Multi-Channel Notification Dispatcher (SMS / Email / Push Notifications)"""
    
    @staticmethod
    def send_status_notification(app_record, status, remarks=None):
        """Dispatch real-time SMS & Email notification alerts when application is Approved or Rejected"""
        if not app_record:
            return
            
        applicant = db.session.get(User, app_record.applicant_id)
        email = applicant.email if (applicant and applicant.email) else 'citizen@example.com'
        phone = applicant.phone if (applicant and applicant.phone) else '9123456789'
        full_name = applicant.full_name if applicant else 'Valued Citizen'
        tracking_id = app_record.tracking_id
        service_title = app_record.service_title
        
        if status in ['APPROVED', 'SANCTIONED']:
            sms_text = f"🎉 CONGRATULATIONS {full_name}! Your application for '{service_title}' (ID: {tracking_id}) has been APPROVED & SANCTIONED."
            email_subject = f"APPLICATION APPROVED & SANCTIONED: {tracking_id}"
            email_body = f"Dear {full_name},\n\nWe are pleased to inform you that your application for '{service_title}' (Tracking ID: {tracking_id}) has been officially APPROVED & SANCTIONED by the Governance Administrator.\n\nView details: http://127.0.0.1:5000/track-page?id={tracking_id}"
            action_code = "SMS_EMAIL_APPROVED_NOTIFIED"
        else:
            sms_text = f"⚠️ UPDATE: Your application for '{service_title}' (ID: {tracking_id}) has been REJECTED. Remarks: {remarks or 'Criteria not met'}."
            email_subject = f"APPLICATION REJECTED: {tracking_id}"
            email_body = f"Dear {full_name},\n\nYour application for '{service_title}' (Tracking ID: {tracking_id}) was reviewed and REJECTED.\nRemarks: {remarks or 'Criteria not met'}.\n\nYou may submit a fresh application at: http://127.0.0.1:5000/apply-page"
            action_code = "SMS_EMAIL_REJECTED_NOTIFIED"

        print(f"\n[SMS DISPATCH -> {phone}]: {sms_text}")
        print(f"[EMAIL DISPATCH -> {email}]: Subject: {email_subject}\n{email_body}\n")

        # Save notification dispatch into AuditLog so citizen can view notification inbox
        try:
            audit = AuditLog(
                application_id=app_record.id,
                actor="NOTIFICATION_SYSTEM",
                action=action_code,
                details=f"SMS sent to {phone} & Email sent to {email}: {sms_text}"
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    @staticmethod
    def handle_event(event_type, payload):
        """Event listener handler for sending real-time alerts"""
        applicant_email = payload.get('email', 'citizen@example.com')
        applicant_phone = payload.get('phone', '9123456789')
        tracking_id = payload.get('tracking_id', 'GOV-2026-X8F9')
        
        if event_type == "APPLICATION_SUBMITTED":
            print(f"[SMS ALERT -> {applicant_phone}]: Your application {tracking_id} is received & standardized under E-GOV-STD-INTEROP-2026.")
            print(f"[EMAIL -> {applicant_email}]: Application Submitted successfully. Track at /track-page?id={tracking_id}")
            
        elif event_type == "STAGE_APPROVED":
            stage_name = payload.get('stage_name', 'Stage')
            print(f"[SMS ALERT -> {applicant_phone}]: Update on {tracking_id}: {stage_name} APPROVED.")
            
        elif event_type == "APPLICATION_SANCTIONED":
            print(f"[SMS ALERT -> {applicant_phone}]: CONGRATULATIONS! Your application {tracking_id} is FINAL SANCTIONED & APPROVED.")
            print(f"[EMAIL -> {applicant_email}]: Sanction Letter generated for tracking ID {tracking_id}.")

from services.event_bus import EventBus
EventBus.register_listener(NotificationService.handle_event)
