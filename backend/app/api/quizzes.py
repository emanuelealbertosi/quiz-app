from typing import Any, List
import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import sqlalchemy.orm

from app.core.security import (
    get_current_active_user,
    check_admin_privileges,
)
from app.db.session import get_db
from app.models.user import User
from app.models.quiz import Quiz, Category, DifficultyLevel
from app.schemas.quiz import (
    QuizCreate,
    QuizUpdate,
    QuizResponse,
    QuizDetailResponse,
    QuizListResponse,
    QuizAttemptCreate,
    QuizAttemptResponse,
    CategoryInQuiz,
    DifficultyLevelInQuiz,
    CompletedQuizIdResponse,
)

router = APIRouter()

@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(
    *,
    db: Session = Depends(get_db),
    quiz_in: QuizCreate,
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Create new quiz (admin only).
    """
    # Verify difficulty level exists if provided
    difficulty_level_id = None
    if quiz_in.difficulty_level_id:
        difficulty_level = db.query(DifficultyLevel).filter(DifficultyLevel.id == quiz_in.difficulty_level_id).first()
        if not difficulty_level:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Difficulty level not found",
            )
        difficulty_level_id = difficulty_level.id
    
    # Create new quiz
    db_quiz = Quiz(
        question=quiz_in.question,
        options=quiz_in.options,
        correct_answer=quiz_in.correct_answer,
        explanation=quiz_in.explanation,
        points=quiz_in.points,
        creator_id=current_user.id,
        difficulty_level_id=difficulty_level_id,
    )
    
    # Add categories if provided
    if quiz_in.category_ids:
        categories = db.query(Category).filter(Category.id.in_(quiz_in.category_ids)).all()
        if len(categories) != len(quiz_in.category_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more categories not found",
            )
        db_quiz.categories = categories
    
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

@router.get("/", response_model=QuizListResponse)
def read_quizzes(
    skip: int = 0,
    limit: int = 100,
    category_id: int = None,
    difficulty_level_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve quizzes with optional filtering.
    """
    query = db.query(Quiz)
    
    # Apply filters if provided
    if category_id:
        query = query.filter(Quiz.categories.any(Category.id == category_id))
    
    if difficulty_level_id:
        query = query.filter(Quiz.difficulty_level_id == difficulty_level_id)
    
    # Include eager loading for categories and difficulty_level to avoid N+1 queries
    query = query.options(
        sqlalchemy.orm.joinedload(Quiz.categories),
        sqlalchemy.orm.joinedload(Quiz.difficulty_level)
    )
    
    total = query.count()
    quizzes = query.offset(skip).limit(limit).all()
    
    return {"quizzes": quizzes, "total": total}

@router.get("/{quiz_id}", response_model=QuizDetailResponse)
def read_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific quiz by id.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )
    
    return quiz

@router.put("/{quiz_id}", response_model=QuizResponse)
def update_quiz(
    *,
    quiz_id: int,
    quiz_in: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Update a quiz (admin only).
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )
    
    # Update quiz fields
    update_data = quiz_in.dict(exclude_unset=True, exclude={"category_ids"})
    for field, value in update_data.items():
        setattr(quiz, field, value)
    
    # Update categories if provided
    if quiz_in.category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(quiz_in.category_ids)).all()
        if len(categories) != len(quiz_in.category_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more categories not found",
            )
        quiz.categories = categories
    
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz

@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    *,
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> None:
    """
    Delete a quiz (admin only).
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )
    
    db.delete(quiz)
    db.commit()
    return None

@router.post("/attempt", response_model=QuizAttemptResponse, status_code=status.HTTP_201_CREATED)
def create_quiz_attempt(
    *,
    db: Session = Depends(get_db),
    attempt_in: QuizAttemptCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a quiz attempt (for students).
    """
    # Only students can attempt quizzes
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can attempt quizzes",
        )
    
    # Verify quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == attempt_in.quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )
    
    # Check if the user has already successfully completed this quiz
    from app.models.challenge import QuizAttempt
    print(f"\n\nDEBUG - Esecuzione query per verificare tentativi precedenti: user_id={current_user.id}, quiz_id={quiz.id}")
    # Mostra prima tutti i tentativi dell'utente per questo quiz
    all_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.quiz_id == quiz.id
    ).all()
    print(f"DEBUG - Tentativi totali per questo quiz: {len(all_attempts)}")
    for att in all_attempts:
        print(f"DEBUG - Tentativo: id={att.id}, quiz_id={att.quiz_id}, correct={att.correct}, completed={att.completed}")
        
    # Poi cerca specificamente tentativi completati
    previous_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.quiz_id == quiz.id,
        QuizAttempt.completed == True
    ).first()
    
    already_completed = previous_attempt is not None
    print(f"\n\nDEBUG - Verifica quiz già completato: quiz_id={quiz.id}, user_id={current_user.id}")
    print(f"DEBUG - Quiz già completato: {already_completed}")
    if previous_attempt:
        print(f"DEBUG - Tentativo precedente: id={previous_attempt.id}, completed={previous_attempt.completed}, correct={previous_attempt.correct}")
    
    # Check if attempt is correct
    is_correct = attempt_in.answer == quiz.correct_answer
    
    # If the quiz has already been completed successfully, award 0 points
    base_points = quiz.points if is_correct else 0
    points_earned = 0 if already_completed else base_points
    
    print(f"DEBUG - Risposta corretta: {is_correct}")
    print(f"DEBUG - Punti base del quiz: {quiz.points}")
    print(f"DEBUG - Punti che sarebbero guadagnati: {base_points}")
    print(f"DEBUG - Punti effettivamente assegnati: {points_earned} (azzerati: {already_completed})")
    
    # Create attempt
    from app.models.challenge import QuizAttempt
    
    db_attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        answer=attempt_in.answer,
        correct=is_correct,  # Nel modello si chiama 'correct' non 'is_correct'
        points_earned=points_earned,
        completed=is_correct,  # Imposta a true se la risposta è corretta
        # attempt_time e challenge_attempt_id non sono presenti nel modello
    )
    
    db.add(db_attempt)
    
    # Update student's points if correct
    print(f"\n\nDebug - Tentativo quiz: utente={current_user.username}, risposta={attempt_in.answer}, corretta={is_correct}")
    print(f"Debug - Punti prima: {current_user.points}")
    
    if is_correct:
        current_user.points += points_earned
        print(f"Debug - Punti guadagnati: {points_earned}")
        print(f"Debug - Punti dopo l'incremento: {current_user.points}")
        db.add(current_user)
        
    db.commit()
    # Refreshiamo anche l'utente per assicurarci che i punti siano stati aggiornati nel database
    db.refresh(current_user)
    db.refresh(db_attempt)
    
    print(f"Debug - Punti finali dopo commit: {current_user.points}\n\n")
    return db_attempt

