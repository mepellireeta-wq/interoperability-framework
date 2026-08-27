from flask import Blueprint, render_template

developer_bp = Blueprint('developer', __name__)

@developer_bp.route('/developer-tech', methods=['GET'])
def developer_tech_page():
    """Dedicated Developer & Technical Architecture Page housing Quantum, Blockchain, and API Specs"""
    return render_template('developer.html')
