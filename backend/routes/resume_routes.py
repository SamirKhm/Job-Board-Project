from flask import Blueprint, request, jsonify, current_app, session
import os
import uuid
import re
from werkzeug.utils import secure_filename

from services.resume_parser import extract_text
from services.llm_processor import extract_details
from db import mysql

resume_bp = Blueprint('resume', __name__)

# ✅ Allowed file types
ALLOWED_EXTENSIONS = {"pdf", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# 🔥 Clean skills (VERY IMPORTANT)
def clean_skills(skills):
    cleaned = []
    for s in skills:
        s = re.sub(r"[^a-zA-Z0-9\s]", "", str(s).lower().strip())
        if s:
            cleaned.append(s)
    return list(set(cleaned))


@resume_bp.route("/upload-resume", methods=["POST"])
def upload_resume():
    print("🔥 Request received", flush=True)

    try:
        # 🔒 Check login
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        # ✅ File validation
        file = request.files.get("resume")
        if not file or file.filename == "":
            return jsonify({"error": "No file uploaded"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        print("📄 File received:", file.filename, flush=True)

        # ✅ Unique filename
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        print("✅ File saved", flush=True)

        # ✅ Extract text
        extracted_text = extract_text(filepath)[:2000]

        print("🚀 Sending to LLM...", flush=True)

        structured_data = extract_details(extracted_text) or {}

        print("🤖 LLM Output:", structured_data, flush=True)

        # ------------------ SAFE DATA HANDLING ------------------

        raw_skills = structured_data.get("skills", [])
        if not isinstance(raw_skills, list):
            raw_skills = []

        # 🔥 Clean skills
        skills_list = clean_skills(raw_skills)

        skills = ", ".join(skills_list)
        experience = str(structured_data.get("experience", ""))
        education = structured_data.get("education", "")
        summary = structured_data.get("summary", "")

        # ------------------ SAVE TO DB ------------------

        cur = mysql.connection.cursor()

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

        # ✅ Delete file after processing
        try:
            os.remove(filepath)
        except Exception as e:
            print("⚠️ File delete error:", e)

        # ------------------ RESPONSE ------------------

        return jsonify({
            "message": "Resume uploaded & updated successfully",
            "data": {
                "skills": skills_list,
                "experience": experience,
                "education": education,
                "summary": summary
            }
        })

    except Exception as e:
        print("❌ ERROR:", e, flush=True)
        return jsonify({"error": str(e)}), 500