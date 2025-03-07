#!/usr/bin/env python
from app.db.session import SessionLocal
from app.models.quiz import Quiz

def update_quiz_points():
    db = SessionLocal()
    try:
        quizzes = db.query(Quiz).all()
        for q in quizzes:
            q.points = 10
            db.add(q)
        db.commit()
        print('Punti aggiornati per tutti i quiz a 10')
    finally:
        db.close()

if __name__ == "__main__":
    update_quiz_points()
