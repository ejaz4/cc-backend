"""
Conversations router for FastAPI
"""

import os
import logging
import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from fastapi.responses import FileResponse

from api.models import (
    ConversationUploadRequest,
    ConversationFileUploadRequest,
    ConversationResponse,
    ConversationListResponse,
    SummaryRequest,
    SummaryResponse,
    AudioGenerationRequest,
    AudioFileListResponse,
    PaginationParams,
    ConversationFilters,
    ErrorResponse,
    SuccessResponse
)
from api.dependencies import (
    ConversationRepo,
    SummaryRepo,
    AudioRepo,
    ConversationProcessorService,
    WhatsAppParserService,
    SummarizerService,
    ElevenLabsService
)
from api.services.summarizer import ChatSummarizer
from config import Config

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", response_model=SuccessResponse, status_code=201)
async def upload_conversation(
    request: ConversationUploadRequest,
    conversation_processor = ConversationProcessorService,
    conversation_repo = ConversationRepo
):
    """Upload conversation data from any platform"""
    try:
        # Convert Pydantic model to dict for processing
        conversation_data = request.model_dump()
        
        # Process conversation
        result = conversation_processor.process_conversation(conversation_data)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return SuccessResponse(
            success=True,
            message="Conversation uploaded successfully",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-file", response_model=SuccessResponse, status_code=201)
async def upload_conversation_file(
    file: UploadFile = File(...),
    main_user: str = Form(...),
    group_name: str = Form(...),
    conversation_type: str = Form("group"),
    conversation_processor = ConversationProcessorService,
    whatsapp_parser = WhatsAppParserService
):
    """Upload conversation file (legacy support for WhatsApp)"""
    try:
        # Validate file type
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files are supported")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Save file
        filename = f"{session_id}_{file.filename}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Read and save file content
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Parse chat content
        parsed_data = whatsapp_parser.parse_chat_file(file_path)
        
        if 'error' in parsed_data:
            raise HTTPException(status_code=400, detail=parsed_data['error'])
        
        # Create conversation data
        conversation_data = {
            'platform': 'whatsapp',
            'main_user': main_user,
            'group_name': group_name,
            'conversation': content.decode('utf-8'),
            'conversation_type': conversation_type
        }
        
        # Process conversation
        result = conversation_processor.process_conversation(conversation_data)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return SuccessResponse(
            success=True,
            message="Conversation file uploaded successfully",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading conversation file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/summarize")
async def summarize_conversation(session_id: str, conversation)
    session = ChatSummarizer()
    summary = session.generate_summary(conversation)
    

#
        
        # # Get user profiles for context
        # participants = conversation_session.get('participants', [])
        # main_user = conversation_session['main_user']
        # platform = conversation_session['platform']
        
        # # Get user context for better summarization
        # user_contexts = {}
        # for participant in participants:
        #     context = conversation_processor.get_user_context(main_user, participant, platform)
        #     user_contexts[participant] = context
        
        # # Generate summary with context
        # summary_data = summarizer.generate_summary_with_context(
        #     conversation_session['messages'],
        #     participants,
        #     user_contexts
        # )
        
        # if 'error' in summary_data:
        #     conversation_repo.update_status(session_id, 'failed')
        #     raise HTTPException(status_code=500, detail=summary_data['error'])
        
        # # Save summary
        # summary_data['session_id'] = session_id
        # summary_data['main_user'] = main_user
        # summary_id = summary_repo.create(summary_data)
        
        # # Update conversation session status
        # conversation_repo.update_status(session_id, 'summarized')
        
        # # Get the created summary
        # summary = summary_repo.find_by_id(summary_id)
        # if not summary:
        #     raise HTTPException(status_code=500, detail="Failed to retrieve created summary")
        
        # return SummaryResponse(**summary)
        
    # except HTTPException:
    #     raise
    # except Exception as e:
    #     logger.error(f"Error summarizing conversation: {e}")
    #     conversation_repo.update_status(session_id, 'failed')
    #     raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/generate-audio", response_model=AudioFileListResponse)
async def generate_audio(
    session_id: str,
    request: AudioGenerationRequest,
    summary_repo = SummaryRepo,
    audio_repo = AudioRepo,
    elevenlabs_service = ElevenLabsService
):
    """Generate TTS audio for script lines"""
    try:
        # Get summary
        summary = summary_repo.find_by_session_id(session_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found for this session")
        
        script_lines = summary.get('script_lines', [])
        if not script_lines:
            raise HTTPException(status_code=400, detail="No script lines found in summary")
        
        # Extract participants from summary
        participants = summary.get('participants', [])
        main_user = summary.get('main_user', 'unknown')
        platform = 'whatsapp'  # Default platform
        
        # Generate audio files
        results = elevenlabs_service.generate_batch_speech_with_profiles(
            script_lines,
            session_id,
            participants,
            main_user,
            platform
        )
        
        # Get all audio files for this session
        audio_files = audio_repo.find_by_session_id(session_id)
        
        return AudioFileListResponse(
            audio_files=[audio_repo.find_by_id(af['id']) for af in audio_files if af['id']],
            total=len(audio_files)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=ConversationResponse)
async def get_conversation(
    session_id: str,
    conversation_repo = ConversationRepo
):
    """Get conversation session by ID"""
    try:
        conversation = conversation_repo.find_by_session_id(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation session not found")
        
        return ConversationResponse(**conversation)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    platform: Optional[str] = None,
    status: Optional[str] = None,
    main_user: Optional[str] = None,
    conversation_repo = ConversationRepo
):
    """List conversation sessions with pagination and filtering"""
    try:
        # Build filter dictionary
        filter_dict = {}
        if platform:
            filter_dict['platform'] = platform
        if status:
            filter_dict['status'] = status
        if main_user:
            filter_dict['main_user'] = main_user
        
        # Get conversations with pagination
        offset = (page - 1) * per_page
        conversations = conversation_repo.find_all(
            filter_dict=filter_dict,
            limit=per_page,
            sort_by='created_at',
            order='desc'
        )
        
        # Get total count
        total = conversation_repo.count(filter_dict)
        
        return ConversationListResponse(
            conversations=[ConversationResponse(**conv) for conv in conversations],
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}", response_model=SuccessResponse)
async def delete_conversation(
    session_id: str,
    conversation_repo = ConversationRepo
):
    """Delete conversation session"""
    try:
        # Get conversation to check if it exists
        conversation = conversation_repo.find_by_session_id(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation session not found")
        
        # Delete the conversation
        success = conversation_repo.delete(conversation['id'])
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete conversation")
        
        return SuccessResponse(
            success=True,
            message="Conversation deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 