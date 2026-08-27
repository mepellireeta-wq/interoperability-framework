from flask import Blueprint, render_template, session, redirect
from database.models import User, Application

citizen_bp = Blueprint('citizen', __name__)

@citizen_bp.route('/citizen-portal', methods=['GET'])
def citizen_portal_page():
    """Dedicated Citizen Portal - Scoped strictly to the logged-in citizen's credentials & applications"""
    user_id = session.get('user_id')
    user_role = session.get('role')
    
    # If not logged in, redirect to login page
    if not user_id:
        return redirect('/login-page')
        
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect('/login-page')
        
    # Retrieve ONLY this specific citizen's applications
    my_applications = Application.query.filter_by(applicant_id=user.id).order_by(Application.id.desc()).all()
    
    return render_template('citizen.html', user=user, applications=my_applications)
