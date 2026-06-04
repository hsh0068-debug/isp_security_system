import pickle
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "model.pkl"), "rb") as f:
    model = pickle.load(f)

with open(os.path.join(BASE_DIR, "encoder.pkl"), "rb") as f:
    encoder = pickle.load(f)

def calculate_risk_score(hour: int, country: str,
                          failed_attempts: int, is_new_device: int):
    try:
        country_code = encoder.transform([country])[0]
    except:
        country_code = -1
        return 90  # Unknown country = very high risk

    import pandas as pd
    features = pd.DataFrame([[hour, country_code, failed_attempts, is_new_device]],
                             columns=["hour","country_code","failed_attempts","is_new_device"])

    raw_score = model.decision_function(features)[0]

    # Better conversion: raw_score range is roughly -0.5 to +0.5
    # positive = normal (low risk), negative = suspicious (high risk)
    if raw_score > 0.1:
        risk = 10   # Very safe
    elif raw_score > 0:
        risk = 25   # Safe
    elif raw_score > -0.1:
        risk = 55   # Medium risk
    elif raw_score > -0.2:
        risk = 75   # High risk
    else:
        risk = 92   # Critical

    # Extra rules
    if failed_attempts > 5:
        risk = max(risk, 70)
    if hour < 5 and country != "Sri Lanka":
        risk = max(risk, 80)

    return risk

def decide_action(risk_score: int):
    if risk_score <= 30:
        return "allow"
    elif risk_score <= 60:
        return "otp"
    elif risk_score <= 80:
        return "restrict"
    else:
        return "block"

if __name__ == "__main__":
    score1 = calculate_risk_score(10, "Sri Lanka", 0, 0)
    score2 = calculate_risk_score(3, "Russia", 8, 1)
    score3 = calculate_risk_score(14, "Sri Lanka", 1, 0)
    print(f"Normal login (10am, SL):      {score1}/100 → {decide_action(score1)}")
    print(f"Suspicious (3am, Russia):     {score2}/100 → {decide_action(score2)}")
    print(f"Normal login (2pm, SL):       {score3}/100 → {decide_action(score3)}")