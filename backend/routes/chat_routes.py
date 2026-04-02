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
        file_data = None
    else:
        message = request.form.get('message', '').strip()
        session_id = request.form.get('sessionId')
        case_id = request.form.get('caseId')
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

    # [Setup] Init Session
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

    # [Parallel] WORKER ORCHESTRATION
    # Workers only run for 'client' roles. Lawyers/Firms get streamlined responses.
    run_background_workers = (request.user_role == 'client')
    worker_b_result = [None] # Cart Manager
    worker_c_result = [None] # Risk Analyst
    threads = []

    if run_background_workers:
        # Worker B: Intent / Cart Manager
        def _run_worker_b():
            try:
                res = ai.ask("intent_extractor", message or "Reviewing context", context=case_context)
                if res.data and res.data.get('next_step'):
                    worker_b_result[0] = res.data
                    # Thread-safe database update for SQLite
                    if case_id:
                        from database import get_db
                        with get_db() as conn:
                            cursor = conn.cursor()
                            m_key = res.data.get('merge_key', 'default')
                            cursor.execute('SELECT id FROM case_services WHERE case_id = ? AND merge_key = ? AND status = "pending"', (case_id, m_key))
                            if not cursor.fetchone():
                                cursor.execute('''INSERT INTO case_services (case_id, service_type, title, merge_key, extracted_data)
                                               VALUES (?, ?, ?, ?, ?)''', (case_id, res.data['next_step'], res.data['title'], m_key, json.dumps(res.data.get('extracted_data'))))
                                conn.commit()
            except Exception as e: print(f"[Worker B Error] {e}")

        # Worker C: Risk Analyst (Multimodal)
        def _run_worker_c():
            try:
                res = ai.ask("doc_analysis", message or "Analyze risks", file_data=file_data)
                if res.data: worker_c_result[0] = res.data
            except Exception as e: print(f"[Worker C Error] {e}")

        t_b = threading.Thread(target=_run_worker_b, daemon=True)
        threads.append(t_b)
        t_b.start()

        if file_data:
            t_c = threading.Thread(target=_run_worker_c, daemon=True)
            threads.append(t_c)
            t_c.start()

    def generate():
        print(f"[Chat] Stream Start: {session_id}")
        full_response = []
        yield f"event: metadata\ndata: {json.dumps({'sessionId': session_id})}\n\n"
        
        # Step 2: Stream Worker A (Realtime Conversation)
        stream_task = "chat_doc" if file_data else "chat"
        enhanced_message = message
        if not message and file_data: enhanced_message = "Analyze this document"

        try:
            for chunk in ai.ask_stream(stream_task, enhanced_message, file_data=file_data, context=case_context):
                if chunk:
                    full_response.append(chunk)
                    yield f"event: message\ndata: {json.dumps({'text': chunk})}\n\n"
        except Exception as e:
            print(f"[Chat Error] Stream: {str(e)}")
            yield f"event: message\ndata: {json.dumps({'text': f'[Engine Error: {e}]'})}\n\n"
            
        # [Save] Store conversation history
        final_text = "".join(full_response)
        if final_text:
            try:
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)', (session_id, 'ai', final_text))
                    cursor.execute('UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (session_id,))
                    conn.commit()
            except Exception as dbe:
                print(f"[Chat History Error] {str(dbe)}")
            
        # Step 4: Synchronize Background Results
        for t in threads: t.join(timeout=10) # Wait max 10s for workers to finish
        
        if worker_b_result[0]:
            yield f"event: intent\ndata: {json.dumps(worker_b_result[0])}\n\n"
        if worker_c_result[0]:
            yield f"event: document\ndata: {json.dumps(worker_c_result[0])}\n\n"
            
        yield "event: close\ndata: {}\n\n"

    return Response(generate(), mimetype='text/event-stream')

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
