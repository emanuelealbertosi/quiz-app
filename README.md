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
- **Sistema di premi**: Permette agli studenti di acquistare premi utilizzando i punti guadagnati completando i quiz. Gli admin possono creare e gestire i premi, mentre i genitori possono gestire i premi per i loro figli.
- **Sistema di percorsi di apprendimento**: Consente ai genitori di creare percorsi personalizzati composti da quiz multipli, assegnarli ai propri figli e monitorarne il completamento. Gli studenti guadagnano punti bonus al completamento di un intero percorso.
- **Interfaccia responsive**: Design moderno con Material-UI

### Funzionalità da Implementare
- **Interfaccia per genitori**: Migliorare la dashboard per i genitori per monitorare i progressi dei figli
- **Modalità di gioco avanzate**: Quiz a tempo, sfide tra studenti, tornei
- **Esportazione dati**: Aggiungere funzionalità per esportare statistiche e progressi
- **Personalizzazione profilo**: Permettere agli utenti di personalizzare il proprio profilo con avatar e preferenze
- **Notifiche**: Sistema di notifiche per nuove sfide, premi ottenuti, ecc.
- **Correggere percorsi e visualizzazione quiz**: Utilizzare i quiz come template per creare copie dei quiz nei percorsi ogni volta che vengono assegnati

## Tecnologie Utilizzate

- **Backend**: Python con FastAPI
- **Frontend**: React.js con Material-UI
- **Database**: PostgreSQL
- **Containerizzazione**: Docker e Docker Compose

## Appunti Implementazione

### Sistema di Quiz nei Percorsi
- I quiz nei percorsi sono implementati come copie dedicate dei quiz originali
- Ogni copia (PathQuiz) mantiene un riferimento al quiz originale tramite `original_quiz_id`
- I tentativi degli studenti sono tracciati tramite il modello `PathQuizAttempt`
- L'endpoint API è `/api/v1/path-quizzes/*`
- Il completamento di un quiz nel percorso aggiunge punti allo studente in base al valore del quiz
- È possibile verificare quali quiz di un percorso sono stati completati tramite l'endpoint `/api/v1/path-quizzes/completed/{path_id}`

### Richieste API
- Login: Usare `requests.post('/api/v1/login', data={'username': '...', 'password': '...'})` (richiede form-data, non JSON)
- La porta del server è 9999: `http://localhost:9999/`
- Il database PostgreSQL usa la porta 5433: `postgresql://postgres:password@localhost:5433/quiz_app`

### Endpoints principali
- **Login**: `POST /api/v1/login` (form-data con username/password)
- **Creazione percorso**: `POST /api/v1/paths/` (JSON con name, description, quiz_ids, bonus_points)
- **Assegnazione percorso**: `POST /api/v1/paths/assign` (JSON con path_id, user_id)
- **Quiz in percorso**: `GET /api/v1/path-quizzes/path/{path_id}`
- **Dettagli quiz in percorso**: `GET /api/v1/path-quizzes/{path_quiz_id}`
- **Tentativo quiz**: `POST /api/v1/path-quizzes/attempt` (JSON con path_quiz_id, answer, show_explanation)
- **Quiz completati**: `GET /api/v1/path-quizzes/completed/{path_id}`

### Modelli Database
- `User` -> `created_quizzes`, `quiz_attempts`, `path_quiz_attempts`, etc.
- `Path` -> `creator`, `quizzes`, `path_quizzes`
- `PathQuiz` -> `path`, `attempts`, `original_quiz`
- `PathQuizAttempt` -> `user`, `path_quiz`

### Gestione utenti
- **Ruoli**: `admin`, `parent`, `student`
- Gli utenti devono avere una password crittografata con la funzione `get_password_hash`
- I genitori possono creare percorsi e assegnarli ai propri figli
- Gli studenti possono vedere solo i percorsi loro assegnati
- L'assegnazione di un percorso crea copie dei quiz (path_quiz) che lo studente può tentare

## Installazione e Avvio

### Prerequisiti
- Docker e Docker Compose (per esecuzione containerizzata)
- Python 3.8+ e pip (per esecuzione manuale del backend)
- Node.js 14+ e npm (per esecuzione manuale del frontend)
- PostgreSQL 14+ (per esecuzione manuale del database)

### Opzione 1: Avvio con Docker (consigliato)

Questo metodo avvia automaticamente backend, frontend e database in un ambiente isolato.

#### Installazione completa

```bash
# 1. Clonare il repository se non l'hai già fatto
git clone https://github.com/emanuelealbertosi/quiz-app.git
cd quiz-app

# 2. Costruire i container Docker
sudo docker-compose build

# 3. Avviare l'applicazione
sudo docker-compose up -d

# L'applicazione sarà disponibile su:
# - Frontend: http://localhost:3001
# - Backend API: http://localhost:9999
```

#### Comandi Docker utili

```bash
# Visualizzare lo stato dei container
sudo docker-compose ps

# Visualizzare i log (in tempo reale)
sudo docker-compose logs -f

# Visualizzare i log di un servizio specifico
sudo docker-compose logs backend
sudo docker-compose logs frontend

# Fermare l'applicazione mantenendo i dati
sudo docker-compose stop

# Riavviare l'applicazione dopo uno stop
sudo docker-compose start

# Fermare e rimuovere i container (i dati del database rimangono persistenti)
sudo docker-compose down

# Fermare e rimuovere i container E i volumi (CANCELLA tutti i dati del database)
sudo docker-compose down -v

# Ricostruire i container dopo modifiche ai file di configurazione
sudo docker-compose build
sudo docker-compose up -d
```

