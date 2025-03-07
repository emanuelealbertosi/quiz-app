"""
Migrazione per aggiungere la colonna 'color' alla tabella 'categories'
"""
import sys
import os

# Aggiungi il percorso della root del progetto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Ottieni URL del database dalla configurazione
DATABASE_URL = settings.DATABASE_URL
print(f"Utilizzo DATABASE_URL: {DATABASE_URL}")

print("Connessione al database...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("Verifica se la colonna 'color' esiste già...")
        result = conn.execute(text(
            """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'categories' AND column_name = 'color'
            """
        ))
        
        if result.fetchone():
            print("La colonna 'color' esiste già. Migrazione non necessaria.")
        else:
            print("Aggiunta della colonna 'color' alla tabella 'categories'...")
            conn.execute(text(
                """
                ALTER TABLE categories 
                ADD COLUMN color VARCHAR DEFAULT NULL;
                """
            ))
            conn.commit()
            print("Migrazione completata con successo!")
    
    print("Connessione al database chiusa.")
except Exception as e:
    print(f"Errore durante la migrazione: {e}")
