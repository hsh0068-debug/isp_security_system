import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import pickle

# 1. Load the data
print("Loading data...")
df = pd.read_csv("login_data.csv")

# 2. Convert country names to numbers
le = LabelEncoder()
df["country_code"] = le.fit_transform(df["country"])

# 3. Select features for AI to learn from
features = ["hour", "country_code", "failed_attempts", "is_new_device"]
X = df[features]

# 4. Train the Isolation Forest model
print("Training AI model...")
model = IsolationForest(
    contamination=0.1,
    random_state=42,
    n_estimators=100
)
model.fit(X)

# 5. Save the model and encoder
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("encoder.pkl", "wb") as f:
    pickle.dump(le, f)

print("Model trained and saved!")

# 6. Test the model
print("\nTesting model...")
normal_login = [[10, le.transform(["Sri Lanka"])[0], 0, 0]]
suspicious_login = [[3, le.transform(["Russia"])[0], 8, 1]]

normal_score = model.decision_function(normal_login)[0]
suspicious_score = model.decision_function(suspicious_login)[0]

print(f"Normal login score: {normal_score:.3f} (positive = safe)")
print(f"Suspicious login score: {suspicious_score:.3f} (negative = dangerous)")
print("\nAI Model is ready!")