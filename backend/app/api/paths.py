from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.quiz import Path, quiz_path_association, Quiz, PathQuiz, StudentPath
from app.models.user import User, UserRole, parent_student_association
from app.models.challenge import PathQuizAttempt, UserProgress
from app.schemas.path import (
    PathCreate, PathResponse, PathUpdate, AssignPathRequest, 
    StudentPathResponse
)
from app.schemas.user import UserResponse
from app.core.security import verify_parent_student_relation
from app.schemas.quiz import QuizResponse

router = APIRouter()

@router.post("/", response_model=PathResponse, status_code=status.HTTP_201_CREATED)
def create_path(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_in: PathCreate
):
    """
    Crea un nuovo percorso template.
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
    
    # Crea il percorso template
    db_path = Path(
        name=path_in.name,
        description=path_in.description,
        bonus_points=path_in.bonus_points,
        creator_id=current_user.id
    )
    
    # Prima aggiungi il percorso al database per ottenere l'ID
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    
    # Manteniamo l'associazione nella tabella quiz_path_association come riferimento
    db_path.quizzes = quizzes
    
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

@router.get("/my-paths", response_model=List[StudentPathResponse])
def get_my_paths(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Recupera tutti i percorsi assegnati all'utente corrente.
    Solo gli studenti possono vedere i loro percorsi.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli studenti possono accedere ai percorsi assegnati"
        )
    
    # Ottiene i percorsi assegnati direttamente allo studente
    student_paths = db.query(StudentPath).filter(
        StudentPath.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    # Per ogni percorso, aggiungi il numero totale di quiz e i quiz stessi
    for path in student_paths:
        # Usa il template (riferimento al Path originale) per ottenere il numero totale di quiz
        path.total_quizzes = len(path.template.quizzes) if path.template else 0
        
        # Aggiungi i quiz disponibili nell'attributo quizzes
        quiz_list = []
        if path.template and path.template.quizzes:
            for quiz in path.template.quizzes:
                # Converti l'oggetto ORM Quiz in un dizionario compatibile con QuizResponse
                quiz_dict = {
                    "id": quiz.id,
                    "question": quiz.question,
                    "options": quiz.options,
                    "correct_answer": quiz.correct_answer,
                    "explanation": quiz.explanation,
                    "points": quiz.points,
                    "creator_id": quiz.creator_id,
                    "difficulty_level_id": quiz.difficulty_level_id if hasattr(quiz, "difficulty_level_id") else None,
                    "created_at": quiz.created_at
                }
                quiz_list.append(quiz_dict)
        setattr(path, "quizzes", quiz_list)
    
    return student_paths

@router.get("/my", response_model=List[StudentPathResponse])
def get_my_paths(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ottiene tutti i percorsi assegnati all'utente corrente.
    Se l'utente è un genitore, ottiene i percorsi creati da lui.
    Se l'utente è uno studente, ottiene i percorsi assegnati a lui.
    """
    if current_user.role == UserRole.PARENT:
        # Per i genitori, ritorna i percorsi creati
        paths = db.query(Path).filter(Path.creator_id == current_user.id).all()
        return paths
    elif current_user.role == UserRole.STUDENT:
        # Per gli studenti, ritorna gli StudentPath assegnati
        student_paths = db.query(StudentPath).filter(
            StudentPath.user_id == current_user.id
        ).all()
        
        # Carica i path_quizzes per ogni student_path
        for student_path in student_paths:
            path_quizzes = db.query(PathQuiz).filter(
                PathQuiz.path_id == student_path.template_id
            ).all()
            setattr(student_path, "path_quizzes", path_quizzes)
            
            # Aggiungi anche l'attributo quizzes per compatibilità con il frontend
            setattr(student_path, "quizzes", student_path.template.quizzes if student_path.template else [])
        
        return student_paths
    else:
        # Per gli admin, ritorna tutti i percorsi
        paths = db.query(Path).all()
        return paths

