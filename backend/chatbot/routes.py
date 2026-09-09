from flask import Blueprint, jsonify, request, session

from backend.chatbot.context_builder import build_user_context
from backend.chatbot.service import generate_chatbot_response

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.post('/chat')
def chat():
    if not session.get('user_id'):
        return jsonify(success=False, error='Please sign in before using the assistant.'), 401
    message = (request.get_json(silent=True) or {}).get('message', '').strip()
    if not message:
        return jsonify(success=False, error='Message text cannot be empty.'), 400
    context = build_user_context(session['role'], session['user_id'])
    return jsonify(success=True, response=generate_chatbot_response(message, context))


@chatbot_bp.post('/clear')
def clear_history():
    return jsonify(success=True)
