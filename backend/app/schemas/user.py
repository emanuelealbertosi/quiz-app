from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    """Base schema for user data"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str
    
    @validator("role")
    def validate_role(cls, v):
        allowed_roles = ["admin", "parent", "student"]
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of {allowed_roles}")
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    points: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Schema for detailed user response"""
    students: Optional[List["UserResponse"]] = None
    
    class Config:
        from_attributes = True


# Self-referencing model
UserDetailResponse.update_forward_refs()


class UserListResponse(BaseModel):
    """Schema for list of users response"""
    users: List[UserResponse]
    total: int
    
    class Config:
        from_attributes = True


class ParentStudentLink(BaseModel):
    """Schema for linking a parent and student"""
    parent_id: int
    student_id: int


class ChangePoints(BaseModel):
    """Schema for changing a student's points"""
    student_id: int
    points: int  # Can be positive or negative