@router.get("/{path_id}", response_model=PathResponse)
def get_path(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_id: int
):
    """
    Ottiene un percorso specifico tramite ID.
    Accessibile a genitori e studenti.
    Se l'utente è uno studente, mostra solo i percorsi a lui assegnati.
    """
    # Diverso comportamento in base al ruolo
    if current_user.role == UserRole.STUDENT:
        # Trova lo StudentPath associato a questo studente e path template
        student_path = db.query(StudentPath).filter(
            StudentPath.template_id == path_id,
            StudentPath.user_id == current_user.id
        ).first()
        
        if not student_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Percorso non trovato o non assegnato a questo studente"
            )
        
        # Carica i path_quizzes specifici per questo percorso
        from app.models.quiz import PathQuiz
        path_quizzes = db.query(PathQuiz).filter(PathQuiz.path_id == student_path.template_id).all()
        setattr(student_path, "path_quizzes", path_quizzes)
        
        # Aggiungi anche l'attributo quizzes per compatibilità con il frontend
        setattr(student_path, "quizzes", student_path.template.quizzes if student_path.template else [])
        
        return student_path
    else:
        # Per i genitori, mostra il template del percorso
        path = db.query(Path).filter(Path.id == path_id).first()
        
        if not path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Percorso non trovato"
            )
        
        # Carica i quiz associati
        from app.models.quiz import Quiz
        path.quizzes = db.query(Quiz).join(
            Path.quizzes
        ).filter(
            Path.id == path_id
        ).all()
        
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
        from app.models.quiz import Quiz, PathQuiz
        # Verifica che i quiz esistano
        quizzes = db.query(Quiz).filter(Quiz.id.in_(path_in.quiz_ids)).all()
        
        if len(quizzes) != len(path_in.quiz_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alcuni quiz specificati non esistono"
            )
        
        # Quando aggiorniamo un Path template, dobbiamo:
        # 1. Aggiornare la relazione many-to-many con i Quiz
        path.quizzes = quizzes
        
        # 2. Trovare e aggiornare tutti gli StudentPath esistenti per questo template
        student_paths = db.query(StudentPath).filter(StudentPath.template_id == path_id).all()
        
        # Per ogni StudentPath, aggiorniamo i suoi PathQuiz
        for student_path in student_paths:
            # Elimina i PathQuiz esistenti per questo StudentPath
            db.query(PathQuiz).filter(PathQuiz.path_id == student_path.template_id).delete()
            
            # Crea nuove copie dei quiz per questo StudentPath
            for i, quiz in enumerate(quizzes):
                path_quiz = PathQuiz(
                    question=quiz.question,
                    options=quiz.options,
                    correct_answer=quiz.correct_answer,
                    explanation=quiz.explanation,
                    points=quiz.points,
                    order=i,  # Imposta l'ordine in base all'indice nella lista
                    original_quiz_id=quiz.id,
                    student_path_id=student_path.id
                )
                db.add(path_quiz)
    
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
    
    # Trova tutti gli StudentPath associati a questo percorso
    student_paths = db.query(StudentPath).filter(StudentPath.template_id == path_id).all()
    
    # Per ogni StudentPath, elimina tutti i PathQuiz associati
    for student_path in student_paths:
        # Trova tutti i PathQuiz per questo StudentPath
        path_quizzes = db.query(PathQuiz).filter(PathQuiz.path_id == path.id).all()
        
        for path_quiz in path_quizzes:
            # Elimina anche i tentativi associati a questi path_quiz
            db.query(PathQuizAttempt).filter(PathQuizAttempt.path_quiz_id == path_quiz.id).delete()
            db.delete(path_quiz)
        
        # Elimina lo StudentPath
        db.delete(student_path)
    
    # Elimina tutti i PathQuiz direttamente associati al percorso template
    path_quizzes = db.query(PathQuiz).filter(PathQuiz.path_id == path_id).all()
    for path_quiz in path_quizzes:
        # Elimina anche i tentativi associati a questi path_quiz
        db.query(PathQuizAttempt).filter(PathQuizAttempt.path_quiz_id == path_quiz.id).delete()
        db.delete(path_quiz)
    
    # Ora possiamo eliminare il percorso
    db.delete(path)
    db.commit()

