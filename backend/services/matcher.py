import os
from sentence_transformers import SentenceTransformer, util
import re
import json
# ------------------ LOAD MODEL ------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ML",
    "fine_tuned_sbert"
)

print("📁 MODEL PATH:", MODEL_PATH)
print("📁 MODEL EXISTS:", os.path.exists(MODEL_PATH))

try:
    model = SentenceTransformer(MODEL_PATH)
    print("✅ Fine-tuned SBERT loaded successfully")

except Exception as e:
    print("❌ Model loading error:", e)
    model = None
# ============================================================
# NORMALIZE SKILLS
# ============================================================

def normalize_skills(skills):

    if not skills:
        return set()

    # --------------------------------------------------------
    # If skills come from MySQL as a string
    # Example:
    # "python, pandas, numpy, sql, excel"
    # --------------------------------------------------------
    if isinstance(skills, str):

        skills = skills.strip()

        # Try JSON format first
        try:
            parsed = json.loads(skills)

            if isinstance(parsed, list):
                skills = parsed

        except Exception:
            # MySQL comma-separated format
            skills = skills.split(",")

    # --------------------------------------------------------
    # Normalize skills
    # --------------------------------------------------------
    normalized = set()

    for skill in skills:

        skill = str(skill).lower().strip()

        # Replace special characters with spaces
        skill = re.sub(r"[^a-z0-9\s]", " ", skill)

        # Remove multiple spaces
        skill = re.sub(r"\s+", " ", skill).strip()

        if skill:
            normalized.add(skill)

    return normalized
# ============================================================
# EXTRACT YEARS OF EXPERIENCE
# ============================================================

def extract_years(text):

    if not text:
        return 0.0

    text = str(text).lower()

    matches = re.findall(
        r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
        text
    )

    if not matches:
        return 0.0

    return max(
        float(value)
        for value in matches
    )


# ============================================================
# SKILL GAP ANALYSIS
# ============================================================

def skill_gap_analysis(resume_skills, job_skills):

    print("\n========== SKILL DEBUG ==========")
    print("RAW RESUME SKILLS:", resume_skills)
    print("RAW JOB SKILLS:", job_skills)

    resume_set = normalize_skills(resume_skills)
    job_set = normalize_skills(job_skills)

    print("NORMALIZED RESUME:", resume_set)
    print("NORMALIZED JOB:", job_set)

    matched = sorted(
        resume_set.intersection(job_set)
    )

    missing = sorted(
        job_set - resume_set
    )

    print("MATCHED:", matched)
    print("MISSING:", missing)
    print("=================================\n")

    if job_set:

        skill_score = len(matched) / len(job_set)

        gap_percentage = (
            len(missing) / len(job_set)
        ) * 100

    else:

        skill_score = 0.0
        gap_percentage = 0.0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_score": round(skill_score, 4),
        "skill_gap_percentage": round(gap_percentage, 2)
    }
# ============================================================
# EXPERIENCE SCORE
# ============================================================

def calculate_experience_score(
    resume_experience,
    job_experience
):

    resume_years = extract_years(
        resume_experience
    )

    job_text = str(
        job_experience or ""
    ).lower()

    # --------------------------------------------------------
    # Detect experience range
    # Examples:
    # 0-2 years
    # 1-3 years
    # 2 to 4 years
    # --------------------------------------------------------

    range_match = re.search(
        r'(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
        job_text
    )

    if range_match:

        minimum_years = float(
            range_match.group(1)
        )

        maximum_years = float(
            range_match.group(2)
        )

        # Candidate is within acceptable range
        if (
            resume_years >= minimum_years
            and resume_years <= maximum_years
        ):
            return 1.0

        # Candidate has less than minimum
        if resume_years < minimum_years:

            if minimum_years == 0:
                return 1.0

            return round(
                resume_years / minimum_years,
                4
            )

        # Candidate exceeds maximum
        return 1.0

    # --------------------------------------------------------
    # Single minimum requirement
    # Example:
    # "2 years experience"
    # --------------------------------------------------------

    required_years = extract_years(
        job_experience
    )

    if required_years <= 0:
        return 1.0

    if resume_years >= required_years:
        return 1.0

    return round(
        resume_years / required_years,
        4
    )


# ============================================================
# EDUCATION SCORE
# ============================================================