# Get completed quizzes for user
# Specificare un formato di risposta semplificato per i quiz completati
from pydantic import BaseModel

class CompletedQuizIdResponse(BaseModel):
    quiz_id: int

@router.get("/completed-quizzes/", response_model=List[CompletedQuizIdResponse])
def get_completed_quizzes(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get quizzes successfully completed by the current user.
    """
    from app.models.challenge import QuizAttempt
    
    # Query for all attempts where the user completed a quiz successfully
    completed_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed == True
    ).all()
    
    print(f"DEBUG - Quiz completati trovati: {len(completed_attempts)}")
    for attempt in completed_attempts:
        print(f"DEBUG - Quiz completato: quiz_id={attempt.quiz_id} (tipo: {type(attempt.quiz_id)}), user_id={attempt.user_id}, completed={attempt.completed}")
    
    # Costruisci una risposta con solo gli ID dei quiz completati
    response = [CompletedQuizIdResponse(quiz_id=attempt.quiz_id) for attempt in completed_attempts]
    print(f"DEBUG - Risposta formattata:", response)
    
    return response

@router.post("/upload-csv", status_code=status.HTTP_201_CREATED)
async def upload_quizzes_csv(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Upload quizzes from a CSV file (admin only).
    
    CSV format:
    question,option1,option2,option3,option4,correct_answer,explanation,points,category_names,difficulty_level
    
    Example:
    "What is 2+2?","1","2","3","4","4","Basic addition",10,"Math,Basic Arithmetic","Easy"
    """
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV",
        )
    
    contents = await file.read()
    
    # Convert to string
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded",
        )
    
    reader = csv.reader(StringIO(text))
    
    # Skip header
    try:
        next(reader)
    except StopIteration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty",
        )
    
    quizzes_created = 0
    errors = []
    
    for i, row in enumerate(reader, start=2):  # Start at 2 for Excel-like rows (accounting for header)
        try:
            if len(row) < 10:
                errors.append(f"Row {i}: Not enough columns")
                continue
            
            question, *options_list, correct_answer, explanation, points, category_names, difficulty_level_name = row
            
            # Format options as a list
            options = [option.strip() for option in options_list if option.strip()]
            
            # Parse points
            try:
                points = int(points)
            except ValueError:
                points = 0
            
            # Get categories
            categories = []
            for cat_name in [c.strip() for c in category_names.split(",") if c.strip()]:
                category = db.query(Category).filter(Category.name == cat_name).first()
                if not category:
                    # Create category if it doesn't exist
                    category = Category(name=cat_name)
                    db.add(category)
                    db.flush()
                categories.append(category)
            
            # Get difficulty level
            difficulty_level = None
            if difficulty_level_name:
                difficulty_level = db.query(DifficultyLevel).filter(
                    DifficultyLevel.name == difficulty_level_name
                ).first()
                if not difficulty_level:
                    # Create simple difficulty levels if they don't exist
                    if difficulty_level_name.lower() == "easy":
                        difficulty_level = DifficultyLevel(name="Easy", value=1)
                    elif difficulty_level_name.lower() == "medium":
                        difficulty_level = DifficultyLevel(name="Medium", value=2)
                    elif difficulty_level_name.lower() == "hard":
                        difficulty_level = DifficultyLevel(name="Hard", value=3)
                    else:
                        difficulty_level = DifficultyLevel(name=difficulty_level_name, value=2)
                    
                    db.add(difficulty_level)
                    db.flush()
            
            # Create quiz
            db_quiz = Quiz(
                question=question,
                options=options,
                correct_answer=correct_answer,
                explanation=explanation,
                points=points,
                creator_id=current_user.id,
                difficulty_level_id=difficulty_level.id if difficulty_level else None,
                categories=categories,
            )
            
            db.add(db_quiz)
            quizzes_created += 1
            
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
    
    # Commit all changes
    db.commit()
    
    return {
        "message": f"Successfully imported {quizzes_created} quizzes",
        "errors": errors if errors else None,
    }
