from flask import Blueprint, render_template, session, redirect

developer_bp = Blueprint('developer', __name__)

@developer_bp.route('/developer-tech', methods=['GET'])
def developer_tech_page():
    """Dedicated Developer & Technical Architecture Page - Strictly Protected for Admin / Officer Roles"""
    user_role = session.get('role')
    
    # Strict Access Control: Only ADMIN or OFFICER allowed to see Developer Tech Page
    if not user_role or user_role not in ['ADMIN', 'OFFICER']:
        return redirect('/login-page')
        
    username = session.get('username', 'System Administrator')
    return render_template('developer.html', username=username, role=user_role)
