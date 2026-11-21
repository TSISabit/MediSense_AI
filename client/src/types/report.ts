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
  detailed_explanation?: string;
  possible_conditions?: string[];
  recommendations?: string[];
}

export interface AnalysisResponse {
  patient: {
    age: number;
    gender: "Male" | "Female";
  };
  report_type?: string;
  findings: TestFinding[];
  ml_insight: MLInsight;
}