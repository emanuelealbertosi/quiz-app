#!/usr/bin/env python
from app.db.session import SessionLocal
from app.models.quiz import Quiz

def check_quiz_points():
    db = SessionLocal()
    try:
        quizzes = db.query(Quiz).all()
        for q in quizzes:
            print(f'Quiz ID: {q.id}, Punti: {q.points}')
    finally:
        db.close()

if __name__ == "__main__":
    check_quiz_points()
