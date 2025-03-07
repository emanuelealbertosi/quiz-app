#!/usr/bin/env python3
"""
Script per inizializzare il database
"""
import os
import sys

# Aggiungiamo il percorso alla directory principale dell'app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.base import Base
from app.db.session import engine

def create_tables():
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Database initialized successfully!")
