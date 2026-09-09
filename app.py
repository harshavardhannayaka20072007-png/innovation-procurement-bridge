import os
import sys

# Must be at the top: Adds project root to Python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from backend.auth import auth_bp
from backend.pilot.routes import pilot_bp
from backend.applications.routes import applications_bp
from backend.milestones.routes import milestone_bp
from backend.evidence.routes import evidence_bp
from backend.performance.routes import performance_bp
from backend.decisions.routes import decision_bp

app = Flask(__name__)

# Required for Flask session management
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Register Authentication Blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')

# Register Procurement Lifecycle Blueprints
app.register_blueprint(pilot_bp)
app.register_blueprint(applications_bp)
app.register_blueprint(milestone_bp)
app.register_blueprint(evidence_bp)
app.register_blueprint(performance_bp)
app.register_blueprint(decision_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)