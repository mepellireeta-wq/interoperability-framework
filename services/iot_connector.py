import json
from datetime import datetime
from database.models import db, Application, WorkflowStep, AuditLog
from services.interop_service import InteroperabilityEngine

class IoTTelemetryConnector:
    """Phase 16 Optional Hardware & Sensor Telemetry Connector (ESP32 / Ultrasonic Sensors)"""
    
    @staticmethod
    def process_sensor_alert(sensor_id, location, severity, alert_type, metric_value):
        """Process incoming hardware telemetry alert and auto-generate urgent application"""
        payload_data = {
            'applicant': {
                'full_name': f"Automated IoT Sensor ({sensor_id})",
                'email': 'iot-telemetry@interop.gov.in',
                'phone': '9900001122',
                'district': location,
                'state_id_number': f"SENSOR-{sensor_id}"
            },
            'scheme_data': {
                'sensor_id': sensor_id,
                'alert_type': alert_type,
                'metric_value': metric_value,
                'severity': severity,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        # Standardize payload
        standardized_payload = InteroperabilityEngine.standardize_payload(payload_data, 'IOT_TELEMETRY_ALERT')
        
        # Log Audit Record
        audit = AuditLog(
            actor=f"IOT_SENSOR:{sensor_id}",
            action="IOT_TELEMETRY_ALERT_RECEIVED",
            details=json.dumps({
                'location': location,
                'severity': severity,
                'metric': metric_value
            })
        )
        db.session.add(audit)
        db.session.commit()
        
        return {
            'status': 'TELEMETRY_ALERT_PROCESSED',
            'sensor_id': sensor_id,
            'severity': severity,
            'standardized_contract': standardized_payload
        }
