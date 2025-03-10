"""
API per la gestione dei quiz nei percorsi.
Questi endpoint gestiscono la creazione, visualizzazione e completamento
di quiz specifici all'interno dei percorsi di apprendimento.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.quiz import Path, Quiz, PathQuiz
from app.models.challenge import PathQuizAttempt, UserProgress
from app.schemas.quiz import QuizResponse
from app.schemas.path_quiz import PathQuizCreate, PathQuizResponse, PathQuizAttemptCreate, PathQuizAttemptResponse

router = APIRouter()

@router.post("/create", response_model=PathQuizResponse)
def create_path_quiz(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_quiz_in: PathQuizCreate
):
    """
    Crea una copia di un quiz all'interno di un percorso.
    Solo il creatore del percorso può aggiungere quiz.
    """
    # Verifica che l'utente sia un genitore
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i genitori possono aggiungere quiz ai percorsi"
        )
    
    # Verifica che il percorso esista
    path = db.query(Path).filter(Path.id == path_quiz_in.path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Percorso con ID {path_quiz_in.path_id} non trovato"
        )
    
    # Verifica che l'utente sia il creatore del percorso
    if path.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai il permesso di modificare questo percorso"
        )
        
    # Verifica che il quiz originale esista
    original_quiz = db.query(Quiz).filter(Quiz.id == path_quiz_in.original_quiz_id).first()
    if not original_quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz originale con ID {path_quiz_in.original_quiz_id} non trovato"
        )
    
    # Crea la copia del quiz nel percorso
    path_quiz = PathQuiz(
        question=original_quiz.question,
        options=original_quiz.options,
        correct_answer=original_quiz.correct_answer,
        explanation=original_quiz.explanation,
        points=original_quiz.points,
        order=path_quiz_in.order,
        original_quiz_id=original_quiz.id,
        path_id=path.id
    )
    
    db.add(path_quiz)
    db.commit()
    db.refresh(path_quiz)
    
    return path_quiz

@router.get("/path/{path_id}", response_model=List[PathQuizResponse])
def get_path_quizzes(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_id: int
):
    """
    Recupera tutti i quiz di un percorso specifico.
    Gli studenti possono vedere solo i quiz dei percorsi a loro assegnati.
    I genitori possono vedere i quiz dei percorsi che hanno creato.
    """
    # Verifica che il percorso esista
    path = db.query(Path).filter(Path.id == path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Percorso con ID {path_id} non trovato"
        )
    
    # Controlla i permessi
    if current_user.role == UserRole.STUDENT:
        # Verifica che il percorso sia assegnato allo studente
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.path_id == path_id
        ).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non hai accesso a questo percorso"
            )
    elif current_user.role == UserRole.PARENT:
        # Verifica che il genitore sia il creatore del percorso
        if path.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non hai accesso a questo percorso"
            )
    else:
        # Per gli admin, nessuna restrizione
        pass
    
    # Recupera tutti i quiz del percorso, ordinati per posizione
    path_quizzes = db.query(PathQuiz).filter(
        PathQuiz.path_id == path_id
    ).order_by(PathQuiz.order).all()
    
    return path_quizzes

@router.get("/{path_quiz_id}", response_model=PathQuizResponse)
def get_path_quiz(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_quiz_id: int
):
    """
    Recupera un quiz specifico di un percorso.
    """
    # Recupera il quiz del percorso
    path_quiz = db.query(PathQuiz).filter(PathQuiz.id == path_quiz_id).first()
    if not path_quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz con ID {path_quiz_id} non trovato nel percorso"
        )
    
    # Recupera il percorso per controllare i permessi
    path = db.query(Path).filter(Path.id == path_quiz.path_id).first()
    
    # Controlla i permessi
    if current_user.role == UserRole.STUDENT:
        # Verifica che il percorso sia assegnato allo studente
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.path_id == path.id
        ).first()
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non hai accesso a questo quiz"
            )
    elif current_user.role == UserRole.PARENT:
        # Verifica che il genitore sia il creatore del percorso
        if path.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non hai accesso a questo quiz"
            )
    
    return path_quiz

@router.post("/attempt", response_model=PathQuizAttemptResponse)
def create_path_quiz_attempt(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    attempt_in: PathQuizAttemptCreate
):
    """
    Registra un tentativo di rispondere a un quiz all'interno di un percorso.
    """
    # Verifica che l'utente sia uno studente
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli studenti possono completare i quiz"
        )
    
    # Recupera il quiz del percorso
    path_quiz = db.query(PathQuiz).filter(PathQuiz.id == attempt_in.path_quiz_id).first()
    if not path_quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz con ID {attempt_in.path_quiz_id} non trovato nel percorso"
        )
    
    # Verifica che il percorso sia assegnato allo studente
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.path_id == path_quiz.path_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai accesso a questo percorso"
        )
    
    # Verifica se la risposta è corretta
    is_correct = attempt_in.answer == path_quiz.correct_answer
    
    # Calcola i punti guadagnati
    points_earned = path_quiz.points if is_correct else 0
    
    # Crea il nuovo tentativo
    db_attempt = PathQuizAttempt(
        answer=attempt_in.answer,
        correct=is_correct,
        points_earned=points_earned,
        completed=is_correct,
        user_id=current_user.id,
        path_quiz_id=path_quiz.id
    )
    
    db.add(db_attempt)
    
    # Se la risposta è corretta, aggiorna i progressi dell'utente
    if is_correct:
        # Aggiorna i punti dell'utente
        current_user.points += points_earned
        
        # Aggiorna il conteggio dei quiz completati nel percorso
        progress.completed_quizzes += 1
        
        # Verifica se tutti i quiz del percorso sono stati completati
        total_quizzes = db.query(PathQuiz).filter(PathQuiz.path_id == path_quiz.path_id).count()
        
        # Ottieni tutti i tentativi corretti per questo utente in questo percorso
        completed_quizzes = db.query(PathQuizAttempt).join(
            PathQuiz, PathQuiz.id == PathQuizAttempt.path_quiz_id
        ).filter(
            PathQuizAttempt.user_id == current_user.id,
            PathQuiz.path_id == path_quiz.path_id,
            PathQuizAttempt.completed == True
        ).distinct(PathQuiz.id).count()
        
        # Aggiorna il progresso dell'utente
        progress.completed_quizzes = completed_quizzes
        
        # Se tutti i quiz sono stati completati, segna il percorso come completato
        if completed_quizzes >= total_quizzes:
            progress.completed = True
            
            # Assegna i punti bonus
            current_user.points += path_quiz.path.bonus_points
            print(f"Percorso completato! Bonus: {path_quiz.path.bonus_points} punti")
        
        db.add(progress)
    
    db.commit()
    db.refresh(db_attempt)
    db.refresh(current_user)
    
    # Prepara la risposta
    response = PathQuizAttemptResponse(
        id=db_attempt.id,
        path_quiz_id=db_attempt.path_quiz_id,
        user_id=db_attempt.user_id,
        answer=db_attempt.answer,
        correct=db_attempt.correct,
        points_earned=db_attempt.points_earned,
        completed=db_attempt.completed,
        created_at=db_attempt.created_at,
        updated_at=db_attempt.updated_at,
        user_points=current_user.points,
        explanation=path_quiz.explanation if is_correct or attempt_in.show_explanation else None
    )
    
    return response

@router.get("/completed/{path_id}", response_model=List[int])
def get_completed_path_quizzes(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_id: int
):
    """
    Ottiene gli ID dei quiz completati da uno studente all'interno di un percorso specifico.
    """
    # Verifica che l'utente sia uno studente
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli studenti possono vedere i quiz completati"
        )
    
    # Verifica che il percorso esista
    path = db.query(Path).filter(Path.id == path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Percorso con ID {path_id} non trovato"
        )
    
    # Verifica che il percorso sia assegnato allo studente
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.path_id == path_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Percorso con ID {path_id} non assegnato a questo studente"
        )
    
    # Ottieni gli ID dei quiz completati in questo percorso
    completed_quiz_ids = db.query(PathQuiz.id).join(
        PathQuizAttempt, PathQuiz.id == PathQuizAttempt.path_quiz_id
    ).filter(
        PathQuiz.path_id == path_id,
        PathQuizAttempt.user_id == current_user.id,
        PathQuizAttempt.completed == True
    ).distinct().all()
    
    # Estrai gli ID dalla lista di tuple
    return [quiz_id[0] for quiz_id in completed_quiz_ids]
