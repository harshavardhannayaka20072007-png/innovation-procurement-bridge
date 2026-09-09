import os
from flask import Flask, jsonify
from backend.auth import auth_bp

app = Flask(__name__)

# Required for Flask session management
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Register the Authentication Blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route("/")
def root():
    return jsonify({"message": "API is running..."}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)