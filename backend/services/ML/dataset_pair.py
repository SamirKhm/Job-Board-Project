import pandas as pd

resume_df = pd.read_csv("data/resume_clean.csv")
job_df = pd.read_csv("data/job_clean.csv")

pairs = []

for _, r in resume_df.iterrows():
    for _, j in job_df.iterrows():
        label = 1 if r["category"] in j["Job Title"] else 0
        pairs.append([r["resume_text"], j["Description"], label])

pair_df = pd.DataFrame(pairs, columns=["resume", "job", "label"])

positive = pair_df[pair_df["label"] == 1]
negative = pair_df[pair_df["label"] == 0].sample(len(positive))

pair_df = pd.concat([positive, negative])

pair_df.to_csv("data/training_pairs.csv", index=False)
