import os
from sentence_transformers import SentenceTransformer, util

# Correct path to your model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ML", "resume_job_model")

model = SentenceTransformer(MODEL_PATH)

# ✅ THIS FUNCTION MUST EXIST
def calculate_match(resume_text, job_text):
    emb1 = model.encode(resume_text, convert_to_tensor=True)
    emb2 = model.encode(job_text, convert_to_tensor=True)

    similarity = util.cos_sim(emb1, emb2).item()
    return round(similarity * 100, 2)