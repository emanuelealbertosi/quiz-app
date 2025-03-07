"""
Migrazione per aggiungere colori alle categorie esistenti
"""
import sys
import os
import random

# Aggiungi il percorso della root del progetto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.session import SessionLocal
from app import models

# Colori predefiniti per le categorie
CATEGORY_COLORS = {
    'Matematica': '#4CAF50',    # Verde
    'Scienze': '#2196F3',       # Blu
    'Storia': '#FFC107',        # Giallo
    'Geografia': '#FF5722',     # Arancione
    'Lingue': '#9C27B0',        # Viola
    'Astronomia': '#3F51B5',    # Indaco
    'Letteratura': '#795548',   # Marrone
    'Arte': '#E91E63',          # Rosa
    'Musica': '#673AB7',        # Viola scuro
    'Tecnologia': '#00BCD4',    # Ciano
    'Sport': '#F44336',         # Rosso
}

# Funzione per generare un colore hex casuale
def get_random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

def main():
    print("Connessione al database...")
    db = SessionLocal()
    
    try:
        print("Aggiornamento colori delle categorie...")
        categories = db.query(models.quiz.Category).all()
        
        updated_count = 0
        for category in categories:
            if not category.color:  # Solo se il colore non è già impostato
                # Usa il colore predefinito se disponibile, altrimenti genera casuale
                category.color = CATEGORY_COLORS.get(category.name, get_random_color())
                updated_count += 1
        
        db.commit()
        print(f"Migrazione completata con successo! Aggiornate {updated_count} categorie.")
    
    except Exception as e:
        db.rollback()
        print(f"Errore durante la migrazione: {e}")
    finally:
        db.close()
        print("Connessione al database chiusa.")

if __name__ == "__main__":
    main()
