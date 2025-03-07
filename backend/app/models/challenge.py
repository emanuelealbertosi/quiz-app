from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel

class Challenge(BaseModel):
    """Model for quiz challenges (time-limited sets of quizzes)"""
    
    __tablename__ = "challenges"
    
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    points = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    
    # Foreign keys
    path_id = Column(Integer, ForeignKey("paths.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    path = relationship("Path", back_populates="challenges")
    creator = relationship("User")
    user_challenges = relationship("UserChallenge", back_populates="challenge")

class QuizAttempt(BaseModel):
    """Model for tracking user attempts at quizzes"""
    
    __tablename__ = "quiz_attempts"
    
    answer = Column(String, nullable=False)
    correct = Column(Boolean, nullable=False)
    points_earned = Column(Integer, default=0)
    completed = Column(Boolean, default=False)  # Traccia se il quiz è stato completato con successo
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    
    # Relationships
    student = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")

class UserChallenge(BaseModel):
    """Model for tracking user participation in challenges"""
    
    __tablename__ = "user_challenges"
    
    completed = Column(Boolean, default=False)
    points_earned = Column(Integer, default=0)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="challenges")
    challenge = relationship("Challenge", back_populates="user_challenges")

class UserProgress(BaseModel):
    """Model for tracking user progress in paths"""
    
    __tablename__ = "user_progress"
    
    points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    completed_quizzes = Column(Integer, default=0)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    path_id = Column(Integer, ForeignKey("paths.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    path = relationship("Path")

class UserReward(BaseModel):
    """Model for user rewards and achievements"""
    
    __tablename__ = "user_rewards"
    
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    points = Column(Integer, default=0)
    icon = Column(String, nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="rewards")
