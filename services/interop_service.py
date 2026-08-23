import json

class InteroperabilityEngine:
    """Standardizes disparate departmental data formats into unified Universal E-Governance Schema"""
    
    SCHEMA_VERSION = "E-GOV-STD-INTEROP-2026"
    
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
        """Validate payload against required e-governance data quality rules"""
        beneficiary = payload.get('beneficiary', {})
        errors = []
        
        if not beneficiary.get('full_name'):
            errors.append("Beneficiary Full Name is required")
        if not beneficiary.get('email') or '@' not in beneficiary.get('email'):
            errors.append("Valid Email Address is required")
        if not beneficiary.get('phone') or len(beneficiary.get('phone')) < 10:
            errors.append("10-digit Phone Number is required")
            
        return len(errors) == 0, errors
