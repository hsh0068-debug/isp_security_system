import pickle
import numpy as np
import pandas as pd
import os
import shap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "model.pkl"), "rb") as f:
    model = pickle.load(f)

with open(os.path.join(BASE_DIR, "encoder.pkl"), "rb") as f:
    encoder = pickle.load(f)

# Create SHAP explainer
explainer = shap.TreeExplainer(model)

def calculate_risk_score(hour: int, country: str,
                          failed_attempts: int, is_new_device: int):
    try:
        country_code = encoder.transform([country])[0]
    except:
        country_code = -1
        return 90, "Unknown country detected — very high risk"

    features = pd.DataFrame(
        [[hour, country_code, failed_attempts, is_new_device]],
        columns=["hour", "country_code", "failed_attempts", "is_new_device"]
    )

    raw_score = model.decision_function(features)[0]

    if raw_score > 0.1:
        risk = 10
    elif raw_score > 0:
        risk = 25
    elif raw_score > -0.1:
        risk = 55
    elif raw_score > -0.2:
        risk = 75
    else:
        risk = 92

    if failed_attempts > 5:
        risk = max(risk, 70)
    if hour < 5 and country != "Sri Lanka":
        risk = max(risk, 80)

    # Generate SHAP explanation
    explanation = generate_explanation(
        hour, country, failed_attempts, is_new_device, risk
    )

    return risk, explanation

def generate_explanation(hour, country, failed_attempts, 
                          is_new_device, risk_score):
    reasons = []

    if hour < 5 or hour > 23:
        reasons.append(f"unusual login time ({hour}:00)")
    else:
        reasons.append(f"normal login time ({hour}:00)")

    if country != "Sri Lanka":
        reasons.append(f"login from {country} — unusual location")
    else:
        reasons.append("normal location (Sri Lanka)")

    if failed_attempts > 3:
        reasons.append(f"{failed_attempts} failed attempts — suspicious")
    elif failed_attempts > 0:
        reasons.append(f"{failed_attempts} failed attempt(s)")
    else:
        reasons.append("no failed attempts")

    if is_new_device:
        reasons.append("new/unknown device detected")
    else:
        reasons.append("known device")

    if risk_score <= 30:
        verdict = "Login appears safe"
    elif risk_score <= 60:
        verdict = "Some suspicious signals — OTP required"
    elif risk_score <= 80:
        verdict = "High risk — account restricted"
    else:
        verdict = "Critical risk — access blocked"

    return f"{verdict}. Reasons: {', '.join(reasons)}."

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
    score1, exp1 = calculate_risk_score(10, "Sri Lanka", 0, 0)
    score2, exp2 = calculate_risk_score(3, "Russia", 8, 1)
    print(f"Normal login:    {score1}/100 → {decide_action(score1)}")
    print(f"Explanation: {exp1}")
    print()
    print(f"Suspicious login: {score2}/100 → {decide_action(score2)}")
    print(f"Explanation: {exp2}")