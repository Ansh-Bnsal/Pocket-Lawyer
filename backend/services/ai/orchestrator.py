import json
import threading
import time
from database import get_db
from services.ai import ai

class AIOrchestrator:
    @staticmethod
    def process_chat_stream(message: str, file_data: dict, session_id: int, case_id: int, user_role: str, case_context: str, history: list = None, is_transient: bool = False):
        """
        Generator function that orchestrates the 3 workers and yields the SSE chunks.
        """
        safe_context = (case_context or "")[:10000] 
        print(f"[AI Orchestrator] Stream Start: {session_id} | Memory: {'Yes' if history else 'No'}")
        
        worker_b_result = [None] # Intent / Cart Manager
        worker_c_result = [None] # Risk Analyst
        threads = []

        # Background Workers (Staggered by 500ms to prevent 429 burst)
        if user_role == 'client':
            # Worker B: Intent Manager
            def _run_worker_b():
                time.sleep(0.5) # [Burst Shield]
                try:
                    print(f"[Worker B] Firing Intent Extractor...")
                    res = ai.ask("intent_extractor", message or ("User uploaded a document." if file_data else "Reviewing context"), file_data=file_data, context=safe_context, history=history)
                    print(f"[Worker B] RAW AI RESPONSE: {res.text}")
                    print(f"[Worker B] PARSED AI DATA: {res.data}")
                    
                    if res.data and (res.data.get('next_step') or res.data.get('is_case_worthy')):
                        worker_b_result[0] = res.data
                        if not is_transient and case_id and res.data.get('next_step'):
                            with get_db() as conn:
                                cursor = conn.cursor()
                                m_key = res.data.get('merge_key', 'default')
                                cursor.execute('SELECT id FROM case_services WHERE case_id = ? AND merge_key = ? AND status = "pending"', (case_id, m_key))
                                if not cursor.fetchone():
                                    cursor.execute('''INSERT INTO case_services (case_id, service_type, title, merge_key, extracted_data)
                                                   VALUES (?, ?, ?, ?, ?)''', (case_id, res.data['next_step'], res.data['title'], m_key, json.dumps(res.data.get('extracted_data'))))
                                    conn.commit()
                except Exception as e: 
                    print(f"[Worker B CRASHED] {e}")

            t_b = threading.Thread(target=_run_worker_b, daemon=True)
            threads.append(t_b)
            t_b.start()

            if file_data:
                # Worker C: Risk Analyst
                def _run_worker_c():
                    time.sleep(1.0) # [Burst Shield Extended]
                    try:
                        res = ai.ask("doc_analysis", message or "Analyze risks", file_data=file_data)
                        if res.data: 
                            worker_c_result[0] = res.data
                    except Exception as e: 
                        print(f"[Worker C Suppressed] {e}")

                t_c = threading.Thread(target=_run_worker_c, daemon=True)
                threads.append(t_c)
                t_c.start()

        # Step 2: Stream Worker A (Realtime Conversation)
        full_response = []
        if not is_transient:
            yield f"event: metadata\ndata: {json.dumps({'sessionId': session_id})}\n\n"
        
        stream_task = "chat_doc" if file_data else "chat"
        enhanced_message = message or ("Analyze this document" if file_data else "Review context")

        try:
            # Note: No delay on the main chat stream
            for chunk in ai.ask_stream(stream_task, enhanced_message, file_data=file_data, context=safe_context, history=history):
                if chunk:
                    full_response.append(chunk)
                    yield f"event: message\ndata: {json.dumps({'text': chunk})}\n\n"
        except Exception as e:
            print(f"[Chat Error] {e}")
            is_limit = True if '429' in str(e) or 'api_limit' in str(e) else False
            yield f"event: error\ndata: {json.dumps({'error': 'Engine Interruption', 'type': 'api_limit' if is_limit else 'engine_error'})}\n\n"
            return
            
        # [Save] Only if NOT transient
        final_text = "".join(full_response)
        if not is_transient and final_text:
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
            t.join(timeout=25) 
        
        if worker_b_result[0]:
            yield f"event: intent\ndata: {json.dumps(worker_b_result[0])}\n\n"
        if worker_c_result[0]:
            yield f"event: document\ndata: {json.dumps(worker_c_result[0])}\n\n"
            
        yield "event: close\ndata: {}\n\n"
