"""
Pocket Lawyer 2.0 — LegalDesk (SignDesk) Proxy
The "Replaceable" API Bridge. 
Currently returns High-Fidelity Mock JSON to mimic real SignDesk/Melento response schemas.
To switch to production, replace the methods below with real requests.post() logic.
"""
import uuid
import time
import json

class LegalDeskProxy:
    def __init__(self, client_id=None, api_key=None):
        self.client_id = client_id
        self.api_key = api_key
        self.base_url = "https://api.signdesk.com/v2" # Fake production URL

    def initiate_esign(self, signer_name, document_path, metadata=None):
        """
        Mimics SignDesk's eSign initiation endpoint.
        Returns authentic-looking JSON.
        """
        request_id = f"sd-esign-{uuid.uuid4().hex[:12]}"
        
        # MOCK RESPONSE: Structured like a real B2B Legal API
        return {
            "status": "INITIATED",
            "request_id": request_id,
            "signer_details": {
                "name": signer_name,
                "aadhaar_last_4": metadata.get('aadhaar_last_4', 'XXXX') if metadata else 'XXXX'
            },
            "document": {
                "file_path": document_path,
                "document_hash": f"sha256:{uuid.uuid4().hex}"
            },
            "urls": {
                "signing_url": f"https://sandbox.signdesk.com/esign/live/{request_id}",
                "callback_url": "http://pocket-lawyer.local/api/webhooks/esign"
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mode": "MOCK_MODE_ACTIVE"
        }

    def request_estamp(self, state, value, first_party, second_party, document_path):
        """
        Mimics SignDesk's eStamping workflow.
        """
        request_id = f"sd-stamp-{uuid.uuid4().hex[:12]}"
        
        return {
            "status": "PROCESSING",
            "request_id": request_id,
            "stamp_details": {
                "state": state,
                "value": value,
                "first_party": first_party,
                "second_party": second_party
            },
            "document": {
                "source": document_path,
                "status": "UPLOADED_TO_GOVERNMENT_PORTAL"
            },
            "estimated_tat": "4 working hours",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mode": "MOCK_MODE_ACTIVE"
        }

    def start_kyc(self, user_name, kyc_type="video"):
        """
        Mimics SignDesk's eKYC / VCIP flow.
        """
        session_id = f"sd-kyc-{uuid.uuid4().hex[:12]}"
        
        return {
            "status": "SESSION_CREATED",
            "session_id": session_id,
            "kyc_type": kyc_type,
            "user_details": {
                "name": user_name
            },
            "verification_url": f"https://sandbox.melento.ai/vcip/session/{session_id}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mode": "MOCK_MODE_ACTIVE"
        }
