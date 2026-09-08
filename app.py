from flask import Flask

from backend.challenges.routes import challenges_bp
from backend.applications.routes import applications_bp
from backend.scoring.routes import scoring_bp

app = Flask(__name__)

app.register_blueprint(challenges_bp)
app.register_blueprint(applications_bp)
app.register_blueprint(scoring_bp)


@app.route("/")
def home():
    return "Innovation Procurement Bridge Backend is Running!"


if __name__ == "__main__":
    app.run(debug=True)