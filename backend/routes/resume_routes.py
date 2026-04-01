from flask import Blueprint, request, jsonify, current_app, session
import os
from werkzeug.utils import secure_filename

from services.resume_parser import extract_text
from services.llm_processor import extract_details
from db import mysql

resume_bp = Blueprint('resume', __name__)

@resume_bp.route("/upload-resume", methods=["POST"])
def upload_resume():
    print("🔥 Request received")

    try:
        # 🔒 Check login
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        # ✅ File validation
        file = request.files.get("resume")
        if not file or file.filename == "":
            return jsonify({"error": "No file uploaded"}), 400

        print("File received:", file.filename)

        # ✅ Secure filename
        filename = secure_filename(file.filename)

        # ✅ Ensure folder exists
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        print("File saved")

        # ✅ Extract text
        extracted_text = extract_text(filepath)[:3000]

        print("Sending to LLM...")
        structured_data = extract_details(extracted_text) or {}
        print("LLM Done")
        print("Structured Data:", structured_data)

        # ------------------ PREPARE DATA ------------------

        skills = ", ".join(structured_data.get("skills", []) or [])
        experience = str(structured_data.get("experience", ""))
        education = structured_data.get("education", "")
        summary = structured_data.get("summary", "")

        # ------------------ SAVE TO DB ------------------

        cur = mysql.connection.cursor()

        # ✅ INSERT OR UPDATE (BEST APPROACH)
        cur.execute("""
            INSERT INTO resumes (user_id, skills, experience, education, summary)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                skills = VALUES(skills),
                experience = VALUES(experience),
                education = VALUES(education),
                summary = VALUES(summary)
        """, (user_id, skills, experience, education, summary))

        mysql.connection.commit()
        cur.close()

        # ------------------ RESPONSE ------------------

        return jsonify({
            "message": "Resume uploaded & updated successfully",
            "data": structured_data
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500