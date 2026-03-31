"""
Pocket Lawyer 2.0 — Configuration
All secrets and settings are read from environment variables.
"""
import os

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
        user=os.environ.get('PGUSER', 'postgres'),
        password=os.environ.get('PGPASSWORD', 'postgres'),
        host=os.environ.get('PGHOST', 'localhost'),
        port=os.environ.get('PGPORT', '5432'),
        dbname=os.environ.get('PGDATABASE', 'pocket_lawyer'),
    )
)

# ── JWT Authentication ────────────────────────────────────────────────────────
JWT_SECRET = os.environ.get('JWT_SECRET', 'pocket-lawyer-dev-secret-change-in-production')
JWT_EXPIRY_HOURS = int(os.environ.get('JWT_EXPIRY_HOURS', '24'))

# ── AI Provider Configuration ─────────────────────────────────────────────────
# Supported: 'gemini', 'openai', 'anthropic'
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'gemini')

# Google Gemini (default — generous free tier)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# OpenAI (alternative)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Anthropic (alternative)
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# ── File Uploads ──────────────────────────────────────────────────────────────
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), 'uploads'))
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

# ── Server ────────────────────────────────────────────────────────────────────
DEBUG = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
PORT = int(os.environ.get('PORT', '5000'))
HOST = os.environ.get('HOST', '0.0.0.0')
