import pandas as pd
import re
# Load datasets
resumes = pd.read_csv("data/resume_dataset.csv")
jobs = pd.read_csv("data/job_dataset.csv")

print(resumes.columns)
print(jobs.columns)
jobs.dropna(subset=["Description"], inplace=True)
resumes.dropna(subset=["resume_text", "category"], inplace=True)



def clean(text):
    text = text.lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

jobs["Job Title"] = jobs["Job Title"].apply(clean)
jobs["Description"] = jobs["Description"].apply(clean)

resumes["resume_text"] = resumes["resume_text"].apply(clean)
resumes["category"] = resumes["category"].apply(clean)

jobs.drop_duplicates(subset=["Description"], inplace=True)
resumes.drop_duplicates(subset=["resume_text"], inplace=True)

jobs = jobs[["Job Title", "Description"]]
resumes = resumes[["resume_id", "resume_text", "category"]]

jobs.to_csv("data/job_clean.csv", index=False)
resumes.to_csv("data/resume_clean.csv", index=False)