@router.post("/assign", response_model=dict)
def assign_path_to_student(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    assign_request: AssignPathRequest
):
    """
    Assegna un percorso a uno studente.
    Solo i genitori possono assegnare percorsi ai loro studenti.
    Crea una nuova istanza del percorso specifica per lo studente.
    """
    # Verifica che l'utente sia un genitore
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i genitori possono assegnare percorsi"
        )
    
    # Verifica che il percorso template esista
    path_template = db.query(Path).filter(Path.id == assign_request.path_id).first()
    if not path_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Percorso non trovato"
        )
    
    # Verifica che solo il creatore del percorso possa assegnarlo
    if path_template.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai il permesso di assegnare questo percorso"
        )
    
    # Verifica che lo studente esista ed è figlio del genitore
    student = db.query(User).filter(User.id == assign_request.user_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Studente non trovato"
        )
    
    if student.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'utente non è uno studente"
        )
    
    # Verifica la relazione genitore-figlio
    is_parent = verify_parent_student_relation(db, current_user.id, student.id)
    if not is_parent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non sei un genitore di questo studente"
        )
    
    # Verifica se il percorso è già stato assegnato allo studente
    existing_student_path = db.query(StudentPath).filter(
        StudentPath.user_id == student.id,
        StudentPath.template_id == path_template.id
    ).first()
    
    # Se esiste già un'assegnazione, eliminiamo completamente la vecchia istanza
    if existing_student_path:
        # Il cascade="all, delete-orphan" si occuperà automaticamente di eliminare
        # tutti i PathQuiz e i relativi PathQuizAttempt
        db.delete(existing_student_path)
        db.commit()
        
        # Eliminiamo anche il vecchio record in UserProgress per compatibilità
        old_progress = db.query(UserProgress).filter(
            UserProgress.user_id == student.id,
            UserProgress.path_id == path_template.id
        ).first()
        
        if old_progress:
            db.delete(old_progress)
            db.commit()
    
    # Crea una nuova istanza del percorso per lo studente
    student_path = StudentPath(
        name=path_template.name,
        description=path_template.description,
        bonus_points=path_template.bonus_points,
        template_id=path_template.id,
        user_id=student.id,
        completed=False,
        completed_quizzes=0
    )
    
    db.add(student_path)
    db.commit()
    db.refresh(student_path)
    
    # Crea una copia di ogni quiz per questa istanza del percorso
    for i, quiz in enumerate(path_template.quizzes):
        path_quiz = PathQuiz(
            question=quiz.question,
            options=quiz.options,
            correct_answer=quiz.correct_answer,
            explanation=quiz.explanation,
            points=quiz.points,
            order=i,
            original_quiz_id=quiz.id,
            path_id=path_template.id
        )
        db.add(path_quiz)
    
    db.commit()
    
    # Crea anche un record UserProgress per retrocompatibilità
    # Questo potrà essere rimosso in futuro
    progress = UserProgress(
        user_id=student.id,
        path_id=path_template.id,
        completed=False,
        completed_quizzes=0,
        completed_quiz_ids=[]
    )
    
    db.add(progress)
    db.commit()
    
    return {
        "message": f"Percorso '{path_template.name}' assegnato con successo allo studente {student.email}"
    }

@router.post("/unassign", status_code=status.HTTP_200_OK)
def unassign_path_from_student(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    assign_request: AssignPathRequest
):
    """
    Disassegna un percorso da uno studente.
    Solo i genitori possono disassegnare percorsi dai loro studenti.
    """
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i genitori possono disassegnare percorsi"
        )
    
    # Verifica che il percorso esista
    path = db.query(Path).filter(Path.id == assign_request.path_id).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Percorso non trovato"
        )
    
    if path.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai il permesso di disassegnare questo percorso"
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
    
    # Verifica che esista un progresso per questo percorso e questo studente
    existing_progress = db.query(UserProgress).filter(
        UserProgress.user_id == student.id,
        UserProgress.path_id == path.id
    ).first()
    
    if not existing_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questo percorso non è assegnato allo studente specificato"
        )
    
    # Elimina il progresso esistente
    db.delete(existing_progress)
    db.commit()
    
    return {"message": f"Percorso '{path.name}' disassegnato con successo dallo studente {student.email}"}

