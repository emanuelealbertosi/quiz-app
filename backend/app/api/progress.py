from typing import Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    get_current_active_user,
    check_parent_or_admin_privileges,
)
from app.db.session import get_db
from app.models.user import User
from app.models.challenge import QuizAttempt, UserChallenge, UserReward
from app.schemas.progress import (
    RewardCreate,
    RewardUpdate,
    RewardResponse,
    RewardListResponse,
    Create,
    Update,
    Response,
    ListResponse,
    StudentProgressResponse,
)

router = APIRouter()

@router.post("/rewards", response_model=RewardResponse, status_code=status.HTTP_201_CREATED)
def create_reward(
    *,
    db: Session = Depends(get_db),
    reward_in: RewardCreate,
    current_user: User = Depends(check_parent_or_admin_privileges),
) -> Any:
    """
    Create new reward (parent or admin only).
    """
    # Create new reward
    db_reward = Reward(
        name=reward_in.name,
        description=reward_in.description,
        points_cost=reward_in.points_cost,
        icon=reward_in.icon,
        is_active=reward_in.is_active,
        creator_id=current_user.id,
    )
    
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)
    return db_reward

@router.get("/rewards", response_model=RewardListResponse)
def read_rewards(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve rewards.
    """
    query = db.query(Reward)
    
    # Filter by active status if requested
    if active_only:
        query = query.filter(Reward.is_active == True)
    
    # Parents only see rewards they created
    if current_user.role == "parent":
        query = query.filter(Reward.creator_id == current_user.id)
    
    # Students only see active rewards created by their parents or admins
    elif current_user.role == "student":
        parent_ids = [parent.id for parent in current_user.parents]
        query = query.filter(
            Reward.is_active == True,
            (Reward.creator_id.in_(parent_ids)) | 
            (Reward.creator_id.in_(db.query(User.id).filter(User.role == "admin")))
        )
    
    # Admins see all rewards
    
    total = query.count()
    rewards = query.offset(skip).limit(limit).all()
    
    return {"rewards": rewards, "total": total}

@router.get("/rewards/{reward_id}", response_model=RewardResponse)
def read_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific reward by id.
    """
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UserReward not found",
        )
    
    # Check permissions for students
    if current_user.role == "student":
        parent_ids = [parent.id for parent in current_user.parents]
        admin_ids = [user.id for user in db.query(User).filter(User.role == "admin").all()]
        
        if reward.creator_id not in parent_ids and reward.creator_id not in admin_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
    
    # Check permissions for parents
    elif current_user.role == "parent" and reward.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return reward

@router.put("/rewards/{reward_id}", response_model=RewardResponse)
def update_reward(
    *,
    reward_id: int,
    reward_in: RewardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_parent_or_admin_privileges),
) -> Any:
    """
    Update a reward (parent or admin only).
    """
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UserReward not found",
        )
    
    # Check permissions (admin can update any reward, parent can only update their own)
    if current_user.role == "parent" and reward.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Update reward fields
    update_data = reward_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reward, field, value)
    
    db.add(reward)
    db.commit()
    db.refresh(reward)
    return reward

@router.delete("/rewards/{reward_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reward(
    *,
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_parent_or_admin_privileges),
) -> None:
    """
    Delete a reward (parent or admin only).
    """
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UserReward not found",
        )
    
    # Check permissions (admin can delete any reward, parent can only delete their own)
    if current_user.role == "parent" and reward.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    db.delete(reward)
    db.commit()
    return None

