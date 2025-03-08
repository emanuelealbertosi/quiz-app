from app.models.base import Base
from app.models.user import User, UserRole, parent_student_association
from app.models.quiz import Quiz, Category, DifficultyLevel, Path, quiz_category_association, quiz_path_association
from app.models.challenge import Challenge, QuizAttempt, UserChallenge, UserProgress, UserReward
from app.models.reward import Reward, RewardPurchase, student_reward_shop_association