from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.quiz import Path, quiz_path_association
from app.models.user import User, UserRole, parent_student_association
from app.models.challenge import UserProgress
from app.schemas.path import PathCreate, PathResponse, PathUpdate, AssignPathRequest
from app.core.security import verify_parent_student_relation

router = APIRouter()

@router.post("/", response_model=PathResponse, status_code=status.HTTP_201_CREATED)
def create_path(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_in: PathCreate
):
    """
    Crea un nuovo percorso.
    Solo i genitori possono creare percorsi.
    """
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i genitori possono creare percorsi"
        )
    
    # Verifica che i quiz esistano
    from app.models.quiz import Quiz
    quiz_ids = path_in.quiz_ids
    quizzes = db.query(Quiz).filter(Quiz.id.in_(quiz_ids)).all()
    
    if len(quizzes) != len(quiz_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alcuni quiz specificati non esistono"
        )
    
    # Crea il percorso
    db_path = Path(
        name=path_in.name,
        description=path_in.description,
        bonus_points=path_in.bonus_points,
        creator_id=current_user.id
    )
    
    # Aggiungi i quiz al percorso
    db_path.quizzes = quizzes
    
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    
    return db_path

@router.get("/", response_model=List[PathResponse])
def get_paths(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Recupera tutti i percorsi creati dall'utente corrente.
    Solo i genitori possono vedere i loro percorsi.
    """
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i genitori possono accedere ai percorsi"
        )
    
    paths = db.query(Path).filter(Path.creator_id == current_user.id).offset(skip).limit(limit).all()
    return paths

@router.get("/my-paths", response_model=List[PathResponse])
def get_my_paths(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera tutti i percorsi assegnati all'utente corrente.
    Solo gli studenti possono vedere i propri percorsi.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli studenti possono visualizzare i propri percorsi"
        )
    
    # Recupera i progressi dell'utente
    user_progress_list = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).all()
    
    # Recupera i percorsi corrispondenti
    path_ids = [progress.path_id for progress in user_progress_list]
    paths = db.query(Path).filter(Path.id.in_(path_ids)).all()
    
    # Aggiungi informazioni sul completamento
    for path in paths:
        progress = next((p for p in user_progress_list if p.path_id == path.id), None)
        if progress:
            setattr(path, "completed", progress.completed)
            setattr(path, "completed_quizzes", progress.completed_quizzes)
            setattr(path, "total_quizzes", len(path.quizzes))
    
    return paths

@router.get("/{path_id}", response_model=PathResponse)
def get_path(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_id: int
):
    """
    Recupera un percorso specifico per ID.
    I genitori possono vedere solo i percorsi che hanno creato.
    """
    path = db.query(Path).filter(Path.id == path_id).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Percorso non trovato"
        )
    
    if current_user.role == UserRole.PARENT and path.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai il permesso di accedere a questo percorso"
        )
    
    return path

@router.put("/{path_id}", response_model=PathResponse)
def update_path(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_id: int,
    path_in: PathUpdate
):
    """
    Aggiorna un percorso esistente.
    Solo il genitore che ha creato il percorso può modificarlo.
    """
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i genitori possono modificare i percorsi"
        )
    
    path = db.query(Path).filter(Path.id == path_id).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Percorso non trovato"
        )
    
    if path.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai il permesso di modificare questo percorso"
        )
    
    # Aggiorna i campi base
    if path_in.name is not None:
        path.name = path_in.name
    if path_in.description is not None:
        path.description = path_in.description
    if path_in.bonus_points is not None:
        path.bonus_points = path_in.bonus_points
    
    # Aggiorna i quiz se specificati
    if path_in.quiz_ids is not None:
        from app.models.quiz import Quiz
        # Verifica che i quiz esistano
        quizzes = db.query(Quiz).filter(Quiz.id.in_(path_in.quiz_ids)).all()
        
        if len(quizzes) != len(path_in.quiz_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alcuni quiz specificati non esistono"
            )
        
        # Aggiorna i quiz del percorso
        path.quizzes = quizzes
    
    db.commit()
    db.refresh(path)
    
    return path

@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_path(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_id: int
):
    """
    Elimina un percorso.
    Solo il genitore che ha creato il percorso può eliminarlo.
    """
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i genitori possono eliminare i percorsi"
        )
    
    path = db.query(Path).filter(Path.id == path_id).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Percorso non trovato"
        )
    
    if path.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai il permesso di eliminare questo percorso"
        )
    
    # Controlla se ci sono progressi utente associati a questo percorso
    progress_exists = db.query(UserProgress).filter(UserProgress.path_id == path_id).first()
    
    if progress_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossibile eliminare il percorso: ci sono studenti che lo stanno utilizzando"
        )
    
    db.delete(path)
    db.commit()

@router.post("/assign", status_code=status.HTTP_201_CREATED)
def assign_path_to_student(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    assign_request: AssignPathRequest
):
    """
    Assegna un percorso a uno studente.
    Solo i genitori possono assegnare percorsi ai loro studenti.
    """
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i genitori possono assegnare percorsi"
        )
    
    # Verifica che il percorso esista ed è assegnato al genitore
    path = db.query(Path).filter(Path.id == assign_request.path_id).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Percorso non trovato"
        )
    
    if path.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai il permesso di assegnare questo percorso"
        )
    
    # Verifica che lo studente esista e sia associato al genitore
    student = db.query(User).filter(User.id == assign_request.user_id).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Studente non trovato"
        )
    
    # Verifica che lo studente sia associato al genitore
    if not verify_parent_student_relation(db, current_user.id, student.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non sei il genitore di questo studente"
        )
    
    # Verifica che lo studente non abbia già un percorso attivo non completato
    existing_progress = db.query(UserProgress).filter(
        UserProgress.user_id == student.id,
        UserProgress.path_id == path.id
    ).first()
    
    if existing_progress:
        # Se il percorso non è stato completato, non può essere riassegnato
        if not existing_progress.completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lo studente ha già questo percorso assegnato ma non l'ha ancora completato"
            )
    
    # Crea un nuovo progresso utente
    user_progress = UserProgress(
        user_id=student.id,
        path_id=path.id,
        completed=False,
        completed_quizzes=0
    )
    
    db.add(user_progress)
    db.commit()
    
    return {"message": f"Percorso '{path.name}' assegnato con successo allo studente {student.email}"}

@router.get("/assigned/{student_id}", response_model=List[PathResponse])
def get_student_paths(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    student_id: int
):
    """
    Recupera tutti i percorsi assegnati a uno studente.
    I genitori possono vedere solo i percorsi assegnati ai loro studenti.
    Gli studenti possono vedere solo i percorsi assegnati a loro.
    """
    if current_user.role == UserRole.STUDENT:
        # Lo studente può vedere solo i suoi percorsi
        if current_user.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non hai il permesso di visualizzare i percorsi di altri studenti"
            )
    elif current_user.role == UserRole.PARENT:
        # Il genitore può vedere solo i percorsi dei suoi studenti
        if not verify_parent_student_relation(db, current_user.id, student_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non sei il genitore di questo studente"
            )
    else:
        # Gli altri ruoli non possono accedere a questa funzionalità
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai il permesso di visualizzare i percorsi"
        )
    
    # Recupera i progressi dell'utente
    user_progress_list = db.query(UserProgress).filter(UserProgress.user_id == student_id).all()
    
    # Recupera i percorsi corrispondenti
    path_ids = [progress.path_id for progress in user_progress_list]
    paths = db.query(Path).filter(Path.id.in_(path_ids)).all()
    
    # Aggiungi informazioni sul completamento
    for path in paths:
        progress = next((p for p in user_progress_list if p.path_id == path.id), None)
        if progress:
            setattr(path, "completed", progress.completed)
            setattr(path, "completed_quizzes", progress.completed_quizzes)
            setattr(path, "total_quizzes", len(path.quizzes))
    
    return paths

@router.post("/complete-quiz/{path_id}/{quiz_id}", status_code=status.HTTP_200_OK)
def mark_quiz_completed_in_path(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_id: int,
    quiz_id: int
):
    """
    Segna un quiz come completato all'interno di un percorso.
    Questo endpoint viene chiamato automaticamente quando uno studente completa un quiz.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli studenti possono completare quiz in un percorso"
        )
    
    # Verifica che il percorso esista ed è assegnato allo studente
    user_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.path_id == path_id
    ).first()
    
    if not user_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Percorso non trovato o non assegnato"
        )
    
    if user_progress.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Questo percorso è già stato completato"
        )
    
    # Verifica che il quiz faccia parte del percorso
    path = db.query(Path).filter(Path.id == path_id).first()
    quiz_in_path = False
    
    for quiz in path.quizzes:
        if quiz.id == quiz_id:
            quiz_in_path = True
            break
    
    if not quiz_in_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il quiz non fa parte di questo percorso"
        )
    
    # Incrementa il contatore dei quiz completati
    user_progress.completed_quizzes += 1
    
    # Verifica se tutti i quiz sono stati completati
    if user_progress.completed_quizzes >= len(path.quizzes):
        user_progress.completed = True
        
        # Assegna i punti bonus all'utente
        current_user.points += path.bonus_points
        
        # Salva le modifiche
        db.commit()
        
        return {
            "message": f"Percorso '{path.name}' completato con successo!",
            "bonus_points": path.bonus_points,
            "path_completed": True
        }
    
    # Salva le modifiche
    db.commit()
    
    return {
        "message": f"Quiz completato per il percorso '{path.name}'",
        "completed_quizzes": user_progress.completed_quizzes,
        "total_quizzes": len(path.quizzes),
        "path_completed": False
    }
