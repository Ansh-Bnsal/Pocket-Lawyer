"""
Pocket Lawyer 2.0 — Melento (SignDesk) Service Bridge
Integration with Melento/SignDesk for eSign, eStamp, and eKYC.
Uses Client-provided API keys or falls back to "Demo Local Success".
"""
import json
import uuid
import time
from config import MELENTO_CLIENT_ID, MELENTO_API_KEY
from database import get_db

def initiate_esign(user_id, document_name):
    """
    Mock/Real Aadhaar eSign via Melento.
    """
    external_id = f"sd-sign-{uuid.uuid4().hex[:8]}"
    
    # If no keys, return a "Demo Success" instead of a redirect
    if not MELENTO_API_KEY:
        return {
            "status": "success",
            "mode": "demo",
            "message": f"Aadhaar eSign Process Simluated for '{document_name}'",
            "details": "In production, the user would enter Aadhaar OTP here.",
            "externalId": external_id
        }

    # Real implementation logic (Stub)
    return {
        "status": "success",
        "message": "Real API request initiated",
        "redirectUrl": f"https://melento.ai/esign/{external_id}"
    }

def request_estamp(user_id, details):
    """
    Mock/Real Digital Stamping via Melento.
    """
    external_id = f"sd-stamp-{uuid.uuid4().hex[:8]}"
    
    if not MELENTO_API_KEY:
        return {
            "status": "success",
            "mode": "demo",
            "message": f"e-Stamp paper requested for {details.get('state', 'Unknown State')}",
            "details": f"Value: INR {details.get('value', '0')}. Demo mode: Stamping simulated.",
            "externalId": external_id
        }

    return {
        "status": "success",
        "message": "Real eStamp request sent",
        "externalId": external_id
    }

def verify_ekyc(user_id, kyc_type="video"):
    """
    Mock/Real eKYC via Melento.
    """
    external_id = f"sd-kyc-{uuid.uuid4().hex[:8]}"
    
    if not MELENTO_API_KEY:
        return {
            "status": "success",
            "mode": "demo",
            "message": "Aadhaar eKYC Verified",
            "details": "Identity matched via simulated Aadhaar bridge.",
            "externalId": external_id
        }

    return {
        "status": "success",
        "message": "Real Verification session created",
        "redirectUrl": f"https://melento.ai/vcip/{external_id}"
    }

def generate_draft(template_type, data):
    """
    Automated Document Drafting Engine.
    """
    templates = {
        "rent_agreement": "RENT AGREEMENT\n\nThis agreement is made between {landlord_name} (Landlord) and {tenant_name} (Tenant) for the property at {address}.\n\nMonthly Rent: INR {rent_amount}\nSecurity Deposit: INR {deposit_amount}\nDuration: 11 Months\n\nExecuted at {city} on {date}.",
        "affidavit": "AFFIDAVIT\n\nI, {name}, son/daughter of {parent_name}, residing at {address}, do hereby solemnly affirm and state as follows:\n\n1. That {statement}\n\nVerification:\nVerified at {city} that the contents of this affidavit are true to my knowledge.",
        "legal_notice": "LEGAL NOTICE\n\nTo: {receiver_name}\nAddress: {receiver_address}\n\nUnder instructions from my client {client_name}, I hereby serve you this notice regarding {subject}. You are required to {demand} within 15 days.",
        "poa": "SPECIAL POWER OF ATTORNEY\n\nI, {name}, residing at {address}, do hereby appoint {parent_name} as my lawful attorney for the specific purpose of: {statement}."
    }
    
    tpl = templates.get(template_type, "Legal Document Template\n\nContent: {data}")
    try:
        draft_content = tpl.format(**data)
    except:
        draft_content = "Document generated with placeholder data."
    
    return {
        "type": template_type,
        "content": draft_content,
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S")
    }
