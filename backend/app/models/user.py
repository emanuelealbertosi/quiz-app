from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.models.base import BaseModel, Base

# Association table for the many-to-many relationship between parents and students
parent_student_association = Table(
    "parent_student_association",
    Base.metadata,
    Column("parent_id", Integer, ForeignKey("users.id")),
    Column("student_id", Integer, ForeignKey("users.id")),
)

class UserRole(str, PyEnum):
    ADMIN = "admin"
    PARENT = "parent"
    STUDENT = "student"

class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Points are only relevant for students
    points = Column(Integer, default=0)
    
    # A parent can have many students
    students = relationship(
        "User",
        secondary=parent_student_association,
        primaryjoin="User.id==parent_student_association.c.parent_id",
        secondaryjoin="User.id==parent_student_association.c.student_id",
        backref="parents"
    )
    
    # Relationships
    created_quizzes = relationship("Quiz", back_populates="creator")
    quiz_attempts = relationship("QuizAttempt", back_populates="student")
    challenges = relationship("UserChallenge", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")
    rewards = relationship("UserReward", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}, role={self.role}>"
