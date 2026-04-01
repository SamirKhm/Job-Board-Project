<<<<<<< HEAD
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
=======
from flask import Flask, request, jsonify
import os
import uuid
from resume_parser import extract_text
from llm_processor import extract_details
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def format_data(data):
    return {
        "name": data.get("name", ""),
        "skills": ", ".join(data.get("skills", [])),
        "education": data.get("education", ""),
        "experience": str(data.get("experience", "")),
        "summary": data.get("summary", "")
    }

@app.route("/")
def home():
    return "Server Running"


@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    print("🔥 Request received")

    try:
        file = request.files["resume"]
        print("📄 File received:", file.filename)

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        print("✅ File saved")

        extracted_text = extract_text(filepath)
        print("📝 Text extracted length:", len(extracted_text))

        # extracted_text = extracted_text[:3000]
        extracted_text = extracted_text[:1500]
        print("🚀 Sending to LLM...")
        structured_data = extract_details(extracted_text)
        print("✅ LLM Done")
        print("🤖 LLM Output:", structured_data)
        formatted_data = format_data(structured_data)
        print("📦 Formatted Data:", formatted_data)

        return jsonify({
            "message": "Resume processed successfully",
            "data": structured_data
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)
>>>>>>> ab5973e3bb7c12e213dabda389050c17ea384afc
