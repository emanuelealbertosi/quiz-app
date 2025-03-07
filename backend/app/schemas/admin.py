from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class DifficultyLevelBase(BaseModel):
    """Base schema for difficulty level data"""
    name: str
    value: int


class DifficultyLevelCreate(DifficultyLevelBase):
    """Schema for creating a new difficulty level"""
    pass


class DifficultyLevelUpdate(BaseModel):
    """Schema for updating a difficulty level"""
    name: Optional[str] = None
    value: Optional[int] = None


class DifficultyLevelResponse(DifficultyLevelBase):
    """Schema for difficulty level response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PathBase(BaseModel):
    """Base schema for quiz path data"""
    name: str
    description: Optional[str] = None
    bonus_points: int = 10
    icon: Optional[str] = None


class PathCreate(PathBase):
    """Schema for creating a new quiz path"""
    quiz_ids: Optional[List[int]] = None


class PathUpdate(BaseModel):
    """Schema for updating a quiz path"""
    name: Optional[str] = None
    description: Optional[str] = None
    bonus_points: Optional[int] = None
    icon: Optional[str] = None
    quiz_ids: Optional[List[int]] = None


class QuizInPath(BaseModel):
    """Schema for quiz in path response"""
    id: int
    question: str
    
    class Config:
        from_attributes = True


class PathResponse(PathBase):
    """Schema for path response"""
    id: int
    creator_id: int
    created_at: datetime
    quizzes: List[QuizInPath] = []
    
    class Config:
        from_attributes = True


class PathListResponse(BaseModel):
    """Schema for list of paths response"""
    paths: List[PathResponse]
    total: int
    
    class Config:
        from_attributes = True


class TopStudent(BaseModel):
    """Schema for top student in stats"""
    id: int
    username: str
    points: int


class SystemStatsResponse(BaseModel):
    """Schema for system statistics"""
    total_students: int
    total_parents: int
    total_quizzes: int
    total_categories: int
    total_challenges: int
    total_quiz_attempts: int
    total_challenge_attempts: int
    quiz_success_rate: float
    challenge_completion_rate: float
    top_students: List[TopStudent]


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str
    email: str
    password: str
    role: str  # 'student', 'parent', 'admin'
    parent_id: Optional[int] = None  # Solo per gli studenti


class ParentInfo(BaseModel):
    """Schema for parent info"""
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True

class StudentInfo(BaseModel):
    """Schema for student info"""
    id: int
    username: str
    email: str
    points: int
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    points: Optional[int] = None
    parents: Optional[List[ParentInfo]] = None
    
    class Config:
        from_attributes = True

class UserDetailResponse(UserResponse):
    """Schema for detailed user response"""
    full_name: Optional[str] = None
    students: Optional[List[StudentInfo]] = None
    quiz_count: Optional[int] = None
    last_login: Optional[datetime] = None

class QuizAttemptResponse(BaseModel):
    """Schema for quiz attempt response"""
    id: int
    quiz_id: int
    question: str
    answer: str
    correct: bool
    points_earned: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class StudentQuizzesResponse(BaseModel):
    """Schema for student quizzes response"""
    student: UserResponse
    attempts: List[QuizAttemptResponse]
    total_attempts: int
    correct_answers: int
    total_points: int

class StudentProgressSummary(BaseModel):
    """Schema for student progress summary"""
    id: int
    username: str
    points: int
    total_attempts: int
    correct_answers: int
    accuracy: float
    
    class Config:
        from_attributes = True

class ParentChildrenProgressResponse(BaseModel):
    """Schema for parent children progress response"""
    parent: UserResponse
    children: List[StudentProgressSummary]
    total_children: int
