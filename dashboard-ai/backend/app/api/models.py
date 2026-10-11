"""
Models API endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from app.schemas.chat import ComboInfo
from app.services.ninerouter_service import ninerouter_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/combos", tags=["combos"])


@router.get("", response_model=List[ComboInfo])
async def list_combos():
    """
    List available AI Combos from 9Router.
    
    Combos are pre-configured model routing configurations managed by 9Router.
    The application only selects which Combo to use; 9Router handles all
    model selection, provider routing, and fallback logic.
    """
    try:
        combos = await ninerouter_service.list_combos()
        return combos
    except Exception as e:
        logger.error(f"Failed to list combos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve AI Combos from service"
        )
