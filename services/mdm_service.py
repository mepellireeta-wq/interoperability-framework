import hashlib
import json
from flask import current_app
from database.models import db, BeneficiaryMDM, User

class MDMEngine:
    """Master Data Management Engine for Deduplication Key Generation & Privacy Preservation"""
    
    @staticmethod
    def generate_dedup_key(full_name, phone, state_id_hash):
        """Generate privacy-preserving deterministic deduplication key."""
        norm_name = str(full_name).strip().lower() if full_name else ""
        norm_phone = str(phone).strip() if phone else ""
        norm_id = str(state_id_hash).strip().lower() if state_id_hash else ""
        raw = f"{norm_name}|{norm_phone}|{norm_id}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

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
