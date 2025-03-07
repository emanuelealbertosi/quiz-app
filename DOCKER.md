# Quiz App - Docker Setup

Questa guida spiega come avviare l'applicazione Quiz App utilizzando Docker.

## Prerequisiti

- Docker e Docker Compose installati sul sistema

## Avvio Rapido

Abbiamo creato uno script per semplificare l'avvio dei container:

```bash
# Rendi lo script eseguibile (solo la prima volta)
chmod +x docker-start.sh

# Avvia l'ambiente di sviluppo
./docker-start.sh dev

# Avvia l'ambiente di produzione
./docker-start.sh prod

# Arresta l'ambiente di sviluppo
./docker-start.sh stop

# Arresta l'ambiente di produzione
./docker-start.sh stop-prod
```

## Avvio Manuale

### Ambiente di Sviluppo

```bash
# Avvia i servizi in modalità detached
docker-compose up -d

# Visualizza i log
docker-compose logs -f

# Arresta i servizi
docker-compose down
```

### Ambiente di Produzione

```bash
# Avvia i servizi in modalità detached
docker-compose -f docker-compose.prod.yml up -d

# Visualizza i log
docker-compose -f docker-compose.prod.yml logs -f

# Arresta i servizi
docker-compose -f docker-compose.prod.yml down
```

## Accesso ai Servizi

### Ambiente di Sviluppo
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- Documentazione API: http://localhost:8001/docs
- PgAdmin: http://localhost:5050 (email: admin@example.com, password: admin)

### Ambiente di Produzione
- Frontend: http://localhost
- Backend API: http://localhost:8001
- Documentazione API: http://localhost:8001/docs
- PgAdmin: http://localhost:5050 (email: admin@example.com, password: admin)

## Struttura dei File Docker

- `docker-compose.yml` - Configurazione per l'ambiente di sviluppo
- `docker-compose.prod.yml` - Configurazione per l'ambiente di produzione
- `frontend/Dockerfile` - Configurazione Docker per il frontend (sviluppo)
- `frontend/Dockerfile.prod` - Configurazione Docker per il frontend (produzione)
- `backend/Dockerfile` - Configurazione Docker per il backend
- `docker-start.sh` - Script di utilità per avviare/arrestare i container

## Risoluzione dei problemi

### Errori di connessione al database
- Verifica che il servizio `db` sia in esecuzione con `docker-compose ps`
- Controlla i log del database con `docker-compose logs db`

### Errori di connessione al backend
- Assicurati che il backend sia operativo con `docker-compose logs backend`
- Verifica che il frontend punti all'indirizzo corretto del backend

### Errori di CORS
- Il frontend deve comunicare con il backend su `http://localhost:8000`
- Il backend deve permettere richieste dal frontend su `http://localhost:3000` o `http://localhost`

### Persistenza dei dati
- I dati del database sono mantenuti in un volume Docker
- Per eliminare completamente i dati: `docker-compose down -v`
