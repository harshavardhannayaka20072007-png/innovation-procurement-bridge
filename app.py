from flask import Flask
from backend.pilot.routes import pilot_bp
from backend.applications.routes import applications_bp
from backend.milestones.routes import milestone_bp
from backend.evidence.routes import evidence_bp
from backend.performance.routes import performance_bp
from backend.decisions.routes import decision_bp

app = Flask(__name__)

app.register_blueprint(pilot_bp)
app.register_blueprint(applications_bp)
app.register_blueprint(milestone_bp)
app.register_blueprint(evidence_bp)
app.register_blueprint(performance_bp)
app.register_blueprint(decision_bp)


if __name__ == "__main__":
    app.run(debug=True)