#### Accesso al database tramite pgAdmin

Dopo l'avvio, puoi accedere all'interfaccia di pgAdmin:
1. Apri http://localhost:5051 nel browser
2. Login con email: admin@example.com, password: admin
3. Aggiungere un nuovo server:
   - Nome: quiz_app_db
   - Host: db
   - Porta: 5432
   - Database: quiz_app
   - Utente: postgres
   - Password: password

**Nota**: Potrebbe essere necessario utilizzare `sudo` per i comandi Docker a seconda della configurazione del sistema.

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
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9999 --reload
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

- **Frontend**: http://localhost:3001
- **API Backend**: http://localhost:9999
- **Documentazione API**: http://localhost:9999/docs
- **PgAdmin** (se avviato con Docker): http://localhost:5051 (email: admin@example.com, password: admin)

### Importazione di dati di esempio

Per popolare il database con dati di esempio, esegui:

```bash
# Dalla cartella backend, con l'ambiente virtuale attivato
python seed_db.py
```

### Risoluzione dei problemi

#### Errori di timeout Docker
Se riscontri errori come questo durante l'avvio con Docker Compose:
```
ERROR: for quiz_app_frontend_1  UnixHTTPConnectionPool(host='localhost', port=None): Read timed out. (read timeout=60)
ERROR: An HTTP request took too long to complete.
```

È necessario aumentare il timeout HTTP di Docker Compose:

```bash
# Imposta un timeout più lungo (es. 300 secondi invece di 60)
export COMPOSE_HTTP_TIMEOUT=300

# Quindi riprova il comando che stavi eseguendo
sudo docker-compose up -d
```

Puoi anche aggiungere questa impostazione al tuo file `~/.bashrc` per renderla permanente:
```bash
echo "export COMPOSE_HTTP_TIMEOUT=300" >> ~/.bashrc
source ~/.bashrc
```

#### Errori di rete durante il login (NetworkError)
Se riscontri un errore "NetworkError when attempting to fetch resource" durante il login:

1. **Verifica che tutti i servizi siano attivi**:
   ```bash
   sudo docker-compose ps
   ```
   Tutti i servizi dovrebbero essere nello stato "Up".

2. **Verifica i log del backend**:
   ```bash
   sudo docker-compose logs backend
   ```
   Cerca eventuali errori relativi all'autenticazione o alle richieste API.

3. **Inizializza il database se è la prima esecuzione**:
   ```bash
   sudo docker-compose exec backend python seed_db.py
   ```
   Questo creerà l'utente admin di default e i dati iniziali.

4. **Riavvia i container e prova ad accedere con credenziali corrette**:
   ```bash
   sudo docker-compose restart frontend backend
   ```
   Quindi visita http://localhost:3001 e accedi con:
   - Email: admin@example.com
   - Password: password

5. **Disabilita eventuali estensioni del browser che potrebbero bloccare le richieste**.

6. **Se tutto il resto fallisce, prova una soluzione più drastica**:
   ```bash
   sudo docker-compose down
   sudo docker-compose build --no-cache
   sudo docker-compose up -d
   sudo docker-compose exec backend python seed_db.py
   ```

#### Problemi con l'interfaccia utente
Se riscontri problemi con la visualizzazione delle domande dei quiz:

1. Verifica che l'API backend stia restituendo correttamente il formato delle opzioni (array `options` anziché campi separati)
2. Assicurati che il frontend stia interpretando correttamente le risposte API
3. Controlla i log del backend e del frontend per eventuali errori

#### Problemi di connessione in Docker
Se riscontri errori di connessione come "NetworkError when attempting to fetch resource" quando usi Docker:

1. Verifica che tutti i servizi siano attivi con `sudo docker-compose ps`
2. Controlla i log del backend e frontend con `sudo docker-compose logs backend` e `sudo docker-compose logs frontend`
3. Assicurati che il frontend utilizzi l'URL corretto per connettersi al backend (verifica in `frontend/src/config.js`)
4. Se modifichi file di configurazione, ricostruisci i container con `sudo docker-compose build` seguito da `sudo docker-compose up -d`

#### Problemi di permessi
Se riscontri errori di permessi nei container Docker:

1. Esegui i comandi Docker con `sudo`
2. Se stai modificando file all'interno dei container, assicurati che abbiano i permessi corretti

### Docker: Riferimento Rapido

```bash
# Riavvio completo dell'applicazione (stop, build, start)
sudo docker-compose down && sudo docker-compose build && sudo docker-compose up -d

# Visualizzare tutti i container (anche quelli non attivi)
sudo docker ps -a

# Visualizzare tutte le immagini Docker
sudo docker images

# Eliminare immagini non utilizzate (pulizia)
sudo docker image prune -a

# Entrare in un container attivo (per debug)
sudo docker exec -it quiz_app_backend_1 /bin/bash
sudo docker exec -it quiz_app_frontend_1 /bin/sh

# Controllare i log di un servizio specifico (ultimi 100 log)
sudo docker-compose logs --tail=100 backend

# Monitorare l'utilizzo delle risorse dei container
sudo docker stats
```

Questi comandi ti aiuteranno a gestire e risolvere rapidamente i problemi più comuni dell'applicazione in Docker.
