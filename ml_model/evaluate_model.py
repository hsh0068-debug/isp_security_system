import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
import json

print("=" * 60)
print("ISP SECURITY SYSTEM - MODEL EVALUATION REPORT")
print("=" * 60)

# Load data
print("\n1. Loading 10,000 login records...")
df = pd.read_csv("login_data.csv")
print(f"   Total records: {len(df)}")
print(f"   Normal logins: {len(df[df['is_suspicious']==0])}")
print(f"   Suspicious logins: {len(df[df['is_suspicious']==1])}")

# Prepare data
le = LabelEncoder()
df["country_code"] = le.fit_transform(df["country"])
features = ["hour", "country_code", "failed_attempts", "is_new_device"]
X = df[features]
y = df["is_suspicious"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\n2. Training set: {len(X_train)} | Testing set: {len(X_test)}")

results = {}

# Model 1 - Isolation Forest
print("\n3. Evaluating Isolation Forest...")
iso = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
iso.fit(X_train)
iso_preds = [1 if p == -1 else 0 for p in iso.predict(X_test)]
results["Isolation Forest"] = {
    "accuracy":  round(accuracy_score(y_test, iso_preds) * 100, 2),
    "precision": round(precision_score(y_test, iso_preds, zero_division=0) * 100, 2),
    "recall":    round(recall_score(y_test, iso_preds, zero_division=0) * 100, 2),
    "f1_score":  round(f1_score(y_test, iso_preds, zero_division=0) * 100, 2)
}
for k, v in results["Isolation Forest"].items():
    print(f"   {k}: {v}%")

# Model 2 - Random Forest
print("\n4. Evaluating Random Forest...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
rf_preds = rf.predict(X_test)
results["Random Forest"] = {
    "accuracy":  round(accuracy_score(y_test, rf_preds) * 100, 2),
    "precision": round(precision_score(y_test, rf_preds, zero_division=0) * 100, 2),
    "recall":    round(recall_score(y_test, rf_preds, zero_division=0) * 100, 2),
    "f1_score":  round(f1_score(y_test, rf_preds, zero_division=0) * 100, 2)
}
for k, v in results["Random Forest"].items():
    print(f"   {k}: {v}%")

# Model 3 - One Class SVM
print("\n5. Evaluating One-Class SVM...")
svm = OneClassSVM(nu=0.1, kernel="rbf", gamma="auto")
svm.fit(X_train[y_train == 0])
svm_preds = [1 if p == -1 else 0 for p in svm.predict(X_test)]
results["One-Class SVM"] = {
    "accuracy":  round(accuracy_score(y_test, svm_preds) * 100, 2),
    "precision": round(precision_score(y_test, svm_preds, zero_division=0) * 100, 2),
    "recall":    round(recall_score(y_test, svm_preds, zero_division=0) * 100, 2),
    "f1_score":  round(f1_score(y_test, svm_preds, zero_division=0) * 100, 2)
}
for k, v in results["One-Class SVM"].items():
    print(f"   {k}: {v}%")

# Comparison Table
print("\n" + "=" * 60)
print("ALGORITHM COMPARISON TABLE")
print("=" * 60)
print(f"{'Algorithm':<20} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10}")
print("-" * 60)
for algo, m in results.items():
    print(f"{algo:<20} {m['accuracy']:>9}% {m['precision']:>9}% {m['recall']:>9}% {m['f1_score']:>9}%")

# Best model
best = max(results, key=lambda x: results[x]["f1_score"])
print(f"\nBest Model: {best} with F1 Score: {results[best]['f1_score']}%")

# Confusion Matrix
print("\n" + "=" * 60)
print("CONFUSION MATRIX - Isolation Forest")
print("=" * 60)
cm = confusion_matrix(y_test, iso_preds)
print(f"True Negatives  (Normal correctly identified):   {cm[0][0]}")
print(f"False Positives (Normal wrongly flagged):        {cm[0][1]}")
print(f"False Negatives (Suspicious missed):             {cm[1][0]}")
print(f"True Positives  (Suspicious correctly detected): {cm[1][1]}")

# Save results
with open("evaluation_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nResults saved to evaluation_results.json")
print("Evaluation complete!")