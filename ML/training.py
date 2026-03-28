from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import pandas as pd


pair_df = pd.read_csv("data/training_pairs.csv")


pair_df = pair_df.dropna(subset=["resume", "job", "label"])
pair_df["resume"] = pair_df["resume"].astype(str)
pair_df["job"] = pair_df["job"].astype(str)
pair_df = pair_df[pair_df["resume"].str.len() > 20]
pair_df = pair_df[pair_df["job"].str.len() > 20]

print("Total cleaned samples:", len(pair_df))


train_df, test_df = train_test_split(pair_df, test_size=0.2, random_state=42)

print("Training samples:", len(train_df))
print("Testing samples:", len(test_df))


model = SentenceTransformer("all-MiniLM-L6-v2")


train_examples = [
    InputExample(
        texts=[row["resume"], row["job"]],
        label=float(row["label"])
    )
    for _, row in train_df.iterrows()
]

train_loader = DataLoader(train_examples, shuffle=True, batch_size=64)


train_loss = losses.CosineSimilarityLoss(model)


evaluator = EmbeddingSimilarityEvaluator(
    sentences1=test_df["resume"].tolist(),
    sentences2=test_df["job"].tolist(),
    scores=test_df["label"].astype(float).tolist()
)



model.fit(
    train_objectives=[(train_loader, train_loss)],
    evaluator=evaluator,
    epochs=1,
    warmup_steps=100,
    output_path="resume_job_model"
)


print("Training completed and model saved.")
