"""
Pocket Lawyer 2.0 — Upload Routes
Document upload with text extraction, AI summarization, and risk analysis.
"""
import os
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from database import get_db
from services.file_service import extract_text, allowed_file
from services.ai_service import analyze_document
from routes.auth_routes import require_auth

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    case_id = request.form.get('case_id')
    if not case_id:
        return jsonify({'error': 'case_id is required'}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM cases WHERE id = ?', (case_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Case not found'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use PDF, TXT, DOC, or DOCX.'}), 400

    filename = secure_filename(file.filename)
    case_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(case_id))
    os.makedirs(case_folder, exist_ok=True)
    file_path = os.path.join(case_folder, filename)
    file.save(file_path)

    file_size = os.path.getsize(file_path)

    extracted_text = extract_text(file_path)

    ai_summary = ''
    risk_analysis = None
    if extracted_text and not extracted_text.startswith('['):
        try:
            ai_result = analyze_document(extracted_text)
            ai_summary = ai_result.get('simplifiedExplanation', '')
            risk_analysis = ai_result
        except Exception as e:
            ai_summary = f'[AI analysis failed: {str(e)}]'
            risk_analysis = {'error': str(e)}

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO documents (case_id, filename, file_path, file_size, extracted_text, ai_summary, risk_analysis, uploaded_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (case_id, filename, file_path, file_size, extracted_text, ai_summary,
             json.dumps(risk_analysis) if risk_analysis else None, request.user_id)
        )
        doc_id = cursor.lastrowid
        
        cursor.execute('SELECT uploaded_at FROM documents WHERE id = ?', (doc_id,))
        uploaded_at = cursor.fetchone()['uploaded_at']

        cursor.execute(
            '''INSERT INTO case_timeline (case_id, event_type, title, description, actor_id)
               VALUES (?, 'document_uploaded', 'Document Uploaded', ?, ?)''',
            (case_id, f'Document "{filename}" was uploaded and analyzed by AI.', request.user_id)
        )
        conn.commit()

    return jsonify({
        'id': doc_id,
        'caseId': int(case_id),
        'filename': filename,
        'fileSize': file_size,
        'summary': ai_summary,
        'riskAnalysis': risk_analysis,
        'uploadedAt': uploaded_at
    }), 201


@upload_bp.route('/documents/<int:doc_id>', methods=['GET'])
@require_auth
def get_document(doc_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, case_id, filename, file_size, extracted_text, ai_summary, risk_analysis, uploaded_at FROM documents WHERE id = ?',
            (doc_id,)
        )
        doc = cursor.fetchone()

    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    return jsonify(dict(doc)), 200


@upload_bp.route('/documents/<int:doc_id>/risks', methods=['GET'])
@require_auth
def get_document_risks(doc_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT extracted_text, risk_analysis FROM documents WHERE id = ?',
            (doc_id,)
        )
        doc = cursor.fetchone()

    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    return jsonify({
        'text': doc['extracted_text'],
        'risks': doc['risk_analysis']
    }), 200
