from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import func, desc, case, distinct
from sqlalchemy.orm import Session

from app.core.security import (
    get_current_active_user,
    check_admin_privileges,
)
from app.db.session import get_db
from app.models.user import User
from app.models.quiz import DifficultyLevel, Path, Quiz, Category, quiz_category_association, quiz_path_association
from app.models.challenge import QuizAttempt
from app.schemas.admin import (
    DifficultyLevelCreate,
    DifficultyLevelUpdate,
    DifficultyLevelResponse,
    PathCreate,
    PathUpdate,
    PathResponse,
    PathListResponse,
    SystemStatsResponse,
    UserCreate,
    UserResponse,
    UserDetailResponse,
    StudentQuizzesResponse,
    QuizAttemptResponse,
    ParentChildrenProgressResponse,
    StudentProgressSummary,
)

router = APIRouter()

@router.get("/test", status_code=status.HTTP_200_OK)
def test_admin_api(
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Test endpoint for admin API (admin only).
    """
    return {"message": "Admin API is working!", "user": current_user.username}

# Difficulty Levels
@router.post("/difficulty-levels", response_model=DifficultyLevelResponse, status_code=status.HTTP_201_CREATED)
def create_difficulty_level(
    *,
    db: Session = Depends(get_db),
    level_in: DifficultyLevelCreate,
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Create new difficulty level (admin only).
    """
    # Check if level with this name exists
    level = db.query(DifficultyLevel).filter(DifficultyLevel.name == level_in.name).first()
    if level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Difficulty level already exists",
        )
    
    # Create new difficulty level
    db_level = DifficultyLevel(
        name=level_in.name,
        value=level_in.value,
    )
    db.add(db_level)
    db.commit()
    db.refresh(db_level)
    return db_level

@router.get("/difficulty-levels", response_model=List[DifficultyLevelResponse])
def read_difficulty_levels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve all difficulty levels.
    """
    levels = db.query(DifficultyLevel).order_by(DifficultyLevel.value).all()
    return levels

@router.put("/difficulty-levels/{level_id}", response_model=DifficultyLevelResponse)
def update_difficulty_level(
    *,
    level_id: int,
    level_in: DifficultyLevelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Update a difficulty level (admin only).
    """
    level = db.query(DifficultyLevel).filter(DifficultyLevel.id == level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Difficulty level not found",
        )
    
    # Update level fields
    update_data = level_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(level, field, value)
    
    db.add(level)
    db.commit()
    db.refresh(level)
    return level

@router.delete("/difficulty-levels/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_difficulty_level(
    *,
    level_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> None:
    """
    Delete a difficulty level (admin only).
    """
    level = db.query(DifficultyLevel).filter(DifficultyLevel.id == level_id).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Difficulty level not found",
        )
    
    db.delete(level)
    db.commit()
    return None

