from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import logging
from app.services.kafka_producer import publish_event

router = APIRouter()
logger = logging.getLogger(__name__)

class WebhookResponse(BaseModel):
    message: str
    status: str

@router.post("/github", response_model=WebhookResponse)
async def github_webhook(request: Request):
    """
    Receives GitHub PR events.
    """
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")
    
    if event_type == "pull_request":
        action = payload.get("action")
        pr_number = payload.get("pull_request", {}).get("number")
        logger.info(f"Received PR event: action={action}, PR={pr_number}")
        
        # Publish event to Kafka for asynchronous ML processing
        await publish_event("pr_events", payload)
        
        return {"message": f"Published PR {action} to Kafka", "status": "success"}
    
    return {"message": "Ignored non-PR event", "status": "success"}