@router.get("/student/{path_id}/completed-quizzes", response_model=List[int])
def get_completed_quizzes_in_path(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    path_id: int
):
    """
    Ottiene gli ID dei quiz completati da uno studente all'interno di un percorso specifico.
    """
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
    
    # Verifica se il progresso ha un campo per i quiz completati
    if not hasattr(progress, "completed_quiz_ids") or progress.completed_quiz_ids is None:
        # Se non esiste il campo, restituisce un array vuoto
        print(f"Campo completed_quiz_ids non trovato per l'utente {current_user.id} nel percorso {path_id}")
        return []

    # Restituisce la lista degli ID dei quiz completati in questo percorso
    try:
        quiz_ids = progress.completed_quiz_ids if progress.completed_quiz_ids else []
        print(f"Quiz completati trovati per l'utente {current_user.id} nel percorso {path_id}: {quiz_ids}")
        return quiz_ids
    except Exception as e:
        print(f"Errore durante l'accesso a completed_quiz_ids: {str(e)}")
        return []

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
            
            # Carica i path_quizzes specifici per questo percorso
            from app.models.quiz import PathQuiz
            path_quizzes = db.query(PathQuiz).filter(PathQuiz.path_id == path.id).all()
            setattr(path, "path_quizzes", path_quizzes)
            setattr(path, "total_quizzes", len(path_quizzes) if path_quizzes else len(path.quizzes))
            setattr(path, "quizzes", path.quizzes)
    
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
    
    # Trova lo StudentPath
    student_path = db.query(StudentPath).filter(
        StudentPath.template_id == path_id,
        StudentPath.user_id == current_user.id
    ).first()
    
    if not student_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Percorso non trovato o non assegnato a questo studente"
        )
    
    # Verifica che il quiz faccia parte del percorso come PathQuiz
    from app.models.quiz import PathQuiz
    path_quiz = db.query(PathQuiz).filter(
        PathQuiz.path_id == student_path.template_id,
        PathQuiz.original_quiz_id == quiz_id
    ).first()
    
    if not path_quiz:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il quiz non fa parte di questo percorso"
        )
    
    # Crea un tentativo di PathQuiz se non esiste
    from app.models.challenge import PathQuizAttempt
    existing_attempt = db.query(PathQuizAttempt).filter(
        PathQuizAttempt.path_quiz_id == path_quiz.id,
        PathQuizAttempt.user_id == current_user.id
    ).first()
    
    if not existing_attempt:
        # Crea un nuovo tentativo e segna il quiz come completato
        attempt = PathQuizAttempt(
            path_quiz_id=path_quiz.id,
            user_id=current_user.id,
            answer="",  # Questo è un segnaposto, non è importante per questo endpoint
            correct=True,  # Lo consideriamo corretto per il completamento manuale
            points_earned=path_quiz.points,
            completed=True
        )
        db.add(attempt)
    else:
        # Aggiorna il tentativo esistente
        existing_attempt.completed = True
        existing_attempt.correct = True
        existing_attempt.points_earned = path_quiz.points
    
    # Aggiorna il conteggio dei quiz completati nello StudentPath
    completed_count = db.query(PathQuizAttempt).join(
        PathQuiz, PathQuiz.id == PathQuizAttempt.path_quiz_id
    ).filter(
        PathQuiz.path_id == student_path.template_id,
        PathQuizAttempt.user_id == current_user.id,
        PathQuizAttempt.completed == True
    ).count()
    
    student_path.completed_quizzes = completed_count
    
    # Verifica se tutti i quiz sono stati completati
    # Ottieni il numero totale di quiz nel percorso dai PathQuizzes
    total_quizzes = db.query(PathQuiz).filter(PathQuiz.path_id == student_path.template_id).count()
    
    # Controlla se tutti i quiz sono stati completati
    if student_path.completed_quizzes >= total_quizzes:
        student_path.completed = True
        
        # Assegna i punti bonus allo studente
        path = db.query(Path).filter(Path.id == path_id).first()
        if path and path.bonus_points > 0:
            student = db.query(User).filter(User.id == current_user.id).first()
            student.points += path.bonus_points
    
    db.commit()
    
    return {"success": True, "message": "Quiz segnato come completato nel percorso"}

