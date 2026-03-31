"""
Pocket Lawyer 2.0 — Configuration Example
Copy this file, rename it to `config.py`, and fill in your actual API keys.
This file is tracked by git. DO NOT put real keys here!
"""
import os

# ── Database ──────────────────────────────────────────────────────────────────
# By default, Pocket Lawyer 2.0 uses a local SQLite database (pocket_lawyer.db).
# If you want to use PostgreSQL, uncomment and modify the connection string below.
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///pocket_lawyer.db')

# ── JWT Authentication ────────────────────────────────────────────────────────
JWT_SECRET = os.environ.get('JWT_SECRET', 'replace-this-with-a-very-long-random-string')
JWT_EXPIRY_HOURS = int(os.environ.get('JWT_EXPIRY_HOURS', '24'))

# ── AI Provider Configuration ─────────────────────────────────────────────────
# Supported limits: 'gemini', 'openai', 'anthropic'
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'gemini')

# Google Gemini (default — get your free key at https://aistudio.google.com/app/apikey)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# OpenAI (alternative)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Anthropic (alternative)
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# ── File Uploads ──────────────────────────────────────────────────────────────
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), 'uploads'))
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB file limit
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

# ── Server ────────────────────────────────────────────────────────────────────
DEBUG = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
PORT = int(os.environ.get('PORT', '5000'))
HOST = os.environ.get('HOST', '0.0.0.0')
