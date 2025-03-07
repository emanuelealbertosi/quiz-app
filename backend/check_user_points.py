#!/usr/bin/env python
from app.db.session import SessionLocal
from app.models.user import User

def check_user_points():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for u in users:
            print(f'User: {u.username}, Role: {u.role}, Points: {u.points}')
    finally:
        db.close()

if __name__ == "__main__":
    check_user_points()
