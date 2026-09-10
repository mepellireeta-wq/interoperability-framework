from flask import Blueprint, render_template, session, redirect, request
from database.models import User, Application
from services.sso_service import SSOService

citizen_bp = Blueprint('citizen', __name__)

def get_current_citizen_user():
    """Retrieve current logged-in citizen user from Session, JWT Header, Query Param, or Cookie"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return user

    auth_header = request.headers.get('Authorization')
    token = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    elif request.args.get('token'):
        token = request.args.get('token')
    elif request.cookies.get('sso_token'):
        token = request.cookies.get('sso_token')

    if token:
        payload = SSOService.decode_token(token)
        if payload and payload.get('sub'):
            user = User.query.get(payload.get('sub'))
            if user:
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                return user

    return None

@citizen_bp.route('/citizen-portal', methods=['GET'])
def citizen_portal_page():
    """Dedicated Citizen Portal - Scoped strictly to the logged-in citizen's credentials & applications"""
    user = get_current_citizen_user()
    
    # If not logged in, redirect to login page
    if not user:
        return redirect('/login-page')
        
    # Retrieve ONLY this specific citizen's applications
    my_applications = Application.query.filter_by(applicant_id=user.id).order_by(Application.id.desc()).all()
    
    return render_template('citizen.html', user=user, applications=my_applications)
