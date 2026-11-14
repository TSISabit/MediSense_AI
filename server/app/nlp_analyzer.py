import json
import os
import re

REF_PATH = os.path.join(os.path.dirname(__file__), "reference_data.json")

with open(REF_PATH, "r", encoding="utf-8") as f:
    REFERENCE_DATA = json.load(f)

PATTERNS = {
    "Hemoglobin": r"(?:Hemoglobin|Haemoglobin|Hb|HGB)[\s:\-]*(\d+\.?\d*)",
    "WBC": r"(?:WBC|White Blood Cell|Total Leukocyte Count|TLC)[\s:\-]*([\d,]+)",
    "Platelet": r"(?:Platelet|Platelets|PLT)[\s:\-]*([\d,]+)",
    "RBC": r"(?:RBC|Red Blood Cell|Total RBC)[\s:\-]*(\d+\.?\d*)",
    "Fasting Glucose": r"(?:Fasting Glucose|Fasting Blood Sugar|FBS|Glucose Fasting|Blood Glucose)[\s:\-]*(\d+\.?\d*)",
    "HbA1c": r"(?:HbA1c|Glycated Hemoglobin|A1C)[\s:\-]*(\d+\.?\d*)",
    "Creatinine": r"(?:Serum Creatinine|Creatinine)[\s:\-]*(\d+\.?\d*)",
    "SGPT (ALT)": r"(?:SGPT|ALT|Alanine Aminotransferase)[\s:\-]*(\d+\.?\d*)",
    "SGOT (AST)": r"(?:SGOT|AST|Aspartate Aminotransferase)[\s:\-]*(\d+\.?\d*)",
    "Total Cholesterol": r"(?:Total Cholesterol|Cholesterol)[\s:\-]*(\d+\.?\d*)",
    "Triglycerides": r"(?:Triglycerides|Triglyceride|TG)[\s:\-]*(\d+\.?\d*)",
    "TSH": r"(?:TSH|Thyroid Stimulating Hormone)[\s:\-]*(\d+\.?\d*)"
}

def parse_and_analyze(raw_text: str, gender: str) -> tuple[dict, list]:
    extracted = {}
    findings = []

    for test_name, pattern in PATTERNS.items():
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            val_str = match.group(1).replace(",", "")
            try:
                value = float(val_str)
                extracted[test_name] = value
                
                ref_info = REFERENCE_DATA[test_name]
                gender_range = ref_info[gender]
                min_val = gender_range["min"]
                max_val = gender_range["max"]

                if value < min_val:
                    status = "LOW"
                    advice = f"{test_name} is below the normal reference range ({min_val} - {max_val} {gender_range['unit']})."
                elif value > max_val:
                    status = "HIGH"
                    advice = f"{test_name} is above the normal reference range ({min_val} - {max_val} {gender_range['unit']})."
                else:
                    status = "NORMAL"
                    advice = f"{test_name} is within the healthy reference range."

                findings.append({
                    "test": test_name,
                    "value": value,
                    "unit": gender_range["unit"],
                    "min": min_val,
                    "max": max_val,
                    "status": status,
                    "description": ref_info["description"],
                    "interpretation": advice
                })
            except ValueError:
                continue

    return extracted, findings