# Paths (Quiz Paths)
@router.post("/paths", response_model=PathResponse, status_code=status.HTTP_201_CREATED)
def create_path(
    *,
    db: Session = Depends(get_db),
    path_in: PathCreate,
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Create new quiz path (admin only).
    """
    # Create new path
    db_path = Path(
        name=path_in.name,
        description=path_in.description,
        bonus_points=path_in.bonus_points,
        icon=path_in.icon,
        creator_id=current_user.id,
    )
    
    # Add quizzes if provided
    if path_in.quiz_ids:
        from app.models.quiz import Quiz
        quizzes = db.query(Quiz).filter(Quiz.id.in_(path_in.quiz_ids)).all()
        if len(quizzes) != len(path_in.quiz_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more quizzes not found",
            )
        db_path.quizzes = quizzes
    
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    return db_path

@router.get("/paths", response_model=PathListResponse)
def read_paths(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve quiz paths.
    """
    total = db.query(Path).count()
    paths = db.query(Path).offset(skip).limit(limit).all()
    
    return {"paths": paths, "total": total}

@router.get("/paths/{path_id}", response_model=PathResponse)
def read_path(
    path_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific quiz path by id.
    """
    path = db.query(Path).filter(Path.id == path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found",
        )
    
    return path

@router.put("/paths/{path_id}", response_model=PathResponse)
def update_path(
    *,
    path_id: int,
    path_in: PathUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Update a quiz path (admin only).
    """
    path = db.query(Path).filter(Path.id == path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found",
        )
    
    # Update path fields
    update_data = path_in.dict(exclude_unset=True, exclude={"quiz_ids"})
    for field, value in update_data.items():
        setattr(path, field, value)
    
    # Update quizzes if provided
    if path_in.quiz_ids is not None:
        from app.models.quiz import Quiz
        quizzes = db.query(Quiz).filter(Quiz.id.in_(path_in.quiz_ids)).all()
        if len(quizzes) != len(path_in.quiz_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more quizzes not found",
            )
        path.quizzes = quizzes
    
    db.add(path)
    db.commit()
    db.refresh(path)
    return path

@router.delete("/paths/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_path(
    *,
    path_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> None:
    """
    Delete a quiz path (admin only).
    """
    path = db.query(Path).filter(Path.id == path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found",
        )
    
    db.delete(path)
    db.commit()
    return None

@router.get("/stats", response_model=dict)
def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Get system statistics (admin only).
    """
    try:
        from app.models.challenge import Challenge, QuizAttempt, UserChallenge
        from datetime import datetime
        
        # Conta gli utenti
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        inactive_users = total_users - active_users
        admin_users = db.query(User).filter(User.role == "admin").count()
        total_students = db.query(User).filter(User.role == "student").count()
        active_students = db.query(User).filter(User.role == "student", User.is_active == True).count()
        total_parents = db.query(User).filter(User.role == "parent").count()
        active_parents = db.query(User).filter(User.role == "parent", User.is_active == True).count()
        
        # Conta i quiz e le categorie
        total_quizzes = db.query(Quiz).count()
        total_categories = db.query(Category).count()
        total_challenges = db.query(Challenge).count()
        total_quiz_attempts = db.query(QuizAttempt).count()
        total_challenge_attempts = db.query(UserChallenge).count()
        
        # Calcola il tasso di successo
        successful_quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.correct == True).count()
        quiz_success_rate = (successful_quiz_attempts / total_quiz_attempts * 100) if total_quiz_attempts > 0 else 0
        
        # Nota: la colonna completed potrebbe non esistere nella tabella UserChallenge
        try:
            completed_challenge_attempts = db.query(UserChallenge).filter(UserChallenge.completed == True).count()
            challenge_completion_rate = (completed_challenge_attempts / total_challenge_attempts * 100) if total_challenge_attempts > 0 else 0
        except Exception as e:
            print(f"Error getting completed challenges: {e}")
            completed_challenge_attempts = 0
            challenge_completion_rate = 0
        
        # Statistiche sui quiz per categoria
        category_stats = []
        for category in db.query(Category).all():
            # Conta i quiz associati a questa categoria
            quizzes_count = db.query(quiz_category_association.c.quiz_id)\
                .filter(quiz_category_association.c.category_id == category.id)\
                .distinct().count()
            
            # Conta i tentativi per i quiz di questa categoria
            attempts_subquery = db.query(quiz_category_association.c.quiz_id)\
                .filter(quiz_category_association.c.category_id == category.id).subquery()
            
            attempts_count = db.query(QuizAttempt)\
                .filter(QuizAttempt.quiz_id.in_(attempts_subquery))\
                .count()
            
            # Conta i tentativi corretti per i quiz di questa categoria
            success_count = db.query(QuizAttempt)\
                .filter(QuizAttempt.quiz_id.in_(attempts_subquery), QuizAttempt.correct == True)\
                .count()
            
            success_rate = (success_count / attempts_count * 100) if attempts_count > 0 else 0
            
            category_stats.append({
                "id": category.id,
                "name": category.name,
                "quizzes_count": quizzes_count,
                "attempts_count": attempts_count,
                "success_count": success_count,
                "success_rate": round(success_rate, 2)
            })
        
        # Top students by points
        top_students = db.query(User).filter(User.role == "student").order_by(User.points.desc()).limit(5).all()
        
        # Studenti più attivi (con più tentativi di quiz)
        most_active_students_query = (
            db.query(
                User.id,
                User.username,
                User.email,
                User.points,
                func.count(QuizAttempt.id).label('attempts_count')
            )
            .join(QuizAttempt, User.id == QuizAttempt.user_id)
            .filter(User.role == "student")
            .group_by(User.id)
            .order_by(desc('attempts_count'))
            .limit(5)
        )
        
        most_active_students = []
        for student in most_active_students_query.all():
            most_active_students.append({
                "id": student.id,
                "username": student.username,
                "email": student.email,
                "points": student.points or 0,
                "attempts_count": student.attempts_count
            })
        
        # Informazioni sul sistema
        api_version = "1.0.0"
        environment = "development"
        server_time = datetime.utcnow().isoformat()
        
        return {
            # Statistiche utenti
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "admin_users": admin_users,
            "total_students": total_students,
            "active_students": active_students,
            "total_parents": total_parents,
            "active_parents": active_parents,
            
            # Statistiche quiz e categorie
            "total_quizzes": total_quizzes,
            "total_categories": total_categories,
            "total_challenges": total_challenges,
            "total_quiz_attempts": total_quiz_attempts,
            "total_challenge_attempts": total_challenge_attempts,
            "quiz_success_rate": round(quiz_success_rate, 2),
            "challenge_completion_rate": round(challenge_completion_rate, 2),
            
            # Statistiche dettagliate
            "category_stats": category_stats,
            "top_students": [{"id": s.id, "username": s.username, "points": s.points or 0} for s in top_students],
            "most_active_students": most_active_students,
            
            # Informazioni sistema
            "api_version": api_version,
            "environment": environment,
            "server_time": server_time
        }
    except Exception as e:
        print(f"Error in get_system_stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting system stats: {str(e)}"
        )

@router.post("/import-quizzes", status_code=status.HTTP_201_CREATED)
def import_quizzes_from_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Import quizzes from a CSV file (admin only).
    CSV format: question,option1,option2,option3,option4,correct_answer,explanation,difficulty_level,category
    """
    import csv
    import io
    from app.models.quiz import Quiz, Category, DifficultyLevel
    
    # Leggi il file CSV
    content = file.file.read().decode('utf-8')
    csv_reader = csv.reader(io.StringIO(content))
    next(csv_reader)  # Salta l'intestazione
    
    imported_count = 0
    errors = []
    
    for row_idx, row in enumerate(csv_reader, start=2):  # Start from 2 to account for header
        try:
            if len(row) < 9:
                errors.append(f"Row {row_idx}: Not enough columns. Expected at least 9 columns.")
                continue
                
            question, option1, option2, option3, option4, correct_answer, explanation, difficulty_name, category_name = row[:9]
            
            # Verifica che la risposta corretta sia tra le opzioni
            options = [option1, option2, option3, option4]
            if correct_answer not in options:
                errors.append(f"Row {row_idx}: Correct answer '{correct_answer}' is not among the options.")
                continue
            
            # Trova o crea la categoria
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                category = Category(name=category_name)
                db.add(category)
                db.flush()
            
            # Trova il livello di difficoltà
            difficulty = db.query(DifficultyLevel).filter(DifficultyLevel.name == difficulty_name).first()
            if not difficulty:
                errors.append(f"Row {row_idx}: Difficulty level '{difficulty_name}' not found.")
                continue
            
            # Crea il quiz
            quiz = Quiz(
                question=question,
                options=options,
                correct_answer=correct_answer,
                explanation=explanation,
                creator_id=current_user.id,
                difficulty_level_id=difficulty.id
            )
            
            # Aggiungi la categoria al quiz
            quiz.categories.append(category)
            
            db.add(quiz)
            imported_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_idx}: Error - {str(e)}")
    
    db.commit()
    
    return {
        "imported_count": imported_count,
        "errors": errors
    }

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Create a new user with a specific role (admin only).
    """
    from app.core.security import get_password_hash
    
    # Verifica se esiste già un utente con lo stesso username o email
    user = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.email)
    ).first()
    
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )
    
    # Verifica che il ruolo sia valido
    valid_roles = ["student", "parent", "admin"]
    if user_in.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )
    
    # Se è uno studente, verifica che il parent_id sia valido
    if user_in.role == "student" and user_in.parent_id:
        parent = db.query(User).filter(
            (User.id == user_in.parent_id) & (User.role == "parent")
        ).first()
        
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent_id. Parent not found or not a parent role.",
            )
    
    # Crea il nuovo utente
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        points=0 if user_in.role == "student" else None,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Se è uno studente e ha un parent_id, aggiungi la relazione
    if user_in.role == "student" and user_in.parent_id:
        parent = db.query(User).filter(User.id == user_in.parent_id).first()
        if parent:
            # Aggiungi il genitore alla lista dei genitori dello studente
            user.parents.append(parent)
            db.commit()
    
    return user

@router.get("/users", status_code=status.HTTP_200_OK)
def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Get all users, optionally filtered by role (admin only).
    """
    query = db.query(User)
    
    if role:
        valid_roles = ["student", "parent", "admin"]
        if role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role filter. Must be one of: {', '.join(valid_roles)}",
            )
        query = query.filter(User.role == role)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    # Convertiamo gli oggetti User in UserResponse
    user_responses = [UserResponse.from_orm(user) for user in users]
    
    return {
        "users": user_responses,
        "total": total
    }

@router.put("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,
    user_update: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Update an existing user (admin only).
    """
    from app.core.security import get_password_hash
    
    # Verifica se l'utente esiste
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Verifica che il ruolo sia valido
    valid_roles = ["student", "parent", "admin"]
    if user_update.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )
    
    # Verifica se l'username o l'email sono già in uso da un altro utente
    existing_user = db.query(User).filter(
        (User.id != user_id) & 
        ((User.username == user_update.username) | (User.email == user_update.email))
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already in use by another user",
        )
    
    # Se è uno studente, verifica che il parent_id sia valido
    if user_update.role == "student" and user_update.parent_id:
        parent = db.query(User).filter(
            (User.id == user_update.parent_id) & (User.role == "parent")
        ).first()
        
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent_id. Parent not found or not a parent role.",
            )
    
    # Aggiorna i campi dell'utente
    user.username = user_update.username
    user.email = user_update.email
    user.role = user_update.role
    
    # Aggiorna la password solo se è stata fornita
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)
    
    # Gestisci la relazione genitore-studente
    if user_update.role == "student" and user_update.parent_id:
        # Rimuovi tutte le relazioni genitore-studente esistenti
        user.parents.clear()
        
        # Aggiungi la nuova relazione genitore-studente
        parent = db.query(User).filter(User.id == user_update.parent_id).first()
        if parent:
            user.parents.append(parent)
            db.commit()
    elif user_update.role != "student":
        # Se l'utente non è più uno studente, rimuovi tutte le relazioni genitore-studente
        user.parents.clear()
    
    # Aggiorna i punti (solo per gli studenti)
    if user_update.role == "student" and user.points is None:
        user.points = 0
    elif user_update.role != "student":
        user.points = None
    
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/users/{user_id}", response_model=dict)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Get detailed information about a user (admin only).
    """
    try:
        # Verifica se l'utente esiste
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Informazioni aggiuntive in base al ruolo dell'utente
        role_info = {}
        
        if user.role == "student":
            # Calcola il numero totale di tentativi
            total_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user.id).count()
            
            # Calcola il numero di risposte corrette
            correct_answers = db.query(QuizAttempt).filter(
                QuizAttempt.user_id == user.id,
                QuizAttempt.correct == True
            ).count()
            
            # Calcola l'accuratezza
            accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0
            
            # Aggiungi informazioni specifiche per gli studenti
            role_info = {
                "total_attempts": total_attempts,
                "correct_answers": correct_answers,
                "accuracy": round(accuracy, 2),
                "parents": [{
                    "id": parent.id,
                    "username": parent.username,
                    "email": parent.email
                } for parent in user.parents]
            }
        elif user.role == "parent":
            # Aggiungi informazioni specifiche per i genitori
            role_info = {
                "children": [{
                    "id": child.id,
                    "username": child.username,
                    "email": child.email,
                    "points": child.points or 0
                } for child in user.students]
            }
        
        # Restituisci i dati dell'utente con informazioni aggiuntive
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "points": user.points if user.role == "student" else None,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "role_info": role_info
        }
    except Exception as e:
        print(f"Error in get_user_detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user details: {str(e)}"
        )

