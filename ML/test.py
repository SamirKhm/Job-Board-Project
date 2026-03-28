from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("resume_job_model")

resume_text = """
Frontend Developer with experience in HTML, CSS, JavaScript and React.
Basic knowledge of Python and SQL.
Built responsive web applications.

"""

job_text = """
Looking for a Python Developer with backend experience.
Knowledge of Django, APIs and databases required.

"""


# Convert text → embeddings
emb1 = model.encode(resume_text, convert_to_tensor=True)
emb2 = model.encode(job_text, convert_to_tensor=True)

# Calculate cosine similarity
score = util.cos_sim(emb1, emb2)

print("Match Score:", score.item())
