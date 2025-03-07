#!/usr/bin/env python3
"""
Script per popolare il database con dati iniziali
"""
import os
import sys
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

# Aggiungiamo il percorso alla directory principale dell'app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash
from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.user import User
from app.models.quiz import Category, Quiz, DifficultyLevel, Path
from app.models.challenge import Challenge, QuizAttempt, UserChallenge, UserProgress, UserReward


def init_db(db: Session) -> None:
    """Inizializza il database con dati di esempio"""
    print("Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    print("Creating initial data...")
    
    # Crea utenti di default
    print("Creating users...")
    admin_user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin"),
        full_name="Administrator",
        role="admin",
        is_active=True,
    )
    db.add(admin_user)
    
    parent_user = User(
        username="parent",
        email="parent@example.com",
        hashed_password=get_password_hash("parent"),
        full_name="Test Parent",
        role="parent",
        is_active=True,
    )
    db.add(parent_user)
    
    student_user = User(
        username="student",
        email="student@example.com",
        hashed_password=get_password_hash("student"),
        full_name="Test Student",
        role="student",
        is_active=True,
        points=100,
    )
    db.add(student_user)
    
    # Salva gli utenti per ottenere gli ID
    db.commit()
    
    # Associa studente a genitore
    parent_user.students.append(student_user)
    db.add(parent_user)
    db.commit()
    
    # Crea categorie di esempio
    print("Creating categories...")
    categories = [
        {"name": "Matematica", "description": "Quiz di matematica per tutte le età"},
        {"name": "Scienze", "description": "Quiz di scienze naturali e fisica"},
        {"name": "Storia", "description": "Quiz di storia e cultura generale"},
        {"name": "Geografia", "description": "Quiz di geografia mondiale"},
        {"name": "Lingue", "description": "Quiz di lingue straniere"},
    ]
    
    category_objects = []
    for cat_data in categories:
        category = Category(
            name=cat_data["name"],
            description=cat_data["description"]
        )
        db.add(category)
        category_objects.append(category)
    
    db.commit()
    
    # Crea livelli di difficoltà
    print("Creating difficulty levels...")
    difficulty_levels = [
        {"name": "Facile", "value": 1},
        {"name": "Medio", "value": 2},
        {"name": "Difficile", "value": 3},
        {"name": "Esperto", "value": 4},
    ]
    
    difficulty_objects = []
    for dl_data in difficulty_levels:
        difficulty = DifficultyLevel(
            name=dl_data["name"],
            value=dl_data["value"],
        )
        db.add(difficulty)
        difficulty_objects.append(difficulty)
    
    db.commit()
    
    # Crea percorsi di quiz
    print("Creating quiz paths...")
    paths = [
        {"name": "Percorso base matematica", "description": "Concetti base di matematica", "bonus_points": 50},
        {"name": "Percorso scienze elementari", "description": "Scienze per principianti", "bonus_points": 30},
        {"name": "Percorso storia mondiale", "description": "Eventi storici importanti", "bonus_points": 40},
    ]
    
    path_objects = []
    for path_data in paths:
        path = Path(
            name=path_data["name"],
            description=path_data["description"],
            bonus_points=path_data["bonus_points"],
            creator_id=admin_user.id,
        )
        db.add(path)
        path_objects.append(path)
    
    db.commit()
    
    # Crea quiz di esempio
    print("Creating sample quizzes...")
    math_category = category_objects[0]     # Matematica
    science_category = category_objects[1]  # Scienze
    history_category = category_objects[2]  # Storia
    
    easy_level = difficulty_objects[0]    # Facile
    medium_level = difficulty_objects[1]  # Medio
    hard_level = difficulty_objects[2]    # Difficile
    
    quizzes = [
        {
            "question": "Quanto fa 2 + 2?", 
            "options": ["3", "4", "5", "6"],
            "correct_answer": "4",
            "category_id": math_category.id,
            "difficulty_level_id": easy_level.id
        },
        {
            "question": "Qual è la formula dell'acqua?", 
            "options": ["H2O", "CO2", "O2", "H2SO4"],
            "correct_answer": "H2O",
            "category_id": science_category.id,
            "difficulty_level_id": easy_level.id
        },
        {
            "question": "In quale anno è caduto il muro di Berlino?", 
            "options": ["1985", "1989", "1991", "1993"],
            "correct_answer": "1989",
            "category_id": history_category.id,
            "difficulty_level_id": medium_level.id
        },
    ]
    
    for quiz_data in quizzes:
        category = db.query(Category).filter(Category.id == quiz_data["category_id"]).first()
        quiz = Quiz(
            question=quiz_data["question"],
            options=quiz_data["options"],
            correct_answer=quiz_data["correct_answer"],
            difficulty_level_id=quiz_data["difficulty_level_id"],
            creator_id=admin_user.id,
        )
        quiz.categories.append(category)
        db.add(quiz)
    
    db.commit()
    
    # Crea sfide di esempio
    print("Creating sample challenges...")
    challenge = Challenge(
        name="Sfida matematica",
        description="Completa i quiz di matematica",
        points=50,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=7),
        active=True,
        creator_id=parent_user.id,
        path_id=path_objects[0].id,  # Percorso base matematica
    )
    db.add(challenge)
    db.commit()
    
    # Crea alcuni premi di esempio
    print("Creating sample rewards...")
    rewards = [
        {"name": "Giorno senza compiti", "description": "Un giorno senza compiti a casa", "points_cost": 50},
        {"name": "Sessione extra di gioco", "description": "30 minuti extra di videogiochi", "points_cost": 30},
    ]
    
    for reward_data in rewards:
        reward = UserReward(
            name=reward_data["name"],
            description=reward_data["description"],
            points=reward_data["points_cost"],
            user_id=student_user.id
        )
        db.add(reward)
    
    db.commit()
    
    print("Database initialization completed!")


def main() -> None:
    """Main function to initialize the database"""
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
