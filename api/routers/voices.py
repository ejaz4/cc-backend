"""
Voices router for FastAPI
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException

from api.models import (
    VoiceListResponse,
    VoiceResponse,
    SuccessResponse
)
from api.dependencies import ElevenLabsService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=VoiceListResponse)
async def get_voices(
    elevenlabs_service = ElevenLabsService
):
    """Get available ElevenLabs voices"""
    try:
        voices = elevenlabs_service.get_available_voices()
        
        return VoiceListResponse(
            voices=[VoiceResponse(**voice) for voice in voices],
            total=len(voices)
        )
        
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{voice_id}", response_model=VoiceResponse)
async def get_voice(
    voice_id: str,
    elevenlabs_service = ElevenLabsService
):
    """Get specific voice by ID"""
    try:
        voice_info = elevenlabs_service.get_voice_info(voice_id)
        if not voice_info:
            raise HTTPException(status_code=404, detail="Voice not found")
        
        return VoiceResponse(**voice_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{voice_id}", response_model=SuccessResponse)
async def delete_voice(
    voice_id: str,
    elevenlabs_service = ElevenLabsService
):
    """Delete voice"""
    try:
        success = elevenlabs_service.delete_voice(voice_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete voice")
        
        return SuccessResponse(
            success=True,
            message="Voice deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting voice: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 