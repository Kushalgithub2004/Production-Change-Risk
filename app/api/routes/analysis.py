from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.ml.inference import RiskInferenceEngine
import urllib.request
import urllib.parse
import json
import os

router = APIRouter()

# Initialize engine globally so it loads the model once on startup
try:
    engine = RiskInferenceEngine()
except Exception as e:
    engine = None
    print(f"Failed to load ML model: {e}")

class PRFeatures(BaseModel):
    lines_added: int
    lines_deleted: int
    files_changed: int
    api_changes: int
    db_changes: int
    config_changes: int
    dependency_changes: int
    services_touched: int
    criticality: int

class AnalysisResponse(BaseModel):
    risk_probability: float
    risk_level: str
    shap_explanations: List[Dict[str, Any]]
    similar_historical_changes: List[Dict[str, Any]]
    parsed_features: Optional[Dict[str, Any]] = None
    ai_justification: Optional[str] = None

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_pr(features: PRFeatures):
    if engine is None:
        raise HTTPException(status_code=500, detail="ML model not loaded")
    
    try:
        result = engine.predict_risk(features.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GitHubPRRequest(BaseModel):
    owner: str
    repo: str
    pr_number: int
    github_token: Optional[str] = None

@router.post("/analyze-github-pr", response_model=AnalysisResponse)
async def analyze_github_pr(req: GitHubPRRequest):
    if engine is None:
        raise HTTPException(status_code=500, detail="ML model not loaded")
        
    url = f"https://api.github.com/repos/{req.owner}/{req.repo}/pulls/{req.pr_number}/files"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    if req.github_token:
        headers['Authorization'] = f"token {req.github_token}"
    
    try:
        req_obj = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req_obj) as response:
            files = json.loads(response.read().decode())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch PR from GitHub: {str(e)}")
        
    lines_added = sum(f.get("additions", 0) for f in files)
    lines_deleted = sum(f.get("deletions", 0) for f in files)
    files_changed = len(files)
    
    api_changes = 0
    db_changes = 0
    config_changes = 0
    dependency_changes = 0
    
    for f in files:
        filename = f.get("filename", "").lower()
        if "api" in filename or "routes" in filename or "controller" in filename:
            api_changes = 1
        if "migration" in filename or "schema" in filename or "db" in filename or ".sql" in filename:
            db_changes = 1
        if "config" in filename or ".env" in filename or ".yml" in filename or ".yaml" in filename:
            config_changes = 1
        if "package.json" in filename or "requirements.txt" in filename or "pom.xml" in filename or "go.mod" in filename or "build.gradle" in filename:
            dependency_changes = 1
            
    # Estimate services touched (for microservices repos, count root directories)
    root_dirs = set(f.get("filename").split('/')[0] for f in files if '/' in f.get("filename", ""))
    services_touched = max(1, len(root_dirs) if len(root_dirs) < 5 else 5)
    
    features = {
        "lines_added": lines_added,
        "lines_deleted": lines_deleted,
        "files_changed": files_changed,
        "api_changes": api_changes,
        "db_changes": db_changes,
        "config_changes": config_changes,
        "dependency_changes": dependency_changes,
        "services_touched": services_touched,
        "criticality": 2
    }
    
    try:
        result = engine.predict_risk(features)
        result["parsed_features"] = features
        
        # Ask Gemini for justification
        prompt = f"You are a Senior SRE. A developer opened a PR with these stats: {features}. The ML model predicted a {result['risk_level']} risk (Probability: {result['risk_probability']:.2f}). The top risk drivers (SHAP values) are: {result['shap_explanations'][:3]}. Write a short, highly technical 2-sentence explanation of why this risk score makes sense and what the reviewer should double check before approving."
        try:
            import os
            gemini_key = os.getenv('GEMINI_API_KEY', '')
            gemini_req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
                headers={'Content-Type': 'application/json'},
                data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
            )
            with urllib.request.urlopen(gemini_req) as resp:
                resp_data = json.loads(resp.read().decode())
                result["ai_justification"] = resp_data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            result["ai_justification"] = f"AI Analysis unavailable: {str(e)}"

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
