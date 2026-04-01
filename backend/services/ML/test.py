from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("../ML/resume_job_model")

resume_text = "Java , Spring Boot"
job_text = "Data Analysis"
# Convert text → embeddings
emb1 = model.encode(resume_text, convert_to_tensor=True)
emb2 = model.encode(job_text, convert_to_tensor=True)

# Calculate cosine similarity
score = util.cos_sim(emb1, emb2)

print("Match Score:", score.item())
