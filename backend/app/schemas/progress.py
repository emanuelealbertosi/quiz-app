from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class RewardBase(BaseModel):
    """Base schema for reward data"""
    name: str
    description: Optional[str] = None
    points_cost: int
    icon: Optional[str] = None
    is_active: bool = True


class RewardCreate(RewardBase):
    """Schema for creating a new reward"""
    pass


class RewardUpdate(BaseModel):
    """Schema for updating a reward"""
    name: Optional[str] = None
    description: Optional[str] = None
    points_cost: Optional[int] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class RewardResponse(RewardBase):
    """Schema for reward response"""
    id: int
    creator_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RewardListResponse(BaseModel):
    """Schema for list of rewards response"""
    rewards: List[RewardResponse]
    total: int
    
    class Config:
        from_attributes = True


class Create(BaseModel):
    """Schema for creating a reward redemption"""
    reward_id: int


class Update(BaseModel):
    """Schema for updating a reward redemption"""
    status: str  # pending, approved, rejected, fulfilled


class Response(BaseModel):
    """Schema for reward redemption response"""
    id: int
    student_id: int
    reward_id: int
    points_spent: int
    status: str
    redemption_date: datetime
    approved_by_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ListResponse(BaseModel):
    """Schema for list of reward redemptions response"""
    redemptions: List[Response]
    total: int
    
    class Config:
        from_attributes = True


class StudentInfo(BaseModel):
    """Schema for student info in progress response"""
    id: int
    username: str
    full_name: Optional[str] = None
    points: int


class QuizStats(BaseModel):
    """Schema for quiz statistics"""
    total_attempted: int
    correct_answers: int
    success_rate: float


class ChallengeStats(BaseModel):
    """Schema for challenge statistics"""
    total_attempted: int
    completed: int
    completion_rate: float


class PointsStats(BaseModel):
    """Schema for points statistics"""
    total_earned: int
    total_spent: int
    current_balance: int


class RecentQuizAttempt(BaseModel):
    """Schema for recent quiz attempt in progress response"""
    id: int
    quiz_id: int
    is_correct: bool
    points_earned: int
    created_at: datetime


class RecentUserChallenge(BaseModel):
    """Schema for recent challenge attempt in progress response"""
    id: int
    challenge_id: int
    is_completed: bool
    points_earned: int
    created_at: datetime


class RecentRedemption(BaseModel):
    """Schema for recent redemption in progress response"""
    id: int
    reward_id: int
    points_spent: int
    status: str
    created_at: datetime


class StudentProgressResponse(BaseModel):
    """Schema for student progress response"""
    student: StudentInfo
    quiz_stats: QuizStats
    challenge_stats: ChallengeStats
    points_stats: PointsStats
    recent_quiz_attempts: List[RecentQuizAttempt]
    recent_challenge_attempts: List[RecentUserChallenge]
    recent_redemptions: List[RecentRedemption]
