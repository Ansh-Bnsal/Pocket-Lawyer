"""
Pocket Lawyer 2.0 — Case Routes
CRUD operations, AI analysis, Case Token generation, and transfer.
"""
import json
import uuid
import datetime
from flask import Blueprint, request, jsonify
from database import get_db
from services.ai import ai
from routes.auth_routes import require_auth

case_bp = Blueprint('cases', __name__)

@case_bp.route('/cases', methods=['POST'])
@require_auth
def create_case():
    """Create a new case with AI-powered structuring."""
    data = request.get_json()
    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    case_type = data.get('caseType', data.get('type', ''))
    risk_level = data.get('riskLevel', 'medium')

    if not title or not description:
        return jsonify({'error': 'Title and description are required'}), 400

    # 🧠 AI ANALYSIS (Gateway)
    try:
        result = ai.ask("analyze_case", description)
        ai_summary = result.text
        ai_result = result.data
        if not case_type:
            case_type = ai_result.get('caseClassification', 'General')
        ai_risk = ai_result.get('riskLevel', '').lower()
        if ai_risk in ('high', 'medium', 'low'):
            risk_level = ai_risk
    except Exception as e:
        ai_result = {'error': str(e)}
        ai_summary = f'[AI analysis failed: {str(e)}]'

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute(
            '''INSERT INTO cases (client_id, title, case_type, description, risk_level, ai_summary)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (request.user_id, title, case_type, description, risk_level, ai_summary)
        )
        case_id = cursor.lastrowid
        
        cursor.execute('SELECT created_at FROM cases WHERE id = ?', (case_id,))
        created_at = cursor.fetchone()['created_at']

        token_data = {
            'tokenId': str(uuid.uuid4()),
            'metadata': {
                'caseId': case_id,
                'status': 'active',
                'originRole': request.user_role,
                'createdAt': str(created_at)
            },
            'rawInput': description,
            'structuredBreakdown': ai_result
        }

        cursor.execute(
            '''INSERT INTO case_tokens (case_id, token_data, owner_id)
               VALUES (?, ?, ?)''',
            (case_id, json.dumps(token_data), request.user_id)
        )

        cursor.execute(
            '''INSERT INTO case_timeline (case_id, event_type, title, description, actor_id)
               VALUES (?, 'created', 'Case Created', ?, ?)''',
            (case_id, f'Case "{title}" was created and structured by AI.', request.user_id)
        )

        conn.commit()

    return jsonify({
        'id': case_id,
        'title': title,
        'caseType': case_type,
        'description': description,
        'riskLevel': risk_level,
        'aiSummary': ai_summary,
        'aiAnalysis': ai_result,
        'createdAt': created_at
    }), 201


@case_bp.route('/cases', methods=['GET'])
@require_auth
def list_cases():
    """List cases based on user role."""
    with get_db() as conn:
        cursor = conn.cursor()

        if request.user_role == 'client':
            cursor.execute(
                '''SELECT c.*, u.name as lawyer_name FROM cases c
                   LEFT JOIN users u ON c.lawyer_id = u.id
                   WHERE c.client_id = ? ORDER BY c.updated_at DESC''',
                (request.user_id,)
            )
        elif request.user_role == 'lawyer':
            cursor.execute(
                '''SELECT c.*, u.name as client_name FROM cases c
                   LEFT JOIN users u ON c.client_id = u.id
                   WHERE c.lawyer_id = ? ORDER BY c.updated_at DESC''',
                (request.user_id,)
            )
        elif request.user_role == 'firm':
            cursor.execute('SELECT firm_id FROM users WHERE id = ?', (request.user_id,))
            user = cursor.fetchone()
            firm_id = user['firm_id'] if user else None
            cursor.execute(
                '''SELECT c.*, u1.name as client_name, u2.name as lawyer_name FROM cases c
                   LEFT JOIN users u1 ON c.client_id = u1.id
                   LEFT JOIN users u2 ON c.lawyer_id = u2.id
                   WHERE c.firm_id = ? ORDER BY c.updated_at DESC''',
                (firm_id,)
            )
        else:
            return jsonify([]), 200

        rows = cursor.fetchall()

    return jsonify([dict(r) for r in rows]), 200


@case_bp.route('/cases/<int:case_id>', methods=['GET'])
@require_auth
def get_case(case_id):
    """Get full case details including documents, notes, hearings, and timeline."""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM cases WHERE id = ?', (case_id,))
        case = cursor.fetchone()
        if not case:
            return jsonify({'error': 'Case not found'}), 404

        cursor.execute(
            'SELECT id, filename, file_size, ai_summary, risk_analysis, uploaded_at FROM documents WHERE case_id = ? ORDER BY uploaded_at DESC',
            (case_id,)
        )
        documents = [dict(r) for r in cursor.fetchall()]

        cursor.execute(
            '''SELECT cn.*, u.name as author_name FROM case_notes cn
               LEFT JOIN users u ON cn.author_id = u.id
               WHERE cn.case_id = ? ORDER BY cn.created_at DESC''',
            (case_id,)
        )
        notes = [dict(r) for r in cursor.fetchall()]

        cursor.execute(
            'SELECT * FROM hearings WHERE case_id = ? ORDER BY hearing_date ASC',
            (case_id,)
        )
        hearings = [dict(r) for r in cursor.fetchall()]

        cursor.execute(
            '''SELECT ct.*, u.name as actor_name FROM case_timeline ct
               LEFT JOIN users u ON ct.actor_id = u.id
               WHERE ct.case_id = ? ORDER BY ct.created_at DESC''',
            (case_id,)
        )
        timeline = [dict(r) for r in cursor.fetchall()]

        cursor.execute(
            'SELECT token_data FROM case_tokens WHERE case_id = ? AND is_frozen = 0 ORDER BY version DESC LIMIT 1',
            (case_id,)
        )
        token_row = cursor.fetchone()

    result = dict(case)
    result['documents'] = documents
    result['notes'] = notes
    result['hearings'] = hearings
    result['timeline'] = timeline
    result['token'] = token_row['token_data'] if token_row else None

    return jsonify(result), 200


@case_bp.route('/cases/<int:case_id>/token/export', methods=['GET'])
@require_auth
def export_token(case_id):
    """Export the case token as a portable JSON object."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT token_data FROM case_tokens WHERE case_id = ? AND is_frozen = 0 ORDER BY version DESC LIMIT 1',
            (case_id,)
        )
        token_row = cursor.fetchone()

    if not token_row:
        return jsonify({'error': 'No active token found for this case'}), 404

    return jsonify(token_row['token_data']), 200


@case_bp.route('/cases/<int:case_id>/assign', methods=['POST'])
@require_auth
def assign_lawyer(case_id):
    """Assign a lawyer to a case."""
    data = request.get_json()
    lawyer_id = data.get('lawyerId')

    if not lawyer_id:
        return jsonify({'error': 'lawyerId is required'}), 400

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT name FROM users WHERE id = ? AND role = ?', (lawyer_id, 'lawyer'))
        lawyer = cursor.fetchone()
        if not lawyer:
            return jsonify({'error': 'Lawyer not found'}), 404

        cursor.execute(
            'UPDATE cases SET lawyer_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (lawyer_id, case_id)
        )

        cursor.execute(
            '''INSERT INTO case_timeline (case_id, event_type, title, description, actor_id)
               VALUES (?, 'lawyer_assigned', 'Lawyer Assigned', ?, ?)''',
            (case_id, f'Lawyer {lawyer["name"]} was assigned to this case.', request.user_id)
        )

        conn.commit()

    return jsonify({'message': f'Lawyer {lawyer["name"]} assigned successfully'}), 200


@case_bp.route('/cases/<int:case_id>/notes', methods=['POST'])
@require_auth
def add_note(case_id):
    """Add a date-wise note to a case."""
    data = request.get_json()
    content = (data.get('content') or '').strip()
    hearing_date = data.get('hearingDate')

    if not content:
        return jsonify({'error': 'Note content is required'}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO case_notes (case_id, author_id, hearing_date, content)
               VALUES (?, ?, ?, ?)''',
            (case_id, request.user_id, hearing_date, content)
        )
        note_id = cursor.lastrowid
        cursor.execute('SELECT id, created_at FROM case_notes WHERE id = ?', (note_id,))
        note = cursor.fetchone()

        cursor.execute(
            '''INSERT INTO case_timeline (case_id, event_type, title, description, actor_id)
               VALUES (?, 'note_added', 'Note Added', ?, ?)''',
            (case_id, f'A note was added to the case.', request.user_id)
        )

        conn.commit()

    return jsonify({'id': note['id'], 'createdAt': note['created_at']}), 201


@case_bp.route('/search', methods=['GET'])
@require_auth
def search_cases():
    """Simple text search for SQLite."""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([]), 200
        
    term = f"%{q}%"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, case_type, risk_level, status, created_at
            FROM cases
            WHERE search_text LIKE ? OR title LIKE ?
            LIMIT 20
        ''', (term, term))
        rows = cursor.fetchall()

    return jsonify([dict(r) for r in rows]), 200
