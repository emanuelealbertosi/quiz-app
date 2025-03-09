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
from app.models.quiz import Quiz, Category, DifficultyLevel, Path, quiz_path_association
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

from pydantic import BaseModel

class QuizAttemptResponse(BaseModel):
    user_id: int
    quiz_id: int
    answer: str
    correct: bool
    completed: bool = False
    points_earned: int = 0
    current_quiz_points: int = None  # Punteggio attuale del quiz

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
    
    # Recupera l'ultimo tentativo fallito per questo quiz (per tracciare il punteggio attuale)
    last_failed_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.quiz_id == quiz.id,
        QuizAttempt.correct == False
    ).order_by(QuizAttempt.created_at.desc()).first()
    
    # Determina il punteggio attuale del quiz per questo studente
    current_quiz_points = quiz.points
    
    # Se ci sono tentativi falliti precedenti, usa il loro punteggio come base
    if last_failed_attempt:
        # Il punteggio attuale è il punteggio dell'ultimo tentativo fallito
        # (che già riflette i dimezzamenti precedenti)
        print(f"DEBUG - Trovato tentativo fallito precedente con punteggio: {last_failed_attempt.points_earned}")
        if last_failed_attempt.points_earned > 0:  # Usa il punteggio precedente solo se è maggiore di zero
            current_quiz_points = last_failed_attempt.points_earned
    
    # Calcola i punti guadagnati in base alla correttezza della risposta
    if is_correct:
        # Per le risposte corrette, assegna il punteggio attuale
        base_points = current_quiz_points
    else:
        # Per le risposte sbagliate, dimezza il punteggio attuale fino a un minimo di 1
        base_points = max(current_quiz_points // 2, 1)
    
    # Se il quiz è già stato completato con successo, non assegnare punti
    points_earned = 0 if already_completed else base_points
    
    print(f"DEBUG - Risposta corretta: {is_correct}")
    print(f"DEBUG - Punti originali del quiz: {quiz.points}")
    print(f"DEBUG - Punti attuali del quiz per lo studente: {current_quiz_points}")
    print(f"DEBUG - Punti che sarebbero guadagnati: {base_points}")
    print(f"DEBUG - Punti effettivamente assegnati: {points_earned} (azzerati: {already_completed})")
    
    # Create attempt
    from app.models.challenge import QuizAttempt
    
    db_attempt = QuizAttempt(
        user=current_user,
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
    
    # Se la risposta è corretta, segna il quiz come completato nei percorsi associati
    if is_correct:
        # Trova tutti i percorsi che contengono questo quiz e che sono assegnati allo studente
        from app.models.quiz import Path, quiz_path_association
        from app.models.challenge import UserProgress
        from sqlalchemy import and_
        
        # Query per trovare i percorsi che contengono questo quiz
        paths_with_quiz = db.query(Path).join(
            quiz_path_association,
            and_(
                quiz_path_association.c.path_id == Path.id,
                quiz_path_association.c.quiz_id == quiz.id
            )
        ).all()
        
        # Per ogni percorso trovato, verifica se lo studente ha un progresso attivo
        for path in paths_with_quiz:
            user_progress = db.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == current_user.id,
                    UserProgress.path_id == path.id,
                    UserProgress.completed == False
                )
            ).first()
            
            if user_progress:
                # Conta i quiz già completati in questo percorso
                from sqlalchemy import select, func
                
                # Trova tutti i quiz del percorso
                stmt = select([quiz_path_association.c.quiz_id]).where(
                    quiz_path_association.c.path_id == path.id
                )
                quiz_ids_in_path = [row[0] for row in db.execute(stmt)]
                
                # Trova i tentativi completati con successo per questi quiz
                completed_in_path = db.query(func.count(QuizAttempt.id)).filter(
                    and_(
                        QuizAttempt.user_id == current_user.id,
                        QuizAttempt.quiz_id.in_(quiz_ids_in_path),
                        QuizAttempt.completed == True
                    )
                ).scalar()
                
                # Aggiorna il progresso dell'utente
                user_progress.completed_quizzes = completed_in_path
                
                # Verifica se tutti i quiz sono stati completati
                if completed_in_path >= len(quiz_ids_in_path):
                    user_progress.completed = True
                    
                    # Assegna i punti bonus
                    current_user.points += path.bonus_points
                    print(f"Debug - Percorso completato! Bonus: {path.bonus_points} punti")
                
                db.add(user_progress)
        
        # Commit delle modifiche aggiuntive
        db.commit()
        db.refresh(current_user)
    
    # Creiamo una risposta personalizzata che include anche il punteggio attuale del quiz
    response_data = QuizAttemptResponse(
        user_id=db_attempt.user_id,
        quiz_id=db_attempt.quiz_id,
        answer=db_attempt.answer,
        correct=db_attempt.correct,
        completed=db_attempt.completed,
        points_earned=points_earned,
        current_quiz_points=current_quiz_points
    )
    
    return response_data

# Get completed quizzes for user
# Specificare un formato di risposta semplificato per i quiz completati
from pydantic import BaseModel

class CompletedQuizIdResponse(BaseModel):
    quiz_id: int
    current_points: int = None

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
    
    # Creazione di un dizionario per tenere traccia dei punteggi aggiornati per ogni quiz
    quiz_points = {}
    
    # Cerchiamo anche tutti i tentativi falliti per determinare il punteggio attuale di ogni quiz
    all_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id
    ).order_by(QuizAttempt.created_at).all()
    
    print(f"DEBUG - Totale tentativi trovati: {len(all_attempts)}")
    
    for attempt in all_attempts:
        quiz_id = attempt.quiz_id
        print(f"DEBUG - Trovato tentativo: quiz_id={quiz_id}, correct={attempt.correct}")
        
        # Inizializza il punteggio del quiz se non è già presente
        if quiz_id not in quiz_points:
            # Ottieni il punteggio base del quiz
            quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
            if quiz:
                quiz_points[quiz_id] = quiz.points
                print(f"DEBUG - Inizializzato punteggio per quiz_id={quiz_id}: {quiz_points[quiz_id]}")
        
        # Se è un tentativo fallito, dimezza il punteggio fino a un minimo di 1
        if not attempt.correct:
            old_points = quiz_points.get(quiz_id, 0)
            quiz_points[quiz_id] = max(old_points // 2, 1)
            print(f"DEBUG - Risposta sbagliata per quiz_id={quiz_id}: punteggio ridotto da {old_points} a {quiz_points[quiz_id]}")
    
    print(f"DEBUG - Punteggi aggiornati dei quiz: {quiz_points}")
    
    # Costruisci la risposta con gli ID dei quiz completati e i loro punteggi attuali
    response = []
    print(f"DEBUG - Preparazione risposta finale con {len(completed_attempts)} tentativi completati con successo")
    
    for attempt in completed_attempts:
        quiz_id = attempt.quiz_id
        current_points = quiz_points.get(quiz_id, None)
        
        # Assicuriamoci che vengano passati come interi
        quiz_id_int = int(quiz_id) if quiz_id is not None else None
        
        response.append(CompletedQuizIdResponse(
            quiz_id=quiz_id_int,
            current_points=current_points
        ))
        print(f"DEBUG - Quiz completato: quiz_id={quiz_id_int} (tipo: {type(quiz_id_int)}), current_points={current_points}")
    
    print(f"DEBUG - Risposta formattata (DETTAGLIATA): {[{'quiz_id': r.quiz_id, 'current_points': r.current_points} for r in response]}")
    
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
