"""
Pocket Lawyer 2.0 — Firm Routes
Handles firm creation (Zoom-style), invite codes, member management, and case assignment.
"""
import random
import string
import uuid
from flask import Blueprint, request, jsonify
from database import get_db
from routes.auth_routes import require_auth, require_role, _hash_password, _create_token

firm_bp = Blueprint('firm', __name__)


def _generate_invite_code():
    """Generate a unique 6-char firm invite code like FIRM-K9X2AB."""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=6))
    return f"FIRM-{code}"


# ── Firm Creation (from Landing Page) ─────────────────────────────────────────

@firm_bp.route('/create', methods=['POST'])
def create_firm():
    """Create a new firm + admin account. Called from the pricing section on index.html."""
    data = request.get_json()
    firm_name = (data.get('firmName') or '').strip()
    admin_name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()
    plan = data.get('plan', 'starter')

    if not firm_name or not admin_name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    plan_limits = {'starter': 5, 'professional': 20, 'enterprise': 100}
    max_members = plan_limits.get(plan, 5)
    slug_base = firm_name.lower().replace(' ', '-').replace("'", '')
    slug = f"{slug_base}-{uuid.uuid4().hex[:6]}"
    password_hash = _hash_password(password)

    with get_db() as conn:
        cursor = conn.cursor()

        # Check existing email
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return jsonify({'error': 'An account with this email already exists'}), 409

        # Generate unique invite code
        invite_code = _generate_invite_code()
        while True:
            cursor.execute('SELECT id FROM firms WHERE invite_code = ?', (invite_code,))
            if not cursor.fetchone():
                break
            invite_code = _generate_invite_code()

        # Create firm
        cursor.execute(
            'INSERT INTO firms (name, slug, subscription_tier, max_members, invite_code) VALUES (?, ?, ?, ?, ?)',
            (firm_name, slug, plan, max_members, invite_code)
        )
        firm_id = cursor.lastrowid

        # Create admin user
        cursor.execute(
            '''INSERT INTO users (name, email, password_hash, role, firm_id, firm_role)
               VALUES (?, ?, ?, 'firm', ?, 'admin')''',
            (admin_name, email, password_hash, firm_id)
        )
        user_id = cursor.lastrowid
        conn.commit()

    token = _create_token(user_id, 'firm')

    return jsonify({
        'token': token,
        'user': {
            'id': user_id,
            'name': admin_name,
            'email': email,
            'role': 'firm',
            'firmId': firm_id,
            'firmRole': 'admin',
            'firmName': firm_name,
            'inviteCode': invite_code
        }
    }), 201


# ── Join Firm (for Lawyers) ───────────────────────────────────────────────────

@firm_bp.route('/join', methods=['POST'])
@require_auth
def join_firm():
    """Existing lawyer joins a firm using an invite code."""
    data = request.get_json()
    invite_code = (data.get('inviteCode') or '').strip().upper()

    if not invite_code:
        return jsonify({'error': 'Invite code is required'}), 400

    with get_db() as conn:
        cursor = conn.cursor()

        # Verify user is a lawyer
        cursor.execute('SELECT id, role, firm_id FROM users WHERE id = ?', (request.user_id,))
        user = cursor.fetchone()
        if not user or user['role'] != 'lawyer':
            return jsonify({'error': 'Only lawyers can join a firm'}), 403
        if user['firm_id']:
            return jsonify({'error': 'You are already a member of a firm'}), 409

        # Find firm by invite code
        cursor.execute('SELECT id, name, max_members FROM firms WHERE invite_code = ?', (invite_code,))
        firm = cursor.fetchone()
        if not firm:
            return jsonify({'error': 'Invalid invite code. Please check and try again.'}), 404

        # Check capacity
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE firm_id = ?', (firm['id'],))
        member_count = cursor.fetchone()['count']
        if member_count >= firm['max_members']:
            return jsonify({'error': 'This firm has reached its maximum member capacity'}), 409

        # Link user to firm
        cursor.execute(
            'UPDATE users SET firm_id = ?, firm_role = ? WHERE id = ?',
            (firm['id'], 'member', request.user_id)
        )
        conn.commit()

    return jsonify({
        'message': f"You have joined {firm['name']}!",
        'firmId': firm['id'],
        'firmName': firm['name'],
        'firmRole': 'member'
    }), 200


# ── Firm Members ──────────────────────────────────────────────────────────────

