from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ChallengeBase(BaseModel):
    """Base schema for challenge data"""
    name: str
    description: Optional[str] = None
    points: int = 10
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True


class ChallengeCreate(ChallengeBase):
    """Schema for creating a new challenge"""
    path_id: int


class ChallengeUpdate(BaseModel):
    """Schema for updating a challenge"""
    name: Optional[str] = None
    description: Optional[str] = None
    points: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    path_id: Optional[int] = None


class PathInChallenge(BaseModel):
    """Schema for path in challenge response"""
    id: int
    name: str
    bonus_points: int
    
    class Config:
        from_attributes = True


class ChallengeResponse(ChallengeBase):
    """Schema for challenge response"""
    id: int
    creator_id: int
    path_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChallengeDetailResponse(ChallengeResponse):
    """Schema for detailed challenge response"""
    path: PathInChallenge
    
    class Config:
        from_attributes = True


class ChallengeListResponse(BaseModel):
    """Schema for list of challenges response"""
    challenges: List[ChallengeResponse]
    total: int
    
    class Config:
        from_attributes = True


class UserChallengeCreate(BaseModel):
    """Schema for creating a challenge attempt"""
    challenge_id: int


class UserChallengeResponse(BaseModel):
    """Schema for challenge attempt response"""
    id: int
    student_id: int
    challenge_id: int
    start_time: datetime
    completed_time: Optional[datetime] = None
    is_completed: bool
    points_earned: int
    progress: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizAttemptInChallenge(BaseModel):
    """Schema for quiz attempt in challenge response"""
    id: int
    quiz_id: int
    answer: str
    is_correct: bool
    points_earned: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserChallengeDetailResponse(UserChallengeResponse):
    """Schema for detailed challenge attempt response"""
    challenge: ChallengeResponse
    quiz_attempts: List[QuizAttemptInChallenge] = []
    
    class Config:
        from_attributes = True
