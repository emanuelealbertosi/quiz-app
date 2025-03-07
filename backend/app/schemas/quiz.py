from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, validator


class QuizBase(BaseModel):
    """Base schema for quiz data"""
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None
    points: int = 0


class QuizCreate(QuizBase):
    """Schema for creating a new quiz"""
    category_ids: Optional[List[int]] = None
    difficulty_level_id: Optional[int] = None


class QuizUpdate(BaseModel):
    """Schema for updating a quiz"""
    question: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: Optional[int] = None
    category_ids: Optional[List[int]] = None
    difficulty_level_id: Optional[int] = None


class QuizResponse(QuizBase):
    """Schema for quiz response"""
    id: int
    creator_id: int
    difficulty_level_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryInQuiz(BaseModel):
    """Schema for category in quiz response"""
    id: int
    name: str
    color: Optional[str] = None
    
    class Config:
        from_attributes = True


class DifficultyLevelInQuiz(BaseModel):
    """Schema for difficulty level in quiz response"""
    id: int
    name: str
    value: int
    
    class Config:
        from_attributes = True


class QuizDetailResponse(QuizResponse):
    """Schema for detailed quiz response"""
    categories: List[CategoryInQuiz] = []
    difficulty_level: Optional[DifficultyLevelInQuiz] = None
    
    class Config:
        from_attributes = True


class QuizListResponse(BaseModel):
    """Schema for list of quizzes response"""
    quizzes: List[QuizDetailResponse]
    total: int
    
    class Config:
        from_attributes = True


class QuizAttemptCreate(BaseModel):
    """Schema for creating a quiz attempt"""
    quiz_id: int
    answer: str
    attempt_time: Optional[int] = None  # Time taken in seconds
    challenge_attempt_id: Optional[int] = None


class QuizAttemptResponse(BaseModel):
    """Schema for quiz attempt response"""
    id: int
    quiz_id: int
    user_id: int  # Cambiato da student_id per allinearlo al modello
    answer: str
    correct: bool  # Cambiato da is_correct per allinearlo al modello
    points_earned: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompletedQuizIdResponse(BaseModel):
    """Schema for completed quiz ID response"""
    quiz_id: int
    
    class Config:
        from_attributes = True
