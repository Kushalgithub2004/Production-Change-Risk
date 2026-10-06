import pandas as pd
import numpy as np
import random
import uuid

def generate_dataset(num_samples: int = 1000):
    """
    Generates a synthetic reproducible dataset of historical deployments.
    """
    np.random.seed(42)
    random.seed(42)

    data = []
    for _ in range(num_samples):
        # Base features
        lines_added = max(0, int(np.random.normal(100, 200)))
        lines_deleted = max(0, int(np.random.normal(50, 100)))
        files_changed = max(1, int(np.random.normal(5, 10)))
        
        api_changes = random.choice([True, False, False, False]) # 25% chance
        db_changes = random.choice([True, False, False]) # 33% chance
        config_changes = random.choice([True, False, False, False]) # 25% chance
        dependency_changes = random.choice([True, False, False]) # 33% chance
        
        services_touched = max(1, int(np.random.normal(2, 1.5)))
        criticality = random.choice(["low", "medium", "high"])
        
        # Determine incident probability based on features
        risk_score = 0.0
        
        if lines_added > 500:
            risk_score += 0.2
        if api_changes:
            risk_score += 0.3
        if db_changes:
            risk_score += 0.25
        if dependency_changes:
            risk_score += 0.15
        if services_touched > 3:
            risk_score += 0.1
        if criticality == "high":
            risk_score += 0.15
            
        # Add some noise
        risk_score += np.random.normal(0, 0.1)
        
        # Target label (1 if incident within 24h, 0 otherwise)
        probability = min(max(risk_score, 0.0), 1.0)
        incident_24h = 1 if random.random() < probability else 0
        
        data.append({
            "deployment_id": str(uuid.uuid4()),
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "files_changed": files_changed,
            "api_changes": int(api_changes),
            "db_changes": int(db_changes),
            "config_changes": int(config_changes),
            "dependency_changes": int(dependency_changes),
            "services_touched": services_touched,
            "criticality": 1 if criticality == "low" else (2 if criticality == "medium" else 3),
            "incident_24h": incident_24h
        })
        
    df = pd.DataFrame(data)
    df.to_csv("deployments_dataset.csv", index=False)
    print(f"Generated dataset with {num_samples} samples.")
    print(f"Total Incidents: {df['incident_24h'].sum()} ({df['incident_24h'].mean():.1%})")
    
    return df

if __name__ == "__main__":
    generate_dataset()
