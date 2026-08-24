import json
import re

class InteroperabilityEngine:
    """Standardizes disparate departmental data formats into unified Universal E-Governance Schema"""
    
    SCHEMA_VERSION = "E-GOV-STD-INTEROP-2026"
    
    # Regex patterns for Phase 13 Data Quality Checker
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_REGEX = r'^[6-9]\d{9}$'
    PINCODE_REGEX = r'^\d{6}$'
    PAN_REGEX = r'^[A-Z]{5}\d{4}[A-Z]{1}$'
    AADHAAR_HASH_REGEX = r'^[a-fA-F0-9]{64}$|^\d{12}$|^[A-Z0-9-]{8,}$'
    
    @staticmethod
    def standardize_payload(raw_data, service_code):
        """Transform input payload into standardized JSON data contract"""
        applicant_info = raw_data.get('applicant', {})
        
        standardized_contract = {
            'schema_version': InteroperabilityEngine.SCHEMA_VERSION,
            'service_code': service_code,
            'beneficiary': {
                'full_name': applicant_info.get('full_name', '').strip().title(),
                'email': applicant_info.get('email', '').strip().lower(),
                'phone': applicant_info.get('phone', '').strip(),
                'district': applicant_info.get('district', 'Central Zone').strip(),
                'state': applicant_info.get('state', 'National Jurisdiction').strip(),
                'pincode': applicant_info.get('pincode', '110001').strip(),
                'state_id_type': applicant_info.get('state_id_type', 'NATIONAL_ID'),
                'state_id_number': applicant_info.get('state_id_number', '').strip()
            },
            'scheme_specific_data': raw_data.get('scheme_data', {}),
            'metadata': {
                'data_quality_passed': True,
                'standardization_timestamp': str(json.dumps(raw_data, default=str))
            }
        }
        return standardized_contract

    @staticmethod
    def validate_data_quality(payload):
        """Phase 13 Advanced Data Quality Checker Rule Verification"""
        beneficiary = payload.get('beneficiary', {})
        errors = []
        
        # 1. Full Name Verification
        full_name = beneficiary.get('full_name', '')
        if not full_name or len(full_name) < 2:
            errors.append("Beneficiary Full Name must be at least 2 characters")
        elif not re.match(r'^[a-zA-Z\s\.\'-]+$', full_name):
            errors.append("Beneficiary Full Name contains invalid special characters")
            
        # 2. Email Syntax Verification
        email = beneficiary.get('email', '')
        if not email or not re.match(InteroperabilityEngine.EMAIL_REGEX, email):
            errors.append("Valid Email Address syntax is required (e.g., user@domain.com)")
            
        # 3. 10-Digit Mobile Phone Verification
        phone = beneficiary.get('phone', '')
        if not phone or not re.match(InteroperabilityEngine.PHONE_REGEX, phone):
            errors.append("Valid 10-digit Indian Mobile Number required (starting with 6-9)")
            
        # 4. Pincode Syntax Verification
        pincode = beneficiary.get('pincode', '')
        if pincode and not re.match(InteroperabilityEngine.PINCODE_REGEX, pincode):
            errors.append("Pincode must be a 6-digit number")
            
        # 5. National Identity Format Verification
        state_id = beneficiary.get('state_id_number', '')
        if not state_id or len(state_id) < 5:
            errors.append("Valid National/State Identity Number required")
            
        return len(errors) == 0, errors
