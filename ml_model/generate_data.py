import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker()

def generate_login_data(n=5000):
    data = []
    
    for i in range(n):
        # 90% normal logins, 10% suspicious
        is_suspicious = random.random() < 0.10
        
        if is_suspicious:
            hour = random.choice([0,1,2,3,4,23])
            country = random.choice(["Russia","China","Unknown","North Korea"])
            failed_attempts = random.randint(5, 20)
            is_new_device = 1
        else:
            hour = random.randint(7, 22)
            country = random.choice(["Sri Lanka","Sri Lanka","Sri Lanka"])
            failed_attempts = random.randint(0, 1)
            is_new_device = random.choice([0,0,0,1])
        
        data.append({
            "hour": hour,
            "country": country,
            "failed_attempts": failed_attempts,
            "is_new_device": is_new_device,
            "is_suspicious": 1 if is_suspicious else 0
        })
    
    df = pd.DataFrame(data)
    df.to_csv("login_data.csv", index=False)
    print(f"Generated {n} login records!")
    print(df.head(10))
    return df

generate_login_data(5000)