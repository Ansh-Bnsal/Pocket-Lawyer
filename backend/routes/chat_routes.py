"""
Pocket Lawyer 2.0 — Chat Routes
AI-powered structured legal guidance (NOT a chatbot).
"""
import json
from flask import Blueprint, request, jsonify
from database import get_db
from services.ai_service import chat_response
from routes.auth_routes import require_auth

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
@require_auth
def chat():
    data = request.get_json()
    message = (data.get('message') or '').strip()
    session_id = data.get('sessionId')
    case_id = data.get('caseId')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    case_context = ''
    if case_id:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT title, description, ai_summary, case_type FROM cases WHERE id = ?',
                (case_id,)
            )
            case = cursor.fetchone()
            if case:
                case_context = (
                    f"Case Title: {case['title']}\n"
                    f"Case Type: {case['case_type']}\n"
                    f"Description: {case['description']}\n"
                    f"AI Summary: {case['ai_summary']}"
                )

    with get_db() as conn:
        cursor = conn.cursor()

        if not session_id:
            cursor.execute(
                '''INSERT INTO chat_sessions (user_id, case_id, title)
                   VALUES (?, ?, ?)''',
                (request.user_id, case_id, message[:60])
            )
            session_id = cursor.lastrowid
            conn.commit()

        cursor.execute(
            '''INSERT INTO chat_messages (session_id, role, content)
               VALUES (?, 'user', ?)''',
            (session_id, message)
        )
        conn.commit()

    try:
        ai_result = chat_response(message, case_context)
    except Exception as e:
        ai_result = {
            'domain': 'Error',
            'answer': f'AI service error: {str(e)}. Please try again.',
            'actionSteps': [],
            'warnings': [],
            'needsLawyer': False,
            'confidence': 'LOW'
        }

    response_text = ai_result.get('answer', '')
    if ai_result.get('legalRights'):
        response_text += '\n\n📋 Your Rights:\n' + '\n'.join(f'• {r}' for r in ai_result['legalRights'])
    if ai_result.get('actionSteps'):
        response_text += '\n\n🎯 Next Steps:\n'
        for step in ai_result['actionSteps']:
            response_text += f"{step['step']}. {step['action']} — {step.get('reason', '')}\n"
    if ai_result.get('warnings'):
        response_text += '\n\n⚠️ Important:\n' + '\n'.join(f'• {w}' for w in ai_result['warnings'])

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO chat_messages (session_id, role, content, structured_data)
               VALUES (?, 'ai', ?, ?)''',
            (session_id, response_text, json.dumps(ai_result))
        )
        cursor.execute(
            'UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (session_id,)
        )
        conn.commit()

    return jsonify({
        'sessionId': session_id,
        'response': response_text,
        'structured': ai_result
    }), 200


@chat_bp.route('/chat/sessions', methods=['GET'])
@require_auth
def list_sessions():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, title, case_id, created_at, updated_at
               FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC''',
            (request.user_id,)
        )
        rows = cursor.fetchall()
    return jsonify([dict(r) for r in rows]), 200


@chat_bp.route('/chat/sessions/<int:session_id>', methods=['GET'])
@require_auth
def get_session(session_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC',
            (session_id,)
        )
        messages = [dict(r) for r in cursor.fetchall()]
    return jsonify({'messages': messages}), 200
