export interface TestFinding {
  test: string;
  value: number;
  unit: string;
  min: number;
  max: number;
  status: "LOW" | "HIGH" | "NORMAL";
  description: string;
  interpretation: string;
}

export interface MLInsight {
  category: string;
  confidence: number;
}

export interface AnalysisResponse {
  patient: {
    age: number;
    gender: "Male" | "Female";
  };
  extracted_text_preview?: string;
  findings: TestFinding[];
  ml_insight: MLInsight;
}