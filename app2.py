import matplotlib.pyplot as plt

jobs = ["Software Dev", "Data Analyst", "Web Dev", "ML Engineer"]
scores = [85, 65, 88, 60]

plt.bar(jobs, scores)
plt.xlabel("Job Role")
plt.ylabel("Match Score (%)")
plt.title("Match Score Comparison for Single Resume")
plt.show()