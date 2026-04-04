from flask import Blueprint, request, jsonify, session
from db import mysql
from services.matcher import calculate_match
import uuid   # ✅ IMPORTANT

job_bp = Blueprint('job', __name__)

# ------------------ GET EMPLOYER JOBS ------------------

@job_bp.route('/employer-jobs', methods=['GET'])
def employer_jobs():
    try:
        employer_id = session.get('user_id')
        if not employer_id:
            return jsonify({"error": "User not logged in"}), 401

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT job_id, title, description, required_skills, experience_required, location
            FROM jobs
            WHERE employer_id = %s
            ORDER BY created_at DESC
        """, (employer_id,))

        jobs = cur.fetchall()
        cur.close()

        job_list = []
        for job in jobs:
            job_list.append({
                "job_id": job[0],   # ✅ renamed (better than "id")
                "title": job[1],
                "description": job[2],
                "required_skills": job[3],
                "experience_required": job[4],
                "location": job[5]
            })

        return jsonify(job_list)

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ------------------ POST JOB ------------------

@job_bp.route('/post-job', methods=['POST'])
def post_job():
    try:
        data = request.get_json() or {}

        employer_id = session.get('user_id')
        if not employer_id:
            return jsonify({"error": "User not logged in"}), 401

        job_id = str(uuid.uuid4())  # ✅ GENERATE UUID

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO jobs (job_id, employer_id, title, description, required_skills, experience_required, location)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            job_id,
            employer_id,
            data.get('title'),
            data.get('description'),
            data.get('required_skills'),
            data.get('experience_required'),
            data.get('location')
        ))

        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Job posted successfully", "job_id": job_id})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ------------------ GET ALL JOBS ------------------

@job_bp.route('/get-jobs', methods=['GET'])
def get_jobs():
    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT job_id, title, description, required_skills, experience_required, location
            FROM jobs
            ORDER BY created_at DESC
        """)

        jobs = cur.fetchall()
        cur.close()

        job_list = []
        for job in jobs:
            job_list.append({
                "job_id": job[0],
                "title": job[1],
                "description": job[2],
                "required_skills": job[3],
                "experience_required": job[4],
                "location": job[5]
            })

        return jsonify(job_list)

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ------------------ APPLY JOB ------------------


@job_bp.route('/apply-job', methods=['POST'])
def apply_job():
    try:
        data = request.get_json() or {}
        job_id = data.get('job_id')

        # 🔒 Check login
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        if not job_id:
            return jsonify({"error": "Job ID missing"}), 400

        cur = mysql.connection.cursor()

        # -------- GET RESUME --------
        cur.execute("""
            SELECT skills, experience, summary
            FROM resumes
            WHERE user_id = %s
        """, (user_id,))
        resume = cur.fetchone()

        if not resume:
            cur.close()
            return jsonify({"error": "Upload resume first"}), 400

        # ✅ Build resume text (structured)
        resume_text = f"""
        Skills: {resume[0] or ""}
        Experience: {resume[1] or ""}
        Summary: {resume[2] or ""}
        """

        # -------- GET JOB --------
        cur.execute("""
            SELECT required_skills, experience_required, description
            FROM jobs
            WHERE job_id = %s
        """, (job_id,))
        job = cur.fetchone()

        if not job:
            cur.close()
            return jsonify({"error": "Job not found"}), 404

        # ✅ Build job text (structured)
        job_text = f"""
        Skills Required: {job[0] or ""}
        Experience Required: {job[1] or ""}
        Job Description: {job[2] or ""}
        """

        # -------- MATCHING --------
        match_score = calculate_match(resume_text, job_text)

        # # Optional: convert to percentage
        # match_score = round(match_score * 100, 2)

        # -------- CHECK EXISTING APPLICATION --------
        cur.execute("""
            SELECT application_id FROM applications
            WHERE user_id = %s AND job_id = %s
        """, (user_id, job_id))

        existing = cur.fetchone()

        if existing:
            # ✅ UPDATE EXISTING APPLICATION
            cur.execute("""
                UPDATE applications
                SET match_score = %s, status = 'applied'
                WHERE user_id = %s AND job_id = %s
            """, (match_score, user_id, job_id))

            message = "Application updated"

        else:
            # ✅ NEW APPLICATION
            application_id = str(uuid.uuid4())

            cur.execute("""
                INSERT INTO applications (application_id, user_id, job_id, match_score, status)
                VALUES (%s, %s, %s, %s, 'applied')
            """, (application_id, user_id, job_id, match_score))

            message = "Applied successfully"

        mysql.connection.commit()
        cur.close()

        # -------- RESPONSE --------
        return jsonify({
            "message": message,
            "match_score": match_score
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500


@job_bp.route('/job-applicants/<job_id>', methods=['GET'])
def job_applicants(job_id):
    try:
        cursor = mysql.connection.cursor()

        query = """
        SELECT u.name, u.email, a.match_score
        FROM applications a
        JOIN users u ON a.user_id = u.user_id
        WHERE a.job_id = %s
        ORDER BY a.match_score DESC
        """

        cursor.execute(query, (job_id,))
        results = cursor.fetchall()

        applicants = []
        for row in results:
            applicants.append({
                "name": row[0],
                "email": row[1],
                "score": row[2]
            })

        cursor.close()
        return jsonify(applicants)

    except Exception as e:
        return jsonify({"error": str(e)}), 500