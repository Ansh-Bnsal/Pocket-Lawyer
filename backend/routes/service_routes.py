"""
Pocket Lawyer 2.0 — Legal Service Routes
Endpoints for appointments and Melento (SignDesk) integration.
"""
from flask import Blueprint, request, jsonify, send_from_directory
import os
from database import get_db
from routes.auth_routes import require_auth
from services.legal_desk_main import LegalDeskMain, UPLOAD_DIR

service_bp = Blueprint('services', __name__)


# ── Appointments ──────────────────────────────────────────────────────────────
# (Same appointments code as before)
@service_bp.route('/appointments', methods=['GET'])
@require_auth
def list_appointments():
    with get_db() as conn:
        cursor = conn.cursor()
        if request.user_role == 'client':
            cursor.execute(
                '''SELECT a.*, u.name as lawyer_name, u.specialization 
                   FROM appointments a
                   LEFT JOIN users u ON a.lawyer_id = u.id
                   WHERE a.client_id = ? ORDER BY a.scheduled_at ASC''',
                (request.user_id,)
            )
        else:
            cursor.execute(
                '''SELECT a.*, u.name as client_name 
                   FROM appointments a
                   LEFT JOIN users u ON a.client_id = u.id
                   WHERE a.lawyer_id = ? ORDER BY a.scheduled_at ASC''',
                (request.user_id,)
            )
        rows = cursor.fetchall()
    return jsonify([dict(r) for r in rows]), 200