@firm_bp.route('/members', methods=['GET'])
@require_auth
def get_members():
    """List all firm members with their case counts."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Get user's firm
        cursor.execute('SELECT firm_id, firm_role FROM users WHERE id = ?', (request.user_id,))
        user = cursor.fetchone()
        if not user or not user['firm_id']:
            return jsonify({'error': 'You are not part of a firm'}), 403

        # Get all members
        cursor.execute('''
            SELECT u.id, u.name, u.email, u.specialization, u.experience, u.firm_role,
                   u.created_at,
                   (SELECT COUNT(*) FROM cases WHERE lawyer_id = u.id AND status = 'active') as active_cases,
                   (SELECT COUNT(*) FROM cases WHERE lawyer_id = u.id) as total_cases
            FROM users u
            WHERE u.firm_id = ?
            ORDER BY u.firm_role DESC, u.name ASC
        ''', (user['firm_id'],))
        members = cursor.fetchall()

    return jsonify(members), 200


# ── Firm Cases ────────────────────────────────────────────────────────────────

@firm_bp.route('/cases', methods=['GET'])
@require_auth
def get_firm_cases():
    """Get all firm cases. Admin = full access, Member = read-only list."""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT firm_id, firm_role FROM users WHERE id = ?', (request.user_id,))
        user = cursor.fetchone()
        if not user or not user['firm_id']:
            return jsonify({'error': 'You are not part of a firm'}), 403

        cursor.execute('''
            SELECT c.*, 
                   (SELECT name FROM users WHERE id = c.lawyer_id) as assigned_to,
                   (SELECT name FROM users WHERE id = c.client_id) as client_name
            FROM cases c
            WHERE c.firm_id = ?
            ORDER BY c.updated_at DESC
        ''', (user['firm_id'],))
        cases = cursor.fetchall()

    return jsonify(cases), 200


# ── Case Assignment ───────────────────────────────────────────────────────────

@firm_bp.route('/cases/<int:case_id>/assign', methods=['POST'])
@require_auth
def assign_case(case_id):
    """Admin assigns a case to a firm member."""
    data = request.get_json()
    member_id = data.get('memberId')

    with get_db() as conn:
        cursor = conn.cursor()

        # Verify caller is admin
        cursor.execute('SELECT firm_id, firm_role FROM users WHERE id = ?', (request.user_id,))
        user = cursor.fetchone()
        if not user or user['firm_role'] != 'admin':
            return jsonify({'error': 'Only firm admins can assign cases'}), 403

        # Verify member belongs to same firm
        cursor.execute('SELECT id, name, firm_id FROM users WHERE id = ?', (member_id,))
        member = cursor.fetchone()
        if not member or member['firm_id'] != user['firm_id']:
            return jsonify({'error': 'Member not found in your firm'}), 404

        # Assign
        cursor.execute(
            'UPDATE cases SET lawyer_id = ?, firm_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (member_id, user['firm_id'], case_id)
        )
        conn.commit()

    return jsonify({'message': f"Case assigned to {member['name']}"}), 200


# ── Case Transfer ─────────────────────────────────────────────────────────────

@firm_bp.route('/cases/<int:case_id>/transfer', methods=['POST'])
@require_auth
def transfer_case(case_id):
    """Admin transfers a case from one member to another."""
    data = request.get_json()
    to_member_id = data.get('toMemberId')

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT firm_id, firm_role FROM users WHERE id = ?', (request.user_id,))
        user = cursor.fetchone()
        if not user or user['firm_role'] != 'admin':
            return jsonify({'error': 'Only firm admins can transfer cases'}), 403

        # Verify target belongs to firm
        cursor.execute('SELECT id, name, firm_id FROM users WHERE id = ?', (to_member_id,))
        target = cursor.fetchone()
        if not target or target['firm_id'] != user['firm_id']:
            return jsonify({'error': 'Target member not found in your firm'}), 404

        cursor.execute(
            'UPDATE cases SET lawyer_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND firm_id = ?',
            (to_member_id, case_id, user['firm_id'])
        )
        conn.commit()

    return jsonify({'message': f"Case transferred to {target['name']}"}), 200


# ── Available Members (Workload) ──────────────────────────────────────────────

@firm_bp.route('/available', methods=['GET'])
@require_auth
def available_members():
    """Find members sorted by case load (ascending) — lightest load first."""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT firm_id, firm_role FROM users WHERE id = ?', (request.user_id,))
        user = cursor.fetchone()
        if not user or user['firm_role'] != 'admin':
            return jsonify({'error': 'Only firm admins can view workload'}), 403

        cursor.execute('''
            SELECT u.id, u.name, u.specialization,
                   (SELECT COUNT(*) FROM cases WHERE lawyer_id = u.id AND status = 'active') as active_cases
            FROM users u
            WHERE u.firm_id = ? AND u.firm_role = 'member'
            ORDER BY active_cases ASC
        ''', (user['firm_id'],))
        members = cursor.fetchall()

    return jsonify(members), 200


# ── Invite Code ───────────────────────────────────────────────────────────────

@firm_bp.route('/invite-code', methods=['GET'])
@require_auth
def get_invite_code():
    """Get or regenerate the firm's invite code."""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT firm_id, firm_role FROM users WHERE id = ?', (request.user_id,))
        user = cursor.fetchone()
        if not user or user['firm_role'] != 'admin':
            return jsonify({'error': 'Only firm admins can view invite code'}), 403

        cursor.execute('SELECT invite_code, name FROM firms WHERE id = ?', (user['firm_id'],))
        firm = cursor.fetchone()

    return jsonify({
        'inviteCode': firm['invite_code'],
        'firmName': firm['name']
    }), 200
