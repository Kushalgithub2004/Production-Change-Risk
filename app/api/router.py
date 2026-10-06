from fastapi import APIRouter
from app.api.routes import webhooks, analysis, auth

api_router = APIRouter()
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