@router.post("/redeem", response_model=Response, status_code=status.HTTP_201_CREATED)
def redeem_reward(
    *,
    db: Session = Depends(get_db),
    redemption_in: Create,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Redeem a reward (for students).
    """
    # Only students can redeem rewards
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can redeem rewards",
        )
    
    # Verify reward exists and is active
    reward = db.query(Reward).filter(Reward.id == redemption_in.reward_id, Reward.is_active == True).first()
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UserReward not found or not active",
        )
    
    # Verify student has enough points
    if current_user.points < reward.points_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough points to redeem this reward",
        )
    
    # Create redemption
    db_redemption = UserReward(
        user_id=current_user.id,
        name=reward.name,
        description=reward.description,
        points=reward.points_cost,
        icon=reward.icon
    )
    
    # Deduct points from student
    current_user.points -= reward.points_cost
    
    db.add(db_redemption)
    db.add(current_user)
    db.commit()
    db.refresh(db_redemption)
    return db_redemption

@router.get("/redemptions", response_model=ListResponse)
def read_redemptions(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve reward redemptions.
    """
    query = db.query(UserReward)
    
    # Students only see their own rewards
    if current_user.role == "student":
        query = query.filter(UserReward.user_id == current_user.id)
    
    # Parents only see rewards from their students
    elif current_user.role == "parent":
        student_ids = [student.id for student in current_user.students]
        query = query.filter(UserReward.user_id.in_(student_ids))
    
    # Admins see all redemptions
    
    total = query.count()
    redemptions = query.offset(skip).limit(limit).all()
    
    return {"redemptions": redemptions, "total": total}

# Funzione rimossa perché RewardRedemption non esiste più

@router.get("/student/{student_id}", response_model=StudentProgressResponse)
def get_student_progress(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a student's progress (for parents, admins, or the student themselves).
    """
    # Verify student exists
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )
    
    # Check permissions
    is_self = current_user.id == student_id
    is_parent = current_user.role == "parent" and student in current_user.students
    is_admin = current_user.role == "admin"
    
    if not (is_self or is_parent or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get quiz attempts
    quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).all()
    
    # Get challenge attempts
    challenge_attempts = db.query(UserChallenge).filter(UserChallenge.user_id == student_id).all()
    
    # Get reward redemptions
    redemptions = db.query(UserReward).filter(UserReward.user_id == student_id).all()
    
    # Calculate statistics
    total_quizzes_attempted = len(quiz_attempts)
    correct_quiz_answers = len([qa for qa in quiz_attempts if qa.correct])
    quiz_success_rate = (correct_quiz_answers / total_quizzes_attempted * 100) if total_quizzes_attempted > 0 else 0
    
    total_challenges_attempted = len(challenge_attempts)
    completed_challenges = len([ca for ca in challenge_attempts if ca.completed])
    challenge_completion_rate = (completed_challenges / total_challenges_attempted * 100) if total_challenges_attempted > 0 else 0
    
    total_points_earned = student.points + sum(r.points for r in redemptions)
    total_points_spent = sum(r.points for r in redemptions)
    
    return {
        "student": {
            "id": student.id,
            "username": student.username,
            "full_name": student.full_name,
            "points": student.points,
        },
        "quiz_stats": {
            "total_attempted": total_quizzes_attempted,
            "correct_answers": correct_quiz_answers,
            "success_rate": round(quiz_success_rate, 2),
        },
        "challenge_stats": {
            "total_attempted": total_challenges_attempted,
            "completed": completed_challenges,
            "completion_rate": round(challenge_completion_rate, 2),
        },
        "points_stats": {
            "total_earned": total_points_earned,
            "total_spent": total_points_spent,
            "current_balance": student.points,
        },
        "recent_quiz_attempts": [
            {
                "id": qa.id,
                "quiz_id": qa.quiz_id,
                "is_correct": qa.is_correct,
                "points_earned": qa.points_earned,
                "created_at": qa.created_at,
            }
            for qa in sorted(quiz_attempts, key=lambda x: x.created_at, reverse=True)[:5]
        ],
        "recent_challenge_attempts": [
            {
                "id": ca.id,
                "challenge_id": ca.challenge_id,
                "is_completed": ca.is_completed,
                "points_earned": ca.points_earned,
                "created_at": ca.created_at,
            }
            for ca in sorted(challenge_attempts, key=lambda x: x.created_at, reverse=True)[:5]
        ],
        "recent_redemptions": [
            {
                "id": r.id,
                "reward_id": r.reward_id,
                "points_spent": r.points_spent,
                "status": r.status,
                "created_at": r.created_at,
            }
            for r in sorted(redemptions, key=lambda x: x.created_at, reverse=True)[:5]
        ],
    }
