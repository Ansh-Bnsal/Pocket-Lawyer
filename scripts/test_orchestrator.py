from backend.app import create_app
from backend.services.ai.orchestrator import AIOrchestrator

app = create_app()

with app.app_context():
    print("Testing AI Orchestrator directly...")
    try:
        stream = AIOrchestrator.process_chat_stream(
            message="I face ragging",
            file_data=None,
            session_id=1,
            case_id=None,
            user_role="client",
            case_context="",
            is_transient=True
        )
        for chunk in stream:
            print(chunk)
    except Exception as e:
        import traceback
        traceback.print_exc()
