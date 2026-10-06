import pandas as pd
import numpy as np
import pickle
import shap
from sklearn.metrics.pairwise import cosine_similarity
import os
import warnings

# Suppress annoying LightGBM/SHAP warnings in console for clean output
warnings.filterwarnings('ignore')

class RiskInferenceEngine:
    def __init__(self, model_path: str = "risk_model.pkl", dataset_path: str = "deployments_dataset.csv"):
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)
            
        self.explainer = shap.TreeExplainer(self.model)
        
        if os.path.exists(dataset_path):
            self.historical_data = pd.read_csv(dataset_path)
        else:
            self.historical_data = None
            
        self.features = [
            "lines_added", "lines_deleted", "files_changed", 
            "api_changes", "db_changes", "config_changes", 
            "dependency_changes", "services_touched", "criticality"
        ]

    def predict_risk(self, feature_dict: dict):
        df_input = pd.DataFrame([feature_dict])[self.features]
        
        # 1. Predict Probability
        probability = self.model.predict_proba(df_input)[0, 1]
        
        # 2. SHAP Explanations
        shap_values = self.explainer.shap_values(df_input)
        
        # For RandomForest, shap_values might be a list or a 3D array
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
            shap_values = shap_values[:, :, 1]
            
            
        # Format SHAP values
        explanations = []
        for feature_name, value in zip(self.features, shap_values[0]):
            explanations.append({
                "feature": feature_name,
                "impact": float(value)
            })
            
        # Sort by absolute impact to find most important drivers
        explanations.sort(key=lambda x: abs(x["impact"]), reverse=True)
        
        # 3. Retrieve Similar Historical Changes (Cosine Similarity)
        similar_deployments = []
        if self.historical_data is not None:
            hist_features = self.historical_data[self.features]
            similarities = cosine_similarity(df_input, hist_features)[0]
            
            # Get top 3 most similar indices
            top_indices = np.argsort(similarities)[::-1][:3]
            
            for idx in top_indices:
                record = self.historical_data.iloc[idx]
                similar_deployments.append({
                    "deployment_id": record["deployment_id"],
                    "similarity_score": float(similarities[idx]),
                    "incident_24h": bool(record["incident_24h"])
                })
                
        return {
            "risk_probability": float(probability),
            "risk_level": "HIGH" if probability > 0.6 else ("MEDIUM" if probability > 0.3 else "LOW"),
            "shap_explanations": explanations,
            "similar_historical_changes": similar_deployments
        }

if __name__ == "__main__":
    # Smoke test the inference engine
    engine = RiskInferenceEngine()
    test_features = {
        "lines_added": 450,
        "lines_deleted": 20,
        "files_changed": 15,
        "api_changes": 1,
        "db_changes": 1,
        "config_changes": 0,
        "dependency_changes": 1,
        "services_touched": 4,
        "criticality": 3
    }
    result = engine.predict_risk(test_features)
    print(f"\n[INFERENCE RESULT]")
    print(f"Risk Probability: {result['risk_probability']:.2%} ({result['risk_level']})")
    print("\nTop 3 Risk Factors (SHAP):")
    for exp in result["shap_explanations"][:3]:
        print(f"  [{exp['impact']:+.3f}] {exp['feature']}")
    print("\nSimilar Historical Changes:")
    for sc in result["similar_historical_changes"]:
        print(f"  {sc['deployment_id'][:8]}... | Sim: {sc['similarity_score']:.2%} | Caused Incident: {sc['incident_24h']}")
