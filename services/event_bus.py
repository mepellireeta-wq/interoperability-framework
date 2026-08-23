import json
from datetime import datetime
from database.models import db, AuditLog

class EventBus:
    """Event-Driven Message Bus for Asynchronous Governance Events"""
    
    _listeners = []
    
    @classmethod
    def register_listener(cls, listener_fn):
        """Register event listener callback"""
        cls._listeners.append(listener_fn)

    @classmethod
    def publish(cls, event_type, payload):
        """Publish event to all registered listeners & record audit log"""
        event_data = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'payload': payload
        }
        
        # 1. Audit Log Persistence
        try:
            app_id = payload.get('application_id')
            audit = AuditLog(
                application_id=app_id,
                actor=payload.get('actor', 'EVENT_BUS'),
                action=event_type,
                details=json.dumps(payload.get('details', {}))
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"[EVENT_BUS_WARNING] Audit log failed: {e}")
            
        # 2. Trigger Listeners
        for listener in cls._listeners:
            try:
                listener(event_type, payload)
            except Exception as ex:
                print(f"[EVENT_BUS_LISTENER_ERROR] {ex}")
                
        return event_data
