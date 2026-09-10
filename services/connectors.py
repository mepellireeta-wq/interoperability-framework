import requests
import json
import time
from flask import current_app
from database.models import db, RetryQueue, Application, WorkflowStep

class SystemConnectors:
    """Connectors & Protocol Adapters for Heterogeneous Department Systems with Failure Queueing"""
    
    MAX_RETRIES = 3
    RETRY_BACKOFF_SEC = 0.5
    
    @staticmethod
    def _make_post_request(url_path, full_url, json_data=None, xml_data=None, is_xml=False):
        """Helper to execute HTTP POST either via test_client (when testing) or requests."""
        if current_app and current_app.config.get('TESTING'):
            with current_app.test_client() as client:
                if is_xml:
                    res = client.post(url_path, data=xml_data, headers={'Content-Type': 'text/xml'})
                    return res.status_code, res.get_data(as_text=True)
                else:
                    res = client.post(url_path, json=json_data, headers={'Content-Type': 'application/json'})
                    return res.status_code, res.get_json()
        else:
            try:
                headers = {'Content-Type': 'text/xml'} if is_xml else {'Content-Type': 'application/json'}
                data_arg = xml_data if is_xml else None
                json_arg = json_data if not is_xml else None
                res = requests.post(full_url, data=data_arg, json=json_arg, headers=headers, timeout=3)
                if is_xml:
                    return res.status_code, res.text
                return res.status_code, res.json()
            except Exception as ex:
                return 503, str(ex)

    @staticmethod
    def send_to_dept_a_skills(standardized_payload, application_id=None):
        """REST API Protocol Adapter for Department of Skills Development & Entrepreneurship."""
        url_path = '/api/v1/mock/dept-a/skills'
        full_url = current_app.config.get('DEPT_A_SKILLS_URL', f'http://127.0.0.1:5000{url_path}')
        
        for attempt in range(1, SystemConnectors.MAX_RETRIES + 1):
            status_code, resp = SystemConnectors._make_post_request(url_path, full_url, json_data=standardized_payload)
            if status_code in [200, 201]:
                return True, resp
            time.sleep(SystemConnectors.RETRY_BACKOFF_SEC)
            
        # Add to Retry Queue if failed
        if application_id:
            SystemConnectors._enqueue_retry(application_id, 'SKILL_DEV_DEPT', standardized_payload, f"HTTP {status_code}")
        return False, {'status': 'QUEUED', 'error': f"Dept A unavailable (HTTP {status_code}). Queued into Retry Queue."}

    @staticmethod
    def send_to_dept_b_employment_legacy(standardized_payload, application_id=None):
        """SOAP/XML Protocol Adapter for Directorate of Employment."""
        try:
            beneficiary = standardized_payload.get('beneficiary', {})
            xml_soap_envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:emp="http://employment.gov.in/legacy">
               <soapenv:Header/>
               <soapenv:Body>
                  <emp:RegisterEligibilityRequest>
                     <emp:FullName>{beneficiary.get('full_name')}</emp:FullName>
                     <emp:StateId>{beneficiary.get('state_id_number')}</emp:StateId>
                     <emp:Phone>{beneficiary.get('phone')}</emp:Phone>
                  </emp:RegisterEligibilityRequest>
               </soapenv:Body>
            </soapenv:Envelope>"""
            
            url_path = '/api/v1/mock/dept-b/employment'
            full_url = current_app.config.get('DEPT_B_EMPLOYMENT_URL', f'http://127.0.0.1:5000{url_path}')
            
            for attempt in range(1, SystemConnectors.MAX_RETRIES + 1):
                status_code, resp = SystemConnectors._make_post_request(url_path, full_url, xml_data=xml_soap_envelope, is_xml=True)
                if status_code == 200:
                    return True, {'status': 'LEGACY_SOAP_ADAPTER_SUCCESS', 'ack_code': 'SOAP-GOV-200'}
                time.sleep(SystemConnectors.RETRY_BACKOFF_SEC)
                
            if application_id:
                SystemConnectors._enqueue_retry(application_id, 'EMPLOYMENT_DEPT', standardized_payload, f"HTTP {status_code}")
            return False, {'status': 'QUEUED', 'error': f"Dept B SOAP unavailable (HTTP {status_code}). Queued into Retry Queue."}
        except Exception as outer_ex:
            return False, {'status': 'ERROR', 'error': f"SOAP Transformation Error: {outer_ex}"}

    @staticmethod
    def send_to_dept_c_innovation(standardized_payload, application_id=None):
        """Direct DB/API Adapter for State Innovation Society."""
        url_path = '/api/v1/mock/dept-c/innovation'
        full_url = current_app.config.get('DEPT_C_ENTREPRENEURSHIP_URL', f'http://127.0.0.1:5000{url_path}')
        
        status_code, resp = SystemConnectors._make_post_request(url_path, full_url, json_data=standardized_payload)
        if status_code == 200:
            return True, resp
            
        if application_id:
            SystemConnectors._enqueue_retry(application_id, 'INNOVATION_DEPT', standardized_payload, f"HTTP {status_code}")
        return False, {'status': 'QUEUED', 'error': f"Dept C unavailable (HTTP {status_code}). Queued into Retry Queue."}

    @staticmethod
    def _enqueue_retry(application_id, dept_code, payload, error_msg):
        """Persist failed message into database RetryQueue."""
        retry_item = RetryQueue(
            application_id=application_id,
            dept_code=dept_code,
            payload_json=json.dumps(payload),
            status='PENDING',
            last_error=error_msg
        )
        db.session.add(retry_item)
        db.session.commit()

    @staticmethod
    def process_queued_retries():
        """Process all PENDING items in RetryQueue after target systems recover."""
        pending_items = RetryQueue.query.filter_by(status='PENDING').all()
        processed_count = 0
        
        for item in pending_items:
            payload = json.loads(item.payload_json)
            success = False
            
            if item.dept_code == 'SKILL_DEV_DEPT':
                success, resp = SystemConnectors.send_to_dept_a_skills(payload)
            elif item.dept_code == 'EMPLOYMENT_DEPT':
                success, resp = SystemConnectors.send_to_dept_b_employment_legacy(payload)
            elif item.dept_code == 'INNOVATION_DEPT':
                success, resp = SystemConnectors.send_to_dept_c_innovation(payload)
                
            if success:
                item.status = 'PROCESSED'
                item.retry_count += 1
                processed_count += 1
                
                # Update corresponding workflow step to COMPLETED
                step = WorkflowStep.query.filter_by(application_id=item.application_id).first()
                if step:
                    step.status = 'COMPLETED'
                    step.remarks = 'Recovered and processed via Retry Queue'
            else:
                item.retry_count += 1
                item.last_error = f"Retry attempt {item.retry_count} failed"
                if item.retry_count >= item.max_retries:
                    item.status = 'FAILED'
                    
        db.session.commit()
        return processed_count
