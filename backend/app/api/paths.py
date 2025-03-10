from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.quiz import Path, quiz_path_association, Quiz, PathQuiz
from app.models.user import User, UserRole, parent_student_association
from app.models.challenge import PathQuizAttempt, UserProgress
from app.schemas.path import PathCreate, PathResponse, PathUpdate, AssignPathRequest
from app.schemas.user import UserResponse
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
    
    # Prima aggiungi il percorso al database per ottenere l'ID
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    
    # Crea una copia di ogni quiz associata al percorso
    for i, quiz in enumerate(quizzes):
        path_quiz = PathQuiz(
            question=quiz.question,
            options=quiz.options,
            correct_answer=quiz.correct_answer,
            explanation=quiz.explanation,
            points=quiz.points,
            order=i,  # Imposta l'ordine in base all'indice nella lista
            original_quiz_id=quiz.id,
            path_id=db_path.id
        )
        db.add(path_quiz)
    
    # Manteniamo anche l'associazione nella tabella quiz_path_association per compatibilità
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
    print(f"Richiesta percorsi per l'utente {current_user.id} (ruolo: {current_user.role})")
    
    if current_user.role != UserRole.STUDENT:
        print(f"L'utente {current_user.id} non è uno studente. Ruolo: {current_user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo gli studenti possono visualizzare i propri percorsi"
        )
    
    # Recupera i progressi dell'utente
    user_progress_list = db.query(UserProgress).filter(UserProgress.user_id == current_user.id).all()
    print(f"Progressi trovati per l'utente {current_user.id}: {len(user_progress_list)}")
    
    # Recupera i percorsi corrispondenti
    path_ids = [progress.path_id for progress in user_progress_list]
    print(f"ID dei percorsi trovati: {path_ids}")
    
    paths = db.query(Path).filter(Path.id.in_(path_ids)).all() if path_ids else []
    print(f"Percorsi trovati: {len(paths)}")
    
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
    
    # Carica i path_quizzes specifici per questo percorso
    from app.models.quiz import PathQuiz
    path_quizzes = db.query(PathQuiz).filter(PathQuiz.path_id == path_id).all()
    setattr(path, "path_quizzes", path_quizzes)
    
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
        
        # Elimina i PathQuiz esistenti per questo percorso
        db.query(PathQuiz).filter(PathQuiz.path_id == path_id).delete()
        
        # Crea nuove copie dei quiz per questo percorso
        for i, quiz in enumerate(quizzes):
            path_quiz = PathQuiz(
                question=quiz.question,
                options=quiz.options,
                correct_answer=quiz.correct_answer,
                explanation=quiz.explanation,
                points=quiz.points,
                order=i,  # Imposta l'ordine in base all'indice nella lista
                original_quiz_id=quiz.id,
                path_id=path.id
            )
            db.add(path_quiz)
        
        # Aggiorna la relazione quizzes per compatibilità con codice esistente
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
    
    # Elimina prima tutti i progressi degli utenti associati a questo percorso
    user_progress_list = db.query(UserProgress).filter(UserProgress.path_id == path_id).all()
    for progress in user_progress_list:
        db.delete(progress)
    
    # Elimina tutti i path_quizzes associati a questo percorso
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
    """
    # Verifica che l'utente sia un genitore
    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo i genitori possono assegnare percorsi"
        )
    
    # Verifica che il percorso esista
    path = db.query(Path).filter(Path.id == assign_request.path_id).first()
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Percorso non trovato"
        )
    
    # Verifica che solo il creatore del percorso possa assegnarlo
    if path.creator_id != current_user.id:
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
    existing_assignment = db.query(UserProgress).filter(
        UserProgress.user_id == student.id,
        UserProgress.path_id == path.id
    ).first()
    
    # Se esiste già un'assegnazione, ricrea i quiz specifici per questo percorso
    if existing_assignment:
        # Prima elimina il progresso esistente
        db.delete(existing_assignment)
        db.commit()
        
        # Poi elimina i PathQuizAttempt esistenti per i quiz di questo percorso
        from app.models.challenge import PathQuizAttempt
        from app.models.quiz import PathQuiz
        
        # Ottieni prima i PathQuiz per il percorso
        path_quizzes = db.query(PathQuiz).filter(PathQuiz.path_id == path.id).all()
        path_quiz_ids = [pq.id for pq in path_quizzes]
        
        # Elimina tutti i PathQuizAttempt relativi a questi path_quiz_ids
        if path_quiz_ids:
            attempts_to_delete = db.query(PathQuizAttempt).filter(
                PathQuizAttempt.path_quiz_id.in_(path_quiz_ids),
                PathQuizAttempt.user_id == student.id
            ).all()
            
            for attempt in attempts_to_delete:
                db.delete(attempt)
            db.commit()
        
        # Poi elimina i PathQuiz esistenti per questo percorso
        for path_quiz in path_quizzes:
            db.delete(path_quiz)
        db.commit()
        
        # Ricrea i PathQuiz basati sui quiz originali
        for i, quiz in enumerate(path.quizzes):
            path_quiz = PathQuiz(
                question=quiz.question,
                options=quiz.options,
                correct_answer=quiz.correct_answer,
                explanation=quiz.explanation,
                points=quiz.points,
                order=i,
                original_quiz_id=quiz.id,
                path_id=path.id
            )
            db.add(path_quiz)
        db.commit()
    
    # Crea o aggiorna l'assegnazione del percorso
    progress = UserProgress(
        user_id=student.id,
        path_id=path.id,
        completed=False,
        completed_quizzes=0,
        completed_quiz_ids=[]
    )
    
    db.add(progress)
    db.commit()
    
    return {
        "message": f"Percorso '{path.name}' assegnato con successo allo studente {student.email}"
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
    
    # Verifica che il quiz faccia parte del percorso come PathQuiz
    from app.models.quiz import PathQuiz
    path_quiz = db.query(PathQuiz).filter(
        PathQuiz.path_id == path_id,
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
        # Crea un nuovo tentativo completato
        path_quiz_attempt = PathQuizAttempt(
            user_id=current_user.id,
            path_quiz_id=path_quiz.id,
            answer="",  # Non memorizziamo la risposta specifica qui
            is_correct=True,  # Assumiamo che sia corretto perché l'endpoint viene chiamato dopo il completamento
            completed=True
        )
        db.add(path_quiz_attempt)
        db.commit()
    elif not existing_attempt.completed:
        # Aggiorna il tentativo esistente come completato
        existing_attempt.completed = True
        db.commit()
    
    # Aggiorna il progresso dell'utente
    if user_progress:
        # Conta i quiz completati in PathQuizAttempt
        completed_count = db.query(PathQuizAttempt).join(
            PathQuiz, PathQuiz.id == PathQuizAttempt.path_quiz_id
        ).filter(
            PathQuiz.path_id == path_id,
            PathQuizAttempt.user_id == current_user.id,
            PathQuizAttempt.completed == True
        ).count()
        
        user_progress.completed_quizzes = completed_count
    
    # Verifica se tutti i quiz sono stati completati
    # Ottieni il numero totale di quiz nel percorso dai PathQuizzes
    total_quizzes = db.query(PathQuiz).filter(PathQuiz.path_id == path_id).count()
    
    # Controlla se tutti i quiz sono stati completati
    if user_progress.completed_quizzes >= total_quizzes:
        user_progress.completed = True
        
        # Assegna i punti bonus allo studente
        path = db.query(Path).filter(Path.id == path_id).first()
        if path and path.bonus_points > 0:
            student = db.query(User).filter(User.id == current_user.id).first()
            if student:
                student.points = (student.points or 0) + path.bonus_points
                db.commit()
    
    db.commit()
    
    return {"success": True, "message": "Quiz segnato come completato nel percorso"}
