#!/usr/bin/env python3
"""
Script per controllare e correggere gli indirizzi email nel database
"""
import os
import sys

# Aggiungiamo il percorso alla directory principale dell'app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User

def check_and_fix_emails():
    """Controlla gli indirizzi email nel database e corregge quelli non validi"""
    db = SessionLocal()
    
    try:
        # Ottieni tutti gli utenti
        users = db.query(User).all()
        
        print(f"Found {len(users)} users in database:")
        
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Email: '{user.email}', Role: {user.role}")
            
            # Controlla se l'email è vuota o non valida
            if not user.email or '@' not in user.email:
                print(f"  - Invalid email found for user {user.username}")
                
                # Correggi l'email
                new_email = f"{user.username}@example.com"
                print(f"  - Fixing email to: {new_email}")
                
                user.email = new_email
                db.add(user)
        
        # Salva i cambiamenti
        db.commit()
        print("Database updated successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    check_and_fix_emails()
