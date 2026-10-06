from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import urllib.request
import urllib.parse
import json
import os

router = APIRouter()

CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")

@router.get("/github/login")
async def github_login():
    redirect_uri = "http://localhost:8000/api/v1/auth/github/callback"
    url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={redirect_uri}&scope=repo"
    return RedirectResponse(url)

@router.get("/github/callback")
async def github_callback(code: str):
    # Exchange code for access token
    url = "https://github.com/login/oauth/access_token"
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode())
            access_token = resp_data.get("access_token")
            # Redirect back to Next.js frontend with the access token
            return RedirectResponse(f"http://localhost:3000/?token={access_token}")
    except Exception as e:
        return RedirectResponse(f"http://localhost:3000/?error={str(e)}")
