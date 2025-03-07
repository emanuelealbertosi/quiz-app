from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.quiz import Quiz, Category, DifficultyLevel
from app.models.user import User
from app.core.security import get_current_active_user, check_admin_privileges

router = APIRouter()

@router.post("/create-sample-quizzes", status_code=status.HTTP_201_CREATED)
def create_sample_quizzes(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_privileges),
) -> Any:
    """
    Create sample quizzes for testing (admin only).
    """
    # Create difficulty levels if they don't exist
    easy = db.query(DifficultyLevel).filter(DifficultyLevel.name == "Facile").first()
    if not easy:
        easy = DifficultyLevel(name="Facile", value=1)
        db.add(easy)
        db.commit()
        db.refresh(easy)
    
    medium = db.query(DifficultyLevel).filter(DifficultyLevel.name == "Medio").first()
    if not medium:
        medium = DifficultyLevel(name="Medio", value=2)
        db.add(medium)
        db.commit()
        db.refresh(medium)
    
    # Create categories if they don't exist
    geografia = db.query(Category).filter(Category.name == "Geografia").first()
    if not geografia:
        geografia = Category(name="Geografia")
        db.add(geografia)
        db.commit()
        db.refresh(geografia)
    
    matematica = db.query(Category).filter(Category.name == "Matematica").first()
    if not matematica:
        matematica = Category(name="Matematica")
        db.add(matematica)
        db.commit()
        db.refresh(matematica)
    
    storia = db.query(Category).filter(Category.name == "Storia").first()
    if not storia:
        storia = Category(name="Storia")
        db.add(storia)
        db.commit()
        db.refresh(storia)
    
    # Create sample quizzes
    sample_quizzes = [
        {
            "question": "Qual è la capitale dell'Italia?",
            "option_a": "Roma",
            "option_b": "Milano",
            "option_c": "Napoli",
            "option_d": "Torino",
            "correct_answer": "a",
            "explanation": "Roma è la capitale dell'Italia dal 1871.",
            "points": 10,
            "difficulty_level_id": easy.id,
            "categories": [geografia],
            "creator_id": current_user.id
        },
        {
            "question": "Quanto fa 7 x 8?",
            "option_a": "54",
            "option_b": "56",
            "option_c": "58",
            "option_d": "64",
            "correct_answer": "b",
            "explanation": "7 x 8 = 56",
            "points": 10,
            "difficulty_level_id": easy.id,
            "categories": [matematica],
            "creator_id": current_user.id
        },
        {
            "question": "In che anno è iniziata la Prima Guerra Mondiale?",
            "option_a": "1914",
            "option_b": "1915",
            "option_c": "1918",
            "option_d": "1939",
            "correct_answer": "a",
            "explanation": "La Prima Guerra Mondiale è iniziata nel 1914.",
            "points": 15,
            "difficulty_level_id": medium.id,
            "categories": [storia],
            "creator_id": current_user.id
        }
    ]
    
    # Add quizzes to database
    created_quizzes = []
    for quiz_data in sample_quizzes:
        # Check if quiz with same question already exists
        existing_quiz = db.query(Quiz).filter(Quiz.question == quiz_data["question"]).first()
        if not existing_quiz:
            categories = quiz_data.pop("categories")
            quiz = Quiz(**quiz_data)
            quiz.categories = categories
            db.add(quiz)
            db.commit()
            db.refresh(quiz)
            created_quizzes.append(quiz)
    
    return {"message": f"Created {len(created_quizzes)} sample quizzes", "created_count": len(created_quizzes)}