@router.put("/users/{user_id}/toggle-active", response_model=dict)
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Toggle the active status of a user (admin only).
    """
    try:
        # Verifica se l'utente esiste
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Cambia lo stato dell'utente
        user.is_active = not user.is_active
        db.commit()
        db.refresh(user)
        
        # Restituisci i dati dell'utente aggiornati
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "message": f"User {user.username} {'activated' if user.is_active else 'deactivated'} successfully"
        }
    except Exception as e:
        print(f"Error in toggle_user_active: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling user active status: {str(e)}"
        )

@router.put("/users/{user_id}/points", response_model=dict)
def update_student_points(
    user_id: int,
    points: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Update the points of a student (admin only).
    """
    try:
        # Verifica se l'utente esiste
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Verifica che l'utente sia uno studente
        if user.role != "student":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a student",
            )
        
        # Aggiorna i punti dello studente
        user.points = points
        db.commit()
        db.refresh(user)
        
        # Restituisci i dati dell'utente aggiornati
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "points": user.points,
            "message": f"Points for {user.username} updated to {user.points}"
        }
    except Exception as e:
        print(f"Error in update_student_points: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating student points: {str(e)}"
        )

@router.get("/users-stats", response_model=dict)
def get_users_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Get detailed statistics about all users (admin only).
    """
    try:
        # Statistiche generali sugli utenti
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        inactive_users = total_users - active_users
        
        # Statistiche per ruolo
        role_stats = {}
        for role in ["admin", "student", "parent", "teacher"]:
            count = db.query(User).filter(User.role == role).count()
            active_count = db.query(User).filter(User.role == role, User.is_active == True).count()
            role_stats[role] = {
                "total": count,
                "active": active_count,
                "inactive": count - active_count
            }
        
        # Statistiche sugli studenti
        students_with_most_points = db.query(User).filter(User.role == "student").order_by(desc(User.points)).limit(5).all()
        
        # Statistiche sui tentativi di quiz
        most_active_students_query = (
            db.query(
                User.id,
                User.username,
                User.email,
                User.points,
                func.count(QuizAttempt.id).label('attempts_count')
            )
            .join(QuizAttempt, User.id == QuizAttempt.user_id)
            .filter(User.role == "student")
            .group_by(User.id)
            .order_by(desc('attempts_count'))
            .limit(5)
        )
        
        most_active_students = []
        for student in most_active_students_query.all():
            most_active_students.append({
                "id": student.id,
                "username": student.username,
                "email": student.email,
                "points": student.points or 0,
                "attempts_count": student.attempts_count
            })
        
        # Statistiche sugli studenti con la migliore accuratezza
        best_accuracy_students_query = (
            db.query(
                User.id,
                User.username,
                User.email,
                User.points,
                func.count(QuizAttempt.id).label('total_attempts'),
                func.sum(case((QuizAttempt.correct == True, 1), else_=0)).label('correct_answers')
            )
            .join(QuizAttempt, User.id == QuizAttempt.user_id)
            .filter(User.role == "student")
            .group_by(User.id)
            .having(func.count(QuizAttempt.id) > 0)
            .order_by(desc(func.sum(case((QuizAttempt.correct == True, 1), else_=0)) / func.count(QuizAttempt.id)))
            .limit(5)
        )
        
        best_accuracy_students = []
        for student in best_accuracy_students_query.all():
            accuracy = (student.correct_answers / student.total_attempts * 100) if student.total_attempts > 0 else 0
            best_accuracy_students.append({
                "id": student.id,
                "username": student.username,
                "email": student.email,
                "points": student.points or 0,
                "total_attempts": student.total_attempts,
                "correct_answers": student.correct_answers,
                "accuracy": round(accuracy, 2)
            })
        
        return {
            "general": {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users
            },
            "role_stats": role_stats,
            "top_students": [{
                "id": s.id,
                "username": s.username,
                "email": s.email,
                "points": s.points or 0
            } for s in students_with_most_points],
            "most_active_students": most_active_students,
            "best_accuracy_students": best_accuracy_students
        }
    except Exception as e:
        print(f"Error in get_users_stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting users stats: {str(e)}"
        )

@router.get("/quiz-categories-stats", response_model=dict)
def get_quiz_categories_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Get detailed statistics about quiz categories (admin only).
    """
    try:
        # Statistiche generali sulle categorie
        total_categories = db.query(func.count(distinct(Category.id))).scalar()
        
        # Categorie più popolari (con più quiz)
        popular_categories_query = (
            db.query(
                Category.name,
                func.count(Quiz.id).label('quiz_count')
            )
            .join(quiz_category_association, Category.id == quiz_category_association.c.category_id)
            .join(Quiz, Quiz.id == quiz_category_association.c.quiz_id)
            .group_by(Category.name)
            .order_by(desc('quiz_count'))
            .limit(10)
        )
        
        popular_categories = []
        for category in popular_categories_query.all():
            popular_categories.append({
                "category": category.name,
                "quiz_count": category.quiz_count
            })
        
        # Categorie con più tentativi
        most_attempted_categories_query = (
            db.query(
                Category.name,
                func.count(QuizAttempt.id).label('attempts_count')
            )
            .join(quiz_category_association, Category.id == quiz_category_association.c.category_id)
            .join(Quiz, Quiz.id == quiz_category_association.c.quiz_id)
            .join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)
            .group_by(Category.name)
            .order_by(desc('attempts_count'))
            .limit(10)
        )
        
        most_attempted_categories = []
        for category in most_attempted_categories_query.all():
            most_attempted_categories.append({
                "category": category.name,
                "attempts_count": category.attempts_count
            })
        
        # Categorie con migliore accuratezza
        best_accuracy_categories_query = (
            db.query(
                Category.name,
                func.count(QuizAttempt.id).label('total_attempts'),
                func.sum(case((QuizAttempt.correct == True, 1), else_=0)).label('correct_answers')
            )
            .join(quiz_category_association, Category.id == quiz_category_association.c.category_id)
            .join(Quiz, Quiz.id == quiz_category_association.c.quiz_id)
            .join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)
            .group_by(Category.name)
            .having(func.count(QuizAttempt.id) > 5)  # Almeno 5 tentativi per categoria
            .order_by(desc(func.sum(case((QuizAttempt.correct == True, 1), else_=0)) / func.count(QuizAttempt.id)))
            .limit(10)
        )
        
        best_accuracy_categories = []
        for category in best_accuracy_categories_query.all():
            accuracy = (category.correct_answers / category.total_attempts * 100) if category.total_attempts > 0 else 0
            best_accuracy_categories.append({
                "category": category.name,
                "total_attempts": category.total_attempts,
                "correct_answers": category.correct_answers,
                "accuracy": round(accuracy, 2)
            })
        
        # Categorie per percorso
        categories_by_path_query = (
            db.query(
                Path.name.label('path_name'),
                Category.name.label('category_name'),
                func.count(Quiz.id).label('quiz_count')
            )
            .join(quiz_path_association, Path.id == quiz_path_association.c.path_id)
            .join(Quiz, Quiz.id == quiz_path_association.c.quiz_id)
            .join(quiz_category_association, Quiz.id == quiz_category_association.c.quiz_id)
            .join(Category, Category.id == quiz_category_association.c.category_id)
            .group_by(Path.name, Category.name)
            .order_by(Path.name, desc('quiz_count'))
        )
        
        categories_by_path = {}
        for item in categories_by_path_query.all():
            if item.path_name not in categories_by_path:
                categories_by_path[item.path_name] = []
            
            categories_by_path[item.path_name].append({
                "category": item.category_name,
                "quiz_count": item.quiz_count
            })
        
        return {
            "total_categories": total_categories,
            "popular_categories": popular_categories,
            "most_attempted_categories": most_attempted_categories,
            "best_accuracy_categories": best_accuracy_categories,
            "categories_by_path": categories_by_path
        }
    except Exception as e:
        print(f"Error in get_quiz_categories_stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting quiz categories stats: {str(e)}"
        )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> None:
    """
    Delete a user (admin only).
    """
    # Verifica se l'utente esiste
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Non permettere di eliminare l'utente corrente
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    
    # Elimina l'utente
    db.delete(user)
    db.commit()

