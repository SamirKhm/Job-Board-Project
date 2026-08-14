from flask import Blueprint, request, jsonify, session
from db import mysql
import re
import uuid

from services.matcher import calculate_amsm
from services.llm_processor import generate_explanation


job_bp = Blueprint('job', __name__)


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(text):

    if not text:
        return []

    text = str(text).lower()

    # Remove unnecessary phrases
    text = re.sub(
        r"strong knowledge of",
        "",
        text
    )

    # Replace brackets with commas
    text = re.sub(
        r"[()]",
        ",",
        text
    )

    # Replace common separators
    text = re.sub(
        r"/|\\|;",
        ",",
        text
    )

    # Handle common skills that may appear without separators
    text = re.sub(
        r"\b(sql|python|pandas|numpy|excel|power bi|data visualization|analytical thinking)\b",
        r",\1,",
        text
    )

    # Split by comma
    raw_skills = text.split(",")

    skills = []

    for skill in raw_skills:

        skill = re.sub(
            r"[^a-zA-Z0-9\s+#.]",
            "",
            skill
        ).strip()

        if skill:
            skills.append(skill)

    # Remove duplicates
    return list(set(skills))


# ============================================================
# GET EMPLOYER JOBS
# ============================================================

@job_bp.route('/employer-jobs', methods=['GET'])
def employer_jobs():

    try:

        employer_id = session.get('user_id')

        if not employer_id:
            return jsonify({
                "error": "User not logged in"
            }), 401

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT
                job_id,
                title,
                description,
                required_skills,
                experience_required,
                education_required,
                location
            FROM jobs
            WHERE employer_id = %s
            ORDER BY created_at DESC
        """, (employer_id,))

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

                "education_required": job[5],

                "location": job[6]
            })

        return jsonify(job_list)

    except Exception as e:

        print("❌ EMPLOYER JOBS ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# POST JOB
# ============================================================

@job_bp.route('/post-job', methods=['POST'])
def post_job():

    cur = None

    try:

        data = request.get_json() or {}

        employer_id = session.get('user_id')

        if not employer_id:
            return jsonify({
                "error": "User not logged in"
            }), 401

        job_id = str(uuid.uuid4())

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO jobs
            (
                job_id,
                employer_id,
                title,
                description,
                required_skills,
                experience_required,
                education_required,
                location
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            job_id,
            employer_id,
            data.get('title'),
            data.get('description'),
            data.get('required_skills'),
            data.get('experience_required'),
            data.get('education_required'),
            data.get('location')
        ))

        mysql.connection.commit()

        cur.close()
        cur = None

        return jsonify({

            "message":
                "Job posted successfully",

            "job_id":
                job_id
        })

    except Exception as e:

        print("❌ POST JOB ERROR:", e)

        try:
            mysql.connection.rollback()
        except Exception:
            pass

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cur:
            cur.close()


# ============================================================
# GET ALL JOBS
# ============================================================

@job_bp.route('/get-jobs', methods=['GET'])
def get_jobs():

    try:

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT
                job_id,
                title,
                description,
                required_skills,
                experience_required,
                education_required,
                location
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

                "education_required": job[5],

                "location": job[6]
            })

        return jsonify(job_list)

    except Exception as e:

        print("❌ GET JOBS ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# APPLY JOB - AMSM
# ============================================================

@job_bp.route('/apply-job', methods=['POST'])
def apply_job():

    cur = None

    try:

        # ----------------------------------------------------
        # REQUEST DATA
        # ----------------------------------------------------

        data = request.get_json() or {}

        job_id = data.get('job_id')

        user_id = session.get('user_id')


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not user_id:

            return jsonify({
                "error": "User not logged in"
            }), 401

        if not job_id:

            return jsonify({
                "error": "Job ID missing"
            }), 400


        cur = mysql.connection.cursor()


        # ====================================================
        # 1. GET RESUME
        # ====================================================

        cur.execute("""
            SELECT
                skills,
                experience,
                education,
                summary
            FROM resumes
            WHERE user_id = %s
        """, (user_id,))

        resume = cur.fetchone()


        if not resume:

            return jsonify({
                "error": "Upload resume first"
            }), 400


        # ----------------------------------------------------
        # RESUME DATA
        # ----------------------------------------------------

        resume_skills_raw = resume[0] or ""

        resume_experience = resume[1] or ""

        resume_education = resume[2] or ""

        resume_summary = resume[3] or ""


        # Convert skills to list
        resume_skills = extract_skills(
            resume_skills_raw
        )


        # ----------------------------------------------------
        # RESUME TEXT FOR SBERT
        # ----------------------------------------------------

        resume_text = f"""
        Skills:
        {resume_skills_raw}

        Experience:
        {resume_experience}

        Education:
        {resume_education}

        Summary:
        {resume_summary}
        """


        # ====================================================
        # 2. GET JOB
        # ====================================================

        cur.execute("""
            SELECT
                title,
                required_skills,
                experience_required,
                education_required,
                description
            FROM jobs
            WHERE job_id = %s
        """, (job_id,))

        job = cur.fetchone()


        if not job:

            return jsonify({
                "error": "Job not found"
            }), 404


        # ----------------------------------------------------
        # JOB DATA
        # ----------------------------------------------------

        job_title = job[0] or ""

        job_skills_raw = job[1] or ""

        job_experience = job[2] or ""

        job_education = job[3] or ""

        job_description = job[4] or ""


        # Convert job skills to list
        job_skills = extract_skills(
            job_skills_raw
        )


        # ----------------------------------------------------
        # JOB TEXT FOR SBERT
        # ----------------------------------------------------

        job_text = f"""
        Job Title:
        {job_title}

        Required Skills:
        {job_skills_raw}

        Required Experience:
        {job_experience}

        Required Education:
        {job_education}

        Job Description:
        {job_description}
        """


        # ====================================================
        # 3. AMSM CALCULATION
        # ====================================================

        amsm_result = calculate_amsm(

            resume_text=resume_text,

            job_text=job_text,

            resume_skills=resume_skills,

            job_skills=job_skills,

            resume_experience=resume_experience,

            job_experience=job_experience,

            resume_education=resume_education,

            job_education=job_education
        )


        # ====================================================
        # 4. GET AMSM COMPONENTS
        # ====================================================

        match_score = amsm_result[
            "match_score"
        ]

        semantic_score = amsm_result[
            "semantic_score"
        ]

        skill_score = amsm_result[
            "skill_score"
        ]

        experience_score = amsm_result[
            "experience_score"
        ]

        education_score = amsm_result[
            "education_score"
        ]

        complexity_score = amsm_result[
            "complexity_score"
        ]

        job_complexity = amsm_result[
            "job_complexity"
        ]

        weights = amsm_result[
            "weights"
        ]

        matched_skills = amsm_result[
            "matched_skills"
        ]

        missing_skills = amsm_result[
            "missing_skills"
        ]

        skill_gap_percentage = amsm_result[
            "skill_gap_percentage"
        ]


        # ====================================================
        # 5. GENERATE EXPLANATION
        # ====================================================

        explanation = generate_explanation(

            matched_skills,

            missing_skills,

            match_score,

            semantic_score,

            skill_score,

            experience_score,

            education_score
        )


        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if not explanation or not explanation.strip():

            explanation = (
                "Candidate matching was calculated "
                "using semantic, skill, experience, "
                "and education factors."
            )


        # ====================================================
        # 6. CHECK EXISTING APPLICATION
        # ====================================================

        cur.execute("""
            SELECT application_id
            FROM applications
            WHERE user_id = %s
            AND job_id = %s
        """, (
            user_id,
            job_id
        ))

        existing = cur.fetchone()


        # ====================================================
        # 7. UPDATE EXISTING APPLICATION
        # ====================================================

        if existing:

            cur.execute("""
                UPDATE applications
                SET
                    match_score = %s,
                    status = 'applied'
                WHERE user_id = %s
                AND job_id = %s
            """, (
                match_score,
                user_id,
                job_id
            ))

            message = "Application updated"


        # ====================================================
        # 8. INSERT NEW APPLICATION
        # ====================================================

        else:

            application_id = str(
                uuid.uuid4()
            )

            cur.execute("""
                INSERT INTO applications
                (
                    application_id,
                    user_id,
                    job_id,
                    match_score,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    'applied'
                )
            """, (
                application_id,
                user_id,
                job_id,
                match_score
            ))

            message = "Applied successfully"


        # ====================================================
        # 9. COMMIT
        # ====================================================

        mysql.connection.commit()


        # ====================================================
        # 10. RESPONSE
        # ====================================================

        return jsonify({

            "message":
                message,

            # Final AMSM score
            "match_score":
                match_score,

            # Individual scores
            "semantic_score":
                semantic_score,

            "skill_score":
                skill_score,

            "experience_score":
                experience_score,

            "education_score":
                education_score,

            # Complexity
            "complexity_score":
                complexity_score,

            "job_complexity":
                job_complexity,

            # Adaptive weights
            "weights":
                weights,

            # Skill gap
            "matched_skills":
                matched_skills,

            "missing_skills":
                missing_skills,

            "skill_gap_percentage":
                skill_gap_percentage,

            # Explanation
            "explanation":
                explanation
        })


    # ========================================================
    # ERROR
    # ========================================================

    except Exception as e:

        print(
            "❌ APPLY JOB ERROR:",
            e
        )

        try:
            mysql.connection.rollback()
        except Exception:
            pass

        return jsonify({
            "error": str(e)
        }), 500


    finally:

        if cur:
            cur.close()


# ============================================================
# GET JOB APPLICANTS
# ============================================================

@job_bp.route('/job-applicants/<job_id>', methods=['GET'])
def job_applicants(job_id):

    try:

        cursor = mysql.connection.cursor()

        query = """
            SELECT
                u.name,
                u.email,
                a.match_score
            FROM applications a
            JOIN users u
                ON a.user_id = u.user_id
            WHERE a.job_id = %s
            ORDER BY a.match_score DESC
        """

        cursor.execute(
            query,
            (job_id,)
        )

        results = cursor.fetchall()

        applicants = []

        for row in results:

            applicants.append({

                "name":
                    row[0],

                "email":
                    row[1],

                "score":
                    row[2]
            })

        cursor.close()

        return jsonify(applicants)

    except Exception as e:

        print(
            "❌ APPLICANTS ERROR:",
            e
        )

        return jsonify({
            "error": str(e)
        }), 500