from flask import Blueprint, request, jsonify
from database.models import Application
import re

ai_chat_bp = Blueprint('ai_chat', __name__, url_prefix='/api/v1/ai')

# Knowledge Base for AI Chatbot Assistant
SCHEME_KNOWLEDGE = {
    'education': "Our Education Portal offers Merit Scholarships, Fee Waivers, and Central Education Loan Interest Subsidies for students pursuing professional degrees.",
    'health': "Our Health Portal provides Ayushman Bharat Universal Health Cards offering cashless hospital coverage up to ₹5 Lakh per family per year.",
    'banking': "Our Banking & Finance Portal offers PMEGP & MUDRA Loans — collateral-free micro-business loans up to ₹10 Lakh with credit-linked subsidies.",
    'insurance': "Our Insurance Portal provides PM Fasal Bima crop damage protection and social security life insurance for citizens.",
    'agriculture': "Our Agriculture Portal provides PM-KISAN direct annual income support of ₹6,000 transferred directly to farmers' bank accounts.",
    'skills': "Our Skills Portal offers vocational training, national industry certifications, and monthly apprentice stipends.",
    'help': "To apply for any scheme: 1. Click 'Apply Now', 2. Select your State & District, 3. Fill your name, email, and ID number, 4. Check the Data Sharing Consent box, 5. Click Submit to receive your Tracking ID!"
}

@ai_chat_bp.route('/chat', methods=['POST'])
def handle_ai_chat():
    """AI Assistant / Chatbot Response Handler"""
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'reply': "Hello! I am your GovInterop AI Assistant. Ask me about Education, Health, Banking, Agriculture, or tracking your application!"}), 200
        
    user_msg_lower = message.lower()
    
    # 1. Check if user provided a Tracking ID (e.g. GOV-2026-8A4F)
    tracking_match = re.search(r'(GOV-\d{4}-[A-Z0-9]{4})', message.upper())
    if tracking_match:
        tracking_id = tracking_match.group(1)
        app_record = Application.query.filter_by(tracking_id=tracking_id).first()
        if app_record:
            return jsonify({
                'reply': f"🔍 **Application Status for {tracking_id}**:\n"
                         f"• Scheme: {app_record.service_title}\n"
                         f"• Current Status: **{app_record.status}**\n"
                         f"• Progress: Stage {app_record.current_stage} of {app_record.total_stages}\n"
                         f"You can view the full timeline on the 'Track Application' page!"
            }), 200
        else:
            return jsonify({'reply': f"I checked our national records, but could not find tracking ID `{tracking_id}`. Please verify your ID and try again!"}), 200

    # 2. Check Keyword Intents
    if any(k in user_msg_lower for k in ['education', 'scholarship', 'college', 'student', 'degree']):
        reply = f"🎓 **Education Sector**: {SCHEME_KNOWLEDGE['education']}\nWould you like me to help you apply?"
    elif any(k in user_msg_lower for k in ['health', 'hospital', 'ayushman', 'medical', 'doctor']):
        reply = f"🏥 **Health Sector**: {SCHEME_KNOWLEDGE['health']}\nSelect 'Health' in the state portal to claim your card!"
    elif any(k in user_msg_lower for k in ['bank', 'loan', 'mudra', 'finance', 'business', 'credit']):
        reply = f"🏦 **Banking & Financial Sector**: {SCHEME_KNOWLEDGE['banking']}\nApply under Banking schemes to request micro-enterprise credit!"
    elif any(k in user_msg_lower for k in ['insurance', 'crop', 'fasal', 'farmer', 'risk']):
        reply = f"🛡️ **Insurance Sector**: {SCHEME_KNOWLEDGE['insurance']}"
    elif any(k in user_msg_lower for k in ['agriculture', 'kisan', 'dbt', 'farm']):
        reply = f"🌾 **Agriculture Sector**: {SCHEME_KNOWLEDGE['agriculture']}"
    elif any(k in user_msg_lower for k in ['skill', 'training', 'job', 'employment']):
        reply = f"⚙️ **Skills & Employment**: {SCHEME_KNOWLEDGE['skills']}"
    elif any(k in user_msg_lower for k in ['how to', 'help', 'guide', 'navigate', 'apply', 'form', 'field']):
        reply = f"💡 **How to Use the Portal**:\n{SCHEME_KNOWLEDGE['help']}"
    else:
        reply = ("I am your GovInterop AI Guide! You can ask me:\n"
                 "• 'Tell me about Education Scholarships'\n"
                 "• 'How do I apply for Banking Loans?'\n"
                 "• 'Check status of GOV-2026-8A4F'\n"
                 "• 'How do I fill out the application form?'")

    return jsonify({'reply': reply}), 200
