import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "multi_panel_rf_model.joblib")

FEATURES = ["age", "gender", "hb", "wbc", "plt", "glucose", "creatinine", "alt", "cholesterol", "tsh"]

def train_and_save_model():
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    np.random.seed(42)
    
    data = []
    labels = []
    conditions = [
        "Normal Clinical Profile",
        "Anemia-Related Pattern",
        "Infection / Immune Response",
        "Thrombocytopenia / Platelet Risk",
        "Diabetes / Glycemic Risk",
        "Renal / Kidney Function Stress",
        "Hepatic / Liver Enzyme Elevation",
        "Dyslipidemia / Cardiovascular Risk",
        "Thyroid Dysfunction Pattern"
    ]
    
    for _ in range(1800):
        gender = np.random.choice([0, 1])
        age = np.random.randint(18, 80)
        cond = np.random.choice(conditions)
        
        # বেসলাইন নরমাল ভ্যালু
        hb = np.random.uniform(13.6, 17.0) if gender == 1 else np.random.uniform(12.2, 15.0)
        wbc = np.random.uniform(4500, 10500)
        plt = np.random.uniform(160000, 420000)
        glucose = np.random.uniform(75, 96)
        creat = np.random.uniform(0.7, 1.1)
        alt = np.random.uniform(12, 40)
        chol = np.random.uniform(140, 195)
        tsh = np.random.uniform(0.8, 3.5)

        if cond == "Anemia-Related Pattern":
            hb = np.random.uniform(7.0, 11.8)
        elif cond == "Infection / Immune Response":
            wbc = np.random.uniform(11800, 24000)
        elif cond == "Thrombocytopenia / Platelet Risk":
            plt = np.random.uniform(35000, 140000)
        elif cond == "Diabetes / Glycemic Risk":
            glucose = np.random.uniform(126, 280)
        elif cond == "Renal / Kidney Function Stress":
            creat = np.random.uniform(1.4, 4.5)
        elif cond == "Hepatic / Liver Enzyme Elevation":
            alt = np.random.uniform(65, 250)
        elif cond == "Dyslipidemia / Cardiovascular Risk":
            chol = np.random.uniform(210, 320)
        elif cond == "Thyroid Dysfunction Pattern":
            tsh = np.random.choice([np.random.uniform(0.05, 0.35), np.random.uniform(4.8, 15.0)])
            
        data.append([age, gender, hb, wbc, plt, glucose, creat, alt, chol, tsh])
        labels.append(cond)

    df = pd.DataFrame(data, columns=FEATURES)
    clf = RandomForestClassifier(n_estimators=150, random_state=42)
    clf.fit(df, labels)
    joblib.dump(clf, MODEL_PATH)
    return clf

def get_ml_prediction(age: int, gender: str, values: dict) -> dict:
    if not os.path.exists(MODEL_PATH):
        clf = train_and_save_model()
    else:
        clf = joblib.load(MODEL_PATH)

    gender_num = 1 if gender == "Male" else 0
    row = [[
        age,
        gender_num,
        values.get("Hemoglobin", 14.5 if gender_num == 1 else 13.5),
        values.get("WBC", 7500.0),
        values.get("Platelet", 250000.0),
        values.get("Fasting Glucose", 88.0),
        values.get("Creatinine", 0.9),
        values.get("SGPT (ALT)", 25.0),
        values.get("Total Cholesterol", 170.0),
        values.get("TSH", 2.0)
    ]]

    features = pd.DataFrame(row, columns=FEATURES)
    prediction = clf.predict(features)[0]
    probabilities = clf.predict_proba(features)[0]
    confidence = round(float(np.max(probabilities)) * 100, 1)

    return {
        "category": str(prediction),
        "confidence": confidence
    }