from app.db.base import Base
from app.db.session import engine

def create_tables():
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    from sqlalchemy import text
    create_tables()