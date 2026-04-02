"""
Pocket Lawyer 2.0 — Auth Routes
JWT-based authentication for Client, Lawyer, and Law Firm roles.
"""
import hashlib
import hmac
import json
import time
import base64
from flask import Blueprint, request, jsonify
from database import get_db
from config import JWT_SECRET, JWT_EXPIRY_HOURS
from functools import wraps

auth_bp = Blueprint('auth', __name__)


# ── JWT Helpers ───────────────────────────────────────────────────────────────

def _hash_password(password):
    """Hash password with SHA-256 + salt. Not bcrypt for simplicity — upgrade for production."""
    salt = 'pocket-lawyer-salt'
    return hashlib.sha256(f'{salt}{password}'.encode()).hexdigest()


def _create_token(user_id, role):
    """Create a simple JWT-like token."""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': int(time.time()) + (JWT_EXPIRY_HOURS * 3600)
    }
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(JWT_SECRET.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f'{payload_b64}.{signature}'


def _decode_token(token):
    """Decode and verify a token. Returns payload dict or None."""
    try:
        parts = token.split('.')
        if len(parts) != 2:
            return None
        payload_b64, signature = parts
        expected_sig = hmac.new(JWT_SECRET.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        if payload.get('exp', 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def require_auth(f):
    """Decorator to require authentication on a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        elif 'token' in request.args:
            token = request.args.get('token')
            
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
            
        payload = _decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        request.user_id = payload['user_id']
        request.user_role = payload['role']
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """Decorator to require specific role(s)."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.user_role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()
    role = data.get('role', 'client')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    if role not in ('client', 'lawyer'):
        return jsonify({'error': 'Invalid role. Use client or lawyer. Firms are created from the pricing page.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    password_hash = _hash_password(password)

    with get_db() as conn:
        cursor = conn.cursor()

        # Check existing email
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return jsonify({'error': 'An account with this email already exists'}), 409

        # Handle invite code for lawyers joining a firm
        firm_id = None
        firm_role = None
        firm_name = None
        invite_code = (data.get('inviteCode') or '').strip().upper()

        if role == 'lawyer' and invite_code:
            cursor.execute('SELECT id, name, max_members FROM firms WHERE invite_code = ?', (invite_code,))
            firm = cursor.fetchone()
            if not firm:
                return jsonify({'error': 'Invalid firm invite code. Please check and try again.'}), 404

            # Check capacity
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE firm_id = ?', (firm['id'],))
            member_count = cursor.fetchone()['count']
            if member_count >= firm['max_members']:
                return jsonify({'error': 'This firm has reached its maximum member capacity'}), 409

            firm_id = firm['id']
            firm_role = 'member'
            firm_name = firm['name']

        # Create user
        cursor.execute(
            '''INSERT INTO users (name, email, password_hash, role, firm_id, firm_role, specialization, experience, bar_number)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (name, email, password_hash, role, firm_id, firm_role,
             data.get('specialization'), data.get('experience'), data.get('barNumber'))
        )
        user_id = cursor.lastrowid
        conn.commit()

    token = _create_token(user_id, role)

    return jsonify({
        'token': token,
        'user': {
            'id': user_id,
            'name': name,
            'email': email,
            'role': role,
            'firmId': firm_id,
            'firmRole': firm_role,
            'firmName': firm_name
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    password_hash = _hash_password(password)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name, email, role, firm_id, firm_role, specialization, experience, bar_number FROM users WHERE email = ? AND password_hash = ?',
            (email, password_hash)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        user = dict(user)

        # Get firm name if user belongs to a firm
        firm_name = None
        if user['firm_id']:
            cursor.execute('SELECT name FROM firms WHERE id = ?', (user['firm_id'],))
            firm = cursor.fetchone()
            if firm:
                firm_name = firm['name']

    token = _create_token(user['id'], user['role'])

    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'firmId': user['firm_id'],
            'firmRole': user['firm_role'],
            'firmName': firm_name,
            'specialization': user['specialization'],
            'experience': user['experience'],
            'barNumber': user['bar_number']
        }
    }), 200


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_me():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name, email, role, firm_id, specialization, experience, bar_number, created_at FROM users WHERE id = ?',
            (request.user_id,)
        )
        user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'user': dict(user)}), 200
