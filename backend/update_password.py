from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User

def update_password(username, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            print(f"Utente trovato: {user.username}")
            user.hashed_password = get_password_hash(password)
            db.commit()
            print(f"Password aggiornata per l'utente {user.username}")
        else:
            print(f"Utente {username} non trovato")
    finally:
        db.close()

if __name__ == "__main__":
    # Aggiorna password per student e parent
    update_password("student", "password")
    update_password("parent", "password")
