# Import all schemas here for easy access
from app.schemas.token import Token, TokenPayload
from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserResponse, 
    UserDetailResponse, UserListResponse, 
    ParentStudentLink, ChangePoints
)
from app.schemas.reward import (
    RewardBase, RewardCreate, RewardUpdate, Reward,
    StudentRewardAssignment, BulkRewardAssignment,
    RewardPurchaseCreate, RewardPurchase, 
    StudentShopReward, RewardPurchaseUpdate
)
