from flask import Blueprint, request, jsonify, session
from backend.chatbot.context_builder import build_user_context
from backend.chatbot.service import generate_chatbot_response

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """
    Handles chatbot query requests.
    Enforces authorization checks, retrieves context from DB, and queries AI engine.
    """
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message text cannot be empty.'
            }), 400

        # Retrieve user details from session
        role = session.get('role', 'startup')  # Default guest/public role if not logged in
        user_id = session.get('user_id', 0)
        user_info = {
            'username': session.get('username', 'Guest User'),
            'email': session.get('email', ''),
            'role': role,
            'department': session.get('department'),
            'company_name': session.get('company_name')
        }

        # 1. Prepare authorized context from DB
        db_context = build_user_context(role, user_id, user_info)

        # 2. Generate response via AI Service (Gemini/OpenAI/Fallback)
        ai_response = generate_chatbot_response(user_message, db_context, role)

        return jsonify({
            'success': True,
            'response': ai_response,
            'role': role,
            'user': user_info['username']
        })

    except Exception as e:
        print(f"[Chatbot Route Error]: {e}")
        return jsonify({
            'success': False,
            'error': 'An internal error occurred while processing your request. Please try again.'
        }), 500


@chatbot_bp.route('/clear', methods=['POST'])
def clear_history():
    """Clears chatbot session state if needed."""
    return jsonify({
        'success': True,
        'message': 'Chat session history cleared.'
    })
