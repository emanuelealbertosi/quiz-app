# Quiz App

Un'applicazione web interattiva che permette agli studenti di esercitarsi con quiz educativi e accumulare punti.

## Stato del Progetto

### Funzionalità Implementate
- **Sistema di autenticazione**: Login e registrazione utenti con ruoli differenti (admin, student, parent, teacher)
- **Pannello amministrativo**: 
  - Gestione dei livelli di difficoltà
  - Gestione dei percorsi di apprendimento
  - Gestione degli utenti
  - Statistiche dettagliate (utenti, quiz, categorie, difficoltà)
  - Importazione di quiz tramite CSV
- **Sistema di quiz**: Creazione, modifica e gestione dei quiz con categorie e livelli di difficoltà
- **Sistema di sfide**: Creazione e gestione di sfide per gli studenti
- **Monitoraggio progressi**: Tracciamento dei tentativi e dei risultati degli studenti
- **Interfaccia responsive**: Design moderno con Material-UI

### Funzionalità da Implementare
- **Sistema di premi**: Implementare un sistema di premi per gli studenti basato sui punti accumulati
- **Interfaccia per genitori**: Migliorare la dashboard per i genitori per monitorare i progressi dei figli
- **Modalità di gioco avanzate**: Quiz a tempo, sfide tra studenti, tornei
- **Esportazione dati**: Aggiungere funzionalità per esportare statistiche e progressi
- **Personalizzazione profilo**: Permettere agli utenti di personalizzare il proprio profilo con avatar e preferenze
- **Notifiche**: Sistema di notifiche per nuove sfide, premi ottenuti, ecc.

## Tecnologie Utilizzate

- **Backend**: Python con FastAPI
- **Frontend**: React.js con Material-UI
- **Database**: PostgreSQL
- **Containerizzazione**: Docker e Docker Compose

## Installazione e Avvio

### Prerequisiti
- Docker e Docker Compose (per esecuzione containerizzata)
- Python 3.8+ e pip (per esecuzione manuale del backend)
- Node.js 14+ e npm (per esecuzione manuale del frontend)
- PostgreSQL 14+ (per esecuzione manuale del database)

### Opzione 1: Avvio con Docker (consigliato)

Questo metodo avvia automaticamente backend, frontend e database in un ambiente isolato:

```bash
# Avvio dell'intera applicazione
docker-compose up -d

# Per visualizzare i log
docker-compose logs -f

# Per fermare l'applicazione
docker-compose down
```

### Opzione 2: Installazione e avvio manuale

#### 1. Configurazione del database

```bash
# Installazione PostgreSQL (se non presente)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Avvio del servizio PostgreSQL
sudo service postgresql start

# Creazione del database
sudo -u postgres psql -c "CREATE DATABASE quiz_app;"
sudo -u postgres psql -c "CREATE USER quiz_user WITH PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE quiz_app TO quiz_user;"

# Inizializzazione del database (dalla cartella del progetto)
cd backend
sudo -u postgres psql -d quiz_app -f init_db.sql
```

#### 2. Configurazione e avvio del backend

```bash
# Attivazione dell'ambiente virtuale esistente
cd backend
source venv/bin/activate

# Configurazione delle variabili d'ambiente (se necessario)
export DATABASE_URL="postgresql://quiz_user:password@localhost:5432/quiz_app"
export SECRET_KEY="your_secret_key_here"
export ENVIRONMENT="development"

# Avvio del backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

Nota: L'ambiente virtuale necessario è già configurato nella cartella `backend/venv`. Se hai bisogno di aggiornare le dipendenze, puoi eseguire `pip install -r requirements.txt` all'interno dell'ambiente virtuale.

#### 3. Configurazione e avvio del frontend

```bash
# Installazione delle dipendenze
cd frontend
npm install

# Avvio del frontend
npm start
```

### Accesso all'applicazione

Dopo l'avvio, puoi accedere all'applicazione ai seguenti indirizzi:

- **Frontend**: http://localhost:3000
- **API Backend**: http://localhost:8001
- **Documentazione API**: http://localhost:8001/docs
- **PgAdmin** (se avviato con Docker): http://localhost:5050 (email: admin@example.com, password: admin)

### Importazione di dati di esempio

Per popolare il database con dati di esempio, esegui:

```bash
# Dalla cartella backend, con l'ambiente virtuale attivato
python seed_db.py
```

### Risoluzione dei problemi

Se riscontri problemi con la visualizzazione delle domande dei quiz:

1. Verifica che l'API backend stia restituendo correttamente il formato delle opzioni (array `options` anziché campi separati)
2. Assicurati che il frontend stia interpretando correttamente le risposte API
3. Controlla i log del backend e del frontend per eventuali errori
