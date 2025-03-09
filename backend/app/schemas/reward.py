from typing import List, Optional
from pydantic import BaseModel, validator
from datetime import datetime

# Base schema for Reward
class RewardBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    point_cost: int
    is_active: bool = True

# Schema for creating a new Reward
class RewardCreate(RewardBase):
    pass

# Schema for updating an existing Reward
class RewardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    point_cost: Optional[int] = None
    is_active: Optional[bool] = None

# Schema for Reward in response
class Reward(RewardBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Schema for assigning rewards to a student's shop
class StudentRewardAssignment(BaseModel):
    student_id: int
    reward_id: int
    quantity: int = 1

# Schema for bulk assignment of rewards
class BulkRewardAssignment(BaseModel):
    student_ids: List[int]
    reward_id: int
    quantity: int = 1

# Schema for reward purchase
class RewardPurchaseCreate(BaseModel):
    reward_id: int

# Schema for reward purchase in response
class RewardPurchase(BaseModel):
    id: int
    user_id: int
    reward_id: int
    point_cost: int
    is_delivered: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Schema for reward in student shop (Admin version)
class StudentShopReward(Reward):
    quantity: int

# Schema for reward in student shop (Parent version)
class ParentStudentShopReward(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    point_cost: int
    quantity: int
    
    class Config:
        orm_mode = True

# Schema for updating purchase delivery status
class RewardPurchaseUpdate(BaseModel):
    is_delivered: bool = True