@service_bp.route('/appointments/book', methods=['POST'])
@require_auth
def book_appointment():
    data = request.get_json()
    lawyer_id = data.get('lawyerId')
    scheduled_at = data.get('dateTime')
    notes = data.get('notes', '')
    case_id = data.get('caseId')

    if not lawyer_id or not scheduled_at:
        return jsonify({'error': 'lawyerId and dateTime are required'}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO appointments (client_id, lawyer_id, case_id, scheduled_at, notes)
               VALUES (?, ?, ?, ?, ?)''',
            (request.user_id, lawyer_id, case_id, scheduled_at, notes)
        )
        conn.commit()
    return jsonify({'message': 'Appointment booked successfully'}), 201


# ── Production-Grade LegalDesk Implementation ─────────────────────────────────

@service_bp.route('/services/list', methods=['GET'])
@require_auth
def list_available_services():
    services = [
        {"id": "rent_agreement_residential", "name": "Rent Agreement — Residential", "desc": "Professional 11-month residential rental agreement with all mandatory clauses.", "price": "₹449", "price_raw": 449, "require_doc": False, "category": "drafting"},
        {"id": "rent_agreement_commercial", "name": "Rent Agreement — Commercial", "desc": "Commercial/office space rental agreement with business-specific terms.", "price": "₹549", "price_raw": 549, "require_doc": False, "category": "drafting"},
        {"id": "affidavit", "name": "General Affidavit", "desc": "Draft legally valid self-declaration affidavits for any purpose.", "price": "₹279", "price_raw": 279, "require_doc": False, "category": "drafting"},
        {"id": "poa", "name": "Power of Attorney", "desc": "Draft a Special Power of Attorney for property, banking, or legal representation.", "price": "₹849", "price_raw": 849, "require_doc": False, "category": "drafting"},
        {"id": "legal_notice", "name": "Legal Notice", "desc": "Draft a formal legal notice for disputes, refund demands, cheque bounce, or harassment.", "price": "₹749", "price_raw": 749, "require_doc": False, "category": "drafting"},
        {"id": "will", "name": "Last Will & Testament", "desc": "Create a legally binding will for estate planning and asset distribution.", "price": "₹499", "price_raw": 499, "require_doc": False, "category": "drafting"},
        {"id": "nda", "name": "Non-Disclosure Agreement", "desc": "Protect business secrets with a professional NDA for startups and partnerships.", "price": "₹449", "price_raw": 449, "require_doc": False, "category": "drafting"},
        {"id": "gift_deed", "name": "Gift Deed", "desc": "Transfer property or assets to a family member or third party through a legal gift deed.", "price": "₹599", "price_raw": 599, "require_doc": False, "category": "drafting"},
        {"id": "employment_contract", "name": "Employment Contract", "desc": "Draft professional employment agreements covering salary, terms, and obligations.", "price": "₹499", "price_raw": 499, "require_doc": False, "category": "drafting"},
        {"id": "esign", "name": "Aadhaar eSign", "desc": "Sign legally binding documents with Aadhaar OTP verification.", "price": "₹229", "price_raw": 229, "require_doc": True, "category": "infrastructure"},
        {"id": "estamp", "name": "Digital Stamp Paper", "desc": "Purchase government-verified e-stamp papers for any state.", "price": "₹119 + Stamp Duty", "price_raw": 119, "require_doc": True, "category": "infrastructure"},
        {"id": "kyc", "name": "Video KYC (VCIP)", "desc": "Securely verify your identity for legal matters via video call.", "price": "₹139", "price_raw": 139, "require_doc": False, "category": "infrastructure"},
        {"id": "lawyer_appointment", "name": "Lawyer Consultation", "desc": "Book a consultation with a specialist lawyer matched to your case type.", "price": "₹499", "price_raw": 499, "require_doc": False, "category": "consultation"}
    ]
    return jsonify(services), 200


@service_bp.route('/services/esign', methods=['POST'])
@require_auth
def request_esign_api():
    # Handle Multipart/Form-Data for file attachment
    signer_name = request.form.get('signerName', 'Legal Client')
    aadhaar_last_4 = request.form.get('aadhaarLast4', 'XXXX')
    document = request.files.get('document')

    if not document:
        return jsonify({'error': 'Document attachment required for eSign'}), 400

    res = LegalDeskMain.initiate_esign_workflow(
        request.user_id, 
        signer_name, 
        document, 
        {"aadhaar_last_4": aadhaar_last_4}
    )
    return jsonify(res), 200


@service_bp.route('/services/estamp', methods=['POST'])
@require_auth
def request_estamp_api():
    state = request.form.get('state')
    value = request.form.get('value')
    first_party = request.form.get('firstParty')
    second_party = request.form.get('secondParty')
    document = request.files.get('document')

    if not document or not state or not value:
        return jsonify({'error': 'State, Value, and Document are required for eStamp'}), 400

    res = LegalDeskMain.initiate_estamp_workflow(
        request.user_id,
        {"state": state, "value": value, "first_party": first_party, "second_party": second_party},
        document
    )
    return jsonify(res), 200


@service_bp.route('/services/kyc', methods=['POST'])
@require_auth
def request_kyc_api():
    data = request.get_json()
    res = LegalDeskMain.initiate_kyc_workflow(
        request.user_id, 
        request.user_name, 
        data.get('kyc_type', 'video')
    )
    return jsonify(res), 200


@service_bp.route('/services/draft', methods=['POST'])
@require_auth
def request_draft_api():
    data = request.get_json()
    template = data.get('template')
    tpl_data = data.get('data', {})
    res = LegalDeskMain.draft_document(request.user_id, template, tpl_data)
    if "error" in res:
        return jsonify(res), 400
    return jsonify(res), 200


@service_bp.route('/services/download/<filename>', methods=['GET'])
@require_auth
def download_service_file(filename):
    """
    Securely serve files for download.
    """
    # Clean filename to prevent traversal
    safe_filename = os.path.basename(filename)
    return send_from_directory(UPLOAD_DIR, safe_filename, as_attachment=True)


@service_bp.route('/services/logs', methods=['GET'])
@require_auth
def list_service_logs():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM service_logs WHERE user_id = ? ORDER BY created_at DESC',
            (request.user_id,)
        )
        rows = cursor.fetchall()
    return jsonify([dict(r) for r in rows]), 200

# ── Case-Specific Suggestions (Smart Cart) ───────────────────────────────────

@service_bp.route('/cases/<int:case_id>/suggestions', methods=['GET'])
@require_auth
def list_case_suggestions(case_id):
    """
    Fetch all 'pending' suggestions for a specific case.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM case_services WHERE case_id = ? AND status = "pending" ORDER BY created_at DESC',
            (case_id,)
        )
        rows = cursor.fetchall()
    return jsonify([dict(r) for r in rows]), 200


@service_bp.route('/services/suggestions/<int:suggestion_id>/status', methods=['POST'])
@require_auth
def update_suggestion_status(suggestion_id):
    """
    Update status of an AI suggestion (e.g. to 'dismissed' or 'initiated').
    """
    data = request.get_json()
    new_status = data.get('status', 'dismissed')
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE case_services SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (new_status, suggestion_id)
        )
        conn.commit()
    return jsonify({'message': f'Suggestion {new_status}'}), 200