@router.patch("/users/{user_id}/toggle-active", response_model=UserResponse)
def toggle_user_active_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Toggle the active status of a user (admin only).
    """
    # Verifica se l'utente esiste
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Non permettere di disattivare l'utente corrente
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )
    
    # Cambia lo stato attivo dell'utente
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/users/{user_id}/quizzes", response_model=dict)
def get_student_quizzes(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Get all quizzes completed by a student (admin only).
    """
    try:
        # Verifica se l'utente esiste
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Verifica che l'utente sia uno studente
        if user.role != "student":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a student",
            )
        
        # Ottieni tutti i tentativi di quiz dell'utente
        quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user.id).all()
        
        # Calcola le statistiche
        total_attempts = len(quiz_attempts)
        correct_answers = sum(1 for attempt in quiz_attempts if attempt.correct)
        total_points = sum(attempt.points_earned or 0 for attempt in quiz_attempts)
        
        # Formatta i tentativi per la risposta
        formatted_attempts = []
        for attempt in quiz_attempts:
            quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
            formatted_attempts.append({
                "id": attempt.id,
                "quiz_id": attempt.quiz_id,
                "quiz_title": quiz.title if quiz else "Unknown Quiz",
                "answer": attempt.answer,
                "correct": attempt.correct,
                "points_earned": attempt.points_earned,
                "created_at": attempt.created_at.isoformat()
            })
        
        # Restituisci la risposta completa
        return {
            "student": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "points": user.points or 0
            },
            "attempts": formatted_attempts,
            "total_attempts": total_attempts,
            "correct_answers": correct_answers,
            "total_points": total_points
        }
    except Exception as e:
        print(f"Error in get_student_quizzes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting student quizzes: {str(e)}"
        )

