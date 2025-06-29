"""
Audio router for FastAPI
"""

import os
import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from api.models import (
    AudioFileListResponse,
    SuccessResponse
)
from api.dependencies import AudioRepo
from config import Config

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{session_id}/{filename}")
async def serve_audio(
    session_id: str,
    filename: str,
    audio_repo = AudioRepo
):
    """Serve audio file"""
    try:
        # Get audio file record
        audio_files = audio_repo.find_by_session_id(session_id)
        target_file = None
        
        for audio_file in audio_files:
            if audio_file.get('file_name') == filename:
                target_file = audio_file
                break
        
        if not target_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Check if file exists
        file_path = target_file.get('file_path')
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found on disk")
        
        # Return file
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='audio/mpeg'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving audio file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=AudioFileListResponse)
async def get_session_audio_files(
    session_id: str,
    audio_repo = AudioRepo
):
    """Get all audio files for a session"""
    try:
        audio_files = audio_repo.find_by_session_id(session_id)
        
        return AudioFileListResponse(
            audio_files=audio_files,
            total=len(audio_files)
        )
        
    except Exception as e:
        logger.error(f"Error getting session audio files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/completed", response_model=AudioFileListResponse)
async def get_completed_audio_files(
    session_id: str,
    audio_repo = AudioRepo
):
    """Get completed audio files for a session"""
    try:
        audio_files = audio_repo.find_completed_audio(session_id)
        
        return AudioFileListResponse(
            audio_files=audio_files,
            total=len(audio_files)
        )
        
    except Exception as e:
        logger.error(f"Error getting completed audio files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{audio_file_id}", response_model=SuccessResponse)
async def delete_audio_file(
    audio_file_id: int,
    audio_repo = AudioRepo
):
    """Delete audio file"""
    try:
        # Get audio file to check if it exists
        audio_file = audio_repo.find_by_id(audio_file_id)
        if not audio_file:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Delete file from disk if it exists
        file_path = audio_file.get('file_path')
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to delete audio file from disk: {e}")
        
        # Delete from database
        success = audio_repo.delete(audio_file_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete audio file")
        
        return SuccessResponse(
            success=True,
            message="Audio file deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting audio file: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 