@router.get("/student", response_model=List[StudentPathResponse])
def get_student_paths(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    student_id: int
):
    """
    Ottiene tutti i percorsi assegnati a uno studente specifico.
    Accessibile solo ai genitori dello studente.
    """
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i genitori possono visualizzare i percorsi assegnati a uno studente"
        )
    
    # Verifica che lo studente sia figlio del genitore corrente
    student_user = db.query(User).filter(User.id == student_id).first()
    if not student_user or student_user not in current_user.students:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai il permesso di visualizzare i percorsi di questo studente"
        )
    
    # Ottieni tutti gli StudentPath dello studente
    student_paths = db.query(StudentPath).filter(
        StudentPath.user_id == student_id
    ).all()
    
    # Carica i path_quizzes per ogni student_path
    for student_path in student_paths:
        path_quizzes = db.query(PathQuiz).filter(
            PathQuiz.path_id == student_path.template_id
        ).all()
        setattr(student_path, "path_quizzes", path_quizzes)
        
        # Aggiungi i quiz disponibili nell'attributo quizzes
        quiz_list = []
        if student_path.template and student_path.template.quizzes:
            for quiz in student_path.template.quizzes:
                # Converti l'oggetto ORM Quiz in un dizionario compatibile con QuizResponse
                quiz_dict = {
                    "id": quiz.id,
                    "question": quiz.question,
                    "options": quiz.options,
                    "correct_answer": quiz.correct_answer,
                    "explanation": quiz.explanation,
                    "points": quiz.points,
                    "creator_id": quiz.creator_id,
                    "difficulty_level_id": quiz.difficulty_level_id if hasattr(quiz, "difficulty_level_id") else None,
                    "created_at": quiz.created_at
                }
                quiz_list.append(quiz_dict)
        setattr(student_path, "quizzes", quiz_list)
    
    return student_paths

@router.post("/migrate-to-student-paths", response_model=dict)
def migrate_to_student_paths(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Migra i percorsi esistenti al nuovo modello di StudentPath.
    Questa API dovrebbe essere chiamata una sola volta durante la migrazione.
    Solo gli admin possono eseguire questa operazione.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli admin possono eseguire questa operazione"
        )
    
    # Trova tutti i UserProgress esistenti
    progress_items = db.query(UserProgress).all()
    
    # Contatori per statistiche
    created_count = 0
    skipped_count = 0
    
    for progress in progress_items:
        # Verifica se esiste già un StudentPath per questa combinazione
        existing = db.query(StudentPath).filter(
            StudentPath.user_id == progress.user_id,
            StudentPath.template_id == progress.path_id
        ).first()
        
        if existing:
            skipped_count += 1
            continue
        
        # Ottieni il percorso template
        path_template = db.query(Path).filter(Path.id == progress.path_id).first()
        if not path_template:
            continue
        
        # Crea un nuovo StudentPath
        student_path = StudentPath(
            name=path_template.name,
            description=path_template.description,
            bonus_points=path_template.bonus_points,
            template_id=path_template.id,
            user_id=progress.user_id,
            completed=progress.completed,
            completed_quizzes=progress.completed_quizzes
        )
        
        db.add(student_path)
        db.commit()
        db.refresh(student_path)
        
        # Crea una copia di ogni quiz per questa istanza del percorso
        for i, quiz in enumerate(path_template.quizzes):
            path_quiz = PathQuiz(
                question=quiz.question,
                options=quiz.options,
                correct_answer=quiz.correct_answer,
                explanation=quiz.explanation,
                points=quiz.points,
                order=i,
                original_quiz_id=quiz.id,
                student_path_id=student_path.id
            )
            db.add(path_quiz)
        
        created_count += 1
    
    db.commit()
    
    return {
        "message": f"Migrazione completata. Creati {created_count} nuovi StudentPath, saltati {skipped_count} già esistenti."
    }
