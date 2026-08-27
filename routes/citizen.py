from flask import Blueprint, render_template, session, redirect, url_for

citizen_bp = Blueprint('citizen', __name__)

@citizen_bp.route('/citizen-portal', methods=['GET'])
def citizen_portal_page():
    """Dedicated Citizen Portal - Accessible for Citizens to view schemes, apply and track status"""
    user_role = session.get('role', 'CITIZEN')
    username = session.get('username', 'Citizen User')
    
    return render_template('citizen.html', username=username, role=user_role)
