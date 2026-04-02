"""
Pocket Lawyer 2.0 — Flask Application Entry Point
Registers all blueprints, configures CORS, and initializes the database.
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH, DEBUG, PORT, HOST
from database import init_pool, init_db
from routes.auth_routes import auth_bp
from routes.case_routes import case_bp
from routes.chat_routes import chat_bp
from routes.upload_routes import upload_bp
from routes.service_routes import service_bp
from routes.firm_routes import firm_bp
import os


def create_app():
    app = Flask(__name__, static_folder=None)

    # Config
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

    # CORS — allow frontend to call API
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize database pool and schema
    init_pool()
    with app.app_context():
        init_db()

    # Register blueprints under /api prefix
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(case_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(service_bp, url_prefix='/api')
    app.register_blueprint(firm_bp, url_prefix='/api/firm')

    # Serve frontend static files
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')

    @app.route('/')
    def serve_index():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        file_path = os.path.join(frontend_dir, path)
        if os.path.isfile(file_path):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, 'index.html')

    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'Pocket Lawyer 2.0'}), 200

    return app


if __name__ == '__main__':
    app = create_app()
    print(f'\n[Pocket Lawyer 2.0 Backend]')
    print(f'   Running on http://{HOST}:{PORT}')
    print(f'   Debug: {DEBUG}\n')
    app.run(host=HOST, port=PORT, debug=DEBUG)
