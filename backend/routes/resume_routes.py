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

        s = str(s).lower().strip()

        # Replace special characters with spaces
        s = re.sub(r"[^a-z0-9\s]", " ", s)

        # Remove duplicate spaces
        s = re.sub(r"\s+", " ", s).strip()

        if s:
            cleaned.append(s)

    return list(set(cleaned))

def extract_resume_skills(text):
    """
    Extract explicitly mentioned skills from the original resume text.
    This avoids losing skills due to incomplete LLM extraction.
    """

    if not text:
        return []

    text = str(text).lower()

    # Canonical skill names
    skill_patterns = {
        "java": r"\bjava\b",
        "python": r"\bpython\b",
        "javascript": r"\bjavascript\b",
        "sql": r"\bsql\b",
        "pandas": r"\bpandas\b",
        "numpy": r"\bnumpy\b",
        "excel": r"\b(?:excel|microsoft excel)\b",
        "power bi": r"\bpower\s*bi\b",
        "data visualization": r"\bdata visualization\b",
        "analytical thinking": r"\banalytical thinking\b",
        "data structures algorithms": r"\bdata structures\s*(?:&|and)?\s*algorithms\b",
        "rest apis": r"\brest(?:ful)?\s*apis?\b",
        "git": r"\bgit\b",
        "github": r"\bgithub\b",
        "mysql": r"\bmysql\b",
        "node.js": r"\bnode\.?js\b",
        "html": r"\bhtml\b",
        "css": r"\bcss\b",
        "machine learning": r"\bmachine learning\b",
        "nlp": r"\bnlp\b",
        "semantic similarity": r"\bsemantic similarity\b",
        "oop": r"\boop\b"
    }

    found_skills = []

    for skill, pattern in skill_patterns.items():

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills

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
        extracted_text = extract_text(filepath)

        print("🚀 Sending to LLM...", flush=True)

        structured_data = extract_details(extracted_text) or {}

        print("🤖 LLM Output:", structured_data, flush=True)

        # ------------------ SAFE DATA HANDLING ------------------

        # ------------------------------------------------------------
# SKILLS FROM ORIGINAL RESUME TEXT
# ------------------------------------------------------------

        skills_list = extract_resume_skills(extracted_text)

        print(
            "✅ RESUME SKILLS FROM TEXT:",
            skills_list,
            flush=True
        )

        skills = ", ".join(skills_list)
        experience = str(structured_data.get("experience", ""))
        education = structured_data.get("education", "")
        summary = structured_data.get("summary", "")

        # ------------------ SAVE TO DB ------------------

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO resumes
(user_id, skills, experience, education, summary, resume_text)
VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
    skills = VALUES(skills),
    experience = VALUES(experience),
    education = VALUES(education),
    summary = VALUES(summary),
    resume_text = VALUES(resume_text)
        """, (
    user_id,
    skills,
    experience,
    education,
    summary,
    extracted_text
))

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