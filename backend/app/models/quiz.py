from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, Boolean, Table
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, Base

# Association table for the many-to-many relationship between quizzes and categories
quiz_category_association = Table(
    "quiz_category_association",
    Base.metadata,
    Column("quiz_id", Integer, ForeignKey("quizzes.id")),
    Column("category_id", Integer, ForeignKey("categories.id")),
)

# Association table for the many-to-many relationship between quizzes and paths
quiz_path_association = Table(
    "quiz_path_association",
    Base.metadata,
    Column("quiz_id", Integer, ForeignKey("quizzes.id")),
    Column("path_id", Integer, ForeignKey("paths.id")),
)

class Category(BaseModel):
    """Model for quiz categories (e.g., Math, Science, etc.)"""
    
    __tablename__ = "categories"
    
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)  # Path or name of the icon
    color = Column(String, nullable=True)  # Hexadecimal color code (e.g., #FF5733)
    
    # Relationships
    quizzes = relationship(
        "Quiz", 
        secondary=quiz_category_association,
        back_populates="categories"
    )
    
    def __repr__(self):
        return f"<Category {self.name}>"

class DifficultyLevel(BaseModel):
    """Model for difficulty levels (e.g., Easy, Medium, Hard)"""
    
    __tablename__ = "difficulty_levels"
    
    name = Column(String, nullable=False, unique=True)
    value = Column(Integer, nullable=False)  # Numeric value for sorting
    
    # Relationships
    quizzes = relationship("Quiz", back_populates="difficulty_level")
    
    def __repr__(self):
        return f"<DifficultyLevel {self.name}, value={self.value}>"

class Quiz(BaseModel):
    """Model for individual quiz questions"""
    
    __tablename__ = "quizzes"
    
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # JSON array of possible answers
    correct_answer = Column(String, nullable=False)
    explanation = Column(Text, nullable=True)  # Optional explanation of the answer
    points = Column(Integer, default=0)
    
    # Foreign keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    difficulty_level_id = Column(Integer, ForeignKey("difficulty_levels.id"), nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="created_quizzes")
    difficulty_level = relationship("DifficultyLevel", back_populates="quizzes")
    categories = relationship(
        "Category", 
        secondary=quiz_category_association,
        back_populates="quizzes"
    )
    paths = relationship(
        "Path", 
        secondary=quiz_path_association,
        back_populates="quizzes"
    )
    attempts = relationship("QuizAttempt", back_populates="quiz")
    
    def __repr__(self):
        return f"<Quiz id={self.id}, question_preview={self.question[:30]}...>"

class Path(BaseModel):
    """Model for quiz paths (sequences of quizzes with bonus points)"""
    
    __tablename__ = "paths"
    
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    bonus_points = Column(Integer, default=10)
    required_points = Column(Integer, default=0)
    icon = Column(String, nullable=True)
    
    # Foreign keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User")
    quizzes = relationship(
        "Quiz", 
        secondary=quiz_path_association,
        back_populates="paths"
    )
    challenges = relationship("Challenge", back_populates="path")
    
    def __repr__(self):
        return f"<Path {self.name}, bonus_points={self.bonus_points}>"
