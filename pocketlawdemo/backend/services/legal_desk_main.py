"""
Pocket Lawyer 2.0 — LegalDesk Main Orchestrator
Main Program for handling high-level legal service workflows.
Integrates with the LegalDesk Proxy (Mock/Real) and manages database persistence. 
"""
import os
import json
import time
from database import get_db
from config import MELENTO_CLIENT_ID, MELENTO_API_KEY
from services.legal_desk_proxy import LegalDeskProxy
from resources.legal_templates import templates_library

# Initialize the proxy (replaceable bridge)
legal_desk_api = LegalDeskProxy(MELENTO_CLIENT_ID, MELENTO_API_KEY)

# Resolve uploads directory relative to the backend folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

class LegalDeskMain:
    @staticmethod
    def initiate_esign_workflow(user_id, signer_name, document_file, metadata):
        """
        Orchestration for eSign:
        1. Save document locally.
        2. Call legal_desk_api (Mock/Real).
        3. Log to database.
        """
        # Save file (assuming document_file is a Flask FileStorage object)
        filename = f"esign_{int(time.time())}_{document_file.filename}"
        upload_path = os.path.join(UPLOAD_DIR, filename)
        document_file.save(upload_path)
        
        # Call API (Mock/Real)
        response = legal_desk_api.initiate_esign(signer_name, upload_path, metadata)
        
        # Log to service_logs
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO service_logs (user_id, service_type, external_id, status, details)
                   VALUES (?, 'esign', ?, ?, ?)''',
                (user_id, response['request_id'], response['status'], json.dumps(response))
            )
            conn.commit()
            
        return response

    @staticmethod
    def initiate_estamp_workflow(user_id, form_data, document_file):
        """
        Orchestration for eStamp:
        1. Save document.
        2. Call legal_desk_api.
        3. Log to DB.
        """
        filename = f"estamp_{int(time.time())}_{document_file.filename}"
        upload_path = os.path.join(UPLOAD_DIR, filename)
        document_file.save(upload_path)
        
        response = legal_desk_api.request_estamp(
            form_data.get('state'),
            form_data.get('value'),
            form_data.get('first_party'),
            form_data.get('second_party'),
            upload_path
        )
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO service_logs (user_id, service_type, external_id, status, details)
                   VALUES (?, 'estamp', ?, ?, ?)''',
                (user_id, response['request_id'], response['status'], json.dumps(response))
            )
            conn.commit()
            
        return response

    @staticmethod
    def initiate_kyc_workflow(user_id, user_name, kyc_type):
        """
        Orchestration for eKYC.
        """
        response = legal_desk_api.start_kyc(user_name, kyc_type)
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO service_logs (user_id, service_type, external_id, status, details)
                   VALUES (?, 'kyc', ?, ?, ?)''',
                (user_id, response['session_id'], response['status'], json.dumps(response))
            )
            conn.commit()
            
        return response

    @staticmethod
    def draft_document(user_id, template_id, data):
        """
        Professional Drafting Library Engine.
        Saves the result to a file for downloading and logs to DB.
        """
        tpl = templates_library.get(template_id)
        if not tpl:
            return {"error": "Template not found"}
        
        try:
            content = tpl.format(**data)
            
            # Save to a file for download
            filename = f"draft_{template_id}_{int(time.time())}.txt"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Log to service_logs
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO service_logs (user_id, service_type, external_id, status, details)
                       VALUES (?, 'draft', ?, 'DRAFTED', ?)''',
                    (user_id, filename, json.dumps({"filename": filename, "template": template_id}))
                )
                conn.commit()
            
            return {
                "status": "DRAFTED",
                "content": content,
                "template": template_id,
                "filename": filename,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {"error": f"Missing data for template: {str(e)}"}
