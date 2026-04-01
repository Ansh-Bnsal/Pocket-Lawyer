"""
Pocket Lawyer 2.0 — Chat Routes (Refactored)
AI-powered structured legal guidance using the Scalable AI Gateway.
Supports text and multimodal file uploads.
"""
import json
import base64
from flask import Blueprint, request, jsonify
from database import get_db
from services.ai import ai # New Decoupled Gateway
from routes.auth_routes import require_auth

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
@require_auth
def chat():
    # 📝 Handle both JSON and Multipart (for files)
    if request.is_json:
        data = request.get_json()
        message = (data.get('message') or '').strip()
        session_id = data.get('sessionId')
        case_id = data.get('caseId')
        file_data = None
    else:
        message = request.form.get('message', '').strip()
        session_id = request.form.get('sessionId')
        case_id = request.form.get('caseId')
        
        # 📎 Handle Multimodal File Attachment
        file_data = None
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Convert file to Base64 for Gemini/Vision
                file_content = file.read()
                file_data = {
                    "mime_type": file.mimetype,
                    "base64": base64.b64encode(file_content).decode('utf-8')
                }

    if not message and not file_data:
        return jsonify({'error': 'Message or file is required'}), 400

    # 🏛️ FETCH CASE CONTEXT (If applicable)
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
                case_context = f"Context: {case['case_type']} - {case['title']}\nSummary: {case['ai_summary']}"

    # 💾 SAVE USER MESSAGE
    with get_db() as conn:
        cursor = conn.cursor()
        if not session_id:
            cursor.execute(
                'INSERT INTO chat_sessions (user_id, case_id, title) VALUES (?, ?, ?)',
                (request.user_id, case_id, message[:60] if message else "Document Analysis")
            )
            session_id = cursor.lastrowid
            conn.commit()

        cursor.execute(
            'INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)',
            (session_id, 'user', message or "[Attached Document]")
        )
        conn.commit()

    # 🧠 CALL AI GATEWAY (The "Clean" Way)
    # The route doesn't care about Gemini, Prompts, or JSON anymore.
    # It just asks for a "chat" task and gets back professional text.
    result = ai.ask("chat", message, file_data=file_data, context=case_context)
    response_text = result.text

    # 💾 SAVE AI RESPONSE
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)',
            (session_id, 'ai', response_text)
        )
        cursor.execute(
            'UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (session_id,)
        )
        conn.commit()

    return jsonify({
        'sessionId': session_id,
        'response': response_text
    }), 200

@chat_bp.route('/chat/sessions', methods=['GET'])
@require_auth
def list_sessions():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, title, case_id, created_at, updated_at FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC',
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