def calculate_education_score(
    resume_education,
    job_education
):

    resume_text = str(
        resume_education or ""
    ).lower().strip()

    job_text = str(
        job_education or ""
    ).lower().strip()

    print("\n========== EDUCATION DEBUG ==========")
    print("RAW RESUME EDUCATION:", resume_education)
    print("RAW JOB EDUCATION:", job_education)
    print("NORMALIZED RESUME:", resume_text)
    print("NORMALIZED JOB:", job_text)

    # --------------------------------------------------------
    # No education requirement
    # --------------------------------------------------------

    if not job_text:
        print("Education requirement not specified -> 100%")
        return 1.0

    # --------------------------------------------------------
    # Education qualification groups
    # --------------------------------------------------------

    education_patterns = {

        "b.tech": [
            "b.tech",
            "btech",
            "bachelor of technology"
        ],

        "b.e": [
            "b.e",
            "be ",
            "bachelor of engineering"
        ],

        "b.sc": [
            "b.sc",
            "bsc",
            "bachelor of science"
        ],

        "bca": [
            "bca",
            "bachelor of computer applications"
        ],

        "m.tech": [
            "m.tech",
            "mtech",
            "master of technology"
        ],

        "m.e": [
            "m.e",
            "master of engineering"
        ],

        "m.sc": [
            "m.sc",
            "msc",
            "master of science"
        ],

        "mca": [
            "mca",
            "master of computer applications"
        ],

        "mba": [
            "mba",
            "master of business administration"
        ],

        "phd": [
            "phd",
            "doctorate"
        ]
    }

    # --------------------------------------------------------
    # Detect qualification in resume
    # --------------------------------------------------------

    resume_qualifications = set()

    for qualification, patterns in education_patterns.items():

        for pattern in patterns:

            if pattern in resume_text:
                resume_qualifications.add(
                    qualification
                )
                break

    # --------------------------------------------------------
    # Detect qualification required by job
    # --------------------------------------------------------

    job_qualifications = set()

    for qualification, patterns in education_patterns.items():

        for pattern in patterns:

            if pattern in job_text:
                job_qualifications.add(
                    qualification
                )
                break

    print(
        "RESUME QUALIFICATIONS:",
        resume_qualifications
    )

    print(
        "JOB QUALIFICATIONS:",
        job_qualifications
    )

    # --------------------------------------------------------
    # Direct qualification match
    # --------------------------------------------------------

    if (
        resume_qualifications
        and job_qualifications
        and resume_qualifications.intersection(
            job_qualifications
        )
    ):

        print(
            "✅ Education qualification matched -> 100%"
        )

        print(
            "====================================\n"
        )

        return 1.0

    # --------------------------------------------------------
    # If job requires B.Tech and resume has
    # Bachelor of Technology
    # --------------------------------------------------------

    if (
        "b.tech" in job_qualifications
        and "b.tech" in resume_qualifications
    ):

        print(
            "✅ B.Tech requirement satisfied -> 100%"
        )

        print(
            "====================================\n"
        )

        return 1.0

    # --------------------------------------------------------
    # No match
    # --------------------------------------------------------

    print(
        "❌ Education qualification mismatch -> 0%"
    )

    print(
        "====================================\n"
    )

    return 0.0

# ============================================================
# SEMANTIC SCORE
# ============================================================

def calculate_semantic_score(
    resume_text,
    job_text
):

    if not model:

        return 0.0


    if not resume_text or not job_text:

        return 0.0


    try:

        resume_embedding = model.encode(
            resume_text,
            convert_to_tensor=True
        )


        job_embedding = model.encode(
            job_text,
            convert_to_tensor=True
        )


        similarity = util.cos_sim(
            resume_embedding,
            job_embedding
        ).item()


        # Keep score in 0-1 range
        similarity = max(
            0.0,
            min(
                1.0,
                similarity
            )
        )


        return similarity


    except Exception as e:

        print(
            "❌ Semantic similarity error:",
            e
        )

        return 0.0


# ============================================================
# JOB COMPLEXITY
# ============================================================

def calculate_job_complexity(
    job_skills,
    job_experience
):

    required_skill_count = len(
        normalize_skills(
            job_skills
        )
    )


    required_experience = extract_years(
        job_experience
    )


    # --------------------------------------------------------
    # YOUR AMSM FORMULA
    #
    # Job Complexity =
    # 0.6 × Required Skills
    # +
    # 0.4 × Required Experience
    # --------------------------------------------------------

    complexity_score = (

        0.6 *
        required_skill_count

        +

        0.4 *
        required_experience

    )


    # --------------------------------------------------------
    # COMPLEXITY LEVEL
    # --------------------------------------------------------

    if complexity_score <= 5:

        complexity_level = "low"

    elif complexity_score <= 10:

        complexity_level = "medium"

    else:

        complexity_level = "high"


    return {

        "complexity_score":
            round(
                complexity_score,
                2
            ),

        "complexity_level":
            complexity_level
    }


