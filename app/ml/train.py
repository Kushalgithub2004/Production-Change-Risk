import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, precision_recall_curve, auc, confusion_matrix
import pickle
import json
import os

FEATURES = [
    "lines_added", "lines_deleted", "files_changed", 
    "api_changes", "db_changes", "config_changes", 
    "dependency_changes", "services_touched", "criticality"
]
TARGET = "incident_24h"

def train_model(dataset_path: str = "deployments_dataset.csv"):
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}. Run dataset_generator.py first.")
        return

    df = pd.read_csv(dataset_path)
    
    X = df[FEATURES]
    y = df[TARGET]
    
    # Time-aware split simulation (we just use standard split since it's synthetic without time)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Class imbalance handling can be done using class_weight="balanced"
    model = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # PR-AUC
    precision, recall, _ = precision_recall_curve(y_test, y_proba)
    pr_auc = auc(recall, precision)
    print(f"PR-AUC: {pr_auc:.3f}")
    
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save the model
    with open("risk_model.pkl", "wb") as f:
        pickle.dump(model, f)
        
    # Save metrics
    metrics = {
        "pr_auc": float(pr_auc),
        "f1_score": float(classification_report(y_test, y_pred, output_dict=True)['1']['f1-score'])
    }
    with open("metrics.json", "w") as f:
        json.dump(metrics, f)
        
    print("Model trained and saved to risk_model.pkl")

if __name__ == "__main__":
    train_model()
