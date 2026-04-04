from flask import Flask, redirect, url_for
from flask_cors import CORS
import os

# DB
from db import init_db

# Blueprints
from routes.auth_routes import auth_bp
from routes.job_routes import job_bp
from routes.resume_routes import resume_bp
from routes.dashboard_routes import dashboard_bp

# ------------------ CREATE APP ------------------

app = Flask(__name__)
app.secret_key = "secret123"

# Init extensions
CORS(app)
init_db(app)

# Upload config
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------ HOME ------------------

@app.route('/')
def home():
    return redirect(url_for('auth.login'))

# ------------------ REGISTER BLUEPRINTS ------------------

app.register_blueprint(auth_bp)
app.register_blueprint(job_bp)
app.register_blueprint(resume_bp)
app.register_blueprint(dashboard_bp)

# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(debug=True)