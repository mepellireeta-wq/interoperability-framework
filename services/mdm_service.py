import hashlib
import json
from flask import current_app
from database.models import db, BeneficiaryMDM, User

class MDMService:
    """Master Data Management (MDM) Service for Unified Citizen Golden Records"""
    
    @staticmethod
    def get_or_create_master_record(user_id, state_id_number, profile_data):
        """Deduplicate applicant and return master profile record"""
        state_salt = current_app.config.get('STATE_ID_SALT', 'mh-salt')
        state_id_hash = hashlib.sha256(f"{state_id_number}-{state_salt}".encode()).hexdigest()
        
        mdm = BeneficiaryMDM.query.filter_by(state_id_hash=state_id_hash).first()
        
        if mdm:
            # Update existing profile
            existing_profile = json.loads(mdm.master_profile_json)
            existing_profile.update(profile_data)
            mdm.master_profile_json = json.dumps(existing_profile)
            db.session.commit()
            return mdm, False # Existing profile updated
            
        # Create new MDM Record
        new_mdm = BeneficiaryMDM(
            user_id=user_id,
            state_id_hash=state_id_hash,
            master_profile_json=json.dumps(profile_data),
            is_verified=True
        )
        db.session.add(new_mdm)
        db.session.commit()
        return new_mdm, True # New profile created
