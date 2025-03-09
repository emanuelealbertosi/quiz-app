from sqlalchemy import text
from app.db.session import engine
from app.models.base import Base

def reset_database():
    """
    Elimina tutte le tabelle esistenti e ricrea lo schema dal modello
    """
    print("Eliminazione dello schema esistente...")
    try:
        with engine.connect() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.commit()
        print("Schema eliminato con successo.")
    except Exception as e:
        print(f"Errore durante l'eliminazione dello schema: {e}")
        return
    
    print("Ricreazione delle tabelle...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tabelle ricreate con successo.")
    except Exception as e:
        print(f"Errore durante la ricreazione delle tabelle: {e}")

if __name__ == "__main__":
    reset_database()
