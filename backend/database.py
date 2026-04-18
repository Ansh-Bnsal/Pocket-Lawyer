"""
Pocket Lawyer 2.0 — Database Layer (SQLite version)
Adapted for SQLite so it runs out-of-the-box without requiring PostgreSQL.
"""
import sqlite3
import json
from contextlib import contextmanager
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'pocket_lawyer.db')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        # Handle JSON strings seamlessly for token_data and risk_analysis
        val = row[idx]
        if col[0] in ['token_data', 'risk_analysis', 'structured_data', 'extracted_data'] and val:
            try:
                val = json.loads(val)
            except:
                pass
        d[col[0]] = val
    return d

def init_pool():
    """No-op for SQLite."""
    pass

@contextmanager
def get_db():
    """Context manager for SQLite connection."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = dict_factory
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Idempotent schema setup for SQLite."""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS firms (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT        NOT NULL,
                slug            TEXT        UNIQUE,
                subscription_tier TEXT      DEFAULT 'starter',
                max_members     INTEGER     DEFAULT 5,
                invite_code     TEXT        UNIQUE,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                firm_id         INTEGER     REFERENCES firms(id) ON DELETE SET NULL,
                firm_role       TEXT,
                name            TEXT        NOT NULL,
                email           TEXT        UNIQUE NOT NULL,
                password_hash   TEXT        NOT NULL,
                role            TEXT        NOT NULL DEFAULT 'client',
                specialization  TEXT,
                experience      INTEGER,
                bar_number      TEXT,
                verified        BOOLEAN     DEFAULT 0,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id       INTEGER     REFERENCES users(id) ON DELETE SET NULL,
                lawyer_id       INTEGER     REFERENCES users(id) ON DELETE SET NULL,
                firm_id         INTEGER     REFERENCES firms(id) ON DELETE SET NULL,
                title           TEXT        NOT NULL,
                case_type       TEXT,
                description     TEXT        NOT NULL,
                risk_level      TEXT        DEFAULT 'medium',
                status          TEXT        DEFAULT 'active',
                ai_summary      TEXT,
                search_text     TEXT,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_court_registered BOOLEAN DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_tokens (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id         INTEGER     NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                token_data      TEXT        NOT NULL,
                version         INTEGER     DEFAULT 1,
                is_frozen       BOOLEAN     DEFAULT 0,
                owner_id        INTEGER     REFERENCES users(id),
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id         INTEGER     NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                filename        TEXT        NOT NULL,
                file_path       TEXT        NOT NULL,
                file_size       INTEGER,
                extracted_text  TEXT,
                ai_summary      TEXT,
                risk_analysis   TEXT,
                uploaded_by     INTEGER     REFERENCES users(id),
                uploaded_at     DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_notes (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id         INTEGER     NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                author_id       INTEGER     REFERENCES users(id),
                hearing_date    TEXT,
                content         TEXT        NOT NULL,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hearings (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id         INTEGER     NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                hearing_date    DATETIME    NOT NULL,
                court           TEXT,
                judge           TEXT,
                purpose         TEXT,
                outcome         TEXT,
                notes           TEXT,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_timeline (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id         INTEGER     NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                event_type      TEXT        NOT NULL,
                title           TEXT        NOT NULL,
                description     TEXT,
                actor_id        INTEGER     REFERENCES users(id),
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER     REFERENCES users(id),
                case_id         INTEGER     REFERENCES cases(id),
                title           TEXT        DEFAULT 'New Conversation',
                summary         TEXT,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      INTEGER     NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                role            TEXT        NOT NULL,
                content         TEXT        NOT NULL,
                structured_data TEXT,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id       INTEGER     REFERENCES users(id) ON DELETE CASCADE,
                lawyer_id       INTEGER     REFERENCES users(id) ON DELETE SET NULL,
                case_id         INTEGER     REFERENCES cases(id) ON DELETE SET NULL,
                scheduled_at    DATETIME    NOT NULL,
                status          TEXT        DEFAULT 'pending',
                notes           TEXT,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS case_services (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id         INTEGER     NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                service_type    TEXT        NOT NULL,
                title           TEXT        NOT NULL,
                status          TEXT        DEFAULT 'pending',
                merge_key       TEXT,
                extracted_data  TEXT,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_logs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER     REFERENCES users(id) ON DELETE CASCADE,
                service_type    TEXT        NOT NULL,
                external_id     TEXT,
                status          TEXT        DEFAULT 'pending',
                details         TEXT,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS cases_search_trigger 
            AFTER INSERT ON cases
            BEGIN
                UPDATE cases SET search_text = NEW.title || ' ' || COALESCE(NEW.ai_summary, '') || ' ' || NEW.description WHERE id = NEW.id;
            END;
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS cases_search_trigger_update 
            AFTER UPDATE OF title, description, ai_summary ON cases
            BEGIN
                UPDATE cases SET search_text = NEW.title || ' ' || COALESCE(NEW.ai_summary, '') || ' ' || NEW.description WHERE id = NEW.id;
            END;
        ''')

        conn.commit()
