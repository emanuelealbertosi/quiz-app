from sqlalchemy import create_engine, text

# Connessione al database
engine = create_engine('postgresql://postgres:password@localhost:5432/quiz_app')

with engine.connect() as conn:
    # Aggiorna tutti i tentativi corretti impostando completed a TRUE
    result = conn.execute(text('UPDATE quiz_attempts SET completed = TRUE WHERE correct = TRUE'))
    conn.commit()
    print(f'Tentativi aggiornati!')
    
    # Verifica i risultati
    result = conn.execute(text('SELECT id, quiz_id, user_id, correct, completed FROM quiz_attempts ORDER BY id DESC LIMIT 10'))
    print('ID | QUIZ_ID | USER_ID | CORRECT | COMPLETED')
    for row in result:
        print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}')