# ============================================================
# ADAPTIVE WEIGHTS
# ============================================================

def get_adaptive_weights(
    complexity_level
):

    # --------------------------------------------------------
    # LOW COMPLEXITY
    # --------------------------------------------------------

    if complexity_level == "low":

        return {

            "semantic": 0.50,

            "skill": 0.25,

            "experience": 0.15,

            "education": 0.10
        }


    # --------------------------------------------------------
    # MEDIUM COMPLEXITY
    # --------------------------------------------------------

    elif complexity_level == "medium":

        return {

            "semantic": 0.40,

            "skill": 0.35,

            "experience": 0.15,

            "education": 0.10
        }


    # --------------------------------------------------------
    # HIGH COMPLEXITY
    # --------------------------------------------------------

    else:

        return {

            "semantic": 0.30,

            "skill": 0.40,

            "experience": 0.20,

            "education": 0.10
        }


# ============================================================
# AMSM CALCULATION
# ============================================================

def calculate_amsm(

    resume_text,

    job_text,

    resume_skills,

    job_skills,

    resume_experience,

    job_experience,

    resume_education,

    job_education

):

    # ========================================================
    # STEP 1 — SEMANTIC SCORE
    # ========================================================

    semantic_score = calculate_semantic_score(

        resume_text,

        job_text

    )


    # ========================================================
    # STEP 2 — SKILL SCORE
    # ========================================================

    skill_result = skill_gap_analysis(

        resume_skills,

        job_skills

    )


    skill_score = skill_result[
        "skill_score"
    ]


    # ========================================================
    # STEP 3 — EXPERIENCE SCORE
    # ========================================================

    experience_score = calculate_experience_score(

        resume_experience,

        job_experience

    )


    # ========================================================
    # STEP 4 — EDUCATION SCORE
    # ========================================================

    education_score = calculate_education_score(

        resume_education,

        job_education

    )


    # ========================================================
    # STEP 5 — JOB COMPLEXITY
    # ========================================================

    complexity_result = calculate_job_complexity(

        job_skills,

        job_experience

    )


    complexity_score = complexity_result[
        "complexity_score"
    ]

    complexity_level = complexity_result[
        "complexity_level"
    ]


    # ========================================================
    # STEP 6 — ADAPTIVE WEIGHTS
    # ========================================================

    weights = get_adaptive_weights(

        complexity_level

    )


    # ========================================================
    # STEP 7 — FINAL AMSM SCORE
    #
    # AMSM =
    # S × Ws
    # +
    # K × Wk
    # +
    # E × We
    # +
    # D × Wd
    # ========================================================

    amsm_score = (

        semantic_score *
        weights["semantic"]

        +

        skill_score *
        weights["skill"]

        +

        experience_score *
        weights["experience"]

        +

        education_score *
        weights["education"]

    )


    # Convert 0-1 → 0-100
    final_score = round(
        amsm_score * 100,
        2
    )


    # ========================================================
    # RETURN COMPLETE AMSM RESULT
    # ========================================================

    return {

        # Final score
        "match_score":
            final_score,


        # Component scores
        "semantic_score":
            round(
                semantic_score * 100,
                2
            ),

        "skill_score":
            round(
                skill_score * 100,
                2
            ),

        "experience_score":
            round(
                experience_score * 100,
                2
            ),

        "education_score":
            round(
                education_score * 100,
                2
            ),


        # Job complexity
        "complexity_score":
            complexity_score,

        "job_complexity":
            complexity_level,


        # Adaptive weights
        "weights":
            weights,


        # Skill analysis
        "matched_skills":
            skill_result[
                "matched_skills"
            ],

        "missing_skills":
            skill_result[
                "missing_skills"
            ],

        "skill_gap_percentage":
            skill_result[
                "skill_gap_percentage"
            ]
    }


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def calculate_match(
    resume_text,
    job_text
):

    """
    SBERT-only semantic matching.

    Kept for backward compatibility.
    The application system should use
    calculate_amsm() instead.
    """

    similarity = calculate_semantic_score(

        resume_text,

        job_text

    )

    return round(
        similarity * 100,
        2
    )