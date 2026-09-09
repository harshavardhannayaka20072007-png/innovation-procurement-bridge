import os
from flask import Flask, redirect, url_for, session
from config import Config
from backend.db import close_db, init_db, ensure_schema_extensions

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Teardown context for DB closure
    app.teardown_appcontext(close_db)

    # Ensure uploads folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Auto-initialize SQLite database if not present or empty
    if not os.path.exists(Config.DATABASE):
        with app.app_context():
            init_db()
    ensure_schema_extensions()

    # Register Blueprints
    from backend.auth.routes import auth_bp
    from backend.challenges.routes import challenges_bp
    from backend.applications.routes import applications_bp
    from backend.evaluation.routes import evaluation_bp
    from backend.pilot.routes import pilot_bp
    from backend.milestones.routes import milestones_bp
    from backend.performance.routes import performance_bp
    from backend.government_routes import government_bp
    from backend.startup_routes import startup_bp
    from backend.evaluator_routes import evaluator_bp
    from backend.admin_routes import admin_bp
    from backend.assistant.routes import assistant_bp
    from backend.audit.routes import audit_bp
    from backend.evidence.routes import evidence_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(challenges_bp, url_prefix='/challenges')
    app.register_blueprint(applications_bp, url_prefix='/applications')
    app.register_blueprint(evaluation_bp, url_prefix='/evaluation')
    app.register_blueprint(pilot_bp, url_prefix='/pilot')
    app.register_blueprint(milestones_bp, url_prefix='/milestones')
    app.register_blueprint(performance_bp, url_prefix='/performance')
    app.register_blueprint(government_bp)
    app.register_blueprint(startup_bp)
    app.register_blueprint(evaluator_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(assistant_bp, url_prefix='/assistant')
    app.register_blueprint(audit_bp)
    app.register_blueprint(evidence_bp, url_prefix='/evidence')

    @app.route('/')
    def index():
        if 'role' in session:
            role = session['role']
            if role == 'government':
                return redirect(url_for('government.dashboard'))
            elif role == 'startup':
                return redirect(url_for('startup.dashboard'))
            elif role == 'evaluator':
                return redirect(url_for('evaluator.dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin.dashboard'))
        return redirect(url_for('auth.login'))

    return app

app = create_app()

if __name__ == '__main__':
    print("Starting Innovation Procurement Bridge server on http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
