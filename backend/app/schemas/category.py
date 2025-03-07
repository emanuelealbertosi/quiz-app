from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class CategoryBase(BaseModel):
    """Base schema for category data"""
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Schema for list of categories response"""
    categories: List[CategoryResponse]
    total: int
    
    class Config:
        from_attributes = True
