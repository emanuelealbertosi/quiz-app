from app.models.base import Base
from app.models.quiz import Category, DifficultyLevel, quiz_category_association, quiz_path_association
from app.models.challenge import Challenge, QuizAttempt, UserChallenge, UserProgress, UserReward
from app.models.user import User
from app.models.quiz import Quiz, Path

# This will ensure all models are imported and available when creating tables
__all__ = [
    "Base",
    "User",
    "Quiz",
    "Category",
    "DifficultyLevel",
    "Path",
    "Challenge",
    "QuizAttempt",
    "UserChallenge",
    "UserProgress",
    "UserReward"
]
