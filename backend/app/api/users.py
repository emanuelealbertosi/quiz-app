from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    get_password_hash,
    get_current_active_user,
    check_admin_privileges,
)
from app.db.session import get_db
from app.models.user import User, parent_student_association
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserDetailResponse,
    UserListResponse,
    ParentStudentLink,
    ChangePoints,
)

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Create new user (admin only).
    """
    # Check if user with this username or email exists
    user = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.email)
    ).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )
    
    # Create new user
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        points=0 if user_in.role == "student" else None,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=UserListResponse)
def read_users(
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Retrieve users (admin only).
    """
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
        
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return {"users": users, "total": total}

@router.get("/me", response_model=UserDetailResponse)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/{user_id}", response_model=UserDetailResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific user by id.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Only admin or parent of student can access another user's data
    is_admin = current_user.role == "admin"
    is_parent_of_user = current_user.role == "parent" and user.role == "student" and user in current_user.students
    is_self = current_user.id == user_id
    
    if not (is_admin or is_parent_of_user or is_self):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    *,
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check permissions (admin can update any user, user can update themselves)
    if not (current_user.role == "admin" or current_user.id == user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Update user fields
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> None:
    """
    Delete a user (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    db.delete(user)
    db.commit()
    return None

@router.post("/link-parent-student", status_code=status.HTTP_201_CREATED)
def link_parent_student(
    *,
    link_in: ParentStudentLink,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Link a parent to a student (admin only).
    """
    # Verify both users exist
    parent = db.query(User).filter(User.id == link_in.parent_id, User.role == "parent").first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent not found",
        )
    
    student = db.query(User).filter(User.id == link_in.student_id, User.role == "student").first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    # Check if link already exists
    existing_link = db.query(parent_student_association).filter_by(
        parent_id=link_in.parent_id, student_id=link_in.student_id
    ).first()
    
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent and student are already linked",
        )
    
    # Create the link
    parent.students.append(student)
    db.commit()
    
    return {"message": "Parent and student linked successfully"}

@router.post("/points", response_model=UserResponse)
def change_student_points(
    *,
    points_in: ChangePoints,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Change a student's points (admin or parent only).
    """
    # Verify student exists
    student = db.query(User).filter(User.id == points_in.student_id, User.role == "student").first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    # Check permissions (admin can change any student's points, parent can only change their students' points)
    is_admin = current_user.role == "admin"
    is_parent_of_student = current_user.role == "parent" and student in current_user.students
    
    if not (is_admin or is_parent_of_student):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Update points
    student.points += points_in.points
    if student.points < 0:
        student.points = 0  # Prevent negative points
    
    db.add(student)
    db.commit()
    db.refresh(student)
    
    return student
