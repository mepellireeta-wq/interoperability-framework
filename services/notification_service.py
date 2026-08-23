class NotificationService:
    """Multi-Channel Notification Dispatcher (SMS / Email / Push Notifications)"""
    
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

# Register Notification Service with Event Bus
from services.event_bus import EventBus
EventBus.register_listener(NotificationService.handle_event)
