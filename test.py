from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("resume_job_model")

resume_text = """
Software Engineer with 4 years of experience in Python development.
Strong background in Machine Learning, Deep Learning, and Natural Language Processing.
Experienced in building classification models using TensorFlow and PyTorch.
Worked on recommendation systems, data preprocessing, and deploying ML models using Flask and Docker.
"""

job_text = """
We are hiring a Machine Learning Engineer with strong Python programming skills.
The candidate should have experience in Deep Learning, NLP, TensorFlow, PyTorch,
and building classification or recommendation systems.
Experience in deploying ML models is a plus.
"""


# Convert text → embeddings
emb1 = model.encode(resume_text, convert_to_tensor=True)
emb2 = model.encode(job_text, convert_to_tensor=True)

# Calculate cosine similarity
score = util.cos_sim(emb1, emb2)

print("Match Score:", score.item())
