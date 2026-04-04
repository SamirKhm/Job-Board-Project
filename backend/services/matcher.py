import os
from sentence_transformers import SentenceTransformer, util

# ------------------ LOAD MODEL ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ML", "resume_job_model")

try:
    model = SentenceTransformer(MODEL_PATH)
except Exception as e:
    print("❌ Model loading error:", e)
    model = None


# ------------------ SKILL GAP ANALYSIS ------------------
def skill_gap_analysis(resume_skills, job_skills):
    resume_set = set(s.strip().lower() for s in resume_skills if s.strip())
    job_set = set(s.strip().lower() for s in job_skills if s.strip())

    matched = list(resume_set.intersection(job_set))
    missing = list(job_set - resume_set)

    gap_percentage = (len(missing) / len(job_set)) * 100 if job_set else 0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_gap_percentage": round(gap_percentage, 2)
    }


# ------------------ MATCH CALCULATION ------------------
def calculate_match(resume_text, job_text):
    if not model:
        return 0.0

    try:
        emb1 = model.encode(resume_text, convert_to_tensor=True)
        emb2 = model.encode(job_text, convert_to_tensor=True)

        similarity = util.cos_sim(emb1, emb2).item()
        return round(similarity * 100, 2)

    except Exception as e:
        print("❌ Matching Error:", e)
        return 0.0