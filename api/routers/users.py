"""
Users router for FastAPI
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from api.models import (
    UserProfileResponse,
    UserProfileListResponse,
    UserProfileUpdateRequest,
    SuccessResponse,
    PaginationParams,
    UserProfileFilters
)
from api.dependencies import UserProfileRepo

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/profiles", response_model=UserProfileListResponse)
async def get_user_profiles(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    platform: Optional[str] = None,
    relationship_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    main_user_id: Optional[int] = None,
    user_profile_repo = UserProfileRepo
):
    """Get user profiles with pagination and filtering"""
    try:
        # Build filter dictionary
        filter_dict = {}
        if platform:
            filter_dict['platform'] = platform
        if relationship_type:
            filter_dict['relationship_type'] = relationship_type
        if is_active is not None:
            filter_dict['is_active'] = is_active
        if main_user_id:
            filter_dict['main_user_id'] = main_user_id
        
        # Get profiles with pagination
        profiles = user_profile_repo.find_all(
            filter_dict=filter_dict,
            limit=per_page,
            sort_by='created_at',
            order='desc'
        )
        
        # Get total count
        total = user_profile_repo.count(filter_dict)
        
        return UserProfileListResponse(
            profiles=[UserProfileResponse(**profile) for profile in profiles],
            total=total
        )
        
    except Exception as e:
        logger.error(f"Error getting user profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profiles/{profile_id}", response_model=UserProfileResponse)
async def get_user_profile(
    profile_id: int,
    user_profile_repo = UserProfileRepo
):
    """Get user profile by ID"""
    try:
        profile = user_profile_repo.find_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return UserProfileResponse(**profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profiles/{profile_id}", response_model=UserProfileResponse)
async def update_user_profile(
    profile_id: int,
    request: UserProfileUpdateRequest,
    user_profile_repo = UserProfileRepo
):
    """Update user profile"""
    try:
        # Check if profile exists
        profile = user_profile_repo.find_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Update profile
        update_data = request.model_dump(exclude_unset=True)
        success = user_profile_repo.update(profile_id, update_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update user profile")
        
        # Get updated profile
        updated_profile = user_profile_repo.find_by_id(profile_id)
        return UserProfileResponse(**updated_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profiles/frequent", response_model=UserProfileListResponse)
async def get_frequent_contacts(
    main_user_id: int = Query(..., gt=0),
    limit: int = Query(10, ge=1, le=50),
    user_profile_repo = UserProfileRepo
):
    """Get most frequent contacts for a user"""
    try:
        profiles = user_profile_repo.find_frequent_contacts(main_user_id, limit)
        
        return UserProfileListResponse(
            profiles=[UserProfileResponse(**profile) for profile in profiles],
            total=len(profiles)
        )
        
    except Exception as e:
        logger.error(f"Error getting frequent contacts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/profiles/{profile_id}", response_model=SuccessResponse)
async def delete_user_profile(
    profile_id: int,
    user_profile_repo = UserProfileRepo
):
    """Delete user profile"""
    try:
        # Check if profile exists
        profile = user_profile_repo.find_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Delete profile
        success = user_profile_repo.delete(profile_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete user profile")
        
        return SuccessResponse(
            success=True,
            message="User profile deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 