import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "cbc_rf_model.joblib")

def train_and_save_model():
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    np.random.seed(42)
    
    data = []
    labels = []
    
    for _ in range(600):
        gender = np.random.choice([0, 1])
        age = np.random.randint(18, 80)
        condition = np.random.choice(["Normal", "Anemia-Related", "Infection-Related", "Thrombocytopenia-Risk"])
        
        if condition == "Normal":
            hb = np.random.uniform(13.6, 17.0) if gender == 1 else np.random.uniform(12.2, 15.0)
            wbc = np.random.uniform(4500, 10500)
            plt = np.random.uniform(160000, 420000)
            rbc = np.random.uniform(4.6, 5.7) if gender == 1 else np.random.uniform(4.2, 5.0)
        elif condition == "Anemia-Related":
            hb = np.random.uniform(7.5, 11.8)
            wbc = np.random.uniform(4500, 10500)
            plt = np.random.uniform(160000, 420000)
            rbc = np.random.uniform(2.8, 4.0)
        elif condition == "Infection-Related":
            hb = np.random.uniform(12.5, 16.5)
            wbc = np.random.uniform(11500, 22000)
            plt = np.random.uniform(160000, 440000)
            rbc = np.random.uniform(4.2, 5.5)
        else:
            hb = np.random.uniform(12.0, 16.0)
            wbc = np.random.uniform(4500, 10500)
            plt = np.random.uniform(40000, 140000)
            rbc = np.random.uniform(4.1, 5.4)
            
        data.append([age, gender, hb, wbc, plt, rbc])
        labels.append(condition)

    df = pd.DataFrame(data, columns=["age", "gender", "hb", "wbc", "plt", "rbc"])
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(df, labels)
    joblib.dump(clf, MODEL_PATH)
    return clf

def get_ml_prediction(age: int, gender: str, values: dict) -> dict:
    if not os.path.exists(MODEL_PATH):
        clf = train_and_save_model()
    else:
        clf = joblib.load(MODEL_PATH)

    gender_num = 1 if gender == "Male" else 0
    hb = values.get("Hemoglobin", 14.5 if gender_num == 1 else 13.5)
    wbc = values.get("WBC", 7500.0)
    plt = values.get("Platelet", 250000.0)
    rbc = values.get("RBC", 5.0 if gender_num == 1 else 4.5)

    features = pd.DataFrame([[age, gender_num, hb, wbc, plt, rbc]], columns=["age", "gender", "hb", "wbc", "plt", "rbc"])
    prediction = clf.predict(features)[0]
    probabilities = clf.predict_proba(features)[0]
    confidence = round(float(np.max(probabilities)) * 100, 1)

    return {
        "category": str(prediction),
        "confidence": confidence
    }