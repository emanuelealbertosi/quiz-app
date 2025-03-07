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
