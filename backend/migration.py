from sqlalchemy import create_engine, text
import os

def migrate():
    # Usa la variabile d'ambiente o un valore di default per la connessione al database
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/quiz_app')
    
    # Connessione al database
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Aggiungi la colonna completed alla tabella quiz_attempts
        conn.execute(text('ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS completed BOOLEAN DEFAULT FALSE'))
        conn.commit()
        print('Migration completed successfully')

if __name__ == "__main__":
    migrate()
