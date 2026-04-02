"""
Pocket Lawyer 2.0 - Triple-Process AI Orchestrator
Strictly isolates the AI thread-pool execution and context generation away from the HTTP routes.
"""
import json
import threading
from database import get_db
from services.ai import ai

class AIOrchestrator:
    @staticmethod
    def process_chat_stream(message: str, file_data: dict, session_id: int, case_id: int, user_role: str, case_context: str):
        """
        Generator function that orchestrates the 3 workers and yields the SSE chunks.
        """
        run_background_workers = (user_role == 'client')
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
                            with get_db() as conn:
                                cursor = conn.cursor()
                                m_key = res.data.get('merge_key', 'default')
                                cursor.execute('SELECT id FROM case_services WHERE case_id = ? AND merge_key = ? AND status = "pending"', (case_id, m_key))
                                if not cursor.fetchone():
                                    cursor.execute('''INSERT INTO case_services (case_id, service_type, title, merge_key, extracted_data)
                                                   VALUES (?, ?, ?, ?, ?)''', (case_id, res.data['next_step'], res.data['title'], m_key, json.dumps(res.data.get('extracted_data'))))
                                    conn.commit()
                except Exception as e: 
                    print(f"[Worker B Error] {e}")

            # Worker C: Risk Analyst (Multimodal)
            def _run_worker_c():
                try:
                    res = ai.ask("doc_analysis", message or "Analyze risks", file_data=file_data)
                    if res.data: 
                        worker_c_result[0] = res.data
                except Exception as e: 
                    print(f"[Worker C Error] {e}")

            t_b = threading.Thread(target=_run_worker_b, daemon=True)
            threads.append(t_b)
            t_b.start()

            if file_data:
                t_c = threading.Thread(target=_run_worker_c, daemon=True)
                threads.append(t_c)
                t_c.start()

        # Step 2: Stream Worker A (Realtime Conversation)
        print(f"[AI Orchestrator] Stream Start: {session_id}")
        full_response = []
        yield f"event: metadata\ndata: {json.dumps({'sessionId': session_id})}\n\n"
        
        stream_task = "chat_doc" if file_data else "chat"
        enhanced_message = message
        if not message and file_data: 
            enhanced_message = "Analyze this document"

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
        for t in threads: 
            t.join(timeout=10) # Wait max 10s for workers to finish
        
        if worker_b_result[0]:
            yield f"event: intent\ndata: {json.dumps(worker_b_result[0])}\n\n"
        if worker_c_result[0]:
            yield f"event: document\ndata: {json.dumps(worker_c_result[0])}\n\n"
            
        yield "event: close\ndata: {}\n\n"
