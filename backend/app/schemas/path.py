from typing import List, Optional, Any
from pydantic import BaseModel

class PathBase(BaseModel):
    name: str
    description: Optional[str] = None
    bonus_points: int = 10
    
class PathCreate(PathBase):
    quiz_ids: List[int]

class PathUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    bonus_points: Optional[int] = None
    quiz_ids: Optional[List[int]] = None

class QuizInPath(BaseModel):
    id: int
    question: str
    points: int
    
    class Config:
        orm_mode = True

class PathResponse(PathBase):
    id: int
    creator_id: int
    quizzes: List[QuizInPath] = []
    completed: Optional[bool] = None
    completed_quizzes: Optional[int] = None
    total_quizzes: Optional[int] = None
    
    class Config:
        orm_mode = True
        
class AssignPathRequest(BaseModel):
    path_id: int
    user_id: int