@router.get("/users/{user_id}/children-progress", response_model=ParentChildrenProgressResponse)
def get_parent_children_progress(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Get the progress of all children of a parent (admin only).
    """
    try:
        # Verifica se l'utente esiste
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Verifica che l'utente sia un genitore
        if user.role != "parent":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a parent",
            )
        
        # Ottieni i figli dell'utente (studenti associati al genitore)
        children_data = []
        for child in user.students:
            # Calcola il numero totale di tentativi
            total_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == child.id).count()
            
            # Calcola il numero di risposte corrette
            correct_answers = db.query(QuizAttempt).filter(
                QuizAttempt.user_id == child.id,
                QuizAttempt.correct == True
            ).count()
            
            # Calcola l'accuratezza
            accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0
            
            # Aggiungi il sommario del progresso dello studente
            children_data.append({
                "id": child.id,
                "username": child.username,
                "points": child.points or 0,
                "total_attempts": total_attempts,
                "correct_answers": correct_answers,
                "accuracy": round(accuracy, 2)
            })
        
        # Restituisci la risposta
        return ParentChildrenProgressResponse(
            parent=user,
            children=children_data,
            total_children=len(children_data)
        )
    except Exception as e:
        print(f"Error in get_parent_children_progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting children progress: {str(e)}"
        )
