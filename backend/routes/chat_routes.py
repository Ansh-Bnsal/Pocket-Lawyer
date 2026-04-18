"""
# Pocket Lawyer 2.0 - Chat Routes (Triple-Layer AI)
Orchestrates parallel workers for Senior Lawyer (Intent), Risk Analyst (Docs), and 
Realtime Streaming. Uses thread-safe database connections for SQLite.
"""
import json
import base64
import threading
from flask import Blueprint, request, jsonify, Response
from database import get_db
from services.ai import ai
from routes.auth_routes import require_auth

def __summarize_session_async(session_id):
    """
    Rolling Summary Engine — compresses [Previous Summary + Latest 20 messages] into a new summary.
    This is O(1) constant speed: no matter if the conversation is 50 or 500 messages deep,
    the AI only ever reads ~20 messages + 1 summary paragraph to recompress.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            # 1. Fetch the existing summary (if any)
            cursor.execute('SELECT summary FROM chat_sessions WHERE id = ?', (session_id,))
            row = cursor.fetchone()
            prev_summary = (row['summary'] or '') if row else ''

            # 2. Fetch ONLY the last 20 messages (the new ones since last summary)
            cursor.execute('SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT 20', (session_id,))
            msgs = cursor.fetchall()
            if not msgs: return
            msgs.reverse()
            
            recent_transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in msgs])

            # 3. Build the rolling prompt: Previous Summary + New Messages
            if prev_summary:
                prompt = (f"You are a legal case memory engine. Below is a PREVIOUS SUMMARY of an ongoing legal conversation, "
                          f"followed by the LATEST 20 messages. Merge them into ONE comprehensive updated summary. "
                          f"Retain ALL key facts, dates, names, legal issues, grievances, and action items. "
                          f"Provide ONLY the dense technical summary, no commentary.\n\n"
                          f"--- PREVIOUS SUMMARY ---\n{prev_summary}\n\n"
                          f"--- LATEST MESSAGES ---\n{recent_transcript}")
            else:
                prompt = (f"Summarize the following legal conversation comprehensively. "
                          f"Retain all key facts, dates, names, grievances, and legal issues discussed "
                          f"so an AI attorney doesn't forget context. Provide ONLY the dense technical summary:\n\n"
                          f"{recent_transcript}")
            
            res = ai.ask("chat", prompt)
            if res.text:
                cursor.execute('UPDATE chat_sessions SET summary = ? WHERE id = ?', (res.text, session_id))
                conn.commit()
                print(f"[Rolling Summary] Successfully anchored session #{session_id} memory.")
    except Exception as e:
        print(f"[Rolling Summary Failed] {str(e)}")

def __generate_case_token_async(case_id, user_id, history_transcript):
    """
    Background worker that analyzes the raw chat transcript, generates a structured 
    Potential Case Token (JSON), and updates the case details.
    """
    try:
        res = ai.ask("analyze_case", f"Transient Chat Transcript:\n{history_transcript}")
        if not res.data:
            print(f"[Token Minting Warning] AI returned no data for case {case_id}")
            return
            
        token_data = res.data
        case_type = token_data.get('caseClassification', 'Legal Matter')
        summary = token_data.get('summary', 'Case automatically summarized.')
        risk_level = (token_data.get('riskLevel') or 'medium').lower()
        
        with get_db() as conn:
            cursor = conn.cursor()
            # Mint the Token
            cursor.execute('''INSERT INTO case_tokens (case_id, owner_id, token_data)
                              VALUES (?, ?, ?)''', 
                           (case_id, user_id, json.dumps(token_data)))
            
            # Upgrade the physical Case row
            cursor.execute('''UPDATE cases 
                              SET case_type = ?, description = ?, risk_level = ?
                              WHERE id = ?''', 
                           (case_type, summary, risk_level, case_id))
            conn.commit()
            print(f"[Token Minted] Successfully created Potential Case Token for Case #{case_id}")
            
    except Exception as e:
        print(f"[Async Token Minting Failed] {str(e)}")

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
@require_auth
def chat():
    # [Input] Handle JSON or Multipart
    if request.is_json:
        data = request.get_json()
        message = (data.get('message') or '').strip()
        session_id = data.get('sessionId')
        case_id = data.get('caseId')
        is_transient = data.get('is_transient', False)
        history = data.get('history', [])
        file_data = None
    else:
        message = request.form.get('message', '').strip()
        session_id = request.form.get('sessionId')
        case_id = request.form.get('caseId')
        is_transient = request.form.get('is_transient') == 'true'
        history_raw = request.form.get('history', '[]')
        try:
            history = json.loads(history_raw)
        except:
            history = []
        file_data = None
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                file_content = file.read()
                file_data = {
                    "mime_type": file.mimetype,
                    "base64": base64.b64encode(file_content).decode('utf-8')
                }

    if not message and not file_data:
        return jsonify({'error': 'Message or file is required'}), 400

    # [Context] Case Info
    case_context = f"User Role: {request.user_role}\n"
    if case_id:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT title, description, ai_summary, case_type FROM cases WHERE id = ?', (case_id,))
            case = cursor.fetchone()
            if case:
                case_context += f"Context: {case['case_type']} - {case['title']}\nSummary: {case['ai_summary']}"

    # [Setup] Init Session (Only if not transient)
    if not is_transient:
        with get_db() as conn:
            cursor = conn.cursor()
            if not session_id:
                cursor.execute('INSERT INTO chat_sessions (user_id, case_id, title) VALUES (?, ?, ?)',
                               (request.user_id, case_id, message[:60] if message else "Document Analysis"))
                session_id = cursor.lastrowid
                conn.commit()
            cursor.execute('INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)',
                           (session_id, 'user', message or "[Attached Document]"))
            conn.commit()

            session_summary = None
            # [Memory Continuity] Fetch history from backend database
            if not history:
                cursor.execute('SELECT summary FROM chat_sessions WHERE id = ?', (session_id,))
                sess_row = cursor.fetchone()
                if sess_row and sess_row.get('summary'):
                    session_summary = sess_row['summary']

                cursor.execute('SELECT COUNT(*) as cnt FROM chat_messages WHERE session_id = ?', (session_id,))
                total_msgs = cursor.fetchone()['cnt']

                # Fetch ONLY the last 20 messages for the sliding window
                cursor.execute('SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id DESC LIMIT 20', (session_id,))
                rows = cursor.fetchall()
                rows.reverse()
                history = [dict(r) for r in rows]

                # [The Anchor Trigger] If boundary hit, schedule compression
                if total_msgs > 0 and total_msgs % 19 == 0:
                    threading.Thread(target=__summarize_session_async, args=(session_id,), daemon=True).start()

    # [Orchestration] Delegate everything to the AI Orchestrator
    from services.ai.orchestrator import AIOrchestrator
    stream_generator = AIOrchestrator.process_chat_stream(
        message=message,
        file_data=file_data,
        session_id=session_id or 0,
        case_id=case_id or 0,
        user_role=request.user_role,
        case_context=case_context,
        session_summary=session_summary,
        history=history,
        is_transient=is_transient
    )

    return Response(stream_generator, mimetype='text/event-stream')

@chat_bp.route('/chat/sessions', methods=['GET'])
@require_auth
def list_sessions():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, case_id, created_at, updated_at FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC', (request.user_id,))
        rows = cursor.fetchall()
    return jsonify([dict(r) for r in rows]), 200

@chat_bp.route('/chat/sessions/<int:session_id>', methods=['GET'])
@require_auth
def get_session(session_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC', (session_id,))
        messages = [dict(r) for r in cursor.fetchall()]
    return jsonify({'messages': messages}), 200

@chat_bp.route('/chat/promote', methods=['POST'])
@require_auth
def promote_chat():
    """
    [Stability 49.0 - Stage 1 to Stage 2 Gate]
    Promotes a temporary Transient Chat into a permanent Legal Case.
    1. Creates Case.
    2. Maps Session to Case.
    3. Iterates over History to save 'user' / 'ai' messages.
    4. Iterates over 'intent' objects to construct pending records in the Services Cart (case_services).
    """
    data = request.get_json()
    title = data.get('title', 'New Legal Case')
    history = data.get('history', [])

    if not history:
        return jsonify({'error': 'No chat history provided'}), 400

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 1. Initialize Active Legal Case
            cursor.execute('''INSERT INTO cases (client_id, title, description, case_type, status, risk_level) 
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (request.user_id, title, "Case initialized automatically through AI Case Promoter.", "Legal Matter", "active", "medium"))
            case_id = cursor.lastrowid
            
            # 2. Assign Chat Session to the Case
            cursor.execute('INSERT INTO chat_sessions (user_id, case_id, title) VALUES (?, ?, ?)',
                           (request.user_id, case_id, title))
            session_id = cursor.lastrowid

            # 3. Synchronize Transient Memory Array
            for item in history:
                role = item.get('role')
                if role in ['user', 'ai']:
                    content = item.get('content', '')
                    cursor.execute('INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)',
                                   (session_id, role, content))
                                   
                # 4. 🛒 INJECT ACTION CARDS INTO SERVICES CART
                elif role == 'intent':
                    intent_data = item.get('data', {})
                    next_step = intent_data.get('next_step')
                    if next_step:
                        i_title = intent_data.get('title', 'AI Suggested Legal Service')
                        m_key = intent_data.get('merge_key', 'default')
                        ex_data = json.dumps(intent_data.get('extracted_data', {}))
                        
                        # Verify idempotency
                        cursor.execute('SELECT id FROM case_services WHERE case_id = ? AND merge_key = ?', (case_id, m_key))
                        if not cursor.fetchone():
                            cursor.execute('''INSERT INTO case_services (case_id, service_type, title, merge_key, extracted_data, status)
                                           VALUES (?, ?, ?, ?, ?, ?)''',
                                           (case_id, next_step, i_title, m_key, ex_data, 'pending'))
                            
            conn.commit()
            
            # 5. Launch Async Case Token Minting
            transcript = "\n".join([f"{item.get('role', '').upper()}: {item.get('content', '')}" for item in history if item.get('role') in ['user', 'ai']])
            if transcript:
                threading.Thread(target=__generate_case_token_async, args=(case_id, request.user_id, transcript), daemon=True).start()
            
            return jsonify({
                'caseId': case_id,
                'sessionId': session_id,
                'message': 'Successfully promoted chat and injected services cart.'
            }), 201

    except Exception as e:
        print(f"[Promote Chat Critical Error] {str(e)}")
        return jsonify({'error': 'Failed to promote the intelligence track'}), 500

