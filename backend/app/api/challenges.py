from typing import Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.security import (
    get_current_active_user,
    check_parent_or_admin_privileges,
)
from app.db.session import get_db
from app.models.user import User
from app.models.quiz import Path
from app.models.challenge import Challenge, UserChallenge
from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeUpdate,
    ChallengeResponse,
    ChallengeDetailResponse,
    ChallengeListResponse,
    UserChallengeCreate,
    UserChallengeResponse,
    UserChallengeDetailResponse,
)

router = APIRouter()

@router.post("/", response_model=ChallengeResponse, status_code=status.HTTP_201_CREATED)
def create_challenge(
    *,
    db: Session = Depends(get_db),
    challenge_in: ChallengeCreate,
    current_user: User = Depends(check_parent_or_admin_privileges),
) -> Any:
    """
    Create new challenge (parent or admin only).
    """
    # Verify path exists
    path = db.query(Path).filter(Path.id == challenge_in.path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found",
        )
    
    # Create new challenge
    db_challenge = Challenge(
        name=challenge_in.name,
        description=challenge_in.description,
        points=challenge_in.points,
        start_date=challenge_in.start_date,
        end_date=challenge_in.end_date,
        is_active=challenge_in.is_active,
        creator_id=current_user.id,
        path_id=challenge_in.path_id,
    )
    
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

@router.get("/", response_model=ChallengeListResponse)
def read_challenges(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve challenges.
    """
    query = db.query(Challenge)
    
    # Filter by active status if requested
    if active_only:
        now = datetime.now()
        query = query.filter(
            Challenge.is_active == True,
            (Challenge.start_date == None) | (Challenge.start_date <= now),
            (Challenge.end_date == None) | (Challenge.end_date >= now)
        )
    
    # Students only see challenges created for them
    if current_user.role == "student":
        # Get challenges created by their parents
        parent_ids = [parent.id for parent in current_user.parents]
        query = query.filter(Challenge.creator_id.in_(parent_ids))
    
    # Parents only see challenges they created
    elif current_user.role == "parent":
        query = query.filter(Challenge.creator_id == current_user.id)
    
    # Admins see all challenges
    
    total = query.count()
    challenges = query.offset(skip).limit(limit).all()
    
    return {"challenges": challenges, "total": total}

@router.get("/{challenge_id}", response_model=ChallengeDetailResponse)
def read_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific challenge by id.
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )
    
    # Check permissions
    if current_user.role == "student":
        # Students can only view challenges created by their parents
        parent_ids = [parent.id for parent in current_user.parents]
        if challenge.creator_id not in parent_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
    elif current_user.role == "parent":
        # Parents can only view challenges they created
        if challenge.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
    
    return challenge

@router.put("/{challenge_id}", response_model=ChallengeResponse)
def update_challenge(
    *,
    challenge_id: int,
    challenge_in: ChallengeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_parent_or_admin_privileges),
) -> Any:
    """
    Update a challenge (parent or admin only).
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )
    
    # Check permissions (admin can update any challenge, parent can only update their own)
    if current_user.role == "parent" and challenge.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Update path if provided
    if challenge_in.path_id is not None:
        path = db.query(Path).filter(Path.id == challenge_in.path_id).first()
        if not path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Path not found",
            )
    
    # Update challenge fields
    update_data = challenge_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(challenge, field, value)
    
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge

@router.delete("/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_challenge(
    *,
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_parent_or_admin_privileges),
) -> None:
    """
    Delete a challenge (parent or admin only).
    """
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )
    
    # Check permissions (admin can delete any challenge, parent can only delete their own)
    if current_user.role == "parent" and challenge.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    db.delete(challenge)
    db.commit()
    return None

@router.post("/attempt", response_model=UserChallengeResponse, status_code=status.HTTP_201_CREATED)
def create_challenge_attempt(
    *,
    db: Session = Depends(get_db),
    attempt_in: UserChallengeCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Start a challenge attempt (for students).
    """
    # Only students can attempt challenges
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can attempt challenges",
        )
    
    # Verify challenge exists and is active
    challenge = db.query(Challenge).filter(Challenge.id == attempt_in.challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )
    
    # Check if challenge is active
    now = datetime.now()
    if not challenge.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge is not active",
        )
    
    if challenge.start_date and challenge.start_date > now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge has not started yet",
        )
    
    if challenge.end_date and challenge.end_date < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge has already ended",
        )
    
    # Check if student already has an active attempt
    existing_attempt = db.query(UserChallenge).filter(
        UserChallenge.student_id == current_user.id,
        UserChallenge.challenge_id == challenge.id,
        UserChallenge.is_completed == False
    ).first()
    
    if existing_attempt:
        return existing_attempt
    
    # Create attempt
    db_attempt = UserChallenge(
        student_id=current_user.id,
        challenge_id=challenge.id,
        is_completed=False,
        points_earned=0,
        progress={
            "total_quizzes": len(challenge.path.quizzes),
            "completed_quizzes": 0,
            "correct_answers": 0,
        },
    )
    
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt

@router.get("/attempt/{attempt_id}", response_model=UserChallengeDetailResponse)
def read_challenge_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific challenge attempt by id.
    """
    attempt = db.query(UserChallenge).filter(UserChallenge.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge attempt not found",
        )
    
    # Check permissions
    is_student_owner = current_user.id == attempt.student_id
    is_parent_of_student = current_user.role == "parent" and attempt.student in current_user.students
    is_admin = current_user.role == "admin"
    
    if not (is_student_owner or is_parent_of_student or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return attempt

@router.put("/attempt/{attempt_id}/complete", response_model=UserChallengeResponse)
def complete_challenge_attempt(
    *,
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Complete a challenge attempt (for students).
    """
    # Only students can complete their own challenges
    attempt = db.query(UserChallenge).filter(UserChallenge.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge attempt not found",
        )
    
    # Check permissions
    if current_user.id != attempt.student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Check if already completed
    if attempt.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge attempt is already completed",
        )
    
    # Get quiz attempts for this challenge
    from app.models.challenge import QuizAttempt
    quiz_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.challenge_attempt_id == attempt.id
    ).all()
    
    # Get all quizzes in the path
    path_quizzes = attempt.challenge.path.quizzes
    
    # Check if all quizzes have been attempted
    attempted_quiz_ids = {qa.quiz_id for qa in quiz_attempts}
    path_quiz_ids = {q.id for q in path_quizzes}
    
    if not attempted_quiz_ids.issuperset(path_quiz_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not all quizzes in the challenge have been attempted",
        )
    
    # Calculate points earned
    correct_attempts = [qa for qa in quiz_attempts if qa.is_correct]
    quiz_points = sum(qa.points_earned for qa in quiz_attempts)
    
    # Add bonus points if all answers are correct
    all_correct = len(correct_attempts) == len(path_quizzes)
    bonus_points = attempt.challenge.path.bonus_points if all_correct else 0
    
    # Set completion data
    attempt.is_completed = True
    attempt.completed_time = func.now()
    attempt.points_earned = quiz_points + bonus_points
    attempt.progress = {
        "total_quizzes": len(path_quizzes),
        "completed_quizzes": len(attempted_quiz_ids),
        "correct_answers": len(correct_attempts),
        "bonus_earned": all_correct,
        "quiz_points": quiz_points,
        "bonus_points": bonus_points,
    }
    
    # Update student's points
    student = attempt.student
    student.points += attempt.points_earned
    
    db.add(attempt)
    db.add(student)
    db.commit()
    db.refresh(attempt)
    
    return attempt
