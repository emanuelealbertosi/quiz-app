from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    get_current_active_user,
    check_admin_privileges,
)
from app.db.session import get_db
from app.models.user import User
from app.models.quiz import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)

router = APIRouter()

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Create new category (admin only).
    """
    # Check if category with this name exists
    category = db.query(Category).filter(Category.name == category_in.name).first()
    if category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists",
        )
    
    import random

    # Generate a random color if not provided
    color = category_in.color
    if not color:
        # Genera un colore casuale vibrante (evitare colori troppo scuri o chiari)
        r = random.randint(100, 200)
        g = random.randint(100, 200)
        b = random.randint(100, 200)
        # Rendi uno dei canali più brillante per avere colori più vivaci
        bright_channel = random.randint(0, 2)
        if bright_channel == 0:
            r = random.randint(180, 255)
        elif bright_channel == 1:
            g = random.randint(180, 255)
        else:
            b = random.randint(180, 255)
        color = f"#{r:02x}{g:02x}{b:02x}"

    # Create new category
    db_category = Category(
        name=category_in.name,
        description=category_in.description,
        icon=category_in.icon,
        color=color,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=CategoryListResponse)
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve categories.
    """
    total = db.query(Category).count()
    categories = db.query(Category).offset(skip).limit(limit).all()
    
    return {"categories": categories, "total": total}

@router.get("/{category_id}", response_model=CategoryResponse)
def read_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific category by id.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    *,
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Update a category (admin only).
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    # Update category fields
    update_data = category_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    *,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> None:
    """
    Delete a category (admin only).
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    db.delete(category)
    db.commit()
    return None
